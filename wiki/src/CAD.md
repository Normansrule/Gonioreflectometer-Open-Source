# 3D files and making parts

![All printed parts]({{REPO}}/docs/assets/parts.png?raw=true)

**Every part has a 3D model in the repo** — list and status per part: [cad/README.md]({{REPO}}/cad/README.md).

| Folder | What |
|---|---|
| `phases/NN/3d/` | printed parts: **STEP** (Onshape: Insert → Import, editable solid) and **STL** (slicer) |
| [`cad/bought/`]({{REPO}}/cad/bought) | dummy models of every bought part at true size (motors, boards, bearings, belts, camera, lens…) |
| [`cad/open/`]({{REPO}}/cad/open) | real open-licence models (Adafruit MIT, KiCad CC-BY-SA + exception) |
| [`cad/assembly/opengonio_assembly.step`]({{REPO}}/cad/assembly) | the whole machine, one STEP: import this into Onshape to start |
| `cad/vendor/` (not committed) | real vendor models: `bash scripts/get_cad.sh` |
| [`cad/PRINT.md`]({{REPO}}/cad/PRINT.md) | print list: how many of each, size vs build volume, ≈ grams of ABS (core ≈ 2.7 kg, deck tiles ≈ 1.4 kg) |

**Putting it together:** the [build book]({{REPO}}/docs/build.html) shows every modelled part in order, one step per page ([PDF]({{REPO}}/exports/build-book.pdf)); the order is `docs/assembly.yaml`, the words come from the stage checklists.

`make cad` regenerates dummies + assembly and runs `make cad-check` (no collisions across every axis' travel, clear sight lines from both cameras and the lamp to the sample); `make cad-zip` packs every STEP into `dist/opengonio-cad.zip` (one Onshape import).


- **Starter geometry, generated:** `python tools/cad/parts.py` (CadQuery; parameters at the top). Print the [tolerance coupon]({{REPO}}/phases/00-plan/3d/PLAN-01_tolerance_coupon.stl) first and set `CLEAR` / `M2_TAP`.
- **Vendor models:** `bash scripts/get_cad.sh` → `cad/vendor/` (not committed); browser-only downloads: `bash scripts/get_cad.sh --from /mnt/c/Users/aleks/Downloads`.
- **Deck:** [deck map]({{REPO}}/phases/03-frame/deck-map.svg) (tiles and every pilot; `PLACE` in `tools/cad/parts.py` is the source) · [frame design]({{REPO}}/phases/03-frame/design.md).
- **Wiring:** [power netlist]({{REPO}}/phases/01-power/design.md) · [controller pins]({{REPO}}/phases/02-controller/design.md) · [standalone wiring]({{REPO}}/phases/15-standalone/design.md).
- **Onshape:** [set-up steps]({{REPO}}/phases/00-plan/design.md#onshape-set-up) — import the STEP files, edit, export STEP + STL back.
