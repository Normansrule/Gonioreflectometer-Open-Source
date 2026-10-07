# 01 · Power box

<img src="../../docs/assets/steps/01.svg" width="100%" alt="Steps of stage 01">

<img src="../../docs/assets/power-flow.svg" width="100%" alt="Power box">

$70.33 · total so far $70.33 / $450

[Design](design.md) · [Research](research.md) · [Parts list](bom.csv) · [3D files](3d/) · [Tests](test.csv)

## M04 · Order power parts

Everything for the power box on the bench. · 0/3 steps done · ~1.1 h hands-on · ~2 wk

### M04.1 Order

**Time** 30 min (+ shipping 3–10 days) · **Needs** `PARTS.md` → 01 · Power box · FRM-06 screws (03 · Frame) · `PARTS.md` → 00 · Tools

#### Do

1. Order every stage-01 part ticked `[x]` (status `agreed`), using its link.
2. Also order FRM-06 (M3/M4/M5 screws): the box needs them now.
3. Tools: set `have` on the TLS rows you own; buy the multimeter (TLS-05) and wire stripper (TLS-04) now if you don't.
4. In `PARTS.md` set each ordered part to `status: ordered` and fill `paid:`.

#### Verify

- [ ] Stage 01 in `PARTS.md` has no `agreed` or `suggested` parts left; *Paid so far* went up.
- [ ] Tools TLS-02 to TLS-06 are `have` or `ordered`.

#### If a check fails

- Part out of stock: its *Must meet* line says what a substitute needs; set `swap` + `note:`, or add one with `python tools/new.py part …`.

#### Record

Commit the dated BOM.

### M04.2 Print the box

**Time** 15 min (+ print 5 h) · **Needs** PETG

#### Do

1. Print `phases/01-power/3d/PWR-18a_power_box.stl` and `PWR-18b_power_lid.stl`: PETG, 0.2 mm, 4 walls, 30 % infill.

#### Verify

- [ ] Walls not split; the Ø22.3 e-stop hole in the lid is round (calipers 22.2–22.5 mm).

#### If a check fails

- Hole too small: scale the lid XY by +1 % in the slicer and reprint (no drilling).

#### Record

Tick the boxes; `make done id=M04.2`.

### M04.3 Check parts

**Time** 20 min · **Needs** all PWR parts · printed box + lid

#### Do

1. Lay all parts out; check each against its *Must meet* line in `PARTS.md` (value, rating).
2. Dry-fit: DC jack adapter PWR-03 in the slot of the +X wall; e-stop PWR-13 in the lid.

#### Verify

- [ ] Fuse PWR-05 marked 3.15 A **T** (time-lag), 2 pieces.
- [ ] E-stop has an NC contact block with screw terminals.
- [ ] Each part fits its hole without forcing.

#### If a check fails

- Wrong part: return it now; don't substitute ratings (fuse 3.15 A T, e-stop NC ≥ 3 A at 24 V DC).

#### Record

`status: have` per part in `PARTS.md` as it arrives; commit.

## M05 · Wire the power box

Fuse and e-stop wired with screw terminals only; nothing soldered; not powered yet. · 0/3 steps done · ~1.2 h hands-on · ~1 wk

### M05.1 Box hardware

**Time** 20 min · **Needs** PWR-18 box + lid · PWR-03 jack adapter · PWR-13 e-stop · 4 × M3 × 10 · TLS-02 / TLS-03

#### Do

1. Drive the 4 M3 × 10 into the box posts once and back out (cuts the threads).
2. DC jack adapter (PWR-03) into the +X wall slot: barrel facing out, screw block inside.
3. E-stop (PWR-13) through the lid hole, ring nut tight; NC contact block on its back (marked NC, usually red, terminals 1–2).

#### Verify

- [ ] Twisting each part by hand: nothing rotates.
- [ ] Lid closes on 4 × M3 × 10 with no gap.

#### If a check fails

- Lid screw spins: that post's hole is too big; reprint the box with a smaller `M3_TAP`.

#### Record

Tick the boxes; `make done id=M05.1`.

### M05.2 Main wiring

