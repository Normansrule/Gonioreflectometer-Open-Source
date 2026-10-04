# Gonioreflectometer-Open-Source — OpenGantry Lite

A **$500, fully open-source tabletop gonioreflectometer** that measures how real materials reflect
light and turns them into Unreal / Unity materials — then grows, phase by phase, into a photo-based
3D scanner. A scaled-down, printable descendant of the Stanford Spherical Gantry.

> **Status:** Phase 1 design. Power module fully specified; other modules are scoped and waiting their turn.
> Progress lives in [GitHub milestones](../../milestones) and [`ROADMAP.md`](ROADMAP.md).
> Onshape document: _link added at milestone M0.2_.

## What it does at each phase

| Phase | The machine can… | Cap | Milestone |
|---|---|---:|---|
| 1 | measure in-plane reflectance (camera A1 + light A2) | $300 | M1 |
| 2 | output calibrated BRDF fits as game-engine materials | $75 | M2 |
| 3 | measure full isotropic BRDF (light azimuth ring A3) | $45 | M3 |
| 4 | measure anisotropic materials, rotate objects (turntable A4) | $35 | M4 |
| 5 | 3D-scan objects (photogrammetry + photometric stereo) | $30 | M5 |
| 6 | fit spatially varying reflectance on scanned objects | $0 | M6 |
| Pro | stretch features from research rigs (adaptive sampling, multi-light, spectral) | — | M7 |

## Budget at a glance (approximate, checked 2026-10-04)

| Path | Total | vs $500 |
|---|---:|---|
| Parts exactly as briefed | $658.71 | over |
| Budget substitutes | $517.29 | over |
| **Budget + consumables you already own** | **$478.15** | **under, $21.85 spare** |

Details and the decision you need to make: [`docs/05-budget-and-sourcing.md`](docs/05-budget-and-sourcing.md).
Line-item BOM: [`bom/master_bom.csv`](bom/master_bom.csv) → per-module CSVs in [`bom/modules/`](bom/modules/).

## Repository layout

```
hardware/<module>/     8-section module docs, Onshape notes, STEP (cad/) and 3MF (print/) exports
electronics/           power architecture, harness list
firmware/klipper/      printer.cfg for the SKR Mini E3 V3 (manual_steppers, 1 unit = 1 degree)
software/              Python package `opengantry`: gantry, camera, calib, hdr, plans, brdf, scan, svbrdf, export
data/                  power-budget inputs
docs/                  overview, BRDF theory, power budget, interfaces, decisions, licensing, OSHWA, Onshape, safety
bom/                   master BOM (source of truth), generated summary and module CSVs
tools/                 bom_check.py, power_budget.py, roadmap.py
.github/               milestones.yml (roadmap source), CI, templates
```

## Quick start (software, no hardware needed)

```bash
cd software && pip install -e ".[dev]" && python -m pytest -q
opengantry check-pose A1=12 A2=12          # collision model: is this pose safe?
opengantry --dry-run move A1=45 A2=45      # prints the Klipper G-code for a specular pose
python ../tools/bom_check.py                # budget per phase
python ../tools/power_budget.py --check     # final-machine power headroom
```

## Start here

1. [`docs/00-project-overview.md`](docs/00-project-overview.md) — machine, coordinate frame, build-once layout
2. [`docs/01-theory-brdf.md`](docs/01-theory-brdf.md) — what we measure and why the calibration works
3. [`docs/02-power-budget.md`](docs/02-power-budget.md) — final-machine power budget
4. [`hardware/power/README.md`](hardware/power/README.md) — the first module, complete
5. [`docs/03-architecture-interfaces.md`](docs/03-architecture-interfaces.md) — bolt pattern, drill map, connectors, Pi pins

## Licences

Hardware **CERN-OHL-S-2.0** · software **GPL-3.0-or-later** · documentation **CC BY-SA 4.0**.
Vendor CAD is linked, never redistributed. See [`docs/06-licensing.md`](docs/06-licensing.md) and
[`LICENSE`](LICENSE). Working toward OSHWA certification ([`docs/07-oshwa-certification.md`](docs/07-oshwa-certification.md)).

## Safety

24 V at up to 5 A, moving arms and a bright LED. Read [`docs/09-safety.md`](docs/09-safety.md) and each
module's section 8 before building.
