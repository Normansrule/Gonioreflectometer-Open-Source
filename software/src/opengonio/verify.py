"""Check a job folder (manifest.json + images) on the laptop: `opengonio verify DIR`, then `opengonio curve DIR`.

FAIL  missing image, unsafe pose, run not finished, lamp drift over the limit
WARN  saturated or dark images, mirror peak > 0.5 deg off, calibration older than max_age_days
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .calibration import Calibration, load_calibration
from .gantry.collision import pose_is_safe
from .gantry.config import Machine
from .imageio import centre_mean, default_reader

CLEAR = 8                   # AS7341 clear channel index in SPECTRAL_CHANNELS


def _drift(m: dict, d: Path, read, dark: float) -> float | str | None:
    """Lamp drift in % from the reference shots (camera; spectral clear channel if no images).
    None = no reference shots; "dark" = reference pose too dark to judge (e.g. off the mirror peak)."""
    ref = m.get("reference") or {}
    a, b = ref.get("start"), ref.get("end")
    if not a or not b:
        return None
    if a.get("file") and b.get("file") and (d / a["file"]).exists() and (d / b["file"]).exists():
        ia, ib = read(d / a["file"]), read(d / b["file"])
        if ia is None or ib is None:
            return None
        s, e = centre_mean(ia) - dark, centre_mean(ib) - dark
    elif "spectral" in a and "spectral" in b:
        s, e = float(a["spectral"][CLEAR]), float(b["spectral"][CLEAR])
    else:
        return None
    return "dark" if s < 5 else round(100.0 * (e - s) / s, 2)


def verify(run_dir: str | Path, cfg: Machine, read_image=None, cal: Calibration | None = None) -> dict:
    """read_image(path) -> 2-D/3-D array or None; default: OpenCV if installed, else the built-in PNG reader."""
    d = Path(run_dir)
    m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    cal = cal or load_calibration()
    read = read_image or default_reader()
    shots = m.get("shots", [])
    rep = {"job": m.get("job"), "schema": m.get("schema", 0), "shots": len(shots), "finished": bool(m.get("finished")),
           "missing": [], "unsafe": [], "saturated": [], "dark": [], "notes": []}
    means = []
    for s in shots:
        if not s.get("file"):
            continue
        f = d / s["file"]
        if not f.exists() or f.stat().st_size == 0:
            rep["missing"].append(s["file"])
            continue
        if not pose_is_safe(cfg, {**cfg.default_pose(), **s["pose"]}):
            rep["unsafe"].append(s["file"])
        img = read(f)
        if img is not None:
            import numpy as np
            a = np.asarray(img, dtype=float)
            if (a >= 254).mean() > 0.01:
                rep["saturated"].append(s["file"])
            if a.mean() < 2:
                rep["dark"].append(s["file"])
            means.append(centre_mean(a))
    if m.get("light") is None and "light" in m:
        rep["dark"] = []                                    # dark-frame run: dark is the point
    if "mirror" in str(m.get("job", "")).lower() and means and len(means) == len(shots):
        k = max(range(len(means)), key=means.__getitem__)
        p = shots[k]["pose"]
        err = p["M3"] - p["M4"] / 2
        rep["mirror_peak_error_deg"] = round(err, 3)
        if abs(err) > 0.5:
            rep["notes"].append(f"mirror peak {err:+.2f} deg from M3 = M4/2: run `opengonio calibrate mirror`")
    drift = _drift(m, d, read, cal.dark)
    if drift == "dark":
        drift = None
        rep["notes"].append("reference pose too dark to measure lamp drift (normal for mirror runs)")
    elif drift is not None:
        rep["lamp_drift_pct"] = drift
        if abs(drift) > cal.drift_limit_pct:
            rep["notes"].append(f"lamp drift {drift:+.2f} % > {cal.drift_limit_pct} %: longer warm-up (lights.white.warmup_s) or check the driver")
    elif m.get("light") and not m.get("reference"):
        rep["notes"].append("no reference shots: lamp drift unknown")
    snap = m.get("calibration") or {}
    stale = []
    if snap.get("dates"):
        started = dt.datetime.strptime(m["started"][:8], "%Y%m%d").date() if m.get("started") else None
        c = Calibration({**cal.data, "dates": snap["dates"]})
        stale = c.stale(started)
        if stale:
            rep["notes"].append(f"calibration older than {c.data.get('max_age_days', 30)} days at capture: {', '.join(stale)}")
    drift_bad = drift is not None and abs(drift) > cal.drift_limit_pct
    bad = rep["missing"] or rep["unsafe"] or not rep["finished"] or drift_bad
    warn = rep["saturated"] or rep["dark"] or abs(rep.get("mirror_peak_error_deg", 0)) > 0.5 or stale
    rep["result"] = "FAIL" if bad else "WARN" if warn else "PASS"
    return rep


def curve(run_dir: str | Path, cfg: Machine, read_image=None, cal: Calibration | None = None) -> Path:
    """curve.csv: angles, centre brightness, BRDF in 1/sr (after `calibrate white`), spectral channels if present."""
    from dataclasses import replace

    from .gantry.kinematics import brdf_coords
    d = Path(run_dir)
    m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    cal = cal or load_calibration()
    read = read_image or default_reader()
    has_spec = any("spectral" in s for s in m["shots"])
    scfg = replace(cfg, camera_elevation_deg=cfg.camera_elevation_deg + float(cfg.spectral.get("elevation_deg", 0.0)))
    rows = ["i,M4,M3,M2,M1,theta_i,phi_i,theta_r,phi_r,delta_phi,centre_mean,brdf_per_sr"
            + (",spec_theta_r,spectral" if has_spec else "")]
    for s in m["shots"]:
        pose = {**cfg.default_pose(), **s["pose"]}
        b = brdf_coords(cfg, pose)
        mean = f_r = ""
        if s.get("file") and (d / s["file"]).exists():
            img = read(d / s["file"])
            if img is not None:
                c = centre_mean(img)
                mean = f"{c:.2f}"
                v = None if c >= 250 else cal.brdf(c, b.theta_i)        # saturated: no value rather than a wrong one
                f_r = "" if v is None else f"{v:.5f}"
        spec = (f",{brdf_coords(scfg, pose).theta_r:.2f},\"" + " ".join(str(v) for v in s["spectral"]) + "\"") if "spectral" in s else ""
        rows.append(f"{s['i']},{pose['M4']},{pose['M3']},{pose['M2']},{pose['M1']},{b.theta_i:.2f},{b.phi_i:.2f},"
                    f"{b.theta_r:.2f},{b.phi_r:.2f},{b.delta_phi:.2f},{mean},{f_r}{spec}")
    out = d / "curve.csv"
    out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    (d / "curve.svg").write_text(curve_svg(m, rows), encoding="utf-8")
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
