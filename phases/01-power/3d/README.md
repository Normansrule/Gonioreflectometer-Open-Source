# 01 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| PWR-18a | Power box | [PWR-18a_power_box.step](PWR-18a_power_box.step) | [PWR-18a_power_box.stl](PWR-18a_power_box.stl) |
| PWR-18b | Power box lid (e-stop) | [PWR-18b_power_lid.step](PWR-18b_power_lid.step) | [PWR-18b_power_lid.stl](PWR-18b_power_lid.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| PWR-21 | 24 V Li-ion battery pack 5 Ah with built-in protection board (BMS) | [`PWR-21_battery_6s_24v_5ah.step`](../../../cad/bought/PWR-21_battery_6s_24v_5ah.step) | None published - repo model at the listing size 78 x 50 x 72 mm (listing read 2026-10-12; measure on arrival) |
| PWR-27 | USB-C PD trigger board, 20 V by DIP switch, voltage display, screw terminals | [`PWR-27_usb_c_pd_trigger.step`](../../../cad/bought/PWR-27_usb_c_pd_trigger.step) | None published - repo model at an ESTIMATED 60 x 30 mm (no size published; measure on arrival) |
| PWR-29 | DROK buck-boost module 35 W, constant voltage + constant current, LCD (V in, V out, A, W) | [`PWR-29_drok_cc_cv_35w.step`](../../../cad/bought/PWR-29_drok_cc_cv_35w.step) | None published - repo model at the maker's size 72 x 59 x 32 mm (droking.com) |
| PWR-04 | Inline 5 x 20 mm fuse holder, 16 AWG (2-pack) | [`PWR-04_fuse_holder_inline_5x20.step`](../../../cad/bought/PWR-04_fuse_holder_inline_5x20.step) | None published - repo model at an ESTIMATED body Ø12 x 50 mm (no size published; measure on arrival) |
| PWR-05 | Fuse 3.15 A time-lag 5 x 20 mm | [`PWR-05_fuse_5x20.step`](../../../cad/bought/PWR-05_fuse_5x20.step) | None needed - 5 x 20 mm cylinder (repo model) |
| PWR-28 | Emergency stop 22 mm latching, 1 NO + 1 NC, screw terminals (2-pack) | [`PWR-28_estop_22mm_1no1nc.step`](../../../cad/bought/PWR-28_estop_22mm_1no1nc.step) | None published - repo model at the listing size (40 mm head, 70 mm overall height) |
| PWR-10 | Optocoupler module PC817, 24 V input, screw terminals (2-pack) | [`PWR-10_pc817_opto_module_24v.step`](../../../cad/bought/PWR-10_pc817_opto_module_24v.step) | None published - repo model at the maker size 66 x 16.5 x 12 mm |
| PWR-15 | 18 AWG silicone wire red/black, 1 m pair | [`PWR-15_wire_18awg_pair.step`](../../../cad/bought/PWR-15_wire_18awg_pair.step) | None published - use the dummy (wire) |
| PWR-20 | Lever wire connectors, WAGO 221 assortment (28) | [`PWR-20_lever_connector_221_412.step`](../../../cad/bought/PWR-20_lever_connector_221_412.step) | [link](https://www.wago.com/ch-de/installationsklemmen/compact-verbindungsklemme/p/221-412) (Downloads → STEP) |

Design notes: [../design.md](../design.md).
