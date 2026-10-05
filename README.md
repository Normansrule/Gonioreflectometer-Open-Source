<img src="docs/assets/hero.svg" width="100%" alt="OpenGonio">

# Gonioreflectometer-Open-Source

Measures how materials reflect light, then scans objects in 3D. Laptop or buttons control it over USB, WiFi or Bluetooth. $498.95 total. Based on Ansari-Asl et al. 2024 [R1].

[Interactive site](docs/index.html) · [References (478)](REFERENCES.md) · [Papers (PDF)](papers/)

## Phases

<img src="docs/assets/axes.svg" width="100%" alt="Four axes">

One GitHub milestone per phase, one checklist issue per step.

<!-- phases:start -->
| # | Phase | Goal | Cost |
|---:|---|---|---:|
| 00 | [Plan](phases/00-plan/) | Fix the design and budget before buying. | — |
| 01 | [Power box](phases/01-power/) | Safe, fused 24 V from one wall plug, with an e-stop. | $67 |
| 02 | [Controller and buttons](phases/02-controller/) | Laptop and buttons talk to the machine. | $56 |
| 03 | [Frame](phases/03-frame/) | Flat, level base with every hole drilled. | $63 |
| 04 | [Light arm moves (M4)](phases/04-light-arm/) | Light circles the sample and returns to the same spot. | $45 |
| 05 | [Table turns (M3)](phases/05-table/) | Sample turns to any angle and returns to the same spot. | $22 |
| 06 | [First measurement](phases/06-camera-light/) | Camera sees a mirror's shine at the right angle. | $93 |
| 07 | [Calibrate → game material](phases/07-calibrate/) | A measured swatch looks right in Unreal or Unity. | $73 |
| 08 | [Tilt (M2) → full reflectance (BRDF)](phases/08-tilt/) | Sample tilts, so light can come from any direction. | $22 |
| 09 | [Spin (M1) → brushed metal and textures](phases/09-spin/) | Sample spins: brushed metal and textures. | $22 |
| 10 | [Colour bands and polarizers](phases/10-color/) | 8 colour bands; polarizers split shine from colour. | $30 |
| 11 | [3D scan: capture](phases/11-scan-capture/) | Photograph an object from 144 known positions. | $4 |
| 12 | [3D scan: mesh](phases/12-scan-mesh/) | Turn the photos into an accurate 3D model. | — |
| 13 | [Material on the 3D model](phases/13-object-material/) | The scanned object looks real in a game engine. | — |
| 14 | [Laptop app](phases/14-laptop-app/) | Every workflow from one app or the buttons. | — |
| 15 | [Release](phases/15-release/) | Public, certified open hardware. | — |
| 16 | [Upgrades (optional)](phases/16-upgrades/) | Research extras; the cheap build keeps working. | — |
<!-- phases:end -->

<img src="docs/assets/budget.svg" width="100%" alt="Cost per phase">

<details><summary><b>Milestones and issues</b></summary>

One milestone per phase; each item is a checklist issue.

<!-- issues:start -->
- **P00 · Plan** — [P00.1] Check the budget · [P00.2] Set up computer-aided design (CAD)
- **P01 · Power box** — [P01.1] Buy and print · [P01.2] Build · [P01.3] Test
- **P02 · Controller and buttons** — [P02.1] Flash boards · [P02.2] Wire and box · [P02.3] Test links
- **P03 · Frame** — [P03.1] Cut and drill · [P03.2] Assemble
- **P04 · Light arm moves (M4)** — [P04.1] Build the ring drive · [P04.2] Tune
- **P05 · Table turns (M3)** — [P05.1] Build · [P05.2] Tune
- **P06 · First measurement** — [P06.1] Mount camera and light · [P06.2] Mirror test · [P06.3] First curves
- **P07 · Calibrate → game material** — [P07.1] Dark box and targets · [P07.2] Calibrate · [P07.3] Fit and export
- **P08 · Tilt (M2) → full reflectance (BRDF)** — [P08.1] Build the tilt yoke · [P08.2] Full scan
- **P09 · Spin (M1) → brushed metal and textures** — [P09.1] Build the spin platter · [P09.2] Measure
- **P10 · Colour bands and polarizers** — [P10.1] LED bank · [P10.2] Polarizers and calibration
- **P11 · 3D scan: capture** — [P11.1] Scan setup · [P11.2] Calibrate camera position · [P11.3] Capture
- **P12 · 3D scan: mesh** — [P12.1] Quick preview · [P12.2] Full mesh
- **P13 · Material on the 3D model** — [P13.1] Fit textures · [P13.2] Export
- **P14 · Laptop app** — [P14.1] Control user interface (UI) · [P14.2] One-button workflows
- **P15 · Release** — [P15.1] Finish docs · [P15.2] Publish
- **P16 · Upgrades (optional)** — [P16.1] Adaptive sampling · [P16.2] Space carving · [P16.3] Compare with MERL / RGL data
<!-- issues:end -->
</details>

