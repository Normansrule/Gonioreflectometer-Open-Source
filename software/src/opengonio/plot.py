"""Small SVG line charts for measurement folders (curve.svg, fit.svg), no plotting library needed.

Style matches docs/assets: dark surface, one blue hue stepped light -> dark for ordered series (theta_i),
validated as an ordinal ramp on the dark surface; 2 px lines, 8 px markers with a surface ring,
hairline grid, one y axis, direct labels at the line ends, hover titles when the SVG is opened directly.
"""
from __future__ import annotations

import math
from html import escape

SURFACE, GRID, TEXT, MUTED = "#0d1117", "#21262d", "#e6edf3", "#8b949e"
RAMP = ["#9ec5f4", "#6da7ec", "#3987e5", "#256abf"]          # ordinal blue, light -> dark (max 4 series)
ACCENT = "#f0883e"                                             # reference line (e.g. M3 = M4/2)


def _ticks(lo: float, hi: float, n: int = 5) -> list[float]:
    if hi <= lo:
        hi = lo + 1
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw))
    step = min((s * mag for s in (1, 2, 2.5, 5, 10) if s * mag >= raw), default=raw)
    t = math.ceil(lo / step) * step
    out = []
    while t <= hi + 1e-9:
        out.append(round(t, 10))
        t += step
    return out


def _fmt(v: float) -> str:
    return f"{v:.3g}" if abs(v) < 1000 else f"{v:.0f}"


def line_chart(series: list[dict], title: str, xlabel: str, ylabel: str, note: str = "",
               vline: tuple[float, str] | None = None, w: int = 760, h: int = 420) -> str:
    """series: [{"label": str, "points": [(x, y)], "line": [(x, y)] (optional model curve)}], at most 4.
    Points are drawn as dots; `line` (or the points themselves when absent) as a 2 px line."""
    series = series[:4]
    L, R, T, B = 64, 40, 84, 52
    xs = [p[0] for s in series for p in s["points"] + s.get("line", [])]
    ys = [p[1] for s in series for p in s["points"] + s.get("line", [])]
    if vline:
        xs.append(vline[0])
    if not xs:
        xs, ys = [0, 1], [0, 1]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(0.0, min(ys)), max(ys) * 1.08 or 1.0
    X = lambda x: L + (x - x0) / ((x1 - x0) or 1) * (w - L - R)      # noqa: E731
    Y = lambda y: h - B - (y - y0) / ((y1 - y0) or 1) * (h - T - B)  # noqa: E731
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="Segoe UI,Helvetica,Arial,sans-serif">',
         f'<rect width="{w}" height="{h}" rx="10" fill="{SURFACE}"/>',
         f'<text x="{L}" y="28" fill="{TEXT}" font-size="16" font-weight="600">{escape(title)}</text>']
    if note:
        o.append(f'<text x="{L}" y="47" fill="{MUTED}" font-size="12">{escape(note)}</text>')
    for t in _ticks(y0, y1):
        o.append(f'<line x1="{L}" x2="{w - R}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" stroke="{GRID}" stroke-width="1"/>'
                 f'<text x="{L - 8}" y="{Y(t) + 4:.1f}" fill="{MUTED}" font-size="11" text-anchor="end">{_fmt(t)}</text>')
    for t in _ticks(x0, x1, 8):
        o.append(f'<text x="{X(t):.1f}" y="{h - B + 18}" fill="{MUTED}" font-size="11" text-anchor="middle">{_fmt(t)}</text>')
    o.append(f'<text x="{(L + w - R) / 2}" y="{h - 12}" fill="{MUTED}" font-size="12" text-anchor="middle">{escape(xlabel)}</text>'
             f'<text x="16" y="{(T + h - B) / 2}" fill="{MUTED}" font-size="12" text-anchor="middle" '
             f'transform="rotate(-90 16 {(T + h - B) / 2})">{escape(ylabel)}</text>')
    if vline:
        o.append(f'<line x1="{X(vline[0]):.1f}" x2="{X(vline[0]):.1f}" y1="{T - 8}" y2="{h - B}" stroke="{ACCENT}" stroke-width="1.5"/>'
                 f'<text x="{X(vline[0]) + 6:.1f}" y="{T - 2}" fill="{TEXT}" font-size="11">{escape(vline[1])}</text>')
    # legend row (always for >= 2 series), keys carry the colour, text stays in text ink
    if len(series) > 1 or any("line" in s for s in series):
        lx = L
        for k, s in enumerate(series):
            c = RAMP[k if len(series) > 1 else 2]
            o.append(f'<line x1="{lx}" x2="{lx + 16}" y1="58" y2="58" stroke="{c}" stroke-width="2"/>'
                     f'<circle cx="{lx + 8}" cy="58" r="4" fill="{c}" stroke="{SURFACE}" stroke-width="2"/>'
                     f'<text x="{lx + 22}" y="62" fill="{TEXT}" font-size="12">{escape(s["label"])}</text>')
            lx += 30 + 7 * len(s["label"])
        if any("line" in s for s in series):
            o.append(f'<text x="{w - R}" y="62" fill="{MUTED}" font-size="12" text-anchor="end">dots measured · line fitted</text>')
    placed: list[tuple[float, float]] = []
    for k, s in enumerate(series):
        c = RAMP[k if len(series) > 1 else 2]
        line = sorted(s.get("line") or s["points"])
        if len(line) > 1:
            d = " ".join(f"{'M' if i == 0 else 'L'}{X(x):.1f},{Y(y):.1f}" for i, (x, y) in enumerate(line))
            o.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>')
        for x, y in s["points"]:
            o.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="4" fill="{c}" stroke="{SURFACE}" stroke-width="2">'
                     f'<title>{escape(s["label"])}: {xlabel.split(" (")[0]} {_fmt(x)}, {_fmt(y)}</title></circle>')
        if line and len(series) > 1:                    # direct label above the peak; skipped if it would collide
            px, py = max(line, key=lambda p: p[1])
            lx, ly = X(px), Y(py) - 10
            if all(abs(lx - a) > 40 or abs(ly - b) > 14 for a, b in placed):
                placed.append((lx, ly))
                o.append(f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{TEXT}" font-size="11" text-anchor="middle">{escape(s["label"])}</text>')
    o.append(f'<line x1="{L}" x2="{w - R}" y1="{Y(y0):.1f}" y2="{Y(y0):.1f}" stroke="{MUTED}" stroke-width="1"/></svg>')
    return "\n".join(o) + "\n"
