"""Software collision model: capsules around each arm, 30 mm keep-out.

Every moving assembly is a chain of line segments with a radius (2020 spar +
brackets, camera head, lamp head). A pose is safe when the surface-to-surface
gap between the camera assembly and the light assembly is at least
``keep_out_mm``. Moves are checked by sampling the straight joint-space path.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import MachineConfig
from .kinematics import camera_arm, light_arm


def segment_distance(p1: np.ndarray, q1: np.ndarray, p2: np.ndarray, q2: np.ndarray) -> float:
    """Minimum distance between segments p1-q1 and p2-q2 (Ericson, Real-Time Collision Detection 5.1.9)."""
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
            denom = a * e - b * b
            s = min(max((b * f - c * e) / denom, 0.0), 1.0) if denom > eps else 0.0
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
    radius: float
    label: str


def assemblies(cfg: MachineConfig, pose: dict[str, float]) -> tuple[list[Capsule], list[Capsule]]:
    a1 = pose.get("A1", 85.0)
    a2 = pose.get("A2", 85.0)
    a3 = pose.get("A3", 0.0)
    cam, lit = camera_arm(cfg, a1), light_arm(cfg, a2, a3)
    ra = cfg.arm_radius_mm
    cam_caps = [Capsule(p, q, ra, f"camera seg {i}") for i, (p, q) in enumerate(cam.segments())]
    cam_caps.append(Capsule(cam.head, cam.head, cfg.camera_head_radius_mm, "camera head"))
    lit_caps = [Capsule(p, q, ra, f"light seg {i}") for i, (p, q) in enumerate(lit.segments())]
    lit_caps.append(Capsule(lit.head, lit.head, cfg.lamp_head_radius_mm, "lamp head"))
    return cam_caps, lit_caps


@dataclass(frozen=True)
class Clearance:
    gap_mm: float
    between: tuple[str, str]

    def ok(self, keep_out_mm: float) -> bool:
        return self.gap_mm >= keep_out_mm


def clearance(cfg: MachineConfig, pose: dict[str, float]) -> Clearance:
    cam, lit = assemblies(cfg, pose)
    best = Clearance(float("inf"), ("", ""))
    for c in cam:
        for l in lit:
            gap = segment_distance(c.p, c.q, l.p, l.q) - c.radius - l.radius
            if gap < best.gap_mm:
                best = Clearance(gap, (c.label, l.label))
    return best


def pose_is_safe(cfg: MachineConfig, pose: dict[str, float]) -> bool:
    return clearance(cfg, pose).ok(cfg.keep_out_mm)


def path_is_safe(cfg: MachineConfig, start: dict[str, float], end: dict[str, float], step_deg: float = 1.0) -> tuple[bool, dict[str, float] | None]:
    """Check a straight joint-space move. Returns (safe, first unsafe pose)."""
    keys = sorted(set(start) | set(end))
    span = max((abs(end.get(k, start.get(k, 0)) - start.get(k, 0)) for k in keys), default=0.0)
    n = max(1, int(np.ceil(span / step_deg)))
    for i in range(n + 1):
        f = i / n
        pose = {k: start.get(k, 0.0) + f * (end.get(k, start.get(k, 0.0)) - start.get(k, 0.0)) for k in keys}
        if not pose_is_safe(cfg, pose):
            return False, pose
    return True, None
