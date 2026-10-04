# Roadmap

Goal-oriented milestones. Each item is a GitHub issue with a checklist; each phase is a GitHub
milestone whose progress bar fills as issues close. Generated from `.github/milestones.yml` by
`python tools/roadmap.py --write-md` — edit the YAML, not this file.

| Milestone | Goal | Cap | Items |
|---|---|---:|---:|
| M0 - Design baseline | Architecture, interfaces and budget agreed before buying. | — | 2 |
| M1 - Phase 1: In-plane gonioreflectometer | Fixed camera, light arm M4 and table M3 work from the laptop and the buttons; both axes repeat within 0.1 deg; the mirror peak appears at M3 = M4/2. | $347 | 8 |
| M2 - Phase 2: Calibrated BRDF and game materials | A fitted swatch rendered in Unreal/Unity matches a photo under the same light angle. | $73.5 | 7 |
| M3 - Phase 3: Isotropic BRDF (add M2 tilt) | Full isotropic scan of one swatch runs unattended with the collision model active. | $22.5 | 3 |
| M4 - Phase 4: Anisotropic BRDF and SVBRDF (add M1 spin) | Brushed metal highlight follows M1; per-pixel SVBRDF of a textured swatch. | $22.5 | 3 |
| M5 - Phase 5: Multispectral and polarization | Eight-band reflectance of a colour target repeats within 3 %; crossed polarizers separate specular from diffuse. | $30 | 4 |
| M6 - Phase 6: 3D photo scanner | A 40 mm printed cube scans to within 0.5 mm on every edge, and a 1:43 model car mesh imports cleanly into Blender. | $4.5 | 8 |
| M7 - Phase 7: On-object appearance | The scanned model car rendered in-engine matches a gantry photo under the same light. | $0 | 4 |
| M8 - OpenGonio Studio (laptop app) | Every workflow (BRDF scan, multispectral, 3D scan) runs from one laptop app or the physical buttons, with no terminal. | — | 3 |
| M9 - Release and certification | Public, documented, OSHWA-certified open hardware with a v1.0 release. | — | 3 |
| M10 - Stretch: research-grade upgrades | Upgrades from published rigs without breaking the low-cost build. | — | 4 |

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
- [ ] Camera outrigger + post; mark the 350 mm (BRDF) and 650 mm (scan) positions
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
- [ ] Spindle hub accepts scan-kit risers (Phase 6)
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


## M5 - Phase 5: Multispectral and polarization

**Goal:** Eight-band reflectance of a colour target repeats within 3 %; crossed polarizers separate specular from diffuse.

### M5.1 — LED bank on the 40 deg mast

- [ ] Choose 8 bands (~420-660 nm)
- [ ] Print LED ring + 40 deg mast on the light arm
- [ ] NLDD-350H on E4 GPIO4, ULN2803A from Pico GP8-15
- [ ] Collision model includes the mast
- [ ] **Acceptance:** Each band on/off from laptop and buttons; mast clears the camera at M4 = 20 deg.

### M5.2 — Polarizers

- [ ] Film in the lamp slot
- [ ] Rotatable lens disc with index marks
- [ ] **Acceptance:** Crossed polarizers cut the mirror highlight >= 20x.

### M5.3 — Spectral calibration

- [ ] Per-band PTFE reference
- [ ] Per-band light direction (mast elevation) in kinematics
- [ ] Colour target check (borrowed)
- [ ] **Acceptance:** Band ratios repeat within 3 %.

### M5.4 — Phase 5 milestone test

- [ ] Multispectral in-plane BRDF of two paints that look alike in RGB
- [ ] **Acceptance:** Paints separated in at least one band.


## M6 - Phase 6: 3D photo scanner

**Goal:** A 40 mm printed cube scans to within 0.5 mm on every edge, and a 1:43 model car mesh imports cleanly into Blender.

### M6.1 — Scan kit hardware

- [ ] Print risers 60/40/20/0 mm (delta = 60 - riser), nest, 650 mm camera stop, outrigger end foot
- [ ] Buy putty; print the ChArUco mat
- [ ] Check object sphere r = 55 clears the light arm in ASM - Phase 6
- [ ] **Acceptance:** Putty holds a 100 g object at 80 deg elevation for 3 turns (test S3).

### M6.2 — Scan-mode camera

- [ ] Slide to 650 mm, f/8 stop, refocus, lock
- [ ] opengonio scan calibrate: ChArUco intrinsics + distortion + measured camera pose
- [ ] Set scan.calibration in machine.yaml; keep the BRDF-mode (350 mm) profile
- [ ] **Acceptance:** Reprojection RMS <= 0.5 px (test S1).

### M6.3 — Scan planner and known poses

- [ ] opengonio scan plan: rings 0/20/40/60/80 deg, 144 views
- [ ] Object-frame poses from M1/M2/M3 + platter offset
- [ ] Joint fit of camera pose + board placement (AX = YB) at 12 poses
- [ ] **Acceptance:** Kinematic pose within 0.2 deg / 0.3 mm of solvePnP (test S2).

### M6.4 — Capture run

- [ ] opengonio scan run: lamp at M4 = 30 deg, crossed polarizers
- [ ] Locked exposure; frames saved as img_0000.jpg ...
- [ ] Buttons: START runs the scan, PAUSE/STOP work mid-scan
- [ ] scan.json with poses and settings
- [ ] **Acceptance:** 144 sharp frames, no motion blur, unattended.

