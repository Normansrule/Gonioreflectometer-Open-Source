# 00 · Design

## Architecture

Camera fixed, sample turns on three axes, light turns on an arm; all meet at one zero point [R1]. Laptop controls and processes.

<img src="../../docs/assets/axes.svg" width="100%" alt="Axes">

### Axes

| Axis | Moves | Range | Drive | Step | Phase |
|---|---|---|---|---|---|
| M4 | Light arm around the sample | 20–340° | belt on 12 in ring, ~24:1 | 0.0047° | 04 |
| M3 | Table (vertical axis) | ±180° | 5:1 belt | 0.0225° | 05 |
| M2 | Tilt | ±90° | 5:1 belt | 0.0225° | 08 |
| M1 | Spin | ±180° | direct drive (pancake motor), 1/64 microstep | 0.028° | 09 |

Optical home per axis; over-travel switches in the e-stop loop; software keep-out ≥ 30 mm and ≥ 5° light–camera gap [R1].

### Frame

Origin = sample surface. +Z up. Camera on +X (350 mm; 650 mm for scans). Light at 300 mm. $R = R_z(M_3)R_y(-M_2)R_x(M_1)$ ([theory](research.md)).

### Control

<img src="../../docs/assets/architecture.svg" width="100%" alt="Control">

| Path | How |
|---|---|
| Laptop → motors | FluidNC on FYSETC E4: USB, WiFi (telnet :23) or Bluetooth [R24][R30] |
| Laptop → camera | USB, locked exposure / gain / white balance [R47][R50] |
| Keys | HOME START STOP LIGHT NEXT (membrane keypads) → Pico → `opengonio panel` |
| No laptop | Pi Zero 2 W runs `opengonio station`: buttons + OLED pick jobs, images saved on the Pi ([15-standalone](../15-standalone/design.md)); phone WebUI; PAUSE on E4 feed hold [R27] |
| Stop | E-stop cuts 24 V; software re-inits drivers (`$MI`) and forces re-home |

### Interfaces (frozen)

- **OG-40:** 4 holes (4.5 mm: M4 or #8 wood screw) on 40 × 40 mm, Ø6.2 locating hole. Onto the plywood: #8 Type 17 wood screws, no drilling.
- **Joins (no solder, no crimp):** screw terminals; lever connectors for wire to wire; jumper wires onto pins; breadboard for small parts; JST-XH pre-crimped leads into the E4; 1 m PH→XH cables for the motors; M8 bolts as axles (no shafts to cut).

| Code | Connector | Pins |
|---|---|---|
| J1 | DC jack → screw terminals (Adafruit 368) | +24 V centre, GND sleeve |
| J2 | 18 AWG pair → E4 VIN screw terminal | 24 V after e-stop (red), GND (black) |
| J3 | the red wire itself, through the switch's COM–NC screws | over-travel switch (NC) |
| SENSE | breadboard + jumpers | isolated e-stop sense (PC817) → Pico GP7, GND |
| M-x | 1 m cable PH2.0-6P → XH2.54-4P (CTL-11) | motor A+ A− B+ B− |
| E-x | double-ended JST-XH leads (CTL-06), XH housing on the module pins | V, GND, signal (TCST2103); M1 on TH0 takes V from Pico 3V3 |
| L-x | breadboard rows; jumper chains to the lamp | driver +Vin, −Vin to E4 HE0 −, +Vo/−Vo to the COB holder |
| KEY | 2 × membrane 1x4, male–female jumpers | 5 keys (+ PAUSE) + common to GND |

## Onshape set-up

1. Create one document, **OpenGonio**, with a Variable Studio `OG globals`: `#clear` `#og40` `#cam_d`=350 `#scan_d`=650 `#light_d`=300 `#zero_h`=150 `#ring_r`=140.
2. Import the starter parts: **Insert → Import** each `phases/NN/3d/*.step` (or drag them in). STEP arrives as editable solids; STL would arrive as a fixed mesh.
3. One Part Studio per stage; name parts by BOM ID (e.g. `PWR-18a`). One assembly with the zero point as origin; run interference check.
4. Release: export STEP + STL back into that stage's `3d/`, commit with `bash scripts/update.sh "…"`.

Or edit the numbers in `tools/cad/parts.py` and run `python tools/cad/parts.py` to regenerate every file.

## Results

(fill in)
