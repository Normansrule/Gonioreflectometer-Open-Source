# 04 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| LAR-08a | Belt rim segment (print 7) | [LAR-08a_rim_segment.step](LAR-08a_rim_segment.step) | [LAR-08a_rim_segment.stl](LAR-08a_rim_segment.stl) |
| LAR-08b | M4 motor mount at 0 deg, pinion meshes the rim | [LAR-08b_ring_motor_mount.step](LAR-08b_ring_motor_mount.step) | [LAR-08b_ring_motor_mount.stl](LAR-08b_ring_motor_mount.stl) |
| LAR-08c | Arm segment: rim segment + upright socket | [LAR-08c_arm_segment.step](LAR-08c_arm_segment.step) | [LAR-08c_arm_segment.stl](LAR-08c_arm_segment.stl) |
| LAR-08e | Cross clamp: upright to horizontal arm | [LAR-08e_cross_clamp.step](LAR-08e_cross_clamp.step) | [LAR-08e_cross_clamp.stl](LAR-08e_cross_clamp.stl) |
| LAR-08f | Light-arm upright bar, 200 mm | [LAR-08f_upright_bar.step](LAR-08f_upright_bar.step) | [LAR-08f_upright_bar.stl](LAR-08f_upright_bar.stl) |
| LAR-08g | Horizontal light-arm bar, 200 mm | [LAR-08g_arm_bar.step](LAR-08g_arm_bar.step) | [LAR-08g_arm_bar.stl](LAR-08g_arm_bar.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| LAR-01 | 12 in lazy Susan bearing | [`LAR-01_lazy_susan_12in.step`](../../../cad/bought/LAR-01_lazy_susan_12in.step) | [link](https://www.mcmaster.com/1443T2) (12 in turntable, CAD tab; close match, not the same part) |
| LAR-02 | NEMA 17 stepper 42 Ncm 1.5 A, 38 mm (5-pack: M4, M3, M2 + 2 spare) | [`LAR-02_nema17_17hs4401.step`](../../../cad/bought/LAR-02_nema17_17hs4401.step) | None published - repo model at 42.3 x 42.3 x 38 mm (standard NEMA 17 face) |
| LAR-03 | GT2 6 mm open belt (5 m) | [`LAR-03_gt2_belt_open_1m.step`](../../../cad/bought/LAR-03_gt2_belt_open_1m.step) | None published - use the dummy (belt) |
| LAR-04 | GT2 20T pulley 5 mm bore (5-pack) | [`LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step`](../../../cad/open/LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step)<br>[`LAR-04_gt2_pulley_20t_5mm.step`](../../../cad/bought/LAR-04_gt2_pulley_20t_5mm.step) | cad/open/LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step (set bore to 5 mm) |
| LAR-05 | Optical endstop module, slot type (6-pack) | [`LAR-05_tcst2103_endstop_module.step`](../../../cad/bought/LAR-05_tcst2103_endstop_module.step) | [link](https://www.vishay.com/en/product/81147/) (TCST2103 sensor only: ECAD models, free login) |
| LAR-06 | Roller-lever limit switch, sealed, 3 wires attached (2-pack) | [`LAR-06_limit_switch_sealed_prewired.step`](../../../cad/bought/LAR-06_limit_switch_sealed_prewired.step) | None published - repo model at an ESTIMATED 20 x 10 x 6.4 mm body + 20 mm lever (measure on arrival) |

Design notes: [../design.md](../design.md).
