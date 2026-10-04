# Roadmap

Goal-oriented milestones. Each item is a GitHub issue with a checklist; each phase is a GitHub
milestone whose progress bar fills as issues close. Generated from `.github/milestones.yml` by
`python tools/roadmap.py --write-md` — edit the YAML, not this file.

| Milestone | Goal | Cap | Items |
|---|---|---:|---:|
| M0 - Design baseline | Repository, licences, interfaces and budget path agreed before anything is bought. | — | 3 |
| M1 - Phase 1: In-plane gonioreflectometer core | Light and camera move in one plane; both axes home and repeat within 0.1 deg; a mirror shows its specular peak at the mirror angle. | $300 | 8 |
| M2 - Phase 2: Calibrated swatch BRDF and first game materials | A fitted swatch rendered in-engine matches a photo of the swatch under the same light angle. | $75 | 8 |
| M3 - Phase 3: Full isotropic gonioreflectometer (A3 light ring) | A full isotropic scan of one swatch completes unattended with the collision model active. | $45 | 4 |
| M4 - Phase 4: Anisotropic BRDF and motorised object rotation (A4) | A brushed-metal swatch shows its highlight stretching with turntable angle; A4 homes and repeats within 0.1 deg. | $35 | 3 |
| M5 - Phase 5: Photo-based 3D scanner | A scanned test block measures within 0.5 mm of its true size and a model car mesh imports cleanly into Blender. | $30 | 5 |
| M6 - Phase 6: On-object reflectance and open-source release | The model car rendered in-engine matches a gantry photo under the same light; the project is public and OSHWA-ready. | $0 | 4 |
| M7 - Stretch: OpenGantry Pro (advanced track) | Research-grade features inspired by the Stanford Spherical Gantry, X-Rite TAC7/PANTORA and RGL-EPFL, added without breaking the Lite build. | — | 4 |

## M0 - Design baseline

**Goal:** Repository, licences, interfaces and budget path agreed before anything is bought.

### M0.1 — Answer the three open questions (Pi model, own stock, budget path)

- [ ] Confirm Raspberry Pi 4 or Pi 5 (power budget assumes Pi 5 worst case)
- [ ] List consumables already owned (wire, perfboard, JST-XH, screws, inserts)
- [ ] Choose spec / budget / budget + own stock path (see docs/05-budget-and-sourcing.md)
- [ ] Update bom/master_bom.csv and re-run tools/bom_check.py
- [ ] **Acceptance:** bom/summary.md shows the chosen path within every phase cap and the $500 hard cap.

### M0.2 — Freeze interfaces: coordinate frame, OG-40, drill map, connector registry

- [ ] Review docs/03-architecture-interfaces.md
- [ ] Create the public Onshape document with the OG globals Variable Studio
- [ ] Model the REF coordinate-frame Part Studio with OG-40 mate connectors
- [ ] Print the tolerance coupon and set #clear
- [ ] Link the Onshape document from README.md
- [ ] **Acceptance:** Onshape document public, globals match docs/03, #clear measured.

### M0.3 — Approve the final-machine power budget

- [ ] Review docs/02-power-budget.md
- [ ] Confirm 120 W adapter and buck choice
- [ ] python tools/power_budget.py --check passes
- [ ] **Acceptance:** Headroom >= 25 % at peak, approved in the issue.


## M1 - Phase 1: In-plane gonioreflectometer core

**Goal:** Light and camera move in one plane; both axes home and repeat within 0.1 deg; a mirror shows its specular peak at the mirror angle.

### M1.1 — Power module

- [ ] Order PWR-01..PWR-18 (bom/modules/power.csv)
- [ ] Confirm jack, fuse-holder, rocker cutouts from datasheets; update Onshape variables
- [ ] Model and print the power box and lid
- [ ] Build the protection perfboard per the netlist
- [ ] Wire main path in 18 AWG, XT30s female on the box
- [ ] Run acceptance tests T1-T12, fill hardware/power/acceptance_log.csv
- [ ] Put measured buck efficiency into data/power_loads.yaml, re-run the budget
- [ ] Export STEP + 3MF, commit with tag M1.1-power-v1
- [ ] **Acceptance:** T1-T11 pass; buck efficiency >= 90 % or a recorded deviation issue.

### M1.2 — Controller module (Pi + SKR Mini E3 V3, fan-cooled case)

