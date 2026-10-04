"""Collision model: capsules for the camera assembly and the light arm, 30 mm keep-out.

Only M4 moves anything near the camera; the sample stage stays inside the ring.
The paper's rule of a minimum angle between light and camera [R1] is enforced on top.
Segment distance after Ericson, Real-Time Collision Detection, sec. 5.1.9 [R9].
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import Machine
from .kinematics import camera_dir, light_dir


def segment_distance(p1, q1, p2, q2) -> float:
    d1, d2, r = q1 - p1, q2 - p2, p1 - p2
    a, e, f = float(d1 @ d1), float(d2 @ d2), float(d2 @ r)
    eps = 1e-12
    if a <= eps and e <= eps:
        return float(np.linalg.norm(r))
    if a <= eps:
        s, t = 0.0, min(max(f / e, 0.0), 1.0)
    else:
        c = float(d1 @ r)
        if e <= eps:
            t, s = 0.0, min(max(-c / a, 0.0), 1.0)
        else:
            b = float(d1 @ d2)
            den = a * e - b * b
            s = min(max((b * f - c * e) / den, 0.0), 1.0) if den > eps else 0.0
            t = (b * s + f) / e
            if t < 0.0:
                t, s = 0.0, min(max(-c / a, 0.0), 1.0)
            elif t > 1.0:
                t, s = 1.0, min(max((b - c) / a, 0.0), 1.0)
    return float(np.linalg.norm((p1 + d1 * s) - (p2 + d2 * t)))


@dataclass(frozen=True)
class Capsule:
    p: np.ndarray
    q: np.ndarray
    r: float
    label: str


def camera_capsules(cfg: Machine) -> list[Capsule]:
    c = camera_dir(cfg.camera_elevation_deg)
    d = cfg.camera_distance_mm
    head = Capsule(d * c, (d + 60) * c, cfg.camera_head_radius_mm, "camera body")
    foot = np.array([(d + 30) * c[0], (d + 30) * c[1], -150.0])
    post = Capsule(foot, (d + 30) * c, cfg.arm_radius_mm, "camera post")
    return [head, post]


def light_capsules(cfg: Machine, m4: float) -> list[Capsule]:
    l = light_dir(m4)
    arm = Capsule(cfg.ring_radius_mm * l, (cfg.light_distance_mm + 40) * l, cfg.arm_radius_mm, "light arm")
    head = Capsule(cfg.light_distance_mm * l, cfg.light_distance_mm * l, cfg.lamp_head_radius_mm, "lamp head")
    caps = [arm, head]
    if "multispectral" in cfg.lights:          # LED bank mast (printed, built in phase 10)
        bank = cfg.light_distance_mm * light_dir(m4, cfg.light_elevation("multispectral"))
        caps.append(Capsule(cfg.light_distance_mm * l, bank, cfg.arm_radius_mm, "LED mast"))
        caps.append(Capsule(bank, bank, cfg.lamp_head_radius_mm, "LED bank"))
    return caps


def clearance_mm(cfg: Machine, m4: float) -> float:
    return min(segment_distance(a.p, a.q, b.p, b.q) - a.r - b.r
               for a in camera_capsules(cfg) for b in light_capsules(cfg, m4))


def phase_angle(m4: float) -> float:
    """Angle between the camera and light directions (0-180)."""
    a = m4 % 360.0
    return min(a, 360.0 - a)


def pose_is_safe(cfg: Machine, pose: dict[str, float]) -> bool:
    m4 = pose.get("M4", 90.0)
    return clearance_mm(cfg, m4) >= cfg.keep_out_mm and phase_angle(m4) >= cfg.min_phase_angle_deg


def min_safe_m4(cfg: Machine, step: float = 0.1) -> float:
    a = 0.0
    while a < 180.0 and not pose_is_safe(cfg, {"M4": a}):
        a += step
    return round(a, 1)


def path_is_safe(cfg: Machine, start: dict[str, float], end: dict[str, float], step_deg: float = 0.5):
    s4, e4 = start.get("M4", 90.0), end.get("M4", start.get("M4", 90.0))
    n = max(1, int(abs(e4 - s4) / step_deg) + 1)
    for i in range(n + 1):
        m4 = s4 + (e4 - s4) * i / n
        if not pose_is_safe(cfg, {"M4": m4}):
            return False, m4
    return True, None
