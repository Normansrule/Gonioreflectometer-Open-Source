# Component decisions

Prices approximate, checked 2026-10-04, USD before tax and shipping.

## Camera: HQ Camera (M12) vs Camera Module 3

| | HQ Camera M12 + 16 mm lens | Camera Module 3 (focus locked) |
|---|---|---|
| Cost | $50 + $21 = $71 | $29.25 |
| Sensor | IMX477, 1.55 µm pixels, 12-bit RAW, 1/2.3 in | IMX708, smaller pixels, 10-bit RAW |
| Field at 300 mm | about 22° × 16° → 117 × 88 mm: the 120 mm object nearly fills it | 66° × 41° → about 390 mm wide: the 50 mm swatch is ~13 % of the frame |
| Focus | fixed mechanical lens, no moving parts | voice-coil lens held in place electrically; lock with `--autofocus-mode manual --lens-position <dioptres>` |
| Radiometric stability | better SNR and more bits for HDR | adequate for BRDF averaging over the swatch; position drift of the voice coil is a risk |
| STEP | not published (drawing only) | published |

**Recommendation:** HQ Camera if the budget allows (better HDR and photogrammetry), Camera Module 3 on
the budget path. The camera head is designed with both hole patterns so you can upgrade without
reprinting anything else. The 16 mm lens has a 1/2 in image circle that only just covers the
7.9 mm sensor — check the corners on the first capture; the Commonlands CIL160 ($39) has margin.

## Motion controller: SKR Mini E3 V3 vs Arduino Nano + 4 TMC2209 (vs Pico)

| | SKR Mini E3 V3.0 | Arduino Nano + 4 modules | Raspberry Pi Pico + 4 modules |
|---|---|---|---|
| Cost | $49.85 (BTT store) | ≈ $25–35 | ≈ $31 (estimate) |
| Drivers | 4 × TMC2209 on board, UART-configured | separate modules on perfboard | separate modules on perfboard |
| Klipper fit | first-class config | ATmega328: 2 KB RAM, tight for 4 steppers + TMC UART | RP2040: comfortable |
| Light/fan switching | HE0, HB, FAN0–2 MOSFETs on board | add your own MOSFETs | add your own MOSFETs |
| Protection | main fuse, proper layout | whatever you build | whatever you build |
| STEP | published by BTT | modules vary | Pico published |

**Recommendation: SKR Mini E3 V3.** It is the only option that gives four UART-configured drivers,
switched 24 V outputs for the lights and fan, and a published STEP file in one board. The Nano is not
recommended — Klipper on an ATmega328 is memory-starved for this job. If money is the constraint,
the Pico is the better substitute (saves about $19).

## Light: why a CRI-95, 18 V-class COB

The NLDD-350H is a buck (step-down) LED driver: from 24 V it can only drive LEDs below about 20 V.
The brief's typical 36 V COBs would need a 48 V supply. The Luminus CXM-4 18 V class (16.9 V typ.,
CRI 95 bins at 2700–5000 K, 4.5 mm emitting area) fits a 24 V system and its small source
approximates a point light (0.9° at 300 mm). Exact bin price/stock is confirmed in the Light Source
module.

## Fill light: second COB instead of an LED strip

The only CRI-90 24 V strip found was sold as a $38.99 roll — over the Phase 5 cap by itself. A second
CXM-4 + NLDD behind a diffuser costs about $16.50, matches the main light's spectrum (one white
balance for both) and reuses the driver design.
