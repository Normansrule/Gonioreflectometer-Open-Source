#!/usr/bin/env python3
"""README parts tables from phases/*/bom.csv: Electronics, Mechanical, Printed parts, Tools + optional kits.
Each bought part: picture, qty, price, buy link (Digi-Key / Amazon / Adafruit) and its 3D model (STEP, STL);
each printed part: picture and STEP / STL downloads.

    python tools/bom_readme.py

Blocks: <!-- bom-electronics:start --> … :end, likewise bom-mechanical, bom-printed, bom-tools.
$0 rows that come out of another row's pack are left out (the pack row says what it covers).
Pictures come from `python tools/part_images.py --stl`; links ending in ?raw=true download on GitHub.
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
PICS = ROOT / "docs" / "assets" / "parts"
STORES = ("Digi-Key", "Amazon", "Adafruit")
ELECTRONIC_PREFIX = ("PWR-", "CTL-", "STA-", "SPC-")
ELECTRONIC_IDS = {"LAR-02", "LAR-05", "LAR-06", "TBL-01", "TBL-04", "TLT-01", "TLT-04", "SPN-01", "SPN-04",
                  "CAM-01", "CAM-04", "LSR-01", "LSR-02", "LSR-06", "MSK-01", "MSK-02", "MSK-03"}
_KITS_UNUSED = {"Spectral sensor": ("SPC-",), "Standalone (no laptop)": ("STA-",), "Second camera": ("CAM-04", "CAM-05", "CAM-08"),
        "Colour LEDs + polarizers": ("MSK-",), "Enclosure, extra calibration targets, fan": ("ENC-", "CAL-", "CTL-")}


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def electronic(r: dict) -> bool:
    return r["ID"].startswith(ELECTRONIC_PREFIX) or r["ID"] in ELECTRONIC_IDS


def pic(r: dict, f: Path | None, size: int = 48) -> str:
    png = PICS / f"{f.stem}.png" if f else None
    src = rel(png) if png and png.exists() else part_images.image_for(r)
    img = f'<img src="{src}" width="{size}" height="{size}" alt="{r["ID"]}">'
    stl = f.with_suffix(".stl") if f else None
    return f'<a href="{rel(stl)}">{img}</a>' if stl and stl.exists() else img


def model_links(r: dict, files: list[Path]) -> str:
    """Stand-in STEP + STL (true size), then the maker's open models (Adafruit / KiCad) and the maker's CAD page."""
    stand = [f for f in files if "cad/open/" not in rel(f)][:1]
    opens = [f for f in files if "cad/open/" in rel(f)]
    out = []
    for f in stand:
        out += [f"[STEP]({rel(f)}?raw=true)"] + ([f"[STL]({rel(f.with_suffix('.stl'))}?raw=true)"] if f.with_suffix(".stl").exists() else [])
    out += [f"[open model{' ' + str(i + 1) if len(opens) > 1 else ''}]({rel(f)}?raw=true)" for i, f in enumerate(opens)]
    url = re.search(r"https?://[^\s;)]+", r.get("STEP", ""))
    if url and "Drawing" not in r["STEP"]:
        out.append(f"[maker]({url.group(0)})")
    return " · ".join(out) or "-"


def money(x: float) -> str:
    return f"\\${x:,.2f}"          # \$: GitHub would read two $ in one line as math


def bought_table(rows: list[tuple[str, dict]], al: dict) -> str:
    L = ["| | Part | Qty | Price | Buy | 3D model |", "|:-:|---|:-:|--:|---|---|"]
    for stage, r in rows:
        files, _, _ = catalog.classify(stage, r, al)
        qty, unit, tot = r["Qty"], float(r["Unit USD"] or 0), float(r["Total USD"] or 0)
        price = money(tot) if qty in ("1", "") else f"{qty} × {money(unit)}"
        name = f"**{r['ID']}** {r['Part'].replace('|', '/')}"
        L.append(f"| {pic(r, files[0] if files else None)} | {name} | {qty} | {price} | [{r['Supplier']}]({r['Link']}) | {model_links(r, files)} |")
    total = sum(float(r["Total USD"] or 0) for _, r in rows)
    L.append(f"| | **Total** | | **{money(total)}** | | |")
    return "\n".join(L)


def printed_table(titles: dict) -> str:
    L = ["| | Part | Stage | Download |", "|:-:|---|---|---|"]
    for stl in sorted((ROOT / "phases").glob("*/3d/*.stl")):
        pid, _, name = stl.stem.partition("_")
        stage = stl.parent.parent.name
        png = PICS / f"{stl.stem}.png"
        img = f'<a href="{rel(stl)}"><img src="{rel(png)}" width="48" height="48" alt="{pid}"></a>' if png.exists() else ""
        step = stl.with_suffix(".step")
        dl = f"[STL]({rel(stl)}?raw=true)" + (f" · [STEP]({rel(step)}?raw=true)" if step.exists() else "")
        L.append(f"| {img} | **{pid}** {name.replace('_', ' ')} | [{stage[:2]} {titles.get(stage, stage)}](phases/{stage}/) | {dl} |")
    return "\n".join(L)


def tools_block(rows: list[tuple[str, dict]]) -> str:
    tools = [r for _, r in rows if r["Type"] == "Tool"]
    L = ["| Tool | Price | Buy |", "|---|--:|---|"]
    L += [f"| **{r['ID']}** {r['Part']} | {money(float(r['Total USD'] or 0))} | [{r['Supplier']}]({r['Link']}) |" for r in tools]
    L.append(f"| **Total** (kept after the build; not in the machine cap) | **{money(sum(float(r['Total USD'] or 0) for r in tools))}** | |")
    return "\n".join(L)


def put(text: str, name: str, body: str) -> str:
    a, b = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if a not in text or b not in text:
        print(f"README.md: no {a} block", file=sys.stderr)
        return text
    return text[:text.index(a) + len(a)] + "\n" + body + "\n" + text[text.index(b):]


def main() -> int:
    titles, al = parts_doc.stage_titles(), catalog.aliases()
    rows = [(f.parent.name, r) for f in sorted((ROOT / "phases").glob("*/bom.csv"))
            for r in csv.DictReader(f.open(newline="", encoding="utf-8"))]
    bad = [r["ID"] for _, r in rows if r["Type"] not in ("Print", "Owned") and r["Supplier"] not in STORES]
    if bad:
        print("not from Digi-Key / Amazon / Adafruit: " + ", ".join(bad), file=sys.stderr)
        return 1
    core = [(s, r) for s, r in rows if r["Type"] == "Purchase" and float(r["Total USD"] or 0) > 0]
    text = README.read_text(encoding="utf-8")
    text = put(text, "bom-electronics", bought_table([x for x in core if electronic(x[1])], al))
    text = put(text, "bom-mechanical", bought_table([x for x in core if not electronic(x[1])], al))
    text = put(text, "bom-printed", printed_table(titles))
    text = put(text, "bom-tools", tools_block(rows))
    README.write_text(text, encoding="utf-8")
    print("README.md: electronics, mechanical, printed parts, tools")
    return 0


if __name__ == "__main__":
    sys.exit(main())
