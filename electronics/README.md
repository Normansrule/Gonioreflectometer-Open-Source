# Electronics

| Rail / signal | Source | Consumers | Protection |
|---|---|---|---|
| 24 V BUS | GST120A24 via fuse, rocker, reverse-polarity FET | buck, e-stop | 6.3 A T fuse, P6KE30A, 100 µF |
| 24 V MOTION (J2) | BUS through the latching e-stop | SKR VIN → 4 steppers, HE0 main light, FAN1 controller fan, FAN2 fill light | e-stop, SKR 20 A board fuse |
| 5 V HOST (J3) | Pololu D42V55F5 | Pi via USB-C pigtail, servo (Phase 5) | buck current limit, Pi input protection |
| MOTION_SENSE / BUCK_PG (J4) | power module | Pi GPIO17 / GPIO27 | 1 k series, 3.3 V-safe divider |

Detailed netlist: [`hardware/power/README.md`](../hardware/power/README.md) §5.
Connector registry and Pi pin map: [`docs/03-architecture-interfaces.md`](../docs/03-architecture-interfaces.md).

## Harness list (Phase 1)

| Harness | From | To | Connector | Wire |
|---|---|---|---|---|
| H-J2 | power J2 | SKR VIN | XT30 m/m | 18 AWG |
| H-J3 | power J3 | controller box → USB-C pigtail | XT30 m/m | 18 AWG |
| H-J4 | power J4 | Pi header | JST-XH 4 → Dupont | 24 AWG |
| H-UART | Pi GPIO14/15/GND | SKR TFT header | Dupont → JST | 24 AWG |
| M-A1, M-A2 | motors | SKR X, Y | JST-XH 4 | supplied cable |
| E-A1, E-A2 | TCST2103 | SKR X-STOP, Y-STOP | JST-XH 3 | 24 AWG |
| I-A1, I-A2 | AS5600 | Pi i2c1 / i2c3 (Pi 4) or i2c2 (Pi 5) | JST-XH 4 | 24 AWG twisted SDA/GND, SCL/GND |
| L-MAIN | NLDD-350H | SKR HE0 | JST-XH 2 | 22 AWG |
| CSI | camera head | Pi camera port | 500 mm FFC | — |

A dedicated carrier PCB (KiCad) replacing the perfboard is a candidate for the M7 stretch track.
