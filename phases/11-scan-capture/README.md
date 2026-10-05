# 11 · 3D scan: capture

<img src="../../docs/assets/scanner.svg" width="100%" alt="3D scan: capture">

$4.49 · total so far $498.95 / $500

[Design](design.md) · [Parts list](bom.csv) · [3D files](3d/) · [Tests](test.csv)

## M31 · Scan hardware

Object held securely, camera at 650 mm. · ~1 wk

**M31.1 Risers and camera stop**

- [ ] Print risers, nest, 650 mm stop
- [ ] Slide camera, refocus
- [ ] **Done:** Putty holds a 100 g object at 80° tilt for 3 turns.

## M32 · Camera position calibrated

Every photo's pose known to 0.3 mm. · ~1 wk

**M32.1 Calibrate**

- [ ] opengonio scan calibrate
- [ ] Set scan.calibration in machine.yaml
- [ ] **Done:** Fit ≤ 0.2° and ≤ 0.3 mm (S1–S2).

## M33 · First full scan

144 photos plus photometric-stereo set, unattended. · ~1 wk

**M33.1 Capture**

- [ ] opengonio scan run --background
- [ ] opengonio scan run
- [ ] **Done:** All photos sharp; S3 passes.

[Sources](../../REFERENCES.md): S9 · S12 · S14 · S20 · G4 · G39 · V7 · V8 · V9 · V10 · V11 · V12 · V13 · V14 · V15 · V16 · V17 · V18 · V25 · V27 · V30 · V48 · V50 · V51 · V53 · V54 · V55 · H49
