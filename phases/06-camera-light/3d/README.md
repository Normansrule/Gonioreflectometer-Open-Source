# 06 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| CAM-03a | f/8 aperture stop | [CAM-03a_aperture_stop_f8.step](CAM-03a_aperture_stop_f8.step) | [CAM-03a_aperture_stop_f8.stl](CAM-03a_aperture_stop_f8.stl) |
| CAM-03b | Camera plate + post clamp | [CAM-03b_camera_plate.step](CAM-03b_camera_plate.step) | [CAM-03b_camera_plate.stl](CAM-03b_camera_plate.stl) |
| LSR-05a | Lamp tube, aperture, polarizer slot | [LSR-05a_lamp_tube.step](LSR-05a_lamp_tube.step) | [LSR-05a_lamp_tube.stl](LSR-05a_lamp_tube.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| CAM-01 | USB camera 12 MP IMX477, M12 mount (UVC) | [link](https://www.uctronics.com/download/Amazon/B0433_Arducam_12MP_USB_Camera_Module_Datasheet.pdf) Drawing only:  (38 x 38 mm, holes 34/28 mm) |
| CAM-02 | M12 lens 16 mm F2.0, 1/2 in | Not confirmed - M12 x 0.5 barrel |
| LSR-01 | COB LED CRI 93, 9 V, 400 mA | Not confirmed |
| LSR-02 | Constant-current driver 350 mA | Mean Well 3D OUTLINE on the spec page (not downloaded) |
| LSR-03 | Heatsink 40 x 40 mm (from a pack) | Block model |
| LSR-04 | Thermal adhesive pad | n/a |

Design notes: [../design.md](../design.md).
