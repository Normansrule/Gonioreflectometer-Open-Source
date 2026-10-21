# Hardware

Every electrical connection, pin by pin (power box, SKR Pico, ESP32-S3 header, lamp, USB): [README → Wiring]({{REPO}}/README.md#wiring).

| Subsystem | Parts | Stage |
|---|---|---|
| Power | 24 V Li-ion pack with protection board (~6 h per charge), charged over USB-C (PD trigger + CC/CV module), 3.15 A fuse, latching e-stop, lever connectors | [01]({{REPO}}/phases/01-power) |
| Controller | BTT SKR Pico (grblHAL, USB-C) + ESP32-S3 hub, keypads | [02]({{REPO}}/phases/02-controller) |
| Frame | printed 600 × 600 mm deck (9 tiles), printed 20 × 20 bars, M2 screws | [03]({{REPO}}/phases/03-frame) |
| Light arm (M4) | 12 in lazy Susan, GT2 belt rim, 24:1 | [04]({{REPO}}/phases/04-light-arm) |
| Table (M3), tilt (M2), spin (M1) | NEMA 17 steppers, 5:1 belts, M8 bolt axles, direct-drive spin | [05]({{REPO}}/phases/05-table) · [08]({{REPO}}/phases/08-tilt) · [09]({{REPO}}/phases/09-spin) |
| Camera | 12 MP IMX477 USB, 16 mm M12 lens, printed f/8 stop | [06]({{REPO}}/phases/06-camera-light) |
| Light | Citizen CLU7A3 COB, colour rendering index (CRI) 97, in a solderless TE holder, 350 mA driver | [06]({{REPO}}/phases/06-camera-light) |

- **No tools beyond a kit:** lever connectors, screw terminals, modules instead of loose chips, M2 screws self-tapping into printed pilots.
- **One screw size:** M2 everywhere; M3 only into the motors, M8 bolts as axles.
- **Printed parts:** black ABS (acrylonitrile butadiene styrene) on an enclosed printer; ≈ 2.7 kg, half of it the deck.
- **Circuit board (future):** a carrier board that replaces the modules and jumpers: [pcb/]({{REPO}}/pcb/README.md).
- **Optical homing** on every axis; over-travel switches in the e-stop loop.
- **Cost:** see the [bill of materials]({{REPO}}/README.md#electronics) (pictures, buy links, STEP/STL downloads).

Open-hardware practice [@H28; @H31]: [Appendix E](Appendix-E-Hardware.md).
