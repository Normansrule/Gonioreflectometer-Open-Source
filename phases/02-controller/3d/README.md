# 02 · 3D files

## Print

Black ABS, enclosed printer: nozzle 245–255 °C, bed 100–105 °C, fan ≤ 20 %, 0.2 mm layers, 4 walls, 25 % gyroid, brim on tall or long parts, no supports unless noted; XY shrink compensation from the coupon (M03.3). Ventilate the room (ABS fumes). Counts and grams: [cad/PRINT.md](../../../cad/PRINT.md). v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| CTL-10a | Keypad panel + OLED window | [CTL-10a_button_panel.step](CTL-10a_button_panel.step) | [CTL-10a_button_panel.stl](CTL-10a_button_panel.stl) |
| CTL-10b | Controller tray (SKR Pico + ESP32-S3 + opto + LED driver) | [CTL-10b_controller_tray.step](CTL-10b_controller_tray.step) | [CTL-10b_controller_tray.stl](CTL-10b_controller_tray.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

Every bought part has a model in the repo (dummy in `cad/bought/` or open model in `cad/open/`; list: [cad/README.md](../../../cad/README.md)). `bash scripts/get_cad.sh` saves the real vendor models into `cad/vendor/` (not committed: vendor licences).

| ID | Part | In the repo | Real model |
|---|---|---|---|
| CTL-01 | BIGTREETECH SKR Pico V1.0 (RP2040, 4 × TMC2209 UART, USB-C) | [`CTL-01_btt_skr_pico_envelope.step`](../../../cad/bought/CTL-01_btt_skr_pico_envelope.step) | [link](https://github.com/bigtreetech/SKR-Pico/blob/master/3D/BTT%20SKR%20Pico%20V1.0.step) |
| CTL-03 | USB-A to USB-C data cables, 3 ft (2-pack) | [`CTL-03_usb_cable_e4.step`](../../../cad/bought/CTL-03_usb_cable_e4.step) | None published - use the dummy (generic cable) |
| CTL-05 | Membrane keypad 1 x 4 | [`CTL-05_membrane_keypad_1x4.step`](../../../cad/bought/CTL-05_membrane_keypad_1x4.step) | None published - use the dummy |
| CTL-06 | JST-XH pre-crimped lead kit | [`CTL-06_kicad_JST_XH_B3B_header.step`](../../../cad/open/CTL-06_kicad_JST_XH_B3B_header.step)<br>[`CTL-06_jst_xh_lead_3pin.step`](../../../cad/bought/CTL-06_jst_xh_lead_3pin.step) | cad/open/CTL-06_kicad_JST_XH_B3B_header.step (socket side) |
| CTL-07 | Jumper wires male-female 20 cm (120) | [`CTL-07_jumper_wire_mf.step`](../../../cad/bought/CTL-07_jumper_wire_mf.step) | None published - use the dummy (wire) |
| CTL-08 | Fan 40 mm 24 V | [`CTL-08_fan_40mm.step`](../../../cad/bought/CTL-08_fan_40mm.step) | None published - use the dummy (generic fan; 40 x 40 x 10 envelope) |
| CTL-11 | Stepper cables 1 m, PH2.0 6-pin to XH2.54 4-pin (4-pack) | [`CTL-11_kicad_JST_XH_B4B_header.step`](../../../cad/open/CTL-11_kicad_JST_XH_B4B_header.step)<br>[`CTL-11_kicad_JST_PH_B6B_header.step`](../../../cad/open/CTL-11_kicad_JST_PH_B6B_header.step)<br>[`CTL-11_stepper_cable_ph_xh.step`](../../../cad/bought/CTL-11_stepper_cable_ph_xh.step) | cad/open/CTL-11_kicad_JST_XH_B4B_header.step; cad/open/CTL-11_kicad_JST_PH_B6B_header.step |

Design notes: [../design.md](../design.md).
