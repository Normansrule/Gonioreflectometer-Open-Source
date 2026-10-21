#!/usr/bin/env python3
"""Final-machine power budget: phases/01-power/power_loads.yaml -> power_budget.md beside it.

Power path: 6S Li-ion pack (built-in BMS) -> fuse -> e-stop -> SKR Pico (bus = pack voltage, 18-24 V).
Charging (laptop-style, can stay plugged in): USB-C charger -> PD trigger (20 V) -> DROK CC/CV (24.0 V, 1.0 A) -> pack.
Checks (exit 1 if one fails):
  battery   pack current at the recharge level, peak load <= max A / (1 + headroom)
  runtime   typical session on the pack alone >= 3 h
  charger   charge power >= typical draw (plugged in, the pack does not run down while measuring)
  usb       USB-C power the DROK needs <= the USB-C charger rating
  bus       charge voltage <= motor-board rated input

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
MIN_HOURS = 3.0


def compute(cfg: dict) -> dict:
    s = cfg["supply"]
    bat, ch = s["battery"], s["charger"]
    usable_wh = bat["capacity_ah"] * bat["nominal_volts"] * bat["usable_fraction"]
    charge_w = ch["volts"] * ch["amps"]
    out = {"usable_wh": usable_wh, "charge_w": charge_w, "usb_w": charge_w / ch["efficiency"],
           "charge_h": bat["capacity_ah"] * bat["usable_fraction"] / ch["amps"] * 1.2}   # CC, then the CV taper
    for m in MODES:
        dc = sum(l[f"{m}_w"] for l in cfg["loads"])
        bat_w = dc / s["path_efficiency"]
        out[m] = {"dc_w": dc, "bat_w": bat_w, "amps_low": bat_w / bat["cutoff_volts"],
                  "hours": usable_wh / bat_w if bat_w else float("inf")}
    return out


def checks(cfg: dict, res: dict) -> dict[str, tuple[float, bool, str]]:
    s, hr = cfg["supply"], cfg["required_headroom"]
    bat, ch = s["battery"], s["charger"]
    p, t = res["peak"], res["typical"]
    b = bat["max_amps"] / p["amps_low"] - 1.0
    run = t["hours"] / MIN_HOURS - 1.0
    chg = res["charge_w"] / t["bat_w"] - 1.0
    usb = ch["usb_watts"] / res["usb_w"] - 1.0
    bus = s["bus_max_volts"] / ch["volts"] - 1.0
    return {"battery": (b, b >= hr, f"{bat['max_amps']:.0f} A pack / {p['amps_low']:.2f} A peak at {bat['cutoff_volts']:g} V"),
            "runtime": (run, run >= 0.0, f"{t['hours']:.1f} h typical / {MIN_HOURS:g} h needed"),
            "charger": (chg, chg >= 0.0, f"{res['charge_w']:.0f} W charge / {t['bat_w']:.1f} W typical"),
            "usb": (usb, usb >= 0.0, f"{ch['usb_watts']:.0f} W USB-C charger / {res['usb_w']:.1f} W needed"),
            "bus": (bus, bus >= 0.0, f"motor board rated {s['bus_max_volts']:g} V / {ch['volts']:g} V charge voltage")}


def render(cfg: dict, res: dict) -> str:
    s = cfg["supply"]
    b, ch = s["battery"], s["charger"]
    rows = "\n".join(f"| {l['name']} | {l['phase']} | {l['typical_w']:.1f} | {l['peak_w']:.1f} | {l['idle_w']:.2f} |" for l in cfg["loads"])
    t, p, i = res["typical"], res["peak"], res["idle"]
    ck = "\n".join(f"| {k} | {txt} | {100 * v:.0f} % | **{'PASS' if ok else 'FAIL'}** |" for k, (v, ok, txt) in checks(cfg, res).items())
    return f"""# Power budget (generated)

All phases installed. Laptop, ESP32-S3 hub and USB camera are powered by the laptop. Path: {b['name']} → fuse → e-stop →
SKR Pico; the bus is the pack voltage ({b['cutoff_volts']:g}–{ch['volts']:g} V). Charging: USB-C charger → {ch['name']} → pack,
{ch['volts']:g} V, {ch['amps']:g} A; it can stay plugged in while measuring.

| Load | Phase | Typical W | Peak W | Idle W |
|---|---:|---:|---:|---:|
{rows}

| | Typical | Peak | Idle (motors asleep) |
|---|---:|---:|---:|
| Motor board input | {t['dc_w']:.1f} W | {p['dc_w']:.1f} W | {i['dc_w']:.1f} W |
| From the pack | {t['bat_w']:.1f} W | {p['bat_w']:.1f} W | {i['bat_w']:.1f} W |
| Pack current at {b['cutoff_volts']:g} V (worst) | {t['amps_low']:.2f} A | {p['amps_low']:.2f} A | {i['amps_low']:.2f} A |
| On the pack alone | {t['hours']:.1f} h | {p['hours']:.1f} h | {i['hours']:.0f} h |

Usable energy {res['usable_wh']:.0f} Wh ({b['capacity_ah']:g} Ah × {b['nominal_volts']:g} V × {100 * b['usable_fraction']:.0f} %, 4.0 → 3.0 V per cell).
Charge {res['charge_w']:.0f} W ({res['usb_w']:.0f} W from USB-C): empty to full in about {res['charge_h']:.0f} h. Plugged in while measuring, it
covers the typical draw and still charges. Off (e-stop pressed): no draw from the pack; charging still works.

| Check | | Headroom | |
|---|---|---:|---|
{ck}

Headroom needed: pack current ≥ {100 * cfg['required_headroom']:.0f} % under its limit. Efficiencies and the usable fraction are estimates until
measured (stage 01 tests T12, T13, T15). No low-voltage alarm: recharge after each session (the BMS is the last cut-off).
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
