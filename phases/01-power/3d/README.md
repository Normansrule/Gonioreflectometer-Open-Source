# 01 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| PWR-18 | Power plate (jack + e-stop box) | [PWR-18_power_plate.step](PWR-18_power_plate.step) | [PWR-18_power_plate.stl](PWR-18_power_plate.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| PWR-30 | 24 V 3 A wall adapter with screw-terminal DC jack | [`PWR-30_dc_jack_screw_terminal.step`](../../../cad/bought/PWR-30_dc_jack_screw_terminal.step) | None published - repo model of the jack at an ESTIMATED 32 x 14 x 13 mm (measure on arrival) |
| PWR-28 | Emergency stop in its own box, latching, 1 NO + 1 NC, screw terminals | [`PWR-28_estop_station_1no1nc.step`](../../../cad/bought/PWR-28_estop_station_1no1nc.step) | None published - repo model at an ESTIMATED 70 x 70 x 60 mm box + Ø40 head (measure on arrival) |
| PWR-10 | Optocoupler module PC817, 24 V input, screw terminals (2-pack) | [`PWR-10_pc817_opto_module_24v.step`](../../../cad/bought/PWR-10_pc817_opto_module_24v.step) | None published - repo model at the maker size 66 x 16.5 x 12 mm |
| PWR-15 | 18 AWG silicone wire red/black, 1.5 m (5 ft) each colour | [`PWR-15_wire_18awg_pair.step`](../../../cad/bought/PWR-15_wire_18awg_pair.step) | None published - use the dummy (wire) |
| PWR-20 | Lever wire connectors, WAGO 221 assortment (12) | [`PWR-20_wago_221_assortment_12.step`](../../../cad/bought/PWR-20_wago_221_assortment_12.step) | [link](https://www.wago.com/ch-de/installationsklemmen/compact-verbindungsklemme/p/221-412) (Downloads → STEP) |

Design notes: [../design.md](../design.md).
