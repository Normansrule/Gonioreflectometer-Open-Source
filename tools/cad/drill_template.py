#!/usr/bin/env python3
"""1:1 drill template for the 600 x 600 mm base -> phases/03-frame/drill-template.svg.
Print at 100 % (poster / tile mode), check the 100 mm bar, tape to the plywood, centre-punch each cross.
SPDX-License-Identifier: CERN-OHL-S-2.0
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "phases/03-frame/drill-template.svg"
S, HALF = 600, 300                       # plate size; origin (0, 0) under the zero point = plate centre
DRILL = {"M4 tee": 6.0, "M5 tee": 7.0, "M8 tee": 10.0, "M5": 5.5}


def og40(x, y):
    return [(x + dx, y + dy, "M4 tee") for dx in (-20, 20) for dy in (-20, 20)]


holes = []
holes += [(x, y, k, "table post") for x, y, k in og40(0, 0)]
holes += [(125 * math.cos(math.radians(a)), 125 * math.sin(math.radians(a)), "M5 tee", "ring plate") for a in (45, 135, 225, 315)]
holes += [(220, 0, "M5", "outrigger"), (280, 0, "M5", "outrigger")]
holes += [(x, y, k, "power box") for x, y, k in og40(-220, -220)]
holes += [(x, y, k, "controller") for x, y, k in og40(-220, 220)]
holes += [(sx * 270, sy * 270, "M8 tee", "foot") for sx in (-1, 1) for sy in (-1, 1)]


def P(x, y):                             # plate mm -> SVG mm (y down)
    return x + HALF, HALF - y


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}mm" height="{S}mm" viewBox="0 0 {S} {S}" font-family="Arial" font-size="5">',
       f'<rect x="0.5" y="0.5" width="{S - 1}" height="{S - 1}" fill="none" stroke="#000" stroke-width="0.5"/>',
       f'<circle cx="{HALF}" cy="{HALF}" r="150" fill="none" stroke="#999" stroke-width="0.3" stroke-dasharray="4 3"/>',
       f'<text x="{HALF + 4}" y="{HALF - 152}" fill="#666">12 in ring (reference)</text>',
       f'<line x1="{HALF}" y1="{HALF}" x2="{S}" y2="{HALF}" stroke="#4a8" stroke-width="0.3" stroke-dasharray="2 2"/>',
       f'<text x="{S - 120}" y="{HALF - 3}" fill="#4a8">+X to camera (outrigger)</text>']
labelled = set()
for x, y, kind, what in holes:
    cx, cy = P(x, y)
    d = DRILL[kind]
    svg.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{d / 2}" fill="none" stroke="#c00" stroke-width="0.3"/>'
               f'<path d="M{cx - 6:.2f} {cy:.2f}h12M{cx:.2f} {cy - 6:.2f}v12" stroke="#000" stroke-width="0.2"/>')
    if (what, kind) not in labelled or what in ("foot", "ring plate"):
        labelled.add((what, kind))
        anchor, dx = ("end", -5) if x > 150 else ("start", 5)
        svg.append(f'<text x="{cx + dx:.2f}" y="{cy - 8:.2f}" text-anchor="{anchor}">{what}: drill Ø{d:g} ({kind})</text>')
svg.append('<path d="M250 585h100" stroke="#000" stroke-width="0.6"/><path d="M250 581v8M350 581v8" stroke="#000" stroke-width="0.6"/>'
           '<text x="250" y="578" font-size="6">100 mm: measure before drilling</text>')
svg.append('<text x="20" y="20" font-size="8">OpenGonio base drill template 1:1 (600 x 600 mm). Origin = centre = zero point.</text>')
svg.append("</svg>")
OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"{len(holes)} holes -> {OUT.relative_to(ROOT)}")
