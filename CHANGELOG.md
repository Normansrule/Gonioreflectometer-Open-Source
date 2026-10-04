# Changelog

## [0.1.0] - 2026-10-04
### Added
- Repository structure, licences (CERN-OHL-S-2.0, GPL-3.0-or-later, CC BY-SA 4.0).
- Final-machine power budget (`data/power_loads.yaml`, `tools/power_budget.py`).
- Master BOM for all six phases with spec / budget / own-stock paths (`tools/bom_check.py`).
- Phase 1 Power module: complete 8-section documentation and acceptance log.
- Interface standards: coordinate frame, OG-40 bolt pattern, base drill map, connector registry, Pi pin map.
- Klipper `printer.cfg` (A1/A2 active, A3/A4 ready), idle sleep macros.
- Python package `opengantry`: config-driven axes, kinematics, collision model, Moonraker client,
  power manager, AS5600 reader, BRDF models; 31 tests.
- Goal-oriented roadmap: 8 milestones, 39 checklist issues (`.github/milestones.yml`).
