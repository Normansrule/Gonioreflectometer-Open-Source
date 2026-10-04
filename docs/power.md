# Power

<img src="assets/power-flow.svg" width="100%" alt="Power path">

| Requirement (brief) | How it is met | Check |
|---|---|---|
| One certified plug-in adapter, no exposed mains | MEAN WELL GST60A24-P1J: UL62368-1, DOE Level VI, 90.5 % [P1][P2] | Mains only inside the adapter |
| Final-machine budget, ≥ 25 % headroom | 28 W peak vs 60 W → 114 % | `tools/power_budget.py --check` (CI) |
| 5.1 V buck ≥ 90 % for the Pi | **Not needed**: no Pi; laptop powers the Pico and camera over USB | — |
| Fuse, reverse polarity, master switch, latching e-stop on motor power | 3.15 A T fuse, IRF4905 P-FET, rocker, IDEC e-stop on the E4 feed | Power module tests T1–T9 |
| Wall-plug efficiency, idle draw | 88 % typical, ~1.2 W idle | T10 |
| Sleep mode | `opengonio sleep` → lights off + `$MD` (drivers off) | T10 |

Generated numbers: [`generated/power_budget.md`](generated/power_budget.md).
