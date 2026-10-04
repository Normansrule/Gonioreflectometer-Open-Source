# Budget

<img src="assets/budget.svg" width="100%" alt="Budget per phase">

Cheapest credible part is the default on every line. Generated numbers: [`../bom/summary.md`](../bom/summary.md). USD, approximate, before tax and shipping; each price carries its check date and reference ID in `bom/master_bom.csv`.

| | Buy everything | Already own wire, screws, cords, inserts, JST kit |
|---|---:|---:|
| Phase 1 | $348.98 | $294.30 |
| All phases | **$496.62** | **$441.94** |
| vs $500 hard cap | $3.38 under | $58.06 under |

## Caps

The brief's caps assumed a moving camera. With the fixed-camera layout [R1], Phase 1 needs the light ring **and** the table, while Phases 3–4 need only one small axis each. Proposed caps keep the $500 total:

| Phase | Brief | Proposed |
|---|---:|---:|
| 1 | $300 | $350 |
| 2 | $75 | $74 |
| 3 | $45 | $23 |
| 4 | $35 | $23 |
| 5 | $30 | $30 |
| 6 | $0 | $0 |

## Where the money goes and why

| Choice | Cheapest option chosen | Rejected (and why) |
|---|---|---|
| Compute | Your laptop ($0) | Raspberry Pi 5 ($110–175 [R63]) |
| Motion | FYSETC E4, $32: 4 × TMC2209, WiFi, BT, USB [C3] | SKR Pico $39.85 [R56], DIY ESP32 + 4 modules ~$36 [R68][R69], SKR Mini E3 $49.85 [R64] |
| Power | GST60A24 60 W, $19.40 [P1] (114 % headroom) | 120 W adapter + 5 V buck ($85, only needed for a Pi) [P31][P32] |
| Camera | Arducam B0433 IMX477 USB + 16 mm lens, $80.99 [K1][K5] | Pi HQ camera (needs a Pi) [K19]; ESP32-S3 cameras (autofocus) [R79][R80] |
| White light | Cree CXA1304 CRI 93, $2.66 + NLDD-350H $4.81 [L1][L4] | 36 V COBs need a 48 V supply [L9][L18] |
| E-stop | IDEC YW1B, $9.96 (3 A+ DC rated) [P15] | Schneider XB5 (0.5 A DC) [P23], Eaton $19.90 [P17] |
| Mirror | Craft glass mirror tile, ~$3 | Edmund first-surface $45.75 [E5] (upgrade later) |
| Multispectral | 8 narrow-band LEDs + 1 driver + ULN2803A, ~$17 | Filter cameras of [R1] (lab-grade cost) |

**Estimates:** $117.89 of the total is still "estimate (not checked)" (wire, screws, fuses, cords, LEDs). They are marked in the CSV and get real prices when each module starts.
