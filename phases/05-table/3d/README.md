# 05 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| TBL-07a | Table drum: 100T teeth, 608 seats, OG-40 top | [TBL-07a_table_drum.step](TBL-07a_table_drum.step) | [TBL-07a_table_drum.stl](TBL-07a_table_drum.stl) |
| TBL-07b | Home flag (print 3: table, tilt, spin) | [TBL-07b_home_flag.step](TBL-07b_home_flag.step) | [TBL-07b_home_flag.stl](TBL-07b_home_flag.stl) |
| TBL-07c | Table motor bracket (shaft up, slotted) | [TBL-07c_table_motor_bracket.step](TBL-07c_table_motor_bracket.step) | [TBL-07c_table_motor_bracket.stl](TBL-07c_table_motor_bracket.stl) |
| TBL-07d | Table post: fixed M8 x 75 axle (hex-locked head) | [TBL-07d_table_post.step](TBL-07d_table_post.step) | [TBL-07d_table_post.stl](TBL-07d_table_post.stl) |
| TBL-07f | Spacers + shims, table and tilt (one print) | [TBL-07f_spacers.step](TBL-07f_spacers.step) | [TBL-07f_spacers.stl](TBL-07f_spacers.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| TBL-01 | NEMA 17 stepper 59 Ncm 2 A | [link](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) |
| TBL-02 | GT2 6 mm closed belt 232 mm | Model as belt path in Onshape |
| TBL-03 | GT2 20T pulley 5 mm bore | Not confirmed - 16 mm flange, 12.2 mm pitch dia |
| TBL-04 | Optical endstop TCST2103 module | Not confirmed - 33 x 11 mm PCB, 5.8 mm slot |
| TBL-05 | M8 x 75 hex bolt, partial thread + M8 nut (fixed table axle) | Model as 8 x 70 bolt |
| TBL-06 | Axis fasteners (M3/M5 set) | Onshape Standard Content |

Design notes: [../design.md](../design.md).
