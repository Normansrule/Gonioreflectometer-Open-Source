# Power budget (generated)

All phases installed. Laptop, ESP32-S3 hub and USB camera are powered by the laptop. Path: Xeanerol 6S Li-ion 5 Ah with BMS (PWR-21) → fuse → e-stop →
SKR Pico; the bus is the pack voltage (18–24 V). Charging: USB-C charger → DROK CC/CV (PWR-29) from a USB-C PD trigger at 20 V (PWR-27) → pack,
24 V, 1 A; it can stay plugged in while measuring.

| Load | Phase | Typical W | Peak W | Idle W |
|---|---:|---:|---:|---:|
| BTT SKR Pico logic (RP2040; estimate kept from the ESP32 board) | 2 | 1.0 | 1.5 | 0.80 |
| Steppers M1-M4 (TMC2209, 0.8 A RMS run) | 4 | 7.0 | 21.2 | 0.00 |
| White COB, CLU7A3-0403E1 at 350 mA via NLDD-350H | 6 | 4.4 | 4.9 | 0.00 |
| Multispectral LED (one band on) via NLDD-350H (BLOCKED, design.md stage 10) | 10 | 0.0 | 2.1 | 0.00 |
| Wiring, fuse, terminal losses | 1 | 0.1 | 0.4 | 0.02 |

| | Typical | Peak | Idle (motors asleep) |
|---|---:|---:|---:|
| Motor board input | 12.5 W | 30.1 W | 0.8 W |
| From the pack | 12.9 W | 31.0 W | 0.8 W |
| Pack current at 18 V (worst) | 0.72 A | 1.72 A | 0.05 A |
| On the pack alone | 5.9 h | 2.4 h | 89 h |

Usable energy 76 Wh (5 Ah × 21.6 V × 70 %, 4.0 → 3.0 V per cell).
Charge 24 W (27 W from USB-C): empty to full in about 4 h. Plugged in while measuring, it
covers the typical draw and still charges. Off (e-stop pressed): no draw from the pack; charging still works.

| Check | | Headroom | |
|---|---|---:|---|
| battery | 10 A pack / 1.72 A peak at 18 V | 480 % | **PASS** |
| runtime | 5.9 h typical / 3 h needed | 96 % | **PASS** |
| charger | 24 W charge / 12.9 W typical | 86 % | **PASS** |
| usb | 30 W USB-C charger / 27.3 W needed | 10 % | **PASS** |
| bus | motor board rated 24 V / 24 V charge voltage | 0 % | **PASS** |

Headroom needed: pack current ≥ 25 % under its limit. Efficiencies and the usable fraction are estimates until
measured (stage 01 tests T12, T13, T15). No low-voltage alarm: recharge after each session (the BMS is the last cut-off).
