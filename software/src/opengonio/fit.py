"""Fit a game-engine material to a measured curve: `opengonio fit data/<run>` -> fit.json + fit.svg (stage 07, M24).

Model: Lambert diffuse + GGX specular, metallic-roughness parameters (the glTF / Unreal / Unity / Blender
convention) [R6][R2]. Grey (one channel): base colour is a single value 0–1.
Search: coarse grid over (base colour, roughness, metallic), then three finer grids around the best point;
the error is the RMS of f_r - model over all rows, reported as % of the measured peak.
Validation: the same fit on 4 of every 5 rows, scored on the 5th (holdout RMS); a holdout RMS far above the fit RMS
means the model or the sampling does not support the parameters. fit.json records what was fitted (curve file and
calibration id, quantity, model) - a material fitted to relative values is labelled so.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np


def _vec(theta, phi) -> np.ndarray:
    t, p = np.radians(theta), np.radians(phi)
    return np.stack([np.sin(t) * np.cos(p), np.sin(t) * np.sin(p), np.cos(t)], axis=-1)


def ggx(wi: np.ndarray, wo: np.ndarray, base: float, rough: float, metal: float, f0_d: float = 0.04) -> np.ndarray:
    """Vectorised twin of brdf.models.ggx_brdf (same formula, arrays of unit vectors, normal = +Z)."""
    ci, co = wi[..., 2], wo[..., 2]
    h = wi + wo
    h = h / np.linalg.norm(h, axis=-1, keepdims=True)
    a = max(rough * rough, 1e-4)
    a2 = a * a
    ch = h[..., 2]
    d = a2 / (math.pi * (ch * ch * (a2 - 1) + 1) ** 2)
    g = 2 * ci * co / (co * np.sqrt(ci * ci * (1 - a2) + a2) + ci * np.sqrt(co * co * (1 - a2) + a2))
    f0 = f0_d * (1 - metal) + base * metal
    f = f0 + (1 - f0) * (1 - np.clip((wi * h).sum(-1), 0, 1)) ** 5
    out = d * g * f / (4 * ci * co) + (1 - metal) * (1 - f) * base / math.pi
    return np.where((ci > 0) & (co > 0), out, 0.0)


def load_curve(run: str | Path) -> dict[str, np.ndarray]:
    rows = [r for r in csv.DictReader((Path(run) / "curve.csv").open(encoding="utf-8")) if r.get("brdf_per_sr")]
    if not rows:
        raise ValueError("curve.csv has no brdf_per_sr values: run `opengonio calibrate dark` and `calibrate white` first")
    col = lambda k: np.array([float(r[k]) for r in rows])  # noqa: E731
    return {"theta_i": col("theta_i"), "phi_i": col("phi_i"), "theta_r": col("theta_r"), "phi_r": col("phi_r"),
            "f": col("brdf_per_sr")}


def fit(data: dict[str, np.ndarray]) -> dict:
    wi, wo, f = _vec(data["theta_i"], data["phi_i"]), _vec(data["theta_r"], data["phi_r"]), data["f"]
    err = lambda p: float(np.sqrt(np.mean((ggx(wi, wo, *p) - f) ** 2)))  # noqa: E731
    grids = [np.linspace(0, 1, 21), np.linspace(0.05, 1, 20), np.linspace(0, 1, 11)]
    best = min(((b, r, m) for b in grids[0] for r in grids[1] for m in grids[2]), key=err)
    span = [0.05, 0.05, 0.1]
    for _ in range(3):
        cand = [np.clip(np.linspace(best[k] - span[k], best[k] + span[k], 9), lo, 1.0)
                for k, lo in enumerate((0.0, 0.03, 0.0))]
        best = min(((b, r, m) for b in cand[0] for r in cand[1] for m in cand[2]), key=err)
        span = [s / 4 for s in span]
    b, r, m = (round(float(v), 3) for v in best)
    rms = err(best)
    peak = float(f.max())
    return {"base_color": b, "roughness": r, "metallic": m, "rms_per_sr": round(rms, 5),
            "rms_pct_of_peak": round(100 * rms / peak, 2), "rows": int(len(f)),
            "engines": {"glTF / Blender Principled BSDF": {"Base Color": [b, b, b], "Roughness": r, "Metallic": m},
                        "Unreal": {"BaseColor": [b, b, b], "Roughness": r, "Metallic": m, "Specular": 0.5},
                        "Unity (URP Lit, metallic)": {"Base Map": [b, b, b], "Smoothness": round(1 - r, 3), "Metallic": m}}}


def holdout(data: dict[str, np.ndarray], every: int = 5) -> dict | None:
    """Fit on all rows except every `every`-th, score on those. None when there are too few rows to hold any out."""
    n = len(data["f"])
    test = np.arange(n) % every == every - 1
    if test.sum() < 2 or (~test).sum() < 6:
        return None
    train = fit({k: v[~test] for k, v in data.items()})
    wi, wo = _vec(data["theta_i"][test], data["phi_i"][test]), _vec(data["theta_r"][test], data["phi_r"][test])
    pred = ggx(wi, wo, train["base_color"], train["roughness"], train["metallic"])
    rms = float(np.sqrt(np.mean((pred - data["f"][test]) ** 2)))
    return {"rows_held_out": int(test.sum()), "rule": f"every {every}th row", "rms_per_sr": round(rms, 5),
            "rms_pct_of_peak": round(100 * rms / float(data["f"].max()), 2),
            "params_from_training_rows": {k: train[k] for k in ("base_color", "roughness", "metallic")}}


def fit_run(run: str | Path) -> dict:
    from . import __version__
    from .plot import line_chart
    d = Path(run)
    data = load_curve(d)
    res = fit(data)
    meta = d / "curve.json"
    cprov = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else {}
    res["holdout"] = holdout(data)
    res["provenance"] = {"curve": "curve.csv", "calibration": cprov.get("calibration"),
                         "relative_only": cprov.get("relative_only"), "software": f"opengonio {__version__}",
                         "quantity": "grey BRDF of the signal plane mean(R,G,B) (one channel: no colour)",
                         "model": "Lambert + GGX, metallic-roughness, F0 dielectric 0.04",
                         "note": "an engine material approximates the measured curve; check holdout before use"}
    (d / "fit.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    inplane = np.abs(np.abs(((data["phi_r"] - data["phi_i"] + 180) % 360) - 180) - 180) < 1.0
    inplane |= (data["theta_i"] < 0.5) | (data["theta_r"] < 0.5)
    series = []
    tis = sorted(set(np.round(data["theta_i"][inplane]).tolist()))
    for ti in [t for t in tis if t > 0][:: max(1, len(tis) // 4)][:4]:
        sel = inplane & (np.round(data["theta_i"]) == ti)
        tr = np.linspace(0, max(data["theta_r"][sel].max(), 1), 60)
        wi = _vec(np.full_like(tr, ti), np.zeros_like(tr))
        wo = _vec(tr, np.full_like(tr, 180.0))
        model = ggx(wi, wo, res["base_color"], res["roughness"], res["metallic"])
        series.append({"label": f"θi {ti:g}°", "points": list(zip(data["theta_r"][sel], data["f"][sel])),
                       "line": list(zip(tr, model))})
    (d / "fit.svg").write_text(line_chart(
        series, f"Fit: base {res['base_color']}, roughness {res['roughness']}, metallic {res['metallic']}",
        "θr (deg, in the plane of incidence)", "BRDF (1/sr)",
        f"RMS {res['rms_pct_of_peak']} % of peak over {res['rows']} rows"), encoding="utf-8")
    return res
