# 01 · Research

## Requirements

| Need | Met by | Check |
|---|---|---|
| Fewest parts, plug or screw only | 24 V 3 A wall adapter with a screw-terminal jack [P59], e-stop in its own box [P60], WAGO lever connectors [P62] | T1, T3 |
| Bus inside the motor board's 12–24 V | regulated 24 V adapter | `tools/power_budget.py --check` (bus) |
| ≥ 25 % current headroom | 3 A adapter / peak draw | `power_budget.py` (adapter) |
| Short-circuit protection without a fuse | adapter's own short-circuit and overload protection (listing) | T1 before power; T5 |
| E-stop, no solder | latching e-stop NC on the + line, screw terminals + lever connectors | T1, T5 |
| Over-travel cut | pre-wired sealed roller switch [P61] in the + line after the e-stop (stage 04) | M14.1 |
| Motion-power sense | PC817 opto module (24 V version) | T7 |

## Options considered

| Option | Why not (now) |
|---|---|
| 6S Li-ion pack + USB-C PD trigger + CC/CV module + fuse (~$90, the 12–19 Oct design) | dropped on 19 Oct 2026: plug-in only, fewer parts |
| MEAN WELL GST60A24 adapter ($35) | UL-listed, but no screw-terminal jack included (needs a separate jack) and twice the price |
| Bare 22 mm e-stop in a printed lid | needs a printed box and a panel hole; the e-stop station comes in its own box |
| ME-8108 roller limit switch with screw terminals | DC rating 0.25 A in its listing; the pre-wired sealed switch lists 6 A at 12 V DC and needs no terminals |
| USB-C power bank 65 W + trigger (~$66) | replaced on request: a plain lithium pack instead of a power bank |
| Pack + 80 W converter for a regulated 24 V (~$143) | the converter isn't needed once the pack is charged to 24.0 V |
| Parts with maker 3D models (MEAN WELL, Phoenix Contact) | ~$50 more; the cheap modules are measured on arrival instead |
| Pack's own 25.2 V wall charger | full pack 25.2 V is above the motor board's 24 V rating; not USB-C |
| USB-C charging board for 6S (built-in boost + balance) | needs soldering on the boards found; the DROK has screw terminals |

Numbers: [power_budget.md](power_budget.md).
