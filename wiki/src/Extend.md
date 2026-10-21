# Tweak and extend

Everything is generated from a few source files. Edit the source, run `make all`, then `make publish m="…"`.

| To change… | Edit | Then |
|---|---|---|
| a step, a milestone, a pass number | `.github/phases.yml` (`do`, `verify`, `fail`, `record`, `time`, `wait`, `needs`) | `make all` |
| mark a step done | — | `make done id=M05.1` (closes the issue, refreshes ticks and figures) |
| add a stage / milestone / step | `python tools/new.py stage 18-name "Title"` · `milestone 04-light-arm "Title" "Goal"` · `step M14 "Title"` | fill the TODO lines, `make all` |
| agree / have / ordered / swap / skip a part, what you paid | [PARTS.md]({{REPO}}/PARTS.md) (also on GitHub in the browser) | `make` locally, or nothing: *parts-sync* runs on GitHub |
| a part's spec, price or link; a new part | `phases/NN/bom.csv` (or `python tools/new.py part …`) | `make all` (budget is re-checked) |
| a printed part's size | the PARAMETERS block or the part function in `tools/cad/parts.py` | `make parts` |
| a printed part, by hand | import `phases/NN/3d/*.step` into Onshape, export STEP + STL back | `make all` |
| machine geometry, ports, gear ratios (what you **built**) | `software/config/machine.yaml` | `make all` (simulator numbers update too) |
| angle offsets, dark level, white reference (what you **measured**) | written by `opengonio calibrate …` into `software/config/calibration.yaml` | commit it |
| lamp warm-up, drift limit | `lights.white.warmup_s` (machine.yaml) · `drift_limit_pct` (calibration.yaml) | — |
| what you paid | `Paid USD` column in `phases/NN/bom.csv` | `make` prints *spent so far* |
| mark a stage done | — | `make release s=06` (tag `v0.6` + every STEP/STL as a zip on GitHub) |
| motor board settings | `tools/grblhal_settings.py` → `firmware/grblhal/settings.txt` | `make build`, then `bash scripts/controller.sh settings` |
| buttons, screen, spectral sensor | `firmware/hub/main.py` | `bash scripts/hub.sh` |
| a reference | `python tools/new.py ref G "Source" "Used for (phase NN)"`; cite as `[G53]({{REPO}}/REFERENCES.md)` | `make all` |
| how-to text for a stage | `phases/NN/design.md` (how) · `research.md` (why) | `make check` |
| a test result | `phases/NN/test.csv` | commit |

Rules that keep it simple:
- **Generated, don't edit by hand:** `phases/NN/README.md`, `phases/NN/3d/README.md`, the tables between `<!-- … -->` markers in this README, `docs/assets/*.svg`, `docs/assets/steps/*.svg`, `docs/machine.js`, `docs/plan.js`, `.github/progress.json`, `optics.md`, `power_budget.md`, `deck-map.svg`.
- **Specs vs decisions:** `bom.csv` holds what a part is (spec, price, link); `PARTS.md` holds what you decided (status, paid, note). `make` copies decisions into `bom.csv` (`Status`, `Own`, `Paid USD`), so edit those three only in `PARTS.md`. Zip updates never overwrite your `PARTS.md`.
- **Math on GitHub:** `make check` rejects TeX macros GitHub refuses (operator-name and new-command macros); write `\mathrm{atan2}`.
- **Built vs measured:** `machine.yaml` holds design values; `calibration.yaml` holds measured ones with dates. `verify` warns when a calibration is older than 30 days.
- **Simulator = software:** the web simulator reads `docs/machine.js`, generated from `machine.yaml`; `make check` fails if they differ.
- **Test without hardware first:** a code change must keep `make sim` at `ALL PASS`.
- **Go back:** `git checkout v0.6` returns to the state when stage 06 passed (`git checkout main` to return).
- **Every step has a time and a pass number:** `make check` rejects a step without Do / Verify, with a malformed `time`, or with `TODO` left in it.
- **Milestone IDs never change** once published: new ones get the next free number, so GitHub issue history stays attached.
- **`make check`** lists every problem in one place: milestone format, parts lists, the budget cap, reference IDs, broken links, machine and calibration config.
- **Measurement data** goes in `data/<job>/`: `manifest.json`, `curve.csv` and `spectral.csv` are committed; images stay local.
