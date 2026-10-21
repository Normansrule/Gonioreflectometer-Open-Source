"""Silhouette carving (visual hull) with known poses - fast preview and photogrammetry check.

A voxel survives if every view that sees it projects it inside the object silhouette
(visual hull, Laurentini 1994 [S5]; octree/voxel carving, Szeliski 1993 [S6]; space carving
generalises it with photo-consistency, Kutulakos & Seitz 2000 [S7]).
Silhouettes come from the black backdrop: mask = pixel brighter than a threshold.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .geometry import project


@dataclass
class VoxelGrid:
    occ: np.ndarray            # bool (n, n, n)
    origin: np.ndarray         # corner (mm, object frame)
    voxel_mm: float

    def centers(self) -> np.ndarray:
        idx = np.argwhere(self.occ)
        return self.origin + (idx + 0.5) * self.voxel_mm

    @property
    def volume_mm3(self) -> float:
        return float(self.occ.sum()) * self.voxel_mm ** 3

    def surface_points(self) -> np.ndarray:
        o = self.occ
        pad = np.pad(o, 1)
        inner = pad[2:, 1:-1, 1:-1] & pad[:-2, 1:-1, 1:-1] & pad[1:-1, 2:, 1:-1] & \
            pad[1:-1, :-2, 1:-1] & pad[1:-1, 1:-1, 2:] & pad[1:-1, 1:-1, :-2]
        surf = o & ~inner
        return self.origin + (np.argwhere(surf) + 0.5) * self.voxel_mm


def carve(masks: list[np.ndarray], views: list[tuple[np.ndarray, np.ndarray]], K: np.ndarray,
          half_size_mm: float, n: int = 64, center: np.ndarray | None = None,
          clip_below_z: float | None = None, dist=None, max_voxels: int = 20_000_000) -> VoxelGrid:
    """masks: bool images (H, W); views: (R_oc, t_oc) per mask; cube of side 2*half_size around center.
    clip_below_z: drop voxels below the support plane (nest, riser and platter are not the object).
    dist: lens distortion (k1 k2 p1 p2) of the calibrated camera. Memory grows as n^3 (~25 bytes per voxel):
    grids over max_voxels are refused (choose a coarser --voxel)."""
    if n ** 3 > max_voxels:
        raise MemoryError(f"{n}^3 = {n ** 3:,} voxels (~{n ** 3 * 25 / 1e9:.1f} GB) exceeds {max_voxels:,}: use a coarser voxel")
    c = np.zeros(3) if center is None else np.asarray(center, float)
    vox = 2.0 * half_size_mm / n
    origin = c - half_size_mm
    g = (np.arange(n) + 0.5) * vox
    X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
    pts = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()]) + origin
    keep = np.ones(len(pts), bool)
    if clip_below_z is not None:
        keep &= pts[:, 2] >= clip_below_z
    for mask, (R, t) in zip(masks, views):
        h, w = mask.shape
        uv, z = project(pts[keep], K, R, t, dist)
        u = np.floor(np.nan_to_num(uv[:, 0], nan=-1.0)).astype(int)
        v = np.floor(np.nan_to_num(uv[:, 1], nan=-1.0)).astype(int)
        inside = (z > 0) & (u >= 0) & (u < w) & (v >= 0) & (v < h)
        ok = np.ones(len(u), bool)                       # outside the image: no evidence, keep
        ok[inside] = mask[v[inside], u[inside]]
        idx = np.flatnonzero(keep)
        keep[idx[~ok]] = False
    return VoxelGrid(keep.reshape(n, n, n), origin, vox)


def sphere_mask(center: np.ndarray, radius: float, K: np.ndarray, R: np.ndarray, t: np.ndarray,
                width: int, height: int) -> np.ndarray:
    """Exact silhouette of a sphere (ray-sphere test per pixel) - synthetic test data."""
    u, v = np.meshgrid(np.arange(width) + 0.5, np.arange(height) + 0.5)
    rays_c = np.stack([u, v, np.ones_like(u)], -1) @ np.linalg.inv(K).T
    d = rays_c @ R                                       # R^T applied row-wise: camera -> object
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    o = -R.T @ t                                         # camera centre in object frame
    oc = o - center
    b = d @ oc
    disc = b * b - (oc @ oc - radius * radius)
    return (disc >= 0) & (b < 0)                         # hit in front of the camera


def silhouette_from_background(img: np.ndarray, background: np.ndarray, threshold: float = 12.0) -> np.ndarray:
    """Object mask by background differencing: the empty-platter pass (scan run --background)
    is captured at the same poses, so dark object parts (tyres) still differ from the backdrop."""
    d = np.abs(img.astype(np.float32) - background.astype(np.float32))
    if d.ndim == 3:
        d = d.max(axis=2)
    return d > threshold


def write_ply(path: str | Path, points: np.ndarray, normals: np.ndarray | None = None) -> Path:
    """ASCII PLY point cloud - opens in Blender [S16], MeshLab, CloudCompare."""
    p = Path(path)
    hdr = ["ply", "format ascii 1.0", f"element vertex {len(points)}",
           "property float x", "property float y", "property float z"]
    if normals is not None:
        hdr += ["property float nx", "property float ny", "property float nz"]
    hdr.append("end_header")
    rows = points if normals is None else np.hstack([points, normals])
    body = "\n".join(" ".join(f"{x:.4f}" for x in r) for r in rows)
    p.write_text("\n".join(hdr) + "\n" + body + "\n", encoding="utf-8")
    return p
