# 04 · Design

- 12 in lazy Susan (ID ~160 mm) screwed straight to the plywood through its own holes, each screw through a printed 4 mm washer (FRM-09g) so it can't poke through.
- GT2 belt glued teeth-out on 8 printed rim segments (bolted with M4 × 12 + nuts where a slot meets a top-plate hole, CA-glued elsewhere) → 24 : 1 with a 20T pinion (set `gear_ratio` from the measured rim).
- M4 motor at 0° (+X), inside the arm's keep-out: its mount sits outside the lazy Susan and cantilevers the motor over the rim; the pinion meshes the rim belt directly (no idlers). Radial slots set the mesh.
- Arm: bracket (50 mm wide, slotted, M4 + nuts) on the top plate at r ≈ 140 → vertical 2020 → cross clamp → horizontal 2020 at lamp height; lamp 300 mm from the zero point.
- Home flag at 20°; roller over-travel switch (screw terminals) just beyond: the red 24 V wire passes through its COM–NC on the way to the E4 [R1].

Fasteners: #8 × 5/8 Type 17 wood screws × 10 (lazy Susan with washers, motor mount), M4 × 12 + nuts × 6, M3 × 8 × 4 (motor), M5 × 10 + T-nuts × 3.

## 3D parts

| Part | Source |
|---|---|
| Rim segments, M4 motor mount, arm bracket, cross clamp (LAR-08a–e) | `tools/cad/parts.py` — measure the bearing first (no published holes) |
| NEMA 17 | [STEP](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) [P40] |

## Results

(fill in)