- [ ] Write the 8-section module README
- [ ] Order CTL lines
- [ ] Model and print the case with the 40 mm fan duct
- [ ] Flash Klipper (STM32G0B1, 8 KiB bootloader, USART2) and install Moonraker
- [ ] Wire UART (5 V not connected), J2/J3/J4, safe-shutdown button
- [ ] Apply config.txt block; verify /dev/ttyAMA0 and I2C buses
- [ ] DUMP_TMC answers for X and Y drivers
- [ ] Acceptance test
- [ ] **Acceptance:** Klipper Ready over UART; opengantry status answers; e-stop drops the MCU and recovery works.

### M1.3 — Base and frame (with Phase 3/4 interfaces pre-drilled)

- [ ] Write the 8-section module README
- [ ] Cut the 600 x 600 base, drill the full drill map incl. ring footprint
- [ ] Install tee nuts and feet; level the base
- [ ] Cut 2020: two towers, centre post, two arm spars, two crossbars
- [ ] Print tower feet, OG-40 adapters, centre-post turntable-height spacer
- [ ] Check: tower pivot axes coaxial and through the centre within 0.5 mm
- [ ] **Acceptance:** Pivot axes coaxial within 0.5 mm at the centre (string line / dial test).

### M1.4 — Camera arm A1

- [ ] Write the 8-section module README
- [ ] Model hub, 100T pulley, elbow, counterweight cage, home flag
- [ ] Assemble on 608 bearings, tension belt
- [ ] Balance with counterweight (arm stays put at 45 deg with motor off)
- [ ] Mount TCST2103 at 85 deg and AS5600 on the axle
- [ ] Home + move tests; opengantry repeatability --axis A1
- [ ] **Acceptance:** 20-cycle repeatability max deviation <= 0.1 deg.

### M1.5 — Light arm A2 (ring-ready bracket + riser)

- [ ] Write the 8-section module README
- [ ] Same arm as A1; bracket on the OG-40 at r = 140 with the ring-stack riser
- [ ] Balance, endstop, encoder
- [ ] opengantry repeatability --axis A2
- [ ] **Acceptance:** 20-cycle repeatability max deviation <= 0.1 deg.

### M1.6 — Camera head

- [ ] Write the 8-section module README
- [ ] Model a head that fits both HQ (M12) and Camera Module 3
- [ ] Route the 500 mm CSI cable along the arm through the pivot
- [ ] Picamera2 RAW capture with locked exposure, gain, white balance, focus
- [ ] Aim: optical axis through the centre within 0.5 mm (crosshair target)
- [ ] **Acceptance:** RAW (DNG) captures at 4 elevations with the centre target within 0.5 mm of image centre.

### M1.7 — Light source (CRI-95 COB + constant-current driver)

- [ ] Write the 8-section module README
- [ ] Confirm CXM-4 95-CRI bin availability and the optic
- [ ] Model lamp housing with polarizer slot
- [ ] Wire NLDD-350H to SKR HE0 (on/off), SET_PIN test
- [ ] Thermal test: COB case <= 70 C after 30 min
- [ ] Flicker check: no banding in a short-exposure capture
- [ ] **Acceptance:** Lamp on/off from Klipper, case <= 70 C, no flicker bands.

### M1.8 — Phase 1 integration and milestone test

- [ ] Collision model check on hardware: approach the 9 deg minimum slowly
- [ ] Both axes: 20-cycle repeatability <= 0.1 deg
- [ ] Mirror on the stage: sweep A1 with A2 fixed at 20/40/60 deg; peak at A1 = A2
- [ ] Record arm angle offsets from the peak positions
- [ ] First in-plane reflectance curve of a paper and a plastic swatch
- [ ] Tag release v0.1-phase1
- [ ] **Acceptance:** Specular peak within 0.5 deg of the mirror angle (before calibration) at all three light angles.


## M2 - Phase 2: Calibrated swatch BRDF and first game materials

**Goal:** A fitted swatch rendered in-engine matches a photo of the swatch under the same light angle.

### M2.1 — Enclosure (blackout + flock where the camera looks)

- [ ] Write the module README
- [ ] Dowel frame + drape, vents clear
- [ ] Measure stray light: dark frame with lamp on, sample removed
- [ ] **Acceptance:** Stray light < 0.1 % of the PTFE signal at the same exposure.

### M2.2 — Calibration kit