**Time** 45 min · **Needs** PWR-04 fuse holder + PWR-05 fuse · PWR-15 18 AWG pair (1 m) · TLS-04 stripper · TLS-02 flat screwdriver

#### Do

1. Strip 8 mm, twist the strands tight.
2. Jack `+` terminal → fuse holder lead A. Fuse holder lead B → e-stop NC terminal 1.
3. E-stop NC terminal 2 → the whole red wire, out through the J3 slot (it will later pass through the over-travel switch, M14.1, on its way to the E4).
4. Jack `−` terminal → the whole black wire, out through the −X slot. Leave both ends free; zip-tie the pair to the box.
5. Tug every wire: none slips out.

#### Verify

- [ ] Continuity beeps along each row of the netlist (`phases/01-power/design.md`): jack + … red end, jack − … black end.
- [ ] No beep red out ↔ black out.

#### If a check fails

- No beep through the e-stop: you used the NO block; move the wires to NC.
- Wire pulls out: strip longer, twist, re-tighten.

#### Record

Tick each row on the printed netlist. Tick the boxes; `make done id=M05.2`.

### M05.3 Checks with power off

**Time** 10 min · **Needs** TLS-05 multimeter · adapter unplugged · e-stop released

#### Do

1. Ω range: red out to black out (T1).
2. Ω range: across the fuse holder leads with the fuse in (T2).

#### Verify

- [ ] T1 > 10 kΩ (or OL).
- [ ] T2 < 1 Ω.

#### If a check fails

- T1 low: a stray strand bridges + and − at the jack screws; re-strip and re-tighten.
- T2 OL: fuse blown or not seated; fit the spare.

#### Record

T1, T2 in `phases/01-power/test.csv` (date, value, PASS/FAIL).

## M06 · First power-on

Safe 24 V that the e-stop cuts. · 0/3 steps done · ~40 min hands-on · ~1 wk

### M06.1 First 24 V and polarity

**Time** 15 min · **Needs** PWR-01 adapter · PWR-02 cord · TLS-05 multimeter

#### Do

1. E-stop pressed. Plug the adapter into the jack, then into the wall.
2. Release the e-stop; DC V: black probe on black out, red probe on red out (T3).

#### Verify

- [ ] T3 = +23.5 to +24.5 V (a plus sign: polarity right).
- [ ] No smell, nothing warm after 1 min.

#### If a check fails

- Reads −24 V: jack + / − swapped; unplug, swap the two wires at the jack screws.
- 0 V: fuse (check T2), e-stop pressed, or the J3 loop open.

#### Record

T3 in `test.csv`.

### M06.2 E-stop and unplug

**Time** 10 min · **Needs** TLS-05 multimeter

#### Do

1. Press the e-stop; read the out leads after 1 s (T5). Release.
2. Pull the adapter from the wall; read after 2 s (T6). (No rocker: off = e-stop pressed or unplugged.)

#### Verify

- [ ] T5 < 1 V within 1 s.
- [ ] T6 < 0.5 V within 2 s.

#### If a check fails

- Stays high on e-stop: J3 loop bypassed or NC/NO swapped.

#### Record

T5, T6 in `test.csv`.

### M06.3 Heat

**Time** 15 min (+ 30 min soak) · **Needs** TLS-05 temperature probe · optional: plug-in power meter

#### Do

1. Check the fitted fuse and the spare (T8).
2. Lid closed, 30 min on; temperature probe through the J3 slot into the box air (T9).
3. Optional: wall power meter, nothing on the out leads: read watts (T10).

#### Verify

- [ ] T8 3.15 A T fitted + spare.
- [ ] T9 ≤ 45 °C.
- [ ] T10 ≤ 3 W (if measured).

#### If a check fails

- T9 high: a loose screw terminal heats up; feel each one, re-tighten.

#### Record

T8–T10 in `test.csv`; label the box *24 V*; commit.

> **Safety:** Mains stays inside the certified adapter. Plug in with the e-stop pressed; unplug before touching any screw terminal.

[Sources](../../REFERENCES.md): N48 · N49 · N51 · H9 · H43 · P1 · P2 · P3 · P6 · P15 · P16 · P17 · P20 · P45 · P46 · P47
