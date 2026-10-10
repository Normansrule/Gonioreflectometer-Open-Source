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
| PWR-01 | AC adapter 24 V 2.5 A 60 W | [`PWR-01_gst60a24_adapter.step`](../../../cad/bought/PWR-01_gst60a24_adapter.step) | [link](https://www.meanwellusa.com/) (search GST60A → product page → 3D STEP); or the Mouser page's ECAD/CAD model link |
| PWR-02 | IEC C13 mains cord | [`PWR-02_iec_c13_cord.step`](../../../cad/bought/PWR-02_iec_c13_cord.step) | None published - use the dummy (generic cord) |
| PWR-03 | DC jack to screw-terminal adapter 2.1 mm | [`PWR-03_dc_jack_screw_terminal.step`](../../../cad/bought/PWR-03_dc_jack_screw_terminal.step) | None published - use the dummy |
| PWR-04 | Inline 5 x 20 mm fuse holder | [`PWR-04_inline_fuse_holder.step`](../../../cad/bought/PWR-04_inline_fuse_holder.step) | Digi-Key product page (Link column) → EDA / CAD Models (free login) |
| PWR-05 | Fuse 3.15 A time-lag 5 x 20 mm | [`PWR-05_fuse_5x20.step`](../../../cad/bought/PWR-05_fuse_5x20.step) | Digi-Key product page (Link column) → EDA / CAD Models (free login) |
| PWR-10 | Optocoupler LTV-817 / PC817 (DIP-4) | [`PWR-10_kicad_DIP-4_W7.62mm_pc817.step`](../../../cad/open/PWR-10_kicad_DIP-4_W7.62mm_pc817.step) | cad/open/PWR-10_kicad_DIP-4_W7.62mm_pc817.step |
| PWR-11 | Resistors 10k (2) | [`PWR-11_kicad_R_Axial_DIN0207_resistor.step`](../../../cad/open/PWR-11_kicad_R_Axial_DIN0207_resistor.step) | cad/open/PWR-11_kicad_R_Axial_DIN0207_resistor.step |
| PWR-13 | Emergency stop 22 mm latching, 1 NC | [`PWR-13_estop_22mm.step`](../../../cad/bought/PWR-13_estop_22mm.step) | [link](https://us.idec.com/) (search YW1B-V4E01R → CAD → STEP; button + contact block) |
| PWR-15 | 18 AWG silicone wire red/black, 1 m pair | [`PWR-15_wire_18awg_pair.step`](../../../cad/bought/PWR-15_wire_18awg_pair.step) | None published - use the dummy (wire) |
| PWR-19 | Half-size breadboard (400 points) | [`PWR-19_adafruit_64_halfsize_breadboard.step`](../../../cad/open/PWR-19_adafruit_64_halfsize_breadboard.step) | cad/open/PWR-19_adafruit_64_halfsize_breadboard.step |
| PWR-20 | Lever wire connectors, WAGO 221 assortment (12) | [`PWR-20_lever_connector_221_412.step`](../../../cad/bought/PWR-20_lever_connector_221_412.step) | [link](https://www.wago.com/ch-de/installationsklemmen/compact-verbindungsklemme/p/221-412) (Downloads → STEP) |

Design notes: [../design.md](../design.md).
