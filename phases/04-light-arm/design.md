# 04 · Design

- 12 in lazy Susan (ID ~160 mm) held by the 4 ring-scale segments (FRM-09c): their inner wall centres the bottom plate, a lip presses it onto the deck, 2 × M2 × 10 each into the deck pilots. No holes to find in the steel.
- GT2 belt CA-glued teeth-out on a 6 mm band around 8 printed rim segments (7 × LAR-08a + the arm segment LAR-08c; bolted with M2 × 12 + a wide printed washer + nut where a slot meets a top-plate hole, CA-glued elsewhere) → 24 : 1 with a 20T pinion (set `gear_ratio` from the measured rim). No lips on the band: the pinion's 16 mm flanges pass above and below it. The belt's pitch line sits on `RIM_R` (back 0.38 mm inside it), and the pinion centre is `RIM_R` + 6.37 mm.
- M4 motor at 0° (+X), inside the arm's keep-out: its mount sits outside the lazy Susan (M2 slots over two deck pilots, reachable from above) and cantilevers a 56 mm plate over the rim, narrow enough for the arm to pass at the travel ends; the pinion meshes the rim belt directly (no idlers). Radial slots set the mesh.
- Arm: the arm segment (one of the 8 rim positions) holds the printed 200 mm upright bar (LAR-08f) at r = 136.8 mm, **36 mm beside the beam line** (15.3° ahead of the lamp): an upright on the beam line would shade the sample. Cross clamp (at the upright's upper pilot) → horizontal 200 mm bar (LAR-08g) parallel to the beam line, 14 mm beside it → lamp clamp offset 14 mm so the beam axis passes through the zero point at 150 mm; lamp 300 mm out. M4 range 20–324° (the upright reaches the motor's keep-out at 339°).
- `make cad-check` proves it: no part collides in any axis position, and nothing blocks the camera, scan camera or lamp sight lines to the sample.
- Home flag at 20°; roller over-travel switch (screw terminals) just beyond: the red motor-power wire passes through its COM–NC on the way to the SKR Pico [R1].

Fasteners (all FRM-06 M2 except the motor face): M2 × 10 + washers × 8 (ring scales), M2 × 12 + washers × 2 (motor mount), M2 × 12 + nuts × ~4 (rim), M2 × 16 × 3 (socket, cross clamp × 2) + 1 (lamp), M3 × 8 × 4 (motor, FRM-07).

## 3D parts

| Part | Source |
|---|---|
| Rim segments, M4 motor mount, arm segment, cross clamp (LAR-08a–e) | `tools/cad/parts.py` — measure the bearing first (no published holes) |
| NEMA 17 (17HS4401, 38 mm) | repo model `cad/bought/LAR-02_nema17_17hs4401.step` (no maker STEP for the SIMAX pack) [P58] |

## Results

(fill in)
