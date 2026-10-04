# Flash firmware

**E4 (FluidNC)** [R81]
1. Chrome/Edge → https://installer.fluidnc.com → Install → **WiFi** or **BT** build (not both [R24]).
2. Upload [`firmware/fluidnc/config.yaml`](../../../firmware/fluidnc/config.yaml).
3. WiFi: join `FluidNC` hotspot, set network, then `http://fluidnc.local`. BT: pair; Windows gives a COM port, Linux `rfcomm` [R45][R46].
4. Set `controller` in [`software/config/machine.yaml`](../../../software/config/machine.yaml).

Check: `?` → `<Idle|MPos:…>`; blocking a flag shows `Pn:`. Inverted? flip `:low`/`:high`.

**Pico (hub)** [R42]
1. Hold BOOTSEL, plug in, copy MicroPython `.uf2` to `RPI-RP2`.
2. `pip install mpremote && mpremote cp firmware/pico-hub/main.py :main.py`
3. Check: `PING` → `PONG…`; a button → `BTN HOME`.

**Laptop:** `opengonio home` · `opengonio move M4=60 M3=30` · `opengonio panel` (buttons).
