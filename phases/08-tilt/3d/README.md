# 08 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| TLT-07a | Tilt yoke: 608 seats, motor slots above the axis | [TLT-07a_tilt_yoke.step](TLT-07a_tilt_yoke.step) | [TLT-07a_tilt_yoke.stl](TLT-07a_tilt_yoke.stl) |
| TLT-07b | GT2 100T pulley (5:1) on the stub axle | [TLT-07b_pulley_100T.step](TLT-07b_pulley_100T.step) | [TLT-07b_pulley_100T.stl](TLT-07b_pulley_100T.stl) |
| TLT-07c | Tilt cradle: stub-axle nut traps, spin motor floor | [TLT-07c_tilt_cradle.step](TLT-07c_tilt_cradle.step) | [TLT-07c_tilt_cradle.stl](TLT-07c_tilt_cradle.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| TLT-01 | NEMA 17 stepper 59 Ncm 2 A | [link](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) |
| TLT-02 | GT2 6 mm closed belt 280 mm | Model as belt path in Onshape |
| TLT-03 | GT2 20T pulley 5 mm bore | Not confirmed - 16 mm flange, 12.2 mm pitch dia |
| TLT-04 | Optical endstop TCST2103 module | Not confirmed - 33 x 11 mm PCB, 5.8 mm slot |
| TLT-05 | M8 x 35 hex bolts, partial thread + nuts (2, tilt stub axles) | Model as 8 x 35 bolt |
| TLT-06 | Axis fasteners (M3/M5 set) | Onshape Standard Content |

Design notes: [../design.md](../design.md).
