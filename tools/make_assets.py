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
sys.path.insert(0, str(ROOT / "tools"))
import machine3d as m3d  # noqa: E402

FONT = "Segoe UI,Helvetica,Arial,sans-serif"
BG, PANEL, LINE, TXT, MUTED = "#0d1117", "#161b22", "#30363d", "#f0f6fc", "#8b949e"
ORANGE, BLUE, GREEN, PURPLE, YELLOW = "#f0883e", "#58a6ff", "#3fb950", "#bc8cff", "#e3b341"


def svg(w: int, h: int, body: str, extra_style: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="{FONT}">\n'
            f'<style>.t{{fill:{TXT}}} .m{{fill:{MUTED}}} .b{{font-weight:600}} {extra_style}</style>\n'
            f'<rect width="{w}" height="{h}" rx="14" fill="{BG}"/>\n{body}\n</svg>\n')


def hero() -> str:
    poses, active = m3d.demo_poses()
    body = f"""<text x="56" y="150" class="t b" font-size="40">Gonioreflectometer</text>
<text x="56" y="196" class="t b" font-size="40">Open-Source</text>
<text x="58" y="236" fill="{ORANGE}" font-size="18" class="b">material capture + 3D scanner · under $500</text>
<text x="58" y="266" class="m" font-size="15">sample turns, tilts, spins · light circles · camera fixed</text>
<text x="58" y="340" class="m" font-size="12">after Ansari-Asl et al. 2024 [R1]</text>
{m3d.machine(m3d.View(720, 250, 0.72), poses, active, labels=(1010, 60))}"""
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
    b += box(30, 20, 250, 62, "Power", "60 W adapter · fuse · E-STOP", ORANGE)
    b += box(30, 110, 250, 70, "Laptop (mode 1)", "control · capture · processing", GREEN)
    b += box(30, 205, 250, 70, "Pi Zero 2 W (mode 2)", "no laptop: runs jobs, saves data", GREEN)
    b += box(30, 320, 250, 62, "USB camera (fixed)", "on the laptop or the Pi", BLUE)
    b += box(450, 70, 280, 90, "FYSETC E4 · FluidNC", "ESP32 · 4 × TMC2209 · WebUI", PURPLE)
    b += box(450, 280, 280, 90, "Pico panel", "buttons · OLED · e-stop sense · LEDs", PURPLE)
    b += box(900, 20, 270, 62, "M1 – M4 steppers", "optical homing · safety switches", BLUE)
    b += box(900, 100, 270, 62, "Lights", "white COB · 8-band LEDs", YELLOW)
    b += box(900, 180, 270, 52, "PAUSE button", "feed hold on the E4", ORANGE)
    b += box(900, 260, 270, 62, "Buttons + OLED", "NEXT · START · STOP · HOME · LIGHT", ORANGE)
    b += box(900, 345, 270, 52, "Phone (no computer)", "WebUI: jog, home", MUTED)
    b += flow(280, 51, 450, 95, ORANGE, "24 V")
    b += flow(280, 140, 450, 115, PURPLE, "USB · WiFi · BT")
    b += flow(280, 240, 450, 135, GREEN, "WiFi")
    b += flow(280, 155, 450, 300, PURPLE, "USB")
    b += flow(280, 255, 450, 330, GREEN, "UART")
    b += flow(155, 320, 155, 275, BLUE)
    b += flow(730, 100, 900, 51, BLUE)
    b += flow(730, 120, 900, 131, YELLOW)
    b += flow(900, 206, 730, 140, ORANGE)
    b += flow(900, 291, 730, 325, ORANGE)
    b += flow(900, 371, 730, 150, MUTED)
    return svg(1200, 410, b)


