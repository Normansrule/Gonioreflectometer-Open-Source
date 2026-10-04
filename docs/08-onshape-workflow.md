# Onshape workflow

One public Onshape document, **OpenGantry Lite**, linked from the README.

## Structure

| Tab | Type | Contents |
|---|---|---|
| `OG globals` | Variable Studio | `#clear`, `#wall`, `#og40`, `#m4_clear`, `#ins_m3_d`, `#radius_work` (300), `#sample_h` (150), `#cam_tower_y` (175), `#light_tower_y` (140), `#ring_stack_h`, `#tt_spacer_h` |
| `REF – Coordinate frame` | Part Studio | origin = measurement centre, base top at Z = −`#sample_h`, mate connectors for every OG-40 pad |
| `PWR – Power box` | Part Studio | see `hardware/power/README.md` §3 |
| `CTL – Controller case`, `FRM – Base and frame`, `CAR – Camera arm`, … | Part Studio per module | one per module, same prefixes as the BOM IDs |
| `VENDOR – envelopes` | Part Studio | imported vendor STEP (kept private to your copy if the licence forbids sharing) or datasheet envelopes |
| `ASM – <module>` | Assembly per module | module + its vendor parts, interference-checked |
| `ASM – Phase N` | Assembly per phase | the whole machine at each phase; the collision study uses these |

## Rules

- Every dimension that another module depends on lives in `OG globals`, never typed into a sketch.
- Every custom part's name starts with its BOM ID prefix (`OG-PWR-ENC`, `OG-CAR-HUB`, …).
- Use mate connectors on the OG-40 pattern so modules snap to the base in assemblies.
- Release process per module: Onshape **Version** named `M1.1-power-v1` → export STEP to
  `hardware/<module>/cad/` and 3MF to `hardware/<module>/print/` → commit with the same tag.
- Print a tolerance coupon (holes and pegs at ±0.1 mm steps) first and set `#clear` from it.

## Importing purchased parts

1. Download the vendor STEP from the BOM link (or build the envelope from the listed dimensions).
2. Onshape → Import → into the `VENDOR – envelopes` Part Studio.
3. Do not make the document public with redistributable-restricted vendor geometry inside; keep a
   private copy with vendor parts and a public copy with envelopes, or link instead.
