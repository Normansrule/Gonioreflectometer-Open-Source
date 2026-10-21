"""Check a run folder (manifest.json + images) on the laptop: `opengonio verify DIR`, then `opengonio curve DIR`.

Four separate statements, each reported on its own:
  acquisition_complete  the run finished and recorded every planned shot (no duplicates, no extras)
  data_valid            every shot has evidence (a decodable image matching its hash and/or a 10-value spectral
                        reading), a pose inside every axis range and the keep-out, and a controller-reported pose
                        that agrees with the requested one
  measurement_valid     lamp drift within the limit
  calibrated            the run's own calibration snapshot supports absolute BRDF (white reference, same exposure)
result: FAIL unless the first three hold; WARN for clipped/dark images, mirror peak > 0.5 deg off, stale
calibration; PASS otherwise. A run that is PASS but not `calibrated` gives relative values only.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import numpy as np

from .calibration import Calibration, from_snapshot, load_calibration
from .gantry.collision import pose_is_safe
from .gantry.config import Machine
from .imageio import clipped, decoded, default_reader, region_mean, signal_plane
from .runrecord import SCHEMA, sha256_file

CLEAR = 8                   # AS7341 clear channel index in SPECTRAL_CHANNELS
N_SPECTRAL = 10             # F1-F8, CLEAR, NIR
SPECTRAL_MAX = 65535        # 16-bit ADC
POSE_TOL_DEG = 0.01         # requested vs controller-reported pose (default; controller.position_tol_deg overrides)


def pose_problems(cfg: Machine, pose: dict) -> list[str]:
    """Every axis known, finite, inside its configured range; whole pose outside the keep-out."""
    out = []
    if not isinstance(pose, dict) or not pose:
        return ["no pose"]
    for k, v in pose.items():
        if k not in cfg.axes:
            out.append(f"unknown axis {k}")
            continue
        try:
            v = float(v)
        except (TypeError, ValueError):
            out.append(f"{k}={v!r} not a number")
            continue
        if not np.isfinite(v) or not cfg.axes[k].in_range(v):
            out.append(f"{k}={v} outside [{cfg.axes[k].min_deg}, {cfg.axes[k].max_deg}]")
    if not out and not pose_is_safe(cfg, {**cfg.default_pose(), **{k: float(v) for k, v in pose.items()}}):
        out.append("pose inside the keep-out")
    return out


def spectral_problems(vals) -> list[str]:
    if not isinstance(vals, (list, tuple)) or len(vals) != N_SPECTRAL:
        n = len(vals) if isinstance(vals, (list, tuple)) else repr(vals)
        return [f"spectral reading needs {N_SPECTRAL} values, got {n}"]
    bad = [v for v in vals if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= SPECTRAL_MAX
           or (isinstance(v, float) and not v.is_integer())]
    return [f"spectral values out of range or not integer: {bad[:3]}"] if bad else []


def _ref_mean(m: dict, d: Path, key: str, read, cal: Calibration):
    r = (m.get("reference") or {}).get(key) or {}
    if r.get("file") and (d / r["file"]).exists():
        img = read(d / r["file"])
        return region_mean(img, linear=cal.linear_array) if decoded(img) else None
    if "spectral" in r and not spectral_problems(r["spectral"]):
        return float(r["spectral"][CLEAR])
    return None


def _drift(m: dict, d: Path, read, cal: Calibration) -> float | str | None:
    """Lamp drift in % between the reference shots (camera; spectral clear channel if no images).
    None = no reference shots; "dark" = reference too dark to judge (e.g. off the mirror peak)."""
    s, e = _ref_mean(m, d, "start", read, cal), _ref_mean(m, d, "end", read, cal)
    if s is None or e is None:
        return None
    return "dark" if s < 5 else round(100.0 * (e - s) / s, 2)


def _shot_checks(cfg: Machine, d: Path, s: dict, read, rep: dict, schema: int = SCHEMA) -> tuple[np.ndarray | None, list[str]]:
    """Problems of one shot (data validity). Returns (decoded image or None, problems).
    Schema 2+ records must carry the controller-reported pose and, for an image, its hash: missing = invalid."""
    probs = pose_problems(cfg, s.get("pose"))
    rp = s.get("reported_pose")
    tol = float(cfg.controller.get("position_tol_deg", POSE_TOL_DEG))
    if schema >= 2 and not isinstance(rp, dict):
        probs.append("no controller-reported pose")
    if isinstance(rp, dict) and isinstance(s.get("pose"), dict):
        off = [k for k, v in s["pose"].items() if k not in rp or abs(float(rp[k]) - float(v)) > tol]
        if off:
            got = ", ".join(f"{k}={rp.get(k)}" for k in off)
            want = ", ".join(f"{k}={s['pose'][k]}" for k in off)
            probs.append(f"controller reported {got} (requested {want})")
    has_file, has_spec = bool(s.get("file")), "spectral" in s
    if not has_file and not has_spec:
        probs.append("no evidence (no image, no spectral reading)")
    if has_spec:
        probs += spectral_problems(s["spectral"])
    img = None
    if has_file:
        f = d / s["file"]
        if not f.exists() or f.stat().st_size == 0:
            rep["missing"].append(s["file"])
            probs.append(f"image missing: {s['file']}")
        else:
            if s.get("sha256"):
                if sha256_file(f) != s["sha256"]:
                    probs.append(f"image changed since capture (hash): {s['file']}")
            elif schema >= 2:
                probs.append(f"no hash recorded for {s['file']}")
            img = read(f)
            if not decoded(img):
                rep["corrupt"].append(s["file"])
                probs.append(f"image not decodable: {s['file']}")
                img = None
            elif s.get("shape") and list(np.asarray(img).shape) != list(s["shape"]):
                probs.append(f"image shape {list(np.asarray(img).shape)} differs from capture {s['shape']}")
    return img, probs


def verify(run_dir: str | Path, cfg: Machine, read_image=None, cal: Calibration | None = None) -> dict:
    """read_image(path) -> 2-D/3-D array or None; default: OpenCV if installed, else the built-in PNG reader.
    cal: the CURRENT calibration; only used for fields an old (schema 1) manifest did not store."""
    d = Path(run_dir)
    rep = {"run": str(d), "result": "FAIL", "acquisition_complete": False, "data_valid": False,
           "measurement_valid": False, "calibrated": False, "missing": [], "corrupt": [], "invalid_shots": {},
           "unsafe": [], "saturated": [], "dark": [], "problems": [], "notes": []}
    mf = d / "manifest.json"
    try:
        m = json.loads(mf.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        rep["problems"].append(f"manifest.json unreadable: {exc}")
        return rep
    read = read_image or default_reader()
    current = cal or load_calibration()
    cal, prov = from_snapshot(m.get("calibration"), current)
    rep.update({"job": m.get("job"), "run_id": m.get("run_id"), "schema": m.get("schema", 1), "calibration": prov})
    if rep["schema"] < SCHEMA:
        rep["notes"].append(f"legacy manifest (schema {rep['schema']}): no planned count, status or file hashes to check")
    if rep["schema"] > SCHEMA:
        rep["problems"].append(f"manifest schema {rep['schema']} is newer than this software ({SCHEMA}): update opengonio")
    shots = m.get("shots", [])
    rep["shots"] = len(shots)
    status = m.get("status", "finished" if m.get("finished") else "running")
    rep["status"] = status

    # ---- acquisition complete
    complete = []
    if status != "finished" or not m.get("finished"):
        why = "; ".join(m.get("errors", []))
        complete.append(f"run not finished (status {status}{': ' + why if why else ''})")
    if m.get("aborted"):
        complete.append(f"aborted: {m['aborted']}")
    if not shots:
        complete.append("run has no shots")
    planned = m.get("planned")
    if planned is None and rep["schema"] >= 2:
        complete.append("no planned shot count recorded")
    if planned is not None and len(shots) != int(planned):
        complete.append(f"{len(shots)} shots recorded, {planned} planned")
    ids = [s.get("i") for s in shots]
    if len(set(ids)) != len(ids):
        complete.append("duplicate shot numbers")
    elif planned is not None and sorted(i for i in ids if isinstance(i, int)) != list(range(int(planned))):
        complete.append("shot numbers are not 0..planned-1")
    if m.get("cleanup_errors"):
        rep["notes"].append("cleanup errors: " + "; ".join(m["cleanup_errors"]))
    rep["acquisition_complete"] = not complete

    # ---- data valid
    means = []
    for s in shots:
        img, probs = _shot_checks(cfg, d, s, read, rep, rep["schema"])
        key = str(s.get("i", s.get("file")))
        if probs:
            rep["invalid_shots"][key] = probs
            if any("keep-out" in p or "outside" in p for p in probs):
                rep["unsafe"].append(key)
        if img is not None:
            plane = signal_plane(img)
            if clipped(img).mean() > 0.01:
                rep["saturated"].append(s["file"])
            if plane.mean() < 2:
                rep["dark"].append(s["file"])
            means.append(region_mean(plane))
    for k in ("start", "end"):
        r = (m.get("reference") or {}).get(k)
        if r:
            _, probs = _shot_checks(cfg, d, r, read, rep, rep["schema"])
            if probs:
                rep["invalid_shots"][f"reference {k}"] = probs
    rep["data_valid"] = bool(shots) and not rep["invalid_shots"]
    if m.get("light") is None and "light" in m:
        rep["dark"] = []                                    # dark-frame run: dark is the point

    # ---- mirror peak (angle calibration input)
    if "mirror" in str(m.get("job", "")).lower() and means and len(means) == len(shots):
        k = max(range(len(means)), key=means.__getitem__)
        p = shots[k]["pose"]
        err = p["M3"] - p["M4"] / 2
        rep["mirror_peak_error_deg"] = round(err, 3)
        if abs(err) > 0.5:
            rep["notes"].append(f"mirror peak {err:+.2f} deg from M3 = M4/2: run `opengonio calibrate mirror`")

    # ---- measurement valid: lamp drift
    drift = _drift(m, d, read, cal)
    drift_bad = False
    if drift == "dark":
        rep["notes"].append("reference pose too dark to measure lamp drift (normal for mirror runs)")
    elif drift is not None:
        rep["lamp_drift_pct"] = drift
        drift_bad = abs(drift) > cal.drift_limit_pct
        if drift_bad:
            rep["problems"].append(f"lamp drift {drift:+.2f} % > {cal.drift_limit_pct} %: longer warm-up "
                                   "(lights.white.warmup_s) or check the driver")
    elif m.get("light") and not m.get("reference"):
        rep["notes"].append("no reference shots: lamp drift unknown")
    rep["measurement_valid"] = rep["acquisition_complete"] and rep["data_valid"] and not drift_bad

    # ---- calibration support (the run's own snapshot)
    stale = []
    if (m.get("calibration") or {}).get("dates"):
        started = dt.datetime.strptime(m["started"][:8], "%Y%m%d").date() if m.get("started") else None
        stale = cal.stale(started)
        if stale:
            rep["notes"].append(f"calibration older than {cal.data.get('max_age_days', 30)} days at capture: {', '.join(stale)}")
    cal_probs = cal.brdf_problems(m.get("exposure_ms")) if m.get("light") else ["dark run"]
    rep["calibrated"] = not cal_probs and not stale
    if m.get("light") and cal_probs:
        rep["notes"].append("relative values only: " + "; ".join(cal_probs))

    rep["problems"] = complete + rep["problems"]
    bad = rep["problems"] or not rep["acquisition_complete"] or not rep["data_valid"]
    warn = rep["saturated"] or rep["dark"] or abs(rep.get("mirror_peak_error_deg", 0)) > 0.5 or stale
    rep["result"] = "FAIL" if bad else "WARN" if warn else "PASS"
    return rep


def curve(run_dir: str | Path, cfg: Machine, read_image=None, cal: Calibration | None = None,
          recalibrate: bool = False) -> Path:
    """curve.csv: angles, raw counts, linear signal, BRDF in 1/sr, valid-region size and angular acceptance per pose
    (+ spectral channels). Uses the calibration stored with the run. recalibrate=True applies `cal` instead and writes
    a separately labelled revision (curve_recal-<id>.csv) with its provenance; the original curve is never replaced."""
    from dataclasses import replace

    from . import __version__
    from .calibration import calibration_id
    from .gantry.kinematics import brdf_coords
    from .roi import sample_roi
    d = Path(run_dir)
    m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    current = cal or load_calibration()
    if recalibrate:
        use, prov = current, {"source": "recalibrated (explicit)", "id": calibration_id(current.data),
                              "capture_id": (m.get("calibration") or {}).get("id")}
    else:
        use, prov = from_snapshot(m.get("calibration"), current)
    read = read_image or default_reader()
    cal_probs = use.brdf_problems(m.get("exposure_ms"))
    has_spec = any("spectral" in s for s in m["shots"])
    scfg = replace(cfg, camera_elevation_deg=cfg.camera_elevation_deg + float(cfg.spectral.get("elevation_deg", 0.0)))
    rows = ["i,M4,M3,M2,M1,theta_i,phi_i,theta_r,phi_r,delta_phi,centre_mean,linear_mean,brdf_per_sr,"
            "roi_mm2,view_spread_deg,incidence_spread_deg,valid" + (",spec_theta_r,spectral" if has_spec else "")]
    skipped = {}
    for s in m["shots"]:
        pose = {**cfg.default_pose(), **s["pose"]}
        b = brdf_coords(cfg, pose)
        mean = lin = f_r = area = vs = isp = ""
        valid = "no image"
        if s.get("file") and (d / s["file"]).exists():
            img = read(d / s["file"])
            if decoded(img):
                roi = sample_roi(cfg, pose, np.asarray(img).shape)
                area, vs, isp = f"{roi.area_mm2:.1f}", f"{roi.view_spread_deg:.2f}", f"{roi.incidence_spread_deg:.2f}"
                if roi.valid:
                    raw = region_mean(img, mask=roi.mask)
                    lv = region_mean(img, mask=roi.mask, linear=use.linear_array, reject_saturated=True)
                    mean = f"{raw:.2f}"
                    if lv is None:
                        valid = "clipped"
                    else:
                        lin = f"{lv:.4f}"
                        v = None if cal_probs else use.brdf_linear(lv, b.theta_i)
                        f_r = "" if v is None else f"{v:.5f}"
                        valid = "yes" if v is not None else "relative"
                else:
                    valid = roi.reason.replace(",", ";")
            else:
                valid = "undecodable"
        if valid not in ("yes", "relative"):
            skipped[str(s["i"])] = valid
        spec = (f",{brdf_coords(scfg, pose).theta_r:.2f},\"" + " ".join(str(v) for v in s["spectral"]) + "\"") if "spectral" in s else ""
        rows.append(f"{s['i']},{pose['M4']},{pose['M3']},{pose['M2']},{pose['M1']},{b.theta_i:.2f},{b.phi_i:.2f},"
                    f"{b.theta_r:.2f},{b.phi_r:.2f},{b.delta_phi:.2f},{mean},{lin},{f_r},{area},{vs},{isp},{valid}{spec}")
    stem = f"curve_recal-{prov['id']}" if recalibrate else "curve"
    out = d / f"{stem}.csv"
    out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    (d / f"{stem}.json").write_text(json.dumps({"calibration": prov, "relative_only": cal_probs, "software": f"opengonio {__version__}",
                                                "quantity": "signal plane = mean(R,G,B), linearised per pixel, mean over the valid region",
                                                "rows_without_value": skipped}, indent=1), encoding="utf-8")
    (d / f"{stem}.svg").write_text(curve_svg(m, rows), encoding="utf-8")
    return out


def curve_svg(m: dict, rows: list[str]) -> str:
    """Picture of the run: mirror runs -> brightness vs M3 with the M3 = M4/2 line; others -> in-plane curves per theta_i."""
    from .plot import line_chart
    head = rows[0].split(",")
    data = [dict(zip(head, r.split(",")[:len(head)])) for r in rows[1:]]
    data = [r for r in data if r.get("centre_mean")]
    job = str(m.get("job", "run"))
    if "mirror" in job.lower() and data:
        pts = [(float(r["M3"]), float(r["centre_mean"])) for r in data]
        m4 = float(data[0]["M4"])
        return line_chart([{"label": job, "points": pts}], f"{job}: brightness vs table angle", "M3 (deg)",
                          "centre brightness (counts)", "peak should sit on the orange line; `verify` reports the gap",
                          vline=(m4 / 2, f"M3 = M4/2 = {m4 / 2:g}°"))
    use_f = any(r.get("brdf_per_sr") for r in data)
    key = "brdf_per_sr" if use_f else "centre_mean"
    inpl = [r for r in data if r.get(key) and (abs(float(r["delta_phi"]) - 180) < 1 or float(r["theta_i"]) < 0.5 or float(r["theta_r"]) < 0.5)]
    tis = sorted({round(float(r["theta_i"])) for r in inpl if float(r["theta_i"]) > 0})
    pick = tis[:: max(1, -(-len(tis) // 4))][:4]
    series = [{"label": f"θi {ti}°", "points": sorted((float(r["theta_r"]), float(r[key])) for r in inpl
                                                     if round(float(r["theta_i"])) == ti)} for ti in pick]
    note = f"in-plane rows; showing θi {', '.join(str(t) for t in pick)}° of {len(tis)} (all values in curve.csv)"
    return line_chart(series, f"{job}: reflectance vs viewing angle", "θr (deg, in the plane of incidence)",
                      "BRDF (1/sr)" if use_f else "centre brightness (counts) — run calibrate white for 1/sr", note)
