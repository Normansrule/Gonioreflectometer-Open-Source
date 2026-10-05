#!/usr/bin/env python3
"""Check every phases/*/bom/bom.csv and the $500 total; draw docs/assets/budget.svg.

    python tools/bom_check.py            # check + chart
    python tools/bom_check.py --strict   # also fail if the total > $500

SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHASES = ROOT / "phases"
SVG = ROOT / "docs" / "assets" / "budget.svg"
REFS = ROOT / "REFERENCES.md"
COLUMNS = ["ID", "Type", "Part", "Use", "Qty", "Maker", "Part number", "Supplier", "Link", "Unit USD",
           "Total USD", "STEP", "CAD license", "Notes", "Own", "Price", "Refs"]
TYPES = {"Purchase", "Print", "Owned", "Optional"}
HARD_CAP = 500.0


def load() -> dict[str, list[dict]]:
    out = {}
    for f in sorted(PHASES.glob("*/bom/bom.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            rd = csv.DictReader(fh)
            if rd.fieldnames != COLUMNS:
                raise ValueError(f"{f}: header must be {COLUMNS}")
            out[f.parts[-3]] = list(rd)
    return out


def ref_ids() -> set[str]:
    return set(re.findall(r"^\|\s*\*\*([A-Z]\d+)\*\*", REFS.read_text(encoding="utf-8"), flags=re.M))


def validate(boms: dict[str, list[dict]]) -> list[str]:
    errs, seen, known = [], set(), ref_ids()
    for phase, rows in boms.items():
        for r in rows:
            i = f"{phase}/{r['ID']}"
            if r["ID"] in seen:
                errs.append(f"{i}: duplicate ID")
            seen.add(r["ID"])
            if r["Type"] not in TYPES:
                errs.append(f"{i}: bad Type")
            try:
                q, u, t = float(r["Qty"]), float(r["Unit USD"]), float(r["Total USD"])
            except ValueError as exc:
                errs.append(f"{i}: {exc}")
                continue
            if abs(q * u - t) > 0.011:
                errs.append(f"{i}: Qty × Unit ≠ Total")
            if r["Type"] in {"Print", "Owned"} and u:
                errs.append(f"{i}: {r['Type']} must be $0")
            if r["Own"] not in {"Y", "N"}:
                errs.append(f"{i}: Own must be Y/N")
            if r["Type"] == "Purchase" and not r["Price"].startswith(("checked", "estimate")):
                errs.append(f"{i}: Price must be 'checked …' or 'estimate'")
            for ref in filter(None, (x.strip() for x in r["Refs"].split(","))):
                if ref != "-" and ref not in known:
                    errs.append(f"{i}: {ref} missing from REFERENCES.md")
    return errs


def cost(r: dict, own: bool) -> float:
    if r["Type"] != "Purchase" or (own and r["Own"] == "Y"):
        return 0.0
    return float(r["Total USD"])


def totals(boms: dict[str, list[dict]]) -> dict[str, dict[str, float]]:
    return {p: {"buy": sum(cost(r, False) for r in rows), "own": sum(cost(r, True) for r in rows),
                "opt": sum(float(r["Total USD"]) for r in rows if r["Type"] == "Optional"),
                "est": sum(float(r["Total USD"]) for r in rows if r["Type"] == "Purchase" and r["Price"] == "estimate")}
            for p, rows in boms.items()}


def budget_svg(t: dict[str, dict[str, float]]) -> str:
    """Bars per phase + running total against $500."""
    w, h, left, bottom, top = 1000, 330, 60, 260, 70
    n = len(t)
    gap = (w - left - 40) / n
    vmax = HARD_CAP
    run, bars, pts = 0.0, [], []
    for i, (p, v) in enumerate(t.items()):
        x = left + i * gap + gap * 0.2
        bw = gap * 0.6
        hh = (bottom - top) * v["buy"] / vmax
        run += v["buy"]
        bars.append(f'<rect x="{x:.1f}" y="{bottom - hh:.1f}" width="{bw:.1f}" height="{hh:.1f}" rx="3" fill="#f0883e">'
                    f'<animate attributeName="height" from="0" to="{hh:.1f}" dur="1s" fill="freeze"/>'
                    f'<animate attributeName="y" from="{bottom}" to="{bottom - hh:.1f}" dur="1s" fill="freeze"/></rect>'
                    f'<text x="{x + bw / 2:.1f}" y="{bottom - hh - 6:.1f}" class="v">{v["buy"]:.0f}</text>'
                    f'<text x="{x + bw / 2:.1f}" y="{bottom + 18}" class="l">{p[:2]}</text>')
        pts.append(f"{x + bw / 2:.1f},{bottom - (bottom - top) * run / vmax:.1f}")
    cap_y = top
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="Segoe UI,Helvetica,Arial,sans-serif">
<style>.v{{fill:#c9d1d9;font-size:12px;text-anchor:middle}} .l{{fill:#8b949e;font-size:12px;text-anchor:middle}}
.t{{fill:#f0f6fc;font-size:16px;font-weight:600}} .s{{fill:#8b949e;font-size:12px}}</style>
<rect width="{w}" height="{h}" rx="12" fill="#0d1117"/>
<text class="t" x="24" y="30">Cost per phase (USD, cheapest parts)</text>
<text class="s" x="{w - 24}" y="30" text-anchor="end">total ${run:.2f} of $500</text>
<line x1="{left}" y1="{cap_y}" x2="{w - 30}" y2="{cap_y}" stroke="#f85149" stroke-dasharray="6 5"/>
<text class="s" x="{w - 32}" y="{cap_y - 6}" text-anchor="end">$500 cap</text>
<line x1="{left}" y1="{bottom}" x2="{w - 30}" y2="{bottom}" stroke="#30363d"/>
{''.join(bars)}
<polyline points="{' '.join(pts)}" fill="none" stroke="#58a6ff" stroke-width="2.5" stroke-dasharray="1200" stroke-dashoffset="1200">
<animate attributeName="stroke-dashoffset" from="1200" to="0" dur="2s" fill="freeze"/></polyline>
<rect x="24" y="{h - 26}" width="12" height="12" rx="2" fill="#f0883e"/><text class="s" x="42" y="{h - 16}">phase</text>
<rect x="100" y="{h - 26}" width="12" height="12" rx="2" fill="#58a6ff"/><text class="s" x="118" y="{h - 16}">running total</text>
</svg>
'''


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    boms = load()
    errs = validate(boms)
    if errs:
        print("BOM errors:\n  " + "\n  ".join(errs))
        return 1
    t = totals(boms)
    run = 0.0
    for p, v in t.items():
        run += v["buy"]
        print(f"{p:<18} ${v['buy']:>7.2f}   own-stock ${v['own']:>7.2f}   running ${run:>7.2f}")
    own = sum(v["own"] for v in t.values())
    print(f"{'TOTAL':<18} ${run:>7.2f}   own-stock ${own:>7.2f}   cap ${HARD_CAP:.0f}")
    sa = t.get("15-standalone", {}).get("opt", 0.0)
    print(f"{'+ standalone kit':<18} ${sa:>7.2f}   optional, not in the total (own-stock path + kit ${own + sa:.2f})")
    SVG.write_text(budget_svg(t), encoding="utf-8")
    if a.strict and run > HARD_CAP:
        print("over the $500 cap")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
