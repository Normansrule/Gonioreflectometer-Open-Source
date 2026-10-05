# 02 · Design

## Wiring and pins

Verify E4 pins on its schematic [C1].

| E4 function | GPIO |
|---|---|
| M4 (X) step, dir | 27, 26 |
| M3 (Y) step, dir | 33, 32 |
| M2 (Z) step, dir | 14, 12 |
| M1 (E0) step, dir | 16, 17 |
| Enable (all) | 25 |
| TMC UART TX, RX | 22, 21 — addr X1 Y3 Z0 E2 |
| Home M4, M3, M2, M1 | 34, 35, 15, 36 |
| PAUSE | 39 |
| White light, LED bank, fan | 2, 4, 13 (`M62/M63 P0/P1/P2`) |

| Pico function | GP |
|---|---|
| HOME START STOP LIGHT NEXT (to GND) | 2–6 |
| UART to the Pi station (TX, RX) | 0, 1 |
| E-stop sense (J4, low = on) | 7 |
| LED bank → ULN2803A (Phase 10) | 8–15 |
| OLED (SDA, SCL) on the first I2C pair | 16, 17 |
| Optional AS5600 (SCL, SDA) | (17,16) (19,18) (21,20) (27,26) |

| From | To |
|---|---|
| J2 | E4 VIN |
| Motors M4 M3 M2 M1 | E4 X Y Z E |
| White COB driver −Vin | E4 HE0 |
| J4-1 / J4-2 | Pico GP7 / GND |

## Flash and test (copy-paste)

**0. Windows + WSL only:** pass USB into Ubuntu. PowerShell as administrator:

```powershell
winget install --interactive --exact dorssel.usbipd-win
usbipd list                              # find the E4 (CH340) and Pico bus IDs
usbipd bind --busid 1-4                  # once per device; use your bus ID
usbipd attach --wsl --busid 1-4          # after every replug
```

**1. Ubuntu, once:**

```bash
sudo apt install -y python3-venv unzip curl
sudo usermod -aG dialout $USER && newgrp dialout
cd ~/projects/Gonioreflectometer-Open-Source
ls /dev/ttyUSB* /dev/ttyACM*             # E4 = ttyUSB0, Pico = ttyACM0
```

**2. E4 motor board (FluidNC)** [R81][R24][R25]:

```bash
bash scripts/e4.sh flash                     # firmware + file system; Ctrl+] closes its terminal
bash scripts/e4.sh wifi "YourWiFi" "YourPassword"
## press E4 reset; join hotspot FluidNC / 12345678 if your WiFi fails
bash scripts/e4.sh config fluidnc.local      # or the printed IP, or 192.168.0.1
## press E4 reset
```

**3. Motors** (24 V on, e-stop released):

```bash
bash scripts/e4.sh test                      # info, home, M4=60, M4=90 M3=45, motors off
opengonio send '?'                           # status
opengonio send '$H'                          # home all
opengonio send 'G53 G1 X60 F600'             # raw move: M4 (X) to 60°
opengonio send '$MD'                         # motors off
```

Wrong direction: flip `direction_pin` `:low`/`:high` in [`config.yaml`](../../firmware/fluidnc/config.yaml), re-run `e4.sh config`. Bluetooth: use the BT build from [installer.fluidnc.com](https://installer.fluidnc.com) instead of step 2.

**4. Pico button hub** [R42]: hold BOOTSEL, plug in, drop the [MicroPython .uf2](https://micropython.org/download/RPI_PICO/) onto `RPI-RP2`, then:

```bash
bash scripts/pico.sh                         # copies main.py, prints PONG
opengonio panel                              # buttons drive the machine
```

## 3D parts

| Part | Source |
|---|---|
| Case + button panel (CTL-10) | Onshape `CTL`: E4 standoffs (4 × Ø3.2 on 83.6 × 60.6 mm), Pico standoffs (holes 47 × 11.4, Ø2.1), 6 × Ø12.2 button holes, USB slots, OG-40 floor |
| Pico | [STEP](https://datasheets.raspberrypi.com/pico/Pico-R3-step.zip) [C6] |
| FYSETC E4 | `E4 V1.0B.step` in the [hardware folder](https://github.com/FYSETC/FYSETC-E4/tree/main/hardware) [C1]: board 96 × 68 mm, 4 × Ø3.2 holes on 83.6 × 60.6 mm |
