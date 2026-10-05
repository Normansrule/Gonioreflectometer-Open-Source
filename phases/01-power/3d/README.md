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
| PWR-03 | Panel DC jack 2.1 mm pin, 5 A / 24 V | [link](https://www.switchcraft.com/dc-power-jack-0-084-2-1mm-pin-solder-lugs-termination/721a/) Not confirmed - datasheet drawing on |
| PWR-04 | Inline 5 x 20 mm fuse holder | n/a |
| PWR-05 | Fuse 3.15 A time-lag 5 x 20 mm | n/a |
| PWR-06 | P-channel MOSFET -55 V 74 A | Standard TO-220 model (SnapEDA lists one) |
| PWR-07 | Zener 12 V 1 W | Standard DO-41 |
| PWR-08 | TVS diode 30 V | Standard DO-15 |
| PWR-09 | Capacitor 100 uF 50 V | Standard radial |
| PWR-10 | Optocoupler PC817 (DIP-4) | Standard DIP-4 model |
| PWR-11 | Resistors 10k (2) | Standard axial |
| PWR-12 | Rocker switch SPST, DC rated | Not confirmed - measure cutout |
| PWR-13 | Emergency stop 22 mm latching, 1 NC | Not confirmed - 22.3 mm hole, 40 mm head |
| PWR-14 | XT30U pairs (5) | [link](https://github.com/realthunder/Connectors_Amass.3dshapes) Community STEP (no licence stated) |
| PWR-15 | 18 AWG silicone wire red/black, 1 m pair | n/a |
| PWR-16 | Perfboard 2 x 8 cm (3-pack) | Plate model |
| PWR-17 | Heat-shrink assortment | n/a |

Design notes: [../design.md](../design.md).
