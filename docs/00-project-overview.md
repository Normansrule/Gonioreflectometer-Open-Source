# Project overview

**OpenGantry Lite** is a tabletop, open-source take on the Stanford Spherical Gantry: a
four-axis gonioreflectometer that measures how real materials reflect light, then grows into a
photo-based 3D scanner. Target: 300 mm working radius, swatches up to 50 × 50 mm, objects up to
about 120 mm, all four axes meeting at one measurement centre within 0.5 mm, about 0.1° repeatability.

## The machine

| Axis | Motion | Range | Drive | Phase |
|---|---|---|---|---|
| A1 | Camera elevation about a horizontal axis through the centre | 0–85° from the normal | NEMA 17, 20T → printed 100T (5:1) | 1 |
| A2 | Light elevation on its own pivot | 0–85° | NEMA 17, 5:1 | 1 |
| A3 | Light azimuth: 12 in lazy Susan carrying the light tower | ±170° (collision model limits mid-elevation poses to about ±120°) | NEMA 17, GT2 belt around the ring (~24:1) | 3 |
| A4 | Turntable under the sample | 360° | NEMA 17, 20T → printed 80T (4:1) | 4 |

Every axis has an optical home flag and an AS5600 magnetic encoder. Software (Klipper on an SKR Mini
E3 V3, Python on the Pi) treats each axis as configuration: Phase 3 and 4 are a one-line change in
`software/config/machine.yaml` plus uncommenting a block in `printer.cfg`.

## Coordinate frame (used everywhere: CAD, firmware, software)

- Origin = measurement centre = top surface of the sample, `sample_height_mm` (150 mm) above the base.
- +Z up. **A1 rotates about the Y axis**; the camera sits on the −X side.
- At A3 = 0 the lamp sits on the +X side, in the same plane as the camera (Phase 1 in-plane geometry).
- θ is measured from the surface normal (+Z), φ is azimuth in the sample plane, matching the BRDF
  notation in [`01-theory-brdf.md`](01-theory-brdf.md).
- Phase 1 specular condition: **A1 = A2** (camera on the mirror direction of the light).

```
            +Z (normal)
             |      lamp (A2)
   camera    |     /
   (A1) \    |    /
         \   |   /
          \  |  /
  -X ------- O ------- +X        Y axis (into the page) = A1 pivot axis
          sample (A4 turntable underneath)
```

## Build-once layout

```
          base plate 600 x 600 mm (12 mm birch)
   ┌───────────────────────────────────────────────┐
   │                 light tower (+Y)              │
   │      ┌────── 12 in ring footprint ──────┐     │   OG-40 pads:
   │      │       (Phase 3, pre-drilled)     │     │    C  centre post (turntable-ready)
   │      │              [C]                 │     │    L  light bracket at r = 140 mm
   │      │              ( )                 │     │       = the ring top-plate position
   │      └──────────────────────────────────┘     │    K  camera tower at r = 175 mm
   │                 camera tower (-Y) [K]          │    P  power box, front right
   │  [CTL]                                   [P]   │
   └───────────────────────────────────────────────┘
```

- The Phase 1 light bracket bolts to the base at the same radius and with the same OG-40 pattern it
  will use on the ring's top plate. A printed **riser** equal to the ring stack height keeps the light
  pivot at sample height; in Phase 3 the riser is removed and the bracket moves onto the ring.
- The centre post carries a printed **turntable-height spacer**; in Phase 4 the turntable replaces it,
  so the sample surface stays at the same height and the calibration from Phase 2 still holds.
- The power supply, buck converter and motion board are sized for all four axes from day one.

## Phases and goals

| Phase | Goal (the machine does something useful at the end of every phase) | Cap |
|---|---|---:|
| 1 | In-plane gonioreflectometer: both axes home, repeat within 0.1°, mirror peak appears at the mirror angle | $300 |
| 2 | Calibrated in-plane BRDF of swatches → GGX fit → Unreal/Unity material that matches a photo | $75 |
| 3 | Full isotropic BRDF (light azimuth ring), unattended scan with the collision model on | $45 |
| 4 | Anisotropic BRDF (turntable), brushed-metal highlight follows the turntable | $35 |
| 5 | Photogrammetry + photometric stereo scanner, test block within 0.5 mm | $30 |
| 6 | On-object spatially varying reflectance → engine material maps | $0 |
| Stretch | "Pro" track: ideas borrowed from research and commercial rigs (below) | — |

Progress is tracked as GitHub milestones with checklist issues — see [`ROADMAP.md`](../ROADMAP.md).

## Advanced reference rigs (for the stretch "Pro" track)

| Rig | What to borrow | Link |
|---|---|---|
| Stanford Spherical Gantry (Levoy et al.) | The four-axis architecture this project scales down | [project](https://graphics.stanford.edu/projects/gantry/), [specs](https://graphics.stanford.edu/projects/gantry/design/specifications.html) |
| X-Rite TAC7 + PANTORA | Multi-light, multi-camera appearance capture and a material-exchange workflow | [TAC7](https://www.xrite.com/categories/appearance/tac7), [PANTORA](https://www.xrite.com/pantora-software) |
| Cornell gonioreflectometer | Three-axis design, published measurement data for validation | [gonio](http://w1.graphics.cornell.edu/research/measure/gonio.html), [data](https://www.graphics.cornell.edu/online/measurements/) |
| MERL BRDF database (Matusik 2003) | Dense isotropic sampling with spheres; reference data for fits | [database](https://www.merl.com/brdf/) |
| RGL-EPFL (Dupuy & Jakob 2018) | Adaptive sampling that puts measurements where the BRDF changes | [paper](https://rgl.epfl.ch/publications/Dupuy2018Adaptive), [data](https://rgl.epfl.ch/pages/lab/material-database) |
| UTIA | Gonioreflectometer + BTF (texture) capture | [BTF database](https://btf.utia.cas.cz/?faq=) |
