# Onshape set-up

One public document, **OpenGonio**.

| Tab | Contents |
|---|---|
| `OG globals` (Variable Studio) | `#clear` `#wall` `#og40` `#m4_clear` `#ins_m3_d` `#cam_d`=350 `#scan_d`=650 `#light_d`=300 `#zero_h`=150 `#ring_r`=140 |
| `REF – Zero point` | origin at the sample surface; mate connectors on every OG-40 pad |
| One Part Studio per phase | name parts with the BOM ID (e.g. `PWR-18`) |
| `ASM – Phase NN` | assembly per phase; run interference check |

Rules: shared sizes only in `OG globals`. Print the tolerance coupon first, set `#clear`. Release = Onshape version → STEP + 3MF into that phase's `3d/`.
