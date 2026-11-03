#!/usr/bin/env python3
"""Pictures for PARTS.md (original drawings, no vendor photos): one line icon per kind of bought part,
a rendered thumbnail of every printed part (orange) and of every bought part's 3D model (blue-grey) from its STL
(parts more than 4 x longer than wide are drawn shortened, like a broken view).

    python tools/part_images.py           icons -> docs/assets/parts/icon-*.svg
    python tools/part_images.py --stl     also thumbnails -> docs/assets/parts/<file stem>.png (needs numpy-stl, matplotlib)

The store page behind each part's buy link has the real product photo.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "parts"
BG, LINE, INK, ACC, WARM = "#161b22", "#30363d", "#c9d1d9", "#58a6ff", "#f0883e"
S = f'fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"'
A = f'fill="none" stroke="{ACC}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"'
W = f'fill="none" stroke="{WARM}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"'

ICONS = {   # 96 x 96 drawings
    "psu": f'<rect x="18" y="30" width="44" height="34" rx="6" {S}/><path d="M62 47h14M76 47c8 0 8 14 0 14" {S}/><text x="40" y="52" fill="{WARM}" font-size="13" text-anchor="middle" font-family="sans-serif">24V</text>',
    "battery": f'<rect x="16" y="30" width="58" height="36" rx="5" {S}/><rect x="74" y="40" width="7" height="16" rx="2" {S}/><path d="M26 48h10M31 43v10" {W}/><path d="M54 48h10" {A}/>',
    "cable": f'<path d="M14 66c18 0 18-36 36-36s18 36 34 36" {S}/><rect x="8" y="60" width="12" height="12" rx="2" {A}/><rect x="78" y="60" width="12" height="12" rx="2" {A}/>',
    "jack": f'<circle cx="48" cy="48" r="20" {S}/><circle cx="48" cy="48" r="6" {A}/><path d="M48 68v14M40 82h16" {S}/>',
    "fuse": f'<rect x="20" y="38" width="56" height="20" rx="10" {S}/><path d="M8 48h12M76 48h12M28 48c6-8 10 8 16 0s10 8 16 0 10 8 12 0" {W}/>',
    "transistor": f'<rect x="28" y="20" width="40" height="34" rx="3" {S}/><circle cx="48" cy="30" r="5" {S}/><path d="M36 54v26M48 54v26M60 54v26" {A}/>',
    "diode": f'<path d="M10 48h22M64 48h22" {S}/><path d="M32 32v32l26-16z" {S}/><path d="M60 32v32" {W}/>',
    "capacitor": f'<rect x="30" y="16" width="36" height="52" rx="8" {S}/><path d="M42 68v14M54 68v14" {A}/><path d="M36 24h8" {W}/>',
    "switch": f'<rect x="24" y="30" width="48" height="36" rx="6" {S}/><path d="M36 60l24-20" {W}/><circle cx="36" cy="60" r="4" {A}/>',
    "estop": f'<circle cx="48" cy="46" r="26" fill="none" stroke="{WARM}" stroke-width="5"/><circle cx="48" cy="46" r="14" {S}/><rect x="26" y="74" width="44" height="10" rx="3" {S}/>',
    "wire": f'<path d="M10 40c20-14 40 14 76 0" fill="none" stroke="#f85149" stroke-width="4"/><path d="M10 56c20-14 40 14 76 0" fill="none" stroke="{INK}" stroke-width="4"/>',
    "board": f'<rect x="14" y="22" width="68" height="52" rx="5" {S}/><rect x="36" y="38" width="22" height="20" rx="2" {A}/>' + "".join(f'<circle cx="{22 + 8 * i}" cy="30" r="2" fill="{INK}"/>' for i in range(8)),
    "tube": f'<rect x="12" y="34" width="72" height="12" rx="6" {S}/><rect x="20" y="54" width="56" height="10" rx="5" {A}/><rect x="30" y="70" width="36" height="8" rx="4" {W}/>',
    "button": f'<rect x="20" y="52" width="56" height="18" rx="4" {S}/><rect x="34" y="34" width="28" height="18" rx="6" {W}/><path d="M40 70v12M56 70v12" {A}/>',
    "fan": f'<rect x="16" y="16" width="64" height="64" rx="8" {S}/><circle cx="48" cy="48" r="8" {A}/><path d="M48 40c-4-14 10-18 14-10M56 48c14-4 18 10 10 14M48 56c4 14-10 18-14 10M40 48c-14 4-18-10-10-14" {S}/>',
    "laptop": f'<rect x="22" y="24" width="52" height="34" rx="3" {S}/><path d="M12 66h72l-6 8H18z" {S}/><path d="M30 36h20" {A}/>',
    "hardware": f'<path d="M30 20h20v10H30z" {S}/><path d="M40 30v46" {S}/><path d="M34 38h12M34 46h12M34 54h12M34 62h12" {A}/><path d="M60 52l8-8h10l8 8-8 8H68z" {W}/><circle cx="73" cy="52" r="3" {S}/>',
    "bearing": f'<circle cx="48" cy="48" r="30" {S}/><circle cx="48" cy="48" r="12" {S}/>' + "".join(f'<circle cx="{48 + 21 * c:.1f}" cy="{48 + 21 * s:.1f}" r="4" fill="{ACC}"/>' for c, s in ((1, 0), (0.5, 0.87), (-0.5, 0.87), (-1, 0), (-0.5, -0.87), (0.5, -0.87))),
    "turntable": f'<ellipse cx="48" cy="44" rx="34" ry="12" {S}/><ellipse cx="48" cy="56" rx="34" ry="12" {S}/><ellipse cx="48" cy="50" rx="22" ry="7" {A}/>',
    "motor": f'<rect x="22" y="26" width="44" height="44" rx="4" {S}/><circle cx="44" cy="48" r="10" {A}/><path d="M66 48h18" fill="none" stroke="{WARM}" stroke-width="5" stroke-linecap="round"/>',
    "belt": f'<rect x="12" y="32" width="72" height="32" rx="16" {S}/>' + "".join(f'<path d="M{20 + 7 * i} 32v-4" {A}/>' for i in range(9)),
    "pulley": f'<circle cx="48" cy="48" r="24" {S}/>' + "".join(f'<path d="M{48 + 24 * c:.1f} {48 + 24 * s:.1f}l{4 * c:.1f} {4 * s:.1f}" {A}/>' for c, s in [(__import__("math").cos(k * 0.314), __import__("math").sin(k * 0.314)) for k in range(20)]) + f'<circle cx="48" cy="48" r="5" {W}/>',
    "endstop": f'<path d="M24 64V30h14v34M58 64V30h14v34" {S}/><rect x="18" y="64" width="60" height="12" rx="2" {S}/><path d="M48 20v40" {W}/>',
    "shaft": f'<rect x="10" y="42" width="76" height="12" rx="6" {S}/><path d="M18 42v12M78 42v12" {A}/>',
    "laser": f'<rect x="12" y="40" width="40" height="16" rx="8" {S}/><path d="M52 48h34" fill="none" stroke="#f85149" stroke-width="3" stroke-dasharray="6 4"/>',
    "camera": f'<rect x="18" y="22" width="52" height="52" rx="6" {S}/><circle cx="44" cy="48" r="14" {A}/><circle cx="44" cy="48" r="5" {S}/><path d="M70 40h12v16H70" {S}/>',
    "lens": f'<rect x="28" y="20" width="40" height="56" rx="6" {S}/><path d="M28 34h40M28 62h40" {A}/><ellipse cx="48" cy="20" rx="14" ry="4" {W}/>',
    "led": f'<polygon points="48,14 76,30 76,62 48,78 20,62 20,30" {S}/><circle cx="48" cy="46" r="12" fill="{WARM}" opacity=".85"/>',
    "driver": f'<rect x="16" y="30" width="64" height="36" rx="4" {S}/><path d="M24 48h10l4-8 6 16 4-8h10" {A}/><path d="M66 40v16" {W}/>',
    "heatsink": f'<rect x="16" y="62" width="64" height="12" rx="2" {S}/>' + "".join(f'<path d="M{22 + 10 * i} 62V24" {S}/>' for i in range(7)),
    "tape": f'<circle cx="48" cy="48" r="28" {S}/><circle cx="48" cy="48" r="12" {S}/><path d="M76 48h12v20" {A}/>',
    "fabric": f'<path d="M16 22h64v44c-10 8-22-8-32 0s-22-8-32 0z" fill="#0b0f14" stroke="{INK}" stroke-width="3"/>',
    "dowel": f'<path d="M30 14l36 68" fill="none" stroke="{WARM}" stroke-width="8" stroke-linecap="round"/>',
    "plate": f'<path d="M14 42l34-16 34 16-34 16z" fill="#f0f6fc" stroke="{INK}" stroke-width="2"/><path d="M14 42v10l34 16 34-16V42" {S}/>',
    "mirror": f'<rect x="18" y="18" width="60" height="60" rx="4" fill="#1f6feb" fill-opacity=".25" stroke="{INK}" stroke-width="3"/><path d="M28 60l24-30M40 66l20-24" fill="none" stroke="#f0f6fc" stroke-width="3" opacity=".7"/>',
    "ball": f'<circle cx="34" cy="50" r="18" {S}/><circle cx="64" cy="50" r="18" {S}/><circle cx="28" cy="44" r="4" fill="#f0f6fc"/><circle cx="58" cy="44" r="4" fill="#f0f6fc"/>',
    "chart": f'<rect x="16" y="20" width="64" height="56" rx="3" {S}/>' + "".join(f'<rect x="{22 + 13 * (k % 4)}" y="{26 + 16 * (k // 4)}" width="10" height="10" fill="{c}"/>' for k, c in enumerate(["#f0f6fc", "#8b949e", "#30363d", "#f85149", "#3fb950", "#58a6ff", "#e3b341", "#bc8cff", "#0d1117", "#f0883e", "#c9d1d9", "#6e7681"])),
    "film": f'<rect x="18" y="18" width="60" height="60" rx="3" fill="#30363d" fill-opacity=".6" stroke="{INK}" stroke-width="3"/>' + "".join(f'<path d="M{26 + 8 * i} 22v52" fill="none" stroke="{ACC}" stroke-width="1.5"/>' for i in range(6)),
    "putty": f'<path d="M20 64c0-20 12-30 28-30s28 10 28 30z" fill="#e3b341" fill-opacity=".35" stroke="{INK}" stroke-width="3"/>',
    "sd": f'<path d="M28 16h30l12 12v52H28z" {S}/><path d="M36 16v10M44 16v10M52 16v10" {A}/>',
    "screen": f'<rect x="16" y="26" width="64" height="44" rx="4" {S}/><rect x="24" y="34" width="48" height="24" fill="#0b0f14" stroke="{ACC}" stroke-width="2"/><path d="M30 42h20M30 50h30" fill="none" stroke="{ACC}" stroke-width="2"/>',
    "keypad": f'<rect x="12" y="24" width="72" height="30" rx="4" {S}/>' + "".join(f'<rect x="{18 + 17 * i}" y="31" width="11" height="16" rx="2" {A}/>' for i in range(4)) + f'<path d="M44 54v24M48 54v24M52 54v24" {S}/>',
    "jumper": f'<rect x="10" y="40" width="14" height="16" rx="2" {S}/><path d="M24 48c16 0 16-22 32-22s14 22 20 22" {A}/><rect x="72" y="42" width="14" height="12" rx="2" {S}/><path d="M86 48h4" {S}/>',
    "lever": f'<rect x="18" y="40" width="60" height="30" rx="5" {S}/><path d="M26 40l10-18h8l-8 18M52 40l10-18h8l-8 18" {A}/><path d="M6 60h12M78 60h12" {S}/>',
    "holder": f'<rect x="20" y="20" width="56" height="56" rx="10" {S}/><rect x="36" y="36" width="24" height="24" rx="2" fill="{WARM}" opacity=".7"/><path d="M76 34h12M76 62h12" {A}/>',
    "printer": f'<path d="M16 20h64v60H16z" {S}/><path d="M16 30h64" {S}/><path d="M40 30v14h16V30" {A}/><path d="M48 44v8" {A}/><rect x="30" y="64" width="36" height="8" fill="{WARM}" opacity=".7"/>',
    "screwdriver": f'<rect x="14" y="40" width="30" height="16" rx="6" {S}/><path d="M44 48h34" {A}/><path d="M78 44l8 4-8 4z" {A}/>',
    "hexkey": f'<path d="M24 22v42q0 10 10 10h40" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/><path d="M24 22v42q0 10 10 10h40" fill="none" stroke="{ACC}" stroke-width="2"/>',
    "stripper": f'<path d="M20 80l24-34M76 80L52 46" {S}/><path d="M44 46l4-30 4 30z" {A}/><circle cx="48" cy="40" r="3" fill="{WARM}"/>',
    "meter": f'<rect x="24" y="14" width="48" height="68" rx="8" {S}/><rect x="32" y="22" width="32" height="16" fill="#0b0f14" stroke="{ACC}" stroke-width="2"/><circle cx="48" cy="58" r="10" {A}/><path d="M48 58l6-6" {A}/>',
    "caliper": f'<path d="M14 30h68v10H14z" {S}/><path d="M20 40v30l8-6V40M40 40v26l8-4V40" {A}/><rect x="36" y="22" width="20" height="8" fill="{WARM}" opacity=".7"/>',
    "ruler": f'<rect x="12" y="36" width="72" height="24" rx="3" {S}/>' + "".join(f'<path d="M{18 + 8 * i} 36v{8 if i % 2 else 12}" {A}/>' for i in range(9)),
    "paper": f'<path d="M26 14h32l12 12v56H26z" {S}/><path d="M34 40h28M34 50h28M34 60h20" {A}/><path d="M48 66v-8" {S}/>',
}

KIND = {  # part ID -> icon kind (printed parts use their STL thumbnail instead)
    "PWR-30": "psu", "PWR-28": "estop", "PWR-10": "board",
     "PWR-15": "wire", "PWR-20": "lever",
    "CTL-01": "board", "CTL-02": "board", "CTL-03": "cable", "CTL-04": "cable", "CTL-05": "keypad", "CTL-06": "cable",
    "CTL-07": "jumper", "CTL-08": "fan", "CTL-09": "laptop", "FRM-07": "hardware",
    "FRM-08": "bearing", "LAR-01": "turntable", "LAR-03": "belt", "LAR-06": "switch", "LAR-09": "laser",
    "CAM-01": "camera", "CAM-02": "lens", "CAM-04": "camera", "CAM-05": "lens",
    "LSR-01": "led", "LSR-02": "driver", "LSR-06": "holder", "LSR-03": "heatsink", "LSR-04": "tape", "ENC-01": "fabric", "ENC-02": "fabric",
    "ENC-03": "dowel", "ENC-05": "fabric", "CAL-01": "plate", "CAL-02": "mirror", "CAL-03": "ball", "CAL-04": "chart",
    "CAL-05": "chart", "CAL-07": "chart", "MSK-01": "led", "MSK-02": "driver", "MSK-03": "board", "MSK-04": "heatsink",
    "MSK-05": "film", "SPC-01": "board", "SPC-02": "cable", "SCN-01": "putty", "SCN-02": "chart",
    "STA-01": "board", "STA-02": "sd", "STA-03": "driver", "STA-04": "cable", "STA-05": "screen", "STA-06": "jumper", "STA-08": "cable", "CTL-11": "cable", "TBL-05": "hardware", "TLT-05": "hardware",
    "TLS-01": "printer", "TLS-02": "screwdriver", "TLS-03": "hexkey", "TLS-04": "stripper", "TLS-05": "meter",
    "TLS-06": "caliper", "TLS-07": "ruler", "TLS-08": "printer", "TLS-11": "paper", "TLS-09": "tape", "TLS-10": "hexkey",
}
SUFFIX = {"-01": "motor", "-02": "belt", "-03": "pulley", "-04": "endstop", "-05": "shaft", "-06": "hardware"}


def kind(pid: str) -> str:
    if pid in KIND:
        return KIND[pid]
    if pid[:3] in ("TBL", "TLT", "SPN") or pid in ("LAR-02", "LAR-04", "LAR-05"):
        return {"LAR-02": "motor", "LAR-04": "pulley", "LAR-05": "endstop"}.get(pid) or SUFFIX.get(pid[3:], "hardware")
    return "hardware"


def image_for(row: dict) -> str:
    """Repo-relative picture path for a parts-list row."""
    if row["Type"] == "Print":
        step = row.get("STEP", "").split(";")[0].strip()
        if step.startswith("3d/"):
            return f"docs/assets/parts/{Path(step).stem}.png"
    return f"docs/assets/parts/icon-{kind(row['ID'])}.svg"


def write_icons() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, body in ICONS.items():
        (OUT / f"icon-{name}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96">'
            f'<rect width="96" height="96" rx="14" fill="{BG}" stroke="{LINE}"/>{body}</svg>\n', encoding="utf-8")
    return len(ICONS)


def write_thumbs() -> int:
    import glob

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from stl import mesh
    n = 0
    files = [(f, (0.94, 0.53, 0.24)) for f in sorted(glob.glob(str(ROOT / "phases/*/3d/*.stl")))]
    files += [(f, (0.55, 0.68, 0.85)) for f in sorted(glob.glob(str(ROOT / "cad/bought/*.stl")))]
    for f, (cr, cg, cb) in files:
        v = mesh.Mesh.from_file(f).vectors.copy()
        mn, ext = v.reshape(-1, 3).min(0), np.ptp(v.reshape(-1, 3), 0)
        k, second = int(ext.argmax()), np.sort(ext)[-2]
        if ext[k] > 4 * second > 0:                     # long part (cable, belt, extrusion): draw it shortened
            v[..., k] = mn[k] + (v[..., k] - mn[k]) * (4 * second / ext[k])
        fig = plt.figure(figsize=(1.6, 1.6), facecolor=BG)
        ax = fig.add_subplot(projection="3d")
        ax.set_facecolor(BG)
        nrm = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
        nrm /= np.linalg.norm(nrm, axis=1)[:, None] + 1e-9
        shade = 0.35 + 0.65 * np.clip(nrm @ np.array([0.4, -0.5, 0.77]), 0, 1)
        ax.add_collection3d(Poly3DCollection(v, facecolors=np.c_[cr * shade, cg * shade, cb * shade, np.ones_like(shade)]))
        mn, mx = v.reshape(-1, 3).min(0), v.reshape(-1, 3).max(0)
        c, r = (mn + mx) / 2, (mx - mn).max() / 2
        ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
        ax.view_init(28, -55); ax.set_axis_off()
        fig.subplots_adjust(0, 0, 1, 1)
        fig.savefig(OUT / f"{Path(f).stem}.png", dpi=60, facecolor=BG)
        plt.close(fig)
        n += 1
    return n


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stl", action="store_true")
    a = ap.parse_args()
    print(f"{write_icons()} icons" + (f", {write_thumbs()} thumbnails (printed + bought)" if a.stl else "") + f" -> {OUT.relative_to(ROOT)}")
