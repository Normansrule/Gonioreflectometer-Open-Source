# Safety (whole machine)

Module-specific notes live in section 8 of each module README. These apply everywhere.

- **Electrical.** Mains only inside the certified adapter. 24 V / 5 A can melt wire and start fires:
  fuse fitted, 18 AWG for power, heat-shrink every joint, strain relief at every exit.
- **Mechanical.** Arms carry counterweights and can pinch. Keep hands out of the arm envelope while
  motors are enabled; the e-stop is a convenience stop, not a certified safety circuit.
- **Optical.** The COB is bright at close range. Do not stare into the lamp; the light is off whenever
  the machine sleeps or the e-stop is pressed. Use the polarizer film and diffuser as supplied.
- **Thermal.** PETG softens near 80 °C. Keep the LED case below 70 °C (heatsink) and run acceptance
  thermal tests before closing enclosures. Do not drape the blackout cloth over the power box or controller vents.
- **Unattended operation** only after the phase's integration test passes, and never with the enclosure
  cloth touching the lamp.
- **Software.** The collision model is the only thing stopping arms from hitting each other in Phase 3+.
  Never bypass `Gantry.validate()`; run new scan plans in `--dry-run` first.
