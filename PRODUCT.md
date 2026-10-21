# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

- Website (GitHub Pages, `docs/`): delegated. Chosen: static HTML/CSS/JS with no build step, so the existing 3D simulator, generated data files (`docs/machine.js`, `docs/plan.js`) and the Pages workflow keep working.
- App: one control interface in HTML/CSS/JS, shipped two ways (user's answer: "both website and desktop app versions"): served in the browser by the `opengonio` Python package, and in a native desktop window around the same interface. Desktop wrapper: delegated (proposal: a lightweight Python webview, so it installs with the package and needs no second toolchain).

## Users

- **Academic reviewers** (professors, PhD admissions): read the site as evidence of the builder's engineering judgement. They need to see what the instrument does, how it works, and what is proven versus designed, quickly.
- **Graphics and material people** (game artists, rendering and material-capture people): want reflectance (BRDF) data and fitted game-engine materials, and to understand what a measurement gives them.
- Builders (secondary): print and build their own from the repository.

## Product Purpose

OpenGonio is a printable, low-cost gonioreflectometer: it measures how a material reflects light at every angle (the bidirectional reflectance distribution function, BRDF) and also scans objects in 3D. Four motorised axes turn the sample (tilt, spin, table) and swing a lamp around it while a fixed camera records. The output is a reflectance curve and a fitted game-engine material (base colour, roughness, metallic). Runs from a laptop or standalone. Success: a reviewer understands the instrument and its evidence in minutes; a material person can see what a measurement looks like and get the files.

## Positioning

Built only from 3D-printed parts, M2 screws and off-the-shelf modules (no soldering, drilling, sawing or crimping), every part from Amazon, Digi-Key or Adafruit, under a hard budget cap of $630. Design after Ansari-Asl et al. (2024). Every hardware claim is labelled with its evidence level; the software is tested end to end on a simulated machine.

## Operating Context

- The machine sits in a dark box on a desk; parts are printed in matte black ABS to avoid stray reflections. A white PTFE tile is the brightness reference; a mirror and a laser on a wall 2 m away test repeatability.
- Light: a 3000 K, colour-rendering-index 97 chip-on-board LED; optional narrow-band colour LEDs (450–660 nm) are blocked pending a safe driver.
- The laptop runs `opengonio` (capture → verify → calibrate → curve → fit). The control app talks to the motion board (SKR Pico, grblHAL, USB-C) and the button hub (ESP32-S3).
- The project is built in stages 00–17 with checklists; the owner commits and pushes all changes.

## Capabilities and Constraints

- Real today: CLI, simulator (`make sim` ends "ALL PASS"), CAD with clash checks, BOM and budget, wiring tables, paper PDF, 3D simulator page.
- Not yet: no machine has been built or measured. The control app (stage 14) is not built before this work.
- Must not fabricate: measurements, board functionality, camera control, optical accuracy, safety certification, reconstructed accuracy, or successful unattended operation.
- Colour LED bank is blocked and must be shown as such.

## Evidence on Hand

- Simulated outputs: `docs/assets/example-mirror.svg`, `docs/assets/example-fit.svg`, `make sim` data in `data/sim`.
- CAD: STEP/STL in `cad/`, assembly renders, `docs/lab.html` 3D simulator; part pictures in `docs/assets/parts/`.
- Paper: `paper/build/opengonio.pdf`; references in `REFERENCES.md`.
- Wiring: `docs/wiring.yaml` and its diagrams.
- Absent: photographs of a built machine, real measurements, users, testimonials, press. None may be invented.

## Product Principles

1. Evidence before claims: every number says whether it is simulated, modelled, or measured.
2. Show the light: the thing being measured (how light leaves a surface) is the clearest explanation.
3. Buildable by one person with a printer and a screwdriver.
4. Honest states: blocked, untested and simulated are shown, never hidden.

## Accessibility & Inclusion

Keyboard navigation throughout, WCAG AA contrast in light and dark modes, respects reduced-motion (user requirement).
