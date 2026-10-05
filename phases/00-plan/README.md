# 00 · Plan

<img src="../../docs/assets/architecture.svg" width="100%" alt="Plan">

[Research](research/) · [Design](design/) · [3D files](3d/)

## M01 · Read and decide

Know what you are building and what to buy. · ~1 wk

**M01.1 Read**

- [ ] bash scripts/get_papers.sh
- [ ] Read R1 sections 2–4 (papers/open)
- [ ] Try the simulator: docs/index.html
- [ ] **Done:** You can explain M1–M4 and θi/θr.

**M01.2 Shopping list**

- [ ] Set Own = Y for parts you have, in phases/*/bom/bom.csv
- [ ] python3 tools/bom_check.py --strict
- [ ] **Done:** Total ≤ $500.

## M02 · Software runs on the laptop

Simulator, tests and dry-run moves work before any hardware. · ~1 wk

**M02.1 Install**

- [ ] cd software && python3 -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'
- [ ] python -m pytest -q
- [ ] **Done:** All tests pass.

**M02.2 Dry run**

- [ ] opengonio check-pose M4=60 M3=30
- [ ] opengonio --dry-run move M4=80 M3=25
- [ ] opengonio scan demo --out demo
- [ ] **Done:** G-code printed; demo PLY opens in Blender.

## M03 · CAD and printer ready

Printed parts will fit first time. · ~1 wk

**M03.1 Onshape**

- [ ] Create the document and OG globals (design/onshape.md)
- [ ] **Done:** Globals match design/architecture.md.

**M03.2 Tolerance coupon**

- [ ] Print phases/00-plan/3d/print/PLAN-01_tolerance_coupon.stl in PETG
- [ ] Set CLEAR and INSERT in tools/cad/parts.py from the hole that fits; python tools/cad/parts.py
- [ ] **Done:** Coupon fits.

[Sources](../../REFERENCES.md): R1 · R2 · R5 · R6 · R7 · R8 · R24 · R27 · R30 · R47 · R50 · R56 · R63 · R64 · R68 · R69 · R79 · R80 · S3 · S18 · S20 · G1 · G2 · G6 · G7 · G33 · G35 · G36 · G38 · T1 · T4 · T11 · T17 · T35 · T38 · T40 · V19 · V20 · N6 · N12 · N14 · N50 · H28 · H29 · H35 · H44 · H56 · H57 · H58 · P1 · P15 · P17 · P23 · P31 · P32 · C3 · K1 · K5 · K19 · L1 · L4 · L9 · L18 · E5
