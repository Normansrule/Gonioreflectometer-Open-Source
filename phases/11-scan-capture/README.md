# 11 · 3D scan: capture

**Goal:** Photograph an object from 144 known positions.

<img src="../../docs/assets/scanner.svg" width="100%" alt="3D scan: capture">

**Cost:** $4.49 · running total $498.95 of $500

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

<sub>Generated from `.github/phases.yml` by `tools/roadmap.py`.</sub>
