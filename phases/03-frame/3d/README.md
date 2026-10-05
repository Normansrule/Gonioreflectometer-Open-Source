# 03 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

| ID | Part | STEP (edit / Onshape) | STL (slice) |
|---|---|---|---|
| FRM-09a | OG-40 adapter plate | [FRM-09a_og40_adapter.step](print/FRM-09a_og40_adapter.step) | [FRM-09a_og40_adapter.stl](print/FRM-09a_og40_adapter.stl) |
| FRM-09b | Foot cup (print 4) | [FRM-09b_foot.step](print/FRM-09b_foot.step) | [FRM-09b_foot.stl](print/FRM-09b_foot.stl) |
| FRM-09c | Ring scale, 90 deg (print 4) | [FRM-09c_protractor_segment.step](print/FRM-09c_protractor_segment.step) | [FRM-09c_protractor_segment.stl](print/FRM-09c_protractor_segment.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves downloadable vendor models into `vendor/` (git-ignored: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| FRM-01 | Birch plywood 1/2 in, 2 x 2 ft | Custom - modelled in Onshape |
| FRM-02 | 2020 V-slot 500 mm | Onshape Standard Content 2020 profile |
| FRM-03 | M5 drop-in T-nut for 2020 | Onshape Standard Content |
| FRM-04 | M8 tee nut, 4-prong | Model as 22 mm flange |
| FRM-05 | M8 x 40 bolt + jam nut | Onshape Standard Content |
| FRM-06 | Socket screw assortment M3/M4/M5 | Onshape Standard Content |
| FRM-07 | M3 heat-set inserts (50) | 4.0 mm hole, 5.7 mm deep |
| FRM-08 | 608-2RS bearings (10) | Onshape bearing generator |
| FRM-10 | M4 tee nut, 4-prong | Onshape Standard Content |
| FRM-11 | M5 tee nut, 4-prong | Onshape Standard Content |

## Design notes

| Part | Source |
|---|---|
| Post feet, OG-40 adapters, camera L-arm, protractor scales (FRM-09) | Onshape `FRM` |
| 2020 extrusion | Onshape Standard Content |
| 608 bearings | Onshape bearing generator |
