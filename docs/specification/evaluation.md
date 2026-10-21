# OpenGonio evaluation specification

What the instrument is meant to measure, how each claim is backed, and the tests that move a claim from "designed" to
"measured". Every number in the README, paper and wiki should carry one of the evidence levels below.

## Evidence levels

| Level | Meaning | Example |
|---|---|---|
| **NOMINAL** | Datasheet or design value, not checked here | lamp umbra radius 16.2 mm from the lamp geometry |
| **MODELED** | Computed from the geometry or a physical model in this repository | field of view 124 × 98 mm at 350 mm (thin lens) |
| **SIMULATED** | Reproduced end-to-end by the simulator (`make sim`), which uses the same code paths as hardware | mirror zero error found and removed |
| **MEASURED** | Measured on a built machine, with the run folder (manifest + images) kept as evidence | — (nothing yet) |
| **NOT CHARACTERIZED** | No evidence; the feature exists in software or design only | AS7341 driver on hardware |

No OpenGonio has been built yet: **nothing is MEASURED**. Nothing is safety-certified.

## First target

A laptop-controlled, white-light gonioreflectometer for flat samples up to 50 × 50 mm: in-plane (M4 + M3, stages 04–07),
then isotropic out-of-plane (M2, stage 08) and anisotropic (M1, stage 09). Output per pose: angles, raw and linearised
signal over the valid region, BRDF in 1/sr against a reflectance standard, the region's size and angular acceptance
(`opengonio curve`). The 3D scanner, the spectral sensor and the colour kit come after this target.

## Quantities and definitions

| Quantity | Definition (code) |
|---|---|
| Pose | requested true angles M4 M3 M2 M1 (deg, after calibration offsets) and the controller-reported pose; a run is invalid if they differ by more than 0.01° (`verify.py`) |
| Signal plane | mean(R, G, B) of the 8-bit RGB frame (`imageio.signal_plane`); greyscale frames are used as they are |
| Linear signal | per-pixel camera-response correction max(c − dark, 0)^γ, applied to every pixel before averaging (`Calibration.linear_array`) |
| Valid region | pixels on the sample (centre 80 % of its side) inside 90 % of the lamp umbra, sample facing camera and lamp (`roi.sample_roi`); poses with < 25 mm² are not used |
| Angular acceptance | full cone angle of viewing and incidence directions over the valid region (MODELED: ≈ 5–7° at the poses checked) |
| BRDF | f_r = (S / S_white) × (ρ_white / π) × cos θ_i,white / cos θ_i, with S the linear region means at the same exposure (`Calibration.brdf_linear`); none for θ_i ≥ 89° |
| Spectral reading | AS7341 raw counts F1–F8 (8 visible bands, 415–680 nm) + clear + NIR = 10 values, 0–65535 |

## Capabilities and evidence

| Capability | Level | Evidence / test that would make it MEASURED |
|---|---|---|
| Axis step resolution (M4 0.0047°, M3/M2 0.0225°, M1 0.028° per microstep) | MODELED | gear ratios × microsteps in `machine.yaml` |
| Repeatability ≤ 0.1° per axis | NOT CHARACTERIZED | laser-and-wall test `opengonio repeat` (M14, M16, M25, M27) |
| Position trust (end position = request, alarms clear homing) | SIMULATED | `tests/test_audit.py` M01, M02; bench: stall a motor, check the refusal |
| Mirror zero (M3 offset) | SIMULATED | `capture mirror` + `calibrate mirror` (M19) |
| Camera response (γ) | SIMULATED | `capture linearity`, fit r² ≥ 0.99 over ≥ 4× exposure (M22) |
| Absolute BRDF vs PTFE | SIMULATED | `capture white` + `calibrate white` with a certified ρ (M23) |
| Lamp drift within the limit (2 % per run, `drift_limit_pct`) | SIMULATED | reference shots start/end of every run (`verify`) |
| Angular acceptance ≈ 5–7° | MODELED | `roi.py`; measure the umbra (M18.1) and recompute |
| Field of view 124 × 98 mm, depth of field | MODELED | `tools/optics.py`; photograph a ruler at the zero point (M17) |
| No mechanical interference over the travel | MODELED | `make cad-check`: every axis sweep + 256 mixed poses, computation errors fail |
| AS7341 spectral readings | NOT CHARACTERIZED | firmware is register-level from the datasheet, untested (M29.2) |
| Colour LED bank (MSK) | **BLOCKED** | driver circuit unsafe as designed (see stage 10 design.md); do not energize |
| 3D visual hull | SIMULATED | `scan demo`; real scan of the reference cube (M33) |
| Photometric stereo normals | SIMULATED | far-field light model: direction error up to atan(r/d), not corrected; needs the blocked LED bank |
| Standalone station runs unattended | NOT CHARACTERIZED | station tests are simulated; M42 is the first real run |
| Run time ≈ 6 h per charge, 18–24 V pack charged to 24.0 V over USB-C | MODELED | `tools/power_budget.py` from listing values; stage 01 tests T3, T4, T13, T15 |
| Electrical safety | NOT CHARACTERIZED | no certification; power from a ready-made Li-ion pack with its own protection board, a 3.15 A fuse and a CC/CV charging module set to 24.0 V / 1.0 A (no mains in the machine); e-stop, wiring and charge temperature checked by the stage 01/02 steps only |

