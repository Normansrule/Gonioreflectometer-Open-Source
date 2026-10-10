# 09 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| SPN-07a | Spin platter: clamps the motor D-shaft (direct drive) | [SPN-07a_spin_platter.step](SPN-07a_spin_platter.step) | [SPN-07a_spin_platter.stl](SPN-07a_spin_platter.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| SPN-01 | NEMA 17 pancake stepper 16 Ncm 1 A (direct drive) | [`SPN-01_nema17_17hs08_1004s_pancake.step`](../../../cad/bought/SPN-01_nema17_17hs08_1004s_pancake.step) | [link](https://files.omc-stepperonline.com/17HS08-1004S.STEP) |
| SPN-04 | Optical endstop module, slot type (from the LAR-05 6-pack) | [`LAR-05_tcst2103_endstop_module.step`](../../../cad/bought/LAR-05_tcst2103_endstop_module.step) | [link](https://www.vishay.com/en/product/81147/) (TCST2103 sensor only) |
| SPN-06 | Axis fasteners (M3/M5 set) | [`FRM-06_screws_m3_m4_m5_samples.step`](../../../cad/bought/FRM-06_screws_m3_m4_m5_samples.step) | Onshape Standard Content |

Design notes: [../design.md](../design.md).
