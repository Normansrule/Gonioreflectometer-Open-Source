# Parts list (working copy)

Your decisions on every part I suggested. **Edit this file** (on GitHub: open it → ✏️ → *Commit changes*); everything else follows: `bom.csv`, budget, checklists (`make`, or the *parts-sync* action on GitHub within a minute).

**How to edit a line**

- Tick `[x]` = you agree; untick = back to `suggested`.
- Or change the word after `status:` to one of: `suggested` · `agreed` · `ordered` · `have` · `swap` (you want another part: say which in `note:`) · `skip` (not using it). For printed parts, `have` = printed.
- `paid:` what you really paid, shipping included (e.g. `paid: 27.40`). `note:` anything.
- Only the `- [ ]` line, `note:` and `paid:` are read; the picture, *Must meet* and *why* lines are rewritten each time. New parts: `python tools/new.py part …`.
- **Must meet** = what any substitute has to match (rating, size, focal length, …), so you can buy elsewhere safely. Pictures are drawings of the kind of part; the buy link shows the real product.

<!-- parts-summary -->
| Status | Parts | Core USD | Optional USD | Tools USD |
|---|---:|---:|---:|---:|
| suggested | 96 | $576.06 | $408.64 | $417.80 |
| agreed | 0 | $0.00 | $0.00 | $0.00 |
| ordered | 0 | $0.00 | $0.00 | $0.00 |
| have | 0 | $0.00 | $0.00 | $0.00 |
| swap | 0 | $0.00 | $0.00 | $0.00 |
| skip | 0 | $0.00 | $0.00 | $0.00 |
| **Still to buy** | 72 | **$576.06** | **$0.00** | **$417.80** |
| Paid so far | | $0.00 | | |
| Plan: every core part bought (cap $630) | | $576.06 | | |

Still to buy = core parts not `ordered` / `have` / `swap` / `skip`, plus optional parts you `agreed` to. Tools are bought once and kept: they have their own total and are not in the machine cap.

## 00 · Plan

0/11 decided · still to buy $31.98 · [bom.csv](phases/00-plan/bom.csv) · [checklist](phases/00-plan/README.md)