<details><summary><b>Test materials · light and camera placement</b></summary>

θi = M4 − M3 (light from the normal), θr = M3 (camera from the normal), in-plane. Isotropic needs 3 angles (M4, M3, M2); anisotropic needs 4 (adds M1).

| Material | Type | Light (M4) · camera (θr = M3) | What to look for |
|---|---|---|---|
| PTFE white reference | isotropic, diffuse | 45° · 0° (CIE 45°:0°) | flat response; calibrates brightness [N30] |
| Matte paper | isotropic, diffuse | 60° · sweep M3 | ≈ cos θr |
| First-surface mirror | isotropic, specular | 60° · 30° | peak at M3 = M4/2; calibrates angles |
| Glossy plastic (acrylic, LEGO) | isotropic, glossy | 40/80/120° · M4/2 ± 10° | lobe width → roughness |
| Metallic car paint | isotropic, flake | 90° · 35° (15° off specular) | sparkle, colour shift [N8] |
| Brushed aluminium | **anisotropic** | 60° · 30°, spin M1 0–180° | highlight stretches across the brushing [G9] |
| Satin ribbon | **anisotropic** | 70° · 35°, M2 15°, M1 15° steps | two lobes vs direction |
| Velvet / retroreflective tape | back-scatter | 20° (closest allowed) · 10° | peak toward the light |
| 3D scan: matte print, painted toy | object | lamp 30°, camera 650 mm, M2 90→10°, M1 36 steps | spray shiny parts matte |
</details>

<details><summary><b>Equations</b></summary>

**BRDF and reflection equation** [R2][G1]

```math
f_r(\omega_i\to\omega_r)=\frac{dL_r(\omega_i\to\omega_r)}{dE_i}\;[\mathrm{sr}^{-1}],\qquad L_r(x,\omega_r)=\int_{H^2} f_r\,L_i(x,\omega_i)\cos\theta_i\,d\omega_i
```

**Reciprocity, isotropy, energy** [R2]

```math
f_r(\omega_r\to\omega_i)=f_r(\omega_i\to\omega_r),\qquad f_r^{\mathrm{iso}}=f_r(\theta_i,\theta_r,|\varphi_r-\varphi_i|),\qquad \int_{H^2} f_r\cos\theta_r\,d\omega_r\le 1
```

**Anisotropic (needs M1)** [G9]

```math
f_r^{\mathrm{aniso}}=f_r(\theta_i,\varphi_i,\theta_r,\varphi_r)\quad\text{(4 angles; } \varphi \text{ measured from the brushing direction)}
```

**Mirror, Snell, total internal reflection** [R2]

```math
\hat R=\hat I-2(\hat I\cdot\hat N)\hat N,\qquad \eta_i\sin\theta_i=\eta_t\sin\theta_t,\qquad 1-\mu^2\left(1-(\hat I\cdot\hat N)^2\right)<0
```

**Fresnel (Schlick), Lambert** [R7][R2]

```math
F(\theta)=F_0+(1-F_0)(1-\cos\theta)^5,\quad F_0=\left(\tfrac{\eta-1}{\eta+1}\right)^2,\qquad f_{r,d}=\frac{\rho_d}{\pi}
```

**Fitted model (Lambert + GGX)** [R6][T11][T17]

```math
f_r=(1-m)(1-F)\frac{\rho}{\pi}+\frac{D\,G_2\,F}{4\cos\theta_i\cos\theta_r},\quad D=\frac{\alpha^2}{\pi\left((h\cdot n)^2(\alpha^2-1)+1\right)^2},\quad h=\frac{\omega_i+\omega_r}{\lVert\omega_i+\omega_r\rVert}
```

**Sample orientation and angles** [R1]

```math
R=R_z(M_3)\,R_y(-M_2)\,R_x(M_1),\quad \omega^s=R^\top\omega^w,\quad \theta=\arccos(\omega^s\cdot\hat n),\quad \varphi=\operatorname{atan2}(\omega^s_z,\omega^s_y)
```

**Light and camera directions** [R1]

