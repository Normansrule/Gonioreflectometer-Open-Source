# Changelog

## [0.3.0] - 2026-10-04
### Added
- Phase 6 3D photo scanner: scan mode (camera at 650 mm, f/8), 144-view ring plan from M1/M2, measured camera pose (ChArUco + AX = YB fit), known poses → COLMAP model + ID sync + run script, near-light visual-hull carving, photometric stereo (LED bank on a 40° mast), PLY export, `opengonio scan` CLI, scan-kit module.
- Phase 7 on-object appearance, M8 Studio app, M9 release, M10 stretch milestones (11 milestones, 49 issues); roadmap sync updates renamed items.
- Scanner figure, interactive view-sphere planner, scanner equations, references S1–S20.
### Changed
- Caps rebalanced to seven phases; buy-all $498.95 (P6KE30A from Littelfuse, T-nut count from the fastener schedule).

## [0.2.0] - 2026-10-04
### Changed
- Architecture now follows Ansari-Asl et al. 2024 [R1]: fixed camera, 3-axis sample stage (M3, M2, M1), light arm (M4).
- Laptop is the host (no Raspberry Pi): FYSETC E4 + FluidNC over USB / WiFi / Bluetooth; Pico hub for buttons and sensors.
- Cheapest parts by default: $496.62 buy-all, $441.94 with own consumables. 60 W adapter, no 5 V buck.
### Added
- Animated SVG figures, interactive Pages site (simulator, BRDF explorer, equations), full equation set, REFERENCES.md with every source.
- Controller module (8 sections), fastener schedule, FluidNC config, Pico hub firmware, optics calculator, publish script.

## [0.1.0] - 2026-10-04
- Initial Stanford-gantry-style design with Raspberry Pi + Klipper (superseded).
