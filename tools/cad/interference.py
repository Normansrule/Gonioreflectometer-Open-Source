#!/usr/bin/env python3
"""Interference check of the whole-machine assembly (tools/cad/assembly.py): the shown pose, each axis across its
configured travel (software/config/machine.yaml: M4 light arm, M3 table, M2 tilt, M1 spin), a coarse grid of mixed
poses (every axis away from the shown pose at once, keep-out-safe poses only), and sight lines from both cameras and
the lamp to the zero point. Pose transforms: tools/cad/poses.py (one convention, unit-tested against the kinematics).

Every checked pair ends in one of three states:
    CLEAR               solids overlap by <= 1 mm^3
    INTERSECTION        solids overlap by more than 1 mm^3 (a clash)
    COMPUTATION_ERROR   the Boolean failed or returned a non-finite / negative volume: NOT treated as clear
Exit 0 only if every pair is CLEAR and every sight line is open; 1 for clashes or blocked views; 2 for computation errors.

    python tools/cad/interference.py            # static pose + sweeps + mixed poses (a few minutes)
    python tools/cad/interference.py --static   # shown pose only

Needs cadquery. Dummies are envelopes, so a hit near a dummy means "check with the real part", not always a clash.
SPDX-License-Identifier: CERN-OHL-S-2.0
"""
from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "software" / "src"))
import assembly as A  # noqa: E402
import poses as P0  # noqa: E402

TOL = 1.0                                     # mm^3
SKIP: list[tuple[str, str]] = [("LSR-05b", "LSR-03")]   # (name prefix, name prefix) pairs that overlap by design:
                                                       # the lamp cap preloads the heatsink by PRELOAD (0.3 mm)
ERRORS: list[str] = []                                 # pairs whose Boolean failed (COMPUTATION_ERROR)


def ranges() -> dict[str, tuple[float, float]]:
    """Travel of every axis from machine.yaml (all phases: the CAD shows the finished machine)."""
    from opengonio.gantry.config import load_config
    cfg = load_config()
    return {k: (a.min_deg, a.max_deg) for k, a in cfg.axes.items()}


def safe(pose: dict) -> bool:
    """Poses the software allows (keep-out between the arm and the stage); others are never commanded."""
    from opengonio.gantry.collision import pose_is_safe
    from opengonio.gantry.config import load_config
    return pose_is_safe(load_config(), pose)


def parts() -> list[tuple[str, cq.Shape, str]]:
    a = A.build()
    out = []
    for shape, name, loc, _ in a:
        if shape is None:
            continue
        s = shape.moved(loc) if loc else shape
        short = name.split("/")[-1]
        out.append((short, s, A.GROUPS.get(short, "fixed")))
    return out


def overlap(b1, b2, t=0.05) -> bool:
    return (b1.xmin < b2.xmax - t and b2.xmin < b1.xmax - t and b1.ymin < b2.ymax - t and b2.ymin < b1.ymax - t
            and b1.zmin < b2.zmax - t and b2.zmin < b1.zmax - t)


def skipped(n1: str, n2: str) -> bool:
    return any((n1.startswith(a) and n2.startswith(b)) or (n1.startswith(b) and n2.startswith(a)) for a, b in SKIP)


def hits(group_a, group_b) -> list[tuple[float, str, str]]:
    res = []
    pairs = itertools.combinations(group_a, 2) if group_b is None else itertools.product(group_a, group_b)
    for (n1, s1, b1), (n2, s2, b2) in pairs:
        if skipped(n1, n2) or not overlap(b1, b2):
            continue
        err, v = None, None
        try:
            v = s1.intersect(s2).Volume()
        except Exception as exc:                                   # noqa: BLE001 - a failed Boolean is an error, not clear
            err = exc
        state = P0.classify(v, err, TOL)
        if state == P0.INTERSECTION:
            res.append((v, n1, n2))
        elif state == P0.COMPUTATION_ERROR:
            ERRORS.append(f"{n1} x {n2}: {err or f'volume {v}'}")
    return res


def move(s, g: str, pose: dict):
    for pt, d, a in P0.rotations(g, pose):
        s = s.rotate(cq.Vector(*pt), cq.Vector(*pt) + cq.Vector(*d), a)
    return s


def posed(ps, m4: float, m3: float, m2: float, m1: float = 0.0):
    """Parts moved from the shown pose (M4 = 90, M3 = 0, M2 = 90, M1 = 0) to the given angles (tools/cad/poses.py)."""
    pose = {"M4": m4, "M3": m3, "M2": m2, "M1": m1}
    out = []
    for n, s, g, _ in ps:
        s = move(s, g, pose)
        out.append((n, s, g, s.BoundingBox()))
    return out


