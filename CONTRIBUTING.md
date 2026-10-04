# Contributing

Thanks for helping build an open gonioreflectometer.

## Workflow

1. Pick or open an issue under a milestone (see `ROADMAP.md`). One module per pull request.
2. Branch `m<id>-<module>` (for example `m1.2-controller`).
3. Every module follows the 8-section template: purpose/interfaces → BOM → Onshape → assembly →
   wiring → firmware/software → acceptance test → safety.
4. Hardware changes: update the Onshape document, export STEP to `hardware/<module>/cad/` and 3MF to
   `hardware/<module>/print/`, and edit `bom/master_bom.csv` (never the generated module CSVs).
5. Run before pushing:
   ```bash
   python tools/bom_check.py
   python tools/power_budget.py --check
   cd software && python -m pytest -q
   ```
6. Interfaces in `docs/03-architecture-interfaces.md` are frozen; changing one needs a design-change issue.

## Rules

- **Never invent a link.** If you cannot confirm a STEP file exists, write "not confirmed" and give
  datasheet dimensions.
- Prices are approximate and carry the date checked.
- Do not commit vendor CAD; link it.
- New files carry an `SPDX-License-Identifier` (CERN-OHL-S-2.0, GPL-3.0-or-later or CC-BY-SA-4.0).
- Contributions are accepted under the licence of the part of the repository they touch.
