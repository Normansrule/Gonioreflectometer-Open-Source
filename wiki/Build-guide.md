<!-- generated from wiki/src/Build-guide.md by tools/refs_bib.py - edit the source -->

# Build guide

## Start here

1. **Set up once:** publish the repo ([commands](Commands.md#publish-and-update-the-private-github-repo-ubuntu)), then `make setup`. Decide your parts in [PARTS.md](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/PARTS.md).
2. **Try the software without hardware:** [Try without hardware](Commands.md#try-without-hardware).
3. **Do the steps in order.** `make next` prints the next one; its stage checklist has the full instructions.
4. **After each step:** `make done id=M05.1` closes its GitHub issue, ticks it in the checklists and figures, and publishes.

Every step (= one GitHub issue) is **Time · Needs** → **Do** (numbered actions) → **Verify** (a measurement with a pass number) → **If a check fails** (what to look at first) → **Record** (the file to fill in). To change or extend anything, see [Tweak and extend](Extend.md).

## Two ways to run

| | Laptop mode | Standalone mode (stage 15) |
|---|---|---|
| Who runs jobs | laptop (`opengonio`) | Pi Zero 2 W (`opengonio station`) |
| Inputs | laptop or buttons | buttons + OLED menu; phone WebUI for jogging |
| Data | processed live | saved on the Pi → laptop `opengonio pull` + `opengonio verify` |
| Extra cost | $0 | $38 kit (optional) |

![Laptop mode and standalone mode](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/docs/assets/architecture.svg?raw=true)
