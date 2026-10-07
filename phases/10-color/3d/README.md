# 10 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| MSK-06a | LED ring (8 bands) | [MSK-06a_led_ring.step](MSK-06a_led_ring.step) | [MSK-06a_led_ring.stl](MSK-06a_led_ring.stl) |
| MSK-06b | 40 deg LED mast | [MSK-06b_led_mast.step](MSK-06b_led_mast.step) | [MSK-06b_led_mast.stl](MSK-06b_led_mast.stl) |
| SPC-03a | Spectral sensor tube + post clamp | [SPC-03a_spectral_tube.step](SPC-03a_spectral_tube.step) | [SPC-03a_spectral_tube.stl](SPC-03a_spectral_tube.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| MSK-01 | Narrow-band star LEDs (8 bands, ~420-660 nm) | n/a |
| MSK-02 | Constant-current driver 350 mA | Mean Well 3D OUTLINE (not downloaded) |
| MSK-03 | Darlington array 8-ch | DIP-18 model |
| MSK-04 | Heatsink 40 mm (from LSR-03 pack) | Block model |
| MSK-05 | Linear polarizer film 10 x 10 cm (10) | n/a |
| SPC-01 | AS7341 10-band spectral sensor breakout (STEMMA QT) | — |
| SPC-02 | JST-SH 4-pin to female jumper cable 150 mm | — |

Design notes: [../design.md](../design.md).
