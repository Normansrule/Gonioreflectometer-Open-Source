#!/usr/bin/env python3
"""Validate bom/master_bom.csv and track phases against caps.

Two totals per phase (cheapest parts are already the default):
  buy_all    - every Purchase line bought new
  with_stock - Stock candidate = Y lines (wire, screws, cords...) at $0

    python tools/bom_check.py               # validate, write bom/summary.md, bom/modules/*.csv, assets/budget.svg
    python tools/bom_check.py --check-only  # validate only
    python tools/bom_check.py --strict      # exit 1 if buy_all breaks a cap or the hard cap

SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "bom" / "master_bom.csv"
SUMMARY = ROOT / "bom" / "summary.md"
MODULE_DIR = ROOT / "bom" / "modules"
SVG = ROOT / "docs" / "assets" / "budget.svg"
REFS = ROOT / "REFERENCES.md"

COLUMNS = ["ID", "Type", "Phase", "Module", "Part name", "Function", "Qty", "Manufacturer",
           "Mfr part number", "Supplier", "Supplier link", "Unit cost (USD approx)", "Extended cost",
           "STEP file link", "CAD license", "Notes or cheaper alternative", "Stock candidate",
           "Price status", "Refs"]
TYPES = {"Purchase", "Print", "Owned", "Optional"}
BRIEF_CAPS = OrderedDict([(1, 300.0), (2, 75.0), (3, 45.0), (4, 35.0), (5, 30.0), (6, 0.0)])
# Rebalanced for the fixed-camera architecture: Phase 1 now carries the ring and the table.
PROPOSED_CAPS = OrderedDict([(1, 350.0), (2, 74.0), (3, 23.0), (4, 23.0), (5, 30.0), (6, 0.0)])
HARD_CAP = 500.0
PATHS = ("buy_all", "with_stock")


def money(x: float) -> str:
    return f"${x:,.2f}"


def load(path: Path = MASTER) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        if rd.fieldnames != COLUMNS:
            raise ValueError(f"header mismatch: {rd.fieldnames}")
        return list(rd)


def ref_ids() -> set[str]:
    if not REFS.exists():
        return set()
    return set(re.findall(r"^\|\s*\*\*([A-Z]\d+)\*\*", REFS.read_text(encoding="utf-8"), flags=re.M))


def validate(rows: list[dict], check_refs: bool = True) -> list[str]:
    errs, seen, known = [], set(), ref_ids()
    for r in rows:
        i = r["ID"]
        if i in seen:
            errs.append(f"{i}: duplicate")
        seen.add(i)
        if r["Type"] not in TYPES:
            errs.append(f"{i}: bad Type")
        try:
            q, u, e = float(r["Qty"]), float(r["Unit cost (USD approx)"]), float(r["Extended cost"])
            int(r["Phase"])
        except ValueError as exc:
            errs.append(f"{i}: {exc}")
            continue
        if abs(q * u - e) > 0.011:
            errs.append(f"{i}: Qty x Unit != Extended")
        if r["Type"] in {"Print", "Owned"} and u:
            errs.append(f"{i}: {r['Type']} must be $0")
        if r["Stock candidate"] not in {"Y", "N"}:
            errs.append(f"{i}: Stock candidate must be Y/N")
        if r["Type"] == "Purchase" and not r["Price status"].startswith(("checked", "estimate")):
            errs.append(f"{i}: Price status must say checked/estimate")
        if check_refs and known:
            for ref in filter(None, (x.strip() for x in r["Refs"].split(","))):
                if ref != "-" and ref not in known:
                    errs.append(f"{i}: reference {ref} missing from REFERENCES.md")
    return errs


def cost(r: dict, path: str) -> float:
    if r["Type"] != "Purchase":
        return 0.0
    if path == "with_stock" and r["Stock candidate"] == "Y":
        return 0.0
    return float(r["Extended cost"])


def totals(rows: list[dict]) -> dict:
    ph = {p: {k: 0.0 for k in PATHS} for p in BRIEF_CAPS}
    mod: dict = defaultdict(lambda: {k: 0.0 for k in PATHS})
    est = {p: 0.0 for p in BRIEF_CAPS}
    for r in rows:
        p = int(r["Phase"])
        for k in PATHS:
            ph[p][k] += cost(r, k)
            mod[(p, r["Module"])][k] += cost(r, k)
        if r["Type"] == "Purchase" and r["Price status"].startswith("estimate"):
            est[p] += float(r["Extended cost"])
    return {"phase": ph, "module": dict(mod), "estimated": est,
            "grand": {k: sum(v[k] for v in ph.values()) for k in PATHS}}


def summary_md(t: dict) -> str:
    g = t["grand"]
    out = ["# BOM summary (generated)", "",
           "From `tools/bom_check.py`. USD, approximate, before tax/shipping. Cheapest parts are the default.", "",
           "| Phase | Brief cap | Proposed cap | Buy all | With own stock | Of which estimated |",
           "|---|---:|---:|---:|---:|---:|"]
    for p in BRIEF_CAPS:
        v = t["phase"][p]
        out.append(f"| {p} | {money(BRIEF_CAPS[p])} | {money(PROPOSED_CAPS[p])} | {money(v['buy_all'])} | "
                   f"{money(v['with_stock'])} | {money(t['estimated'][p])} |")
    out += [f"| **Total** | **{money(sum(BRIEF_CAPS.values()))}** | **{money(sum(PROPOSED_CAPS.values()))}** | "
            f"**{money(g['buy_all'])}** | **{money(g['with_stock'])}** | {money(sum(t['estimated'].values()))} |", "",
            f"Hard cap {money(HARD_CAP)}: buy all leaves {money(HARD_CAP - g['buy_all'])}, "
            f"with own stock {money(HARD_CAP - g['with_stock'])}.", "",
            "## Modules", "", "| Phase | Module | Buy all | With own stock |", "|---|---|---:|---:|"]
    for (p, m), v in sorted(t["module"].items()):
        out.append(f"| {p} | {m} | {money(v['buy_all'])} | {money(v['with_stock'])} |")
    return "\n".join(out) + "\n"


def budget_svg(t: dict) -> str:
    """Grouped bars: cap vs buy-all per phase, animated on load."""
    w, h, left, bottom, top = 720, 330, 60, 270, 78
    vmax = 360.0
    bw, gap = 34, 110
    bars = []
    for i, p in enumerate(BRIEF_CAPS):
        x0 = left + 20 + i * gap
        for j, (val, cls, label) in enumerate(((PROPOSED_CAPS[p], "cap", "cap"),
                                               (t["phase"][p]["buy_all"], "buy", "buy"))):
            hh = (bottom - top) * val / vmax
            x = x0 + j * (bw + 6)
            y = bottom - hh
            bars.append(
                f'<rect class="{cls}" x="{x}" y="{y:.1f}" width="{bw}" height="{hh:.1f}" rx="4">'
                f'<animate attributeName="height" from="0" to="{hh:.1f}" dur="1.2s" fill="freeze"/>'
                f'<animate attributeName="y" from="{bottom}" to="{y:.1f}" dur="1.2s" fill="freeze"/></rect>'
                f'<text class="v" x="{x + bw / 2}" y="{y - 6:.1f}">{val:.0f}</text>')
        bars.append(f'<text class="l" x="{x0 + bw + 3}" y="{bottom + 22}">Phase {p}</text>')
    g = t["grand"]["buy_all"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="Segoe UI,Helvetica,Arial,sans-serif">
<style>
.bg{{fill:#0d1117}} .cap{{fill:#30363d}} .buy{{fill:#f0883e}} .v{{fill:#c9d1d9;font-size:12px;text-anchor:middle}}
.l{{fill:#8b949e;font-size:13px;text-anchor:middle}} .t{{fill:#f0f6fc;font-size:16px;font-weight:600}} .s{{fill:#8b949e;font-size:12px}}
</style>
<rect class="bg" width="{w}" height="{h}" rx="12"/>
<text class="t" x="24" y="28">Budget by phase (USD, cheapest parts)</text>
<text class="s" x="{w - 24}" y="28" text-anchor="end">total ${g:.0f} of $500</text>
<rect class="cap" x="430" y="{h - 22}" width="12" height="12" rx="2"/><text class="s" x="448" y="{h - 12}">proposed cap</text>
<rect class="buy" x="560" y="{h - 22}" width="12" height="12" rx="2"/><text class="s" x="578" y="{h - 12}">buy all</text>
<line x1="{left}" y1="{bottom}" x2="{w - 20}" y2="{bottom}" stroke="#30363d"/>
{''.join(bars)}
</svg>
'''


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    rows = load()
    errs = validate(rows)
    if errs:
        print("BOM validation FAILED:\n  - " + "\n  - ".join(errs))
        return 1
    t = totals(rows)
    for p in BRIEF_CAPS:
        v = t["phase"][p]
        print(f"Phase {p}: cap {money(PROPOSED_CAPS[p]):>8}  buy_all {money(v['buy_all']):>8}  with_stock {money(v['with_stock']):>8}")
    print(f"TOTAL : buy_all {money(t['grand']['buy_all'])}  with_stock {money(t['grand']['with_stock'])}  (hard cap {money(HARD_CAP)})")
    if not a.check_only:
        SUMMARY.write_text(summary_md(t), encoding="utf-8")
        MODULE_DIR.mkdir(parents=True, exist_ok=True)
        for old in MODULE_DIR.glob("*.csv"):
            old.unlink()
        groups: dict = OrderedDict()
        for r in rows:
            groups.setdefault(r["Module"], []).append(r)
        for m, items in groups.items():
            with (MODULE_DIR / f"{m}.csv").open("w", newline="", encoding="utf-8") as fh:
                wr = csv.DictWriter(fh, fieldnames=COLUMNS, quoting=csv.QUOTE_ALL)
                wr.writeheader()
                wr.writerows(items)
        SVG.parent.mkdir(exist_ok=True)
        SVG.write_text(budget_svg(t), encoding="utf-8")
    if a.strict:
        bad = [p for p in PROPOSED_CAPS if t["phase"][p]["buy_all"] > PROPOSED_CAPS[p] + 0.005]
        if bad or t["grand"]["buy_all"] > HARD_CAP:
            print(f"STRICT: over cap in phases {bad}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
