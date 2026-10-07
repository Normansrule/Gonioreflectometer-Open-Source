# 15 · Design

| | Laptop mode | Standalone mode |
|---|---|---|
| Runs jobs | `opengonio` on the laptop | `opengonio station` on a Pi Zero 2 W |
| E4 motors | USB, WiFi or Bluetooth | WiFi (`fluidnc.local`) |
| Camera | laptop USB | Pi USB (OTG adapter) |
| Buttons + OLED | Pico over USB | Pico over UART |
| Data | processed live | saved on the Pi SD card → `opengonio pull` → `opengonio verify` |
| No computer at all | — | phone WebUI (`http://fluidnc.local`) jogs and homes; PAUSE on E4 |

**Buttons:** NEXT chooses a job · START runs it · STOP aborts · HOME · LIGHT. The OLED shows the job and progress.

**Jobs:** mirror check 30° · swatch grid 10° · 3D scan (after phase 09). Each job writes `img_NNNN.png` + `manifest.json` (pose per image).

### Wiring

| From | To |
|---|---|
| Pi GPIO14 TX (pin 8) | Pico GP1 RX |
| Pi GPIO15 RX (pin 10) | Pico GP0 TX |
| Pi GND (pin 6) | Pico GND |
| OLED SDA / SCL / VCC / GND | Pico GP16 / GP17 / 3V3 / GND |
| Buck input | the jack's `+` / `−` screws in the power box (a second thin pair under the same screws: the Pi keeps running on e-stop) |
| Buck 5.1 V out | Pi 5V (pin 2) + GND (pin 6), two cut female jumpers |
| Pi 5V (pin 4) | Pico VSYS (pin 39): powers the Pico without the laptop |
| Camera USB | Pi micro-USB data port via OTG adapter |

### Set up the Pi (from the laptop)

1. Raspberry Pi Imager → Raspberry Pi OS Lite (64-bit) → hostname `opengonio`, enable SSH, your WiFi (same as the E4).
2. `bash scripts/station.sh aleks@opengonio.local` — copies the repo, installs, enables UART, starts the service.
3. After a job: `opengonio pull aleks@opengonio.local` then `opengonio verify data/*`.

## 3D parts

| Part | Source |
|---|---|
| Pi Zero mount (STA-07) | `tools/cad/parts.py`: push-fit pegs on the Pi's 58 × 23 mm holes (no screws); OLED window in the keypad panel |
| Pi Zero 2 W | [mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) [H51] |

## Results

(fill in)
