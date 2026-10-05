# 15 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

| ID | Part | STEP (edit / Onshape) | STL (slice) |
|---|---|---|---|
| STA-07a | Pi Zero 2 W mount | [STA-07a_pi_zero_mount.step](print/STA-07a_pi_zero_mount.step) | [STA-07a_pi_zero_mount.stl](print/STA-07a_pi_zero_mount.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves downloadable vendor models into `vendor/` (git-ignored: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| STA-01 | Raspberry Pi Zero 2 W | [link](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| STA-02 | microSD card 32 GB | — |
| STA-03 | Buck converter 24 V to 5 V 3 A | — |
| STA-04 | Micro-USB OTG adapter | — |
| STA-05 | SSD1306 OLED 0.96 in I2C 128x64 | — |
| STA-06 | Jumper wires female-female (10) | — |

## Design notes

| Part | Source |
|---|---|
| Pi Zero mount + OLED window (STA-07) | Onshape `STA`: Pi holes 58 × 23 mm, M2.5; OLED cut-out 26 × 15 mm in the panel |
| Pi Zero 2 W | [mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) [H51] |
