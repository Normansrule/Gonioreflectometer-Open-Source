"""Photometric stereo (Woodham 1980 [S4]): per-pixel normal and albedo from k >= 3 images
taken with a fixed camera and object under different, non-coplanar light directions.

Lambertian model [R2]:  I_j = rho * max(0, n . l_j)  ->  I = L g,  g = rho n.
Solved per pixel as weighted normal equations (L^T W L) g = L^T W I, batched over all pixels,
where W drops shadowed / saturated observations. A pixel is valid only if its usable lights
give cond(L) <= max_cond.

Lights: the white lamp moves only in the horizontal plane (rank 2), so the LED bank sits on a
40 deg mast [S8]. The bank is ~300 mm away and objects ~110 mm across, so `near_light_inputs`
gives per-pixel directions and 1/r^2 falloff from 3-D points (visual hull or mesh) [S14];
light positions are refined with the chrome balls [S13].
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


class CoplanarLightsError(ValueError):
    pass


@dataclass
class PSResult:
    normals: np.ndarray       # (..., 3) unit
    albedo: np.ndarray        # (...)
    valid: np.ndarray         # (...) bool


def light_rank(L: np.ndarray, tol: float = 1e-3) -> int:
    s = np.linalg.svd(np.asarray(L, float), compute_uv=False)
    return int((s > tol * s[0]).sum())


def solve(I: np.ndarray, L: np.ndarray, shadow: float = 0.02, saturate: float = 0.98,
          max_cond: float = 50.0) -> PSResult:
    """I: (k, ...) linear intensities (0-1 after HDR).
    L: (k, 3) distant lights, or (k, N, 3) per-pixel lights with N = prod(I.shape[1:])."""
    L = np.asarray(L, float)
    k = I.shape[0]
    shape = I.shape[1:]
    Ii = I.reshape(k, -1)
    npx = Ii.shape[1]
    if L.ndim == 2:
        if light_rank(L) < 3:
            raise CoplanarLightsError("light directions are coplanar: need lights off the horizontal plane")
        Lp = np.broadcast_to(L[:, None, :], (k, npx, 3))
    else:
        Lp = L.reshape(k, npx, 3)
    w = ((Ii > shadow) & (Ii < saturate)).astype(float)                # (k, N)
    A = np.einsum("kn,kni,knj->nij", w, Lp, Lp)                        # (N, 3, 3) = L^T W L
    b = np.einsum("kn,kni,kn->ni", w, Lp, Ii)                          # (N, 3)
    ev = np.linalg.eigvalsh(A)                                         # ascending
    valid = (w.sum(0) >= 3) & (ev[:, 0] > 0) & (ev[:, 2] <= max_cond ** 2 * np.maximum(ev[:, 0], 1e-300))
    g = np.zeros((npx, 3))
    if valid.any():
        g[valid] = np.linalg.solve(A[valid], b[valid][..., None])[..., 0]
    rho = np.linalg.norm(g, axis=1)
    n = np.divide(g, rho[:, None], out=np.zeros_like(g), where=rho[:, None] > 0)
    return PSResult(n.reshape(*shape, 3), rho.reshape(shape), valid.reshape(shape))


def near_light_inputs(I: np.ndarray, points: np.ndarray, light_pos: np.ndarray,
                      ref_dist_mm: float = 300.0) -> tuple[np.ndarray, np.ndarray]:
    """Per-pixel unit light directions and falloff-corrected intensities for point lights.

    I: (k, N) intensities; points: (N, 3) surface points (mm, object frame);
    light_pos: (k, 3) light positions (mm, object frame). Returns (I_corr (k, N), L (k, N, 3)).
    """
    d = light_pos[:, None, :] - points[None, :, :]                     # (k, N, 3)
    r = np.linalg.norm(d, axis=-1)
    return I * (r / ref_dist_mm) ** 2, d / r[..., None]


def render_lambert(normals: np.ndarray, albedo: np.ndarray, L: np.ndarray) -> np.ndarray:
    """Synthetic images (k, ...) for distant lights (k, 3) - tests and demos."""
    return np.stack([albedo * np.clip(normals @ l, 0, None) for l in L])
