# 01 · Design

## Battery, charged over USB-C

<img src="../../docs/assets/power-flow.svg" width="100%" alt="Power path">

The machine runs from a **ready-made 24 V lithium-ion pack** (6 cells in series, 5 Ah) with its own protection board
(battery management system, BMS: over-charge, over-discharge, over-current, short circuit). The bus is the pack voltage,
18–24 V; the SKR Pico motor board takes 12–24 V. Charging is laptop-style: a USB-C charger plugs into a trigger board in the box wall that
asks it for 20 V (USB Power Delivery, PD); a constant-voltage / constant-current (CC/CV) module turns that into
**24.0 V, 1.0 A** for the pack. It can stay plugged in while measuring. No mains in the machine, no solder, no crimps.

| Part | Job | Rating |
|---|---|---|
| PWR-21 Xeanerol 6S 5 Ah pack [P49] | battery, BMS inside, bare red/black leads | 10 A out, 2 A charge max; ~76 Wh usable to 3.0 V per cell |
| PWR-27 USB-C PD trigger [P55] | USB-C input in the +X wall; DIP switch on 20 V; display shows what it got | falls back to 5 V if 20 V isn't offered: then nothing charges (M04.2) |
| PWR-29 DROK CC/CV module [P57] | the charger: 20 V in → 24.00 V, 1.000 A limit; LCD shows pack voltage and charge current | 35 W; output anti-backflow (the pack can't feed back into it) |
| PWR-04 + PWR-05 fuse | 3.15 A time-lag in an inline holder on the pack `+` lead: a short anywhere after it blows the fuse before the 18 AWG wire heats | peak draw 1.7 A at 18 V |
| PWR-28 e-stop [P56] | cuts the pack to the SKR Pico: motors, lamp; also the off switch | NC contact, 10 A |
| PWR-10 opto module | SKR Pico POWER → ESP32-S3 GPIO 17: motion-power sense | 24 V module |

**Why 24.0 V and not 25.2 V:** a 6S pack is full at 25.2 V (4.2 V per cell), above the motor board's 24 V rating. Charging to
4.0 V per cell keeps the bus at ≤ 24.0 V and is gentler on the cells, for ~15 % less capacity. The pack ships with a
25.2 V wall charger: **don't use it** for this machine.

**Trade-offs:** no low-voltage alarm. The BMS is the last cut-off, at a voltage the listing doesn't give: recharge after
each session, or keep the USB-C charger plugged in (24 W charge covers the 13 W typical draw). Charging runs with the
e-stop pressed too. Charge on a hard surface and don't leave it charging unattended until M06's temperature check has
passed. Run time and charge time: [power_budget.md](power_budget.md) (~6 h typical; ~4 h empty to full).

## Netlist and build (no solder)

Pin by pin, with every terminal: [README → Wiring](../../README.md#wiring) (groups 1–2, 6).

| Net | Members | Joined by |
|---|---|---|
| USB-C | USB-C charger (≥ 30 W, 20 V PD; the laptop's) → trigger board input through the +X wall | plug |
| V20 | trigger `+` / `−` → DROK IN `+` / `−` | screw terminals |
| BAT+ | pack red lead → fuse holder lead A (2-way lever connector) | lever connector |
| FUSED | fuse holder lead B + DROK OUT `+` + red wire to e-stop NC 1 (+ optional Pi buck `+`, stage 15) | 3-way (5-way with the Pi) lever connector |
| MOTION (red wire) | e-stop NC 2 → out of the +Y slot → over-travel switch COM–NC (stage 04) → MOT+ lever connector on the tray → 10 cm lead → SKR Pico POWER `+` (+ opto sense lead) | screw terminals, 3-way lever connector |
| GND (black) | pack black lead + DROK OUT `−` + black wire (+ optional Pi buck `−`) → MOT− lever connector on the tray → 10 cm lead → SKR Pico POWER `−` (+ opto sense lead) | 3-way (5-way) lever connector; 3-way on the tray |
| OPTO_IN | MOT+ / MOT− lever connectors → opto module (PWR-10) input `+` / `−` (series resistor on the module) | cut jumpers folded double; module screw terminals |
| OPTO_OUT | module VCC ← ESP32-S3 3V3, GND ← ESP32-S3 GND, OUT → GPIO 17 | male–female jumpers |

ESP32-S3 GPIO 17 reads low when MOTION is on (`SENSE_ACTIVE_LOW` in the hub firmware flips it for modules that drive OUT high).
The optional standalone Pi (STA-03 buck) takes its input after the fuse, before the e-stop.

### Build

1. Set the DROK first, on the bench, pack **not** connected: USB-C charger → trigger (20 V) → DROK IN; turn the CV pot
   to 24.00 V on the LCD, short OUT `+`/`−` with a spare wire through the multimeter on 10 A and turn the CC pot to
   1.00 A (M04). Then unplug the USB-C charger.
2. Self-tap 4 × M2 × 10 into the box posts once. E-stop in the lid hole.
3. Pack upright in its floor frame, leads toward +X. The lid ribs stop it lifting.
4. DROK and trigger board in their frames on double-sided tape (TLS-09); trigger USB-C into the +X opening.
5. Fuse (3.15 A T) into the holder; holder in its cradle. Wire per the netlist, pack leads **last**. Strip 8 mm for
   screws, 11 mm for lever connectors; twist strands; tug-test every wire.
6. Lid M2 × 10, snug (it's plastic); box to deck: 4 × M2 × 12 through the floor bosses into the SE tile's pilots.

## 3D parts

| Part | Source |
|---|---|
| Box 160 × 130 × 80, lid (PWR-18) | `tools/cad/parts.py`: walls 2.4 mm, floor frames on pads for the pack (`PACK`), the DROK (`DROK`) and the trigger board (`TRIG`), fuse-holder cradle, USB-C opening (+X), lid ribs over the pack, Ø22.3 e-stop hole, motor-power and J3 slots (+Y), vents (±X), M2 self-tap posts, 6 mm floor bosses (M2 into the deck pilots) |
| Bought parts | models drawn in this repo (`tools/cad/bought.py` → `cad/bought/`) at the sizes below: simplified outer shapes, not maker models (none are published), except WAGO, whose own STEP is linked in the BOM |

### Model sizes and where they come from

Checked 2026-10-14. The size column is the generated file's bounding box (`cad/bought/*.step`).

| Part | Model size (mm) | Source | Status |
|---|---|---|---|
| PWR-21 pack | 78 × 50 × 72 (+12 lead stub) | Amazon listing [P49], read 2026-10-12 | listing value; Amazon could not be re-read on 2026-10-14: **measure on arrival** |
| PWR-29 DROK CC/CV | 72 × 59 × 32 | DROK product page: "Size: 72\*59\*32mm" [P57] | maker value |
| PWR-27 PD trigger | 60 × 30 × 13.6 | none published | **estimate: measure on arrival** |
| PWR-04 fuse holder | body Ø11 × 47.5, leads Ø2.6 (16 AWG) | Littelfuse drawing for 01500274Z [P6] | maker value |
| PWR-05 fuse | Ø5 × 20 | IEC 60127 size | standard |
| PWR-28 e-stop | Ø40 head, 70 overall, 22 mm hole | LAY37-11ZS listing: 40 mm head, "60 × 70 mm (max D × H)" [P56] | listing value |
| PWR-10 opto module | 66 × 16.5 × 12 | NOYITO manual: "66mm x 16.5mm x 12mm" | maker value |
| PWR-20 WAGO 221-412 | 18.6 × 13.2 × 8.4 | WAGO data sheet [P47] | maker value (maker STEP also available) |

If a part measures more than 1 mm off, change its constant in `tools/cad/parts.py` (`PACK`, `DROK`, `TRIG`) and the model in
`tools/cad/bought.py`, then `make parts cad` (the clash check must stay at 0).

## Results

(fill in)
