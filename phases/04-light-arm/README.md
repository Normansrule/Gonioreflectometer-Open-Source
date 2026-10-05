# 04 · Light arm (M4)

$45.40 · total so far $230.98 / $500

[Design](design.md) · [Parts list](bom.csv) · [3D files](3d/)

## M13 · Ring drive built

Light arm turns smoothly on the ring. · ~1 wk

**M13.1 Build**

- [ ] Measure the lazy Susan, model the belt rim
- [ ] Fit belt, idlers, motor, arm
- [ ] **Done:** Arm turns 20–340° by hand, no binding.

## M14 · Light arm homes and repeats

M4 returns to the same spot every time. · ~1 wk

**M14.1 Home**

- [ ] Home flag at 20°, over-travel switch beyond it
- [ ] machine.yaml: installed_phase 4
- [ ] **Done:** opengonio home finds the flag 10/10 times.

**M14.2 Tune**

- [ ] Set gear_ratio from the measured rim
- [ ] bash scripts/e4.sh test; 20 return moves
- [ ] **Done:** Returns within 0.1°.

[Sources](../../REFERENCES.md): R1 · G10 · N15 · N47 · H2 · H11 · H16 · H17 · H18 · H26 · P40 · P42 · P43 · P44 · M1 · M2 · M3
