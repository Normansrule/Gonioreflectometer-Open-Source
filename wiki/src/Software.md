# Software

Python package `opengonio` ([software/]({{REPO}}/software)). Motion: grblHAL on the BTT SKR Pico over USB-C (FluidNC ESP32 boards also supported); the ESP32-S3 hub reads keypads and sensors.

```bash
make setup && source .venv/bin/activate
make sim                                   # simulated machine, ends "ALL PASS"
opengonio check-pose M4=60 M3=30           # angles + collision check
opengonio --sim plastic capture inplane --step 10 --out data/sim/plastic
opengonio curve data/sim/plastic           # reflectance curve
```

- Laptop mode: the laptop runs jobs. Standalone mode: a Pi Zero 2 W runs them; `opengonio pull` + `opengonio verify` bring data back.
- `make all`: rebuild docs, checks, tests.
