#!/usr/bin/env python3
"""docs/build-book.js: the build book (docs/build.html), one step per page, like a toy-brick instruction book.

Sources (nothing is typed twice):
  docs/assembly.yaml       the order: which CAD parts each step adds, where they come in from, the camera angle
  docs/og/model/rig.js     the parts and their meshes (tools/site_model.py, from tools/cad/assembly.py)
  .github/phases.yml       the words: each step shows the lines of its checklist step (`ref`, `lines`)
  phases/*/bom.csv         names of bought parts

    python tools/build_book.py            write docs/build-book.js (run by `make build`)
    python tools/build_book.py --check    exit 1 if a part is in no step or in two, or a ref / line is missing
    python tools/build_book.py --pdf      also exports/build-book.pdf, one page per step (needs playwright + Chromium)

SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from wiring import md_html  # noqa: E402

BOOK = ROOT / "docs" / "assembly.yaml"
RIG = ROOT / "docs" / "og" / "model" / "rig.js"
OUT = ROOT / "docs" / "build-book.js"
PDF = ROOT / "exports" / "build-book.pdf"
REPO = "https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/"
FROM = ("down", "out", "+x", "-x", "+y", "-y")
SCREW = re.compile(r"(?:(\d+) × )?(M[2348]) × (\d+)")


def rig_meta() -> dict:
    head = RIG.read_text(encoding="utf-8").split("window.RIG = ", 1)[1].split(";\n", 1)[0]
    return json.loads(head)


def part_id(name: str) -> str:
    m = re.match(r"[A-Z]+-\d+[a-z]?", name)
    return m.group(0) if m else name


def bom_rows() -> dict[str, dict]:
    rows = {}
    for f in sorted(ROOT.glob("phases/*/bom.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                rows[r["ID"]] = r
    return rows


def checklist() -> tuple[dict[str, dict], dict[str, dict]]:
    d = yaml.safe_load((ROOT / ".github" / "phases.yml").read_text(encoding="utf-8"))
    out = {}
    stages = {s["folder"]: {"title": s["title"], "safety": md_html(s.get("safety", ""))} for s in d["stages"]}
    for m in d["milestones"]:
        for s in m["steps"]:
            out[s["id"]] = {"title": s["title"], "milestone": m.get("title", ""), "stage": m["stage"], "do": s.get("do", [])}
    return out, stages


def label(pid: str, info: dict, bom: dict) -> tuple[str, str]:
    """(what it is, print | buy)"""
    i = info.get(pid, {})
    if i.get("what"):
        return re.sub(r"\s*\(print \d+[^)]*\)", "", i["what"]), "print"
    r = bom.get(pid)
    if r:
        name = re.sub(r"\s*\((?:\d+|[^)]*pack[^)]*)\)\s*$", "", r["Part"]).strip()
        return name, "print" if r["Type"] == "Print" else "buy"
    return pid, i.get("kind", "buy")


def screws(lines: list[str]) -> list[dict]:
    """Every 'n × M2 × 12' in the step's own words, once each (count only where the checklist gives one)."""
    seen: dict[str, dict] = {}
    for line in lines:
        for n, size, length in SCREW.findall(line):
            k = f"{size} × {length}"
            s = seen.setdefault(k, {"size": size, "len": int(length), "n": []})
            if n and int(n) not in s["n"]:
                s["n"].append(int(n))
    return sorted(seen.values(), key=lambda s: (s["size"], s["len"]))


def build() -> tuple[dict, list[str]]:
    meta, book = rig_meta(), yaml.safe_load(BOOK.read_text(encoding="utf-8"))
    names, info, bom, todo, stages = meta["names"], meta.get("info", {}), bom_rows(), *checklist()
    errs, used, steps, section = [], {}, [], ""
    for k, s in enumerate(book["steps"], 1):
        section = s.get("section", section)
        if not section:
            errs.append(f"step {k}: the first step needs a `section`")
        idx = []
        for pat in s["add"]:
            hit = [i for i, n in enumerate(names) if fnmatch.fnmatchcase(n, pat)]
            if not hit:
                errs.append(f"step {k} ({s['title']}): no part matches {pat!r}")
            idx += [i for i in hit if i not in idx]
        for i in idx:
            if i in used:
                errs.append(f"{names[i]} is in step {used[i]} and step {k}")
            used.setdefault(i, k)
        ref = todo.get(s["ref"])
        if not ref:
            errs.append(f"step {k}: checklist step {s['ref']} not in .github/phases.yml")
            continue
        lines = []
        for n in s.get("lines", range(len(ref["do"]))):
            if n >= len(ref["do"]):
                errs.append(f"step {k}: {s['ref']} has no line {n}")
            else:
                lines.append(ref["do"][n])
        if s.get("from", "down") not in FROM:
            errs.append(f"step {k}: from must be one of {FROM}")
        items: dict[str, dict] = {}
        for i in idx:
            pid = part_id(names[i])
            what, kind = label(pid, info, bom)
            it = items.setdefault(pid, {"id": pid, "what": what, "kind": kind, "parts": []})
            it["parts"].append(i)
            if info.get(pid, {}).get("stl"):
                it["stl"] = REPO + info[pid]["stl"]
        steps.append({"title": s["title"], "section": section, "ref": s["ref"], "refTitle": ref["title"], "milestone": ref["milestone"],
                      "stage": ref["stage"], "text": [md_html(x) for x in lines], "screws": screws(lines),
                      "note": md_html(s["note"]) if s.get("note") else "", "from": s.get("from", "down"),
                      "stack": bool(s.get("stack")),
                      "view": s.get("view"), "parts": idx, "items": list(items.values())})
    for i, n in enumerate(names):
        if i not in used:
            errs.append(f"{n} is in no step of docs/assembly.yaml")
    used_st = {s["stage"] for s in steps}
    return {"note": "Generated by tools/build_book.py from docs/assembly.yaml, .github/phases.yml and rig.js",
            "steps": steps, "parts": len(names), "stages": {k: v for k, v in stages.items() if k in used_st},
            "repo": REPO}, errs


def pdf() -> int:
    """One A4-landscape page per step: the page itself in print mode (docs/build.html?print)."""
    from playwright.sync_api import sync_playwright
    PDF.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        page = b.new_page(viewport={"width": 1400, "height": 990})
        page.goto((ROOT / "docs" / "build.html").as_uri() + "?print")
        page.wait_for_function("window.__book && window.__book.ready", timeout=120000)
        page.pdf(path=str(PDF), format="A4", landscape=True, print_background=True)
        b.close()
    print(f"{PDF.relative_to(ROOT)}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--pdf", action="store_true")
    a = ap.parse_args(argv)
    data, errs = build()
    for e in errs:
        print("build book: " + e, file=sys.stderr)
    if errs:
        return 1
    if not a.check:
        OUT.write_text("// Written by tools/build_book.py (`make build`): do not edit by hand.\nwindow.BOOK = "
                       + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
        print(f"{OUT.relative_to(ROOT)}: {len(data['steps'])} steps, {data['parts']} parts")
    return pdf() if a.pdf else 0


if __name__ == "__main__":
    sys.exit(main())
