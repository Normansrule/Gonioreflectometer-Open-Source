# Architecture and interface standards

These interfaces are frozen at milestone M0. Changing one needs a design-change issue, because
modules built in earlier phases depend on them.

## Module split

The brief's twelve modules are kept, with one change: **base and frame** owns every pre-drilled
future interface (ring footprint, turntable post, OG-40 pads), so later modules never drill the base.

| Module | Phase | Mechanical interface | Electrical interface |
|---|---|---|---|
| power | 1 | OG-40 on base | J1 in · J2 24 V MOTION · J3 5 V HOST · J4 PWR-SIG |
| controller | 1 | OG-40 on base | J2/J3/J4 in · stepper, endstop, encoder, light, fan harnesses out |
| base-frame | 1 | defines OG-40 pads, ring and post footprints | — |
| camera-arm (A1) | 1 | OG-40 tower foot at r = 175 mm | M-A1 motor, E-A1 endstop, I-A1 encoder |
| camera-head | 1 | 2 × M3 on 20 mm at the arm end | CSI ribbon |
| light-arm (A2) | 1 | OG-40 bracket at r = 140 mm (+ riser) | M-A2, E-A2, I-A2 |
| light-source | 1 | 2 × M3 on 20 mm at the arm end | L-MAIN |
| enclosure | 2 | dowel sockets on the base edge | — |
| calibration-kit | 2 | sits on the sample stage | — |
| light-ring (A3) | 3 | bolts to the 4 ring-footprint holes; top plate carries the light OG-40 | M-A3, E-A3, I-A3 |
| turntable (A4) | 4 | replaces the post's turntable-height spacer | M-A4, E-A4, I-A4 |
| polarizer-fill-kit | 5 | polarizer slot in the lamp housing; servo on the camera head | SERVO, L-FILL |

## OG-40 bolt pattern

- 4 × M4 on a **40 × 40 mm** square, Ø6.2 mm centre locating hole (printed Ø6 peg on the module side).
- On plywood: M4 tee nuts pressed in from below. On printed parts: M4 heat-set inserts or nyloc nuts.
- Screws M4 × 12 button head, 1.2 N·m in wood, 1.0 N·m into inserts.

## Base plate drill map (all holes drilled in Phase 1)

| Feature | Position (mm, origin at plate centre under the measurement centre) | Holes |
|---|---|---|
| Centre post pad | (0, 0) | OG-40 |
| Light bracket pad | (0, +140) | OG-40 — same radius as on the ring top plate |
| Camera tower pad | (0, −175) | OG-40 |
| Ring footprint | 4 holes on Ø250 at 45°, 135°, 225°, 315° | M5 tee nuts (Phase 3 sub-plate) |
| Power box | front right corner, (+220, −220) | OG-40 |
| Controller case | front left corner, (−200, −220) | OG-40 |
| Feet | 4 × M8 tee nuts, 30 mm from each corner | M8 |
| Cable pass-throughs | Ø20 at (0, −120) and (+100, −200) | — |

## Connector registry

Rules: JST-XH inside a module and from module to controller; XT30 for anything carrying more than 3 A;
power sources carry the **female** XT30; every harness is labelled at both ends with its code.

| Code | Connector | Pin 1 | Pin 2 | Pin 3 | Pin 4 | Pin 5 | Pin 6 |
|---|---|---|---|---|---|---|---|
| J2 | XT30 | + 24 V MOTION | GND | | | | |
| J3 | XT30 | + 5 V HOST | GND | | | | |
| J4 PWR-SIG | JST-XH 4 | MOTION_SENSE | BUCK_PG | +3V3 | GND | | |
| M-Ax motor | JST-XH 4 (SKR side as supplied) | A+ (1A) | A− (1B) | B+ (2A) | B− (2B) | | |
| E-Ax endstop | JST-XH 3 | +5 V | GND | SIGNAL | | | |
| I-Ax encoder | JST-XH 4 | +3V3 | GND | SDA | SCL | | |
| L-MAIN / L-FILL | JST-XH 2 | LED driver +Vin (from SKR VIN) | switched − (HE0 / FAN2) | | | | |
| SERVO | JST-XH 3 | +5 V | GND | PWM | | | |

Motor pin order must match the StepperOnline datasheet colours for the 17HS19-2004S1; check one coil
with a multimeter (≈ 1.6 Ω) before plugging in.

## Raspberry Pi GPIO allocation (BCM)

| Function | Pi 4 | Pi 5 |
|---|---|---|
| UART to SKR (TX via 1 kΩ / RX) | GPIO14 / GPIO15 | GPIO14 / GPIO15 |
| I-A1 encoder | i2c1: GPIO2 / GPIO3 | i2c1: GPIO2 / GPIO3 |
| I-A2 encoder | i2c3: GPIO4 / GPIO5 | i2c2-pi5: GPIO4 / GPIO5 |
| I-A3 encoder (Phase 3) | i2c6: GPIO22 / GPIO23 | i2c3-pi5: GPIO22 / GPIO23 |
| I-A4 encoder (Phase 4) | i2c4: GPIO8 / GPIO9 | i2c0-pi5: GPIO8 / GPIO9 |
| MOTION_SENSE | GPIO17 | GPIO17 |
| BUCK_PG | GPIO27 | GPIO27 |
| Safe-shutdown button | GPIO26 | GPIO26 |
| Polarizer servo (Phase 5) | via SKR servo pin PA1 | via SKR servo pin PA1 |

The AS5600's address is fixed (0x36), so each encoder gets its own hardware I2C bus. Bus numbers in
`machine.yaml` must match `ls /dev/i2c-*` after reboot — **check them on your Pi**.

## Raspberry Pi config.txt

First disable the serial login console (`sudo raspi-config` → Interface Options → Serial Port →
login shell **No**, hardware **Yes**), otherwise a getty fights Klipper on `/dev/ttyAMA0`.

```ini
# --- OpenGantry Lite ---
enable_uart=1
# Pi 4 only: move Bluetooth off the PL011 so /dev/ttyAMA0 is on GPIO14/15
dtoverlay=disable-bt
# Pi 5 only (instead of the two lines above): dtparam=uart0=on

dtparam=i2c_arm=on                     # i2c1 on GPIO2/3 (A1)
# Pi 4 extra buses
dtoverlay=i2c3,pins_4_5                # A2
dtoverlay=i2c6,pins_22_23              # A3
dtoverlay=i2c4,pins_8_9                # A4
# Pi 5 extra buses (use these instead of the Pi 4 block; check the overlay README for exact pin options)
# dtoverlay=i2c2-pi5,pins_4_5
# dtoverlay=i2c3-pi5,pins_22_23
# dtoverlay=i2c0-pi5,pins_8_9

# usb_max_current_enable stays OFF: nothing is powered from the Pi's USB ports
dtoverlay=gpio-shutdown,gpio_pin=26,active_low=1,gpio_pull=up
dtoverlay=disable-wifi                 # optional: wired Ethernet to the PC is faster for RAW copies
```

Overlay names and pin options come from the Raspberry Pi
[overlays README](https://github.com/raspberrypi/linux/blob/rpi-6.12.y/arch/arm/boot/dts/overlays/README);
confirm them against the README for your kernel before relying on them.
