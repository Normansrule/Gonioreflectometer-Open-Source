# Wiring and pins

Verify E4 pins on its schematic [C1].

| E4 function | GPIO |
|---|---|
| M4 (X) step, dir | 27, 26 |
| M3 (Y) step, dir | 33, 32 |
| M2 (Z) step, dir | 14, 12 |
| M1 (E0) step, dir | 16, 17 |
| Enable (all) | 25 |
| TMC UART TX, RX | 22, 21 — addr X1 Y3 Z0 E2 |
| Home M4, M3, M2, M1 | 34, 35, 15, 36 |
| PAUSE | 39 |
| White light, LED bank, fan | 2, 4, 13 (`M62/M63 P0/P1/P2`) |

| Pico function | GP |
|---|---|
| HOME START STOP LIGHT NEXT (to GND) | 2–6 |
| E-stop sense (J4, low = on) | 7 |
| LED bank → ULN2803A (Phase 10) | 8–15 |
| Optional AS5600 (SCL, SDA) | (17,16) (19,18) (21,20) (27,26) |

| From | To |
|---|---|
| J2 | E4 VIN |
| Motors M4 M3 M2 M1 | E4 X Y Z E |
| White COB driver −Vin | E4 HE0 |
| J4-1 / J4-2 | Pico GP7 / GND |
