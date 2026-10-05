"""Check a job folder (manifest.json + images) on the laptop: `opengonio verify DIR`."""
from __future__ import annotations

import json
from pathlib import Path

from .gantry.collision import pose_is_safe
from .gantry.config import Machine


def verify(run_dir: str | Path, cfg: Machine, read_image=None) -> dict:
    """read_image(path) -> 2-D/3-D array or None; default uses OpenCV when installed."""
    d = Path(run_dir)
    m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    shots = m.get("shots", [])
    rep = {"job": m.get("job"), "shots": len(shots), "finished": bool(m.get("finished")),
           "missing": [], "unsafe": [], "saturated": [], "dark": [], "notes": []}
    if read_image is None:
        try:
            import cv2
            read_image = lambda p: cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)  # noqa: E731
        except ImportError:
            read_image = lambda p: None  # noqa: E731
            rep["notes"].append("OpenCV not installed: image checks skipped")
    means = []
    for s in shots:
        f = d / s["file"]
        if not f.exists() or f.stat().st_size == 0:
            rep["missing"].append(s["file"])
            continue
        if not pose_is_safe(cfg, {**cfg.default_pose(), **s["pose"]}):
            rep["unsafe"].append(s["file"])
        img = read_image(f)
        if img is not None:
            import numpy as np
            a = np.asarray(img, dtype=float)
            if (a >= 254).mean() > 0.01:
                rep["saturated"].append(s["file"])
            if a.mean() < 2:
                rep["dark"].append(s["file"])
            h, w = a.shape[:2]
            means.append(a[h // 3: 2 * h // 3, w // 3: 2 * w // 3].mean())
    if str(m.get("job", "")).startswith("Mirror") and means and len(means) == len(shots):
        k = max(range(len(means)), key=means.__getitem__)
        p = shots[k]["pose"]
        err = p["M3"] - p["M4"] / 2
        rep["mirror_peak_error_deg"] = round(err, 3)
        if abs(err) > 0.5:
            rep["notes"].append(f"mirror peak {err:+.2f} deg from M3 = M4/2: recalibrate angles")
    bad = rep["missing"] or rep["unsafe"] or not rep["finished"]
    warn = rep["saturated"] or rep["dark"] or abs(rep.get("mirror_peak_error_deg", 0)) > 0.5
    rep["result"] = "FAIL" if bad else "WARN" if warn else "PASS"
    return rep
