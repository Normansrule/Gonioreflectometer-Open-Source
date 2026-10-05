# 15 · Standalone (no laptop)

Optional kit $32.00 (not in the $500 total)

[Design](design.md) · [Parts list](bom.csv) · [3D files](3d/)

## M40 · Panel screen

OLED shows menu and progress (works in both modes). · ~1 wk

**M40.1 OLED**

- [ ] Order phases/15-standalone/bom.csv
- [ ] OLED on Pico GP16/GP17, bash scripts/pico.sh
- [ ] **Done:** Screen shows 'OpenGonio ready'.

## M41 · Pi Zero station set up

Pi drives the E4 over WiFi and grabs camera frames. · ~1 wk

**M41.1 Install**

- [ ] Imager: Pi OS Lite, hostname opengonio, SSH, WiFi
- [ ] Wire UART + buck (design.md)
- [ ] bash scripts/station.sh USER@opengonio.local; reboot
- [ ] **Done:** journalctl shows 'station ready'.

## M42 · Job with no laptop

Buttons choose and run a job; images saved on the Pi. · ~1 wk

**M42.1 Run**

- [ ] Laptop off; NEXT → Mirror check; START
- [ ] STOP mid-job, START again
- [ ] **Done:** Job folder with images + manifest.json.

## M43 · Laptop collects and verifies

Laptop only pulls and checks data. · ~1 wk

**M43.1 Pull and verify**

- [ ] opengonio pull USER@opengonio.local
- [ ] opengonio verify data/*
- [ ] **Done:** Mirror job: PASS, peak within 0.5°.

[Sources](../../REFERENCES.md): H51 · H52 · H53 · H55
