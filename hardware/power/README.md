# Power module · Phase 1 · M1.1

<img src="../../docs/assets/power-flow.svg" width="100%" alt="Power path">

## 1. Purpose and interfaces

24 V for the whole machine from one certified adapter, with fuse, reverse-polarity protection, master switch and a latching e-stop that cuts the motion board. Sized for all phases: 28 W peak on a 60 W adapter ([`docs/power.md`](../../docs/power.md)).

| Port | Connector | Signal |
|---|---|---|
| J1 in | Switchcraft 721A (2.1 mm) | +24 V centre, GND sleeve |
| J2 out | XT30 female | 24 V MOTION (after e-stop) → E4 VIN |
| J3 loop | JST-XH 2 | over-travel roller switches (NC, in series with the e-stop) |
| J4 out | JST-XH 2 | isolated MOTION_SENSE: 1 opto collector → Pico GP7 (pull-up) · 2 opto emitter → Pico GND |
| Mount | OG-40 at (−220, −220) | 4 × M4 |

Later phases add only loads on J2 (motors via E4, lights via E4 MOSFETs). Nothing here changes.

## 2. BOM — $67.63 buy-all / $47.89 with own stock

[`bom/modules/power.csv`](../../bom/modules/power.csv)

| ID | Part | Qty | USD | Ref |
|---|---|---:|---:|---|
| PWR-01 | MEAN WELL GST60A24-P1J | 1 | 19.40 | [P1] |
| PWR-02 | IEC C13 cord (often owned) | 1 | 5.00 est. | [P3] |
| PWR-03 | Switchcraft 721A jack | 1 | 4.03 | [P4][P5] |
| PWR-04 | Littelfuse 01500274ZXU inline holder | 1 | 3.27 | [P6] |
| PWR-05 | Fuse 3.15 A T 5×20 | 2 | 0.60 est. | — |
| PWR-06 | IRF4905PBF | 1 | 2.73 | [P7][P8] |
| PWR-07 | 1N4742A 12 V zener | 1 | 0.28 | [P9] |
| PWR-08 | P6KE30A TVS | 1 | 0.94 | [P10] |
| PWR-09 | 100 µF 50 V | 1 | 0.59 | [P11] |
| PWR-10 | PC817 optocoupler | 1 | 0.30 est. | — |
| PWR-11 | Resistors 10k ×2 | 1 | 0.40 est. | — |
| PWR-12 | Bulgin C1353ABNAB rocker | 1 | 3.00 est. | [P13] |
| PWR-13 | IDEC YW1B-V4E01R e-stop | 1 | 9.96 | [P15][P16] |
| PWR-14 | XT30U ×5 pairs | 1 | 2.19 | [P18] |
| PWR-15 | 18 AWG silicone pair 1 m | 1 | 8.09 | [P20] |
| PWR-16 | Perfboard 3-pack | 1 | 2.25 | [P21] |
| PWR-17 | Heat-shrink | 1 | 4.00 est. | — |

STEP: adapter (Mouser listing [P1]); XT30 (community [P19]); IRF4905 (TO-220 library). Jack, e-stop, rocker: model from datasheets ([P4][P16][P13]).

## 3. Onshape — Part Studio `PWR`

Variables: `#box` 120 × 80 × 50 mm, `#wall` 3.2, `#clear` 0.25, `#ins_m3_d` 4.0, `#estop_d` 22.3, `#jack_d` (from 721A drawing), `#rocker` (from C1353 datasheet), `#xt30` 10.4 × 5.4.

1. Sketch box outline, fillet 6 → extrude → shell open top.
2. Four corner posts with M3 insert holes; perfboard bosses; Q1 boss (M3 insert).
3. Floor: OG-40 holes, counterbored.
4. Front: rocker cutout. Rear: jack hole, XT30 slot (`24V MOTION`), J4 slot. Lid: `#estop_d` hole + anti-rotation notch.
5. Side vents; embossed labels.

Print PETG, 0.2 mm, 4 walls, 25 % gyroid, open side up, no supports. Export STEP → `cad/`, 3MF → `print/`.

## 4. Assembly

1. Heat-set inserts (245 °C). Fit jack, rocker, e-stop (lid).
2. Perfboard: Q1 (G-D-S legs; drain = input, source = bus), DZ1 band to source, R1 10k gate→GND, D2 band to bus, C1 + to bus.
3. Sense: R2 10k from MOTION to U2 (PC817) anode; U2 cathode → GND. U2 collector → J4-1, emitter → J4-2. Pico side only sees the isolated transistor.
4. Wire 18 AWG: J1+ → fuse → rocker → Q1 drain; bus → e-stop NC → J3 (roller switches, NC, series) → J2+. Star ground.
5. Heat-shrink every joint. Lid M3 × 10 at 0.5 N·m. Box to base M4 × 12 at 1.2 N·m.

## 5. Netlist

| Net | Members |
|---|---|
| VIN | J1 centre, fuse A |
| VIN_F | fuse B, rocker common |
| VIN_SW | rocker out, Q1 drain |
| BUS_24V | Q1 source, DZ1 cathode, D2 cathode, C1 +, e-stop 1 |
| GATE | Q1 gate, DZ1 anode, R1 |
| ESTOP_OUT | e-stop 2 (NC), J3-1 |
| MOTION | J3-2, J2 +, R2 |
| OPTO_A | R2, U2 anode (pin 1) |
| GND | J1 sleeve, R1, D2 anode, C1 −, J2 −, U2 cathode (pin 2) |
| ISO_C | U2 collector (pin 4), J4-1 |
| ISO_E | U2 emitter (pin 3), J4-2 |

LED current (24 − 1.2) / 10k = 2.3 mA. Pico GP7 reads **low** when motion power is on. No 24 V-side wire reaches the Pico.

## 6. Software

- `opengonio sleep` → lights off, `$MD`; `opengonio wake` → `$ME`.
- Pico reports `POWER 0/1`; `Panel` marks all axes unhomed on `POWER 0`.

## 7. Acceptance test (log in [`acceptance_log.csv`](acceptance_log.csv))

| # | Test | Pass |
|---|---|---|
| T1 | Adapter unplugged: bus–GND resistance | > 10 kΩ |
| T2 | Diode test Q1 drain→source | 0.4–0.8 V one way, open the other |
| T3 | No load: J2 voltage | 23.5–24.5 V |
| T4 | E4 + both motors holding: J2 | ≥ 23.0 V |
| T5 | E-stop pressed | J2 < 1 V in 1 s; hub prints `POWER 0`; laptop keeps running |
| T6 | Rocker off | J2 < 0.5 V in 2 s |
| T7 | Hub `POWER?` with 24 V on / e-stop pressed / J3 opened | `POWER 1` / `POWER 0` / `POWER 0` |
| T8 | Fuse | 3.15 A T fitted, spare in box |
| T9 | 30 min run, lid on | box air ≤ 45 °C |
| T10 | Idle wall draw (`opengonio sleep`) | ≤ 3 W |

## 8. Safety

Mains only in the adapter. Plug in with the rocker off. Q1 tab is +24 V. E-stop is not a certified safety circuit. Fuse and 18 AWG on every power path.
