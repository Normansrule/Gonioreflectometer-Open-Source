#!/usr/bin/env python3
"""Final-machine power budget: phases/01-power/power_loads.yaml -> power_budget.md beside it.

Power path: 24 V wall adapter -> e-stop -> limit switch -> SKR Pico (bus = adapter voltage, 24 V).
Checks (exit 1 if one fails):
  adapter   peak current <= adapter max A / (1 + headroom)
  bus       adapter voltage <= motor-board rated input

    python tools/power_budget.py           # print + write
    python tools/power_budget.py --check   # exit status only

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
    ad = s["adapter"]
    out = {}
    for m in MODES:
        dc = sum(l[f"{m}_w"] for l in cfg["loads"])
        in_w = dc / s["path_efficiency"]
        out[m] = {"dc_w": dc, "in_w": in_w, "amps": in_w / ad["volts"]}
    return out


def checks(cfg: dict, res: dict) -> dict[str, tuple[float, bool, str]]:
    s, hr = cfg["supply"], cfg["required_headroom"]
    ad = s["adapter"]
    p = res["peak"]
    a = ad["max_amps"] / p["amps"] - 1.0
    bus = s["bus_max_volts"] / ad["volts"] - 1.0
    return {"adapter": (a, a >= hr, f"{ad['max_amps']:g} A adapter / {p['amps']:.2f} A peak at {ad['volts']:g} V"),
            "bus": (bus, bus >= 0.0, f"motor board rated {s['bus_max_volts']:g} V / {ad['volts']:g} V adapter")}


def render(cfg: dict, res: dict) -> str:
    s = cfg["supply"]
    ad = s["adapter"]
    rows = "\n".join(f"| {l['name']} | {l['phase']} | {l['typical_w']:.1f} | {l['peak_w']:.1f} | {l['idle_w']:.2f} |" for l in cfg["loads"])
    t, p, i = res["typical"], res["peak"], res["idle"]
    ck = "\n".join(f"| {k} | {txt} | {100 * v:.0f} % | **{'PASS' if ok else 'FAIL'}** |" for k, (v, ok, txt) in checks(cfg, res).items())
    return f"""# Power budget (generated)

All phases installed. Laptop, ESP32-S3 hub and USB camera are powered by the laptop. Path: {ad['name']} → e-stop →
limit switch → SKR Pico; the bus is the adapter's {ad['volts']:g} V.

| Load | Phase | Typical W | Peak W | Idle W |
|---|---:|---:|---:|---:|
{rows}

| | Typical | Peak | Idle (motors asleep) |
|---|---:|---:|---:|
| Motor board input | {t['dc_w']:.1f} W | {p['dc_w']:.1f} W | {i['dc_w']:.1f} W |
| From the adapter | {t['in_w']:.1f} W | {p['in_w']:.1f} W | {i['in_w']:.1f} W |
| Adapter current at {ad['volts']:g} V | {t['amps']:.2f} A | {p['amps']:.2f} A | {i['amps']:.2f} A |

| Check | | Headroom | |
|---|---|---:|---|
{ck}

Headroom needed: peak current ≥ {100 * cfg['required_headroom']:.0f} % under the adapter's rating. Efficiencies are estimates until
measured (stage 01 test T12). Off (e-stop pressed): nothing after the e-stop draws power.
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
    return 0 if all(ok for _, ok, _ in checks(cfg, res).values()) else 1


if __name__ == "__main__":
    sys.exit(main())
