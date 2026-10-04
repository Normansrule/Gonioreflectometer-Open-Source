# Onshape workflow

One public document **OpenGonio**.

| Tab | Contents |
|---|---|
| `OG globals` (Variable Studio) | `#clear`, `#wall`, `#og40`, `#m4_clear`, `#ins_m3_d`, `#cam_d` 350, `#light_d` 300, `#zero_h` 150, `#ring_r` 140 |
| `REF – Zero point` | origin = zero point, base top at Z = −`#zero_h`, mate connectors on every OG-40 pad |
| `PWR`, `CTL`, `FRM`, `CAM`, `LAR`, `TBL`, `LSR`, `TLT`, `SPN`, `MSK` | one Part Studio per module (prefix = BOM ID) |
| `VENDOR – envelopes` | vendor STEP (private copy) or datasheet envelopes |
| `ASM – <module>`, `ASM – Phase N` | assemblies; interference check every phase |

Rules: shared dimensions only in `OG globals`; print the tolerance coupon first and set `#clear`; release = Onshape version `M1.x-<module>-v1` → STEP to `hardware/<module>/cad/`, 3MF to `hardware/<module>/print/`.
