# 01 · Design

## Netlist and build

<img src="../../docs/assets/power-flow.svg" width="100%" alt="Power path">

| Net | Members |
|---|---|
| VIN | J1 centre, fuse A |
| VIN_F | fuse B, rocker common |
| VIN_SW | rocker out, Q1 drain |
| BUS_24V | Q1 source, DZ1 cathode, D2 cathode, C1 +, e-stop 1 |
| GATE | Q1 gate, DZ1 anode, R1 |
| ESTOP_OUT | e-stop 2 (NC), J3-1 |
| MOTION | J3-2, J2 +, R2 |
| OPTO_A | R2, U2 pin 1 |
| GND | J1 sleeve, R1, D2 anode, C1 −, J2 −, U2 pin 2 |
| ISO_C | U2 pin 4, J4-1 |
| ISO_E | U2 pin 3, J4-2 |

Q1 IRF4905, DZ1 1N4742A, D2 P6KE30A, C1 100 µF, R1/R2 10 k, U2 PC817. Opto LED 2.3 mA; Pico GP7 reads low when 24 V is on.

### Build

1. Heat-set inserts (245 °C). Fit jack, rocker, e-stop.
2. Q1 legs G-D-S: drain = input, source = bus. Zener band to source.
3. 18 AWG main path; star ground; heat-shrink every joint.
4. Lid M3 × 10 at 0.5 N·m; box to base M4 × 12 at 1.2 N·m.

## 3D parts

| Part | Source |
|---|---|
| Box 120 × 80 × 50, lid (PWR-18) | Onshape `PWR`: shell 3.2 mm, M3 insert posts, OG-40 floor, rocker / jack / XT30 / J3 / J4 cut-outs, Ø22.3 e-stop hole in lid |
| Adapter GST60A24 | STEP on [Mouser](https://www.mouser.com/ProductDetail/MEAN-WELL/GST60A24-P1J?qs=odmYgEirbwyH6XaEPxnETQ%3D%3D) [P1] |
| XT30 | [realthunder](https://github.com/realthunder/Connectors_Amass.3dshapes) [P19] |
| IRF4905 | TO-220 library model |
| Jack, rocker, e-stop | model from datasheets [P4][P13][P16] |
