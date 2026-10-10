#!/usr/bin/env python3
"""Interference check of the whole-machine assembly (tools/cad/assembly.py), in the shown pose and across each
axis' travel: M4 light arm 20-324 deg, M3 table a full turn, M2 tilt -90..90 deg (from software/config/machine.yaml),
plus sight lines from both cameras and the lamp to the zero point in the shown pose.
Every pair of parts whose solids overlap by more than 1 mm^3 is listed; exit 1 if any.

    python tools/cad/interference.py            # static pose + sweeps (~1-2 min)
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assembly as A  # noqa: E402

TOL = 1.0                                     # mm^3
SKIP: list[tuple[str, str]] = [("LSR-05b", "LSR-03")]   # (name prefix, name prefix) pairs that overlap by design:
                                                       # the lamp cap preloads the heatsink by PRELOAD (0.3 mm)
# Sweeps: moving group, rotation axis point + direction, angles relative to the shown pose (deg).
SWEEPS = {
    "arm":   ((0, 0, 0), (0, 0, 1), [m4 - 90 for m4 in list(range(20, 324, 20)) + [324]]),   # shown at M4 = 90
    "table": ((0, 0, 0), (0, 0, 1), list(range(30, 360, 30))),
    "tilt":  ((0, 0, 150), (0, 1, 0), [m2 - 90 for m2 in range(-90, 91, 30) if m2 != 90]),  # shown at M2 = 90
}
MOVES_WITH = {"arm": {"arm"}, "table": {"table", "tilt"}, "tilt": {"tilt"}}


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
        try:
            v = s1.intersect(s2).Volume()
        except Exception:                                          # noqa: BLE001 - a failed boolean is reported
            v = -1.0
        if abs(v) > TOL:
            res.append((v, n1, n2))
    return res


def posed(ps, m4: float, m3: float, m2: float):
    """Parts moved from the shown pose (M4 = 90, M3 = 0, M2 = 90) to (m4, m3, m2) degrees."""
    out = []
    for n, s, g, _ in ps:
        if g == "tilt":
            s = s.rotate(cq.Vector(0, 0, 150), cq.Vector(0, 1, 150), 90 - m2)
        if g in ("table", "tilt"):
            s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), m3)
        if g == "arm":
            s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), m4 - 90)
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
                if overlap(rb, b) and ray.intersect(s).Volume() > 0.01:
                    out.append(f"{eye} -> sample point {tuple(round(v) for v in t)} blocked by {name}")
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
    if args.static:
        return 1 if bad else 0
    for axis, (pt, d, angles) in SWEEPS.items():
        moving = [(n, s) for n, s, g, _ in ps if g in MOVES_WITH[axis]]
        still = [(n, s, b) for n, s, g, b in ps if g not in MOVES_WITH[axis]]
        worst = {}
        for ang in angles:
            mv = []
            for n, s in moving:
                r = s.rotate(cq.Vector(*pt), cq.Vector(*pt) + cq.Vector(*d), ang)
                mv.append((n, r, r.BoundingBox()))
            for v, n1, n2 in hits(mv, still):
                k = (n1, n2)
                if v > worst.get(k, (0, 0))[0]:
                    worst[k] = (v, ang)
        print(f"{axis} sweep ({len(angles)} positions): {len(worst)} clashes")
        for (n1, n2), (v, ang) in sorted(worst.items(), key=lambda kv: -kv[1][0]):
            print(f"  {v:9.1f} mm3  {n1}  x  {n2}  (at {ang:+d} deg from the shown pose)")
        bad += len(worst)
    print("OK  no interference" if not bad else f"FAIL {bad} clashes")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
