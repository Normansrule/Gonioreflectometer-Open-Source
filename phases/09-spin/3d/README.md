# 09 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| SPN-07a | Spin platter: clamps the motor D-shaft (direct drive) | [SPN-07a_spin_platter.step](SPN-07a_spin_platter.step) | [SPN-07a_spin_platter.stl](SPN-07a_spin_platter.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| SPN-01 | NEMA 17 pancake stepper 16 Ncm 1 A (direct drive) | [link](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) |
| SPN-04 | Optical endstop TCST2103 module | Not confirmed - 33 x 11 mm PCB, 5.8 mm slot |
| SPN-06 | Axis fasteners (M3/M5 set) | Onshape Standard Content |

Design notes: [../design.md](../design.md).
