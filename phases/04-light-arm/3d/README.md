# 04 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

| ID | Part | STEP (edit / Onshape) | STL (slice) |
|---|---|---|---|
| LAR-08a | Belt rim segment (print 8) | [LAR-08a_rim_segment.step](print/LAR-08a_rim_segment.step) | [LAR-08a_rim_segment.stl](print/LAR-08a_rim_segment.stl) |
| LAR-08b | Motor mount, slotted | [LAR-08b_nema17_mount.step](print/LAR-08b_nema17_mount.step) | [LAR-08b_nema17_mount.stl](print/LAR-08b_nema17_mount.stl) |
| LAR-08c | Light-arm bracket | [LAR-08c_arm_bracket.step](print/LAR-08c_arm_bracket.step) | [LAR-08c_arm_bracket.stl](print/LAR-08c_arm_bracket.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves downloadable vendor models into `vendor/` (git-ignored: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| LAR-01 | 12 in lazy Susan bearing | Not confirmed - measure on arrival |
| LAR-02 | NEMA 17 stepper 59 Ncm 2 A | [link](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) |
| LAR-03 | GT2 6 mm open belt (2 m) | n/a |
| LAR-04 | GT2 20T pulley 5 mm bore | Not confirmed |
| LAR-05 | Optical endstop TCST2103 module | Not confirmed |
| LAR-06 | Roller-lever micro switch (10) | Not confirmed |
| LAR-07 | Wood screws, M4 hardware, 2 x M8 x 40 idler axles | Onshape Standard Content |

## Design notes

| Part | Source |
|---|---|
| Belt rim segments, idlers, motor mount, arm bracket (LAR-08) | Onshape `LAR` — measure the bearing first (no published holes) |
| NEMA 17 | [STEP](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) [P40] |
