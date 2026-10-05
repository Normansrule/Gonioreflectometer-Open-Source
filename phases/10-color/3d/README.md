# 10 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

| ID | Part | STEP (edit / Onshape) | STL (slice) |
|---|---|---|---|
| MSK-06a | LED ring (8 bands) | [MSK-06a_led_ring.step](print/MSK-06a_led_ring.step) | [MSK-06a_led_ring.stl](print/MSK-06a_led_ring.stl) |
| MSK-06b | 40 deg LED mast | [MSK-06b_led_mast.step](print/MSK-06b_led_mast.step) | [MSK-06b_led_mast.stl](print/MSK-06b_led_mast.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves downloadable vendor models into `vendor/` (git-ignored: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| MSK-01 | Narrow-band star LEDs (8 bands, ~420-660 nm) | n/a |
| MSK-02 | Constant-current driver 350 mA | Mean Well 3D OUTLINE (not downloaded) |
| MSK-03 | Darlington array 8-ch | DIP-18 model |
| MSK-04 | Heatsink 40 mm (from LSR-03 pack) | Block model |
| MSK-05 | Linear polarizer film 10 x 10 cm (10) | n/a |

## Design notes

| Part | Source |
|---|---|
| LED ring, 40° mast, polarizer holders (MSK-06) | Onshape `MSK` |
