# Licensing

| What | Licence | File |
|---|---|---|
| Hardware (Onshape models, STEP/3MF exports, drawings, PCB/perfboard layouts, BOM) | CERN-OHL-S-2.0 (strongly reciprocal) | `LICENSES/CERN-OHL-S-2.0.txt` |
| Software and firmware configuration | GPL-3.0-or-later | `LICENSES/GPL-3.0-only.txt` (the GPL v3 text) |
| Documentation, images, data | CC BY-SA 4.0 | `LICENSES/CC-BY-SA-4.0.txt` |

Each file carries an `SPDX-License-Identifier` line where the format allows.

## GPL-3.0 vs MIT for the software

| | GPL-3.0 | MIT |
|---|---|---|
| Anyone can use, modify, sell | yes | yes |
| Modified versions that are distributed must publish source | **yes** | no |
| Can be folded into closed products | no | yes |
| Fits CERN-OHL-S hardware | same "share alike" spirit | mismatched: hardware must stay open, software need not |
| Klipper (which we configure) | GPL-3.0 | — |

**Chosen: GPL-3.0-or-later.** The hardware licence is strongly reciprocal, Klipper itself is GPL-3.0,
and the goal is that improved versions of the scanner stay open. Choose MIT only if you want companies
to embed the Python package in closed products — that is a project-owner decision, so it is recorded
here rather than changed silently.

## Vendor CAD

STEP files from Raspberry Pi, BIGTREETECH, Pololu, StepperOnline, Mean Well, Same Sky, LEDiL and
community authors are **not** committed. Their terms vary and many forbid redistribution. The BOM's
`STEP file link` column links to the source; `hardware/<module>/cad/VENDOR_CAD.md` lists what to
download and where to put it locally (`hardware/<module>/cad/vendor/`, ignored by git).