def rays(ps, eyes: dict, targets: list) -> list[str]:
    out = []
    for eye, a in eyes.items():
        for t in targets:
            d = cq.Vector(*t) - cq.Vector(*a)
            n = d.normalized()
            ray = cq.Solid.makeCylinder(1.0, d.Length - 6, cq.Vector(*a) + n * 3, n)
            rb = ray.BoundingBox()
            for name, s, _, b in ps:
                if not overlap(rb, b):
                    continue
                err, v = None, None
                try:
                    v = ray.intersect(s).Volume()
                except Exception as exc:                           # noqa: BLE001 - never read as "clear"
                    err = exc
                if P0.classify(v, err, 0.01) == P0.COMPUTATION_ERROR:
                    ERRORS.append(f"sight line {eye} x {name}: {err or f'volume {v}'}")
                elif v > 0.01:
                    out.append(f"{eye} -> sample point {tuple(round(x) for x in t)} blocked by {name}")
    return sorted(set(out))


def sightlines(ps) -> list[str]:
    """Rays to the sample: (1) a typical in-plane pose - lamp at 60 deg, the sample facing the 30 deg bisector
    (M3 = 30, M2 = 0) - from the measuring camera and the lamp; (2) the scan camera looking at the platter face up
    (shown pose). A part in a ray's way shades or hides the sample there."""
    import math
    import parts as P
    m4, bis = 60.0, 30.0
    c, s_ = math.cos(math.radians(bis)), math.sin(math.radians(bis))
    lamp_r = 300.0 + P.LAMP_COB_Z - P.LAMP_EXIT_Z                                    # lamp exit
    eyes = {"measuring camera": (350.0, 0.0, 150.0),
            "lamp": (lamp_r * math.cos(math.radians(m4)), lamp_r * math.sin(math.radians(m4)), 150.0)}
    face = [(3 * c - u * s_, 3 * s_ + u * c, 150.0 + v) for u in (-20.0, 0.0, 20.0) for v in (-20.0, 0.0, 20.0)]
    out = rays(posed(ps, m4, bis, 0.0), eyes, face)
    e = math.radians(P.SCAN_TILT)
    top = [(x, y, 152.0) for x in (-20.0, 0.0, 20.0) for y in (-20.0, 0.0, 20.0)]
    return out + rays(ps, {"scan camera": (650 * math.cos(e), 0.0, P.SCAN_LENS_Z)}, top)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--static", action="store_true")
    args = ap.parse_args()
    ps = [(n, s, g, s.BoundingBox()) for n, s, g in parts()]
    bad = 0
    static = hits([(n, s, b) for n, s, g, b in ps], None)
    print(f"shown pose: {len(ps)} parts, {len(static)} clashes")
    for v, n1, n2 in sorted(static, reverse=True):
        print(f"  {v:9.1f} mm3  {n1}  x  {n2}")
    bad += len(static)
    blocked = sightlines(ps)
    print(f"sight lines (cameras, lamp -> zero point): {len(blocked)} blocked")
    for b in blocked:
        print("  " + b)
    bad += len(blocked)
    if not args.static:
        rg = ranges()
        for axis, poses in P0.axis_sweeps(rg).items():
            moving = P0.moves_with(axis)
            worst = sweep(ps, poses, lambda g1, g2: (g1 in moving) != (g2 in moving), axis)
            print(f"{axis} sweep ({len(poses)} positions, {rg[axis][0]:g}..{rg[axis][1]:g} deg): {len(worst)} clashes")
            report(worst)
            bad += len(worst)
        mixed = [p for p in P0.mixed_poses(rg, 4) if safe(p)]
        worst = sweep(ps, mixed, lambda g1, g2: g1 != g2, None)
        print(f"mixed poses ({len(mixed)} keep-out-safe combinations of all axes): {len(worst)} clashes")
        report(worst)
        bad += len(worst)
    if ERRORS:
        print(f"COMPUTATION_ERROR {len(ERRORS)} pair(s): the Boolean failed, interference unknown")
        for e in sorted(set(ERRORS)):
            print("  " + e)
        return 2
    print("OK  no interference" if not bad else f"FAIL {bad} clashes")
    return 1 if bad else 0


def sweep(ps, poses: list[dict], pair_moves, axis: str | None) -> dict:
    """Worst overlap per part pair over `poses`; only pairs whose relative position changes are checked."""
    worst = {}
    for pose in poses:
        mv = [(n, move(s, g, pose), g) for n, s, g, _ in ps]
        boxed = [(n, s, s.BoundingBox(), g) for n, s, g in mv]
        for (n1, s1, b1, g1), (n2, s2, b2, g2) in itertools.combinations(boxed, 2):
            if not pair_moves(g1, g2):
                continue
            for v, a, b in hits([(n1, s1, b1)], [(n2, s2, b2)]):
                if v > worst.get((a, b), (0, None))[0]:
                    worst[(a, b)] = (v, pose[axis] if axis else pose)
    return worst


def report(worst: dict) -> None:
    for (n1, n2), (v, at) in sorted(worst.items(), key=lambda kv: -kv[1][0]):
        where = f"at {at:g} deg" if isinstance(at, float) else "at " + " ".join(f"{k}={v_:g}" for k, v_ in at.items())
        print(f"  {v:9.1f} mm3  {n1}  x  {n2}  ({where})")


if __name__ == "__main__":
    sys.exit(main())
