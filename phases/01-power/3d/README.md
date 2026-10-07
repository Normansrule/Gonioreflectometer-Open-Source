# 01 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| PWR-18a | Power box | [PWR-18a_power_box.step](PWR-18a_power_box.step) | [PWR-18a_power_box.stl](PWR-18a_power_box.stl) |
| PWR-18b | Power box lid (e-stop) | [PWR-18b_power_lid.step](PWR-18b_power_lid.step) | [PWR-18b_power_lid.stl](PWR-18b_power_lid.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| PWR-01 | AC adapter 24 V 2.5 A 60 W | STEP listed on the Mouser product page (not downloaded) |
| PWR-02 | IEC C13 mains cord | n/a |
| PWR-03 | DC jack to screw-terminal adapter 2.1 mm | Model as a 11 × 30 mm cylinder + block |
| PWR-04 | Inline 5 x 20 mm fuse holder | n/a |
| PWR-05 | Fuse 3.15 A time-lag 5 x 20 mm | n/a |
| PWR-10 | Optocoupler PC817 (DIP-4) | Standard DIP-4 model |
| PWR-11 | Resistors 10k (2) | Standard axial |
| PWR-13 | Emergency stop 22 mm latching, 1 NC | Not confirmed - 22.3 mm hole, 40 mm head |
| PWR-15 | 18 AWG silicone wire red/black, 1 m pair | n/a |
| PWR-19 | Half-size breadboard (400 points) | n/a |
| PWR-20 | Lever wire connectors, assorted (28) | n/a |

Design notes: [../design.md](../design.md).
