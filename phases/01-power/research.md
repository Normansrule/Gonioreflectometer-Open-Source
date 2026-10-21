# 01 · Research

## Requirements

| Need | Met by | Check |
|---|---|---|
| Rechargeable over USB-C, cheap | 6S pack with BMS [P49] + PD trigger [P55] + CC/CV module [P57], ~$69 | T3, T13 |
| Lithium made safe without soldering | ready-made pack with BMS (over-charge/-discharge/-current, short); CC/CV limits charge to 24.0 V, 1.0 A; 3.15 A fuse on the pack lead; screw terminals + lever connectors | T1, T3, T13 |
| Bus inside the motor board's 12–24 V | pack 18–24.0 V (charged to 4.0 V per cell) | `tools/power_budget.py --check` (bus) |
| ≥ 25 % current headroom | 10 A pack / 1.7 A peak at 18 V | `power_budget.py` (battery) |
| A working session on the pack | ~6 h typical (≥ 3 h required); unlimited with the USB-C charger plugged in | T15 |
| E-stop, no solder | latching e-stop NC on the pack line, screw terminals + lever connectors | T1, T5 |
| Motion-power sense | PC817 opto module (24 V version) | T7 |

## Options considered

| Option | Why not (now) |
|---|---|
| 24 V adapter only (MEAN WELL GST60A24, $35) | not rechargeable; was the first design |
| USB-C power bank 65 W + trigger (~$66) | replaced on request: a plain lithium pack instead of a power bank |
| Pack + 80 W converter for a regulated 24 V (~$143) | the converter isn't needed once the pack is charged to 24.0 V |
| Parts with maker 3D models (MEAN WELL, Phoenix Contact) | ~$50 more; the cheap modules are measured on arrival instead |
| Pack's own 25.2 V wall charger | full pack 25.2 V is above the motor board's 24 V rating; not USB-C |
| USB-C charging board for 6S (built-in boost + balance) | needs soldering on the boards found; the DROK has screw terminals |

Numbers: [power_budget.md](power_budget.md).
