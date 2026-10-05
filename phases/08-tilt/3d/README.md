# 08 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| TLT-07a | Tilt yoke | [TLT-07a_tilt_yoke.step](TLT-07a_tilt_yoke.step) | [TLT-07a_tilt_yoke.stl](TLT-07a_tilt_yoke.stl) |
| TLT-07b | GT2 100T pulley (5:1) | [TLT-07b_pulley_100T.step](TLT-07b_pulley_100T.step) | [TLT-07b_pulley_100T.stl](TLT-07b_pulley_100T.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| TLT-01 | NEMA 17 stepper 59 Ncm 2 A | [link](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) |
| TLT-02 | GT2 6 mm closed belt 280 mm | Model as belt path in Onshape |
| TLT-03 | GT2 20T pulley 5 mm bore | Not confirmed - 16 mm flange, 12.2 mm pitch dia |
| TLT-04 | Optical endstop TCST2103 module | Not confirmed - 33 x 11 mm PCB, 5.8 mm slot |
| TLT-05 | 8 mm steel shaft 100 mm | Model as 8 x 100 mm rod |
| TLT-06 | Axis fasteners (M3/M5 set) | Onshape Standard Content |

Design notes: [../design.md](../design.md).
