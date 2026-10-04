# Power budget (generated)

All phases installed. Laptop, Pico hub and USB camera are powered by the laptop.

| Load | Phase | Typical W | Peak W | Idle W |
|---|---:|---:|---:|---:|
| FYSETC E4 logic (ESP32 + WiFi) | 2 | 1.0 | 1.5 | 0.80 |
| Steppers M1-M4 (TMC2209, 0.8 A RMS run) | 4 | 7.0 | 21.2 | 0.00 |
| White COB, CXA1304 at 350 mA via NLDD-350H | 6 | 3.4 | 3.6 | 0.00 |
| Multispectral LED (one band on) via NLDD-350H | 10 | 0.0 | 1.3 | 0.00 |
| Wiring, fuse, MOSFET losses | 1 | 0.1 | 0.4 | 0.02 |

| | Typical | Peak | Idle |
|---|---:|---:|---:|
| 24 V DC | 11.5 W (0.48 A) | 28.0 W (1.17 A) | 0.8 W |
| Wall | 13.1 W | 30.9 W | 1.2 W |
| Efficiency | 88 % | 90 % | 66 % |

Headroom: 60 W adapter / 28.0 W peak = **114 %** (need >= 25 %): **PASS**.
