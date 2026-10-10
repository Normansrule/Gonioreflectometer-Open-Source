# 03 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| FRM-09a | OG-40 adapter plate | [FRM-09a_og40_adapter.step](FRM-09a_og40_adapter.step) | [FRM-09a_og40_adapter.stl](FRM-09a_og40_adapter.stl) |
| FRM-09b | Corner foot, screws on (print 4) | [FRM-09b_foot.step](FRM-09b_foot.step) | [FRM-09b_foot.stl](FRM-09b_foot.stl) |
| FRM-09c | Ring scale, 80 deg (print 4: 20-340 deg) | [FRM-09c_protractor_segment.step](FRM-09c_protractor_segment.step) | [FRM-09c_protractor_segment.stl](FRM-09c_protractor_segment.stl) |
| FRM-09d | 2020 saddle, screws on (print 2) | [FRM-09d_extrusion_saddle.step](FRM-09d_extrusion_saddle.step) | [FRM-09d_extrusion_saddle.stl](FRM-09d_extrusion_saddle.stl) |
| FRM-09e | Scan-post socket on the outrigger | [FRM-09e_post_socket.step](FRM-09e_post_socket.step) | [FRM-09e_post_socket.stl](FRM-09e_post_socket.stl) |
| FRM-09f | Outrigger end foot | [FRM-09f_end_foot.step](FRM-09f_end_foot.step) | [FRM-09f_end_foot.stl](FRM-09f_end_foot.stl) |
| FRM-09g | 4 mm screw washers for the lazy Susan (8) | [FRM-09g_washers.step](FRM-09g_washers.step) | [FRM-09g_washers.stl](FRM-09g_washers.stl) |
| FRM-09h | Measuring-camera pillar on the outrigger | [FRM-09h_camera_pillar.step](FRM-09h_camera_pillar.step) | [FRM-09h_camera_pillar.stl](FRM-09h_camera_pillar.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| FRM-01 | Baltic birch plywood 1/2 in, 24 x 24 in | [`FRM-01_plywood_610x610x12.step`](../../../cad/bought/FRM-01_plywood_610x610x12.step) | None published - use the dummy (stock sheet, 610 x 610 x 12) |
| FRM-02 | 2020 V-slot 500 mm (4-pack) | [`FRM-02_vslot_2020_500.step`](../../../cad/bought/FRM-02_vslot_2020_500.step) | [link](https://grabcad.com/openbuilds-1/models) (V-Slot 20x20, free login) or Onshape Standard Content |
| FRM-03 | M5 T-nuts for 2020, 50 drop-in + 50 sliding | [`FRM-03_tnut_m5_dropin.step`](../../../cad/bought/FRM-03_tnut_m5_dropin.step) | [link](https://grabcad.com/openbuilds-1/models) Onshape Standard Content (T-slot nut) or |
| FRM-06 | Socket screw kit M2–M5, 8/10/16/20 mm, with nuts | [`FRM-06_screws_m3_m4_m5_samples.step`](../../../cad/bought/FRM-06_screws_m3_m4_m5_samples.step) | Onshape Standard Content: ISO 4762 socket head M3/M4/M5 |
| FRM-08 | 608-2RS bearings (10) | [`FRM-08_bearing_608_2rs.step`](../../../cad/bought/FRM-08_bearing_608_2rs.step) | Onshape Standard Content: ball bearing 608 (8 x 22 x 7) |
| FRM-12 | Wood screws #8 x 5/8 in, Type 17 point (100) | [`FRM-12_wood_screw_8x5_8.step`](../../../cad/bought/FRM-12_wood_screw_8x5_8.step) | Onshape Standard Content (wood screw) or the dummy |

Design notes: [../design.md](../design.md).
