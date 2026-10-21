# 10 · Design

> **BLOCKED — do not build or power the LED bank (MSK-01…03) yet.** The MEAN WELL NLDD-350H regulates only with at least 6 V across its output; a single colour LED drops about 2–3.5 V, so the driver runs out of regulation, and switching LEDs on its live output (MSK-03 low-side) can spike the current through the next LED. The software refuses `M62 P3` (any spelling, and `M64`) while `lights.multispectral.blocked` is set in `machine.yaml`. A reviewed driver circuit (driver whose output range covers one LED, switched with its supply off) is needed first. The spectral sensor (SPC) and polarizers (MSK-05) are unaffected.

**Optional colour kit.** Nothing in BRDF measurement, calibration or the 3D shape needs this stage; it adds colour bands, polarizers (shine separated from colour) and the lights for photometric stereo. It is off by default (`lights.multispectral.built: false` in `software/config/machine.yaml`), so `opengonio scan run` leaves out the photometric set; set `true` once you build it (M30). Spectral sensor (SPC) and colour kit (MSK) are bought separately.

## Spectral sensor (AS7341)

| | |
|---|---|
| Job | Spectrum of the spot at the zero point: 8 visible bands (F1–F8, 415–680 nm) + clear + NIR = 10 raw readings; the camera keeps doing images |
| Mount | `3d/SPC-03a_spectral_tube` on the camera pillar (FRM-09h) above the lens, M2 × 16 into its z 181 pilot; 3 mm aperture, ~4° field, ~25 mm spot |
| Wiring | SDA → ESP32-S3 GPIO 1, SCL → GPIO 2, VIN → 3V3, GND (shares the OLED bus; address 0x39) |
| Read | hub `SPEC? <id>` → `SPEC #<id> f1..f8 clear nir` (raw counts, 0–65535, validated); `opengonio capture … --spectral` writes `spectral.csv` |
| Geometry | `spectral.elevation_deg` = atan(height above camera axis / 350) in `machine.yaml` |
| Firmware | register-level driver in `firmware/hub/main.py` (from the ams datasheet; untested on hardware: check M29.2) |

## Results

(fill in)


- 7 narrow-band LEDs (450, 465, 520, ≈ 590, ≈ 605, 620, 660 nm; pre-soldered leads, no solder) in 7 of the 8 slots of a ring at the top of a 40° mast on the light arm; one band on at a time [N37].
- One NLDD-350H, supply switched by the SKR Pico HB output (`M62 P3`); band chosen by ESP32-S3 GPIO 8–14 and 21 → two 4-channel MOSFET modules (MSK-03, opto-isolated inputs, screw terminals), low-side on each LED cathode.
- The 40° mast also gives photometric stereo its non-coplanar lights (Phase 11–12).
- Polarizer film in the lamp slot; rotatable disc on the lens [V49][V51].

## 3D parts

| Part | Source |
|---|---|
| LED ring, 40° mast, polarizer holders (MSK-06) | Onshape `MSK` |