def axes() -> str:
    poses, active = m3d.demo_poses()
    body = f"""<text x="40" y="44" class="t b" font-size="20">Four axes, one zero point</text>
<text x="40" y="70" class="m" font-size="13">each axis moves in turn [R1]</text>
<text x="40" y="330" class="m" font-size="12">M4 ring 12 in · M3, M2 5:1 · M1 4:1</text>
<text x="40" y="350" class="m" font-size="12">orange square = sample · blue = fixed camera</text>
{m3d.machine(m3d.View(560, 225, 0.68), poses, active, labels=(40, 120))}"""
    return svg(1000, 420, body)


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
<text x="720" y="300" class="m" font-size="12">from software/src/opengonio/brdf/models.py</text>'''
    return svg(1100, 380, b)


def phases() -> str:
    import yaml
    y = yaml.safe_load((ROOT / ".github" / "phases.yml").read_text(encoding="utf-8"))
    count = {}
    for m in y["milestones"]:
        count[m["stage"]] = count.get(m["stage"], 0) + 1
    group = lambda n: LINE if n <= 3 else ORANGE if n <= 10 else BLUE if n <= 13 else GREEN
    per_row, w, h, gx, gy, x0, y0 = 6, 182, 76, 14, 14, 24, 56
    b = f'<text x="24" y="36" class="t b" font-size="18">{len(y["stages"])} stages · {len(y["milestones"])} small milestones</text>'
    for i, (name, col) in enumerate((("setup", LINE), ("measure", ORANGE), ("3D scan", BLUE), ("app · standalone · release", GREEN))):
        b += f'<rect x="{620 + i * 120}" y="24" width="12" height="12" rx="2" fill="{col}"/><text x="{638 + i * 120}" y="35" class="m" font-size="12">{name}</text>'
    for i, st in enumerate(y["stages"]):
        n = int(st["folder"][:2])
        x, yy = x0 + (i % per_row) * (w + gx), y0 + (i // per_row) * (h + gy)
        col = group(n)
        b += f'<rect x="{x}" y="{yy}" width="{w}" height="{h}" rx="10" fill="{PANEL}" stroke="{col}" stroke-width="2" opacity="0">'
        b += f'<animate attributeName="opacity" from="0" to="1" begin="{i * 0.1:.2f}s" dur="0.4s" fill="freeze"/></rect>'
        b += f'<text x="{x + 12}" y="{yy + 22}" fill="{col if col != LINE else MUTED}" font-size="12" class="b">{n:02d} · {count.get(st["folder"], 0)} milestones</text>'
        words, lines = st["title"].split(), [""]
        for wd in words:
            lines[-1:] = [f"{lines[-1]} {wd}".strip()] if len(f"{lines[-1]} {wd}") <= 23 else [lines[-1], wd]
        for k, ln in enumerate(lines[:2]):
            b += f'<text x="{x + 12}" y="{yy + 42 + 16 * k}" class="t" font-size="13">{ln}</text>'
    rows = (len(y["stages"]) + per_row - 1) // per_row
    return svg(1200, y0 + rows * (h + gy) + 6, b)


def scanner() -> str:
    """Fixed camera, object on the tilted platter spinning (M1), elevation stepping (M2), view sphere filling in."""
    cx, cy = 330, 230
    b = '<text x="40" y="44" class="t b" font-size="20">3D photo scanner (Phases 11–12)</text>'
    b += f'<text x="40" y="70" class="m" font-size="13">M1 spins, M2 tilts, camera fixed: every pose known [S9]</text>'
    # platter + object, tilt animation
    b += f'''<g>
 <animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};-20 {cx} {cy};-40 {cx} {cy};-60 {cx} {cy};0 {cx} {cy}" keyTimes="0;0.25;0.5;0.75;1" dur="12s" repeatCount="indefinite" calcMode="discrete"/>
 <rect x="{cx - 70}" y="{cy + 40}" width="140" height="12" rx="4" fill="{PURPLE}"/>
 <rect x="{cx - 12}" y="{cy + 52}" width="24" height="40" fill="{MUTED}"/>
 <path d="M{cx - 55} {cy + 40} L{cx - 50} {cy + 8} L{cx - 20} {cy - 6} L{cx + 30} {cy - 6} L{cx + 52} {cy + 14} L{cx + 58} {cy + 40} Z" fill="{ORANGE}" opacity="0.9"/>
 <rect x="{cx - 14}" y="{cy}" width="34" height="12" rx="3" fill="{BG}" opacity="0.6">
  <animate attributeName="x" values="{cx - 40};{cx + 10};{cx - 40}" dur="3s" repeatCount="indefinite"/></rect>
 <circle cx="{cx - 32}" cy="{cy + 40}" r="10" fill="{BG}" stroke="{TXT}" stroke-width="2"/>
 <circle cx="{cx + 36}" cy="{cy + 40}" r="10" fill="{BG}" stroke="{TXT}" stroke-width="2"/>
