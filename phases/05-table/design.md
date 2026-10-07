# 05 · Design

- **Fixed bolt axle (skateboard-wheel style):** an M8 × 75 bolt (TBL-05, DIN 931 smooth shank) stands in the post at (0, 0), its head locked in a hex pocket. The **drum** (TBL-07a: 100T teeth, two 608 seats, OG-40 top) turns on the two bearings around it. The inner races are clamped to the bolt by a 1 mm shim on the post top, a 6 mm spacer and one nut tightened with a 13 mm spanner; the outer races turn with the drum. Nothing to cut or file.
- Drive 5 : 1 (20T → 100T teeth on the drum) on a 232 mm belt: the motor stands shaft-up on the plywood **inside the lazy Susan opening** (centre 49.4 mm from the axis), in a bracket whose rails slide in slots for belt tension.
- Home flag (TBL-07b) on the drum rim at −180°; the drum's OG-40 top (M4 × 16 self-tap) takes the stage-08 yoke (a swatch clamp until then).
- Checked in CAD: nothing that turns with the table (drum, yoke, cradle, motors) touches the table motor, its bracket, the lazy Susan or the M4 motor over a full turn.

| z above plywood (mm) | Part |
|---|---|
| 1.0–6.5 | bolt head (hex-locked in the post) |
| 52.5–53.5 | 1 mm shim on the post top (inner race only) |
| 53.5–60.5 / 66.5–73.5 | lower / upper 608 in the drum; drum teeth 54.7–61.7 (= the motor's 20T: motor body 48 + bracket plate 5) |
| 73.5–80.0 | M8 nut (bolt end 81.5) |
| 80.7 | drum top: yoke base; tilt axis at 150 |

Fasteners: #8 wood screws × 4 (post) + 2 (bracket slots), M3 × 8 × 6 (motor face, flag).

## 3D parts

| Part | Source |
|---|---|
| Drum, flags, motor bracket, post, spacers (TBL-07a–f) | `tools/cad/parts.py` (`TABLE_Z`, `TABLE_BELT_C`) |
| NEMA 17 | [STEP](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) [P40] |

## Results

(fill in)
