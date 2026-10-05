# 11 · 3D scan: capture

Photograph an object from 144 known positions.

<img src="../../docs/assets/scanner.svg" width="100%" alt="3D scan: capture">

$4.49 · total so far $498.95 / $500

[Design](design/) · [3D files](3d/) · [Bill of materials](bom/) · [Tests](test/)

## 11.1 Scan setup

- [ ] Print risers, nest, 650 mm camera stop
- [ ] Slide camera to 650 mm, refocus
- [ ] **Done:** Putty holds a 100 g object at 80° for 3 turns.

## 11.2 Calibrate camera position

- [ ] opengonio scan calibrate
- [ ] Set scan.calibration in machine.yaml
- [ ] **Done:** Fit ≤ 0.2° and ≤ 0.3 mm (test S1–S2).

## 11.3 Capture

- [ ] opengonio scan run --background
- [ ] opengonio scan run
- [ ] **Done:** 144 sharp photos + photometric-stereo set, unattended.

[Sources](../../REFERENCES.md): S9 · S12 · S14 · S20 · G4 · G39 · V7 · V8 · V9 · V10 · V11 · V12 · V13 · V14 · V15 · V16 · V17 · V18 · V25 · V27 · V30 · V48 · V50 · V51 · V53 · V54 · V55 · H49
