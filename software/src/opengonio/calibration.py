"""Measured calibration (config/calibration.yaml): angle offsets, dark level, white reference, drift limit.

    opengonio calibrate show
    opengonio calibrate mirror data/mirror_20 data/mirror_40 …   angle offset from mirror peaks (stage 07)
    opengonio calibrate dark data/dark                          lamp-off level (camera + spectral)
    opengonio calibrate white data/white --rho 0.99             PTFE at 45:0 -> absolute BRDF units
    opengonio calibrate linearity data/linearity                camera response: counts vs exposure -> gamma

Radiometry [R2][R1]: the camera counts are proportional to radiance L_r; the lamp gives irradiance E_i = E_0 cos(theta_i).
PTFE (Lambertian, reflectance rho) at theta_i = 45 deg gives  C_w - C_d = k E_0 cos(45) rho / pi, so for any sample
    f_r = (C - C_d) / (C_w - C_d) * rho / pi * cos(45 deg) / cos(theta_i)        [1/sr]
(same exposure, gain and lamp distance as the white shot). Counts are made linear PER PIXEL before averaging:
C_lin = (C - C_d)^gamma, gamma from an exposure series (gamma = 1: the camera is already linear; ~2.2: sRGB-like) [R5].

The calibration used for a run is copied whole into its manifest (`snapshot`, with an id). Processing uses that copy;
a different calibration is applied only on request and the result is labelled as a recalibrated revision.
Assumptions the conversion depends on are checked, not assumed: same exposure as the white shot, a positive white
signal, 0 < rho <= 1, theta_i < 89 deg. rho is recorded with its source ("assumed" unless a certificate is named).
"""
from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import math
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

import numpy as np

from .imageio import decoded, region_mean, default_reader

AXES = ("M4", "M3", "M2", "M1")
BLANK = {"schema": 2, "angle_offset_deg": dict.fromkeys(AXES, 0.0), "gamma": 1.0, "dark_counts": None, "spectral_dark": None,
         "white": None, "drift_limit_pct": 2.0, "max_age_days": 30,
         "dates": {"angle_offset_deg": None, "gamma": None, "dark_counts": None, "spectral_dark": None, "white": None}}


def _default_cal_path() -> Path:
    """Repository checkout: software/config/calibration.yaml. Installed package: $OPENGONIO_HOME (default
    ~/.config/opengonio)/calibration.yaml - never inside the package."""
    if os.environ.get("OPENGONIO_CALIBRATION"):
        return Path(os.environ["OPENGONIO_CALIBRATION"])
    repo = Path(__file__).resolve().parents[2] / "config" / "calibration.yaml"
    if repo.parent.is_dir():
        return repo
    return Path(os.environ.get("OPENGONIO_HOME", "~/.config/opengonio")).expanduser() / "calibration.yaml"


DEFAULT_CAL = _default_cal_path()


class CalibrationError(ValueError):
    pass


