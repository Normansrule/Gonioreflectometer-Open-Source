# 07 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| CAL-06a | PTFE holder | [CAL-06a_ptfe_holder.step](CAL-06a_ptfe_holder.step) | [CAL-06a_ptfe_holder.stl](CAL-06a_ptfe_holder.stl) |
| CAL-06b | Mirror holder | [CAL-06b_mirror_holder.step](CAL-06b_mirror_holder.step) | [CAL-06b_mirror_holder.stl](CAL-06b_mirror_holder.stl) |
| CAL-06c | Chrome-ball holder | [CAL-06c_ball_holder.step](CAL-06c_ball_holder.step) | [CAL-06c_ball_holder.stl](CAL-06c_ball_holder.stl) |
| ENC-04a | Dowel socket (print 4) | [ENC-04a_dowel_socket.step](ENC-04a_dowel_socket.step) | [ENC-04a_dowel_socket.stl](ENC-04a_dowel_socket.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| ENC-01 | Blackout fabric, black (2 units) | [`ENC-01_blackout_fabric_2yd.step`](../../../cad/bought/ENC-01_blackout_fabric_2yd.step) | None published - use the dummy (fabric) |
| ENC-02 | Black felt sheet | [`ENC-02_felt_9x12in.step`](../../../cad/bought/ENC-02_felt_9x12in.step) | None published - use the dummy (sheet) |
| ENC-03 | Dowels 1/2 x 36 in (10) | [`ENC-03_dowel_half_in_36in.step`](../../../cad/bought/ENC-03_dowel_half_in_36in.step) | None published - use the dummy (dowel) |
| CAL-01 | PTFE sheets 100 x 100 x 3 mm (2): white tile = 3 stacked 50 mm squares | [`CAL-01_ptfe_tile_50mm_3x3mm.step`](../../../cad/bought/CAL-01_ptfe_tile_50mm_3x3mm.step) | None published - use the dummy (stack of three 50 mm squares) |
| CAL-02 | Glass mirror tile ~50 mm | [`CAL-02_mirror_tile_50mm.step`](../../../cad/bought/CAL-02_mirror_tile_50mm.step) | None published - use the dummy (tile) |
| CAL-03 | Chrome steel ball 1 in G25 (2) | [`CAL-03_chrome_ball_1in.step`](../../../cad/bought/CAL-03_chrome_ball_1in.step) | None published - use the dummy (25.4 mm sphere) |
| CAL-04 | ChArUco print + picture-frame glass | [`CAL-04_charuco_glass_4x6in.step`](../../../cad/bought/CAL-04_charuco_glass_4x6in.step) | None published - use the dummy (print + glass) |
| CAL-05 | Colour target (ColorChecker Mini or similar) | [`CAL-05_colorchecker_mini.step`](../../../cad/bought/CAL-05_colorchecker_mini.step) | None published - use the dummy |
| ENC-05 | Flocked light-trap sheet, self-adhesive | [`ENC-05_flock_sheet.step`](../../../cad/bought/ENC-05_flock_sheet.step) | None published - use the dummy (sheet) |
| CAL-07 | 18 % grey card + white card set (8 x 10 in) | [`CAL-07_grey_card_8x10in.step`](../../../cad/bought/CAL-07_grey_card_8x10in.step) | None published - use the dummy (card) |

Design notes: [../design.md](../design.md).
