# 01 · Power box

<img src="../../docs/assets/power-flow.svg" width="100%" alt="Power box">

$66.83 · total so far $66.83 / $500

[Research](research/) · [Design](design/) · [3D files](3d/) · [Bill of materials](bom/) · [Tests](test/)

## M04 · Order power parts

Everything for the power box on the bench. · ~2 wk

**M04.1 Order and print**

- [ ] Order phases/01-power/bom/bom.csv
- [ ] Print PWR-18a box and PWR-18b lid (3d/README.md)
- [ ] **Done:** Parts arrived, checked against the BOM.

## M05 · Build the protection board

Fuse, reverse-polarity MOSFET and e-stop wired, not yet powered. · ~1 wk

**M05.1 Solder**

- [ ] Solder per design/netlist.md
- [ ] Heat-shrink every joint
- [ ] **Done:** Board matches the netlist.

**M05.2 Checks with power off**

- [ ] Run T1–T3 (continuity, no shorts)
- [ ] Fill test/log.csv
- [ ] **Done:** T1–T3 pass.

## M06 · First power-on

Safe 24 V that the e-stop cuts. · ~1 wk

**M06.1 Power tests**

- [ ] Run T4–T10 with no load
- [ ] Close the box, add labels
- [ ] **Done:** All T tests pass; e-stop drops the bus to 0 V.

> **Safety:** Mains stays inside the adapter. Plug in with the rocker off.

[Sources](../../REFERENCES.md): N48 · N49 · N51 · H9 · H43 · P1 · P2 · P3 · P4 · P5 · P6 · P7 · P8 · P9 · P10 · P11 · P13 · P14 · P15 · P16 · P17 · P18 · P19 · P20 · P21
