# Flash and test (copy-paste)

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
# press E4 reset; join hotspot FluidNC / 12345678 if your WiFi fails
bash scripts/e4.sh config fluidnc.local      # or the printed IP, or 192.168.0.1
# press E4 reset
```

**3. Motors** (24 V on, e-stop released):

```bash
bash scripts/e4.sh test                      # info, home, M4=60, M4=90 M3=45, motors off
opengonio send '?'                           # status
opengonio send '$H'                          # home all
opengonio send 'G53 G1 X60 F600'             # raw move: M4 (X) to 60°
opengonio send '$MD'                         # motors off
```

Wrong direction: flip `direction_pin` `:low`/`:high` in [`config.yaml`](../../../firmware/fluidnc/config.yaml), re-run `e4.sh config`. Bluetooth: use the BT build from [installer.fluidnc.com](https://installer.fluidnc.com) instead of step 2.

**4. Pico button hub** [R42]: hold BOOTSEL, plug in, drop the [MicroPython .uf2](https://micropython.org/download/RPI_PICO/) onto `RPI-RP2`, then:

```bash
bash scripts/pico.sh                         # copies main.py, prints PONG
opengonio panel                              # buttons drive the machine
```
