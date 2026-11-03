# 02 · Design

## Boards

| Board | Job | Link to the laptop |
|---|---|---|
| **BTT SKR Pico V1.0** (CTL-01) [C12] | motion: 4 × TMC2209 (UART), endstops, lamp and fan outputs; runs **grblHAL** [R83][R85] | **USB-C** (USB VID 0x2E8A) |
| **ESP32-S3-DevKitC-1** (CTL-02, owned) [C13] | buttons, PAUSE, motor-power sense, LED bank, OLED / AS7341; runs MicroPython | **USB-C** — the connector marked USB (VID 0x303A), not UART |

Why not the FYSETC E4: USB-B only and three endstop inputs; grblHAL on the SKR Pico gives USB-C and four homed axes.
No WiFi on the SKR Pico: the laptop (or the Pi station, stage 15) connects over USB. FluidNC boards remain supported
(`controller.firmware: fluidnc` in machine.yaml, firmware/fluidnc/).

## Wiring and pins

Pin-by-pin tables for every connection (power to laptop): [README → Wiring](../../README.md#wiring), generated from [`docs/wiring.yaml`](../../docs/wiring.yaml). Summary:

SKR Pico pins from the maker pin diagram and grblHAL board map [C12][R85]:

| SKR Pico port | Use | grblHAL |
|---|---|---|
| X | M4 light arm | X |
| Y | M3 table | Y |
| Z1 (Z2 is the same driver) | M2 tilt | Z |
| E | M1 spin | A |
| X-STOP / Y-STOP / Z-STOP / E0-STOP (signal, GND, 5 V) | home M4 / M3 / M2 / M1 (optical modules: 3-pin leads) | X / Y / Z / A limit |
| HE (heater MOSFET): `12/24V` + `IO23` (switched −) | white COB driver +Vin / −Vin | `M62/M63 P4` (expected) |
| HB (bed MOSFET, IO21) | colour LED driver (stage 10, BLOCKED) | `P3` (expected) |
| FAN1 (IO17) | optional 40 mm fan (CTL-08) | `P2` (expected) |
| POWER 12/24 V screw terminal | red / black motor-power leads (via the J3 over-travel loop) | — |

Output port numbers depend on the firmware build: check them with `bash scripts/controller.sh pins` (grblHAL `$PINS`)
and set `lights.<name>.output` in machine.yaml to match.

ESP32-S3 hub pins (GPIO numbers; all clear of the strapping, USB, flash/PSRAM and UART0 pins [R86]):

| Hub function | GPIO |
|---|---|
| HOME START STOP LIGHT (keypad A keys 1–4; common to GND) | 4, 5, 6, 7 |
| NEXT, PAUSE (keypad B keys 1–2; common to GND) | 15, 16 |
| Motion-power sense (opto module OUT, low = on) | 17 |
| LED bank → MOSFET module inputs (stage 10) | 8–14, 21 |
| OLED / AS7341 first I2C pair (SCL, SDA) | 2, 1 |
| Optional AS5600 encoders (SCL, SDA) | (40, 39) (42, 41) (18, 38) |
| UART to the Pi station (TX, RX) | 47, 48 |

| From | To |
|---|---|
| Red / black motor-power leads | MOT+ / MOT− 3-way lever connectors on the tray → 10 cm 18 AWG leads → SKR Pico POWER + / − (screw terminal) |
| Motors M4 M3 M2 | SKR Pico X, Y, Z1 (the 5-pack's 1 m cables; CTL-11 only if they don't latch) |
| M1 pancake (bare leads) | SKR Pico E, through a spare 5-pack cable spliced with 3 × WAGO 221-412 + 1 × 221-415 (coil pair 1 → plug pins 1 + 4, pair 2 → pins 2 + 3; M27.1) |
| Endstop modules M4 M3 M2 M1 | X-STOP, Y-STOP, Z-STOP, E0-STOP (3-pin: signal, GND, 5 V) |
| White COB driver +Vin / −Vin (female jumpers on its pins) | SKR Pico HE `12/24V` / HE `IO23` (cut jumpers under the screws) |
| Opto module input + / − | MOT+ / MOT− lever connectors, slot 2 (short 18 AWG red / black offcuts) |
| Opto module OUT / GND / VCC | ESP32-S3 J1-10 (GPIO 17) / J3-21 (GND) / J1-1 (3V3) (male–female jumpers) |
| Keypad A keys 1–4 | ESP32-S3 J1-4…J1-7 (GPIO 4–7) |
| Keypad B keys 1, 2 | ESP32-S3 J1-8, J1-9 (GPIO 15, 16: NEXT, PAUSE) |
| Both keypad commons | 3-way lever connector → ESP32-S3 J1-22 (GND) |

PAUSE stops the plan after the pose in progress (START carries on). It is a hub button: the e-stop is the immediate stop.

## Flash and test (copy-paste)

**0. Windows + WSL only:** pass USB into Ubuntu. PowerShell as administrator:

```powershell
winget install --interactive --exact dorssel.usbipd-win
usbipd list                              # find the SKR Pico (2e8a) and the ESP32-S3 (303a) bus IDs
usbipd bind --busid 1-4                  # once per device; use your bus ID
usbipd attach --wsl --busid 1-4          # after every replug (and after each UF2 flash: the board re-enumerates)
```

**1. Ubuntu, once:**

```bash
sudo apt install -y python3-venv unzip curl
sudo usermod -aG dialout $USER && newgrp dialout
cd ~/projects/Gonioreflectometer-Open-Source
ls /dev/ttyACM*                          # SKR Pico and ESP32-S3 both appear as ttyACM*
```

**2. SKR Pico motion board (grblHAL)** [R85]:

```bash
bash scripts/controller.sh flash             # prints the steps: Web Builder .uf2, BOOT jumper + RESET, copy to RPI-RP2
bash scripts/controller.sh settings          # sends firmware/grblhal/settings.txt (generated from machine.yaml)
bash scripts/controller.sh pins              # output port numbers for machine.yaml lights
```

**3. Motors** (24 V adapter in, e-stop released):

```bash
bash scripts/controller.sh test              # info, home, M4=60, M4=90 M3=45, motors off ($SLP)
opengonio send '?'                           # status
opengonio send '$HX'                         # home M4 only
opengonio send 'G53 G1 X40 F600'             # raw move: M4 to 60° (grblHAL reads 0 at the switch, 20°)
opengonio send 'M122 I'                      # re-initialise the drivers (after motor power returns)
```

Wrong direction: set that axis bit in `$3` (direction invert mask: X 1, Y 2, Z 4, A 8), e.g. `opengonio send '$3=2'`.
Then add the line to `tools/grblhal_settings.py` so the next `make build` keeps it.

**4. ESP32-S3 button hub** [C13]: plug in its **USB** connector (not UART), then:

```bash
bash scripts/hub.sh flash oct                # MicroPython; "oct" if the module can says N8R8 / N16R8, else "plain"
bash scripts/hub.sh                          # copies main.py, prints PONG
opengonio panel                              # buttons drive the machine
```

## 3D parts

| Part | Source |
|---|---|
| Case + keypad panel (CTL-10) | `tools/cad/parts.py`: SKR Pico standoffs (6 mm, M2 self-tap on 58 × 49 mm, board turned so its USB-C faces the tray edge), ESP32-S3 locating frame with a pedestal under the module can (board **upside down, header pins up**, on double-sided foam tape; USB opening at the +X end), window under the SKR Pico, frames for the opto module (66 × 16.5) and the LED driver (32 × 20.3), 2 keypad recesses (70 × 20) + tail slots, 4 corner bosses (M2 into the NW tile's pilots) |
| SKR Pico | maker [STEP](https://github.com/bigtreetech/SKR-Pico/blob/master/3D/BTT%20SKR%20Pico%20V1.0.step) [C12]: 85 × 56 mm, 4 × Ø2.7 holes on 58 × 49 mm |
| ESP32-S3-DevKitC-1 | repo model at an estimated 69 × 26 mm (clones vary): measure yours and change `ESP` in `tools/cad/parts.py` |

## Results

(fill in)
