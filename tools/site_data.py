#!/usr/bin/env python3
"""docs/site-data.js: the numbers the website shows, from the repo's sources of truth (run by `make build`).

    python tools/site_data.py

Stages and hours: .github/phases.yml · costs and cap: phases/*/bom.csv (tools/bom_check.py) · evidence: the README
Status table · CAD part count: docs/og/model/rig.js. The page reads window.SITE; nothing on it is typed in twice.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bom_check  # noqa: E402
import roadmap  # noqa: E402
import roadmap_svg  # noqa: E402

OUT = ROOT / "docs" / "site-data.js"


def evidence() -> list[dict]:
    """README Status table -> [{claim, evidence}]: the honest state of every capability."""
    t = (ROOT / "README.md").read_text(encoding="utf-8")
    block = t.split("## Status", 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in block.splitlines():
        m = re.match(r"^\| (?!Capability|---)(.+?) \| (.+?) \|$", line.strip())
        if m:
            rows.append({"claim": re.sub(r"\*\*(.+?)\*\*", r"\1", m[1]), "evidence": re.sub(r"\*\*(.+?)\*\*", r"\1", m[2])})
    return rows


def data() -> dict:
    stages, ms = roadmap.load()
    cost = roadmap.costs()
    out = []
    for st in stages:
        mine = [m for m in ms if m["stage"] == st["folder"]]
        steps = [s for m in mine for s in m["steps"]]
        out.append({"id": st["folder"][:2], "folder": st["folder"], "title": st["title"],
                    "goal": mine[0]["goal"] if mine else "",
                    "milestones": [m["title"] for m in mine], "steps": len(steps),
                    "hours": round(sum(roadmap_svg.hours(s.get("time")) for s in steps), 1),
                    "cost": round(cost.get(st["folder"], 0.0), 2)})
    totals = bom_check.totals(bom_check.load())
    return {"stages": out, "plan_usd": round(sum(v["buy"] for v in totals.values()), 2), "cap_usd": bom_check.HARD_CAP,
            "steps": sum(s["steps"] for s in out), "hours": round(sum(s["hours"] for s in out), 1),
            "parts": cad_parts(), "evidence": evidence()}


def cad_parts() -> int:
    """Parts in the CAD assembly, from the website model's own header (docs/og/model/rig.js, written by `make cad`)."""
    f = ROOT / "docs" / "og" / "model" / "rig.js"
    m = re.search(r'"parts":(\d+)', f.read_text(encoding="utf-8")[:4000]) if f.exists() else None
    return int(m[1]) if m else 0


def main() -> int:
    d = data()
    OUT.write_text("// Written by tools/site_data.py (`make build`): do not edit by hand.\nwindow.SITE = "
                   + json.dumps(d, indent=1, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"docs/site-data.js: {len(d['stages'])} stages, {d['steps']} steps, plan ${d['plan_usd']:.2f}, {len(d['evidence'])} evidence rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
