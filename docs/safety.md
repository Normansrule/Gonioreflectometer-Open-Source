# Safety

- **Mains** stays inside the certified adapter. Never use an open-frame supply.
- **24 V** can't shock you but can start fires: fuse fitted, 18 AWG, heat-shrink, strain relief.
- **Plug in with the rocker off**, then switch on.
- **Q1 tab is live** (+24 V).
- **E-stop** is single-channel convenience stopping, not a certified safety circuit. Keep hands out of the light-arm sweep.
- **Light**: don't stare into the COB or the 400–420 nm LEDs; lights turn off on sleep, STOP and e-stop.
- **Heat**: COB case ≤ 70 °C; PETG softens near 80 °C.
- **Software**: never bypass `Gantry.validate()`; dry-run new plans (`opengonio --dry-run`).
- Unattended runs only after the phase's integration test passes.
