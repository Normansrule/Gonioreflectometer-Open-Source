# Light Source module (Phase 1, M1.7)

Status: **planned** — full documentation is written when this module's milestone starts (one module at a time, with your approval before moving on).

## 1. Purpose
CRI-95, 18 V-class COB (Luminus CXM-4, 4.5 mm LES) on a 40 mm heatsink, NLDD-350H constant-current driver, narrow optic, black housing with a polarizer slot.

## Interface spec
2 x M3 on 20 mm to the light arm. L-MAIN: driver +Vin from SKR VIN, switched return through HE0 MOSFET (on/off only, no PWM).

## What later phases attach
Phase 5 drops polarizer film into the housing slot.

## 2. BOM
[`bom/modules/light-source.csv`](../../bom/modules/light-source.csv) — subtotal **$23.50 spec / $23.50 budget / $23.50 with own stock** (approximate, checked 2026-10-04).

## Deliverables still to write (tracked in issue `M1.7`)
- [ ] 1. Purpose, interface spec, future attachments (frozen)
- [ ] 2. BOM with confirmed STEP links and budget share
- [ ] 3. Onshape modelling instructions (variables, features, print settings)
- [ ] 4. Step-by-step assembly with alignment, torque and wiring notes
- [ ] 5. Wiring diagram and connector pinout
- [ ] 6. Firmware / software for this module
- [ ] 7. Acceptance test with pass/fail numbers
- [ ] 8. Safety notes
