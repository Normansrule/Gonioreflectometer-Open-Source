# Roadmap

Goal-oriented milestones. Each item is a GitHub issue with a checklist; each phase is a GitHub
milestone whose progress bar fills as issues close. Generated from `.github/milestones.yml` by
`python tools/roadmap.py --write-md` — edit the YAML, not this file.

| Milestone | Goal | Cap | Items |
|---|---|---:|---:|
| M0 - Design baseline | Architecture, interfaces and budget agreed before buying. | — | 2 |
| M1 - Phase 1: In-plane gonioreflectometer | Fixed camera, light arm M4 and table M3 work from the laptop and the buttons; both axes repeat within 0.1 deg; the mirror peak appears at M3 = M4/2. | $350 | 8 |
| M2 - Phase 2: Calibrated BRDF and game materials | A fitted swatch rendered in Unreal/Unity matches a photo under the same light angle. | $74 | 7 |
| M3 - Phase 3: Isotropic BRDF (add M2 tilt) | Full isotropic scan of one swatch runs unattended with the collision model active. | $23 | 3 |
| M4 - Phase 4: Anisotropic BRDF and SVBRDF (add M1 spin) | Brushed metal highlight follows M1; per-pixel SVBRDF of a textured swatch. | $23 | 3 |
| M5 - Phase 5: Multispectral | Eight-band reflectance of a colour target matches its reference trend; polarized capture separates specular. | $30 | 2 |
| M6 - Phase 6: Scanning, SVBRDF maps, release | Object scanned with M1/M2 in front of the fixed camera; textures render in-engine; project public and OSHWA-ready. | $0 | 3 |
| M7 - Stretch: research-grade upgrades | Upgrades from published rigs without breaking the low-cost build. | — | 3 |

## M0 - Design baseline

**Goal:** Architecture, interfaces and budget agreed before buying.

### M0.1 — Confirm parts already owned and approve proposed caps

- [ ] Mark owned consumables (Stock candidate) in bom/master_bom.csv
- [ ] Approve proposed caps (docs/budget.md)
- [ ] python tools/bom_check.py --strict passes
- [ ] **Acceptance:** Buy-all total within $500 and every proposed cap.

### M0.2 — Freeze interfaces and start the Onshape document

- [ ] Review docs/architecture.md
- [ ] Create public Onshape doc with OG globals
- [ ] REF zero-point Part Studio with OG-40 mate connectors
- [ ] Print tolerance coupon, set #clear
- [ ] Link Onshape doc in README
- [ ] **Acceptance:** Globals match docs/architecture.md; #clear measured.


## M1 - Phase 1: In-plane gonioreflectometer

**Goal:** Fixed camera, light arm M4 and table M3 work from the laptop and the buttons; both axes repeat within 0.1 deg; the mirror peak appears at M3 = M4/2.

### M1.1 — Power module

- [ ] Order PWR lines
- [ ] Confirm jack/rocker cutouts from datasheets
- [ ] Print box and lid
- [ ] Build protection perfboard per netlist
- [ ] Wire 18 AWG, XT30 female on box
- [ ] Run T1-T10, fill acceptance_log.csv
- [ ] Export STEP + 3MF
- [ ] **Acceptance:** T1-T10 pass.

### M1.2 — Controller module (E4 + Pico hub + buttons)

- [ ] Order CTL lines
- [ ] Flash FluidNC (installer.fluidnc.com), upload config.yaml
- [ ] Flash MicroPython + pico-hub/main.py
- [ ] Print case and button panel
- [ ] Wire buttons, flags, J4
- [ ] Test USB, WiFi and BT links
- [ ] Run C1-C8
- [ ] **Acceptance:** C1-C8 pass.

### M1.3 — Base and frame

- [ ] Cut 600 x 600 base, drill full drill map
- [ ] Tee nuts, feet, level
- [ ] Camera outrigger + post
- [ ] Print protractor scales
- [ ] **Acceptance:** Ring footprint and table post concentric within 0.5 mm.

### M1.4 — Light arm M4 (ring)

- [ ] Measure lazy Susan, model sub-plate/top plate/belt rim
- [ ] Belt drive with printed idlers on 608s
- [ ] Home flag at 20 deg, roller switch at ~16 deg in e-stop chain
- [ ] Set gear_ratio from measured rim
- [ ] $HX homes; moves 20-340 deg
- [ ] **Acceptance:** M4 repeatability <= 0.1 deg (camera mirror test).

### M1.5 — Sample table M3

- [ ] Centre post with 2 x 608 spindle
- [ ] 100T pulley, belt, motor mount
- [ ] Home flag at -180 deg
- [ ] Vertical swatch clamp
- [ ] **Acceptance:** M3 repeatability <= 0.1 deg (ChArUco pose test).

### M1.6 — Fixed camera

- [ ] L-arm mount, 16 mm lens, f/8 aperture stop
- [ ] v4l2-ctl -l: confirm manual exposure and WB
- [ ] Lock exposure/gain/WB from opengonio.camera
- [ ] Align optical axis to zero point (crosshair)
- [ ] **Acceptance:** Zero point within 0.5 mm of image centre.

### M1.7 — White light source

- [ ] Confirm COB stock (CXA1304 or CXM-4)
- [ ] Housing, collimation tube, aperture
- [ ] NLDD-350H on E4 HE0, M62/M63 P0
- [ ] COB case <= 70 C after 30 min
- [ ] **Acceptance:** Light toggles from laptop and LIGHT button; <= 70 C.

### M1.8 — Phase 1 integration

