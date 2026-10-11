# Rules for AI agents working in this repo

## After every change
1. `make all` (build, checks, tests, paper, exports). Fix failures before committing.
2. CAD changed: `make parts` and/or `make cad` first (STEP/STL, pictures, clash check, paper figures).
3. Commit everything, including `paper/build/opengonio.pdf` and `exports/`.
4. `make ci` (replays the GitHub checks in a clean clone of HEAD); fix and recommit until it passes.
5. Push (`bash scripts/update.sh "msg"` or `git push`).

## Sources of truth (edit these; the rest is generated)
- Parts: `phases/*/bom.csv` → README bill of materials, PARTS.md, budget, paper tables.
- References: `REFERENCES.md` → `paper/references.bib`, wiki Bibliography + appendices, README list.
- Steps: `.github/phases.yml` → stage checklists, issues.
- Wiki text: `wiki/src/*.md` → `wiki/*.md` (`make build`); publish with `bash scripts/publish_wiki.sh`.
- Geometry: `tools/cad/parts.py`, `tools/cad/bought.py`.

## Writing
- Fewest words that stay precise. Tables and lists over prose.
- Write acronyms out once, with the short form in parentheses.
- Citations: APA 7 in wiki and paper (`[@ID]` in wiki sources, `\parencite{ID}` in LaTeX). Stage docs keep `[ID]`.
- Never invent links, part numbers, prices or results; mark unknowns `[TBD]`.

## Constraints
- Parts from Digi-Key, Amazon or Adafruit; cheapest that meets the spec; prices checked on the store page.
- No soldering, drilling, sawing or crimping. Printed parts: black ABS, enclosed printer.
- Budget cap: `HARD_CAP` in `tools/bom_check.py`.

## Other software
- Never edit `exports/` by hand; edit the source named in `exports/README.md`.
- Edits made in Word, Google Docs or Overleaf go back into `paper/opengonio.tex` (or `wiki/src/`) by hand.
