#!/usr/bin/env python3
"""docs/og/model/rig.js: the whole-machine CAD assembly as a compact mesh for the website's four-axis view.

    python tools/site_model.py          (needs cadquery; run by `make cad`)

Every part from tools/cad/assembly.py is tessellated in the shown pose (M4 = 90, M3 = 0, M2 = 90, M1 = 0) and tagged
with the group that moves it (fixed, arm, table, tilt, spin). The page moves the groups with the same rotations as
tools/cad/poses.py (the CAD clash check), so the animation is the modelled machine, not a drawing of it.

Format (little-endian, deflate-compressed, base64 in a .js file so the page also works opened from disk):
  per vertex (16 bytes): int16 x, y, z (position / scale mm) · int8 nx, ny, nz, group · uint8 colour index, build order
  · int8 explode direction x, y, z · uint8 explode distance / 4 mm; then uint32 triangle indices.
Build order and explode vector are per part: the page flies each part in from outside, bottom parts first.
Per part (meta "names", "spans" = [first vertex, vertices, first index, indices], "info" = printed part name + STL): the
build book (docs/build.html, tools/build_book.py) draws parts one step at a time from the same mesh.
SPDX-License-Identifier: CERN-OHL-S-2.0
"""
from __future__ import annotations

import base64
import json
import re
import struct
import sys
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "cad"))
OUT = ROOT / "docs" / "og" / "model" / "rig.js"
GROUPS = ("fixed", "arm", "table", "tilt", "spin")
SCALE = 0.05                      # mm per int16 step: +/-1638 mm range, 0.05 mm resolution


def main() -> int:
    import assembly as A
    import poses
    asm = A.build()
    import bought as B
    import parts as PP
    pos, nrm, grp, cid, idx, owner, cents = [], [], [], [], [], [], []
    names, spans, info = [], [], {}
    palette: list[tuple] = []
    base = 0
    for shape, name, loc, col in asm:
        if shape is None:
            continue
        part = name.split("/")[-1]
        g = GROUPS.index(A.GROUPS.get(part, "fixed"))
        c = tuple(round(x, 3) for x in (col.toTuple()[:3] if col else (0.6, 0.6, 0.6)))
        if c not in palette:
            palette.append(c)
        s = shape.moved(loc) if loc else shape
        v, f = s.tessellate(1.2, 0.6)
        if not f:
            continue
        v = np.array([[q.x, q.y, q.z] for q in v], dtype=np.float64)
        f = np.array(f, dtype=np.int64)
        n = np.zeros_like(v)                                   # area-weighted vertex normals (vertices are per face)
        fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
        for k in range(3):
            np.add.at(n, f[:, k], fn)
        n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
        pid = part_id(part)
        if pid in PP.PARTS:                                     # printed: what it is + its STL, for the build book
            st, stem, _, what = PP.PARTS[pid]
            info[pid] = {"what": what, "stl": f"phases/{st}/3d/{pid}_{stem}.stl", "kind": "print"}
        elif pid in B.B_PARTS:
            info[pid] = {"kind": "buy"}
        names.append(part); spans.append([base, len(v), sum(len(x) for x in idx) * 3, len(f) * 3])
        pos.append(v); nrm.append(n); grp.append(np.full(len(v), g)); cid.append(np.full(len(v), palette.index(c)))
        owner.append(np.full(len(v), len(cents))); cents.append(v.mean(0))
        idx.append(f + base)
        base += len(v)
    P, N = np.concatenate(pos), np.concatenate(nrm)
    G, C, I = np.concatenate(grp), np.concatenate(cid), np.concatenate(idx)
    O, cen = np.concatenate(owner), np.array(cents)
    mid = np.array([0.0, 0.0, 60.0])
    away = cen - mid
    away[:, 2] = np.abs(away[:, 2]) + 0.6 * np.linalg.norm(away[:, :2], axis=1) + 80.0    # out and up, never through the deck
    dist = np.linalg.norm(away, axis=1)
    edir = away / dist[:, None]
    emag = np.clip(180.0 + 0.55 * dist, 0, 1020)                                            # mm
    order = np.argsort(np.argsort(cen[:, 2]))                                                # lowest parts land first
    delay = np.round(255 * order / max(len(cen) - 1, 1))
    q = np.clip(np.round(P / SCALE), -32767, 32767).astype("<i2")
    nn = np.clip(np.round(N * 127), -127, 127).astype("i1")
    rec = np.zeros(len(P), dtype=[("p", "<i2", 3), ("n", "i1", 3), ("g", "i1"), ("c", "u1"), ("d", "u1"),
                                  ("e", "i1", 3), ("m", "u1")])
    rec["p"], rec["n"], rec["g"], rec["c"] = q, nn, G.astype("i1"), C.astype("u1")
    rec["d"] = delay[O].astype("u1")
    rec["e"] = np.clip(np.round(edir[O] * 127), -127, 127).astype("i1")
    rec["m"] = np.round(emag[O] / 4).astype("u1")
    blob = rec.tobytes() + I.astype("<u4").tobytes()
    packed = base64.b64encode(zlib.compress(blob, 9)).decode()
    axes = {k: {"point": list(pt), "dir": list(d), "moves": sorted(m)} for k, (pt, d, _, m) in poses.AXES.items()}
    meta = {"note": "CAD assembly (tools/cad/assembly.py), shown pose; generated by tools/site_model.py",
            "vertices": int(len(P)), "triangles": int(len(I)), "parts": len(cents), "stride": 16, "scale": SCALE, "groups": list(GROUPS),
            "palette": palette, "shown": poses.SHOWN, "order": list(poses.ORDER), "axes": axes, "ranges": ranges(),
            "camera": [350.0, 0.0, 150.0],
            "zero_z": poses.ZERO_Z, "bbox": [P.min(0).round(1).tolist(), P.max(0).round(1).tolist()],
            "lamp": lamp_point(A),
            "names": names, "spans": spans, "info": info}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("// Written by tools/site_model.py (`make cad`): do not edit by hand.\nwindow.RIG = "
                   + json.dumps(meta, separators=(",", ":")) + ';\nwindow.RIG.data = "' + packed + '";\n', encoding="utf-8")
    print(f"docs/og/model/rig.js: {len(P)} vertices, {len(I)} triangles, {OUT.stat().st_size / 1e6:.2f} MB")
    return 0


def part_id(name: str) -> str:
    """'LAR-08a_3' -> 'LAR-08a', 'FRM-08_608_2' -> 'FRM-08': the parts-list ID at the start of an assembly name."""
    m = re.match(r"[A-Z]+-\d+[a-z]?", name)
    return m.group(0) if m else name


def lamp_point(A) -> list[float]:
    """The COB in the shown pose: 300 mm from the zero point along +y (assembly.py), so the page lights from it."""
    return [0.0, 300.0, 150.0]


def ranges() -> dict[str, list[float]]:
    """Axis travel from software/config/machine.yaml: the animation never goes where the machine can't."""
    sys.path.insert(0, str(ROOT / "software" / "src"))
    from opengonio.gantry.config import load_config
    return {k: [a.min_deg, a.max_deg] for k, a in load_config().axes.items()}


if __name__ == "__main__":
    sys.exit(main())
