# 11 · 3D scan: capture

<img src="../../docs/assets/steps/11.svg" width="100%" alt="Steps of stage 11">

<img src="../../docs/assets/scanner.svg" width="100%" alt="3D scan: capture">

$4.49 · total so far $428.39 / $450

[Design](design.md) · [Parts list](bom.csv) · [3D files](3d/) · [Tests](test.csv)

## M31 · Scan hardware

Scan camera fixed at 650 mm, object held securely; nothing on the measuring side moves. · 0/3 steps done · ~1.2 h hands-on · ~1 wk

### M31.1 Print risers and wedge

**Time** 10 min (+ print 3 h) · **Needs** SCN-03 prints · a second CAM-03b camera plate

#### Do

1. Print `SCN-03a/b/c` risers, `SCN-03d_scan_camera_wedge_15.stl` and a second `CAM-03b_camera_plate.stl` + `CAM-03a_aperture_stop_f8.stl`.

#### Verify

- [ ] Risers sit flat on the platter.
- [ ] Wedge: thin end 3 mm, thick end 16.4 mm (calipers).

#### Record

Tick the boxes; `make done id=M31.1`.

### M31.2 Mount the scan camera

**Time** 45 min · **Needs** scan post at x = 658 (M12.2) · CAM-08 M2.5 × 20 screws · CAM-04 camera + CAM-05 lens (optional kit), or the measuring camera moved here

#### Do

1. The scan post stands on the outrigger at x = 658 mm (650 mm × cos 15° + 30) since M12.2.
2. Camera plate on the post, wedge between plate and board (thick end down): lens centre 168 mm above the zero point, looking 15° down.
3. Focus on the zero point (M17.3 method) and lock the lens; aperture stop on.
4. Plug it in; `machine.yaml` → `scan.camera_index` = its index (usually 1); `opengonio scan plan`.

#### Verify

- [ ] `scan plan` prints `two_cameras: true` and both clearances > 0.
- [ ] Scan camera image: zero point within ±15 px of centre; the measuring camera is not in the picture.
- [ ] 1 mm grid resolved at the zero point.

#### If a check fails

- Measuring camera visible at the bottom edge: raise the scan camera (bigger `scan.camera_elevation_deg`, re-check with `scan plan`).
- One-camera option (no CAM-04/05): move the measuring camera to this post, refocus, set `scan.camera_index` = `camera.index`; move it back and redo M17.3–M17.5 before measuring BRDFs.

#### Record

Index, height and the clearance numbers in phases/11-scan-capture/design.md → Results.

### M31.3 Putty hold (S3)

**Time** 20 min · **Needs** SCN-01 putty · 100 g object · SCN-02 ChArUco mat

#### Do

1. Object on the riser with putty; `opengonio move M2=80`; spin `M1` three turns (`opengonio move M1=180` … `-180`).

#### Verify

- [ ] Mat corners move ≤ 1 px between turn 1 and turn 3.

#### Record

S3 in `phases/11-scan-capture/test.csv`.

## M32 · Camera position calibrated

Every photo's pose known to 0.3 mm. · 0/2 steps done · ~50 min hands-on · ~1 wk

### M32.1 ChArUco board

**Time** 20 min · **Needs** CAL-04 print + glass

#### Do

1. Print the ChArUco board at 100 %; glue flat under the picture-frame glass.

#### Verify

- [ ] Square size = 10.0 ± 0.1 mm (calipers).

#### Record

Tick the boxes; `make done id=M32.1`.

### M32.2 Calibrate

**Time** 30 min · **Needs** board on the platter

#### Do

1. `opengonio scan calibrate`
2. Copy the printed file path into `scan.calibration` in `machine.yaml`.

#### Verify

- [ ] S1 reprojection RMS ≤ 0.5 px; S2 ≤ 0.2° and ≤ 0.3 mm (both printed).

#### If a check fails

- S1 high: blurry board → refocus; board not flat → re-glue.

#### Record

S1, S2 in `test.csv`; commit.

## M33 · First full scan

144 photos (plus the photometric set with the optional LED bank), unattended. · 0/2 steps done · ~25 min hands-on · ~1 wk

### M33.1 Background pass

**Time** 10 min (+ ~15 min) · **Needs** empty platter with the riser

#### Do

1. Riser on, no object, lamp at M4 = 30: `opengonio scan run --background --out scan_cube`.

#### Verify

- [ ] `ls scan_cube/background | wc -l` prints 144.

#### Record

Tick the boxes; `make done id=M33.1`.

### M33.2 Cube scan

**Time** 15 min (+ ~20 min) · **Needs** printed 40 mm cube · putty

#### Do

1. Cube on the riser, one face toward M1 = 0.
2. `opengonio scan run --out scan_cube`

#### Verify

- [ ] `ls scan_cube/images | wc -l` prints 144; with the LED bank (M30), `scan_cube/ps/` has the photometric set.
- [ ] No image blurred at 100 % zoom.

#### Record

Folder name in phases/11-scan-capture/design.md → Results.

[Sources](../../REFERENCES.md): S9 · S12 · S14 · S20 · G4 · G39 · V7 · V8 · V9 · V10 · V11 · V12 · V13 · V14 · V15 · V16 · V17 · V18 · V25 · V27 · V30 · V48 · V50 · V51 · V53 · V54 · V55 · H49 · K1 · K2 · K5
