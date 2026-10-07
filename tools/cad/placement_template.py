#!/usr/bin/env python3
"""1:1 placement template for the 2 x 2 ft base -> phases/03-frame/placement-template.svg. No drilling:
print at 100 % (poster / tile mode), check the 100 mm bar, tape it on centred, set each printed part on its outline
and drive #8 Type 17 wood screws [F8] straight through the paper at the crosses.
SPDX-License-Identifier: CERN-OHL-S-2.0
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "phases/03-frame/placement-template.svg"
S, HALF = 610, 305                       # 2 x 2 ft panel as sold; origin (0, 0) under the zero point = panel centre


def og40(x, y):
    return [(x + dx, y + dy) for dx in (-20, 20) for dy in (-20, 20)]


# (label, outline centre, outline w x h, screw points)
PARTS = [
    ("table post", (0, 0), (54, 54), [(22.2 * math.cos(math.radians(a)), 22.2 * math.sin(math.radians(a))) for a in (45, 135, 225, 315)]),
    ("table motor bracket (slots)", (-49.4, 0), (46, 79), [(-49.4, sy * 34.3) for sy in (-1, 1)]),
    ("outrigger saddles", (237, 0), (45, 40), [(237 + sx * 16, sy * 13) for sx in (-1, 1) for sy in (-1, 1)]),
    ("", (282, 0), (45, 40), [(282 + sx * 16, sy * 13) for sx in (-1, 1) for sy in (-1, 1)]),
    ("M4 motor mount (radial slots)", (183.5, 0), (55, 96), [(183.5, sy * 38) for sy in (-1, 1)]),
    ("power box (OG-40)", (220, -220), (120, 80), og40(220, -220)),
    ("controller tray", (-190, 220), (200, 130), [(-190 + sx * 92, 220 + sy * 57) for sx in (-1, 1) for sy in (-1, 1)]),
]


def P(x, y):                             # panel mm -> SVG mm (y down)
    return x + HALF, HALF - y


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}mm" height="{S}mm" viewBox="0 0 {S} {S}" font-family="Arial" font-size="5">',
       f'<rect x="0.5" y="0.5" width="{S - 1}" height="{S - 1}" fill="none" stroke="#000" stroke-width="0.5"/>',
       f'<circle cx="{HALF}" cy="{HALF}" r="152.5" fill="none" stroke="#c00" stroke-width="0.5"/>',
       f'<text x="{HALF + 4}" y="{HALF - 156}" fill="#c00">12 in lazy Susan: centre it on this circle, screw through its own holes</text>',
       f'<path d="M{HALF - 10} {HALF}h20M{HALF} {HALF - 10}v20" stroke="#000" stroke-width="0.3"/>',
       f'<line x1="{HALF}" y1="{HALF}" x2="{S}" y2="{HALF}" stroke="#4a8" stroke-width="0.3" stroke-dasharray="2 2"/>',
       f'<text x="{S - 8}" y="{HALF + 30}" fill="#4a8" text-anchor="end">+X to camera: outrigger (2020) in the saddles</text>']
n = 0
for label, (cx, cy), (w, h), pts in PARTS:
    x, y = P(cx, cy)
    svg.append(f'<rect x="{x - w / 2:.2f}" y="{y - h / 2:.2f}" width="{w}" height="{h}" fill="none" stroke="#06c" stroke-width="0.4" stroke-dasharray="3 2"/>')
    anchor, dx = ("end", w / 2 + 52) if cx > 150 else ("start", -w / 2)
    if label:
        svg.append(f'<text x="{x + dx:.2f}" y="{y - h / 2 - 3:.2f}" text-anchor="{anchor}" fill="#06c">{label}: outline, screw at each cross</text>')
    for px, py in pts:
        qx, qy = P(px, py)
        n += 1
        svg.append(f'<path d="M{qx - 5:.2f} {qy:.2f}h10M{qx:.2f} {qy - 5:.2f}v10" stroke="#000" stroke-width="0.3"/>'
                   f'<circle cx="{qx:.2f}" cy="{qy:.2f}" r="2.1" fill="none" stroke="#000" stroke-width="0.2"/>')
svg.append('<path d="M490 595h100" stroke="#000" stroke-width="0.6"/><path d="M490 591v8M590 591v8" stroke="#000" stroke-width="0.6"/>'
           '<text x="490" y="588" font-size="6">100 mm: measure before placing</text>')
svg.append('<text x="200" y="585" font-size="7">OpenGonio base placement template 1:1 (2 x 2 ft)</text>')
svg.append('<text x="200" y="594" font-size="5">Origin = centre = zero point. No drilling: #8 Type 17 wood screws straight through the paper.</text>')
svg.append('<text x="200" y="602" font-size="5">Feet: one under each corner, flush with the edges (no marks needed).</text>')
svg.append("</svg>")
OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"{n} screw points -> {OUT.relative_to(ROOT)}")
