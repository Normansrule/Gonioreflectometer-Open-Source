# Changelog

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
