# Klipper firmware

`printer.cfg` drives the four axes as Klipper `manual_stepper`s (not printer kinematics), with one
Klipper unit equal to one output degree. Python talks to it through Moonraker
(`POST /printer/gcode/script`).

## Install on the Pi (once)

1. Flash Raspberry Pi OS Lite (64-bit) to the 128 GB card. Enable SSH.
2. Install Klipper + Moonraker with [KIAUH](https://github.com/dw-0/kiauh) (Klipper, Moonraker; Mainsail is optional but handy for the console).
3. Enable the UART and the extra I2C buses: copy the block from
   [`docs/03-architecture-interfaces.md`](../../docs/03-architecture-interfaces.md#raspberry-pi-configtxt) into `/boot/firmware/config.txt`, reboot, then check `ls /dev/ttyAMA0 /dev/i2c-*`.
4. Copy `printer.cfg` to `~/printer_data/config/printer.cfg`.

## Build and flash the SKR Mini E3 V3.0

```bash
cd ~/klipper && make menuconfig
#   Micro-controller: STMicroelectronics STM32
#   Processor model:  STM32G0B1
#   Bootloader offset: 8KiB bootloader
#   Clock reference:  8 MHz crystal
#   Communication:    Serial (on USART2 PA3/PA2)     <- UART to the Pi (USB also works)
make
```

Copy `out/klipper.bin` to a FAT32 microSD as `firmware.bin`, put it in the SKR, power the SKR from
24 V, wait 10 s, remove the card (the file is renamed `FIRMWARE.CUR` when flashing worked).
These menuconfig choices follow BTT's V3.0 Klipper README; check it if anything differs.

## Wiring the serial link

| Pi 40-pin header | SKR TFT header |
|---|---|
| GPIO14 TXD (pin 8) | RX2 |
| GPIO15 RXD (pin 10) | TX2 |
| GND (pin 6) | GND |
| — | 5V **not connected** |

Leaving 5 V unconnected means the e-stop really removes all power from the SKR and Klipper
reports the lost MCU immediately (a forced re-home after every e-stop, which is what we want).

## First-power checklist

- [ ] Motors unplugged, `printer.cfg` loaded, Klipper shows **Ready**.
- [ ] `QUERY_ENDSTOPS` style check: `QUERY_ENDSTOPS` does not list manual steppers, so trigger each flag by hand and watch `MANUAL_STEPPER ... MOVE=... STOP_ON_ENDSTOP=1` stop.
- [ ] `DUMP_TMC STEPPER="manual_stepper a1_camera_el"` answers (proves UART and 24 V present).
- [ ] Motor connected, `MANUAL_STEPPER STEPPER=a1_camera_el ENABLE=1 SET_POSITION=45` then `MOVE=50 SPEED=2`: arm rises 5 deg (flip `dir_pin` if it goes the other way).
- [ ] `SET_PIN PIN=main_light VALUE=1` lights the lamp; `OG_SLEEP` turns it and the fan off.
