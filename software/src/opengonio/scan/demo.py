"""Offline demo: synthetic sphere -> silhouette carving + photometric stereo, no hardware.

    opengonio scan demo --out scan_demo
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from ..gantry.config import Machine
from .carve import carve, sphere_mask, write_ply
from .geometry import intrinsics, light_in_object, object_to_camera
from .photometric import render_lambert, solve
from .plan import photometric_stations, rings_plan


def run(cfg: Machine, out_dir: str | Path = "scan_demo", radius: float = 30.0, scale: float = 0.05) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    scfg = cfg.for_scan()
    K = intrinsics(scfg, cfg.scan["camera_distance_mm"]).scaled(scale)
    plan = rings_plan(cfg)[::3]
    center = np.array([0.0, 0.0, 0.0])
    views = [object_to_camera(scfg, sp.pose) for sp in plan]
    masks = [sphere_mask(center, radius, K.K, R, t, K.width, K.height) for R, t in views]
    grid = carve(masks, views, K.K, half_size_mm=1.4 * radius, n=56)
    r_eq = (3 * grid.volume_mm3 / (4 * math.pi)) ** (1 / 3)
    write_ply(out / "visual_hull.ply", grid.surface_points())

    st = photometric_stations(cfg)[0]
    L = np.array([light_in_object(cfg, st, float(m)) for m in cfg.scan["ps_m4_deg"]])
    yy, xx = np.mgrid[-1:1:64j, -1:1:64j]
    zz = np.sqrt(np.clip(1 - xx ** 2 - yy ** 2, 0, None))
    n_true = np.dstack([xx, yy, zz])
    n_true /= np.linalg.norm(n_true, axis=-1, keepdims=True)
    # orient the test hemisphere toward the camera (what the camera actually sees)
    from .geometry import camera_center_object
    Rc, tc = object_to_camera(scfg, st)
    axis = camera_center_object(Rc, tc)
    axis = axis / np.linalg.norm(axis)
    z = np.array([0.0, 0.0, 1.0])
    v = np.cross(z, axis)
    c = float(z @ axis)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    Rz = np.eye(3) + vx + vx @ vx / (1 + c)
    n_true = n_true @ Rz.T
    imgs = render_lambert(n_true, np.full(n_true.shape[:2], 0.6), L) * 0.9
    res = solve(imgs, L)
    ang = np.degrees(np.arccos(np.clip((res.normals * n_true).sum(-1), -1, 1)))[res.valid]
    return {"views": len(plan), "voxel_mm": round(grid.voxel_mm, 2),
            "sphere_radius_mm": radius, "visual_hull_equiv_radius_mm": round(r_eq, 2),
            "ps_lights": len(L), "ps_median_normal_error_deg": round(float(np.median(ang)), 3),
            "ps_valid_fraction": round(float(res.valid.mean()), 3), "ply": str(out / "visual_hull.ply")}
