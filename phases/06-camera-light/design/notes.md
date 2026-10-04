# Design

**Camera:** Arducam B0433 (IMX477, USB) + 16 mm M12 lens + printed 2.0 mm stop (f/8), on the L-arm at 350 mm, aimed at the zero point. Lock exposure, gain, white balance (`opengonio.camera`). Some UVC modules apply new exposure after a few frames [K6].

**Light:** Cree CXA1304 on a 40 mm heatsink, NLDD-350H at 350 mA, switched by E4 HE0 (`M62/M63 P0`, no PWM). Printed collimation tube + aperture [R1]. COB case ≤ 70 °C.

Optics numbers: [optics.md](optics.md). Fasteners: M2.5 × 8 × 4 (camera, 34 mm pitch [K3]), M5 × 10 + T-nuts × 2, M3 × 8 × 2, M3 inserts × 4.