```math
\hat l=R_z(M_4)\,\hat x,\qquad \hat c=\hat x\;(\text{fixed}),\qquad \omega_i(p)=\frac{P_L-p}{\lVert P_L-p\rVert},\quad \omega_r(p)=\frac{P_C-p}{\lVert P_C-p\rVert}
```

**In-plane geometry (M2 = M1 = 0)** [R1]

```math
\theta_r=M_3,\qquad \theta_i=M_4-M_3,\qquad \text{specular: } M_3=\tfrac{M_4}{2}
```

**Step size** 

```math
\Delta\theta=\frac{360^\circ}{200\cdot 16\cdot G}\;\Rightarrow\;0.0047^\circ\,(M_4,\,G=24),\;0.0225^\circ\,(M_3,M_2),\;0.028^\circ\,(M_1)
```

**Optics** [R1]

```math
\frac{1}{p'}-\frac{1}{p}=\frac{1}{f},\quad m=\frac{p'}{p},\quad d_{\mathrm{Airy}}=2.44\,\lambda N,\quad \mathrm{DOF}\approx\frac{2Nc(1+m)}{m^2}
```

**HDR** [R5]

```math
g(Z_{ij})=\ln E_i+\ln\Delta t_j
```

**Repeatability from the mirror** [R1]

```math
\Delta\theta_L=\frac{s\,p_{px}\,P}{f\,D_L}
```

**3D scan: projection, view elevation** [S1][S11]

```math
\lambda[u,v,1]^\top=K(R_{oc}p_O+t_{oc}),\quad R_{oc}=R_{wc}RP,\qquad \epsilon=90^\circ-M_2+e_{cam}
```

**3D scan: camera calibration (AX = YB)** [V15]

```math
\min_{X,Y}\sum_i\left\lVert\log\left(A_i^{-1}XB_iY\right)\right\rVert^2
```

**3D scan: visual hull, photometric stereo** [S5][S4]

```math
V=\bigcap_j\{p:\pi_j(p)\in S_j\},\qquad I=L\,g,\;g=L^{+}I,\;\rho=\lVert g\rVert,\;\hat n=g/\rho
```

Full notes: [theory.md](phases/00-plan/research/theory.md) · [scan methods](phases/12-scan-mesh/research/methods.md).
</details>

<details><summary><b>Try without hardware</b></summary>

```bash
cd software && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
python -m pytest -q
opengonio check-pose M4=60 M3=30
opengonio scan demo --out demo
```
</details>

<details><summary><b>Flash and move the motors</b></summary>

Full steps (incl. WSL USB): [firmware.md](phases/02-controller/design/firmware.md).

```bash
bash scripts/e4.sh flash                  # FluidNC onto the E4 over USB
bash scripts/e4.sh wifi "YourWiFi" "YourPassword"   # then press E4 reset
bash scripts/e4.sh config fluidnc.local   # upload config.yaml, then press E4 reset
bash scripts/e4.sh test                   # home, move, motors off
bash scripts/pico.sh                      # button hub
```
</details>

<details><summary><b>Publish and update the private GitHub repo (Ubuntu)</b></summary>

```bash
# 1. Tools
sudo apt update && sudo apt install -y git python3-venv unzip curl
sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
sudo apt update && sudo apt install -y gh

# 2. Log in (workflow scope lets the CI file push)
gh auth login --hostname github.com --git-protocol https --web --scopes workflow
gh auth setup-git

# 3. Unzip (WSL: /mnt/c/Users/<you>/Downloads)
mkdir -p ~/projects && cd ~/projects
unzip -q ~/Downloads/Gonioreflectometer-Open-Source.zip
cd Gonioreflectometer-Open-Source

# 4. Private repo, push, milestones, issues
bash scripts/publish.sh

# 5. Check
gh repo view --web
```

Other account over SSH: `OWNER=<user> REMOTE=git@<host-alias>:<user>/Gonioreflectometer-Open-Source.git bash scripts/publish.sh`

**Every update after that** (pushes, then syncs milestones and issues with `.github/phases.yml`):

```bash
cd ~/projects/Gonioreflectometer-Open-Source

# your own edits
bash scripts/update.sh "phase 01: power box built"

# a new zip (keeps your history; replaces repo files with the zip's)
bash scripts/update.sh "update from new zip" /mnt/c/Users/<you>/Downloads/Gonioreflectometer-Open-Source.zip
bash scripts/get_papers.sh
```
</details>

## Licence

Hardware CERN-OHL-S-2.0 · software GPL-3.0-or-later · docs CC BY-SA 4.0 ([LICENSE](LICENSE)). Figures are original.
