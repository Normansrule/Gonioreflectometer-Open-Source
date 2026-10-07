# 02 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| CTL-10a | Keypad panel + OLED window | [CTL-10a_button_panel.step](CTL-10a_button_panel.step) | [CTL-10a_button_panel.stl](CTL-10a_button_panel.stl) |
| CTL-10b | Controller tray (E4 + Pico + breadboard) | [CTL-10b_controller_tray.step](CTL-10b_controller_tray.step) | [CTL-10b_controller_tray.stl](CTL-10b_controller_tray.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| CTL-01 | FYSETC E4 (ESP32, 4x TMC2209, WiFi + Bluetooth) | [link](https://github.com/FYSETC/FYSETC-E4/tree/main/hardware) E4 V1.0B.step (confirmed) |
| CTL-02 | Raspberry Pi Pico H (headers soldered) | [link](https://datasheets.raspberrypi.com/pico/Pico-R3-step.zip) Confirmed |
| CTL-03 | USB cable for the E4 (match its port) | n/a |
| CTL-04 | USB-A to micro-B data cable 1 m | n/a |
| CTL-05 | Membrane keypad 1 x 4 | n/a |
| CTL-06 | JST-XH pre-crimped lead kit | JST XH models in KiCad / Onshape libraries |
| CTL-07 | Jumper wires male-female 150 mm (20) | n/a |
| CTL-08 | Fan 40 mm 24 V | n/a |
| CTL-11 | Stepper cable 1 m, PH2.0 6-pin to XH2.54 4-pin (4) | n/a |

Design notes: [../design.md](../design.md).