### M6.5 — Visual hull preview

- [ ] Empty-platter background pass (scan run --background)
- [ ] Silhouettes by background differencing
- [ ] Voxel carving with known poses, clipped at the support plane
- [ ] PLY preview in under 1 min on the laptop
- [ ] **Acceptance:** 40 mm cube hull edges within 1 mm (test S4).

### M6.6 — Photogrammetry with pose priors

- [ ] Export COLMAP model (OPENCV camera when calibrated)
- [ ] run_colmap.sh: feature_extractor -> sync-ids -> point_triangulator -> patch_match_stereo (CUDA) -> stereo_fusion -> poisson_mesher
- [ ] Optional bundle_adjuster + model_aligner to the kinematic camera centres
- [ ] No CUDA: Meshroom / OpenMVS / RealityScan
- [ ] Mesh units = mm
- [ ] **Acceptance:** Dense mesh of the cube, no manual alignment.

### M6.7 — Photometric stereo detail

- [ ] PS stations every 60 deg of M1 at 30 deg elevation
- [ ] LED bank band, 6 M4 positions (non-coplanar via the 40 deg mast)
- [ ] Light positions refined with chrome balls; near-light directions + 1/r^2 from the hull or mesh
- [ ] Merge normals into a normal map on the mesh
- [ ] **Acceptance:** Matte sphere median normal error <= 5 deg (test S6).

### M6.8 — Phase 6 milestone test

- [ ] Scan the 40 mm cube, measure edges in the mesh
- [ ] Scan a 1:43 car (flip once for the underside, merge)
- [ ] Import PLY/OBJ/glTF into Blender
- [ ] **Acceptance:** Cube edges 40.0 +/- 0.5 mm; car imports without repair (tests S5, S7).


## M7 - Phase 7: On-object appearance

**Goal:** The scanned model car rendered in-engine matches a gantry photo under the same light.

### M7.1 — Project captures onto the mesh

- [ ] UV-unwrap the mesh
- [ ] Per-texel visibility over all views and light positions
- [ ] Per-pixel directions from the known poses
- [ ] **Acceptance:** Each texel has >= 20 valid observations.

### M7.2 — Per-texel SVBRDF fit

- [ ] Initialise from Phase 2-4 swatch fits
- [ ] Fit base colour, roughness, metallic, clear-coat; normals from PS
- [ ] Energy and reciprocity checks
- [ ] **Acceptance:** Held-out images reproduced within 10 % RMS.

### M7.3 — Engine export

- [ ] glTF 2.0 with PBR textures
- [ ] Unreal and Unity material setup
- [ ] **Acceptance:** Imports in both engines without edits.

### M7.4 — Phase 7 milestone test

- [ ] Gantry photo vs in-engine render, same light pose
- [ ] **Acceptance:** Side-by-side published in docs.


## M8 - OpenGonio Studio (laptop app)

**Goal:** Every workflow (BRDF scan, multispectral, 3D scan) runs from one laptop app or the physical buttons, with no terminal.

### M8.1 — Local web UI

- [ ] Connect USB / WiFi / Bluetooth
- [ ] Live camera view with exposure lock
- [ ] Jog, home, light controls
- [ ] Collision preview from the simulator code
- [ ] **Acceptance:** Full Phase 1 run from the browser.

### M8.2 — Workflow presets

- [ ] BRDF swatch, multispectral, 3D scan presets
- [ ] Buttons map to the selected preset
- [ ] Progress and ETA
- [ ] **Acceptance:** Each preset runs unattended from START.

### M8.3 — Data management

- [ ] Session folders with scan.json
- [ ] Resume after STOP / e-stop
- [ ] Export bundle (images, model, materials)
- [ ] **Acceptance:** Interrupted scan resumes without re-capturing done poses.


## M9 - Release and certification

**Goal:** Public, documented, OSHWA-certified open hardware with a v1.0 release.

### M9.1 — Documentation pass

- [ ] All modules have 8 sections
- [ ] Build video or GIF per phase
- [ ] STEP + 3MF for every printed part
- [ ] **Acceptance:** A new builder completes Phase 1 from the docs alone.

### M9.2 — Make public + OSHWA

- [ ] docs/licensing.md checklist
- [ ] Repo and Onshape public
- [ ] Apply for OSHWA certification
- [ ] **Acceptance:** OSHWA UID in README.

### M9.3 — v1.0 release

- [ ] Tag v1.0
- [ ] Release notes with measured accuracy numbers
- [ ] **Acceptance:** Release published.


## M10 - Stretch: research-grade upgrades

**Goal:** Upgrades from published rigs without breaking the low-cost build.

### M10.1 — Adaptive BRDF sampling

- [ ] Prototype RGL-EPFL-style adaptive sampling [R15]
- [ ] **Acceptance:** Same fit with >= 3x fewer captures.

### M10.2 — Mono camera + filter wheel multispectral

- [ ] Compare with LED bands; follow the channel design of [R1]
- [ ] **Acceptance:** Documented comparison.

### M10.3 — Space carving with photo-consistency

- [ ] Extend the visual hull to space carving [S7]
- [ ] **Acceptance:** Concavities recovered on a test bowl.

### M10.4 — Validation vs MERL / RGL data

- [ ] Measure a shared material [R13][R16]
- [ ] **Acceptance:** Published comparison.

