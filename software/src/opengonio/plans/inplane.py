"""Phase 1 in-plane plans: (theta_i, theta_r) grid -> (M3, M4) poses.

In-plane (M2 = 0, camera elevation 0) with the camera at 0 deg and the light at M4:
theta_r = |M3|, theta_i = |M4 - M3|, light and camera on opposite sides of the normal.
So M3 = theta_r and M4 = theta_r + theta_i.  Specular when theta_i = theta_r.
"""
from __future__ import annotations

from ..gantry.collision import pose_is_safe
from ..gantry.config import Machine


def pose_for(theta_i: float, theta_r: float) -> dict[str, float]:
    return {"M3": theta_r, "M4": theta_r + theta_i}


def grid(cfg: Machine, step_deg: float = 5.0, max_deg: float = 80.0) -> list[dict[str, float]]:
    out = []
    n = int(max_deg / step_deg)
    for i in range(n + 1):
        for j in range(n + 1):
            p = pose_for(i * step_deg, j * step_deg)
            a4 = cfg.axes["M4"]
            if a4.in_range(p["M4"]) and pose_is_safe(cfg, p):
                out.append(p)
    # serpentine order keeps M4 travel short
    out.sort(key=lambda p: (p["M3"], p["M4"] if int(p["M3"] / step_deg) % 2 == 0 else -p["M4"]))
    return out


def mirror_sweep(theta_i: float, span: float = 4.0, step: float = 0.1) -> list[dict[str, float]]:
    """Phase 1 milestone: hold the light, sweep the table through the specular angle."""
    n = int(2 * span / step)
    m4 = 2 * theta_i
    return [{"M4": m4, "M3": theta_i - span + k * step} for k in range(n + 1)]
