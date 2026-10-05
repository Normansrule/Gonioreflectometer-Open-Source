#!/usr/bin/env python3
"""Render every printed part (phases/*/3d/print/*.stl) into docs/assets/parts.png.  pip install numpy-stl matplotlib
SPDX-License-Identifier: GPL-3.0-or-later
"""
import glob
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402
from stl import mesh  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
files, seen = [], set()
for f in sorted(glob.glob(str(ROOT / "phases/*/3d/print/*.stl"))):
    stem = Path(f).stem.split("_", 1)[1]
    if stem not in seen:
        seen.add(stem)
        files.append(f)
cols = 6
rows = math.ceil(len(files) / cols)
fig = plt.figure(figsize=(cols * 2.6, rows * 2.6), facecolor="#0d1117")
for i, f in enumerate(files):
    v = mesh.Mesh.from_file(f).vectors
    ax = fig.add_subplot(rows, cols, i + 1, projection="3d")
    ax.set_facecolor("#0d1117")
    n = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
    n /= np.linalg.norm(n, axis=1)[:, None] + 1e-9
    shade = 0.35 + 0.65 * np.clip(n @ np.array([0.4, -0.5, 0.77]), 0, 1)
    ax.add_collection3d(Poly3DCollection(v, facecolors=np.c_[0.94 * shade, 0.53 * shade, 0.24 * shade, np.ones_like(shade)]))
    mn, mx = v.reshape(-1, 3).min(0), v.reshape(-1, 3).max(0)
    c, r = (mn + mx) / 2, (mx - mn).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.view_init(28, -55); ax.set_axis_off()
    ax.set_title(Path(f).stem.replace("_", " ", 1), color="#c9d1d9", fontsize=8)
plt.tight_layout()
plt.savefig(ROOT / "docs/assets/parts.png", dpi=80, facecolor="#0d1117")
print(len(files), "parts -> docs/assets/parts.png")
