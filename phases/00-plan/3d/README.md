# 00 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| PLAN-01 | Fit test: insert holes + 608 pockets | [PLAN-01_tolerance_coupon.step](PLAN-01_tolerance_coupon.step) | [PLAN-01_tolerance_coupon.stl](PLAN-01_tolerance_coupon.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

Design notes: [../design.md](../design.md).
