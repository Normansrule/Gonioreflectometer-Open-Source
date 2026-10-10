# 03 · Design

## Placement map (no cutting, no drilling)

2 × 2 ft plywood used as bought; origin at the panel centre, under the zero point; zero point 150 mm above the base.

**1:1 template:** [placement-template.svg](placement-template.svg) (print at 100 %, poster/tile mode; check the 100 mm bar). Each printed part sits on its outline; #8 × 5/8 in Type 17 wood screws [F8] go straight through the paper at the crosses; the point drills its own hole. Every screw passes through ≥ 6 mm of printed part, so 16 mm never pokes through 12 mm plywood.

| Feature | Position (mm) | Fixing |
|---|---|---|
| Table post (TBL-07d) | (0, 0) | 4 wood screws through its round flange (stage 05) |
| Table motor bracket (TBL-07c) | (−49.4, 0), inside the lazy Susan | 2 wood screws in slots (stage 05) |
| 12 in lazy Susan | centred on the Ø305 circle | wood screws through its own holes + 4 mm washers (stage 04) |
| M4 motor mount (LAR-08b) | 0°, base r 156–211 | 2 wood screws in radial slots (stage 04) |
| Outrigger saddles (FRM-09d) | (237, 0), (282, 0) | 4 wood screws each; 2020 held by M5 × 10 into side-slot T-nuts |
| Camera outrigger (2020) | +X from (215, 0) to (715, 0) | in the saddles, end foot (FRM-09f, 30 mm) at 628 (just inside the scan post) |
| Cameras | (391.8, 0) measuring camera on a printed pillar (FRM-09h, top at z 170; lens front at 350) · (674.4, 0) scan camera on a 500 mm 2020 post (FRM-09e socket), 15° down, lens 650 mm from the zero point and 168 mm above it | both on the outrigger. No tall post at the measuring camera: it would stand in the scan camera's line of sight |
| Power box | (220, −220) | 4 wood screws through its floor bosses (OG-40) |
| Controller tray | centre (−190, 220) | 4 wood screws through its corner bosses |
| Feet (FRM-09b) | flush in each corner, underneath | 2 wood screws each; no levelling bolts (the optics reference the board, not gravity) |

Fasteners: #8 × 5/8 Type 17 wood screws × ~50 (FRM-12), M5 × 10 + T-nuts × 7 (stage 03; 13 in all).

## 3D parts

| Part | Source |
|---|---|
| OG-40 adapter, feet, 2020 saddles, post sockets, end foot, washers, protractor scales (FRM-09) | `tools/cad/parts.py` (`FRM-09a`–`g`) |
| 2020 extrusion | Onshape Standard Content |
| 608 bearings | Onshape bearing generator |

## Results

(fill in)
