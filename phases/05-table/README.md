# 05 · Table (M3)

$22.38 · total so far $253.36 / $500

[Design](design.md) · [Parts list](bom.csv) · [3D files](3d/)

## M15 · Table axis built

Sample table turns on its post without wobble. · ~1 wk

**M15.1 Build**

- [ ] Order phases/05-table/bom.csv
- [ ] Post with two 608s, 100T pulley, belt, motor
- [ ] **Done:** Turns ±180°, no visible wobble.

## M16 · Table homes and repeats

M3 returns to the same spot every time. · ~1 wk

**M16.1 Home and tune**

- [ ] Home flag at −180°, swatch clamp
- [ ] machine.yaml: installed_phase 5
- [ ] 20 return moves
- [ ] **Done:** Returns within 0.1°.

[Sources](../../REFERENCES.md): G33 · H11 · H16 · H17 · H26 · H37 · H41 · P40 · P41 · P42 · P43
