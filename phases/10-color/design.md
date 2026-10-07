# 10 · Design

**Optional colour kit.** Nothing in BRDF measurement, calibration or the 3D shape needs this stage; it adds colour bands, polarizers (shine separated from colour) and the lights for photometric stereo. It is off by default (`lights.multispectral.built: false` in `software/config/machine.yaml`), so `opengonio scan run` leaves out the photometric set; set `true` once you build it (M30). Spectral sensor (SPC) and colour kit (MSK) are bought separately.

## Spectral sensor (AS7341)

| | |
|---|---|
| Job | 10-band spectrum of the spot at the zero point; the camera keeps doing images |
| Mount | `3d/SPC-03a_spectral_tube` on the camera post, above the lens; 3 mm aperture, ~4° field, ~25 mm spot |
| Wiring | SDA → Pico GP16, SCL → GP17, VIN → 3V3, GND (shares the OLED bus; address 0x39) |
| Read | hub `SPEC?` → `SPEC f1..f8 clear nir`; `opengonio capture … --spectral` writes `spectral.csv` |
| Geometry | `spectral.elevation_deg` = atan(height above camera axis / 350) in `machine.yaml` |
| Firmware | register-level driver in `firmware/pico-hub/main.py` (from the ams datasheet; untested on hardware: check M29.2) |

## Results

(fill in)


- 8 narrow-band LEDs (~420–660 nm) on a ring at the top of a 40° mast on the light arm; one band on at a time [N37].
- One NLDD-350H, supply switched by E4 GPIO4 (`M62 P1`); band chosen by Pico GP8–15 → ULN2803A.
- The 40° mast also gives photometric stereo its non-coplanar lights (Phase 11–12).
- Polarizer film in the lamp slot; rotatable disc on the lens [V49][V51].

## 3D parts

| Part | Source |
|---|---|
| LED ring, 40° mast, polarizer holders (MSK-06) | Onshape `MSK` |
