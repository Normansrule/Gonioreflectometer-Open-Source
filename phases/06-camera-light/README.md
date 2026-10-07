# 06 · Camera and light

<img src="../../docs/assets/steps/06.svg" width="100%" alt="Steps of stage 06">

<img src="../../docs/assets/brdf-lobe.svg" width="100%" alt="Camera and light">

$98.36 · total so far $360.13 / $450

[Design](design.md) · [Parts list](bom.csv) · [3D files](3d/)

## M17 · Camera sees the zero point

Sharp, fixed-exposure image centred on the sample. · 0/5 steps done · ~2.8 h hands-on · ~2 wk

### M17.1 Camera reaches the software

**Time** 30 min · **Needs** CAM-01 camera · Windows PowerShell (or a Linux laptop)

#### Do

1. WSL's standard kernel has no USB-camera driver, so camera stages run `opengonio` from Windows Python. PowerShell, in the repo folder (`cd \\wsl.localhost\Ubuntu\home\<you>\projects\Gonioreflectometer-Open-Source`):
2. `py -m venv $HOME\og-win; & $HOME\og-win\Scripts\pip install "./software[hw]"`
3. `usbipd detach --busid <E4 busid>` (Windows keeps the E4 as a COM port); set `controller.port: COM5` (your port) in `machine.yaml`.
4. `& $HOME\og-win\Scripts\opengonio status`

#### Verify

- [ ] `status` prints `<Idle|` or `<Alarm|`.
- [ ] `& $HOME\og-win\Scripts\python -c "import cv2; print(cv2.VideoCapture(0).read()[0])"` prints `True`.

#### If a check fails

- `False`: camera index is 1 (laptop webcam is 0); set `camera.index: 1`.
- Linux laptop instead: everything runs natively; `v4l2-ctl --list-devices` shows the camera.

#### Record

Which setup you use in phases/06-camera-light/design.md → Results.

### M17.2 Mount

**Time** 1 h (+ print 1 h) · **Needs** CAM-01 camera · CAM-02 lens · CAM-03 prints

#### Do

1. Order the stage-06 parts ticked in `PARTS.md`, plus CAL-01 PTFE, CAL-02 mirror (stage 07): M17.5–M19 use them. Print `CAM-03a_aperture_stop_f8.stl`, `CAM-03b_camera_plate.stl`, `CAL-06a/b` holders.
2. Camera board on the plate: 4 × M2.5 × 8 (CAM-07) self-tap into the 2.2 mm holes.
3. Camera on the post: lens front 350 mm from the zero point; aperture stop in front of the lens.

#### Verify

- [ ] Tape measure zero point → lens front: 350 ± 2 mm; camera axis level (phone level app on the plate).

#### Record

Tick the boxes; `make done id=M17.2`.

### M17.3 Focus

**Time** 30 min · **Needs** printed 1 mm grid

#### Do

1. Grid at the zero point. Live view: Windows *Camera* app (or `guvcview` on Linux).
2. Turn the lens for the sharpest grid; lock it with the M12 lock ring.

#### Verify

- [ ] 1 mm lines resolved across the whole image.

#### Record

Image as `phases/06-camera-light/focus.jpg`.

### M17.4 Centre

**Time** 15 min · **Needs** table centre mark

#### Do

1. Image the table centre mark; find its pixel position (any image viewer).

#### Verify

- [ ] Within ±15 px of the image centre (= ±0.5 mm).

#### If a check fails

- Off-centre: shim the camera plate or slide it on the post.

#### Record

Offset (px) in design.md.

### M17.5 Lock exposure and colour

**Time** 30 min · **Needs** CAL-01 PTFE in its holder (or CAL-07 grey card if you bought it)

#### Do

1. Lock exposure, gain, white balance (`v4l2-ctl` lines in `software/src/opengonio/camera/uvc.py`).
2. Two frames of the PTFE tile 60 s apart.

#### Verify

- [ ] Mean grey of the two frames differs < 1 %.

#### If a check fails

- Drifts: auto exposure still on; `v4l2-ctl -l` and set `auto_exposure=1`.

#### Record

Locked values into `machine.yaml` → `camera:` (`exposure_ms`); commit.

## M18 · Lamp on and safe

Light switches from the laptop, stays cool and steady. · 0/3 steps done · ~1.6 h hands-on · ~1 wk

### M18.1 Lamp assembly

**Time** 1 h (+ print 2 h) · **Needs** LSR-01 COB · LSR-06 holder · LSR-02 driver · LSR-03 heatsink · LSR-04 pad · LSR-05 print · PWR-20 lever connectors

#### Do

