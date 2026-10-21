"""Pose transforms and result classes for the CAD interference check, without cadquery (unit-tested).

The assembly (tools/cad/assembly.py) is modelled in the SHOWN pose M4 = 90, M3 = 0, M2 = 90, M1 = 0: lamp at +y,
sample face up (normal +z), camera at +x. A part is moved to another pose by the rotations of every axis that carries
it, applied in this order (innermost first), each about a line through the zero point:

    spin  (M1)  about +z through (0, 0, 150)       by M1 - 0        moves: spin
    tilt  (M2)  about +y through (0, 0, 150)       by 90 - M2       moves: spin, tilt
    table (M3)  about +z through (0, 0, 0)         by M3 - 0        moves: spin, tilt, table
    arm   (M4)  about +z through (0, 0, 0)         by M4 - 90       moves: arm

so the sample normal follows software kinematics R = Rz(M3) Ry(-M2) Rx(M1) (tests/test_cad_poses.py checks this).
SPDX-License-Identifier: CERN-OHL-S-2.0
"""
from __future__ import annotations

import itertools
import math

ZERO_Z = 150.0
SHOWN = {"M4": 90.0, "M3": 0.0, "M2": 90.0, "M1": 0.0}

# axis -> (point, direction, angle(pose) in deg, groups it moves)
AXES = {
    "M1": ((0.0, 0.0, ZERO_Z), (0.0, 0.0, 1.0), lambda p: p["M1"] - SHOWN["M1"], {"spin"}),
    "M2": ((0.0, 0.0, ZERO_Z), (0.0, 1.0, 0.0), lambda p: SHOWN["M2"] - p["M2"], {"spin", "tilt"}),
    "M3": ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), lambda p: p["M3"] - SHOWN["M3"], {"spin", "tilt", "table"}),
    "M4": ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), lambda p: p["M4"] - SHOWN["M4"], {"arm"}),
}
ORDER = ("M1", "M2", "M3", "M4")                       # innermost first
GROUPS = ("fixed", "arm", "table", "tilt", "spin")

CLEAR, INTERSECTION, COMPUTATION_ERROR = "CLEAR", "INTERSECTION", "COMPUTATION_ERROR"


def tilt_angle(m2: float) -> float:
    """Rotation about +y from the shown pose (M2 = 90, face up) to M2: the one tilt convention."""
    return SHOWN["M2"] - m2


def rotations(group: str, pose: dict[str, float]) -> list[tuple[tuple, tuple, float]]:
    """(point, direction, angle deg) to apply, in order, to a part of `group` modelled in the shown pose."""
    p = {**SHOWN, **pose}
    out = []
    for k in ORDER:
        pt, d, ang, moves = AXES[k]
        a = ang(p)
        if group in moves and abs(a) > 1e-9:
            out.append((pt, d, a))
    return out


def moves_with(axis: str) -> set[str]:
    return AXES[axis][3]


def classify(volume: float | None, error: BaseException | None = None, tol: float = 1.0) -> str:
    """Result of one pair check. A failed Boolean is never treated as clear."""
    if error is not None or volume is None or not math.isfinite(volume) or volume < -1e-6:
        return COMPUTATION_ERROR
    return INTERSECTION if volume > tol else CLEAR


def _rot(d, a_deg):
    x, y, z = d
    c, s = math.cos(math.radians(a_deg)), math.sin(math.radians(a_deg))
    C = 1 - c
    return [[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
            [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
            [z * x * C - y * s, z * y * C + x * s, c + z * z * C]]


def apply(point, group: str, pose: dict[str, float]):
    """Move a point of `group` from the shown pose to `pose` (same rotations cadquery applies)."""
    v = list(point)
    for pt, d, a in rotations(group, pose):
        R = _rot(d, a)
        q = [v[i] - pt[i] for i in range(3)]
        v = [sum(R[i][j] * q[j] for j in range(3)) + pt[i] for i in range(3)]
    return v


def axis_sweeps(ranges: dict[str, tuple[float, float]], step: float = 30.0) -> dict[str, list[dict]]:
    """One-axis sweeps over each configured range (others at the shown pose), ends included."""
    out = {}
    for k, (lo, hi) in ranges.items():
        n = max(1, math.ceil((hi - lo) / step))
        out[k] = [{**SHOWN, k: lo + (hi - lo) * i / n} for i in range(n + 1)]
    return out


def mixed_poses(ranges: dict[str, tuple[float, float]], per_axis: int = 4) -> list[dict]:
    """Coarse grid over every configured axis together: clashes that need two axes away from the shown pose
    (e.g. tilted platter against the arm at a low M4)."""
    vals = {k: [lo + (hi - lo) * i / (per_axis - 1) for i in range(per_axis)] for k, (lo, hi) in ranges.items()}
    keys = sorted(vals)
    return [{**SHOWN, **dict(zip(keys, combo))} for combo in itertools.product(*(vals[k] for k in keys))]
