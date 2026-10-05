# 05 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

| ID | Part | STEP (edit / Onshape) | STL (slice) |
|---|---|---|---|
| TBL-07a | GT2 100T pulley (5:1) | [TBL-07a_pulley_100T.step](print/TBL-07a_pulley_100T.step) | [TBL-07a_pulley_100T.stl](print/TBL-07a_pulley_100T.stl) |
| TBL-07b | Home flag | [TBL-07b_home_flag.step](print/TBL-07b_home_flag.step) | [TBL-07b_home_flag.stl](print/TBL-07b_home_flag.stl) |
| TBL-07c | Motor mount | [TBL-07c_nema17_mount.step](print/TBL-07c_nema17_mount.step) | [TBL-07c_nema17_mount.stl](print/TBL-07c_nema17_mount.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves downloadable vendor models into `vendor/` (git-ignored: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| TBL-01 | NEMA 17 stepper 59 Ncm 2 A | [link](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) |
| TBL-02 | GT2 6 mm closed belt 280 mm | Model as belt path in Onshape |
| TBL-03 | GT2 20T pulley 5 mm bore | Not confirmed - 16 mm flange, 12.2 mm pitch dia |
| TBL-04 | Optical endstop TCST2103 module | Not confirmed - 33 x 11 mm PCB, 5.8 mm slot |
| TBL-05 | 8 mm steel shaft 100 mm | Model as 8 x 100 mm rod |
| TBL-06 | Axis fasteners (M3/M5 set) | Onshape Standard Content |

## Design notes

| Part | Source |
|---|---|
| Hub, pulley, motor mount, home flag (TBL-07) | Onshape `TBL` |
| NEMA 17 | [STEP](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) [P40] |
