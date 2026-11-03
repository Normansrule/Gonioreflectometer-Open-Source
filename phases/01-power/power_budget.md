# Power budget (generated)

All phases installed. Laptop, ESP32-S3 hub and USB camera are powered by the laptop. Path: ALITOVE 24 V 3 A adapter (PWR-30) → e-stop →
limit switch → SKR Pico; the bus is the adapter's 24 V.

| Load | Phase | Typical W | Peak W | Idle W |
|---|---:|---:|---:|---:|
| BTT SKR Pico logic (RP2040; estimate kept from the ESP32 board) | 2 | 1.0 | 1.5 | 0.80 |
| Steppers M1-M4 (TMC2209, 0.8 A RMS run) | 4 | 7.0 | 21.2 | 0.00 |
| White COB, CLU7A3-0403E1 at 350 mA via NLDD-350H | 6 | 4.4 | 4.9 | 0.00 |
| Multispectral LED (one band on) via NLDD-350H (BLOCKED, design.md stage 10) | 10 | 0.0 | 2.1 | 0.00 |
| Wiring and terminal losses | 1 | 0.1 | 0.4 | 0.02 |

| | Typical | Peak | Idle (motors asleep) |
|---|---:|---:|---:|
| Motor board input | 12.5 W | 30.1 W | 0.8 W |
| From the adapter | 12.9 W | 31.0 W | 0.8 W |
| Adapter current at 24 V | 0.54 A | 1.29 A | 0.04 A |

| Check | | Headroom | |
|---|---|---:|---|
| adapter | 3 A adapter / 1.29 A peak at 24 V | 132 % | **PASS** |
| bus | motor board rated 24 V / 24 V adapter | 0 % | **PASS** |

Headroom needed: peak current ≥ 25 % under the adapter's rating. Efficiencies are estimates until
measured (stage 01 test T12). Off (e-stop pressed): nothing after the e-stop draws power.