@dataclass
class Calibration:
    data: dict = field(default_factory=lambda: copy.deepcopy(BLANK))
    path: Path | None = None

    # ---- read ------------------------------------------------------------
    @property
    def offsets(self) -> dict[str, float]:
        return {k: float(self.data["angle_offset_deg"].get(k, 0.0)) for k in AXES}

    @property
    def dark(self) -> float:
        return float(self.data.get("dark_counts") or 0.0)

    @property
    def drift_limit_pct(self) -> float:
        return float(self.data.get("drift_limit_pct", 2.0))

    def stale(self, today: dt.date | None = None) -> list[str]:
        """Entries measured more than max_age_days ago."""
        today = today or dt.date.today()
        out = []
        for k, d in (self.data.get("dates") or {}).items():
            if d and (today - dt.date.fromisoformat(str(d))).days > int(self.data.get("max_age_days", 30)):
                out.append(f"{k} ({d})")
        return out

    def missing(self) -> list[str]:
        return [k for k, d in (self.data.get("dates") or {}).items() if not d]

    @property
    def gamma(self) -> float:
        return float(self.data.get("gamma") or 1.0)

    def linear(self, counts: float) -> float:
        """One count value -> value proportional to light (dark removed, response undone)."""
        return max(counts - self.dark, 0.0) ** self.gamma

    def linear_array(self, a) -> np.ndarray:
        """Per-pixel version of `linear` (use it before averaging a region)."""
        return np.clip(np.asarray(a, dtype=float) - self.dark, 0.0, None) ** self.gamma

    def white_linear(self) -> float | None:
        """Linear signal of the white reference: stored per-pixel mean (schema 2) or, for older files, from its counts."""
        w = self.data.get("white")
        if not w:
            return None
        v = w.get("linear")
        return float(v) if v is not None else self.linear(float(w["counts"]))

    def brdf_problems(self, exposure_ms: float | None = None, check_exposure: bool = True) -> list[str]:
        """Why an absolute BRDF can't be given for a run with this exposure ([] = it can). Callers that have already
        checked the run's exposure (brdf_linear, per value) pass check_exposure=False."""
        w = self.data.get("white")
        if not w:
            return ["no white reference (run `calibrate white`)"]
        out = []
        ref = self.white_linear()
        if ref is None or not math.isfinite(ref) or ref <= 0:
            out.append("white reference signal is zero or invalid")
        rho = float(w.get("rho", 0))
        if not 0 < rho <= 1:
            out.append(f"reference reflectance rho={rho} outside (0, 1]")
        if not math.isfinite(self.gamma) or self.gamma <= 0:
            out.append(f"camera response gamma={self.gamma} invalid")
        we = w.get("exposure_ms")
        if not check_exposure:
            pass
        elif we is None:
            out.append("white reference has no recorded exposure")
        elif exposure_ms is None:
            out.append("run has no recorded exposure: can't match it to the white reference")
        elif abs(float(we) - float(exposure_ms)) > 1e-6:
            out.append(f"run exposure {exposure_ms} ms differs from the white reference ({we} ms)")
        if w.get("linear") is not None:                   # stored linear value is only valid with the response it used
            for k, now in (("gamma", self.gamma), ("dark_counts", self.dark)):
                if w.get(k) is not None and abs(float(w[k]) - float(now)) > 1e-9:
                    out.append(f"white reference was linearised with {k}={w[k]}, now {now}: run `calibrate white` again")
        return out

    def brdf_linear(self, lin: float, theta_i_deg: float) -> float | None:
        """Linear region signal -> f_r [1/sr]; None when the white reference is missing/invalid or theta_i >= 89."""
        w = self.data.get("white")
        if not w or theta_i_deg >= 89.0 or self.brdf_problems(check_exposure=False):
            return None
        return lin / self.white_linear() * float(w["rho"]) / math.pi * \
            math.cos(math.radians(float(w["theta_i_deg"]))) / math.cos(math.radians(theta_i_deg))

    def brdf(self, counts: float, theta_i_deg: float) -> float | None:
        """Single count value -> f_r (kept for scalar callers; images go through brdf_linear(region_mean(...)))."""
        return self.brdf_linear(self.linear(counts), theta_i_deg)

    def snapshot(self) -> dict:
        """The whole calibration, copied into every manifest.json, with an id: processing uses this copy."""
        d = copy.deepcopy(self.data)
        d["id"] = calibration_id(d)
        return d

    # ---- write -----------------------------------------------------------
    def set(self, key: str, value, today: dt.date | None = None) -> None:
        self.data[key] = value
        self.data.setdefault("dates", {})[key] = (today or dt.date.today()).isoformat()

    def save(self, path: str | Path | None = None) -> Path:
        p = Path(path or self.path or DEFAULT_CAL)
        p.parent.mkdir(parents=True, exist_ok=True)
        head = "".join(l + "\n" for l in DEFAULT_CAL.read_text(encoding="utf-8").splitlines()[:3]) if DEFAULT_CAL.exists() else ""
        p.write_text(head + yaml.safe_dump(self.data, sort_keys=False, default_flow_style=None, width=120), encoding="utf-8")
        return p


