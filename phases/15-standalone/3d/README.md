# 15 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| STA-07a | Pi Zero 2 W mount | [STA-07a_pi_zero_mount.step](STA-07a_pi_zero_mount.step) | [STA-07a_pi_zero_mount.stl](STA-07a_pi_zero_mount.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| STA-01 | Raspberry Pi Zero 2 W | [link](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| STA-02 | microSD card 32 GB | — |
| STA-03 | Buck converter 24 V to 5 V 3 A | — |
| STA-04 | Micro-USB OTG adapter | — |
| STA-05 | SSD1306 OLED 0.96 in I2C 128x64 | — |
| STA-06 | Jumper wires female-female (10) | — |

Design notes: [../design.md](../design.md).
