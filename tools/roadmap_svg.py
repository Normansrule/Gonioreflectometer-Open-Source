#!/usr/bin/env python3
"""Build-map figures from .github/phases.yml + .github/progress.json (written by roadmap.py, not by hand).

    docs/assets/phases.svg       every stage: hands-on hours, steps done / total, the next step
    docs/assets/steps/NN.svg     one stage: each milestone as a row of its steps (done · next · to do)

SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import re
from html import escape

FONT = "Segoe UI,Helvetica,Arial,sans-serif"
BG, PANEL, LINE, TXT, MUTED = "#0d1117", "#161b22", "#30363d", "#f0f6fc", "#8b949e"
ORANGE, BLUE, GREEN = "#f0883e", "#58a6ff", "#3fb950"


def hours(t: str | None) -> float:
    """'45 min' -> 0.75, '1.5 h' -> 1.5."""
    m = re.match(r"^\s*([\d.]+)\s*(min|h)\b", t or "")
    return 0.0 if not m else float(m.group(1)) / (60.0 if m.group(2) == "min" else 1.0)


def fmt_h(h: float) -> str:
    return f"{h * 60:.0f} min" if h < 1 else f"{h:.1f} h".replace(".0 h", " h")


def next_step(ms: list[dict], done: set[str]) -> tuple[dict, dict] | None:
    for m in ms:
        for s in m["steps"]:
            if s["id"] not in done:
                return m, s
    return None


def _svg(w: int, h: int, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="{FONT}">\n'
            f'<style>.t{{fill:{TXT}}} .m{{fill:{MUTED}}} .b{{font-weight:600}}</style>\n'
            f'<rect width="{w}" height="{h}" rx="14" fill="{BG}"/>\n{body}\n</svg>\n')


def _wrap(text: str, n: int) -> list[str]:
    lines = [""]
    for wd in text.split():
        lines[-1:] = [f"{lines[-1]} {wd}".strip()] if len(f"{lines[-1]} {wd}") <= n else [lines[-1], wd]
    return lines


def group(n: int) -> str:
    return LINE if n <= 3 else ORANGE if n <= 10 else BLUE if n <= 13 else GREEN


def overview(stages: list[dict], ms: list[dict], done: set[str]) -> str:
    """Stage cards in build order with hours, a progress bar and the next step."""
    per_row, w, h, gx, gy, x0, y0 = 6, 182, 104, 14, 14, 24, 92
    nxt = next_step(ms, done)
    total = sum(len(m["steps"]) for m in ms)
    hrs = sum(hours(s.get("time")) for m in ms for s in m["steps"])
    b = (f'<text x="24" y="36" class="t b" font-size="18">{len(stages)} stages · {len(ms)} milestones · {total} steps · '
         f'~{hrs:.0f} h hands-on</text>'
         f'<text x="24" y="58" class="m" font-size="13">{len(done & {s["id"] for m in ms for s in m["steps"]})} of {total} steps done</text>')
    if nxt:
        m, s = nxt
        b += (f'<rect x="560" y="18" width="616" height="52" rx="10" fill="{PANEL}" stroke="{ORANGE}" stroke-width="2"/>'
              f'<text x="576" y="40" fill="{ORANGE}" font-size="12" class="b">NEXT STEP</text>'
              f'<text x="576" y="60" class="t" font-size="14">{escape(s["id"])} · {escape(s["title"])}'
              f'{" · " + escape(s["time"]) if s.get("time") else ""}</text>'
              f'<text x="1160" y="40" class="m" font-size="12" text-anchor="end">{escape(m["id"])} {escape(m["title"][:38])}</text>')
    for i, st in enumerate(stages):
        n = int(st["folder"][:2])
        steps = [s for m in ms if m["stage"] == st["folder"] for s in m["steps"]]
        k = sum(s["id"] in done for s in steps)
        x, yy = x0 + (i % per_row) * (w + gx), y0 + (i // per_row) * (h + gy)
        col = group(n)
        here = nxt is not None and nxt[0]["stage"] == st["folder"]
        b += (f'<a href="../../phases/{st["folder"]}/README.md"><rect x="{x}" y="{yy}" width="{w}" height="{h}" rx="10" '
              f'fill="{PANEL}" stroke="{ORANGE if here else col}" stroke-width="{3 if here else 2}" opacity="0">'
              f'<animate attributeName="opacity" from="0" to="1" begin="{i * 0.06:.2f}s" dur="0.35s" fill="freeze"/></rect>')
        b += (f'<text x="{x + 12}" y="{yy + 21}" fill="{col if col != LINE else MUTED}" font-size="12" class="b">'
              f'{n:02d}{"  ✓" if steps and k == len(steps) else ""}</text>'
              f'<text x="{x + w - 12}" y="{yy + 21}" class="m" font-size="11" text-anchor="end">'
              f'{fmt_h(sum(hours(s.get("time")) for s in steps))}</text>')
        for j, ln in enumerate(_wrap(st["title"], 24)[:2]):
            b += f'<text x="{x + 12}" y="{yy + 41 + 16 * j}" class="t" font-size="13">{escape(ln)}</text>'
        bw = w - 24
        frac = k / len(steps) if steps else 0
        b += (f'<rect x="{x + 12}" y="{yy + h - 22}" width="{bw}" height="6" rx="3" fill="{LINE}"/>'
              f'<rect x="{x + 12}" y="{yy + h - 22}" width="{bw * frac:.1f}" height="6" rx="3" fill="{GREEN}"/>'
              f'<text x="{x + 12}" y="{yy + h - 30}" class="m" font-size="11">{k}/{len(steps)} steps</text></a>')
    rows = (len(stages) + per_row - 1) // per_row
    legend = [("setup", LINE), ("measure", ORANGE), ("3D scan", BLUE), ("app · standalone · release", GREEN)]
    ly = y0 + rows * (h + gy) + 8
    for i, (name, c) in enumerate(legend):
        b += f'<rect x="{24 + i * 150}" y="{ly}" width="12" height="12" rx="2" fill="{c}"/><text x="{42 + i * 150}" y="{ly + 11}" class="m" font-size="12">{name}</text>'
    b += f'<text x="1176" y="{ly + 11}" class="m" font-size="12" text-anchor="end">hours = hands-on time (printing, shipping, unattended runs not counted)</text>'
    return _svg(1200, ly + 28, b)


def stage(st: dict, ms: list[dict], done: set[str], nxt_id: str | None) -> str:
    """One row per milestone; its steps as chips in order, with time and state."""
    chip_w, chip_h, gap, per_line, left = 214, 58, 10, 4, 290
    y, b = 78, ""
    hrs = sum(hours(s.get("time")) for m in ms for s in m["steps"])
    b += (f'<text x="24" y="34" class="t b" font-size="18">{st["folder"][:2]} · {escape(st["title"])}</text>'
          f'<text x="24" y="56" class="m" font-size="13">{len(ms)} milestones · {sum(len(m["steps"]) for m in ms)} steps · '
          f'~{fmt_h(hrs)} hands-on · each chip is one GitHub issue</text>')
    for i, (label, c) in enumerate((("done", GREEN), ("next", ORANGE), ("to do", LINE))):
        b += f'<rect x="{900 + i * 90}" y="42" width="12" height="12" rx="3" fill="{c}"/><text x="{918 + i * 90}" y="53" class="m" font-size="12">{label}</text>'
    for m in ms:
        lines = (len(m["steps"]) + per_line - 1) // per_line
        row_h = lines * (chip_h + gap)
        b += f'<line x1="24" x2="1176" y1="{y - 8}" y2="{y - 8}" stroke="{LINE}" stroke-width="1"/>'
        b += f'<text x="24" y="{y + 18}" class="t b" font-size="14">{escape(m["id"])}</text>'
        for j, ln in enumerate(_wrap(m["title"], 30)[:2]):
            b += f'<text x="70" y="{y + 18 + 17 * j}" class="t" font-size="14">{escape(ln)}</text>'
        for j, ln in enumerate(_wrap(m["goal"], 40)[:2]):
            b += f'<text x="24" y="{y + 54 + 15 * j}" class="m" font-size="11">{escape(ln)}</text>'
        for k, s in enumerate(m["steps"]):
            x = left + (k % per_line) * (chip_w + gap)
            cy = y + (k // per_line) * (chip_h + gap)
            state = "done" if s["id"] in done else "next" if s["id"] == nxt_id else "todo"
            stroke = {"done": GREEN, "next": ORANGE, "todo": LINE}[state]
            fill = {"done": "#12261a", "next": "#2a1d10", "todo": PANEL}[state]
            b += (f'<rect x="{x}" y="{cy}" width="{chip_w}" height="{chip_h}" rx="9" fill="{fill}" stroke="{stroke}" '
                  f'stroke-width="{2.5 if state == "next" else 1.5}"/>')
            b += (f'<text x="{x + 10}" y="{cy + 19}" fill="{stroke if state != "todo" else MUTED}" font-size="11" class="b">'
                  f'{escape(s["id"])}{"  ✓" if state == "done" else "  ← next" if state == "next" else ""}</text>'
                  f'<text x="{x + chip_w - 10}" y="{cy + 19}" class="m" font-size="11" text-anchor="end">{escape(s.get("time", ""))}</text>')
            b += f'<text x="{x + 10}" y="{cy + 39}" class="t" font-size="13">{escape(s["title"][:27] + ("…" if len(s["title"]) > 27 else ""))}</text>'
            if s.get("wait"):
                b += f'<text x="{x + 10}" y="{cy + 53}" class="m" font-size="10">+ {escape(s["wait"][:32])}</text>'
            if k % per_line and k:
                b += f'<line x1="{x - gap}" x2="{x}" y1="{cy + chip_h / 2}" y2="{cy + chip_h / 2}" stroke="{LINE}" stroke-width="2"/>'
        y += max(row_h, 86) + 16
    return _svg(1200, y + 4, b)
