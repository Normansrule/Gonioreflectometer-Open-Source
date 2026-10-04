# Controller module (Phase 1, M1.2)

Status: **planned** — full documentation is written when this module's milestone starts (one module at a time, with your approval before moving on).

## 1. Purpose
Raspberry Pi + SKR Mini E3 V3 in one printed, fan-cooled case. Runs Klipper (motion), Moonraker (API) and the opengantry Python package; captures RAW images.

## Interface spec
OG-40 on the base (front left). In: J2 24 V MOTION, J3 5 V HOST (USB-C pigtail to the Pi), J4 PWR-SIG. Out: M-A1..M-A4, E-A1..E-A4, I-A1..I-A4, L-MAIN (HE0), L-FILL (FAN2), SERVO (PA1), CSI ribbon. Pi to SKR over UART (TFT header, 5 V pin not connected).

## What later phases attach
All four driver sockets are populated from day one; Phase 3/4 plug in M-A3/M-A4 and uncomment their printer.cfg blocks. FAN2 and the servo pin are reserved for Phase 5.

## 2. BOM
[`bom/modules/controller.csv`](../../bom/modules/controller.csv) — subtotal **$68.29 spec / $49.44 budget / $38.95 with own stock** (approximate, checked 2026-10-04).

## Deliverables still to write (tracked in issue `M1.2`)
- [ ] 1. Purpose, interface spec, future attachments (frozen)
- [ ] 2. BOM with confirmed STEP links and budget share
- [ ] 3. Onshape modelling instructions (variables, features, print settings)
- [ ] 4. Step-by-step assembly with alignment, torque and wiring notes
- [ ] 5. Wiring diagram and connector pinout
- [ ] 6. Firmware / software for this module
- [ ] 7. Acceptance test with pass/fail numbers
- [ ] 8. Safety notes
