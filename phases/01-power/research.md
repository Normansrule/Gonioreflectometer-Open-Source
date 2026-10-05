# 01 · Research

## Requirements

| Need | Met by | Check |
|---|---|---|
| One certified plug, no exposed mains | GST60A24: UL62368-1, Level VI, 90.5 % [P1][P2] | mains only inside adapter |
| ≥ 25 % headroom, final machine | 28 W peak on 60 W | `tools/power_budget.py --check` |
| Fuse, reverse polarity, switch, e-stop on motors | 3.15 A T fuse, IRF4905, rocker, IDEC e-stop | T1–T8 |
| Low idle | ~1.2 W asleep (`opengonio sleep`) | T10 |
| No 5 V buck | no Pi; laptop powers Pico and camera | — |

Numbers: [power_budget.md](power_budget.md).
