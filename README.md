<img src="docs/assets/hero.svg" width="100%" alt="OpenGonio: light arm circling a turning sample, fixed camera">

# Gonioreflectometer-Open-Source

**OpenGonio** measures how materials reflect light and scans objects in 3D. Laptop-controlled (USB, WiFi or Bluetooth) plus physical buttons. Under $500. Based on Ansari-Asl et al. 2024 [R1].

| | |
|---|---|
| **Measures** | Bidirectional reflectance distribution function (BRDF), spatially varying BRDF (SVBRDF) for textures, 8 colour bands |
| **Scans** | Objects up to 110 mm → mesh with materials (PLY / OBJ / glTF) |
| **Precision** | 0.1° repeatability target, optical homing |
| **Cost** | $498.95 · $443.27 if you own the consumables |
| **Site** | [`docs/index.html`](docs/index.html): simulator, BRDF explorer, scan planner, equations |

## Phases

<img src="docs/assets/phases.svg" width="100%" alt="17 phases">

Each phase is a GitHub milestone; each step is an issue with a checklist. Every folder: `research/` · `design/` · `3d/` · `bom/` · `test/` (only where needed).

<!-- phases:start -->
| # | Phase | Goal | Cost |
|---:|---|---|---:|
| 00 | [Plan](phases/00-plan/) | Agree the design and budget before buying anything. | — |
| 01 | [Power box](phases/01-power/) | One wall plug gives safe, fused 24 V with an e-stop. | $67 |
| 02 | [Controller and buttons](phases/02-controller/) | The laptop and the buttons can talk to the machine. | $56 |
| 03 | [Frame](phases/03-frame/) | A flat, level base with every future hole already drilled. | $63 |
| 04 | [Light arm moves (M4)](phases/04-light-arm/) | The light circles the sample and comes back to the same spot. | $45 |
| 05 | [Table turns (M3)](phases/05-table/) | The sample turns to any angle and comes back to the same spot. | $22 |
| 06 | [First measurement](phases/06-camera-light/) | Camera and light see a mirror's shine at the right angle. | $93 |
| 07 | [Calibrate → game material](phases/07-calibrate/) | A measured swatch looks right in Unreal or Unity. | $73 |
| 08 | [Tilt (M2) → full reflectance (BRDF)](phases/08-tilt/) | The sample tilts, so the light can come from any direction. | $22 |
| 09 | [Spin (M1) → brushed metal and textures](phases/09-spin/) | The sample spins, so direction-dependent shine and textures are measured. | $22 |
| 10 | [Colour bands and polarizers](phases/10-color/) | Measure 8 colour bands and separate shine from colour. | $30 |
| 11 | [3D scan: capture](phases/11-scan-capture/) | Photograph an object from 144 known positions. | $4 |
| 12 | [3D scan: mesh](phases/12-scan-mesh/) | Turn the photos into an accurate 3D model. | — |
| 13 | [Material on the 3D model](phases/13-object-material/) | The scanned object looks real in a game engine. | — |
| 14 | [Laptop app](phases/14-laptop-app/) | Every workflow runs from one app or the buttons — no terminal. | — |
| 15 | [Release](phases/15-release/) | Public, certified open hardware. | — |
| 16 | [Upgrades (optional)](phases/16-upgrades/) | Research-grade extras that keep the cheap build working. | — |
<!-- phases:end -->

<img src="docs/assets/budget.svg" width="100%" alt="Cost per phase">

## Try it (no hardware)

```bash
cd software && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
python -m pytest -q
opengonio check-pose M4=60 M3=30        # angles + collision check
opengonio --dry-run move M4=80 M3=25    # prints the G-code
opengonio scan demo --out demo          # synthetic 3D scan
```

## Publish as a private GitHub repo (fresh Ubuntu)

```bash
sudo apt update && sudo apt install -y git python3-venv unzip curl
sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
sudo apt update && sudo apt install -y gh
gh auth login --hostname github.com --git-protocol https --web --scopes workflow
gh auth setup-git
mkdir -p ~/projects && unzip ~/Downloads/Gonioreflectometer-Open-Source.zip -d ~/projects
cd ~/projects/Gonioreflectometer-Open-Source && bash scripts/publish.sh
```

`publish.sh` creates the private repo, pushes, and adds the milestones and issues. Re-run after edits [R70].

## Credits

Design: Ansari-Asl, Barbieri, Obein, Hardeberg, *J. Imaging* 10(3):55, 2024, [doi:10.3390/jimaging10030055](https://doi.org/10.3390/jimaging10030055). Theory: Hanrahan, Stanford CS348b. Firmware: [FluidNC](http://wiki.fluidnc.com/), [MicroPython](https://docs.micropython.org/). Every source: [REFERENCES.md](REFERENCES.md). Figures are original.

Hardware CERN-OHL-S-2.0 · software GPL-3.0-or-later · docs CC BY-SA 4.0 ([LICENSE](LICENSE)).
