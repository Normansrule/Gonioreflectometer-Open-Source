# Camera Arm module (Phase 1, M1.4)

Status: **planned** — full documentation is written when this module's milestone starts (one module at a time, with your approval before moving on).

## 1. Purpose
A1: camera elevation 0-85 deg about the Y axis through the measurement centre. L-shaped 2020 arm, 608 pivot, printed 100T pulley (5:1), counterweight, TCST2103 home flag at 85 deg, AS5600 on the output axle.

## Interface spec
Tower foot on OG-40 at (0, -175). Arm end: 2 x M3 on 20 mm for the camera head. Harness M-A1, E-A1, I-A1 to the controller.

## What later phases attach
Unchanged through Phase 6. Phase 5 adds the polarizer servo on the camera head.

## 2. BOM
[`bom/modules/camera-arm.csv`](../../bom/modules/camera-arm.csv) — subtotal **$22.88 spec / $22.88 budget / $22.88 with own stock** (approximate, checked 2026-10-04).

## Deliverables still to write (tracked in issue `M1.4`)
- [ ] 1. Purpose, interface spec, future attachments (frozen)
- [ ] 2. BOM with confirmed STEP links and budget share
- [ ] 3. Onshape modelling instructions (variables, features, print settings)
- [ ] 4. Step-by-step assembly with alignment, torque and wiring notes
- [ ] 5. Wiring diagram and connector pinout
- [ ] 6. Firmware / software for this module
- [ ] 7. Acceptance test with pass/fail numbers
- [ ] 8. Safety notes
