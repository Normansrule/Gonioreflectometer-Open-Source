#!/usr/bin/env python3
"""Add things to the framework without hand-editing YAML or CSV. Run `make` afterwards.

    python tools/new.py stage 18-gloss-meter "Gloss meter"
    python tools/new.py milestone 04-light-arm "Quieter belt" "Belt noise below 50 dB"
    python tools/new.py step M14 "Check belt tension"
    python tools/new.py part 04-light-arm LAR-10 "Belt tensioner spring" 2 0.50 https://example.com/spring
    python tools/new.py ref G "A. Author, \"Title,\" Venue 2026 — [doi](https://doi.org/…)" "Why it matters (phase 04)"
    python tools/new.py renumber

New milestones get the next free ID (IDs never change, so GitHub issues keep their history) and sit after the
last milestone of their stage. New steps and milestones start with TODO lines: replace them with real Do / Verify.
`renumber` makes IDs consecutive again (only before publishing: it re-points GitHub issues).
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PHASES = ROOT / ".github" / "phases.yml"
HEAD = ("# Single source for stages and milestones. `python tools/roadmap.py` writes phases/*/README.md and the README;\n"
        "# `--github --repo OWNER/NAME` makes one GitHub milestone per milestone and one issue per step (Do / Verify / Record).\n"
        "# Edit freely, or use tools/new.py; then run `make`.\n")


def load() -> dict:
    return yaml.safe_load(PHASES.read_text(encoding="utf-8"))


def save(y: dict) -> None:
    PHASES.write_text(HEAD + yaml.safe_dump(y, sort_keys=False, allow_unicode=True, width=200), encoding="utf-8")


def skeleton_step(sid: str, title: str) -> dict:
    return {"id": sid, "title": title, "time": "30 min", "needs": ["TODO: part IDs, tools"],
            "do": ["TODO: first action (command, part ID, file)"], "verify": ["TODO: measurement + pass number"],
            "fail": ["TODO: first thing to check"], "record": "TODO: file to fill in; commit."}


def renumber(y: dict) -> list[tuple[str, str]]:
    changes = []
    for i, m in enumerate(y["milestones"], 1):
        new = f"M{i:02d}"
        if m["id"] != new:
            changes.append((m["id"], new))
        m["id"] = new
        for k, s in enumerate(m["steps"], 1):
            s["id"] = f"{new}.{k}"
    return changes


def cmd_stage(a) -> None:
    y = load()
    n = len(y["stages"])
    if not a.folder.startswith(f"{n:02d}-"):
        sys.exit(f"next stage number is {n:02d}: use {n:02d}-{a.folder.split('-', 1)[-1]}")
    y["stages"].append({"folder": a.folder, "title": a.title})
    d = ROOT / "phases" / a.folder
    (d / "3d").mkdir(parents=True, exist_ok=True)
    (d / "design.md").write_text(f"# {a.folder[:2]} · Design\n\n## Results\n\n(fill in)\n", encoding="utf-8")
    save(y)
    print(f"stage {a.folder} added: phases/{a.folder}/ (design.md, 3d/). Next: python tools/new.py milestone {a.folder} …")


def cmd_milestone(a) -> None:
    y = load()
    if a.stage not in [s["folder"] for s in y["stages"]]:
        sys.exit(f"unknown stage {a.stage}")
    ms = y["milestones"]
    pos = max([i for i, m in enumerate(ms) if m["stage"] <= a.stage] or [-1]) + 1
    mid = f"M{max(int(m['id'][1:]) for m in ms) + 1:02d}"          # IDs never change once on GitHub
    m = {"id": mid, "stage": a.stage, "title": a.title, "goal": a.goal, "weeks": a.weeks,
         "steps": [skeleton_step(f"{mid}.1", a.title)]}
    ms.insert(pos, m)
    save(y)
    print(f"milestone {mid} · {a.title} added at the end of {a.stage} (IDs are permanent; order comes from the file)")


def cmd_step(a) -> None:
    y = load()
    m = next((m for m in y["milestones"] if m["id"] == a.milestone), None)
    if not m:
        sys.exit(f"unknown milestone {a.milestone}")
    sid = f"{m['id']}.{len(m['steps']) + 1}"
    m["steps"].append(skeleton_step(sid, a.title))
    save(y)
    print(f"step {sid} added: edit its Do / Verify / Record in .github/phases.yml")


def cmd_part(a) -> None:
    f = ROOT / "phases" / a.stage / "bom.csv"
    cols = ["ID", "Type", "Part", "Use", "Requirement", "Qty", "Maker", "Part number", "Supplier", "Link", "Unit USD",
            "Total USD", "STEP", "CAD license", "Notes", "Own", "Price", "Refs", "Paid USD", "Status"]
    rows = list(csv.DictReader(f.open(encoding="utf-8"))) if f.exists() else []
    if any(r["ID"] == a.id for r in rows):
        sys.exit(f"{a.id} already in {f.relative_to(ROOT)}")
    rows.append({"ID": a.id, "Type": a.type, "Part": a.part, "Use": a.use, "Requirement": a.req, "Qty": f"{a.qty:g}", "Maker": "", "Part number": "",
                 "Supplier": "", "Link": a.link or "n/a", "Unit USD": f"{a.unit:.2f}", "Total USD": f"{a.qty * a.unit:.2f}",
                 "STEP": "", "CAD license": "", "Notes": "", "Own": "N",
                 "Price": "estimate" if a.type == "Purchase" else ("n/a" if a.type == "Print" else "estimate"), "Refs": "-",
                 "Paid USD": "", "Status": "suggested"})
    with f.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{a.id} added to {f.relative_to(ROOT)} (Price = estimate; change to 'checked YYYY-MM-DD' once confirmed)")


def cmd_ref(a) -> None:
    f = ROOT / "REFERENCES.md"
    lines = f.read_text(encoding="utf-8").splitlines()
    nums = [int(m.group(1)) for l in lines if (m := re.match(rf"^\| \*\*{a.prefix}(\d+)\*\* \|", l))]
    if not nums:
        sys.exit(f"no {a.prefix} references yet; add the first row by hand")
    new_id = f"{a.prefix}{max(nums) + 1}"
    last = max(i for i, l in enumerate(lines) if re.match(rf"^\| \*\*{a.prefix}\d+\*\* \|", l))
    lines.insert(last + 1, f"| **{new_id}** | {a.source} | {a.used_for} |")
    text = "\n".join(lines) + "\n"
    n = len(re.findall(r"^\| \*\*[A-Z]\d+\*\* \|", text, re.M))
    f.write_text(re.sub(r"^\d+ sources\.", f"{n} sources.", text, count=1, flags=re.M), encoding="utf-8")
    print(f"{new_id} added; cite it as [{new_id}]")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stage"); s.add_argument("folder"); s.add_argument("title"); s.set_defaults(fn=cmd_stage)
    s = sub.add_parser("milestone"); s.add_argument("stage"); s.add_argument("title"); s.add_argument("goal")
    s.add_argument("--weeks", type=int, default=1); s.set_defaults(fn=cmd_milestone)
    s = sub.add_parser("step"); s.add_argument("milestone"); s.add_argument("title"); s.set_defaults(fn=cmd_step)
    s = sub.add_parser("part"); s.add_argument("stage"); s.add_argument("id"); s.add_argument("part")
    s.add_argument("qty", type=float); s.add_argument("unit", type=float); s.add_argument("link", nargs="?")
    s.add_argument("--use", default=""); s.add_argument("--req", default="TODO: rating, size, spec a substitute must meet"); s.add_argument("--type", default="Purchase", choices=["Purchase", "Optional", "Print", "Owned"])
    s.set_defaults(fn=cmd_part)
    s = sub.add_parser("ref"); s.add_argument("prefix"); s.add_argument("source"); s.add_argument("used_for"); s.set_defaults(fn=cmd_ref)
    s = sub.add_parser("renumber"); s.set_defaults(fn=lambda a: (lambda y: (renumber(y), save(y), print("renumbered")))(load()))
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