- [ ] **TLS-01** Enclosed FDM 3D printer for ABS (Elegoo Centauri 2) — 1 × $279.00 = $279.00 · tool · [buy at amazon.com](https://www.amazon.com/dp/B0GZYZY956) · status: suggested
  - <img src="docs/assets/parts/icon-printer.svg" width="64" height="64" alt="TLS-01"> **Qty 1** · **Must meet:** Enclosed FDM printer, hot end ≥ 260 °C, heated bed ≥ 100 °C, build volume ≥ 220 × 220 × 200 mm (the tilt yoke is 175 mm tall)
  - *why:* Every printed part (ABS needs an enclosure: no warping, steady chamber heat) · Enclosed CoreXY, 350 °C nozzle, 256 mm cube. The Centauri Carbon listing (B0FDQP54X8) only had used units. Check the bed reaches 100 °C for ABS.
  - note:
  - paid:
- [ ] **TLS-02** Screwdriver set (Phillips #1/#2 + flat 2–3 mm) — 1 × $9.99 = $9.99 · tool · [buy at amazon.com](https://www.amazon.com/dp/B07RFD9JWZ) · status: suggested
  - <img src="docs/assets/parts/icon-screwdriver.svg" width="64" height="64" alt="TLS-02"> **Qty 1** · **Must meet:** Phillips #2 (wood screws), flat 2–3 mm (screw terminals)
  - *why:* Wood screws, terminal screws
  - note:
  - paid:
- [ ] **TLS-03** Hex keys 1.5 / 2 / 2.5 / 3 / 4 mm — 1 × $9.99 = $9.99 · tool · [buy at amazon.com](https://www.amazon.com/dp/B0CJBRYQF3) · status: suggested
  - <img src="docs/assets/parts/icon-hexkey.svg" width="64" height="64" alt="TLS-03"> **Qty 1** · **Must meet:** Metric hex keys 1.5–4 mm (often in the FRM-06 kit)
  - *why:* Socket screws, grub screws, pulleys
  - note:
  - paid:
- [ ] **TLS-04** Wire stripper / cutter 10–24 AWG — 1 × $10.49 = $10.49 · tool · [buy at amazon.com](https://www.amazon.com/dp/B07TS6KCXD) · status: suggested
  - <img src="docs/assets/parts/icon-stripper.svg" width="64" height="64" alt="TLS-04"> **Qty 1** · **Must meet:** Stripper for 10–24 AWG with a cutter (self-adjusting is easiest)
  - *why:* Strip 11 mm for lever connectors; cut jumpers and belt
  - note:
  - paid:
- [ ] **TLS-05** Multimeter with temperature probe — 1 × $34.99 = $34.99 · tool · [buy at amazon.com](https://www.amazon.com/dp/B071JL6LLL) · status: suggested
  - <img src="docs/assets/parts/icon-meter.svg" width="64" height="64" alt="TLS-05"> **Qty 1** · **Must meet:** Digital multimeter: DC V, Ω, continuity beep, diode; thermocouple probe (°C)
  - *why:* Every electrical check (T1–T9) and the heat checks · Check a K-type probe is in the box.
  - note:
  - paid:
- [ ] **TLS-06** Digital calipers 150 mm — 1 × $14.59 = $14.59 · tool · [buy at amazon.com](https://www.amazon.com/dp/B0D2386QN9) · status: suggested
  - <img src="docs/assets/parts/icon-caliper.svg" width="64" height="64" alt="TLS-06"> **Qty 1** · **Must meet:** 150 mm (6 in) digital calipers, 0.01 mm display
  - *why:* Print fit, tolerance coupon, positions · Check 0.01 mm resolution on the listing.
  - note:
  - paid:
- [ ] **TLS-07** Tape measure 3 m (metric) + phone level app — 1 × $1.48 = $1.48 · tool · [buy at amazon.com](https://www.amazon.com/dp/B0BRFTX359) · status: suggested
  - <img src="docs/assets/parts/icon-ruler.svg" width="64" height="64" alt="TLS-07"> **Qty 1** · **Must meet:** Metric tape ≥ 1 m; any phone level app (replaces a bubble level and set square)
  - *why:* Camera distance, level checks
  - note:
  - paid:
- [ ] **TLS-08** Paper printing at 100 % (print shop or library) — 1 × $5.00 = $5.00 · tool · status: suggested
  - <img src="docs/assets/parts/icon-paper.svg" width="64" height="64" alt="TLS-08"> **Qty 1** · **Must meet:** Prints at 100 % scale (or use a print shop)
  - *why:* Placement template, ChArUco boards, focus grid · A service, not a store item. Placement template (4 tiles), ChArUco boards, focus grid.
  - note:
  - paid:
- [ ] **TLS-09** CA glue, double-sided tape, utility knife, 400-grit sandpaper — 1 × $29.28 = $29.28 · tool · [buy at amazon.com](https://www.amazon.com/dp/B00I4CWHD4) · status: suggested
  - <img src="docs/assets/parts/icon-tape.svg" width="64" height="64" alt="TLS-09"> **Qty 1** · **Must meet:** Cyanoacrylate (super) glue; double-sided foam or carpet tape; snap-off utility knife with spare blades; one sheet of 400-grit wet/dry paper
  - *why:* Rim belt (M13.3), protractor scales (M12.3), labels; cut and sand the PTFE white tile (M16.3) · Four listings: https://www.amazon.com/dp/B00I4CWHD4 , https://www.amazon.com/dp/B0D8PMVRKD , https://www.amazon.com/dp/B07PNG8ZSG , https://www.amazon.com/dp/B00004Z4BE
  - note:
  - paid:
- [ ] **TLS-10** 13 mm spanner (or an adjustable wrench) — 1 × $7.00 = $7.00 · tool · [buy at amazon.com](https://www.amazon.com/dp/B00Q01OBLC) · status: suggested
  - <img src="docs/assets/parts/icon-hexkey.svg" width="64" height="64" alt="TLS-10"> **Qty 1** · **Must meet:** 13 mm open/ring spanner or an adjustable wrench opening ≥ 13 mm
  - *why:* M8 nuts and bolt heads: table axle, tilt stub axles
  - note:
  - paid:
- [ ] **FIL-01** ABS filament 1.75 mm, black, 1 kg (2 spools) — 2 × $15.99 = $31.98 · [buy at amazon.com](https://www.amazon.com/dp/B0DDPSXDHG) · status: suggested
  - <img src="docs/assets/parts/icon-hardware.svg" width="64" height="64" alt="FIL-01"> **Qty 2** · **Must meet:** ABS, 1.75 mm ± 0.03, black (matte if available), sealed with desiccant; ≥ 2 kg so a failed print never stops the build
  - *why:* All printed parts: core ≈ 1.0 kg (cad/PRINT.md) + reprints + optional kits; black so nothing glints near the optics · Core prints ≈ 1.0 kg (cad/PRINT.md); the second spool covers reprints and kits.
  - note:
  - paid:

## 01 · Power box

0/12 decided · still to buy $104.36 · [bom.csv](phases/01-power/bom.csv) · [checklist](phases/01-power/README.md)

- [ ] **PWR-01** AC adapter 24 V 2.5 A 60 W — 1 × $35.26 = $35.26 · [buy at digikey.com](https://www.digikey.com/en/products/detail/mean-well-usa-inc/GST60A24-P1J/7703715) · status: suggested
  - <img src="docs/assets/parts/icon-psu.svg" width="64" height="64" alt="PWR-01"> **Qty 1** · **Must meet:** 24 V DC ±5 %, ≥ 2.5 A (60 W), certified (UL/IEC 62368-1), 5.5 × 2.1 mm centre-positive plug
  - *why:* Single certified wall supply · Digi-Key qty-1 price via Octopart. Level VI, UL62368-1, 90.5 %. Plug 5.5/2.1 mm.
  - note:
  - paid:
- [ ] **PWR-02** IEC C13 mains cord — 1 × $3.14 = $3.14 · [buy at amazon.com](https://www.amazon.com/dp/B07F7NLCL8) · status: suggested
  - <img src="docs/assets/parts/icon-cable.svg" width="64" height="64" alt="PWR-02"> **Qty 1** · **Must meet:** IEC C13 to your wall plug (US: NEMA 5-15P), 18 AWG, ≥ 10 A
  - *why:* Adapter has a C14 inlet; cord sold separately
  - note:
  - paid:
- [ ] **PWR-03** DC jack to screw-terminal adapter 2.1 mm — 1 × $2.00 = $2.00 · [buy at adafruit.com](https://www.adafruit.com/product/368) · status: suggested
  - <img src="docs/assets/parts/icon-jack.svg" width="64" height="64" alt="PWR-03"> **Qty 1** · **Must meet:** Female 5.5 × 2.1 mm barrel jack with a 2-screw terminal block marked + / −, centre-positive, ≥ 3 A
  - *why:* Adapter plug in; wires clamp under screws (no solder) · Held in the box-wall slot by the lid. Tighten each screw on twisted, stripped wire.
  - note:
  - paid:
- [ ] **PWR-04** Inline 5 x 20 mm fuse holder — 1 × $4.00 = $4.00 · [buy at digikey.com](https://www.digikey.com/en/products/detail/littelfuse-inc/01500274Z/29453) · status: suggested
  - <img src="docs/assets/parts/icon-fuse.svg" width="64" height="64" alt="PWR-04"> **Qty 1** · **Must meet:** Inline holder for 5 × 20 mm fuses, ≥ 5 A, with 18 AWG wire leads (no solder: leads go into screw terminals)
  - *why:* Input fuse holder
  - note:
  - paid:
- [ ] **PWR-05** Fuse 3.15 A time-lag 5 x 20 mm — 2 × $1.56 = $3.12 · [buy at digikey.com](https://www.digikey.com/en/products/detail/littelfuse-inc/02183-15MXP/777620) · status: suggested
  - <img src="docs/assets/parts/icon-fuse.svg" width="64" height="64" alt="PWR-05"> **Qty 2** · **Must meet:** 5 × 20 mm glass fuse, 3.15 A, time-lag (T / slow-blow), 250 V
  - *why:* Input over-current protection · 0218 series = time-lag.
  - note:
  - paid:
- [ ] **PWR-10** Optocoupler LTV-817 / PC817 (DIP-4) — 1 × $0.39 = $0.39 · [buy at digikey.com](https://www.digikey.com/en/products/detail/liteon/LTV-817/385836) · status: suggested
  - <img src="docs/assets/parts/icon-chip.svg" width="64" height="64" alt="PWR-10"> **Qty 1** · **Must meet:** Optocoupler, DIP-4 (fits a breadboard), current-transfer ratio ≥ 50 % at 2 mA (PC817)
  - *why:* Isolated e-stop sense (plugs into the breadboard) · The Sharp PC817 is out of stock at Digi-Key; LTV-817 is pin- and spec-compatible.
  - note:
  - paid:
- [ ] **PWR-11** Resistors 10k (2) — 2 × $0.10 = $0.20 · [buy at digikey.com](https://www.digikey.com/en/products/detail/stackpole-electronics-inc/CF14JT10K0/1741265) · status: suggested
  - <img src="docs/assets/parts/icon-resistor.svg" width="64" height="64" alt="PWR-11"> **Qty 2** · **Must meet:** 10 kΩ, ¼ W, ≤ 5 %, axial (legs push into the breadboard)
  - *why:* Opto LED current (2.3 mA at 24 V); spare
  - note:
  - paid:
- [ ] **PWR-13** Emergency stop 22 mm latching, 1 NC — 1 × $30.87 = $30.87 · [buy at digikey.com](https://www.digikey.com/en/products/detail/apem-inc/YW1B-V4E01R/15216547) · status: suggested
  - <img src="docs/assets/parts/icon-estop.svg" width="64" height="64" alt="PWR-13"> **Qty 1** · **Must meet:** 22 mm panel emergency stop, latching (twist to release), ≥ 1 normally-closed contact rated ≥ 24 V DC / 3 A, screw terminals (no solder)
  - *why:* Cuts 24 V to the motion board · Digi-Key qty-1 price via Octopart. Screw terminals: 2 stripped wires may share one screw (twist them together). Also the machine's off switch.
  - note:
  - paid:
- [ ] **PWR-15** 18 AWG silicone wire red/black, 1 m pair — 1 × $7.98 = $7.98 · [buy at amazon.com](https://www.amazon.com/dp/B01708AYYQ) · status: suggested
  - <img src="docs/assets/parts/icon-wire.svg" width="64" height="64" alt="PWR-15"> **Qty 1** · **Must meet:** 18 AWG stranded silicone wire, red + black (≥ 5 A)
  - *why:* Power wiring
  - note:
  - paid:
- [ ] **PWR-19** Half-size breadboard (400 points) — 1 × $4.95 = $4.95 · [buy at adafruit.com](https://www.adafruit.com/product/64) · status: suggested
  - <img src="docs/assets/parts/icon-breadboard.svg" width="64" height="64" alt="PWR-19"> **Qty 1** · **Must meet:** Solderless breadboard, ≥ 400 tie points, 2.54 mm, adhesive back
  - *why:* E-stop sense (PC817 + 10k) and lamp driver without solder · Stuck in the controller case. Low-current parts only (≤ 0.5 A); the 24 V motor feed never goes through it.
  - note:
  - paid:
- [ ] **PWR-20** Lever wire connectors, WAGO 221 assortment (12) — 1 × $12.45 = $12.45 · [buy at amazon.com](https://www.amazon.com/dp/B0CJ5QF4Z2) · status: suggested
  - <img src="docs/assets/parts/icon-lever.svg" width="64" height="64" alt="PWR-20"> **Qty 1** · **Must meet:** Lever splicing connectors for 24–12 AWG stranded and solid wire, 2/3/5-way, ≥ 20 A (WAGO 221-412/413/415)
  - *why:* Every bare-wire join: no solder, no crimp, no heat-shrink
  - note:
  - paid:
- [ ] **PWR-18** Power box + lid — print · print · status: suggested
  - <img src="docs/assets/parts/PWR-18a_power_box.png" width="64" height="64" alt="PWR-18"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/PWR-18a_power_box.step](phases/01-power/3d/PWR-18a_power_box.step)
  - *why:* Houses power parts; OG-40 mount · ~80 g ABS.
  - note:

## 02 · Controller and buttons

0/11 decided · still to buy $79.68 · [bom.csv](phases/02-controller/bom.csv) · [checklist](phases/02-controller/README.md)

- [ ] **CTL-01** FYSETC E4 (ESP32, 4x TMC2209, WiFi + Bluetooth) — 1 × $40.99 = $40.99 · [buy at amazon.com](https://www.amazon.com/dp/B0FGVCX2HN) · status: suggested
  - <img src="docs/assets/parts/icon-board.svg" width="64" height="64" alt="CTL-01"> **Qty 1** · **Must meet:** ESP32 board supported by FluidNC with 4 TMC2209 drivers on UART, 12–24 V input, WiFi + Bluetooth (FYSETC E4)
  - *why:* Motion controller running FluidNC; USB / WiFi / BT to the laptop · Sold by a third-party seller, not FYSETC. Alternative: https://www.amazon.com/dp/B0HD7N6LL1 ($55.74). USB-B port (see CTL-03).
  - note:
  - paid:
- [ ] **CTL-02** Raspberry Pi Pico H (headers soldered) — 1 × $5.00 = $5.00 · [buy at digikey.com](https://www.digikey.com/en/products/detail/raspberry-pi/SC0917/16608257) · status: suggested
  - <img src="docs/assets/parts/icon-board.svg" width="64" height="64" alt="CTL-02"> **Qty 1** · **Must meet:** RP2040 Raspberry Pi Pico with factory-soldered 2.54 mm headers (Pico H; Pico WH also fine), runs MicroPython
  - *why:* Buttons, e-stop sense, LED bank · Adafruit 5525 is out of stock.
  - note:
  - paid:
- [ ] **CTL-03** USB A-to-B cable for the E4 — 1 × $3.95 = $3.95 · [buy at adafruit.com](https://www.adafruit.com/product/62) · status: suggested
  - <img src="docs/assets/parts/icon-cable.svg" width="64" height="64" alt="CTL-03"> **Qty 1** · **Must meet:** USB data cable (not charge-only) with the E4's connector, ≤ 2 m
  - *why:* Laptop to E4 (or use WiFi/BT) · The E4 has a USB-B socket. Adafruit 62 is out of stock: any USB A-B printer cable. Check your E4's USB port: USB-C → this cable; micro-USB → a second CTL-04.
  - note:
  - paid:
- [ ] **CTL-04** USB-A to micro-B data cable 1 m — 1 × $2.95 = $2.95 · [buy at adafruit.com](https://www.adafruit.com/product/592) · status: suggested
  - <img src="docs/assets/parts/icon-cable.svg" width="64" height="64" alt="CTL-04"> **Qty 1** · **Must meet:** USB-A to micro-B data cable (not charge-only), ≤ 2 m
  - *why:* Laptop to Pico · Consumable: set `have` if it's in your drawer.
  - note:
  - paid:
- [ ] **CTL-05** Membrane keypad 1 x 4 — 2 × $2.95 = $5.90 · [buy at adafruit.com](https://www.adafruit.com/product/1332) · status: suggested
  - <img src="docs/assets/parts/icon-keypad.svg" width="64" height="64" alt="CTL-05"> **Qty 2** · **Must meet:** 1 × 4 membrane keypad, 5-wire tail (common + 4 keys) ending in a 2.54 mm female connector, adhesive back
  - *why:* HOME START STOP LIGHT (pad A); NEXT, PAUSE (pad B) · Sticks onto the printed panel. Common → GND, keys → Pico GP2–GP6 with male–female jumpers.
  - note:
  - paid:
- [ ] **CTL-06** JST-XH pre-crimped lead kit — 1 × $10.99 = $10.99 · [buy at amazon.com](https://www.amazon.com/dp/B0F8HMQRRN) · status: suggested
  - <img src="docs/assets/parts/icon-cable.svg" width="64" height="64" alt="CTL-06"> **Qty 1** · **Must meet:** JST-XH 2.54 mm leads crimped on BOTH ends, ≥ 50 cm, with 2- and 3-pin housings (an XH housing also plugs onto a 2.54 mm pin header)
  - *why:* Keyed connectors
  - note:
  - paid:
- [ ] **CTL-07** Jumper wires male-female 150 mm (20) — 2 × $1.95 = $3.90 · [buy at adafruit.com](https://www.adafruit.com/product/1954) · status: suggested
  - <img src="docs/assets/parts/icon-jumper.svg" width="64" height="64" alt="CTL-07"> **Qty 2** · **Must meet:** Male–female 2.54 mm jumper wires, ≥ 150 mm, ≥ 20
  - *why:* Keypads, opto and breadboard to the Pico; cut in half for pin-to-wire leads · 2 packs = 40: keypads 7, opto + ground link 3, lamp lead 10 (daisy-chained), sense/HE0/3V3 leads 4, spares. Cut one in half = pin socket on one end, bare wire on the other.
  - note:
  - paid:
- [ ] **CTL-08** Fan 40 mm 24 V — 1 × $7.99 = $7.99 · optional · [buy at amazon.com](https://www.amazon.com/dp/B09F9JT3BY) · status: suggested
  - <img src="docs/assets/parts/icon-fan.svg" width="64" height="64" alt="CTL-08"> **Qty 1** · **Must meet:** 40 mm fan, 24 V DC, 2-wire
  - *why:* Only if T6 driver temperature fails
  - note:
  - paid:
- [ ] **CTL-11** Stepper cables 1 m, PH2.0 6-pin to XH2.54 4-pin (4-pack) — 1 × $6.00 = $6.00 · [buy at amazon.com](https://www.amazon.com/dp/B099214RPZ) · status: suggested
  - <img src="docs/assets/parts/icon-cable.svg" width="64" height="64" alt="CTL-11"> **Qty 1** · **Must meet:** 1 m, 4-wire, PH2.0 6-pin (motor end) to XH2.54 4-pin (E4 end); check the motor end matches your motor's socket
  - *why:* Motors into the E4 sockets without crimping
  - note:
  - paid:
- [ ] **CTL-09** Laptop (Windows or Linux) — you supply · status: suggested
  - <img src="docs/assets/parts/icon-laptop.svg" width="64" height="64" alt="CTL-09"> **Qty 1** · **Must meet:** Laptop with a free USB port per camera; Windows 10+ (camera via Windows Python) or Linux
  - *why:* Control and processing · The laptop you already run Ubuntu (WSL) on; the only thing assumed owned.
  - note:
- [ ] **CTL-10** Controller case + button panel — print · print · status: suggested
  - <img src="docs/assets/parts/CTL-10a_button_panel.png" width="64" height="64" alt="CTL-10"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/CTL-10a_button_panel.step](phases/02-controller/3d/CTL-10a_button_panel.step)
  - *why:* Holds E4 and Pico, panel labels
  - note:

## 03 · Frame

0/7 decided · still to buy $71.96 · [bom.csv](phases/03-frame/bom.csv) · [checklist](phases/03-frame/README.md)

- [ ] **FRM-01** Baltic birch plywood 1/2 in, 24 x 24 in — 1 × $20.00 = $20.00 · [buy at amazon.com](https://www.amazon.com/dp/B0D5YR61FW) · status: suggested
  - <img src="docs/assets/parts/icon-plywood.svg" width="64" height="64" alt="FRM-01"> **Qty 1** · **Must meet:** 12 mm (½ in) flat plywood, sold pre-cut at 2 × 2 ft (≈ 610 × 610 mm): used as bought, no saw
  - *why:* Base plate
  - note:
  - paid:
- [ ] **FRM-02** 2020 V-slot 500 mm (4-pack) — 1 × $22.39 = $22.39 · [buy at amazon.com](https://www.amazon.com/dp/B0BBR6RPZR) · status: suggested
  - <img src="docs/assets/parts/icon-extrusion.svg" width="64" height="64" alt="FRM-02"> **Qty 1** · **Must meet:** 2020 aluminium extrusion, 6 mm slot (V-slot or T-slot), 500 mm, square-cut ends
  - *why:* Outrigger, scan-camera post, light-arm upright, horizontal light arm
  - note:
  - paid:
- [ ] **FRM-03** M5 T-nuts for 2020, 50 drop-in + 50 sliding — 1 × $5.99 = $5.99 · [buy at amazon.com](https://www.amazon.com/dp/B0GC71GBGJ) · status: suggested
  - <img src="docs/assets/parts/icon-hardware.svg" width="64" height="64" alt="FRM-03"> **Qty 1** · **Must meet:** M5 drop-in T-nuts for 2020 / 6 mm slot
  - *why:* Brackets on extrusion · 12 used.
  - note:
  - paid:
- [ ] **FRM-06** Socket screw kit M2–M5, 8/10/16/20 mm, with nuts — 1 × $9.99 = $9.99 · [buy at amazon.com](https://www.amazon.com/dp/B0DBLCHK48) · status: suggested
  - <img src="docs/assets/parts/icon-hardware.svg" width="64" height="64" alt="FRM-06"> **Qty 1** · **Must meet:** Socket-head M3/M4/M5 screws 8–30 mm with nuts and washers; hex keys 2.5 / 3 / 4 mm included or owned
  - *why:* General fastening · Has M3 x 8/10, M4 x 16 (use for the rim: 9 mm rim + 3 mm plate + nut), M5 x 10. Also covers TBL-06, TLT-06, SPN-06.
  - note:
  - paid:
- [ ] **FRM-08** 608-2RS bearings (10) — 1 × $4.99 = $4.99 · [buy at amazon.com](https://www.amazon.com/dp/B0CX8CDL7D) · status: suggested
  - <img src="docs/assets/parts/icon-bearing.svg" width="64" height="64" alt="FRM-08"> **Qty 1** · **Must meet:** 608-2RS ball bearings, 8 × 22 × 7 mm, sealed
  - *why:* Table 2, tilt 2, spares 6
  - note:
  - paid:
- [ ] **FRM-12** Wood screws #8 x 5/8 in, Type 17 point (100) — 1 × $8.60 = $8.60 · [buy at amazon.com](https://www.amazon.com/dp/B07542157N) · status: suggested
  - <img src="docs/assets/parts/icon-woodscrew.svg" width="64" height="64" alt="FRM-12"> **Qty 1** · **Must meet:** #8 (4.2 mm) × 5/8 in (16 mm) pan-head wood screws with a Type 17 self-drilling point (start without a pilot hole), Phillips or combo drive
  - *why:* Every printed part, the lazy Susan and the feet onto the plywood: no drilling
  - note:
  - paid:
- [ ] **FRM-09** OG-40 adapter, feet, 2020 saddles, scan-post socket, camera pillar, end foot, protractor scales — print · print · status: suggested
  - <img src="docs/assets/parts/FRM-09a_og40_adapter.png" width="64" height="64" alt="FRM-09"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/FRM-09a_og40_adapter.step](phases/03-frame/3d/FRM-09a_og40_adapter.step)
  - *why:* Printed frame parts · Everything screws onto the plywood with FRM-12 wood screws: no drilling. Protractors for alignment [R1].
  - note:

## 04 · Light arm (M4)

0/8 decided · still to buy $74.54 · [bom.csv](phases/04-light-arm/bom.csv) · [checklist](phases/04-light-arm/README.md)

- [ ] **LAR-01** 12 in lazy Susan bearing — 1 × $13.99 = $13.99 · [buy at amazon.com](https://www.amazon.com/dp/B0CQXFVDN7) · status: suggested
  - <img src="docs/assets/parts/icon-turntable.svg" width="64" height="64" alt="LAR-01"> **Qty 1** · **Must meet:** 12 in (≈ 305 mm) lazy-Susan ball bearing, flat, ≥ 50 kg rating, no wobble you can feel
  - *why:* M4: light arm rotates around the sample · Measure it before printing the rim (M13.1); the table motor needs an inner opening ≥ 150 mm.
  - note:
  - paid:
- [ ] **LAR-02** NEMA 17 stepper 59 Ncm 2 A (3-pack: M4, M3, M2) — 1 × $32.99 = $32.99 · [buy at amazon.com](https://www.amazon.com/dp/B00Y2HJE22) · status: suggested
  - <img src="docs/assets/parts/icon-motor.svg" width="64" height="64" alt="LAR-02"> **Qty 1** · **Must meet:** NEMA 17, 1.8°/step, bipolar 4-wire, ≥ 40 N·cm holding, ≤ 2.0 A/phase (driver runs 0.8 A), 5 mm D-shaft
  - *why:* M4 drive · 3-pack covers LAR-02, TBL-01, TLT-01. The included cables end in a 4-pin 0.1 in housing: use the CTL-11 cables to reach the E4's XH sockets.
  - note:
  - paid:
- [ ] **LAR-03** GT2 6 mm open belt (5 m) — 1 × $7.59 = $7.59 · [buy at amazon.com](https://www.amazon.com/dp/B0BSMNZ53S) · status: suggested
  - <img src="docs/assets/parts/icon-belt.svg" width="64" height="64" alt="LAR-03"> **Qty 1** · **Must meet:** GT2 (2 mm pitch) open belt, 6 mm wide, fibre-reinforced, ≥ 1 m per ring (2 m bought)
  - *why:* Teeth-out around the ring rim (~24:1)
  - note:
  - paid:
- [ ] **LAR-04** GT2 20T pulley 5 mm bore (5-pack) — 1 × $3.99 = $3.99 · [buy at amazon.com](https://www.amazon.com/dp/B0DJQC42DT) · status: suggested
  - <img src="docs/assets/parts/icon-pulley.svg" width="64" height="64" alt="LAR-04"> **Qty 1** · **Must meet:** GT2 (2 mm pitch) 20-tooth, 5 mm bore, for 6 mm belt, 2 set screws
  - *why:* M4 motor pulley · 5-pack covers LAR-04, TBL-03, TLT-03.
  - note:
  - paid:
- [ ] **LAR-05** Optical endstop module, slot type (6-pack) — 1 × $8.99 = $8.99 · [buy at amazon.com](https://www.amazon.com/dp/B0719K9Z9R) · status: suggested
  - <img src="docs/assets/parts/icon-endstop.svg" width="64" height="64" alt="LAR-05"> **Qty 1** · **Must meet:** Slotted optical switch module (TCST2103, 3.1 mm slot), 3.3–5 V supply, digital output the E4 home input reads
  - *why:* M4 home · Covers LAR-05, TBL-04, TLT-04, SPN-04. Check the slot is ≥ 3 mm (the flag is 1.5 mm).
  - note:
  - paid:
- [ ] **LAR-06** Roller-lever limit switch, screw terminals (2) — 1 × $6.99 = $6.99 · [buy at amazon.com](https://www.amazon.com/dp/B09TDBH593) · status: suggested
  - <img src="docs/assets/parts/icon-switch.svg" width="64" height="64" alt="LAR-06"> **Qty 1** · **Must meet:** Roller-lever limit switch with screw terminals (ME-8108 style), normally-closed contact ≥ 3 A at 24 V DC
  - *why:* Over-travel switches in the e-stop loop [R1]
  - note:
  - paid:
- [ ] **LAR-09** Laser module class 2 (650 nm, < 1 mW); mirror = one CAL-02 tile — 1 × $15.99 = $15.99 · tool · [buy at amazon.com](https://www.amazon.com/dp/B00ZR80S9S) · status: suggested
  - <img src="docs/assets/parts/icon-laser.svg" width="64" height="64" alt="LAR-09"> **Qty 1** · **Must meet:** Red laser pointer, class 2 (< 1 mW), plus a ~25 mm flat mirror
  - *why:* Repeatability test: mirror on the moving part, spot on a wall 2 m away (0.1 deg = 7 mm) · Bare module, 2.6–6 V: run it from the E4's 5 V pins with two jumper wires. Mirror: one CAL-02 tile.
  - note:
  - paid:
- [ ] **LAR-08** Belt rim segments, arm segment, M4 motor mount, cross clamp — print · print · status: suggested
  - <img src="docs/assets/parts/LAR-08a_rim_segment.png" width="64" height="64" alt="LAR-08"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/LAR-08a_rim_segment.step](phases/04-light-arm/3d/LAR-08a_rim_segment.step)
  - *why:* Printed M4 parts · 7 rim segments + the arm segment (8th, with the upright socket) bolt to the lazy-Susan top plate with M4 x 16 + nuts (FRM-06) where a slot meets a plate hole, CA glue elsewhere; no idlers: the motor pinion meshes with the rim belt.
  - note:

## 05 · Table (M3)

0/7 decided · still to buy $23.56 · [bom.csv](phases/05-table/bom.csv) · [checklist](phases/05-table/README.md)

- [ ] **TBL-01** NEMA 17 stepper 59 Ncm 2 A — $0 (in another row) · [buy at amazon.com](https://www.amazon.com/dp/B00Y2HJE22) · status: suggested
  - <img src="docs/assets/parts/icon-motor.svg" width="64" height="64" alt="TBL-01"> **Qty 1** · **Must meet:** NEMA 17, 1.8°/step, bipolar 4-wire, ≥ 40 N·cm holding, ≤ 2.0 A/phase (driver runs 0.8 A), 5 mm D-shaft
  - *why:* M3 (table rotation, vertical axis) drive · In the LAR-02 3-pack. Same motor on every axis.
  - note:
  - paid:
- [ ] **TBL-02** GT2 6 mm closed belt 232 mm — 1 × $8.19 = $8.19 · [buy at amazon.com](https://www.amazon.com/dp/B0FRFGBS6J) · status: suggested
  - <img src="docs/assets/parts/icon-belt.svg" width="64" height="64" alt="TBL-02"> **Qty 1** · **Must meet:** GT2 (2 mm pitch) closed loop, 6 mm wide, 232 mm (116 teeth): puts the motor 49.4 mm from the table axis, inside the lazy Susan opening
  - *why:* 20T to printed 100T, 5:1
  - note:
  - paid:
- [ ] **TBL-03** GT2 20T pulley 5 mm bore — $0 (in another row) · [buy at amazon.com](https://www.amazon.com/dp/B0DJQC42DT) · status: suggested
  - <img src="docs/assets/parts/icon-pulley.svg" width="64" height="64" alt="TBL-03"> **Qty 1** · **Must meet:** GT2 (2 mm pitch) 20-tooth, 5 mm bore, for 6 mm belt, 2 set screws
  - *why:* Motor pulley · In the LAR-04 5-pack.
  - note:
  - paid:
- [ ] **TBL-04** Optical endstop module, slot type (from the LAR-05 6-pack) — $0 (in another row) · [buy at amazon.com](https://www.amazon.com/dp/B0719K9Z9R) · status: suggested
  - <img src="docs/assets/parts/icon-endstop.svg" width="64" height="64" alt="TBL-04"> **Qty 1** · **Must meet:** Slotted optical switch module (TCST2103, 3.1 mm slot), 3.3–5 V supply, digital output the E4 home input reads
  - *why:* Home · In the LAR-05 6-pack.
  - note:
  - paid:
- [ ] **TBL-05** M8 x 75 hex bolt, partial thread + M8 nut (fixed table axle) — 1 × $15.37 = $15.37 · [buy at amazon.com](https://www.amazon.com/dp/B0D83HW8ZM) · status: suggested
  - <img src="docs/assets/parts/icon-hardware.svg" width="64" height="64" alt="TBL-05"> **Qty 1** · **Must meet:** M8-1.25 × 75 mm hex bolt with ≥ 30 mm smooth shank (DIN 931, partial thread), grade 8.8, + M8 hex nut
  - *why:* Fixed axle: head locked in the post, drum turns on two 608s around it · Bolts $9.38 + nuts $5.99 (https://www.amazon.com/dp/B0CZQNB22Q); nuts also cover TLT-05.
  - note:
  - paid:
- [ ] **TBL-06** Axis fasteners (M3/M5 set) — $0 (in another row) · [buy at amazon.com](https://www.amazon.com/dp/B0DBLCHK48) · status: suggested
  - <img src="docs/assets/parts/icon-hardware.svg" width="64" height="64" alt="TBL-06"> **Qty 1** · **Must meet:** M3/M5 socket screws 8–30 mm, nuts and washers (motor mount, pulley, clamp)
  - *why:* Motor mount, pulley, clamp · From the FRM-06 kit.
  - note:
  - paid:
- [ ] **TBL-07** Printed table parts — print · print · status: suggested
  - <img src="docs/assets/parts/TBL-07a_table_drum.png" width="64" height="64" alt="TBL-07"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/TBL-07a_table_drum.step](phases/05-table/3d/TBL-07a_table_drum.step)
  - *why:* Post, drum (100T teeth + 608 seats + OG-40 top), motor bracket, flags, spacers
  - note:

## 06 · Camera and light

0/10 decided · still to buy $118.20 · [bom.csv](phases/06-camera-light/bom.csv) · [checklist](phases/06-camera-light/README.md)

- [ ] **CAM-01** USB camera 12 MP IMX477, M12 mount (UVC) — 1 × $59.99 = $59.99 · [buy at amazon.com](https://www.amazon.com/dp/B0C1G73QZD) · status: suggested
  - <img src="docs/assets/parts/icon-camera.svg" width="64" height="64" alt="CAM-01"> **Qty 1** · **Must meet:** USB Video Class (UVC) camera, Sony IMX477 12.3 MP, 1.55 µm pixels, M12 × 0.5 lens mount, manual exposure / gain / white balance, ≥ 3840 × 3032 output, IR-cut filter for true colour
  - *why:* Fixed measurement camera on the laptop · Arducam's B0433-family 12 MP USB board.
  - note:
  - paid:
- [ ] **CAM-02** M12 lens 16 mm, ≥ 1/2 in format, low distortion — 1 × $30.11 = $30.11 · [buy at amazon.com](https://www.amazon.com/dp/B0HJWVFD7R) · status: suggested
  - <img src="docs/assets/parts/icon-lens.svg" width="64" height="64" alt="CAM-02"> **Qty 1** · **Must meet:** M12 × 0.5 lens, focal length 16 mm (±0.5) → 124 × 98 mm field and 32 µm per pixel at 350 mm, 236 × 186 mm at 650 mm; covers a ≥ 1/2.3 in sensor; F2.0 or slower (used at f/8 via the 2.0 mm stop: 22.6 mm depth of field at 350 mm, 117 mm at 650 mm); distortion < 1 %
  - *why:* Lens
  - note:
  - paid:
- [ ] **LSR-06** Solderless COB holder 13.5 mm (TE LUMAWISE Z35) — 1 × $3.50 = $3.50 · [buy at digikey.com](https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/2213678-5/6174915) · status: suggested
  - <img src="docs/assets/parts/icon-holder.svg" width="64" height="64" alt="LSR-06"> **Qty 1** · **Must meet:** Solderless holder for a 13.5 × 13.5 mm COB (Citizen CLU700 family), poke-in terminals for 18–20 AWG wire, rated ≥ 0.5 A and ≥ 24 V
  - *why:* Holds and connects the COB without solder · Ø35 × 3.6 mm, 3 A / 60 V DC, poke-in for 18–20 AWG solid or stranded [L23]. No screws: the lamp body's round seat centres it and the cap clamps heatsink + holder. Leads: 2 × 15 cm of PWR-15 18 AWG.
  - note:
  - paid:
- [ ] **CAM-07** M2.5 x 8 mm screws (100-pack) — 1 × $6.29 = $6.29 · [buy at amazon.com](https://www.amazon.com/dp/B07YS6D2GT) · status: suggested
  - <img src="docs/assets/parts/icon-hardware.svg" width="64" height="64" alt="CAM-07"> **Qty 1** · **Must meet:** M2.5-0.45 × 8 mm pan-head machine screws
  - *why:* Camera board onto its plate (self-tap into 2.2 mm holes) · Covers CAM-08.
  - note:
  - paid:
- [ ] **LSR-01** COB LED CRI 97, 12 V, 13.5 mm (Citizen CLU7A3) — 1 × $5.91 = $5.91 · [buy at digikey.com](https://www.digikey.com/en/products/detail/citizen/CLU7A3-0403E1-303H7X5/17053751) · status: suggested
  - <img src="docs/assets/parts/icon-led.svg" width="64" height="64" alt="LSR-01"> **Qty 1** · **Must meet:** White chip-on-board LED, Colour Rendering Index (CRI) ≥ 90, 3000–5000 K, forward voltage ≤ 18 V at 350 mA (the driver needs headroom under 24 V), rated ≥ 350 mA, ≤ 6 mm light-emitting surface, 13.5 × 13.5 mm board (fits LSR-06)
  - *why:* White measurement light · Datasheet: 12.2 V typ at 525 mA, max 900 mA, case ≤ 120 °C, Rj-c 3.4 °C/W; ≈ 4 W at 350 mA. Cree CXA13 COBs dropped: every CXA13 holder is obsolete [L21].
  - note:
  - paid:
- [ ] **LSR-02** Constant-current driver 350 mA — 1 × $5.41 = $5.41 · [buy at digikey.com](https://www.digikey.com/en/products/detail/mean-well-usa-inc/NLDD-350H/13913618) · status: suggested
  - <img src="docs/assets/parts/icon-driver.svg" width="64" height="64" alt="LSR-02"> **Qty 1** · **Must meet:** Constant-current LED driver 350 mA, input range covering 24 V, output covering the LED's ≈ 12 V, no flicker (DC output); 2.54 mm-pitch pins that push into a breadboard (or a wire-lead version)
  - *why:* Drives the COB from 24 V; on/off from E4 GPIO2 MOSFET
  - note:
  - paid:
- [ ] **LSR-03** Heatsink 40 x 40 mm (from a pack) — 1 × $6.99 = $6.99 · [buy at amazon.com](https://www.amazon.com/dp/B07D4FVC61) · status: suggested
  - <img src="docs/assets/parts/icon-heatsink.svg" width="64" height="64" alt="LSR-03"> **Qty 1** · **Must meet:** Aluminium heatsink ≥ 40 × 40 × 11 mm (keeps the LED case ≤ 70 °C)
  - *why:* COB cooling · Tape covers LSR-04.
  - note:
  - paid:
- [ ] **LSR-04** Thermal adhesive pad — $0 (in another row) · [buy at amazon.com](https://www.amazon.com/dp/B07D4FVC61) · status: suggested
  - <img src="docs/assets/parts/icon-tape.svg" width="64" height="64" alt="LSR-04"> **Qty 1** · **Must meet:** Thermally conductive, electrically insulating adhesive tape or pad, ≥ 20 mm wide
  - *why:* COB to heatsink · In the LSR-03 kit.
  - note:
  - paid:
- [ ] **CAM-03** Camera L-arm, aperture stop (f/8), lens lock — print · print · status: suggested
  - <img src="docs/assets/parts/CAM-03a_aperture_stop_f8.png" width="64" height="64" alt="CAM-03"> **Qty 1** · **Must meet:** Aperture stop hole = focal length / 8 = 2.0 mm (f/8); matte black ABS so it can't glint · files: [3d/CAM-03a_aperture_stop_f8.step](phases/06-camera-light/3d/CAM-03a_aperture_stop_f8.step)
  - *why:* Fixed, adjustable camera mount · Stop = f/N = 2.0 mm.
  - note:
- [ ] **LSR-05** Lamp body + tube, back cap — print · print · status: suggested
  - <img src="docs/assets/parts/LSR-05a_lamp_tube.png" width="64" height="64" alt="LSR-05"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/LSR-05a_lamp_tube.step](phases/06-camera-light/3d/LSR-05a_lamp_tube.step)
  - *why:* Holds heatsink + COB holder, 10 mm exit aperture, polarizer slot, clamps to the horizontal 2020 arm
  - note:

## 07 · Calibrate → game material

0/12 decided · still to buy $39.78 · [bom.csv](phases/07-calibrate/bom.csv) · [checklist](phases/07-calibrate/README.md)

- [ ] **ENC-01** Blackout fabric, black (2 units) — 2 × $7.90 = $15.80 · optional · [buy at amazon.com](https://www.amazon.com/dp/B00MQADTVY) · status: suggested
  - <img src="docs/assets/parts/icon-fabric.svg" width="64" height="64" alt="ENC-01"> **Qty 2** · **Must meet:** Opaque blackout fabric, ≥ 2 yd × 54 in
  - *why:* Light-tight drape · Check the listing unit (per yard).
  - note:
  - paid:
- [ ] **ENC-02** Black felt sheet — 1 × $6.99 = $6.99 · [buy at amazon.com](https://www.amazon.com/dp/B0FXKGNV95) · status: suggested
  - <img src="docs/assets/parts/icon-fabric.svg" width="64" height="64" alt="ENC-02"> **Qty 1** · **Must meet:** Matte black felt, ≥ 9 × 12 in
  - *why:* Backdrop behind the sample
  - note:
  - paid:
- [ ] **ENC-03** Dowels 1/2 x 36 in (10) — 1 × $19.99 = $19.99 · optional · [buy at amazon.com](https://www.amazon.com/dp/B0BVGCCMZ9) · status: suggested
  - <img src="docs/assets/parts/icon-dowel.svg" width="64" height="64" alt="ENC-03"> **Qty 1** · **Must meet:** ½ in (12.7 mm) hardwood dowels (poplar is fine), 36 in, straight
  - *why:* Drape frame posts · Bamboo; 4 used.
  - note:
  - paid:
- [ ] **CAL-01** PTFE sheets 100 x 100 x 3 mm (2): white tile = 3 stacked 50 mm squares — 1 × $16.99 = $16.99 · [buy at amazon.com](https://www.amazon.com/dp/B0F83XRXTV) · status: suggested
  - <img src="docs/assets/parts/icon-plate.svg" width="64" height="64" alt="CAL-01"> **Qty 1** · **Must meet:** Virgin white PTFE; 3 stacked 3 mm squares = 9 mm (opaque, like a 3/8 in plate), ≥ 50 × 50 mm face; top sanded with 400 grit for a diffuse surface (reflectance ≈ 0.98–0.99)
  - *why:* Near-Lambertian white reference · Cut one sheet into four 50 mm squares (knife); stack 3 in the holder.
  - note:
  - paid:
- [ ] **CAL-02** Glass mirror tile ~50 mm — 1 × $11.49 = $11.49 · [buy at amazon.com](https://www.amazon.com/dp/B01H0ZU1QA) · status: suggested
  - <img src="docs/assets/parts/icon-mirror.svg" width="64" height="64" alt="CAL-02"> **Qty 1** · **Must meet:** Flat glass mirror ≈ 50 mm; front-surface preferred (no ghost reflection)
  - *why:* Geometric calibration (specular peak)
  - note:
  - paid:
- [ ] **CAL-03** Chrome steel ball 1 in G25 (2) — 1 × $9.95 = $9.95 · optional · [buy at amazon.com](https://www.amazon.com/dp/B01AX6ZRH6) · status: suggested
  - <img src="docs/assets/parts/icon-ball.svg" width="64" height="64" alt="CAL-03"> **Qty 1** · **Must meet:** Two 1 in chrome-steel balls, grade 25 or better (polished)
  - *why:* Optional check of light directions (photometric stereo); light direction already comes from M4 and the mirror test
  - note:
  - paid:
- [ ] **CAL-04** ChArUco print + picture-frame glass — 1 × $4.31 = $4.31 · [buy at amazon.com](https://www.amazon.com/dp/B000Y79K32) · status: suggested
  - <img src="docs/assets/parts/icon-chart.svg" width="64" height="64" alt="CAL-04"> **Qty 1** · **Must meet:** ChArUco board 7 × 5, 10 mm squares, 7 mm markers (DICT_4X4_50), laser-printed at 100 % on matte paper, held flat under glass
  - *why:* Intrinsics, pose, repeatability · Check it has real glass (the board must be flat). Print the ChArUco board at a shop or library.
  - note:
  - paid:
- [ ] **CAL-05** Colour target (ColorChecker Mini or similar) — 1 × $55.50 = $55.50 · optional · [buy at amazon.com](https://www.amazon.com/dp/B0973JNJCB) · status: suggested
  - <img src="docs/assets/parts/icon-chart.svg" width="64" height="64" alt="CAL-05"> **Qty 1** · **Must meet:** 24-patch colour checker with published reference values
  - *why:* Colour validation, as in [R1]
  - note:
  - paid:
- [ ] **ENC-05** Flocked light-trap sheet, self-adhesive — 1 × $12.73 = $12.73 · optional · [buy at amazon.com](https://www.amazon.com/dp/B0FJRWTXXF) · status: suggested
  - <img src="docs/assets/parts/icon-fabric.svg" width="64" height="64" alt="ENC-05"> **Qty 1** · **Must meet:** Flocked light-trap material, self-adhesive, absorbs > 99 %
  - *why:* Line the backdrop and the lamp tube: kills stray reflections
  - note:
  - paid:
- [ ] **CAL-07** 18 % grey card + white card set (8 x 10 in) — 1 × $11.99 = $11.99 · optional · [buy at amazon.com](https://www.amazon.com/dp/B00CJ59AKK) · status: suggested
  - <img src="docs/assets/parts/icon-chart.svg" width="64" height="64" alt="CAL-07"> **Qty 1** · **Must meet:** 18 % neutral grey card, matte, ≥ 4 × 5 in
  - *why:* Lock exposure and white balance (M17.5); warm-up target (M18.3)
  - note:
  - paid:
- [ ] **ENC-04** Dowel sockets, drape clips — print · print · status: suggested
  - <img src="docs/assets/parts/ENC-04a_dowel_socket.png" width="64" height="64" alt="ENC-04"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/ENC-04a_dowel_socket.step](phases/07-calibrate/3d/ENC-04a_dowel_socket.step)
  - *why:* Enclosure hardware
  - note:
- [ ] **CAL-06** Kinematic holders for mirror, PTFE, balls — print · print · status: suggested
  - <img src="docs/assets/parts/CAL-06a_ptfe_holder.png" width="64" height="64" alt="CAL-06"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/CAL-06a_ptfe_holder.step](phases/07-calibrate/3d/CAL-06a_ptfe_holder.step)
  - *why:* Fixtures on the stage
  - note:

## 08 · Tilt (M2)

0/7 decided · still to buy $16.68 · [bom.csv](phases/08-tilt/bom.csv) · [checklist](phases/08-tilt/README.md)

- [ ] **TLT-01** NEMA 17 stepper 59 Ncm 2 A — $0 (in another row) · [buy at amazon.com](https://www.amazon.com/dp/B00Y2HJE22) · status: suggested
  - <img src="docs/assets/parts/icon-motor.svg" width="64" height="64" alt="TLT-01"> **Qty 1** · **Must meet:** NEMA 17, 1.8°/step, bipolar 4-wire, ≥ 40 N·cm holding, ≤ 2.0 A/phase (driver runs 0.8 A), 5 mm D-shaft
  - *why:* M2 (sample tilt, horizontal axis) drive · In the LAR-02 3-pack. Same motor on every axis.
  - note:
  - paid:
- [ ] **TLT-02** GT2 6 mm closed belt 280 mm — 1 × $7.49 = $7.49 · [buy at amazon.com](https://www.amazon.com/dp/B07RK1TX8C) · status: suggested
  - <img src="docs/assets/parts/icon-belt.svg" width="64" height="64" alt="TLT-02"> **Qty 1** · **Must meet:** GT2 6 mm closed loop, 280 mm
  - *why:* 20T to printed 100T, 5:1
  - note:
  - paid:
- [ ] **TLT-03** GT2 20T pulley 5 mm bore — $0 (in another row) · [buy at amazon.com](https://www.amazon.com/dp/B0DJQC42DT) · status: suggested
  - <img src="docs/assets/parts/icon-pulley.svg" width="64" height="64" alt="TLT-03"> **Qty 1** · **Must meet:** GT2 (2 mm pitch) 20-tooth, 5 mm bore, for 6 mm belt, 2 set screws
  - *why:* Motor pulley · In the LAR-04 5-pack.
  - note:
  - paid:
- [ ] **TLT-04** Optical endstop module, slot type (from the LAR-05 6-pack) — $0 (in another row) · [buy at amazon.com](https://www.amazon.com/dp/B0719K9Z9R) · status: suggested
  - <img src="docs/assets/parts/icon-endstop.svg" width="64" height="64" alt="TLT-04"> **Qty 1** · **Must meet:** Slotted optical switch module (TCST2103, 3.1 mm slot), 3.3–5 V supply, digital output the E4 home input reads
  - *why:* Home · In the LAR-05 6-pack.
  - note:
  - paid:
- [ ] **TLT-05** M8 x 35 hex bolts, half thread (10-pack; 2 used) — 1 × $9.19 = $9.19 · [buy at amazon.com](https://www.amazon.com/dp/B08KSVMT7W) · status: suggested
  - <img src="docs/assets/parts/icon-hardware.svg" width="64" height="64" alt="TLT-05"> **Qty 1** · **Must meet:** 2 × M8-1.25 × 35 mm hex bolt (DIN 931, smooth shank under the bearing), grade 8.8, + 2 M8 hex nuts
  - *why:* Cradle turns on two stub axles in the yoke's 608s · Nuts from the TBL-05 pack.
  - note:
  - paid:
- [ ] **TLT-06** Axis fasteners (M3/M5 set) — $0 (in another row) · [buy at amazon.com](https://www.amazon.com/dp/B0DBLCHK48) · status: suggested
  - <img src="docs/assets/parts/icon-hardware.svg" width="64" height="64" alt="TLT-06"> **Qty 1** · **Must meet:** M3/M5 socket screws 8–30 mm, nuts and washers (motor mount, pulley, clamp)
  - *why:* Motor mount, pulley, clamp · From the FRM-06 kit.
  - note:
  - paid:
- [ ] **TLT-07** Printed tilt parts — print · print · status: suggested
  - <img src="docs/assets/parts/TLT-07a_tilt_yoke.png" width="64" height="64" alt="TLT-07"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/TLT-07a_tilt_yoke.step](phases/08-tilt/3d/TLT-07a_tilt_yoke.step)
  - *why:* Yoke (motor slots above the axis), 100T pulley, cradle
  - note:

## 09 · Spin (M1)

0/4 decided · still to buy $11.99 · [bom.csv](phases/09-spin/bom.csv) · [checklist](phases/09-spin/README.md)

- [ ] **SPN-01** NEMA 17 pancake stepper 16 Ncm 1 A (direct drive) — 1 × $11.99 = $11.99 · [buy at amazon.com](https://www.amazon.com/dp/B00PNEQ79Q) · status: suggested
  - <img src="docs/assets/parts/icon-motor.svg" width="64" height="64" alt="SPN-01"> **Qty 1** · **Must meet:** NEMA 17 pancake, body ≤ 25 mm, 1.8°/step, ≥ 13 N·cm, ≤ 1.0 A, 5 mm D-shaft ≥ 16 mm (driver at 1/64 microstep)
  - *why:* M1 spin: the platter sits on its shaft
  - note:
  - paid:
- [ ] **SPN-04** Optical endstop module, slot type (from the LAR-05 6-pack) — $0 (in another row) · [buy at amazon.com](https://www.amazon.com/dp/B0719K9Z9R) · status: suggested
  - <img src="docs/assets/parts/icon-endstop.svg" width="64" height="64" alt="SPN-04"> **Qty 1** · **Must meet:** Slotted optical switch module (TCST2103, 3.1 mm slot), 3.3–5 V supply, digital output the E4 home input reads
  - *why:* Home · In the LAR-05 6-pack.
  - note:
  - paid:
- [ ] **SPN-06** Axis fasteners (M3/M5 set) — $0 (in another row) · [buy at amazon.com](https://www.amazon.com/dp/B0DBLCHK48) · status: suggested
  - <img src="docs/assets/parts/icon-hardware.svg" width="64" height="64" alt="SPN-06"> **Qty 1** · **Must meet:** M3/M5 socket screws 8–30 mm, nuts and washers (motor mount, pulley, clamp)
  - *why:* Motor mount, pulley, clamp · From the FRM-06 kit.
  - note:
  - paid:
- [ ] **SPN-07** Spin platter (direct drive) — print · print · status: suggested
  - <img src="docs/assets/parts/SPN-07a_spin_platter.png" width="64" height="64" alt="SPN-07"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/SPN-07a_spin_platter.step](phases/09-spin/3d/SPN-07a_spin_platter.step)
  - *why:* Sample face; clamps the motor's D-shaft with an M3 grub in a captive nut
  - note:

## 10 · Colour add-ons (optional)

0/9 decided · still to buy $0.00 · [bom.csv](phases/10-color/bom.csv) · [checklist](phases/10-color/README.md)

- [ ] **MSK-01** Narrow-band 3 W star LEDs, pre-soldered leads (7 bands, 450–660 nm) — 7 × $10.99 = $76.93 · optional · [buy at amazon.com](https://www.amazon.com/dp/B0GJMJ5MWN) · status: suggested
  - <img src="docs/assets/parts/icon-led.svg" width="64" height="64" alt="MSK-01"> **Qty 7** · **Must meet:** Narrow-band LEDs on 20 mm stars with pre-soldered wire leads (no solder), 1–3 W, bandwidth ≤ 30 nm, spread over 450–660 nm
  - *why:* Colour bands · One pack per band, $10.99 each (lens angle doesn't matter: the lenses are left off). The yellow and orange listings give no wavelength (typically ≈ 590 / ≈ 605 nm): measure them with the SPC sensor. Ring slot 8 stays spare. The first-draft CHANZON parts are bare chips that need soldering.
  - note:
  - paid:
- [ ] **MSK-02** Constant-current driver 350 mA — 1 × $5.41 = $5.41 · optional · [buy at digikey.com](https://www.digikey.com/en/products/detail/mean-well-usa-inc/NLDD-350H/13913618) · status: suggested
  - <img src="docs/assets/parts/icon-driver.svg" width="64" height="64" alt="MSK-02"> **Qty 1** · **Must meet:** Constant-current LED driver 350 mA, input covering 24 V
  - *why:* One driver, one LED on at a time
  - note:
  - paid:
- [ ] **MSK-03** Darlington array 8-ch — 1 × $3.84 = $3.84 · optional · [buy at digikey.com](https://www.digikey.com/en/products/detail/stmicroelectronics/ULN2803A/599591) · status: suggested
  - <img src="docs/assets/parts/icon-chip.svg" width="64" height="64" alt="MSK-03"> **Qty 1** · **Must meet:** ULN2803A 8-channel Darlington array (500 mA per channel), DIP-18 (plugs into the breadboard)
  - *why:* Pico selects the band (low-side)
  - note:
  - paid:
- [ ] **MSK-04** Heatsink 40 mm (from LSR-03 pack) — $0 (in another row) · optional · [buy at amazon.com](https://www.amazon.com/dp/B07D4FVC61) · status: suggested
  - <img src="docs/assets/parts/icon-heatsink.svg" width="64" height="64" alt="MSK-04"> **Qty 1** · **Must meet:** Aluminium heatsink ≥ 40 × 40 mm
  - *why:* LED bank cooling · From the LSR-03 pack. Optional colour kit (stage 10).
  - note:
  - paid:
- [ ] **MSK-05** Linear polarizer film 10 x 10 cm (10) — 1 × $6.83 = $6.83 · optional · [buy at amazon.com](https://www.amazon.com/dp/B0FX4P45HD) · status: suggested
  - <img src="docs/assets/parts/icon-film.svg" width="64" height="64" alt="MSK-05"> **Qty 1** · **Must meet:** Linear polarizer film for visible light; crossed ÷ parallel ≤ 1/20 when tested
  - *why:* Polarized capture (specular/diffuse separation)
  - note:
  - paid:
- [ ] **SPC-01** AS7341 10-band spectral sensor breakout (STEMMA QT) — 1 × $18.95 = $18.95 · optional · [buy at adafruit.com](https://www.adafruit.com/product/4698) · status: suggested
  - <img src="docs/assets/parts/icon-board.svg" width="64" height="64" alt="SPC-01"> **Qty 1** · **Must meet:** AS7341 10-channel spectral sensor breakout, I²C address 0x39, 3.3 V, STEMMA QT / Qwiic
  - *why:* Spectral reading of the spot at the zero point · I2C 0x39 on Pico GP16/GP17, shared with the OLED
  - note:
  - paid:
- [ ] **SPC-02** JST-SH 4-pin to female jumper cable 150 mm — 1 × $0.95 = $0.95 · optional · [buy at adafruit.com](https://www.adafruit.com/product/4397) · status: suggested
  - <img src="docs/assets/parts/icon-cable.svg" width="64" height="64" alt="SPC-02"> **Qty 1** · **Must meet:** JST-SH 4-pin (STEMMA QT) to female 2.54 mm sockets, ≈ 150 mm
  - *why:* Sensor to Pico
  - note:
  - paid:
- [ ] **MSK-06** LED bank ring on a 40 deg mast, polarizer holders — print · print · status: suggested
  - <img src="docs/assets/parts/MSK-06a_led_ring.png" width="64" height="64" alt="MSK-06"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/MSK-06a_led_ring.step](phases/10-color/3d/MSK-06a_led_ring.step)
  - *why:* 40° mast: 2nd light height
  - note:
- [ ] **SPC-03** Spectral sensor tube + mount — print · print · status: suggested
  - <img src="docs/assets/parts/SPC-03a_spectral_tube.png" width="64" height="64" alt="SPC-03"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/SPC-03a_spectral_tube.step](phases/10-color/3d/SPC-03a_spectral_tube.step)
  - *why:* 3 mm aperture, ~4 deg field; sits above the camera lens
  - note:

## 11 · 3D scan: capture

0/6 decided · still to buy $3.33 · [bom.csv](phases/11-scan-capture/bom.csv) · [checklist](phases/11-scan-capture/README.md)

- [ ] **SCN-01** Mounting putty 2 oz — 1 × $2.33 = $2.33 · [buy at amazon.com](https://www.amazon.com/dp/B003LZMHIY) · status: suggested
  - <img src="docs/assets/parts/icon-putty.svg" width="64" height="64" alt="SCN-01"> **Qty 1** · **Must meet:** Removable mounting putty
  - *why:* Holds objects on the tilted platter during scans
  - note:
  - paid:
- [ ] **SCN-02** ChArUco scanning mat print — 1 × $1.00 = $1.00 · status: suggested
  - <img src="docs/assets/parts/icon-chart.svg" width="64" height="64" alt="SCN-02"> **Qty 1** · **Must meet:** ChArUco mat printed at 100 % on matte paper
  - *why:* Scale and pose check under the object · A service, not a store item. Free generator: ChArUco, A4/Letter, print at 100 %.
  - note:
  - paid:
- [ ] **CAM-04** Second USB camera 12 MP IMX477, M12 mount (scan camera) — 1 × $59.99 = $59.99 · optional · [buy at amazon.com](https://www.amazon.com/dp/B0C1G73QZD) · status: suggested
  - <img src="docs/assets/parts/icon-camera.svg" width="64" height="64" alt="CAM-04"> **Qty 1** · **Must meet:** Identical to CAM-01 (same sensor, so the same settings and calibration steps)
  - *why:* No-switching kit: the scan camera stays at 650 mm; the measuring camera never moves or refocuses
  - note:
  - paid:
- [ ] **CAM-05** Second M12 16 mm lens (scan camera) — 1 × $30.11 = $30.11 · optional · [buy at amazon.com](https://www.amazon.com/dp/B0HJWVFD7R) · status: suggested
  - <img src="docs/assets/parts/icon-lens.svg" width="64" height="64" alt="CAM-05"> **Qty 1** · **Must meet:** Identical to CAM-02: 16 mm focal length (236 × 186 mm field at 650 mm), used at f/8 (2.0 mm stop)
  - *why:* No-switching kit: the scan camera stays at 650 mm; the measuring camera never moves or refocuses
  - note:
  - paid:
- [ ] **CAM-08** M2.5 x 8 mm screws (4), second camera — $0 (in another row) · optional · [buy at amazon.com](https://www.amazon.com/dp/B07YS6D2GT) · status: suggested
  - <img src="docs/assets/parts/icon-hardware.svg" width="64" height="64" alt="CAM-08"> **Qty 1** · **Must meet:** M2.5-0.45 × 8 mm pan-head machine screws
  - *why:* Second camera (CAM-04) onto the scan camera plate (2nd camera kit; without it the CAM-07 screws move with the camera) · From the CAM-07 pack.
  - note:
  - paid:
- [ ] **SCN-03** Platter risers (20/40/60 mm), scan camera plate (15 deg) — print · print · status: suggested
  - <img src="docs/assets/parts/SCN-03a_riser_20.png" width="64" height="64" alt="SCN-03"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/SCN-03a_riser_20.step](phases/11-scan-capture/3d/SCN-03a_riser_20.step)
  - *why:* Object centre at the zero point · δ = 60 − riser height.
  - note:

## 15 · Standalone (no laptop)

0/8 decided · still to buy $0.00 · [bom.csv](phases/15-standalone/bom.csv) · [checklist](phases/15-standalone/README.md)

- [ ] **STA-01** Raspberry Pi Zero 2 WH (header soldered) — 1 × $19.80 = $19.80 · optional · [buy at adafruit.com](https://www.adafruit.com/product/6008) · status: suggested
  - <img src="docs/assets/parts/icon-board.svg" width="64" height="64" alt="STA-01"> **Qty 1** · **Must meet:** Raspberry Pi Zero 2 W with factory-soldered 40-pin header (Zero 2 WH), 64-bit, WiFi
  - *why:* Runs opengonio station: jobs + camera without the laptop · Out of stock at Adafruit when checked. Header pre-soldered: jumpers push on. MSRP; any approved reseller.
  - note:
  - paid:
- [ ] **STA-02** microSD card 32 GB — 1 × $18.99 = $18.99 · optional · [buy at amazon.com](https://www.amazon.com/dp/B0DR926VXL) · status: suggested
  - <img src="docs/assets/parts/icon-sd.svg" width="64" height="64" alt="STA-02"> **Qty 1** · **Must meet:** microSD ≥ 16 GB, A1 class
  - *why:* Pi OS + job data
  - note:
  - paid:
- [ ] **STA-03** Buck converter 24 V to 5 V 3 A — 1 × $7.99 = $7.99 · optional · [buy at amazon.com](https://www.amazon.com/dp/B0DBVYP91F) · status: suggested
  - <img src="docs/assets/parts/icon-driver.svg" width="64" height="64" alt="STA-03"> **Qty 1** · **Must meet:** Buck converter 24 V in → 5.1 V out, ≥ 3 A, screw terminals on input and output
  - *why:* Powers the Pi from BUS_24V (before the e-stop) · Set it to 5.1 V with the trimmer before connecting the Pi; check for screw terminals.
  - note:
  - paid:
- [ ] **STA-04** Micro-USB OTG adapter — 1 × $2.50 = $2.50 · optional · [buy at adafruit.com](https://www.adafruit.com/product/1099) · status: suggested
  - <img src="docs/assets/parts/icon-cable.svg" width="64" height="64" alt="STA-04"> **Qty 1** · **Must meet:** Micro-USB OTG to USB-A adapter (powered USB hub if using two cameras)
  - *why:* Camera into the Pi USB port
  - note:
  - paid:
- [ ] **STA-05** SSD1306 OLED 0.96 in I2C 128x64 — 1 × $17.50 = $17.50 · optional · [buy at adafruit.com](https://www.adafruit.com/product/326) · status: suggested
  - <img src="docs/assets/parts/icon-screen.svg" width="64" height="64" alt="STA-05"> **Qty 1** · **Must meet:** SSD1306 OLED 128 × 64, I²C, 3.3 V, address 0x3C, 4-pin header pre-soldered
  - *why:* Menu and progress on the panel (both modes) · Check the address is 0x3C (some are 0x3D).
  - note:
  - paid:
- [ ] **STA-06** Jumper wires female-female (10) — 1 × $1.95 = $1.95 · optional · [buy at adafruit.com](https://www.adafruit.com/product/1950) · status: suggested
  - <img src="docs/assets/parts/icon-jumper.svg" width="64" height="64" alt="STA-06"> **Qty 1** · **Must meet:** Female–female 2.54 mm jumper wires
  - *why:* Pi UART to Pico; OLED · Consumable: set `have` if it's in your drawer.
  - note:
  - paid:
- [ ] **STA-08** USB-A to micro-B data cable 1 m — 1 × $2.95 = $2.95 · optional · [buy at adafruit.com](https://www.adafruit.com/product/592) · status: suggested
  - <img src="docs/assets/parts/icon-cable.svg" width="64" height="64" alt="STA-08"> **Qty 1** · **Must meet:** USB-A to micro-B data cable (not charge-only), ≤ 1 m
  - *why:* Pi OTG port to a USB hub / camera
  - note:
  - paid:
- [ ] **STA-07** Pi Zero mount + OLED window — print · print · status: suggested
  - <img src="docs/assets/parts/STA-07a_pi_zero_mount.png" width="64" height="64" alt="STA-07"> **Qty 1** · **Must meet:** ABS, 0.2 mm layers, 4 walls, 25–30 % infill, enclosed printer; settings and checks in this stage's checklist · files: [3d/STA-07a_pi_zero_mount.step](phases/15-standalone/3d/STA-07a_pi_zero_mount.step)
  - *why:* Clips into the controller case
  - note:
