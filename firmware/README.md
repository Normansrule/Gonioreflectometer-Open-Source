# Firmware

| Board | Firmware | Link to laptop |
|---|---|---|
| FYSETC E4 (motion) | FluidNC + [`fluidnc/config.yaml`](fluidnc/config.yaml) | USB serial, WiFi (telnet :23, WebUI) or Bluetooth serial |
| Raspberry Pi Pico (panel + sensors) | MicroPython + [`pico-hub/main.py`](pico-hub/main.py) | USB serial |

## E4: flash FluidNC (once)

1. Chrome/Edge → https://installer.fluidnc.com → connect the E4 by USB → **Install** → pick the **WiFi** build (or **BT** build; the ESP32 cannot run both at once [R24]). [R81]
2. Upload `fluidnc/config.yaml` from the installer's file page (or the WebUI → Files).
3. WiFi: join the `FluidNC` hotspot, open the WebUI, set your network. Then `http://fluidnc.local`. [R81]
   - Bluetooth build: pair "FluidNC"; Windows makes a COM port, Linux uses `rfcomm` [R45][R46].
4. Set `controller.transport/port/host` in `software/config/machine.yaml`.

Check: send `?` → `<Idle|MPos:...>`. Block each home flag by hand → `Pn:X` / `Pn:Y` appears. If inverted, flip `:low`↔`:high` on that `limit_neg_pin`.

## Pico: flash the hub (once)

1. Hold **BOOTSEL**, plug in, copy the Raspberry Pi Pico MicroPython `.uf2` (micropython.org/download → Raspberry Pi Pico) to `RPI-RP2`. [R42]
2. Copy `pico-hub/main.py` to the Pico (Thonny, or `pip install mpremote && mpremote cp firmware/pico-hub/main.py :main.py`).
3. Check: open the port at 115200, send `PING` → `PONG OpenGonio-hub 1`; press a button → `BTN HOME`.

## Control paths

```
laptop ──USB / WiFi / BT──► E4 (FluidNC) ──► M1-M4, lights (M62/M63)
laptop ──USB──► Pico hub ◄── HOME START STOP LIGHT NEXT, e-stop sense, (Ph 5) LED bank
PAUSE button ──► E4 feed-hold pin (works with no laptop)        E-STOP ──► cuts 24 V
phone/laptop browser ──WiFi──► FluidNC WebUI (jog, home)
```