- [ ] opengonio plan mirror --theta 20/40/60 on the mirror tile
- [ ] Record specular peak positions -> axis offsets
- [ ] In-plane scan of paper and plastic swatches
- [ ] Button-only run: HOME, NEXT, LIGHT, PAUSE, STOP
- [ ] Tag v0.2-phase1
- [ ] **Acceptance:** Peak within 0.5 deg of M3 = M4/2 before calibration; repeatability <= 0.1 deg.


## M2 - Phase 2: Calibrated BRDF and game materials

**Goal:** A fitted swatch rendered in Unreal/Unity matches a photo under the same light angle.

### M2.1 — Enclosure

- [ ] Dowel frame + drape, vents clear
- [ ] Stray-light test
- [ ] **Acceptance:** Stray light < 0.1 % of PTFE signal.

### M2.2 — Calibration kit

- [ ] PTFE, mirror tile, balls, ChArUco on glass
- [ ] Printed holders
- [ ] **Acceptance:** Re-seat 5x within 0.2 mm.

### M2.3 — HDR from UVC frames

- [ ] Exposure ladder
- [ ] Debevec response + merge
- [ ] Validate on a step target
- [ ] **Acceptance:** Linear within 2 % over 1000:1.

### M2.4 — Geometric calibration + per-pixel directions

- [ ] ChArUco intrinsics
- [ ] Axis offsets from mirror peaks
- [ ] Light position from chrome balls
- [ ] Per-pixel wi/wr maps
- [ ] **Acceptance:** Angle error <= 0.2 deg.

### M2.5 — Radiometric calibration

- [ ] PTFE reference <= 60 deg
- [ ] Reciprocity check (swap light/view)
- [ ] **Acceptance:** Reciprocity mismatch <= 5 %.

### M2.6 — GGX fit + engine export

- [ ] Lambert + GGX + Schlick fit with energy check
- [ ] Export Unreal / Unity material
- [ ] **Acceptance:** RMS log error <= 10 %; imports without edits.

### M2.7 — Phase 2 milestone test

- [ ] Photo vs render at 3 light angles
- [ ] **Acceptance:** Side-by-side documented.


## M3 - Phase 3: Isotropic BRDF (add M2 tilt)

**Goal:** Full isotropic scan of one swatch runs unattended with the collision model active.

### M3.1 — Tilt yoke M2

- [ ] Yoke on table flange
- [ ] Drive, home flag at -90
- [ ] installed_phase: 3
- [ ] **Acceptance:** M2 repeatability <= 0.1 deg; zero point unchanged.

### M3.2 — Isotropic planner

- [ ] Grid in (theta_i, theta_r, delta_phi) -> (M4, M3, M2)
- [ ] Skip unmeasurable/unsafe poses
- [ ] Dry-run
- [ ] **Acceptance:** Zero violations.

### M3.3 — Phase 3 milestone test

- [ ] Unattended isotropic scan
- [ ] Fit vs Phase 2
- [ ] **Acceptance:** Completes unattended; consistent fit.


## M4 - Phase 4: Anisotropic BRDF and SVBRDF (add M1 spin)

**Goal:** Brushed metal highlight follows M1; per-pixel SVBRDF of a textured swatch.

### M4.1 — Spin platter M1

- [ ] Platter on yoke
- [ ] Home flag on TH0
- [ ] installed_phase: 4
- [ ] **Acceptance:** M1 repeatability <= 0.1 deg.

### M4.2 — Anisotropic + SVBRDF fit

- [ ] Anisotropic GGX
- [ ] Per-pixel fit with per-pixel directions
- [ ] **Acceptance:** Brushing direction within 5 deg.

### M4.3 — Phase 4 milestone test

- [ ] Brushed metal at 8 M1 angles
- [ ] **Acceptance:** Highlight stretch follows M1.


## M5 - Phase 5: Multispectral

**Goal:** Eight-band reflectance of a colour target matches its reference trend; polarized capture separates specular.

### M5.1 — LED bank + polarizers

- [ ] Choose 8 bands, build ring
- [ ] NLDD-350H on E4 GPIO4, ULN2803A from Pico
- [ ] Polarizer film on lamp and lens
- [ ] **Acceptance:** Each band on/off from laptop; crossed polarizers cut mirror highlight >= 20x.

### M5.2 — Spectral calibration

- [ ] Per-band PTFE reference
- [ ] Colour target check (borrowed)
- [ ] **Acceptance:** Band ratios repeat within 3 %.


## M6 - Phase 6: Scanning, SVBRDF maps, release

**Goal:** Object scanned with M1/M2 in front of the fixed camera; textures render in-engine; project public and OSHWA-ready.

### M6.1 — Photogrammetry with the rotating stage

- [ ] Pose priors from M1/M2
- [ ] COLMAP / Meshroom
- [ ] Scale from ChArUco
- [ ] **Acceptance:** Test block within 0.5 mm.

### M6.2 — On-object SVBRDF maps

- [ ] Base colour, roughness, metallic, normal maps
- [ ] Engine export
- [ ] **Acceptance:** Render matches a capture.

### M6.3 — Open-source release

- [ ] docs/licensing.md checklist
- [ ] Make repo + Onshape public
- [ ] Apply for OSHWA
- [ ] Tag v1.0
- [ ] **Acceptance:** Public; OSHWA UID in README.


## M7 - Stretch: research-grade upgrades

**Goal:** Upgrades from published rigs without breaking the low-cost build.

### M7.1 — Adaptive sampling

- [ ] Prototype RGL-EPFL-style adaptive sampling [R15]
- [ ] **Acceptance:** Same fit with >= 3x fewer captures.

### M7.2 — Filter-wheel or mono camera multispectral

- [ ] Compare with LED bands; follow [R1] channel design
- [ ] **Acceptance:** Documented comparison.

### M7.3 — Validation vs MERL / RGL data

- [ ] Measure a shared material [R13][R16]
- [ ] **Acceptance:** Published comparison.

