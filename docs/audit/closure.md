# Technical audit: closure report

Audit of the software at commit c19a847 (31 findings, F01–F31). This report gives the closure status of each finding,
the test that shows it, and what still needs a built machine. The audit documents themselves are not in the repository;
where the audit grouped findings, the scope below follows that grouping (F24–F25 and F28–F31 are closed as groups).

Status values: **FIXED AND VERIFIED** (code or doc changed; a test or check failed before and passes now) ·
**TESTED AND NOT DEFECTIVE** · **DEFERRED WITH TECHNICAL JUSTIFICATION** · **BLOCKED BY MISSING EVIDENCE** (needs hardware).

Nothing here was run on hardware: no firmware was flashed, no circuit energized, nothing published.

## Findings

| ID | Finding (scope) | Status | Evidence (software/tests unless noted) |
|---|---|---|---|
| F01 | `verify` passed empty runs, text files named .png, bad spectral readings, out-of-range poses | FIXED AND VERIFIED | test_audit V01–V04, hash/plan/status tests; schema-2 fields required (review follow-up) |
| F02 | Camera settings not confirmed; three different camera interfaces | FIXED AND VERIFIED | one `configure()` with read-back (`camera/uvc.py`), test F02 v4l2 read-back. On the real B0433: BLOCKED BY MISSING EVIDENCE (M17) |
| F03 | Acquisition not transactional: lamp left on, failed saves ignored, manifest lost on error | FIXED AND VERIFIED | test_audit C01–C04, M05, S02 |
| F04 | Run folders reused/overwritten; no run id, plan count, status or file hashes | FIXED AND VERIFIED | `runrecord.py` schema 2; exclusive-dir and claim tests |
| F05 | Position trusted without checking where the controller ended | FIXED AND VERIFIED | end-position check after every move/home + `G4 P0` sync; test M01 |
| F06 | Alarm / reset did not clear homing; controller allowed motion unhomed | FIXED AND VERIFIED (software) · firmware part BLOCKED BY MISSING EVIDENCE | test M02; `must_home: true` with a stage-04 bench check and a documented fallback if a FluidNC build keeps the alarm until every axis is homed |
| F07 | Hub events (STOP, POWER) dropped during sensor reads; SPEC replies unvalidated | FIXED AND VERIFIED | test M03 ×2; firmware echoes the request id (`OpenGonio-hub 3`) |
| F08 | Power events handled differently per mode; no modes / network safety description | FIXED AND VERIFIED | `gantry/safety.py`; test M04, power/STOP lamp-off test; [evaluation spec](../specification/evaluation.md) "Operating modes" |
| F09 | Selectable-colour LED circuit unsafe (NLDD-350H minimum output ≥ 6 V vs one LED) | FIXED AND VERIFIED (blocked) | light refused in code and config, raw `send M62 P1` refused; BOM, design.md, step M30 and power budget (2.1 W) updated; test F09. Redesign: DEFERRED WITH TECHNICAL JUSTIFICATION (optional kit, not part of the first target) |
| F10 | No evaluation specification / evidence levels | FIXED AND VERIFIED | [docs/specification/evaluation.md](../specification/evaluation.md); `make check` links |
| F11 | Calibration not bound to the run: editing calibration.yaml changed old results | FIXED AND VERIFIED | snapshot with id in every manifest; `curve --recalibrate` writes a separate labelled file; test R02 |
| F12 | Mixed pixel conventions (BGR/RGB, grey) | FIXED AND VERIFIED | `imageio` RGB + signal plane mean(R,G,B); test R01 (OpenCV and built-in reader) |
| F13 | Linearisation applied to the mean instead of per pixel | FIXED AND VERIFIED | `region_mean(linear=...)`; test R01 per-pixel |
| F14 | Region of interest ignored sample edges and lamp spot; no angular acceptance | FIXED AND VERIFIED (model) | `roi.py`, `curve.csv` columns; test F14. Umbra radius is NOMINAL: measure in M18.1 (BLOCKED BY MISSING EVIDENCE) |
| F15 | AS7341 described as "10-band" | FIXED AND VERIFIED | "8 visible bands + clear + NIR" in BOM, PARTS.md, wiki, design.md |
| F16 | Reference not checked (ρ, clipping, exposure, stale response); no uncertainty budget | FIXED AND VERIFIED | test R03 ×2, stale-white test; budget table in the spec. Combined uncertainty: BLOCKED BY MISSING EVIDENCE |
| F17 | Station 3D-scan job wrote a different format from `scan run` | FIXED AND VERIFIED | station writes `scan.json` via `scan_meta`; test F17 |
| F18 | Scanner used nominal intrinsics, no distortion, calibration not copied into the run | FIXED AND VERIFIED | run keeps its own calibration copy; distortion in `project`; test F18 matches OpenCV `projectPoints` |
| F19 | Hull from too few views; unbounded memory | FIXED AND VERIFIED | coverage gate + voxel limit; test F19 |
| F20 | Empty / inconsistent calibration accepted | FIXED AND VERIFIED | `solve_ax_yb` and `_calib` checks; test S03 |
| F21 | Fit output without provenance or validation | FIXED AND VERIFIED | `fit.json` provenance + holdout RMS; test F21 |
| F22 | CAD check read a failed Boolean as "no clash" | FIXED AND VERIFIED | CLEAR / INTERSECTION / COMPUTATION_ERROR (exit 2), sight lines too; test_cad_poses |
| F23 | Tilt sweep used the opposite sign; spin platter not moved; single-axis sweeps only | FIXED AND VERIFIED | `tools/cad/poses.py` tested against the kinematics; spin group; 256 mixed poses; `make cad-check`: 0 clashes, 0 errors |
| F24–F25 | Packaging: version in two places; installed package had no config and skipped the depth-of-field check | FIXED AND VERIFIED | dynamic version, packaged `machine.yaml` (kept current by `make build`, test), config search order, `opengonio init`; `scripts/wheel_check.sh` passes in a clean venv |
| F26 | CI only warned on stale generated files; no wheel or CAD job | FIXED AND VERIFIED | strict freshness in `ci.yml` and `ci_local.sh`; `wheel` and `cad` jobs |
| F27 | `e4.sh` masked a failed move and flashed "latest" FluidNC; `station.sh` deleted the station's config | FIXED AND VERIFIED | pinned `FLUIDNC_VERSION` (v3.9.9), conditional M3 move; station update keeps `machine.yaml` + `calibration.yaml`; test F27 (text checks only) |
| F28–F31 | README without status, evidence or cost scope; web page: 390 px overflow, no text H1, CDN-only KaTeX, motion, no "offline" label, keyboard/ARIA, no text pose | FIXED AND VERIFIED | README Status + Cost scope; `docs/index.html` checked in headless Chromium at 390 and 1280 px with the network blocked and reduced motion: no overflow, H1, 11 equations rendered from bundled KaTeX 0.16.9, keyboard orbit, live pose text, no console errors |

## Verification run

| Check | Result |
|---|---|
| `pytest -q software` | 157 passed (before the audit work: 99) |
| `opengonio sim-demo` | ALL PASS |
| `make cad-check` (interference) | shown pose, 4 axis sweeps, 256 mixed poses: 0 clashes, 0 computation errors |
| `scripts/wheel_check.sh` | wheel 0.7.0 installs in a clean venv, `init`, sim-demo ALL PASS |
| `make build`, `make check` | OK; generated files current |
| Independent review | separate agent reviewed the diff; its two high findings (stale white reference after a new γ; homing under `must_home`) and the medium ones are fixed or documented above, with tests |

## Needs a built machine (BLOCKED BY MISSING EVIDENCE)

FluidNC `must_home` behaviour with single-axis homing (stage 04) · camera read-back on the B0433 (M17) · lamp umbra
radius and spot profile (M18.1) · repeatability, mirror zero, camera response, absolute BRDF and its uncertainty (M14–M23) ·
AS7341 driver (M29.2) · standalone station unattended run (M42) · electrical safety (no certification).
