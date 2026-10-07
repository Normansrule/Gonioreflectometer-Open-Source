# 08 · Design

- Yoke (TLT-07a) on the table drum (OG-40, 4 × M4 × 16 self-tap), arms along ±Y so the tilt axis is square to the camera at M3 = 0. Arms carry a 608 each at the tilt axis, 150 mm above the plywood = the zero point.
- Cradle (TLT-07c) turns on two **M8 × 35 stub bolts** (TLT-05): head outside → (100T pulley on the +Y arm, 9.4 mm spacer on the other) → 1 mm shim → 608 inner race → 6.8 mm spacer → M8 nut trapped in the cradle. One nut per side clamps the whole stack: nothing to cut, no flats.
- Drive 5 : 1, 280 mm belt. The motor hangs on the inner face of the pulley-side arm, 75.6 mm above the axis, shaft out through the arm (slots = belt tension); everything that turns with the table stays within r ≈ 90 of its axis (pulley and bolt head outside the arm), so the table can turn ±180°.
- The cradle floor holds the pancake spin motor (stage 09); home flag (TBL-07b) on a cradle end block at −90°, endstop on the arm, lead to E4 Z-MIN.
- Checked in CAD: no part of the cradle, platter or spin motor touches the yoke over M2 = −90…90°, and nothing turning with the table touches the table motor, the lazy Susan or the M4 motor over M3 = 0…360°.

Fasteners: M8 × 35 × 2 + nuts, M4 × 16 × 4 (OG-40, self-tap), M3 × 8 × 8 (motor, flag; self-tap into 2.7 mm holes).

## 3D parts

| Part | Source |
|---|---|
| Yoke, 100T pulley, cradle (TLT-07a–c) | `tools/cad/parts.py` (`YOKE_SEAT`, `TILT_BELT_C`) |
| Spacers and shims (TBL-07f) | printed with the table set |
| NEMA 17 | [STEP](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) [P40] |

## Results

(fill in)
