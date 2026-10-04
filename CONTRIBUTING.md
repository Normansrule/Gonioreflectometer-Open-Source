# Contributing

1. Pick an issue in a milestone ([ROADMAP.md](ROADMAP.md)); one module per PR, branch `m<id>-<module>`.
2. Modules follow the 8-section template (purpose/interfaces · BOM · Onshape · assembly · wiring · software · acceptance test · safety).
3. Edit `bom/master_bom.csv` only; every price needs a check date and a reference ID in `REFERENCES.md`.
4. **Credit every source** in `REFERENCES.md` and cite its ID where used. Never invent a link; write "not confirmed".
5. Run before pushing:
   ```bash
   python tools/bom_check.py --strict && python tools/power_budget.py --check
   python tools/make_assets.py && python tools/roadmap.py --write-md
   cd software && python -m pytest -q
   ```
