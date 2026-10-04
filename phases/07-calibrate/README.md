# 07 · Calibrate → game material

**Goal:** A measured swatch looks right in Unreal or Unity.

**Cost:** $73.32 · running total $420.14 of $500

[Research](research/) · [Design](design/) · [3D files](3d/) · [Bill of materials](bom/)

## 07.1 Dark box and targets

- [ ] Blackout drape, felt backdrop
- [ ] Print holders for PTFE, mirror, balls, ChArUco
- [ ] **Done:** Stray light < 0.1 % of the PTFE signal.

## 07.2 Calibrate

- [ ] High dynamic range (HDR) from exposure brackets
- [ ] Angles from the mirror, light from the balls
- [ ] Brightness from the PTFE (polytetrafluoroethylene) white target
- [ ] **Done:** Angle error ≤ 0.2°; swapping light and camera changes values ≤ 5 %.

## 07.3 Fit and export

- [ ] Fit Lambert + GGX
- [ ] Export Unreal / Unity material
- [ ] **Done:** Render matches a photo at 3 light angles.

<sub>Generated from `.github/phases.yml` by `tools/roadmap.py`.</sub>
