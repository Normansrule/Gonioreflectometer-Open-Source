#!/usr/bin/env python3
"""Bill of materials in README.md (between <!-- bom:start --> and <!-- bom:end -->): every row of phases/*/bom.csv
with a picture, quantity, price, where to buy it, and download links for its 3D files (STEP + STL).

    python tools/bom_readme.py

Pictures: printed parts and bought parts' 3D models are rendered by `python tools/part_images.py --stl` (run by
`make parts`); a row without a rendered model falls back to the line icon. Links ending in `?raw=true` download the
file on GitHub; an STL link without it opens GitHub's 3D viewer.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "cad"))
import catalog  # noqa: E402
import part_images  # noqa: E402
import parts_doc  # noqa: E402

README = ROOT / "README.md"
START, END = "<!-- bom:start -->", "<!-- bom:end -->"
PICS = ROOT / "docs" / "assets" / "parts"
KIND_LABEL = {"Purchase": "", "Optional": " *(optional)*", "Tool": " *(tool)*", "Owned": " *(you have it)*", "Print": ""}


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def money(v: str) -> str:
    try:
        return f"${float(v):,.2f}"
    except ValueError:
        return "-"


def pictures(r: dict, files: list[Path]) -> str:
    """Up to 4 thumbnails; each opens the part's STL in GitHub's 3D viewer when there is one."""
    out = []
    for f in files:
        png, stl = PICS / f"{f.stem}.png", f.with_suffix(".stl")
        if png.exists():
            img = f'<img src="{rel(png)}" width="64" height="64" alt="{f.stem}">'
            out.append(f'<a href="{rel(stl)}">{img}</a>' if stl.exists() else img)
        if len(out) == 4:
            break
    if not out:
        out.append(f'<img src="{part_images.image_for(r)}" width="64" height="64" alt="{r["ID"]}">')
    return "".join(out)


def label(f: Path, pid: str) -> str:
    """Short name of one 3D file: 'a rim segment' for printed sub-parts, 'stand-in' / 'Adafruit model' for bought."""
    if "cad/open/" in rel(f):
        return "Adafruit model" if "_adafruit_" in f.name else "KiCad model"
    if "cad/bought/" in rel(f):
        return "stand-in (true size)"
    stem = f.stem.split("_", 1)
    sub = stem[0][len(pid):]
    return (f"{sub} " if sub else "") + (stem[1].replace("_", " ") if len(stem) > 1 else "")


def downloads(r: dict, files: list[Path]) -> str:
    cells = []
    for f in files:
        links = [f"[STEP ⬇]({rel(f)}?raw=true)"]
        stl = f.with_suffix(".stl")
        if stl.exists():
            links.append(f"[STL ⬇]({rel(stl)}?raw=true)")
        cells.append(f"{label(f, r['ID'])}: " + " · ".join(links))
    url = re.search(r"https?://[^\s;)]+", r.get("STEP", ""))
    if url and r["Type"] != "Print" and "Drawing" not in r["STEP"]:
        cells.append(f"[maker's CAD]({url.group(0)})")
    return "<br>".join(cells) or "-"


def buy(r: dict) -> str:
    if r["Type"] == "Print":
        return "print it (black ABS)"
    if r["Type"] == "Owned":
        return "-"
    link, sup = r["Link"].strip(), r["Supplier"].strip() or "link"
    return f"[{sup}]({link})" if link.startswith("http") else sup


def price(r: dict) -> str:
    if r["Type"] in ("Print", "Owned"):
        return "-"
    if float(r["Unit USD"] or 0) == 0:
        return "in a pack" if r["Notes"].lower().startswith(("in the", "from the", "spare from")) else "$0.00"
    unit, tot = money(r["Unit USD"]), money(r["Total USD"])
    return tot if r["Qty"] in ("1", "") else f"{r['Qty']} × {unit}<br>= {tot}"


def render() -> str:
    titles, al = parts_doc.stage_titles(), catalog.aliases()
    out, grand = [], {"Purchase": 0.0, "Optional": 0.0, "Tool": 0.0}
    for bom in sorted((ROOT / "phases").glob("*/bom.csv")):
        stage = bom.parent.name
        rows = list(csv.DictReader(bom.open(newline="", encoding="utf-8")))
        sums = {k: sum(float(r["Total USD"] or 0) for r in rows if r["Type"] == k) for k in grand}
        for k in grand:
            grand[k] += sums[k]
        n3d = 0
        body = ["| Picture | Part | Qty | Price | Buy | 3D files |", "|:---:|---|:---:|---:|---|---|"]
        for r in rows:
            files, _, _ = catalog.classify(stage, r, al)
            n3d += bool(files)
            name = f"**{r['ID']}** {r['Part'].replace('|', '/')}{KIND_LABEL.get(r['Type'], '')}<br><sub>{r['Use'].replace('|', '/')}</sub>"
            qty = r["Qty"] if r["Type"] != "Print" else "1 set"
            body.append(f"| {pictures(r, files)} | {name} | {qty} | {price(r)} | {buy(r)} | {downloads(r, files)} |")
        money_bits = [f"parts ${sums['Purchase']:,.2f}"] if sums["Purchase"] else []
        money_bits += [f"optional ${sums['Optional']:,.2f}"] if sums["Optional"] else []
        money_bits += [f"tools ${sums['Tool']:,.2f}"] if sums["Tool"] else []
        head = f"<b>{stage[:2]} · {titles.get(stage, stage)}</b> — {len(rows)} rows · {' · '.join(money_bits) or 'no purchases'} · {n3d} with 3D files"
        out += ["<details>", f"<summary>{head}</summary>", "", *body, "",
                f"Stage files: [bom.csv](phases/{stage}/bom.csv) · [3D folder](phases/{stage}/3d/) · [checklist](phases/{stage}/README.md)",
                "", "</details>", ""]
    top = (f"**Machine ${grand['Purchase']:,.2f}** (cap in `tools/bom_check.py`) · optional add-ons ${grand['Optional']:,.2f} · "
           f"tools ${grand['Tool']:,.2f}. Open a stage to see its parts.")
    return "\n".join([top, "", *out]).rstrip()


def main() -> int:
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print(f"README.md has no {START} … {END} block", file=sys.stderr)
        return 1
    a, b = text.index(START) + len(START), text.index(END)
    README.write_text(text[:a] + "\n" + render() + "\n" + text[b:], encoding="utf-8")
    print("README.md: bill of materials updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
