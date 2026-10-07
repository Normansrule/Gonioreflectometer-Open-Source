"""Out-of-plane plans from BRDF angles (stages 08–09): inverse kinematics for the fixed-camera layout [R1].

Wanted (theta_i, theta_r, delta_phi [, phi_i]) -> axis angles:
  1. Light–camera angle:  cos(alpha) = cos(theta_i) cos(theta_r) + sin(theta_i) sin(theta_r) cos(delta_phi)   [R2]
     The light is horizontal and the camera at elevation e, so cos(alpha) = cos(e) cos(M4)  ->  M4.
  2. Normal n with n.c = cos(theta_r), n.l = cos(theta_i), |n| = 1:  n = a c + b l + g (c x l).
  3. n = Rz(M3) Ry(-M2) x  ->  M2 = asin(n_z), M3 = atan2(n_y, n_x).
  4. Anisotropic only: M1 turns the sample about n until phi_i (from the brushing direction) is the wanted one.

    opengonio capture isotropic --step 15        theta_i <= theta_r (reciprocity), delta_phi 0..180
    opengonio capture spin --theta 30 --step 15  theta_i 30, theta_r 40, M1 0..180 (brushed metal, fabric)
    opengonio capture anisotropic --step 15      isotropic set x phi_i every 30 deg (needs M1)
"""
from __future__ import annotations

import math

import numpy as np

from ..gantry.collision import pose_is_safe
from ..gantry.config import Machine
from ..gantry.kinematics import brdf_coords, camera_dir, light_dir


def complete(cfg: Machine, pose: dict[str, float]) -> dict[str, float]:
    """Every installed axis gets a value (missing ones from default_pose: flat, unspun), nothing else.
    Without this a plan written for stage 06 would leave M2 at its home (-90 deg) once the tilt is built."""
    d = cfg.default_pose()
    return {k: float(pose.get(k, d[k])) for k in cfg.active_axes}


def pose_for_angles(cfg: Machine, theta_i: float, theta_r: float, delta_phi: float,
                    phi_i: float | None = None) -> dict[str, float] | None:
    """Axis angles that put light and camera at the wanted BRDF angles; None if the machine can't reach them."""
    ti, tr, dp = (math.radians(v) for v in (theta_i, theta_r, delta_phi))
    cos_a = math.cos(ti) * math.cos(tr) + math.sin(ti) * math.sin(tr) * math.cos(dp)
    ce = math.cos(math.radians(cfg.camera_elevation_deg))
    if abs(cos_a / ce) > 1:
        return None
    m4 = math.degrees(math.acos(cos_a / ce))
    c, l = camera_dir(cfg.camera_elevation_deg), light_dir(m4)
    ca = float(c @ l)
    if abs(1 - ca * ca) < 1e-9:                         # light on the camera axis: not allowed anyway
        return None
    a, b = np.linalg.solve([[1.0, ca], [ca, 1.0]], [math.cos(tr), math.cos(ti)])
    base = a * c + b * l
    cx = np.cross(c, l)
    r2 = 1.0 - float(base @ base)
    if r2 < -1e-9:
        return None
    best = None
    for sgn in (1.0, -1.0):
        n = base + sgn * math.sqrt(max(r2, 0.0)) * cx / np.linalg.norm(cx)
        p = {"M4": m4, "M3": math.degrees(math.atan2(n[1], n[0])), "M2": math.degrees(math.asin(max(-1, min(1, n[2])))), "M1": 0.0}
        if best is None or abs(p["M2"]) < abs(best["M2"]):
            best = p
        if r2 < 1e-12:
            break
    if phi_i is not None:
        p0 = brdf_coords(cfg, best).phi_i
        s = 1.0 if (brdf_coords(cfg, {**best, "M1": 10.0}).phi_i - p0) % 360 < 180 else -1.0
        best["M1"] = (s * (phi_i - p0) + 180.0) % 360.0 - 180.0
    return {k: round(v, 3) for k, v in best.items()}


def reachable(cfg: Machine, pose: dict[str, float] | None) -> bool:
    if pose is None:
        return False
    for k, v in pose.items():
        if k in cfg.axes and abs(v - cfg.default_pose()[k]) > 1e-6 and k not in cfg.active_axes:
            return False                                 # needs an axis that is not built yet
        if k in cfg.active_axes and not cfg.axes[k].in_range(v):
            return False
    return pose_is_safe(cfg, pose)


def isotropic(cfg: Machine, step: float = 15.0, max_theta: float = 75.0) -> list[dict[str, float]]:
    """theta_i <= theta_r (reciprocity halves the work [R2]); delta_phi 0..180. Unreachable poses are skipped."""
    out, seen = [], set()
    n = int(max_theta / step)
    for i in range(n + 1):
        for j in range(i, n + 1):
            ti, tr = i * step, j * step
            for dp in ([0.0] if ti == 0 or tr == 0 else [k * step for k in range(int(180 / step) + 1)]):
                p = pose_for_angles(cfg, ti, tr, dp)
                if reachable(cfg, p):
                    q = complete(cfg, p)
                    key = tuple(round(v, 2) for v in q.values())
                    if key not in seen:
                        seen.add(key)
                        out.append(q)
    out.sort(key=lambda p: (round(p["M4"] / step), p["M3"] if round(p["M4"] / step) % 2 == 0 else -p["M3"]))
    return out


def anisotropic(cfg: Machine, step: float = 15.0, phi_step: float = 30.0, max_theta: float = 75.0) -> list[dict[str, float]]:
    """isotropic set x phi_i 0..180 (from the brushing direction, marked at M1 = 0)."""
    out = []
    n = int(max_theta / step)
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            for dp in [k * step for k in range(int(180 / step) + 1)]:
                for ph in np.arange(0.0, 180.0 + 1e-9, phi_step):
                    p = pose_for_angles(cfg, i * step, j * step, dp, phi_i=float(ph))
                    if reachable(cfg, p):
                        out.append(complete(cfg, p))
    return out


def spin(cfg: Machine, theta: float = 30.0, step: float = 15.0, span: float = 180.0, off: float = 10.0) -> list[dict[str, float]]:
    """In-plane pose theta_i = theta, theta_r = theta + off, sample spun about its normal.
    Slightly off the mirror angle (off = 10 deg) so the highlight shows the roughness along the plane of incidence:
    brushed metal is brightest there when its grooves are perpendicular to that plane."""
    return [complete(cfg, {"M4": 2 * theta + off, "M3": theta + off, "M2": 0.0, "M1": float(a)})
            for a in np.arange(0.0, span + 1e-9, step)]
