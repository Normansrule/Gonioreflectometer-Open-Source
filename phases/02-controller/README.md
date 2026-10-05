# 02 · Controller and buttons

$55.99 · total so far $122.82 / $500

[Design](design/) · [3D files](3d/) · [Bill of materials](bom/) · [Tests](test/)

## M07 · Order controller parts

E4, Pico, buttons and one motor on the bench. · ~2 wk

**M07.1 Order**

- [ ] Order phases/02-controller/bom/bom.csv and one NEMA 17 (LAR-02)
- [ ] **Done:** Parts arrived.

## M08 · One motor turns from the laptop

Laptop → E4 → motor works on the bench. · ~1 wk

**M08.1 Flash the E4**

- [ ] WSL only: usbipd bind/attach (design/firmware.md)
- [ ] bash scripts/e4.sh flash
- [ ] bash scripts/e4.sh wifi "SSID" "PASS"
- [ ] bash scripts/e4.sh config fluidnc.local
- [ ] **Done:** opengonio send '?' prints <Idle|…>.

**M08.2 Bench motor**

- [ ] Motor on X, 24 V on
- [ ] opengonio send 'G91 G1 X10 F600' 'G1 X-10'
- [ ] **Done:** Motor turns both ways; e-stop stops it.

## M09 · Buttons work with the laptop

Physical buttons drive the machine. · ~1 wk

**M09.1 Pico hub**

- [ ] bash scripts/pico.sh
- [ ] Wire 5 buttons to GP2–6, PAUSE to E4 GPIO39
- [ ] **Done:** Each button prints its BTN line.

**M09.2 Panel**

- [ ] opengonio panel
- [ ] PAUSE during a move
- [ ] **Done:** HOME, START, STOP, LIGHT, NEXT act; PAUSE holds.

## M10 · Controller box closed

Boards boxed, links tested. · ~1 wk

**M10.1 Box and test**

- [ ] Print case + panel, mount boards
- [ ] Run C1–C8 (USB, WiFi, Bluetooth), fill test/log.csv
- [ ] **Done:** C1–C8 pass.

> **Safety:** Never plug or unplug motors with 24 V on.

[Sources](../../REFERENCES.md): R24 · R25 · R42 · R81 · N48 · H1 · H2 · H4 · H5 · H6 · H7 · H8 · H23 · H24 · H25 · H43 · H54 · P22 · C1 · C2 · C3 · C4 · C5 · C6 · C7
