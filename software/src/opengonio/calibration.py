"""Measured calibration (config/calibration.yaml): angle offsets, dark level, white reference, drift limit.

    opengonio calibrate show
    opengonio calibrate mirror data/mirror_20 data/mirror_40 …   angle offset from mirror peaks (stage 07)
    opengonio calibrate dark data/dark                          lamp-off level (camera + spectral)
    opengonio calibrate white data/white --rho 0.99             PTFE at 45:0 -> absolute BRDF units
    opengonio calibrate linearity data/linearity                camera response: counts vs exposure -> gamma

Radiometry [R2][R1]: the camera counts are proportional to radiance L_r; the lamp gives irradiance E_i = E_0 cos(theta_i).
PTFE (Lambertian, reflectance rho) at theta_i = 45 deg gives  C_w - C_d = k E_0 cos(45) rho / pi, so for any sample
    f_r = (C - C_d) / (C_w - C_d) * rho / pi * cos(45 deg) / cos(theta_i)        [1/sr]
(same exposure, gain and lamp distance as the white shot). C is first made linear: C_lin = (C - C_d)^gamma,
gamma from an exposure series (gamma = 1: the camera is already linear; ~2.2: sRGB-like output) [R5].
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .imageio import centre_mean, default_reader

DEFAULT_CAL = Path(__file__).resolve().parents[2] / "config" / "calibration.yaml"
AXES = ("M4", "M3", "M2", "M1")
BLANK = {"schema": 1, "angle_offset_deg": dict.fromkeys(AXES, 0.0), "gamma": 1.0, "dark_counts": None, "spectral_dark": None,
         "white": None, "drift_limit_pct": 2.0, "max_age_days": 30,
         "dates": {"angle_offset_deg": None, "gamma": None, "dark_counts": None, "spectral_dark": None, "white": None}}


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
        """Camera counts -> value proportional to light (dark removed, response undone)."""
        return max(counts - self.dark, 0.0) ** self.gamma

    def brdf(self, counts: float, theta_i_deg: float) -> float | None:
        """Counts -> f_r [1/sr] using the PTFE white shot; None until `calibrate white` has run."""
        w = self.data.get("white")
        if not w or theta_i_deg >= 89.0:
            return None
        ref = self.linear(float(w["counts"]))
        return self.linear(counts) / ref * float(w["rho"]) / math.pi * \
            math.cos(math.radians(float(w["theta_i_deg"]))) / math.cos(math.radians(theta_i_deg))

    def snapshot(self) -> dict:
        """Copied into every manifest.json so old data stays traceable."""
        return {k: copy.deepcopy(self.data.get(k)) for k in ("angle_offset_deg", "gamma", "dark_counts", "white", "dates")}

    # ---- write -----------------------------------------------------------
    def set(self, key: str, value, today: dt.date | None = None) -> None:
        self.data[key] = value
        self.data.setdefault("dates", {})[key] = (today or dt.date.today()).isoformat()

    def save(self, path: str | Path | None = None) -> Path:
        p = Path(path or self.path or DEFAULT_CAL)
        head = "".join(l + "\n" for l in DEFAULT_CAL.read_text(encoding="utf-8").splitlines()[:3]) if DEFAULT_CAL.exists() else ""
        p.write_text(head + yaml.safe_dump(self.data, sort_keys=False, default_flow_style=None, width=120), encoding="utf-8")
        return p


def load_calibration(path: str | Path = DEFAULT_CAL) -> Calibration:
    p = Path(path)
    data = copy.deepcopy(BLANK)
    if p.exists():
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        data.update({k: v for k, v in raw.items() if k not in ("angle_offset_deg", "dates")})
        data["angle_offset_deg"].update(raw.get("angle_offset_deg") or {})
        data["dates"].update(raw.get("dates") or {})
    return Calibration(data, p)


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


def from_dark(cal: Calibration, run: str | Path, read_image=None, today=None) -> dict:
    m, read = _manifest(run), read_image or default_reader()
    vals = [centre_mean(read(Path(run) / s["file"])) for s in m["shots"] if s.get("file")]
    out = {}
    if vals:
        cal.set("dark_counts", round(sum(vals) / len(vals), 3), today)
        out["dark_counts"] = cal.data["dark_counts"]
    spec = [s["spectral"] for s in m["shots"] if "spectral" in s]
    if spec:
        cal.set("spectral_dark", [round(sum(c) / len(c), 1) for c in zip(*spec)], today)
        out["spectral_dark"] = cal.data["spectral_dark"]
    return out


def from_white(cal: Calibration, run: str | Path, cfg, rho: float = 0.99, read_image=None, today=None) -> dict:
    from .gantry.kinematics import brdf_coords
    m, read = _manifest(run), read_image or default_reader()
    shots = [s for s in m["shots"] if s.get("file")]
    vals = [centre_mean(read(Path(run) / s["file"])) for s in shots]
    ti = brdf_coords(cfg, shots[0]["pose"]).theta_i
    w = {"counts": round(sum(vals) / len(vals), 3), "theta_i_deg": round(ti, 2), "rho": rho,
         "exposure_ms": m.get("exposure_ms")}
    cal.set("white", w, today)
    return w


def linearity(exposures_ms: list[float], counts: list[float], dark: float, top: float = 240.0) -> dict:
    """Fit log(C - C_d) = (1/gamma) log(t) + k over unsaturated points (C_d + 5 < C < top)."""
    pts = [(math.log(t), math.log(c - dark)) for t, c in zip(exposures_ms, counts) if dark + 5 < c < top]
    if len(pts) < 3:
        raise ValueError("need >= 3 exposures between dark and saturation: change --exposures")
    x = [p[0] for p in pts]
    y = [p[1] for p in pts]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxx = sum((a - mx) ** 2 for a in x)
    slope = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx
    ss_res = sum((b - (my + slope * (a - mx))) ** 2 for a, b in zip(x, y))
    ss_tot = sum((b - my) ** 2 for b in y) or 1e-12
    return {"gamma": round(1 / slope, 3), "r2": round(1 - ss_res / ss_tot, 5), "points_used": len(pts)}


def from_linearity(cal: Calibration, run: str | Path, read_image=None, today=None) -> dict:
    m, read = _manifest(run), read_image or default_reader()
    shots = [s for s in m["shots"] if s.get("file")]
    res = linearity([s["exposure_ms"] for s in shots], [centre_mean(read(Path(run) / s["file"])) for s in shots], cal.dark)
    cal.set("gamma", res["gamma"], today)
    return res
