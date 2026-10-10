# 04 · Design

- 12 in lazy Susan (ID ~160 mm) screwed straight to the plywood through its own holes, each screw through a printed 4 mm washer (FRM-09g) so it can't poke through.
- GT2 belt CA-glued teeth-out on a 6 mm band around 8 printed rim segments (7 × LAR-08a + the arm segment LAR-08c; bolted with M4 × 16 + nuts where a slot meets a top-plate hole, CA-glued elsewhere) → 24 : 1 with a 20T pinion (set `gear_ratio` from the measured rim). No lips on the band: the pinion's 16 mm flanges pass above and below it. The belt's pitch line sits on `RIM_R` (back 0.38 mm inside it), and the pinion centre is `RIM_R` + 6.37 mm.
- M4 motor at 0° (+X), inside the arm's keep-out: its mount sits outside the lazy Susan (wood-screw slots reachable from above) and cantilevers a 56 mm plate over the rim, narrow enough for the arm to pass at the travel ends; the pinion meshes the rim belt directly (no idlers). Radial slots set the mesh.
- Arm: the arm segment (one of the 8 rim positions) holds the 500 mm 2020 upright at r = 136.8 mm, **36 mm beside the beam line** (15.3° ahead of the lamp): an upright on the beam line would shade the sample. Cross clamp (uncut upright runs through) → horizontal 2020 (500 mm) parallel to the beam line, 14 mm beside it → lamp clamp offset 14 mm so the beam axis passes through the zero point at 150 mm; lamp 300 mm out. M4 range 20–324° (the upright reaches the motor's keep-out at 339°).
- `make cad-check` proves it: no part collides in any axis position, and nothing blocks the camera, scan camera or lamp sight lines to the sample.
- Home flag at 20°; roller over-travel switch (screw terminals) just beyond: the red 24 V wire passes through its COM–NC on the way to the E4 [R1].

Fasteners: #8 × 5/8 Type 17 wood screws × 10 (lazy Susan with washers, motor mount), M4 × 16 + nuts × 6, M3 × 8 × 4 (motor), M5 × 10 + T-nuts × 3 (socket, cross clamp × 2) + 1 (lamp).

## 3D parts

| Part | Source |
|---|---|
| Rim segments, M4 motor mount, arm segment, cross clamp (LAR-08a–e) | `tools/cad/parts.py` — measure the bearing first (no published holes) |
| NEMA 17 | [STEP](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) [P40] |

## Results

(fill in)