- [ ] Write the module README
- [ ] Order PTFE, mirror, chrome balls
- [ ] Print holders
- [ ] Generate and print the ChArUco board, bond to glass
- [ ] **Acceptance:** All fixtures seat repeatably on the stage (re-seat 5x, < 0.2 mm).

### M2.3 — RAW + HDR capture (software/hdr)

- [ ] Exposure bracketing in Picamera2
- [ ] Dark-frame subtraction
- [ ] Linear HDR merge with saturation masks
- [ ] Unit tests on synthetic data
- [ ] **Acceptance:** Merged HDR linear within 2 % across a 1000:1 range on a step target.

### M2.4 — Geometric calibration (software/calib)

- [ ] ChArUco intrinsics
- [ ] Arm angle offsets from mirror peaks
- [ ] Light direction from chrome-ball highlights
- [ ] Measurement-centre check
- [ ] **Acceptance:** Angle error <= 0.2 deg after calibration (mirror re-test).

### M2.5 — Radiometric calibration

- [ ] PTFE reference at theta <= 60 deg
- [ ] Lamp falloff and camera response
- [ ] Reciprocity check: swap A1/A2
- [ ] **Acceptance:** Reciprocity mismatch <= 5 % on PTFE and a matte paint swatch.

### M2.6 — GGX fitting (software/brdf)

- [ ] In-plane sample storage format
- [ ] Lambert + GGX + Schlick fit
- [ ] Energy-conservation constraint
- [ ] Fit report plots
- [ ] **Acceptance:** RMS log-error <= 10 % on paint, plastic and rubber swatches.

### M2.7 — Unreal / Unity export (software/export)

- [ ] Map fit to metallic-roughness (roughness = sqrt(alpha))
- [ ] Export material JSON + textures
- [ ] Unreal and Unity import notes
- [ ] **Acceptance:** Materials import in both engines without manual edits.

### M2.8 — Phase 2 milestone test

- [ ] Photograph a swatch at a known light angle
- [ ] Render the fitted material in-engine at the same angles
- [ ] Side-by-side comparison in docs
- [ ] **Acceptance:** Mean colour difference in the highlight and diffuse regions visibly matches; numbers recorded.


## M3 - Phase 3: Full isotropic gonioreflectometer (A3 light ring)

**Goal:** A full isotropic scan of one swatch completes unattended with the collision model active.

### M3.1 — Light ring module A3

- [ ] Write the 8-section module README
- [ ] Measure the lazy Susan, model sub-plate/top plate/belt rim
- [ ] Belt drive with printed idlers on 608s
- [ ] Endstop + AS5600 on motor shaft
- [ ] Uncomment A3 in printer.cfg, installed_phase: 3
- [ ] **Acceptance:** A3 homes and repeats within 0.1 deg.

### M3.2 — Move the light arm onto the ring

- [ ] Remove the riser, bolt the bracket to the ring top plate
- [ ] Re-check pivot coaxiality and centre within 0.5 mm
- [ ] **Acceptance:** Mirror peak still at A1 = A2 with A3 = 0.

### M3.3 — Isotropic scan planner with collision model

- [ ] Plan grid in (theta_i, theta_r, delta_phi)
- [ ] Skip unsafe poses, order moves to minimise travel
- [ ] Dry-run on the CAD-measured geometry
- [ ] Update machine.yaml geometry from measurements
- [ ] **Acceptance:** Planner output has zero keep-out violations; dry-run passes.

### M3.4 — Phase 3 milestone test

- [ ] Unattended isotropic scan of one swatch
- [ ] Fit isotropic GGX, compare to Phase 2 in-plane fit
- [ ] **Acceptance:** Scan completes unattended, no collisions, fit consistent with Phase 2.


## M4 - Phase 4: Anisotropic BRDF and motorised object rotation (A4)

**Goal:** A brushed-metal swatch shows its highlight stretching with turntable angle; A4 homes and repeats within 0.1 deg.

### M4.1 — Turntable module A4

- [ ] Write the 8-section module README
- [ ] Hollow post top, spindle in 2 x 608, 80T pulley
- [ ] Height stage on M8 rod
- [ ] Endstop + AS5600 on spindle
- [ ] Uncomment A4, installed_phase: 4
- [ ] **Acceptance:** A4 homes and repeats within 0.1 deg; sample height unchanged from Phase 1.

### M4.2 — Anisotropic plans and fit

