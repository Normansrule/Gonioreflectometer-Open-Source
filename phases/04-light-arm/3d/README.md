# 04 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| LAR-08a | Belt rim segment (print 8) | [LAR-08a_rim_segment.step](LAR-08a_rim_segment.step) | [LAR-08a_rim_segment.stl](LAR-08a_rim_segment.stl) |
| LAR-08b | Motor mount, slotted | [LAR-08b_nema17_mount.step](LAR-08b_nema17_mount.step) | [LAR-08b_nema17_mount.stl](LAR-08b_nema17_mount.stl) |
| LAR-08c | Light-arm bracket | [LAR-08c_arm_bracket.step](LAR-08c_arm_bracket.step) | [LAR-08c_arm_bracket.stl](LAR-08c_arm_bracket.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| LAR-01 | 12 in lazy Susan bearing | Not confirmed - measure on arrival |
| LAR-02 | NEMA 17 stepper 59 Ncm 2 A | [link](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) |
| LAR-03 | GT2 6 mm open belt (2 m) | n/a |
| LAR-04 | GT2 20T pulley 5 mm bore | Not confirmed |
| LAR-05 | Optical endstop TCST2103 module | Not confirmed |
| LAR-06 | Roller-lever micro switch (10) | Not confirmed |
| LAR-07 | Wood screws, M4 hardware, 2 x M8 x 40 idler axles | Onshape Standard Content |

Design notes: [../design.md](../design.md).
