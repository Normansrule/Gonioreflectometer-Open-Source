"""Animated 3D drawing of the four-axis machine (after [R1]) as SVG/SMIL.

Zero point = origin, +Z up, camera fixed on +X. R = Rz(M3) Ry(-M2) Rx(M1); sample normal = local x.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import math

import numpy as np

BASE_Z, RING_R, LIGHT_D, CAM_D, POST_TOP, YOKE_W, SAMPLE = -150.0, 150.0, 300.0, 350.0, -70.0, 58.0, 40.0
ORANGE, BLUE, YELLOW, PURPLE, GREEN, GREY, PANEL, LINE, TXT = (
    "#f0883e", "#58a6ff", "#e3b341", "#bc8cff", "#3fb950", "#8b949e", "#161b22", "#30363d", "#f0f6fc")


def _r(axis: str, deg: float) -> np.ndarray:
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return {"x": np.array([[1, 0, 0], [0, c, -s], [0, s, c]]),
            "y": np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]),
            "z": np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])}[axis]


def demo_poses(n: int = 96) -> tuple[list[dict], list[str]]:
    """Each axis moves in turn (M4, M3, M2, M1), then returns: one 16 s loop."""
    base = {"M4": 70.0, "M3": 35.0, "M2": 0.0, "M1": 0.0}
    swing = {"M4": 70.0, "M3": 40.0, "M2": 35.0, "M1": 90.0}
    order = ["M4", "M3", "M2", "M1"]
    poses, active = [], []
    for k in range(n):
        t = k / n * len(order)
        ax, u = order[int(t)], t - int(t)
        p = dict(base)
        wave = math.sin(2 * math.pi * u) if ax == "M2" else math.sin(math.pi * u) ** 2
        p[ax] = base[ax] + swing[ax] * wave
        poses.append(p)
        active.append(ax)
    return poses, active


class View:
    def __init__(self, cx: float, cy: float, k: float, yaw: float = -70.0, pitch: float = 24.0):
        self.cx, self.cy, self.k, self.yaw, self.pitch = cx, cy, k, yaw, pitch

    def p(self, v) -> tuple[float, float]:
        a = _r("z", self.yaw) @ np.asarray(v, float)
        cp, sp = math.cos(math.radians(self.pitch)), math.sin(math.radians(self.pitch))
        return self.cx + a[0] * self.k, self.cy - (a[1] * sp + a[2] * cp) * self.k


def _pts(view: View, pts) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in (view.p(q) for q in pts))


def _circle(c, u, v, r, n=28):
    return [np.asarray(c) + r * (math.cos(a) * np.asarray(u) + math.sin(a) * np.asarray(v))
            for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def _shapes(p: dict) -> dict[str, list]:
    """World-space point lists for every moving part at pose p."""
    R = _r("z", p["M3"]) @ _r("y", -p["M2"]) @ _r("x", p["M1"])
    n, u, w = R[:, 0], R[:, 1], R[:, 2]
    yaw = _r("z", p["M3"])
    ay = yaw[:, 1]                                   # tilt axis
    l = _r("z", p["M4"]) @ np.array([1.0, 0, 0])
    lamp = LIGHT_D * l
    back = -6 * n
    return {
        "arm": [RING_R * l + [0, 0, BASE_Z + 12], (LIGHT_D + 30) * l + [0, 0, BASE_Z + 12], (LIGHT_D + 30) * l, lamp],
        "lamp": _circle(lamp, np.cross([0, 0, 1], l), [0, 0, 1], 13, 16),
        "beam": [lamp, [0, 0, 0]],
        "yoke": [YOKE_W * ay, YOKE_W * ay + [0, 0, POST_TOP], -YOKE_W * ay + [0, 0, POST_TOP], -YOKE_W * ay],
        "pivots": [YOKE_W * ay, -YOKE_W * ay],
        "disk": _circle(back, u, w, 50),
        "sample": [SAMPLE * (a * u + b * w) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))],
        "stripe": [-SAMPLE * u * 0.9, SAMPLE * u * 0.9],
        "normal": [[0, 0, 0], 75 * n],
    }


def machine(view: View, poses: list[dict], active: list[str], dur: float = 16.0,
            labels: tuple[float, float] | None = None) -> str:
    frames = [_shapes(p) for p in poses] + [_shapes(poses[0])]
    kt = ";".join(f"{i / (len(frames) - 1):.4f}" for i in range(len(frames)))

    def anim(key, tag="polygon", **style) -> str:
        vals = ";".join(_pts(view, f[key]) for f in frames)
        attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in style.items())
        return (f'<{tag} points="{_pts(view, frames[0][key])}" {attrs}>'
                f'<animate attributeName="points" values="{vals}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/></{tag}>')

    s = []
    # base, ring, post, camera (fixed)
    s.append(f'<polygon points="{_pts(view, [[-200, -200, BASE_Z], [420, -200, BASE_Z], [420, 200, BASE_Z], [-200, 200, BASE_Z]])}" fill="#1c2128" stroke="{LINE}"/>')
    s.append(f'<polygon points="{_pts(view, _circle([0, 0, BASE_Z + 6], [1, 0, 0], [0, 1, 0], RING_R, 60))}" fill="none" stroke="#57606a" stroke-width="5"/>')
    s.append(f'<polygon points="{_pts(view, _circle([0, 0, BASE_Z + 6], [1, 0, 0], [0, 1, 0], RING_R - 14, 60))}" fill="none" stroke="{LINE}" stroke-width="2"/>')
    cam = np.array([CAM_D, 0, 0])
    s.append(f'<polyline points="{_pts(view, [cam + [25, 0, BASE_Z - cam[2]], cam + [25, 0, -20]])}" stroke="#57606a" stroke-width="7" fill="none"/>')
    box = [cam + [d, a, b] for d, a, b in ((0, -22, -18), (0, 22, -18), (0, 22, 18), (0, -22, 18))]
    s.append(f'<polygon points="{_pts(view, [cam + [50, 0, 0] + (q - cam) for q in box])}" fill="#0d1117" stroke="{BLUE}" stroke-width="1.5"/>')
    s.append(f'<polygon points="{_pts(view, box)}" fill="{PANEL}" stroke="{BLUE}" stroke-width="2"/>')
    s.append(f'<polyline points="{_pts(view, [[0, 0, 0], cam])}" stroke="{BLUE}" stroke-width="2" stroke-dasharray="7 5" fill="none"/>')
    # light arm (M4)
    s.append(anim("arm", "polyline", stroke=GREY, stroke_width=6, fill="none", stroke_linejoin="round"))
    s.append(anim("beam", "polyline", stroke=YELLOW, stroke_width=2, stroke_dasharray="7 5", fill="none"))
    lx_ = ";".join(f"{view.p(f['beam'][0])[0]:.1f}" for f in frames)
    ly_ = ";".join(f"{view.p(f['beam'][0])[1]:.1f}" for f in frames)
    c0 = view.p(frames[0]["beam"][0])
    s.append(f'<circle cx="{c0[0]:.1f}" cy="{c0[1]:.1f}" r="11" fill="{YELLOW}" stroke="#fff3c4">'
             f'<animate attributeName="cx" values="{lx_}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/>'
             f'<animate attributeName="cy" values="{ly_}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/></circle>')
    # centre post + yoke (M3 turns it, M2 tilts the plate inside it)
    s.append(f'<polyline points="{_pts(view, [[0, 0, BASE_Z + 6], [0, 0, POST_TOP]])}" stroke="#6e7681" stroke-width="10" fill="none"/>')
    s.append(anim("yoke", "polyline", stroke=PURPLE, stroke_width=6, fill="none", stroke_linejoin="round"))
    s.append(anim("disk", fill="#2d333b", stroke=GREEN, stroke_width=1.5))
    s.append(anim("sample", fill=ORANGE, fill_opacity="0.92", stroke="#ffb27a", stroke_width=1.5))
    s.append(anim("stripe", "polyline", stroke="#7a3a10", stroke_width=4, fill="none"))
    s.append(anim("normal", "polyline", stroke=TXT, stroke_width=1.5, stroke_dasharray="3 4", fill="none"))
    s.append(anim("pivots", "polyline", stroke="none", fill="none"))
    x0, y0 = view.p([0, 0, 0])
    s.append(f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="3" fill="{TXT}"/>')
    if labels:
        lx, ly = labels
        names = [("M4", "light arm", YELLOW), ("M3", "table turns", PURPLE), ("M2", "sample tilts", PURPLE), ("M1", "sample spins", GREEN)]
        for i, (ax, txt, col) in enumerate(names):
            ops = ";".join("1" if a == ax else "0.35" for a in active + [active[0]])
            s.append(f'<g opacity="1"><animate attributeName="opacity" values="{ops}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/>'
                     f'<text x="{lx}" y="{ly + 26 * i}" fill="{col}" font-size="15" font-weight="600">{ax}</text>'
                     f'<text x="{lx + 40}" y="{ly + 26 * i}" fill="{TXT}" font-size="14">{txt}</text></g>')
    return "\n".join(s)