- [ ] Add absolute phi to sample storage
- [ ] Anisotropic GGX (alpha_x, alpha_y) fit
- [ ] Export anisotropy to engines
- [ ] **Acceptance:** Brushed-metal fit recovers the brushing direction within 5 deg.

### M4.3 — Phase 4 milestone test

- [ ] Brushed-metal swatch at 8 turntable angles
- [ ] Highlight stretch plot vs angle
- [ ] **Acceptance:** Highlight elongation follows turntable angle.


## M5 - Phase 5: Photo-based 3D scanner

**Goal:** A scanned test block measures within 0.5 mm of its true size and a model car mesh imports cleanly into Blender.

### M5.1 — Polarizer and fill-light kit

- [ ] Write the 8-section module README
- [ ] Film in lamp slot; servo polarizer wheel on camera head
- [ ] Second COB + NLDD on FAN2 behind diffuser
- [ ] Cross/parallel polarization test
- [ ] **Acceptance:** Crossed polarizers suppress the mirror highlight by >= 20x.

### M5.2 — Scanning mat and scan planner

- [ ] Generate and print the ChArUco mat
- [ ] Plan ~145 poses (turntable x camera elevations)
- [ ] Export poses as COLMAP priors
- [ ] **Acceptance:** Plan runs unattended; every image has a pose prior.

### M5.3 — Photogrammetry pipeline

- [ ] COLMAP with pose priors (RealityScan / Meshroom alternatives)
- [ ] Scale from the ChArUco mat
- [ ] Mesh cleanup and export
- [ ] **Acceptance:** Test block dimensions within 0.5 mm.

### M5.4 — Photometric stereo detail

- [ ] Capture with the moving light
- [ ] Normal map estimation
- [ ] Merge normals onto the mesh
- [ ] **Acceptance:** Fine surface detail visible that the photogrammetry mesh misses.

### M5.5 — Phase 5 milestone test

- [ ] Scan the test block, measure with calipers
- [ ] Scan a 1:43 model car, import into Blender
- [ ] **Acceptance:** Block within 0.5 mm; car mesh imports cleanly.


## M6 - Phase 6: On-object reflectance and open-source release

**Goal:** The model car rendered in-engine matches a gantry photo under the same light; the project is public and OSHWA-ready.

### M6.1 — Spatially varying BRDF fit

- [ ] Project images onto the Phase 5 mesh
- [ ] Initialise from swatch fits
- [ ] Fit base colour, roughness, metallic, normal, clear-coat per texel
- [ ] **Acceptance:** Re-rendered images match held-out captures.

### M6.2 — Engine export of texture maps

- [ ] Unreal material + textures
- [ ] Unity HDRP/URP material + textures
- [ ] **Acceptance:** Both engines render without manual edits.

### M6.3 — Phase 6 milestone test

- [ ] Gantry photo vs in-engine render, same light pose
- [ ] **Acceptance:** Visual match documented with side-by-side images.

### M6.4 — Open-source release and OSHWA certification

- [ ] Work through docs/07-oshwa-certification.md
- [ ] Make repository and Onshape document public
- [ ] Apply for OSHWA certification
- [ ] Tag v1.0
- [ ] **Acceptance:** Public repo, OSHWA UID in README.


## M7 - Stretch: OpenGantry Pro (advanced track)

**Goal:** Research-grade features inspired by the Stanford Spherical Gantry, X-Rite TAC7/PANTORA and RGL-EPFL, added without breaking the Lite build.

### M7.1 — Adaptive BRDF sampling (Dupuy & Jakob 2018 style)

- [ ] Read the RGL-EPFL paper
- [ ] Prototype sample placement from a coarse scan
- [ ] Compare against grid sampling on MERL data
- [ ] **Acceptance:** Same fit quality with >= 3x fewer captures.

### M7.2 — Multi-light capture head (TAC7-style)

- [ ] Ring of fixed LEDs around the camera
- [ ] Sequenced capture
- [ ] Power-budget update
- [ ] **Acceptance:** One pose captures N lighting directions.

### M7.3 — Spectral / polarization-resolved capture

- [ ] Filter wheel or narrowband LEDs
- [ ] Full Stokes with rotating polarizer
- [ ] **Acceptance:** Per-channel BRDF of a coloured metal swatch.

### M7.4 — Validation against published data

- [ ] Measure a material also in the MERL or RGL databases
- [ ] Report differences
- [ ] **Acceptance:** Published comparison in docs.

