# 03 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| FRM-09a | OG-40 adapter plate | [FRM-09a_og40_adapter.step](FRM-09a_og40_adapter.step) | [FRM-09a_og40_adapter.stl](FRM-09a_og40_adapter.stl) |
| FRM-09b | Corner foot, screws on (print 4) | [FRM-09b_foot.step](FRM-09b_foot.step) | [FRM-09b_foot.stl](FRM-09b_foot.stl) |
| FRM-09c | Ring scale, 80 deg (print 4: 20-340 deg) | [FRM-09c_protractor_segment.step](FRM-09c_protractor_segment.step) | [FRM-09c_protractor_segment.stl](FRM-09c_protractor_segment.stl) |
| FRM-09d | 2020 saddle, screws on (print 2) | [FRM-09d_extrusion_saddle.step](FRM-09d_extrusion_saddle.step) | [FRM-09d_extrusion_saddle.stl](FRM-09d_extrusion_saddle.stl) |
| FRM-09e | Post socket on the outrigger (print 2) | [FRM-09e_post_socket.step](FRM-09e_post_socket.step) | [FRM-09e_post_socket.stl](FRM-09e_post_socket.stl) |
| FRM-09f | Outrigger end foot | [FRM-09f_end_foot.step](FRM-09f_end_foot.step) | [FRM-09f_end_foot.stl](FRM-09f_end_foot.stl) |
| FRM-09g | 4 mm screw washers for the lazy Susan (8) | [FRM-09g_washers.step](FRM-09g_washers.step) | [FRM-09g_washers.stl](FRM-09g_washers.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| FRM-01 | Birch plywood 1/2 in, 2 x 2 ft | Custom - modelled in Onshape |
| FRM-02 | 2020 V-slot 500 mm | Onshape Standard Content 2020 profile |
| FRM-03 | M5 drop-in T-nut for 2020 | Onshape Standard Content |
| FRM-06 | Socket screw assortment M3/M4/M5 | Onshape Standard Content |
| FRM-08 | 608-2RS bearings (10) | Onshape bearing generator |
| FRM-12 | Wood screws #8 x 5/8 in, Type 17 point (100) | n/a |

Design notes: [../design.md](../design.md).
