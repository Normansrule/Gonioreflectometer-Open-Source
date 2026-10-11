# Hardware

| Subsystem | Parts | Stage |
|---|---|---|
| Power | 24 V 60 W adapter, fuse, latching e-stop, lever connectors | [01]({{REPO}}/phases/01-power) |
| Controller | FYSETC E4 (FluidNC) + Raspberry Pi Pico H, keypads | [02]({{REPO}}/phases/02-controller) |
| Frame | 610 × 610 mm plywood, 2020 extrusion, printed mounts | [03]({{REPO}}/phases/03-frame) |
| Light arm (M4) | 12 in lazy Susan, GT2 belt rim, 24:1 | [04]({{REPO}}/phases/04-light-arm) |
| Table (M3), tilt (M2), spin (M1) | NEMA 17 steppers, 5:1 belts, M8 bolt axles, direct-drive spin | [05]({{REPO}}/phases/05-table) · [08]({{REPO}}/phases/08-tilt) · [09]({{REPO}}/phases/09-spin) |
| Camera | 12 MP IMX477 USB, 16 mm M12 lens, printed f/8 stop | [06]({{REPO}}/phases/06-camera-light) |
| Light | Citizen CLU7A3 COB, colour rendering index (CRI) 97, in a solderless TE holder, 350 mA driver | [06]({{REPO}}/phases/06-camera-light) |

- **No tools beyond a kit:** lever connectors, screw terminals, breadboard, self-tapping screws into printed parts, wood screws without pilot holes.
- **Printed parts:** black ABS (acrylonitrile butadiene styrene) on an enclosed printer; ≈ 1 kg.
- **Optical homing** on every axis; over-travel switches in the e-stop loop.
- **Cost:** see the [bill of materials]({{REPO}}/README.md#bill-of-materials) (pictures, buy links, STEP/STL downloads).

Open-hardware practice [@H28; @H31]: [Appendix E](Appendix-E-Hardware.md).