1. Print `LSR-05a_lamp_tube`, `LSR-05b_lamp_cap`. COB in the pre-wired holder (LSR-06); thermal pad on the heatsink; holder + COB + heatsink into the body's square pocket, leads out of the cap slot; cap on with 4 × M3 × 8.
2. Lamp clamp onto the horizontal arm (M5 × 10 + T-nut), aperture facing the zero point.
3. Driver (LSR-02) pins into the breadboard. +Vin row ← 24 V sense row; −Vin row → E4 HE0 `−` (cut jumper under the screw).
4. Driver +Vo / −Vo rows → two chains of 5 male–female jumpers along the arm (slack for 20–340°); at the lamp, lever connectors join each chain's last female end (cut off, stripped, folded double) to the holder's red (+) / black (−).

#### Verify

- [ ] Polarity checked with the meter before power: +Vo row → red lead beeps.

#### Record

Tick the boxes; `make done id=M18.1`.

### M18.2 Switch and heat

**Time** 20 min · **Needs** TLS-05 temperature probe · `installed_phase: 6`

#### Do

1. `opengonio light on`; wait 10 min; `opengonio light off`. Repeat on/off 5 ×.

#### Verify

- [ ] Lamp follows every command.
- [ ] COB case ≤ 70 °C after 10 min.

#### If a check fails

- Lamp always on: driver −Vin on GND instead of HE0.

#### Record

Temperature in phases/06-camera-light/design.md → Results.

### M18.3 Warm-up time

**Time** 15 min (+ 10 min run) · **Needs** PTFE tile or grey card · room dark

#### Do

1. `opengonio capture warmup --minutes 10 --out data/warmup`
2. Set `lights.white.warmup_s` in `machine.yaml` to the printed value.

#### Verify

- [ ] `settle_s` ≤ 300.

#### If a check fails

- Longer: thermal pad missing or driver current too high (check LSR-02 is the 350 mA part).

#### Record

`settle_s`, `change_pct` in design.md; commit.

## M19 · Mirror test

First real data proves the angles are right. · 0/1 steps done · ~30 min hands-on · ~1 wk

### M19.1 Mirror sweeps

**Time** 30 min · **Needs** CAL-02 mirror · CAL-06b holder (print)

#### Do

1. Mirror in `CAL-06b_mirror_holder`, clamped on the table.
2. `opengonio capture mirror --theta 20`, then `--theta 40`, then `--theta 60`.
3. `opengonio verify data/mirror_20 data/mirror_40 data/mirror_60`
4. `opengonio curve data/mirror_40`; open `data/mirror_40/curve.svg`.

#### Verify

- [ ] Each `mirror_peak_error_deg` between −0.5 and +0.5.
- [ ] The chart's peak sits within one dot of the orange line.

#### If a check fails

- Same sign every time: table zero offset — fixed in M22.2.
- No clear peak: mirror not facing the camera at M3 = 0; reseat the holder.

#### Record

Three errors in phases/06-camera-light/design.md → Results; commit.

## M20 · First reflectance curves

Two real materials measured and pictured. · 0/2 steps done · ~40 min hands-on · ~1 wk

### M20.1 Paper

**Time** 20 min · **Needs** matte printer paper

#### Do

1. Clamp the paper on the table.
2. `opengonio capture inplane --step 10 --out data/paper`
3. `opengonio verify data/paper`
4. `opengonio curve data/paper`; open `curve.svg`.

#### Verify

- [ ] verify: `lamp_drift_pct` within ±2, `result` PASS.
- [ ] Chart: flat-ish curves; centre_mean ÷ cos(θr) varies < 15 % for θr ≤ 60° at a fixed θi (from `curve.csv`).

#### If a check fails

- Drift FAIL: raise `warmup_s`; check the lamp heatsink.

#### Record

`curve.csv` + `curve.svg` → `phases/06-camera-light/paper_*`.

### M20.2 Glossy plastic

**Time** 20 min · **Needs** acrylic sheet or flat LEGO plate

#### Do

1. Clamp it.
2. `opengonio capture inplane --step 10 --out data/plastic`; `opengonio verify data/plastic`; `opengonio curve data/plastic`.

#### Verify

- [ ] Each θi curve peaks at θr = θi ± 10° (chart).

#### Record

`curve.csv` + `curve.svg` → `phases/06-camera-light/plastic_*`; commit.

> **Safety:** Don't stare into the lamp.

[Sources](../../REFERENCES.md): R1 · G12 · T32 · V1 · V2 · V3 · V4 · V5 · V7 · V8 · V9 · N3 · N11 · N24 · N25 · N45 · N46 · N47 · H13 · H14 · H15 · H49 · K1 · K2 · K3 · K4 · K5 · K6 · K23 · L1 · L2 · L3 · L4 · L5 · L6 · L7 · L21 · F13