</g>
<circle cx="{cx}" cy="{cy + 20}" r="4" fill="{YELLOW}"/>
<line x1="{cx + 330}" y1="{cy + 20}" x2="{cx + 80}" y2="{cy + 20}" stroke="{BLUE}" stroke-width="2" stroke-dasharray="8 6">
 <animate attributeName="stroke-dashoffset" from="0" to="28" dur="0.8s" repeatCount="indefinite"/></line>
<rect x="{cx + 330}" y="{cy}" width="70" height="40" rx="6" fill="{PANEL}" stroke="{BLUE}" stroke-width="2"/>
<rect x="{cx + 330}" y="{cy}" width="70" height="40" rx="6" fill="{TXT}" opacity="0">
 <animate attributeName="opacity" values="0;0.6;0" dur="0.5s" repeatCount="indefinite"/></rect>
<text x="{cx + 365}" y="{cy + 62}" fill="{BLUE}" font-size="12" text-anchor="middle">fixed camera</text>
<text x="{cx - 90}" y="{cy + 120}" fill="{PURPLE}" font-size="12">M2 tilt → view elevation 90° − M2</text>
<text x="{cx - 90}" y="{cy + 138}" fill="{ORANGE}" font-size="12">M1 spin → 36 views per ring</text>'''
    # view sphere (orthographic, tilted) with dots appearing ring by ring
    sx, sy, R = 960, 240, 150
    b += f'<ellipse cx="{sx}" cy="{sy}" rx="{R}" ry="{R}" fill="none" stroke="{LINE}"/>'
    rings = [(0, 36), (20, 36), (40, 36), (60, 24), (80, 12)]
    tilt = math.radians(20)
    k = 0
    total = sum(n for _, n in rings)
    for e, n in rings:
        er = math.radians(e)
        b += f'<ellipse cx="{sx}" cy="{sy - R * math.sin(er) * math.cos(tilt):.1f}" rx="{R * math.cos(er):.1f}" ry="{R * math.cos(er) * math.sin(tilt):.1f}" fill="none" stroke="{LINE}" stroke-dasharray="3 4"/>'
        for j in range(n):
            a = 2 * math.pi * j / n
            x = R * math.cos(er) * math.cos(a)
            yv = R * math.cos(er) * math.sin(a)
            z = R * math.sin(er)
            px = sx + x
            py = sy - (z * math.cos(tilt) - yv * math.sin(tilt))
            front = yv < 0
            t0 = 10.0 * k / total
            col = BLUE if front else "#2d5a8c"
            b += (f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{3.2 if front else 2.4}" fill="{col}" opacity="0">'
                  f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{t0 / 12:.3f};{min(t0 / 12 + 0.01, 0.99):.3f};1" dur="12s" repeatCount="indefinite"/></circle>')
            k += 1
    b += f'<circle cx="{sx}" cy="{sy}" r="6" fill="{ORANGE}"/>'
    b += f'<text x="{sx}" y="{sy + R + 40}" class="m" font-size="13" text-anchor="middle">view sphere around the object: 5 rings, 144 images</text>'
    b += f'<text x="{sx}" y="{sy + R + 60}" class="m" font-size="12" text-anchor="middle">→ COLMAP with known poses · visual hull · photometric stereo</text>'
    return svg(1200, 470, b)


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
    b += f'<text x="20" y="{y + 82}" class="m" font-size="12">Mains stays in the adapter. E-STOP cuts 24 V to the motors; the laptop keeps running.</text>'
    return svg(1200, 150, b)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("hero", hero), ("architecture", architecture), ("axes", axes), ("brdf-lobe", brdf),
                     ("phases", phases), ("power-flow", power_flow), ("scanner", scanner)):
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("wrote", f"docs/assets/{name}.svg")


if __name__ == "__main__":
    main()
