#!/usr/bin/env python3
"""Generate the animated SVG figures in docs/assets/ (original drawings).

    python tools/make_assets.py

SMIL animations play when GitHub shows the SVG as an image.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets"
sys.path.insert(0, str(ROOT / "software" / "src"))

from opengonio.brdf.models import ggx_brdf, sph_to_vec  # noqa: E402

FONT = "Segoe UI,Helvetica,Arial,sans-serif"
BG, PANEL, LINE, TXT, MUTED = "#0d1117", "#161b22", "#30363d", "#f0f6fc", "#8b949e"
ORANGE, BLUE, GREEN, PURPLE, YELLOW = "#f0883e", "#58a6ff", "#3fb950", "#bc8cff", "#e3b341"


def svg(w: int, h: int, body: str, extra_style: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="{FONT}">\n'
            f'<style>.t{{fill:{TXT}}} .m{{fill:{MUTED}}} .b{{font-weight:600}} {extra_style}</style>\n'
            f'<rect width="{w}" height="{h}" rx="14" fill="{BG}"/>\n{body}\n</svg>\n')


def hero() -> str:
    cx, cy = 840, 230
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="460" stroke="#161b22"/>' for x in range(0, 1200, 40))
    grid += "".join(f'<line x1="0" y1="{y}" x2="1200" y2="{y}" stroke="#161b22"/>' for y in range(0, 460, 40))
    body = f'''{grid}
<defs>
 <radialGradient id="glow"><stop offset="0" stop-color="{YELLOW}" stop-opacity="0.9"/><stop offset="1" stop-color="{YELLOW}" stop-opacity="0"/></radialGradient>
 <linearGradient id="fov" x1="1" x2="0"><stop offset="0" stop-color="{BLUE}" stop-opacity="0.25"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>
</defs>
<text x="56" y="150" class="t b" font-size="40">Gonioreflectometer</text>
<text x="56" y="196" class="t b" font-size="40">Open-Source</text>
<text x="58" y="236" fill="{ORANGE}" font-size="18" class="b">OpenGonio · low-cost multispectral material appearance capture</text>
<text x="58" y="270" class="m" font-size="15">fixed camera · 3-axis sample stage · rotating light arm · laptop-controlled</text>
<text x="58" y="294" class="m" font-size="15">USB / WiFi / Bluetooth · physical buttons · 0.1° target repeatability</text>
<text x="58" y="340" class="m" font-size="12">Architecture after Ansari-Asl et al., J. Imaging 10(3):55, 2024 · theory after Hanrahan, CS348b</text>
<!-- machine, top view -->
<circle cx="{cx}" cy="{cy}" r="165" fill="none" stroke="{LINE}" stroke-width="2" stroke-dasharray="6 6"/>
<text x="{cx}" y="{cy + 192}" class="m" font-size="12" text-anchor="middle">12 in ring (M4)</text>
<polygon points="{cx + 270},{cy - 22} {cx + 270},{cy + 22} {cx + 14},{cy + 4} {cx + 14},{cy - 4}" fill="url(#fov)"/>
<line x1="{cx}" y1="{cy}" x2="{cx + 262}" y2="{cy}" stroke="{BLUE}" stroke-width="3" stroke-dasharray="10 8">
 <animate attributeName="stroke-dashoffset" from="0" to="-36" dur="0.9s" repeatCount="indefinite"/></line>
<rect x="{cx + 262}" y="{cy - 18}" width="56" height="36" rx="6" fill="{PANEL}" stroke="{BLUE}" stroke-width="2"/>
<circle cx="{cx + 262}" cy="{cy}" r="9" fill="{BLUE}"/>
<text x="{cx + 290}" y="{cy + 40}" fill="{BLUE}" font-size="12" text-anchor="middle">fixed camera</text>
<g>
 <animateTransform attributeName="transform" type="rotate" values="-30 {cx} {cy};-150 {cx} {cy};-30 {cx} {cy}" dur="9s" repeatCount="indefinite"/>
 <line x1="{cx + 120}" y1="{cy}" x2="{cx + 190}" y2="{cy}" stroke="{MUTED}" stroke-width="10" stroke-linecap="round"/>
 <line x1="{cx + 150}" y1="{cy}" x2="{cx + 4}" y2="{cy}" stroke="{YELLOW}" stroke-width="3" stroke-dasharray="10 8">
  <animate attributeName="stroke-dashoffset" from="0" to="36" dur="0.9s" repeatCount="indefinite"/></line>
 <circle cx="{cx + 160}" cy="{cy}" r="28" fill="url(#glow)"/>
 <circle cx="{cx + 160}" cy="{cy}" r="11" fill="{YELLOW}"/>
</g>
<circle cx="{cx}" cy="{cy}" r="52" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>
<g>
 <animateTransform attributeName="transform" type="rotate" values="-15 {cx} {cy};-75 {cx} {cy};-15 {cx} {cy}" dur="9s" repeatCount="indefinite"/>
 <rect x="{cx - 4}" y="{cy - 34}" width="8" height="68" rx="2" fill="{ORANGE}"/>
 <line x1="{cx}" y1="{cy}" x2="{cx + 44}" y2="{cy}" stroke="{ORANGE}" stroke-width="1.5" stroke-dasharray="3 3"/>
</g>
<circle cx="{cx}" cy="{cy}" r="7" fill="{YELLOW}"><animate attributeName="r" values="5;10;5" dur="1.8s" repeatCount="indefinite"/></circle>
<text x="{cx - 120}" y="{cy - 120}" fill="{YELLOW}" font-size="12">light arm</text>
<text x="{cx - 70}" y="{cy + 80}" fill="{ORANGE}" font-size="12">sample (M3 = M4 / 2 → specular)</text>'''
    return svg(1200, 460, body)


def box(x, y, w, h, title, sub="", color=BLUE):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{PANEL}" stroke="{color}" stroke-width="2"/>'
    s += f'<text x="{x + 14}" y="{y + 26}" class="t b" font-size="15">{title}</text>'
    if sub:
        s += f'<text x="{x + 14}" y="{y + 48}" class="m" font-size="12">{sub}</text>'
    return s


def flow(x1, y1, x2, y2, color, label="", dur="1s"):
    s = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2.5" stroke-dasharray="8 6">'
         f'<animate attributeName="stroke-dashoffset" from="0" to="-28" dur="{dur}" repeatCount="indefinite"/></line>')
    if label:
        s += f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 8}" fill="{color}" font-size="12" text-anchor="middle">{label}</text>'
    return s


def architecture() -> str:
    b = ""
    b += box(30, 30, 250, 70, "Power", "60 W adapter · fuse · rocker · E-STOP", ORANGE)
    b += box(30, 170, 250, 90, "Laptop", "opengonio · capture · processing", GREEN)
    b += box(30, 330, 250, 70, "USB camera (fixed)", "IMX477, 16 mm M12, f/8 stop", BLUE)
    b += box(450, 90, 280, 90, "FYSETC E4 · FluidNC", "ESP32 · 4 × TMC2209 · WebUI", PURPLE)
    b += box(450, 300, 280, 90, "Pico hub · MicroPython", "buttons · e-stop sense · LED bank", PURPLE)
    b += box(900, 30, 270, 62, "M1 – M4 steppers", "homing barriers · safety switches", BLUE)
    b += box(900, 110, 270, 62, "Lights", "white COB · (Ph 5) 8-band LEDs", YELLOW)
    b += box(900, 190, 270, 52, "PAUSE button", "feed hold, no laptop needed", ORANGE)
    b += box(900, 270, 270, 62, "Panel buttons", "HOME · START · STOP · LIGHT · NEXT", ORANGE)
    b += box(900, 350, 270, 62, "Sensors", "e-stop sense · optional AS5600", GREEN)
    b += flow(280, 65, 450, 120, ORANGE, "24 V")
    b += flow(280, 200, 450, 140, PURPLE, "USB · WiFi · Bluetooth")
    b += flow(280, 240, 450, 330, PURPLE, "USB")
    b += flow(155, 330, 155, 260, BLUE, "")
    b += f'<text x="165" y="300" fill="{BLUE}" font-size="12">USB</text>'
    b += flow(730, 120, 900, 61, BLUE)
    b += flow(730, 140, 900, 141, YELLOW)
    b += flow(900, 216, 730, 160, ORANGE)
    b += flow(900, 301, 730, 330, ORANGE)
    b += flow(900, 381, 730, 360, GREEN)
    return svg(1200, 430, b)


def axes() -> str:
    cx, cy = 450, 255
    b = f'''
<ellipse cx="{cx}" cy="{cy + 70}" rx="230" ry="62" fill="none" stroke="{LINE}" stroke-width="3"/>
<ellipse cx="{cx}" cy="{cy + 70}" rx="230" ry="62" fill="none" stroke="{YELLOW}" stroke-width="3" stroke-dasharray="20 340">
 <animate attributeName="stroke-dashoffset" from="0" to="-360" dur="5s" repeatCount="indefinite"/></ellipse>
<text x="{cx + 240}" y="{cy + 120}" fill="{YELLOW}" font-size="14" class="b">M4 light arm (Phase 1)</text>
<line x1="{cx - 180}" y1="{cy + 100}" x2="{cx - 250}" y2="{cy - 40}" stroke="{MUTED}" stroke-width="10" stroke-linecap="round"/>
<circle cx="{cx - 250}" cy="{cy - 45}" r="16" fill="{YELLOW}"/>
<line x1="{cx - 236}" y1="{cy - 40}" x2="{cx - 10}" y2="{cy - 5}" stroke="{YELLOW}" stroke-width="2" stroke-dasharray="8 6">
 <animate attributeName="stroke-dashoffset" from="0" to="-28" dur="0.8s" repeatCount="indefinite"/></line>
<rect x="{cx - 40}" y="{cy + 40}" width="80" height="40" rx="6" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>
<text x="{cx}" y="{cy + 66}" class="m" font-size="12" text-anchor="middle">table</text>
<path d="M{cx - 70} {cy + 30} A70 18 0 0 0 {cx + 70} {cy + 30}" fill="none" stroke="{GREEN}" stroke-width="3" marker-end="url(#ag)"/>
<text x="{cx + 80}" y="{cy + 34}" fill="{GREEN}" font-size="14" class="b">M3 table yaw (Phase 1)</text>
<path d="M{cx - 30} {cy + 40} L{cx - 30} {cy - 60} M{cx + 30} {cy + 40} L{cx + 30} {cy - 60}" stroke="{MUTED}" stroke-width="6"/>
<g>
 <animateTransform attributeName="transform" type="rotate" values="-20 {cx} {cy - 30};20 {cx} {cy - 30};-20 {cx} {cy - 30}" dur="6s" repeatCount="indefinite"/>
 <rect x="{cx - 26}" y="{cy - 75}" width="52" height="90" rx="6" fill="{PANEL}" stroke="{PURPLE}" stroke-width="2"/>
 <circle cx="{cx}" cy="{cy - 30}" r="22" fill="{ORANGE}" opacity="0.9"/>
 <line x1="{cx}" y1="{cy - 30}" x2="{cx}" y2="{cy - 52}" stroke="{BG}" stroke-width="3">
  <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy - 30}" to="360 {cx} {cy - 30}" dur="4s" repeatCount="indefinite"/></line>
</g>
<text x="{cx + 40}" y="{cy - 80}" fill="{PURPLE}" font-size="14" class="b">M2 tilt (Phase 3)</text>
<text x="{cx + 40}" y="{cy - 60}" fill="{ORANGE}" font-size="14" class="b">M1 spin (Phase 4)</text>
<line x1="{cx + 330}" y1="{cy - 30}" x2="{cx + 24}" y2="{cy - 30}" stroke="{BLUE}" stroke-width="2" stroke-dasharray="8 6">
 <animate attributeName="stroke-dashoffset" from="0" to="28" dur="0.8s" repeatCount="indefinite"/></line>
<rect x="{cx + 330}" y="{cy - 52}" width="70" height="44" rx="6" fill="{PANEL}" stroke="{BLUE}" stroke-width="2"/>
<path d="M{cx + 400} {cy - 30} h40 v150" stroke="{MUTED}" stroke-width="6" fill="none"/>
<text x="{cx + 320}" y="{cy - 64}" fill="{BLUE}" font-size="14" class="b">fixed camera on L-arm</text>
<text x="40" y="44" class="t b" font-size="20">Four axes, one zero point</text>
<text x="40" y="70" class="m" font-size="13">sample orientation (M3, M2, M1) + light direction (M4) = full 4-D BRDF; camera never moves [R1]</text>
<defs><marker id="ag" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="{GREEN}"/></marker></defs>'''
    return svg(1000, 420, b)


def brdf() -> str:
    cx, cy, R = 350, 330, 230
    frames = [15, 30, 45, 60, 70, 45, 15]
    pts_n = 91

    def lobe(ti):
        wi = sph_to_vec(ti, 180.0)
        vals = []
        for k in range(pts_n):
            tr = -90 + 180 * k / (pts_n - 1)
            wo = sph_to_vec(abs(tr), 0.0 if tr >= 0 else 180.0)
            f = ggx_brdf(wi, wo, 0.45, 0.28) * max(wo[2], 0.0)
            vals.append((tr, f))
        return vals

    def path(ti):
        pts = []
        vals = lobe(ti)
        fmax = max(f for _, f in vals)
        for tr, f in vals:
            r = R * math.sqrt(f / fmax)
            a = math.radians(tr)
            pts.append(f"{cx + r * math.sin(a):.1f},{cy - r * math.cos(a):.1f}")
        return "M" + " L".join(pts) + " Z"

    dvals = ";".join(path(t) for t in frames)
    lx = ";".join(f"{cx - R * math.sin(math.radians(t)):.1f}" for t in frames)
    ly = ";".join(f"{cy - R * math.cos(math.radians(t)):.1f}" for t in frames)
    arcs = "".join(f'<path d="M{cx - R * k / 3:.0f} {cy} A{R * k / 3:.0f} {R * k / 3:.0f} 0 0 1 {cx + R * k / 3:.0f} {cy}" fill="none" stroke="{LINE}"/>' for k in (1, 2, 3))
    spokes = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{cx + R * math.sin(math.radians(a)):.1f}" y2="{cy - R * math.cos(math.radians(a)):.1f}" stroke="{LINE}"/>'
        for a in range(-90, 91, 30))
    b = f'''{arcs}{spokes}
<line x1="{cx - R - 10}" y1="{cy}" x2="{cx + R + 10}" y2="{cy}" stroke="{MUTED}" stroke-width="2"/>
<path d="{path(frames[0])}" fill="{ORANGE}" fill-opacity="0.25" stroke="{ORANGE}" stroke-width="2.5">
 <animate attributeName="d" values="{dvals}" dur="10s" repeatCount="indefinite"/></path>
<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - R}" stroke="{YELLOW}" stroke-width="3">
 <animate attributeName="x2" values="{lx}" dur="10s" repeatCount="indefinite"/>
 <animate attributeName="y2" values="{ly}" dur="10s" repeatCount="indefinite"/></line>
<text x="{cx - R}" y="{cy + 26}" class="m" font-size="12">light side</text>
<text x="{cx + R - 70}" y="{cy + 26}" class="m" font-size="12">view side</text>
<text x="720" y="70" class="t b" font-size="20">In-plane BRDF lobe</text>
<text x="720" y="100" class="m" font-size="14">Lambert + GGX, roughness 0.28, base 0.45</text>
<text x="720" y="135" fill="{YELLOW}" font-size="14">yellow: incident direction θi</text>
<text x="720" y="160" fill="{ORANGE}" font-size="14">orange: √(f_r · cos θr), scaled per frame</text>
<text x="720" y="205" class="t" font-size="15">f_r = ρ/π + D·G·F / (4 cos θi cos θr)</text>
<text x="720" y="232" class="m" font-size="13">F(θ) = F0 + (1 − F0)(1 − cos θ)^5   [R2][R7]</text>
<text x="720" y="258" class="m" font-size="13">peak sits at θr = θi: what M3 = M4 / 2 measures</text>
<text x="720" y="300" class="m" font-size="12">computed by software/src/opengonio/brdf/models.py</text>'''
    return svg(1100, 380, b)


def phases() -> str:
    data = [("1", "In-plane BRDF", "M4 + M3 · camera", "$350"), ("2", "Calibrated → engine", "HDR · GGX fit", "$74"),
            ("3", "Isotropic BRDF", "+ M2 tilt", "$23"), ("4", "Anisotropic · SVBRDF", "+ M1 spin", "$23"),
            ("5", "Multispectral", "8-band LEDs · polarizer", "$30"), ("6", "Scan + SVBRDF maps", "software only", "$0")]
    w, gap, y = 175, 20, 60
    b = f'<line x1="60" y1="{y + 60}" x2="1140" y2="{y + 60}" stroke="{LINE}" stroke-width="3"/>'
    b += f'<circle cx="60" cy="{y + 60}" r="6" fill="{ORANGE}"><animate attributeName="cx" from="60" to="1140" dur="6s" repeatCount="indefinite"/></circle>'
    for i, (n, t, s, cap) in enumerate(data):
        x = 20 + i * (w + gap)
        col = ORANGE if i == 0 else LINE
        b += f'<rect x="{x}" y="{y}" width="{w}" height="120" rx="12" fill="{PANEL}" stroke="{col}" stroke-width="2">'
        if i == 0:
            b += '<animate attributeName="stroke-opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>'
        b += "</rect>"
        b += f'<text x="{x + 14}" y="{y + 32}" fill="{ORANGE if i == 0 else MUTED}" font-size="13" class="b">PHASE {n}</text>'
        b += f'<text x="{x + 14}" y="{y + 58}" class="t b" font-size="14">{t}</text>'
        b += f'<text x="{x + 14}" y="{y + 80}" class="m" font-size="12">{s}</text>'
        b += f'<text x="{x + 14}" y="{y + 104}" fill="{GREEN}" font-size="13">cap {cap}</text>'
    b += f'<text x="24" y="36" class="t b" font-size="18">Build once, extend each phase</text>'
    return svg(1200, 210, b)


def power_flow() -> str:
    steps = ["Wall", "GST60A24 60 W", "Fuse 3.15 A T", "Rocker", "IRF4905", "24 V bus", "E-STOP", "FYSETC E4"]
    w, gap, y = 128, 18, 50
    b = ""
    for i, s in enumerate(steps):
        x = 20 + i * (w + gap)
        col = ORANGE if s == "E-STOP" else (PURPLE if "E4" in s else LINE)
        b += f'<rect x="{x}" y="{y}" width="{w}" height="48" rx="8" fill="{PANEL}" stroke="{col}" stroke-width="2"/>'
        b += f'<text x="{x + w / 2}" y="{y + 29}" class="t" font-size="13" text-anchor="middle">{s}</text>'
        if i:
            b += f'<line x1="{x - gap}" y1="{y + 24}" x2="{x}" y2="{y + 24}" stroke="{YELLOW}" stroke-width="2"/>'
    b += (f'<circle cy="{y + 24}" r="5" fill="{YELLOW}"><animate attributeName="cx" from="20" to="{20 + 8 * (w + gap) - gap}" '
          f'dur="3s" repeatCount="indefinite"/></circle>')
    b += f'<text x="20" y="{y + 82}" class="m" font-size="12">Mains never leaves the certified adapter. E-STOP removes 24 V from the motion board; the laptop keeps running.</text>'
    return svg(1200, 150, b)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("hero", hero), ("architecture", architecture), ("axes", axes), ("brdf-lobe", brdf),
                     ("phases", phases), ("power-flow", power_flow)):
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("wrote", f"docs/assets/{name}.svg")


if __name__ == "__main__":
    main()
