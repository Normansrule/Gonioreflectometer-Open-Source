"""Process a scan folder written by `opengonio scan run` (stage 12).

    opengonio scan hull --out scan_cube --voxel 0.5      silhouettes -> hull.ply + size of the object (S4)
    opengonio scan ps --out scan_ball --sphere           photometric stereo -> normals.png, albedo.png (+ error on a sphere, S6)

Hull: mask = |image - empty-platter image| > threshold [S5]; carve a voxel cube with the known poses [S6].
PS: one station, k LED-bank directions (object frame, from scan.json) -> per-pixel normal and albedo [S4].
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ..gantry.config import Machine
from ..imageio import default_reader, write_png
from .carve import carve, silhouette_from_background, write_ply
from .geometry import Intrinsics, object_to_camera
from .photometric import solve


def _meta(folder: Path) -> dict:
    return json.loads((folder / "scan.json").read_text(encoding="utf-8"))


def _calib(cfg: Machine, meta: dict):
    if meta.get("calibrated") and cfg.scan.get("calibration"):
        from .calibrate import CameraCalibration
        return CameraCalibration.load(cfg.scan["calibration"])
    return None


def _grey(a) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    return a.mean(axis=2) if a.ndim == 3 else a


def hull(cfg: Machine, folder: str | Path, voxel_mm: float = 1.0, downscale: int = 4, threshold: float = 12.0,
         clip_below_mm: float | None = None, read=None) -> dict:
    folder = Path(folder)
    meta, read = _meta(folder), read or default_reader()
    K = Intrinsics(**meta["intrinsics"]).scaled(1.0 / downscale)
    scfg, calib = cfg.for_scan(), _calib(cfg, meta)
    masks, views = [], []
    for i, pose in enumerate(meta["plan"]):
        name = f"img_{i:04d}"
        f = next((folder / "images" / f"{name}{e}" for e in (".jpg", ".png") if (folder / "images" / f"{name}{e}").exists()), None)
        b = next((folder / "background" / f"{name}{e}" for e in (".jpg", ".png") if (folder / "background" / f"{name}{e}").exists()), None)
        if f is None or b is None:
            continue
        img, bg = _grey(read(f))[::downscale, ::downscale], _grey(read(b))[::downscale, ::downscale]
        masks.append(silhouette_from_background(img, bg, threshold))
        views.append(object_to_camera(scfg, pose, float(meta.get("platter_offset_mm", 0.0)), calib))
    if not masks:
        raise FileNotFoundError("no image + background pairs: run `opengonio scan run --background` and `scan run` first")
    half = 1.1 * float(cfg.scan["object_max_radius_mm"])
    grid = carve(masks, views, K.K, half_size_mm=half, n=int(2 * half / voxel_mm), clip_below_z=clip_below_mm)
    pts = grid.centers()
    write_ply(folder / "hull.ply", grid.surface_points())
    size = (pts.max(0) - pts.min(0) + grid.voxel_mm) if len(pts) else np.zeros(3)
    return {"views": len(masks), "voxel_mm": round(grid.voxel_mm, 3), "size_mm": [round(float(v), 1) for v in size],
            "volume_cm3": round(grid.volume_mm3 / 1000, 2), "ply": str(folder / "hull.ply")}


def ps(cfg: Machine, folder: str | Path, station: int = 0, gamma: float = 1.0, sphere: bool = False, read=None) -> dict:
    folder = Path(folder)
    meta, read = _meta(folder), read or default_reader()
    st = meta["ps"][station]
    L = np.array(st["lights_object_frame"], float)
    imgs = [_grey(read(folder / "ps" / f"st{station:02d}_l{k}.png")) for k in range(len(L))]
    I = (np.clip(np.stack(imgs), 0, 255) / 255.0) ** gamma                    # linear 0-1 [R5]
    res = solve(I, L)
    R_oc, _ = object_to_camera(cfg.for_scan(), st["pose"], float(meta.get("platter_offset_mm", 0.0)), _calib(cfg, meta))
    n_cam = res.normals @ R_oc.T
    rgb = np.where(res.valid[..., None], (n_cam * [1, -1, -1] + 1) / 2 * 255, 0)   # x right, y up, z to viewer
    write_png(folder / f"normals_st{station:02d}.png", rgb)
    write_png(folder / f"albedo_st{station:02d}.png", np.clip(res.albedo / max(res.albedo.max(), 1e-9) * 255, 0, 255))
    out = {"station": station, "lights": len(L), "valid_fraction": round(float(res.valid.mean()), 3),
           "normals": str(folder / f"normals_st{station:02d}.png")}
    if sphere:                                    # S6: compare with the ideal sphere that best fits the normals
        v, u = np.nonzero(res.valid)
        nx, ny = n_cam[v, u, 0], n_cam[v, u, 1]
        # orthographic sphere: u = cu + r nx, v = cv + r ny  ->  least squares for (cu, cv, r)
        A = np.block([[np.ones((len(u), 1)), np.zeros((len(u), 1)), nx[:, None]],
                      [np.zeros((len(u), 1)), np.ones((len(u), 1)), ny[:, None]]])
        cu, cv, r = np.linalg.lstsq(A, np.concatenate([u, v]).astype(float), rcond=None)[0]
        x, y = (u - cu) / r, (v - cv) / r
        inner = x ** 2 + y ** 2 < 0.8 ** 2                                  # skip the limb (perspective, shadows)
        nt = np.stack([x, y, -np.sqrt(np.clip(1 - x ** 2 - y ** 2, 0, None))], -1)[inner]
        nm = n_cam[v[inner], u[inner]]
        out["sphere_radius_px"] = round(float(r), 1)
        ang = np.degrees(np.arccos(np.clip((nt * nm).sum(-1), -1, 1)))
        out["sphere_median_normal_error_deg"] = round(float(np.median(ang)), 2)
    return out
