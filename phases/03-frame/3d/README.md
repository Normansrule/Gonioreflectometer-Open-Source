# 03 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| FRM-01a | Deck tile SW (x -300..-100, y -300..-100) | [FRM-01a_deck_tile_SW.step](FRM-01a_deck_tile_SW.step) | [FRM-01a_deck_tile_SW.stl](FRM-01a_deck_tile_SW.stl) |
| FRM-01b | Deck tile S (x -100..100, y -300..-100) | [FRM-01b_deck_tile_S.step](FRM-01b_deck_tile_S.step) | [FRM-01b_deck_tile_S.stl](FRM-01b_deck_tile_S.stl) |
| FRM-01c | Deck tile SE: power plate (x 100..300, y -300..-100) | [FRM-01c_deck_tile_SE.step](FRM-01c_deck_tile_SE.step) | [FRM-01c_deck_tile_SE.stl](FRM-01c_deck_tile_SE.stl) |
| FRM-01d | Deck tile W (x -300..-100, y -100..100) | [FRM-01d_deck_tile_W.step](FRM-01d_deck_tile_W.step) | [FRM-01d_deck_tile_W.stl](FRM-01d_deck_tile_W.stl) |
| FRM-01e | Deck tile C: table post + motor (x -100..100, y -100..100) | [FRM-01e_deck_tile_C.step](FRM-01e_deck_tile_C.step) | [FRM-01e_deck_tile_C.stl](FRM-01e_deck_tile_C.stl) |
| FRM-01f | Deck tile E: M4 motor + saddles (x 100..300, y -100..100) | [FRM-01f_deck_tile_E.step](FRM-01f_deck_tile_E.step) | [FRM-01f_deck_tile_E.stl](FRM-01f_deck_tile_E.stl) |
| FRM-01g | Deck tile NW: controller tray (x -300..-100, y 100..300) | [FRM-01g_deck_tile_NW.step](FRM-01g_deck_tile_NW.step) | [FRM-01g_deck_tile_NW.stl](FRM-01g_deck_tile_NW.stl) |
| FRM-01h | Deck tile N (x -100..100, y 100..300) | [FRM-01h_deck_tile_N.step](FRM-01h_deck_tile_N.step) | [FRM-01h_deck_tile_N.stl](FRM-01h_deck_tile_N.stl) |
| FRM-01i | Deck tile NE (x 100..300, y 100..300) | [FRM-01i_deck_tile_NE.step](FRM-01i_deck_tile_NE.step) | [FRM-01i_deck_tile_NE.stl](FRM-01i_deck_tile_NE.stl) |
| FRM-02a | Outrigger bar 1, 250 mm (x 215..465) | [FRM-02a_outrigger_bar_1.step](FRM-02a_outrigger_bar_1.step) | [FRM-02a_outrigger_bar_1.stl](FRM-02a_outrigger_bar_1.stl) |
| FRM-02b | Outrigger bar 2, 250 mm (x 465..715) | [FRM-02b_outrigger_bar_2.step](FRM-02b_outrigger_bar_2.step) | [FRM-02b_outrigger_bar_2.stl](FRM-02b_outrigger_bar_2.stl) |
| FRM-02c | Scan post bar 1, 175 mm (z 36..211) | [FRM-02c_scan_post_bar_1.step](FRM-02c_scan_post_bar_1.step) | [FRM-02c_scan_post_bar_1.stl](FRM-02c_scan_post_bar_1.stl) |
| FRM-02d | Scan post bar 2, 175 mm (z 211..386) | [FRM-02d_scan_post_bar_2.step](FRM-02d_scan_post_bar_2.step) | [FRM-02d_scan_post_bar_2.stl](FRM-02d_scan_post_bar_2.stl) |
| FRM-09c | Ring scale + lazy-Susan clamp, 80 deg (print 4: 20-340 deg) | [FRM-09c_protractor_segment.step](FRM-09c_protractor_segment.step) | [FRM-09c_protractor_segment.stl](FRM-09c_protractor_segment.stl) |
| FRM-09d | Outrigger saddle (print 2) | [FRM-09d_bar_saddle.step](FRM-09d_bar_saddle.step) | [FRM-09d_bar_saddle.stl](FRM-09d_bar_saddle.stl) |
| FRM-09e | Scan-post socket on the outrigger | [FRM-09e_post_socket.step](FRM-09e_post_socket.step) | [FRM-09e_post_socket.stl](FRM-09e_post_socket.stl) |
| FRM-09f | Outrigger end foot | [FRM-09f_end_foot.step](FRM-09f_end_foot.step) | [FRM-09f_end_foot.stl](FRM-09f_end_foot.stl) |
| FRM-09h | Measuring-camera pillar on the outrigger | [FRM-09h_camera_pillar.step](FRM-09h_camera_pillar.step) | [FRM-09h_camera_pillar.stl](FRM-09h_camera_pillar.stl) |
| FRM-09i | Bar coupler: outrigger, scan post (print 2) | [FRM-09i_bar_coupler.step](FRM-09i_bar_coupler.step) | [FRM-09i_bar_coupler.stl](FRM-09i_bar_coupler.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| FRM-06 | M2 socket screw kit, 4–25 mm, with nuts and washers (900 pcs) | [`FRM-06_screws_m2_samples.step`](../../../cad/bought/FRM-06_screws_m2_samples.step) | Onshape Standard Content: ISO 4762 socket head M2 |
| FRM-07 | Socket screw kit M2/M3/M4 with nuts (820 pcs): M3 for the motors | [`FRM-07_screw_m3x8.step`](../../../cad/bought/FRM-07_screw_m3x8.step) | Onshape Standard Content: ISO 4762 socket head M3 |
| FRM-08 | 608-2RS bearings (10) | [`FRM-08_bearing_608_2rs.step`](../../../cad/bought/FRM-08_bearing_608_2rs.step) | Onshape Standard Content: ball bearing 608 (8 x 22 x 7) |

Design notes: [../design.md](../design.md).
