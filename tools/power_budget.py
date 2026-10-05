#!/usr/bin/env python3
"""Final-machine power budget: phases/01-power/power_loads.yaml -> power_budget.md beside it.

    python tools/power_budget.py           # print + write
    python tools/power_budget.py --check   # exit 1 if headroom < required

SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "phases" / "01-power" / "power_loads.yaml"
OUTPUT = INPUT.with_name("power_budget.md")
MODES = ("typical", "peak", "idle")


def compute(cfg: dict) -> dict:
    s = cfg["supply"]
    eff = {"typical": s["efficiency_typical_load"], "peak": s["efficiency_peak_load"], "idle": s["efficiency_idle_load"]}
    out = {}
    for m in MODES:
        dc = sum(l[f"{m}_w"] for l in cfg["loads"])
        wall = dc / eff[m] + (s["no_load_watts"] if m == "idle" else 0.0)
        out[m] = {"dc_w": dc, "amps": dc / s["volts"], "wall_w": wall, "eff": dc / wall if wall else 0.0}
    return out


def headroom(cfg: dict, res: dict) -> float:
    return cfg["supply"]["rated_watts"] / res["peak"]["dc_w"] - 1.0


def render(cfg: dict, res: dict) -> str:
    s = cfg["supply"]
    hr = headroom(cfg, res)
    ok = "PASS" if hr >= cfg["required_headroom"] else "FAIL"
    rows = "\n".join(f"| {l['name']} | {l['phase']} | {l['typical_w']:.1f} | {l['peak_w']:.1f} | {l['idle_w']:.2f} |" for l in cfg["loads"])
    t, p, i = res["typical"], res["peak"], res["idle"]
    return f"""# Power budget (generated)

All phases installed. Laptop, Pico hub and USB camera are powered by the laptop.

| Load | Phase | Typical W | Peak W | Idle W |
|---|---:|---:|---:|---:|
{rows}

| | Typical | Peak | Idle |
|---|---:|---:|---:|
| 24 V DC | {t['dc_w']:.1f} W ({t['amps']:.2f} A) | {p['dc_w']:.1f} W ({p['amps']:.2f} A) | {i['dc_w']:.1f} W |
| Wall | {t['wall_w']:.1f} W | {p['wall_w']:.1f} W | {i['wall_w']:.1f} W |
| Efficiency | {100*t['eff']:.0f} % | {100*p['eff']:.0f} % | {100*i['eff']:.0f} % |

Headroom: {s['rated_watts']:.0f} W adapter / {p['dc_w']:.1f} W peak = **{100*hr:.0f} %** (need >= {100*cfg['required_headroom']:.0f} %): **{ok}**.
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    cfg = yaml.safe_load(INPUT.read_text())
    res = compute(cfg)
    txt = render(cfg, res)
    print(txt)
    if not a.check:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(txt, encoding="utf-8")
    return 0 if headroom(cfg, res) >= cfg["required_headroom"] else 1


if __name__ == "__main__":
    sys.exit(main())
