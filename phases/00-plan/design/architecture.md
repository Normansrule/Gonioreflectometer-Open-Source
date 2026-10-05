# Architecture

Camera fixed, sample turns on three axes, light turns on an arm; all meet at one zero point [R1]. Laptop controls and processes.

<img src="../../../docs/assets/axes.svg" width="100%" alt="Axes">

## Axes

| Axis | Moves | Range | Drive | Step | Phase |
|---|---|---|---|---|---|
| M4 | Light arm around the sample | 20–340° | belt on 12 in ring, ~24:1 | 0.0047° | 04 |
| M3 | Table (vertical axis) | ±180° | 5:1 belt | 0.0225° | 05 |
| M2 | Tilt | ±90° | 5:1 belt | 0.0225° | 08 |
| M1 | Spin | ±180° | 4:1 belt | 0.028° | 09 |

Optical home per axis; over-travel switches in the e-stop loop; software keep-out ≥ 30 mm and ≥ 5° light–camera gap [R1].

## Frame

Origin = sample surface. +Z up. Camera on +X (350 mm; 650 mm for scans). Light at 300 mm. $R = R_z(M_3)R_y(-M_2)R_x(M_1)$ ([theory](../research/theory.md)).

## Control

<img src="../../../docs/assets/architecture.svg" width="100%" alt="Control">

| Path | How |
|---|---|
| Laptop → motors | FluidNC on FYSETC E4: USB, WiFi (telnet :23) or Bluetooth [R24][R30] |
| Laptop → camera | USB, locked exposure / gain / white balance [R47][R50] |
| Buttons | HOME START STOP LIGHT NEXT → Pico → `opengonio panel` |
| No laptop | Pi Zero 2 W runs `opengonio station`: buttons + OLED pick jobs, images saved on the Pi ([15-standalone](../../15-standalone/design/notes.md)); phone WebUI; PAUSE on E4 feed hold [R27] |
| Stop | E-stop cuts 24 V; software re-inits drivers (`$MI`) and forces re-home |

## Interfaces (frozen)

- **OG-40:** 4 × M4 on 40 × 40 mm, Ø6.2 locating hole.
- **Connectors:** JST-XH inside modules, XT30 for 24 V, female XT30 on sources.

| Code | Connector | Pins |
|---|---|---|
| J1 | Switchcraft 721A | +24 V centre, GND sleeve |
| J2 | XT30 | 24 V after e-stop, GND |
| J3 | JST-XH 2 | over-travel switches (NC) |
| J4 | JST-XH 2 | isolated e-stop sense → Pico GP7, GND |
| M-x | JST-XH 4 | motor A+ A− B+ B− |
| E-x | JST-XH 3 | V, GND, signal (TCST2103) |
| L-x | JST-XH 2 | driver +Vin, switched − |
| BTN | JST-XH 6 | 5 buttons + GND |
