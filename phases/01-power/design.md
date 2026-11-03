# 01 · Design

## Plug-in power: wall adapter, e-stop, limit switch

<img src="../../docs/assets/power-flow.svg" width="100%" alt="Power path">

The machine runs from a **24 V 3 A wall adapter** (PWR-30, 72 W). The adapter stays outside the machine; its round
plug goes into a **screw-terminal jack** that sits in a frame on the printed power plate. From there one `+` line runs
through the **e-stop** (PWR-28, its own box, NC contact) and the **limit switch** (LAR-06, stage 04) to the MOT+ lever
connector on the controller tray, which feeds the SKR Pico and the opto module. Ground goes straight from the jack to
MOT−. No battery, no charging, no fuse, no solder, no crimps: every join is a screw terminal, a lever connector or a
plug. Changed from the battery design on 19 Oct 2026 (the battery was dropped).

| Part | Job | Rating |
|---|---|---|
| PWR-30 ALITOVE adapter + jack [P59] | 24 V for the motors, lamp and board; the jack turns its round plug into `+` / `−` screws | 24 V, 3 A; short-circuit, overload and over-temperature protection (listing) |
| PWR-28 BAOMAIN e-stop box [P60] | cuts 24 V to the SKR Pico: motors, lamp; also the off switch | NC contact, 10 A (AC rating) |
| LAR-06 limit switch [P61] | over-travel: cuts 24 V if the light arm runs past its range (stage 04) | 6 A at 12 V DC (no 24 V DC rating listed) |
| PWR-20 WAGO 221-413 × 2 | MOT+ and MOT−: split the line to the board and the opto module | 20 A |
| PWR-10 opto module | MOT+ / MOT− → ESP32-S3 GPIO 17: motion-power sense | 24 V module |

**Why no fuse:** the adapter limits its own output (short-circuit and overload protection, listing), so a short after it
shuts the adapter down. The 18 AWG wire carries ≥ 5 A, above the adapter's 3 A.

**Trade-offs:** the adapter's listing gives FCC / CE / RoHS marks, not a UL listing; a UL-listed 24 V adapter without the
jack can replace it (the jack is then a separate part). The limit switch is rated 6 A at 12 V DC; at 24 V it breaks
about 1.3 A (peak draw, `power_budget.md`): it opens only in a fault, and the e-stop stays the switch you use.

## Netlist and build (no solder)

Pin by pin, with every terminal: [README → Wiring](../../README.md#wiring) (groups 1–2, 6) and the step-by-step
[wiring guide](../../docs/wiring.html).

| Net | Members | Joined by |
|---|---|---|
| 24 V in | adapter round plug → jack socket | plug |
| + (before the e-stop) | jack `+` → e-stop NC terminal 1 (+ optional Pi buck `+`, stage 15) | screw terminals |
| MOTION + | e-stop NC terminal 2 → red run → 221-2401 → limit switch COM (black) – NC (grey) → 221-2401 → red run → MOT+ lever connector on the tray → 10 cm lead → SKR Pico POWER `+`; MOT+ → opto IN+ | screw terminals, the switch's own wires, 3-way lever connector |
| GND | jack `−` → MOT− lever connector on the tray → 10 cm lead → SKR Pico POWER `−`; MOT− → opto IN− (+ optional Pi buck `−`) | screw terminal, 3-way lever connector |
| OPTO_OUT | module VCC ← ESP32-S3 3V3, GND ← ESP32-S3 GND, OUT → GPIO 17 | male–female jumpers |

ESP32-S3 GPIO 17 reads low when MOTION is on (`SENSE_ACTIVE_LOW` in the hub firmware flips it for modules that drive
OUT high). Until M14.1 a red wire takes the limit switch's place (e-stop NC 2 → MOT+ slot 1).

### Build

1. Print the power plate (PWR-18) (M04.3); it goes on the SE deck tile in M12.2, once the deck exists (4 × M2 × 12).
2. Jack into its frame, round socket toward the deck edge (+X); e-stop box into its rim on double-sided tape (TLS-09).
3. Wire per the netlist with the adapter **unplugged**: strip 8 mm for screws, 11 mm for lever connectors; twist
   strands; tug-test every wire. On the BAOMAIN e-stop NC = terminals 1 and 2 (check with the meter).
4. Checks with power off (T1), then the adapter into the wall (M06).

## 3D parts

| Part | Source |
|---|---|
| Power plate 130 × 110 × 4 (PWR-18) | `tools/cad/parts.py` `power_plate()`: jack frame (`JACK`, `JACK_AT`), 2 mm rim for the e-stop box (`ESTOP_BOX`, `ESTOP_BOX_AT`), 4 counterbored M2 holes on the OG-40 pattern into the SE tile's pilots |
| Bought parts | models drawn in this repo (`tools/cad/bought.py` → `cad/bought/`) at the sizes below: simplified outer shapes, not maker models (none are published), except WAGO, whose own STEP is linked in the BOM |

### Model sizes and where they come from

| Part | Model size (mm) | Source | Status |
|---|---|---|---|
| PWR-30 screw-terminal jack | 32 × 14 × 13 | none published | **estimate: measure on arrival** |
| PWR-28 e-stop box | 70 × 70 × 60 + Ø40 head | none published | **estimate: measure on arrival** |
| LAR-06 limit switch | body 20 × 6.4 × 10 | none published | **estimate: measure on arrival** |
| PWR-10 opto module | 66 × 16.5 × 12 | NOYITO manual: "66mm x 16.5mm x 12mm" | maker value |
| PWR-20 WAGO 221-412 | 18.6 × 13.2 × 8.4 | WAGO data sheet [P47] | maker value (maker STEP also available) |

If a part measures more than 1 mm off, change its constant in `tools/cad/parts.py` (`JACK`, `ESTOP_BOX`) and the model in
`tools/cad/bought.py`, then `make parts cad` (the clash check must stay at 0).

## Results

(fill in)
