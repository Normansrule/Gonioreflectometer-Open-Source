# 15 · Design

| | Laptop mode | Standalone mode |
|---|---|---|
| Runs jobs | `opengonio` on the laptop | `opengonio station` on a Pi Zero 2 W |
| SKR Pico motors | USB-C | USB-C into the Pi's USB hub (STA-04) |
| Camera | laptop USB | Pi USB (same hub) |
| Buttons + OLED | ESP32-S3 hub over USB | ESP32-S3 hub over UART |
| Data | processed live | saved on the Pi SD card → `opengonio pull` → `opengonio verify` |
| No computer at all | — | not supported (the SKR Pico has no WiFi WebUI) |

**Buttons:** NEXT chooses a job · START runs it · STOP aborts · HOME · LIGHT. The OLED shows the job and progress.

**Jobs:** mirror check 30° · swatch grid 10° · 3D scan (after phase 09). Each job writes `img_NNNN.png` + `manifest.json` (pose per image).

### Wiring

Pin by pin: [README → Wiring → 9](../../README.md#9--standalone-station-no-laptop-optional).

| From | To |
|---|---|
| Pi pin 8 (GPIO14 TX) | ESP32-S3 J3-16 (GPIO 48, hub UART RX) |
| Pi pin 10 (GPIO15 RX) | ESP32-S3 J3-17 (GPIO 47, hub UART TX) |
| Pi pin 6 (GND) | ESP32-S3 J3-1 (GND) |
| Pi pin 4 (5V) | ESP32-S3 J1-21 (5V): powers the hub without the laptop (never with its USB in the laptop at the same time) |
| OLED SDA / SCL / VIN / GND | ESP32-S3 J3-4 (GPIO 1) / J3-5 (GPIO 2) / J1-2 (3V3) / J3-22 (GND); with the AS7341 fitted, chain the OLED from the sensor's second STEMMA QT socket |
| Buck input | FUSED and GND lever connectors in the power box (5-way from here on; after the fuse, before the e-stop), so the Pi keeps running on e-stop (18–24 V in) |
| Buck 5.1 V out + / − | Pi pin 2 (5V) / pin 14 (GND), two cut female jumpers |
| Camera(s) + SKR Pico USB-C | powered USB hub on the Pi's micro-USB data port (OTG adapter) |

### Set up the Pi (from the laptop)

1. Raspberry Pi Imager → Raspberry Pi OS Lite (64-bit) → hostname `opengonio`, enable SSH, your WiFi.
2. `bash scripts/station.sh aleks@opengonio.local` — copies the repo, installs, enables UART, starts the service.
3. After a job: `opengonio pull aleks@opengonio.local` then `opengonio verify data/*`.

## 3D parts

| Part | Source |
|---|---|
| Pi Zero mount (STA-07) | `tools/cad/parts.py`: push-fit pegs on the Pi's 58 × 23 mm holes (no screws); OLED window in the keypad panel |
| Pi Zero 2 W | [mechanical drawing](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) [H51] |

## Results

(fill in)
