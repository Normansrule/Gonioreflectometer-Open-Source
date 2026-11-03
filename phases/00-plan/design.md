# 00 · Design

## Architecture

Camera fixed, sample turns on three axes, light turns on an arm; all meet at one zero point [R1]. Laptop controls and processes.

<img src="../../docs/assets/axes.svg" width="100%" alt="Axes">

### Axes

| Axis | Moves | Range | Drive | Step | Phase |
|---|---|---|---|---|---|
| M4 | Light arm around the sample | 20–324° | belt on 12 in ring, ~24:1 | 0.0047° | 04 |
| M3 | Table (vertical axis) | ±180° | 5:1 belt | 0.0225° | 05 |
| M2 | Tilt | ±90° | 5:1 belt | 0.0225° | 08 |
| M1 | Spin | ±180° | direct drive (pancake motor), 1/64 microstep | 0.028° | 09 |

Optical home per axis; one over-travel switch in the e-stop loop (light arm, at 17°; the other ends rely on soft limits and the e-stop); software keep-out ≥ 30 mm and ≥ 5° light–camera gap [R1].

### Frame

Origin = sample surface. +Z up. Camera on +X (350 mm; 650 mm for scans). Light at 300 mm. $R = R_z(M_3)R_y(-M_2)R_x(M_1)$ ([theory](research.md)).

### Control

<img src="../../docs/assets/architecture.svg" width="100%" alt="Control">

| Path | How |
|---|---|
| Laptop → motors | grblHAL on the BTT SKR Pico over USB-C [C12][R85] (FluidNC ESP32 boards also supported) |
| Laptop → camera | USB, locked exposure / gain / white balance [R47][R50] |
| Keys | HOME START STOP LIGHT NEXT (membrane keypads) → ESP32-S3 hub → `opengonio panel` |
| No laptop | Pi Zero 2 W runs `opengonio station`: buttons + OLED pick jobs, images saved on the Pi ([15-standalone](../15-standalone/design.md)); the Pi drives the SKR Pico over USB |
| Stop | E-stop cuts motor power; software re-inits drivers (grblHAL `M122 I`) and forces re-home |

### Interfaces (frozen)

- **OG-40:** 4 × M2 holes on 40 × 40 mm, Ø6.2 locating hole.
- **One screw size:** every printed join and module mount is an M2 socket screw (FRM-06) self-tapping into a 1.7 mm printed pilot (`M2_TAP`, set from the coupon) or through a clearance hole into a nut. Only the NEMA 17 faces keep M3 (the motors' own thread) and the axles M8 bolts.
- **Deck:** 9 printed 200 mm tiles bolted into a 600 × 600 × 24 mm deck with a pilot boss at every mount point (`PLACE` in `tools/cad/parts.py`; map: `phases/03-frame/deck-map.svg`) and a 40 mm grid of spare pilots. No plywood, no extrusion, no drilling.
- **Joins (no solder, no crimp):** screw terminals; lever connectors for wire to wire; jumper wires onto pins; modules with screw terminals instead of loose chips (no breadboard); JST-XH pre-crimped leads into the SKR Pico; 1 m PH→XH cables for the motors; M8 bolts as axles (no shafts to cut).

| Code | Connector | Pins |
|---|---|---|
| J1 | 24 V wall adapter → screw-terminal jack → e-stop | +24 V, GND |
| J2 | 18 AWG pair → MOT+ / MOT− lever connectors → SKR Pico POWER screw terminal | 24 V after e-stop (red), GND (black) |
| J3 | the limit switch's own black (COM) and grey (NC) wires, in the red line | over-travel switch (NC) |
| SENSE | opto module (PWR-10) screw terminals + jumpers | isolated motion-power sense → ESP32-S3 GPIO 17, GND, 3V3 |
| M-x | the 5-pack's 1 m cables (6-pin motor end → XH2.54 4-pin); M1 pancake: bare leads spliced to a spare cable with lever connectors | SKR Pico socket pins 2B 1B 1A 2A |
| E-x | double-ended JST-XH leads (CTL-06), XH housing on the module pins | signal, GND, 5 V (TCST2103) from the SKR Pico X/Y/Z/E0-STOP ports |
| L-x | female jumper ends on the driver's pins; jumper chains to the lamp | driver +Vin to SKR Pico HE 12/24V, −Vin to HE IO23 (switched), +Vo/−Vo to the COB holder |
| KEY | 2 × membrane 1x4, male–female jumpers; both commons in one lever connector | 5 keys (+ PAUSE) + common to GND (J1-22) |

## Onshape set-up

1. Create one document, **OpenGonio**, with a Variable Studio `OG globals`: `#clear` `#og40` `#cam_d`=350 `#scan_d`=650 `#light_d`=300 `#zero_h`=150 `#ring_r`=140.
2. Import the whole machine: **Create → Import** `cad/assembly/opengonio_assembly.step` (or `dist/opengonio-cad.zip` from `make cad-zip`, every STEP at once). Origin = deck top under the zero point (zero point at z = 150 mm), +X toward the camera, +Z up. Printed parts are black, bought parts are dummies (tan) — [cad/README.md](../../cad/README.md) lists the model for every part.
3. Import the starter parts you edit: **Insert → Import** each `phases/NN/3d/*.step`. STEP arrives as editable solids; STL would arrive as a fixed mesh. Real vendor models (`bash scripts/get_cad.sh` → `cad/vendor/`) replace dummies at the same origin.
4. One Part Studio per stage; name parts by BOM ID (e.g. `PWR-18`). Run interference check on the assembly.
5. Release: export STEP + STL back into that stage's `3d/`, commit with `bash scripts/update.sh "…"`.

Or edit the numbers in `tools/cad/parts.py` and run `python tools/cad/parts.py` to regenerate every file.

## Results

(fill in)
