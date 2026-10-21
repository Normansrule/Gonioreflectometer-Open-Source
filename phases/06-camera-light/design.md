# 06 · Design

**Camera:** Arducam B0433 (IMX477, USB) + 16 mm M12 lens + printed 2.0 mm stop (f/8), on the L-arm at 350 mm, aimed at the zero point. Lock exposure, gain, white balance (`opengonio.camera`). Some UVC modules apply new exposure after a few frames [K6].

**Light:** Citizen CLU7A3-0403E1 (CRI 97, 3000 K, 12.2 V, 4.2 mm light-emitting surface) [L22] in a TE LUMAWISE Z35 solderless holder [L23] on a 40 mm heatsink, NLDD-350H at 350 mA (≈ 4 W), switched by the SKR Pico HE output (`M62/M63 P4`, no PWM). Printed collimation tube + aperture [R1]. COB case ≤ 70 °C (datasheet limit 120 °C). The lamp body's round seat centres the holder; the back cap clamps heatsink + holder (0.3 mm preload), so nothing is screwed into the heatsink. The Cree CXA1304 of the first draft was dropped: every CXA13 holder is obsolete [L21]. Eye safety [N47].

Optics numbers: [optics.md](optics.md). Fasteners (FRM-06): M2 × 8 × 4 (camera, 34 mm pitch [K3]), M2 × 16 × 2 (camera clamp, lamp clamp), M2 × 12 × 4 (lamp cap); all self-tap into 1.7 mm pilots.

## 3D parts

| Part | Source |
|---|---|
| Camera L-arm, f/8 stop, lens lock (CAM-03) | Onshape `CAM` |
| Lamp housing, tube, aperture, polarizer slot (LSR-05) | Onshape `LSR` |
| Arducam B0433 | drawing only: 38 × 38 mm, holes 34/28 mm ([datasheet](https://www.uctronics.com/download/Amazon/B0433_Arducam_12MP_USB_Camera_Module_Datasheet.pdf)) [K3] |

## Results

(fill in)
