# 05 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

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

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| TBL-01 | NEMA 17 stepper 59 Ncm 2 A | [`LAR-02_nema17_17hs19_2004s1.step`](../../../cad/bought/LAR-02_nema17_17hs19_2004s1.step) | [link](https://files.omc-stepperonline.com/17HS19-2004S1.STEP) |
| TBL-02 | GT2 6 mm closed belt 232 mm | [`TBL-02_gt2_belt_232_loop.step`](../../../cad/bought/TBL-02_gt2_belt_232_loop.step) | None published - use the dummy (belt loop) |
| TBL-03 | GT2 20T pulley 5 mm bore | [`LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step`](../../../cad/open/LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step)<br>[`LAR-04_gt2_pulley_20t_5mm.step`](../../../cad/bought/LAR-04_gt2_pulley_20t_5mm.step) | cad/open/LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step (set bore to 5 mm) |
| TBL-04 | Optical endstop module, slot type (from the LAR-05 6-pack) | [`LAR-05_tcst2103_endstop_module.step`](../../../cad/bought/LAR-05_tcst2103_endstop_module.step) | [link](https://www.vishay.com/en/product/81147/) (TCST2103 sensor only) |
| TBL-05 | M8 x 75 hex bolt, partial thread + M8 nut (fixed table axle) | [`TBL-05_bolt_m8x75_nut.step`](../../../cad/bought/TBL-05_bolt_m8x75_nut.step) | Onshape Standard Content: ISO 4014 M8 x 75 hex bolt + ISO 4032 M8 nut |
| TBL-06 | Axis fasteners (M3/M5 set) | [`FRM-06_screws_m3_m4_m5_samples.step`](../../../cad/bought/FRM-06_screws_m3_m4_m5_samples.step) | Onshape Standard Content |

Design notes: [../design.md](../design.md).
