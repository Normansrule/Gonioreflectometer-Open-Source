#!/usr/bin/env python3
"""software/config/machine.yaml -> docs/machine.js, so the web simulator uses the same dimensions and limits
as the software. Run by `make build`; `make check` fails if the two disagree. SPDX-License-Identifier: GPL-3.0-or-later"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "software" / "src"))
from opengonio.gantry.config import load_config  # noqa: E402

OUT = ROOT / "docs" / "machine.js"


def sim_numbers() -> dict:
    c = load_config()
    return {"Dc": c.camera_distance_mm, "Dgonio": c.camera_distance_mm, "Dscan": float(c.scan["camera_distance_mm"]),
            "scanElev": float(c.scan.get("camera_elevation_deg", 0.0)),
            "twoCams": c.for_scan().camera.get("index") != c.camera.get("index"),
            "Dl": c.light_distance_mm, "ring": c.ring_radius_mm, "rc": c.camera_head_radius_mm,
            "rl": c.lamp_head_radius_mm, "ra": c.arm_radius_mm, "keep": c.keep_out_mm, "minA": c.min_phase_angle_deg,
            "axes": {k: [a.min_deg, a.max_deg] for k, a in c.axes.items()}}


def text() -> str:
    return ("// Generated from software/config/machine.yaml by tools/export_machine.py — do not edit; run `make`.\n"
            f"window.MACHINE = {json.dumps(sim_numbers(), sort_keys=True)};\n")


if __name__ == "__main__":
    OUT.write_text(text(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
