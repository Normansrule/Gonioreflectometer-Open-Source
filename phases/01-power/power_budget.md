# Power budget (generated)

All phases installed. Laptop, Pico hub and USB camera are powered by the laptop.

| Load | Phase | Typical W | Peak W | Idle W |
|---|---:|---:|---:|---:|
| FYSETC E4 logic (ESP32 + WiFi) | 2 | 1.0 | 1.5 | 0.80 |
| Steppers M1-M4 (TMC2209, 0.8 A RMS run) | 4 | 7.0 | 21.2 | 0.00 |
| White COB, CLU7A3-0403E1 at 350 mA via NLDD-350H | 6 | 4.4 | 4.9 | 0.00 |
| Multispectral LED (one band on) via NLDD-350H | 10 | 0.0 | 1.3 | 0.00 |
| Wiring, fuse, terminal losses | 1 | 0.1 | 0.4 | 0.02 |

| | Typical | Peak | Idle |
|---|---:|---:|---:|
| 24 V DC | 12.5 W (0.52 A) | 29.3 W (1.22 A) | 0.8 W |
| Wall | 14.2 W | 32.4 W | 1.2 W |
| Efficiency | 88 % | 91 % | 66 % |

Headroom: 60 W adapter / 29.3 W peak = **105 %** (need >= 25 %): **PASS**.
