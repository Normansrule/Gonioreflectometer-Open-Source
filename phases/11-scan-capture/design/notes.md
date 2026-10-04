# Design

<img src="../../../docs/assets/scanner.svg" width="100%" alt="Scanner">

Camera fixed; M1 spins and M2 tilts the object, so every pose is known [S9].

| | Measure mode | Scan mode |
|---|---|---|
| Camera | 350 mm, f/8 | 650 mm, f/8 (printed stop) |
| Field · pixel | 124 × 98 mm · 0.032 mm | 236 × 186 mm · 0.061 mm (detail ~0.25 mm) |
| Depth of field | ~23 mm | ~117 mm |
| Object | swatch, 60 mm riser | ≤ 110 mm object, lower riser |

- Riser sets δ = 60 − riser height (mm) → `scan.platter_offset_mm`; pick δ ≈ object height / 2.
- View elevation = 90° − M2. Plan: rings at 0/20/40/60/80° → 144 photos.
- `opengonio scan calibrate` measures the real camera pose (ChArUco + joint fit), needed for ±0.5 mm.
- Photogrammetry light: lamp at M4 = 30°, crossed polarizers. Photometric stereo: LED bank at 6 arm positions.
- Background pass (empty platter, same poses) → clean silhouettes, even for black parts.

Fasteners: M3 × 8 × 2, M5 × 10 + T-nut × 1. Optics: [optics.md](../../06-camera-light/design/optics.md).