## Uncertainty budget (BRDF, white light)

Each component, its model, and its status. Combined uncertainty is **not stated** until the MEASURED rows exist.

| Component | Effect on f_r | Model / how it is obtained | Status |
|---|---|---|---|
| Reflectance standard ρ | relative, 1:1 | certificate value and its uncertainty; datasheet ρ is recorded as "assumed" (`--rho-source`) | NOT CHARACTERIZED |
| Camera response γ | non-linear in signal | linearity fit residual (r²), repeat with a second exposure series | SIMULATED |
| Dark level | offset | `capture dark` with every light confirmed off | SIMULATED |
| Exposure mismatch sample vs white | relative, 1:1 | refused (`brdf_problems`): same exposure required | enforced |
| Lamp drift | relative over a run | reference shots; run fails above `drift_limit_pct` | enforced; size NOT CHARACTERIZED |
| Angle error δθ_i | ∝ tan θ_i · δθ_i (cos θ_i term) + lobe slope | repeatability (above) and mirror zero | NOT CHARACTERIZED |
| Angular acceptance (≈ 5–7°) | smooths sharp lobes | per-pose spread in `curve.csv`; compare mirror peak width | MODELED |
| Non-uniform lighting in the region | bias | region restricted to 90 % of the umbra; measure the spot profile (M18.1) | NOMINAL |
| Stray light / ambient | offset | dark box (M21), dark frames | NOT CHARACTERIZED |
| Clipped pixels | invalid, not biased | rejected (region returns no value) | enforced |
| Polarization of lamp and camera | material dependent | not modelled | NOT CHARACTERIZED |
| Sample flatness and centring | geometry error | centring check M17.4 | NOT CHARACTERIZED |

## Operating modes and safety boundaries

| Mode | Who drives the controller | Link | Notes |
|---|---|---|---|
| Laptop, USB-C | `opengonio` on the laptop | USB-C serial to the SKR Pico (grblHAL) | default; one program at a time owns the port; no network link (the SKR Pico has no WiFi) |
| Standalone | `opengonio station` on the Pi Zero | SKR Pico USB-C through the Pi's USB hub | buttons + OLED (ESP32-S3 hub on the Pi UART); images stay on the Pi until `opengonio pull` |
| Laptop, WiFi (FluidNC boards only) | `opengonio` on the laptop | FluidNC telnet (port 23) | only with `controller.firmware: fluidnc`; **unauthenticated**: private network only, never forward the port, change the fallback hotspot password |

In every mode the e-stop cuts motor power in hardware. Where the ESP32-S3 hub is read (button panel, standalone station),
`POWER 0` stops the job, switches the lamp off and clears homing, STOP switches the lamp off, and `POWER 1` re-initialises
the drivers and waits for HOME; nothing resumes by itself. A laptop `opengonio capture` does not read the buttons
between poses: stop it with Ctrl+C (lamp off, run marked aborted) or the e-stop (the next move fails its end-position
check). grblHAL starts in Alarm until homed
(`$22` init lock; bench check in stage 04, with the fallback if a build needs every axis homed). PAUSE stops a panel plan after the pose in progress. The LIGHT button is ignored while a job runs. Only one host may be
connected to the controller at a time: the software does not arbitrate between two.

## Acceptance tests (first target)

| Test | Pass when | Milestone |
|---|---|---|
| Homing and repeatability | 20 returns within 0.1° on the wall (`opengonio repeat`) | M14, M16 |
| Mirror test | peak at M3 = M4/2 within 0.5° after `calibrate mirror` | M19 |
| Camera response | r² ≥ 0.99, γ recorded with its run | M22 |
| Absolute BRDF | PTFE measured as a sample returns ρ/π within the stated budget | M23 |
| Run integrity | `opengonio verify` PASS (complete, valid data, drift within limit) and, for absolute values, `calibrated: true` | every run |
