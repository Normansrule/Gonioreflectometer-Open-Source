# 04 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| LAR-08a | Belt rim segment (print 7) | [LAR-08a_rim_segment.step](LAR-08a_rim_segment.step) | [LAR-08a_rim_segment.stl](LAR-08a_rim_segment.stl) |
| LAR-08b | M4 motor mount at 0 deg, pinion meshes the rim | [LAR-08b_ring_motor_mount.step](LAR-08b_ring_motor_mount.step) | [LAR-08b_ring_motor_mount.stl](LAR-08b_ring_motor_mount.stl) |
| LAR-08c | Arm segment: rim segment + 2020 upright socket | [LAR-08c_arm_segment.step](LAR-08c_arm_segment.step) | [LAR-08c_arm_segment.stl](LAR-08c_arm_segment.stl) |
| LAR-08e | 2020 cross clamp: upright to horizontal arm | [LAR-08e_cross_clamp.step](LAR-08e_cross_clamp.step) | [LAR-08e_cross_clamp.stl](LAR-08e_cross_clamp.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| LAR-01 | 12 in lazy Susan bearing | [`LAR-01_lazy_susan_12in.step`](../../../cad/bought/LAR-01_lazy_susan_12in.step) | [link](https://www.mcmaster.com/1443T2) (12 in turntable, CAD tab; close match, not the same part) |
| LAR-02 | NEMA 17 stepper 59 Ncm 2 A (3-pack: M4, M3, M2) | [`LAR-02_nema17_17hs19_2004s1.step`](../../../cad/bought/LAR-02_nema17_17hs19_2004s1.step) | [link](https://files.omc-stepperonline.com/17HS19-2004S1.STEP) |
| LAR-03 | GT2 6 mm open belt (5 m) | [`LAR-03_gt2_belt_open_1m.step`](../../../cad/bought/LAR-03_gt2_belt_open_1m.step) | None published - use the dummy (belt) |
| LAR-04 | GT2 20T pulley 5 mm bore (5-pack) | [`LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step`](../../../cad/open/LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step)<br>[`LAR-04_gt2_pulley_20t_5mm.step`](../../../cad/bought/LAR-04_gt2_pulley_20t_5mm.step) | cad/open/LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step (set bore to 5 mm) |
| LAR-05 | Optical endstop module, slot type (6-pack) | [`LAR-05_tcst2103_endstop_module.step`](../../../cad/bought/LAR-05_tcst2103_endstop_module.step) | [link](https://www.vishay.com/en/product/81147/) (TCST2103 sensor only: ECAD models, free login) |
| LAR-06 | Roller-lever limit switch, screw terminals (2) | [`LAR-06_me8108_limit_switch.step`](../../../cad/bought/LAR-06_me8108_limit_switch.step) | None published - use the dummy |

Design notes: [../design.md](../design.md).
