# 11 · Design

<img src="../../docs/assets/scanner.svg" width="100%" alt="Scanner">

Camera fixed; M1 spins and M2 tilts the object, so every pose is known [S9].

| | Measure mode | Scan mode |
|---|---|---|
| Camera | measuring camera, 350 mm, f/8 | scan camera (second, CAM-04), fixed at 650 mm, 15° up, f/8; or the measuring camera moved there |
| Field · pixel | 124 × 98 mm · 0.032 mm | 236 × 186 mm · 0.061 mm (detail ~0.25 mm) |
| Depth of field | ~23 mm | ~117 mm |
| Object | swatch, 60 mm riser | ≤ 110 mm object, lower riser |

- Riser sets δ = 60 − riser height (mm) → `scan.platter_offset_mm`; pick δ ≈ object height / 2.
- View elevation = 90° − M2. Plan: rings at 0/20/40/60/80° → 144 photos.
- `opengonio scan calibrate` measures the real camera pose (ChArUco [V7] + AX = YB fit [V15]), needed for ±0.5 mm.
- Photogrammetry light: lamp at M4 = 30°, crossed polarizers if you built the colour kit [V51]. Photometric stereo (colour kit only): LED bank at 6 arm positions.
- Background pass (empty platter, same poses) → clean silhouettes, even for black parts.

Fasteners: M2 × 8 × 4 (camera), M2 × 16 × 1 (clamp into the post's pilot), M2 risers into the platter. Optics: [optics.md](../06-camera-light/optics.md).

## 3D parts

| Part | Source |
|---|---|
| Risers 20/40/60 mm (hollow), scan camera plate looking 15° down on the vertical post (SCN-03) | `tools/cad/parts.py` |

## Results

(fill in)
