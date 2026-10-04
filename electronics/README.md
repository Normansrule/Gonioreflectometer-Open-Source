# Electronics

| Rail / signal | Source | Consumers | Protection |
|---|---|---|---|
| 24 V BUS | GST60A24 → 3.15 A T fuse → rocker → IRF4905 | e-stop | TVS P6KE30A, 100 µF |
| 24 V MOTION (J2) | BUS through latching e-stop + over-travel switches (J3) | E4 → 4 steppers, light MOSFETs | e-stop |
| MOTION_SENSE (J4) | PC817 optocoupler, 10k LED resistor | Pico GP7 (pull-up, active low) | galvanic isolation |
| 5 V / 3.3 V | laptop USB | Pico, camera, E4 logic (when on USB) | laptop port |

Netlist: [`hardware/power/README.md`](../hardware/power/README.md) §5. Pin maps: [`docs/architecture.md`](../docs/architecture.md#pin-maps).