def calibration_id(data: dict) -> str:
    """Content id of a calibration (dates included, the id itself excluded)."""
    d = {k: v for k, v in data.items() if k != "id"}
    return hashlib.sha256(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()[:12]


def merged(raw: dict) -> dict:
    data = copy.deepcopy(BLANK)
    data.update({k: v for k, v in raw.items() if k not in ("angle_offset_deg", "dates", "id")})
    data["angle_offset_deg"].update(raw.get("angle_offset_deg") or {})
    data["dates"].update(raw.get("dates") or {})
    return data


def load_calibration(path: str | Path = DEFAULT_CAL) -> Calibration:
    p = Path(path)
    raw = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}
    return Calibration(merged(raw), p)


LEGACY_KEYS = ("angle_offset_deg", "gamma", "dark_counts", "white", "dates")   # what schema-1 manifests stored


def from_snapshot(snap: dict | None, current: Calibration | None = None) -> tuple[Calibration, dict]:
    """The calibration a run was captured with. Returns (calibration, provenance).
    Schema-1 snapshots lack some fields: those come from `current` and are listed in provenance["filled_from_current"]."""
    if not snap:
        cal = current or Calibration()
        return cal, {"source": "current (run has no snapshot)", "id": calibration_id(cal.data)}
    filled = []
    if "id" not in snap and current is not None:                     # legacy snapshot
        base = copy.deepcopy(current.data)
        filled = [k for k in base if k not in snap and k not in ("schema",)]
        base.update({k: copy.deepcopy(v) for k, v in snap.items()})
        data = merged(base)
    else:
        data = merged(snap)
    cal = Calibration(data)
    prov = {"source": "capture snapshot", "id": snap.get("id") or calibration_id(data)}
    if filled:
        prov["filled_from_current"] = filled
    return cal, prov


# ---- from measurement runs -------------------------------------------------
def _manifest(run: str | Path) -> dict:
    return json.loads((Path(run) / "manifest.json").read_text(encoding="utf-8"))


def from_mirror(cal: Calibration, peak_errors_deg: list[float], today=None) -> float:
    """Mirror peak sits at M3 = M4/2 + err (in the angles the run used) -> true M3 is err lower: offset -= mean err."""
    err = sum(peak_errors_deg) / len(peak_errors_deg)
    off = dict(cal.data["angle_offset_deg"])
    off["M3"] = round(float(off.get("M3", 0.0)) - err, 4)
    cal.set("angle_offset_deg", off, today)
    return off["M3"]


def _frames(run: str | Path, shots: list[dict], read) -> list:
    imgs = [read(Path(run) / s["file"]) for s in shots]
    bad = [s["file"] for s, im in zip(shots, imgs) if not decoded(im)]
    if bad:
        raise CalibrationError(f"unreadable image(s) in {run}: {', '.join(bad[:5])}")
    return imgs


def _require(run: str | Path, m: dict, min_shots: int = 1) -> None:
    if m.get("schema", 1) >= 2 and m.get("status") != "finished":
        raise CalibrationError(f"{run}: run is '{m.get('status')}', not finished: capture it again")
    if len(m.get("shots", [])) < min_shots:
        raise CalibrationError(f"{run}: needs at least {min_shots} shot(s)")


def from_dark(cal: Calibration, run: str | Path, read_image=None, today=None) -> dict:
    m, read = _manifest(run), read_image or default_reader()
    _require(run, m)
    if m.get("light"):
        raise CalibrationError(f"{run} was captured with the lamp '{m['light']}' on: dark frames need `capture dark`")
    shots = [s for s in m["shots"] if s.get("file")]
    vals = [region_mean(a) for a in _frames(run, shots, read)]
    out = {}
    if vals:
        cal.set("dark_counts", round(sum(vals) / len(vals), 3), today)
        out["dark_counts"] = cal.data["dark_counts"]
    spec = [s["spectral"] for s in m["shots"] if "spectral" in s]
    if spec:
        cal.set("spectral_dark", [round(sum(c) / len(c), 1) for c in zip(*spec)], today)
        out["spectral_dark"] = cal.data["spectral_dark"]
    return out


