# 03 · Design

## Deck (printed, no plywood)

Nine 200 mm tiles (FRM-01a–i, black ABS, ≈ 160 g and ≈ 6 h each) bolt into a 600 × 600 × 24 mm deck: 2 mm top skin, 3 mm walls, 12 mm ribs; 3 × M2 × 10 + nut through each shared wall. Origin at the deck centre under the zero point; zero point 150 mm above the deck top. Every mount screws into a pilot boss that is already in the right place, so there is nothing to measure, mark or drill; a 40 mm grid of spare pilots in every tile takes endstops, switches and cable clips.

**Map:** [deck-map.svg](deck-map.svg) (tile names from above and from below, every pilot).

| Feature | Position (mm) | Fixing (M2, FRM-06) |
|---|---|---|
| Table post (TBL-07d) | (0, 0) | 4 × M2 × 12 into the C tile (stage 05) |
| Table motor bracket (TBL-07c) | (−49.4, 0), inside the lazy Susan | 2 × M2 × 12 + washers in slots (stage 05) |
| 12 in lazy Susan | centred in the ring scales | clamped by the 4 ring-scale segments (FRM-09c), 2 × M2 × 10 each into pilots at r 163 (stage 04) |
| M4 motor mount (LAR-08b) | 0°, base r 156–211 | 2 × M2 × 12 + washers in radial slots (stage 04) |
| Outrigger saddles (FRM-09d) | (237, 0), (278, 0) | 4 × M2 × 12 each; M2 × 16 sideways into the bar's pilot |
| Outrigger (FRM-02a + b) | +X from (215, 0) to (715, 0), joint at 465 (coupler FRM-09i) | in the saddles; end foot (FRM-09f, 30 mm) on the table at 628 |
| Cameras | (391.8, 0) measuring camera on a printed pillar (FRM-09h; lens front at 350) · (674.4, 0) scan camera on a 350 mm printed post (FRM-02c + d in the FRM-09e socket), 15° down, lens 650 mm from the zero point and 168 mm above it | both on the outrigger, M2 × 16 into its pilots. No tall post at the measuring camera: it would stand in the scan camera's line of sight |
| Power box | (220, −220), SE tile | 4 × M2 × 12 through its floor bosses (OG-40) |
| Controller tray | centre (−200, 220), NW tile | 4 × M2 × 12 through its corner bosses |

Fasteners (stage 03): M2 × 10 + nuts × 36 (seams), M2 × 12 × 16, M2 × 16 × 14. All from FRM-06.

## 3D parts

| Part | Source |
|---|---|
| Deck tiles (FRM-01a–i) | `tools/cad/parts.py` (`deck_tile`, pilots from `PLACE`) |
| Bars 20 × 20 (FRM-02a–d), couplers (FRM-09i) | `tools/cad/parts.py` (`_bar`, pilots at every clamp station) |
| Ring scales + lazy-Susan clamp, saddles, post socket, end foot, camera pillar (FRM-09c–h) | `tools/cad/parts.py` |
| 608 bearings | Onshape bearing generator |

## Results

(fill in)