def from_white(cal: Calibration, run: str | Path, cfg, rho: float = 0.99, read_image=None, today=None,
               rho_source: str = "assumed (datasheet nominal, not a certificate)") -> dict:
    """PTFE at 45:0. Stores the mean raw counts AND the per-pixel linear mean (dark and gamma as they are now: run
    `calibrate dark` and `calibrate linearity` first). Clipped pixels make the reference invalid."""
    from .gantry.kinematics import brdf_coords
    if not 0 < rho <= 1:
        raise CalibrationError(f"rho={rho}: reflectance must be in (0, 1]")
    m, read = _manifest(run), read_image or default_reader()
    _require(run, m)
    from .roi import sample_roi
    shots = [s for s in m["shots"] if s.get("file")]
    imgs = _frames(run, shots, read)
    rois = [sample_roi(cfg, s["pose"], np.asarray(a).shape) for s, a in zip(shots, imgs)]
    if not all(r.valid for r in rois):
        raise CalibrationError(f"white reference pose has no valid region: {rois[0].reason}")
    raw = [region_mean(a, mask=r.mask) for a, r in zip(imgs, rois)]
    lin = [region_mean(a, mask=r.mask, linear=cal.linear_array, reject_saturated=True) for a, r in zip(imgs, rois)]
    if any(v is None for v in lin):
        raise CalibrationError("white reference has clipped pixels: lower the exposure and capture again")
    if sum(lin) <= 0:
        raise CalibrationError("white reference is no brighter than the dark level: is the lamp on?")
    ti = brdf_coords(cfg, shots[0]["pose"]).theta_i
    w = {"counts": round(sum(raw) / len(raw), 3), "linear": round(sum(lin) / len(lin), 6), "theta_i_deg": round(ti, 2),
         "rho": rho, "rho_source": rho_source, "exposure_ms": m.get("exposure_ms"),
         "dark_counts": cal.dark, "gamma": cal.gamma, "run_id": m.get("run_id")}
    cal.set("white", w, today)
    return w


def linearity(exposures_ms: list[float], counts: list[float], dark: float, top: float = 240.0,
              min_r2: float = 0.99) -> dict:
    """Fit log(C - C_d) = (1/gamma) log(t) + k over unsaturated points (C_d + 5 < C < top).
    Rejected (CalibrationError) with fewer than 3 usable points, under a 4x exposure range, or r2 < min_r2."""
    if len(exposures_ms) != len(counts):
        raise CalibrationError("one count per exposure needed")
    pts = [(math.log(t), math.log(c - dark)) for t, c in zip(exposures_ms, counts)
           if t > 0 and math.isfinite(c) and dark + 5 < c < top]
    if len(pts) < 3:
        raise CalibrationError("need >= 3 exposures between dark and saturation: change --exposures")
    if max(p[0] for p in pts) - min(p[0] for p in pts) < math.log(4):
        raise CalibrationError("usable exposures span less than 4x: widen --exposures")
    x = [p[0] for p in pts]
    y = [p[1] for p in pts]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxx = sum((a - mx) ** 2 for a in x)
    slope = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx
    ss_res = sum((b - (my + slope * (a - mx))) ** 2 for a, b in zip(x, y))
    ss_tot = sum((b - my) ** 2 for b in y) or 1e-12
    if slope <= 0:
        raise CalibrationError("brightness does not rise with exposure: is the lamp on and the exposure applied?")
    r2 = 1 - ss_res / ss_tot
    if r2 < min_r2:
        raise CalibrationError(f"camera response fit r2={r2:.4f} < {min_r2}: noisy or non-monotonic series")
    return {"gamma": round(1 / slope, 3), "r2": round(r2, 5), "points_used": len(pts)}


def from_linearity(cal: Calibration, run: str | Path, read_image=None, today=None) -> dict:
    m, read = _manifest(run), read_image or default_reader()
    _require(run, m, 3)
    shots = [s for s in m["shots"] if s.get("file")]
    res = linearity([s.get("applied_exposure_ms", s["exposure_ms"]) for s in shots],
                    [region_mean(a) for a in _frames(run, shots, read)], cal.dark)
    cal.set("gamma", res["gamma"], today)
    return res
