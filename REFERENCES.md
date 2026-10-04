# References and credits

Every source consulted for this repository, including ones that only informed a decision.
IDs are cited in docs, code comments and the BOM `Refs` column. Accessed 2026-10-03/04 unless noted.
Figures in this repo are original drawings; no figure is copied from any source.

## Primary design references

| ID | Source | Used for |
|---|---|---|
| **R1** | M. Ansari-Asl, M. Barbieri, G. Obein, J. Y. Hardeberg, "Optical and Electromechanical Design and Implementation of an Advanced Multispectral Device to Capture Material Appearance," *J. Imaging* 10(3):55, 2024. doi:[10.3390/jimaging10030055](https://doi.org/10.3390/jimaging10030055) · [article](https://www.mdpi.com/2313-433X/10/3/55) | Main reference: fixed camera, 3-rotation sample stage + light arm, zero point, optical homing barriers, roller-lever safety switches, minimum light/camera angle, Tait-Bryan transforms, per-pixel directions, thin-lens/DOF design, deviation test, SVBRDF/BTF definitions |
| **R2** | P. Hanrahan, *Reflection Models I: Ideal Materials*, CS348b Lecture 10, Stanford University, Spring 2016 (slides provided by the user) | BRDF definition, reflection equation, linearity, reciprocity, isotropy, energy conservation, law of reflection, mirror BRDF, Snell's law, refraction vector, TIR, Fresnel/Schlick, Cook-Torrance colour, Lambert |
| **R3** | Stanford Spherical Gantry — [graphics.stanford.edu/projects/gantry](https://graphics.stanford.edu/projects/gantry/) | Original brief's architecture (v0.1) |
| **R4** | Stanford Spherical Gantry specifications — [link](https://graphics.stanford.edu/projects/gantry/design/specifications.html) | v0.1 sizing |

## Theory and algorithms

| ID | Source | Used for |
|---|---|---|
| **R5** | P. Debevec, J. Malik, "Recovering High Dynamic Range Radiance Maps from Photographs," SIGGRAPH 1997 — [PDF](https://pauldebevec.com/Research/HDR/debevec-siggraph97.pdf), [ACM](https://dl.acm.org/doi/10.1145/258734.258884) | Camera response + HDR for 8-bit UVC frames |
| **R6** | B. Walter, S. Marschner, H. Li, K. Torrance, "Microfacet Models for Refraction through Rough Surfaces," EGSR 2007 (bibliographic; not fetched) | GGX distribution |
| **R7** | C. Schlick, "An Inexpensive BRDF Model for Physically-based Rendering," Computer Graphics Forum 13(3), 1994 (bibliographic; cited via [R2]) | Schlick Fresnel |
| **R8** | R. Cook, K. Torrance, "A Reflectance Model for Computer Graphics," ACM TOG 1(1), 1982 (bibliographic; cited via [R2]) | Cook-Torrance colour shift |
| **R9** | C. Ericson, *Real-Time Collision Detection*, Morgan Kaufmann, 2005, §5.1.9 (bibliographic) | Segment-segment distance in the collision model |

## Other measurement rigs (context, stretch track)

| ID | Source | Used for |
|---|---|---|
| **R10** | Cornell gonioreflectometer — [link](http://w1.graphics.cornell.edu/research/measure/gonio.html) | Comparison |
| **R11** | S. Westin et al., Cornell three-axis gonioreflectometer, SPIE 5878-29 — [PDF](https://www.graphics.cornell.edu/~westin/SPIE_5878-29_Gonio.pdf) | Comparison |
| **R12** | Cornell measurement data — [link](https://www.graphics.cornell.edu/online/measurements/) | Validation data |
| **R13** | MERL BRDF database — [merl.com/brdf](https://www.merl.com/brdf/) | Validation data |
| **R14** | W. Matusik et al., MERL TR2003-83 — [PDF](https://www.merl.com/publications/docs/TR2003-83.pdf) | Comparison |
| **R15** | J. Dupuy, W. Jakob, "An Adaptive Parameterization for Efficient Material Acquisition and Rendering," 2018 — [link](https://rgl.epfl.ch/publications/Dupuy2018Adaptive) | Stretch: adaptive sampling |
| **R16** | RGL-EPFL material database — [link](https://rgl.epfl.ch/pages/lab/material-database) | Validation data |
| **R17** | J. Filip et al., specular BRDF with a goniometer, 2017 — [PDF](https://staff.utia.cas.cz/filip/papers/filip17brdf.pdf) | Comparison |
| **R18** | UTIA BTF database — [link](https://btf.utia.cas.cz/?faq=) | BTF context |
| **R19** | X-Rite TAC7 — [product](https://www.xrite.com/categories/appearance/tac7) | Stretch: multi-light capture |
| **R37** | F. Schröder, master's thesis, 2019 — [link](https://f-schroeder.github.io/publication/masterthesis/) | DIY prior art |
| **R38** | GatherLab/Goniometer — [GitHub](https://github.com/GatherLab/Goniometer) | Consulted; emission goniometer, not used |
| **R39** | X-Rite TAC7 user guide — [PDF](https://www.xrite.com/-/media/xrite/files/manuals_and_userguides/t/tac7_user_guide_en.pdf) | Context |
| **R40** | X-Rite PANTORA — [link](https://www.xrite.com/pantora-software) | Context |

## 3D photo scanner (Phase 6)

| ID | Source | Used for |
|---|---|---|
| **S1** | COLMAP output format — [format.html](https://colmap.github.io/format.html) ([source](https://colmap.github.io/_sources/format.rst.txt)); camera models — [cameras](https://colmap.github.io/_sources/cameras.rst.txt); PINHOLE params comment in [models.h](https://github.com/colmap/colmap/blob/ff8842e7d9e985bd0dd87169f61d5aaeb309ab32/src/colmap/sensor/models.h#L197) (found via [blog](https://www.cnblogs.com/xiaohuidi/p/15767477.html), not opened) | cameras.txt / images.txt / points3D.txt, Hamilton quaternion, world-to-camera pose |
| **S2** | COLMAP FAQ, "Reconstruct sparse/dense model from known camera poses" — [faq.html](https://colmap.github.io/faq.html); CLI — [cli.html](https://colmap.github.io/cli.html) | `run_colmap.sh` command sequence, meshing |
| **S3** | J. L. Schönberger, J.-M. Frahm, "Structure-from-Motion Revisited," CVPR 2016 — [CVF](https://openaccess.thecvf.com/content_cvpr_2016/html/Schonberger_Structure-From-Motion_Revisited_CVPR_2016_paper.html), [PDF](https://openaccess.thecvf.com/content_cvpr_2016/papers/Schonberger_Structure-From-Motion_Revisited_CVPR_2016_paper.pdf); J. L. Schönberger, E. Zheng, M. Pollefeys, J.-M. Frahm, "Pixelwise View Selection for Unstructured Multi-View Stereo," ECCV 2016 — [doi:10.1007/978-3-319-46487-9_31](https://link.springer.com/chapter/10.1007/978-3-319-46487-9_31), [mlanthology](https://mlanthology.org/eccv/2016/schonberger2016eccv-pixelwise/); COLMAP licence (BSD) — [license](https://colmap.github.io/license.html) | Photogrammetry engine |
| **S4** | R. J. Woodham, "Photometric method for determining surface orientation from multiple images," *Optical Engineering* 19(1), 1980 — [doi:10.1117/12.7972479](https://www.spiedigitallibrary.org/journals/optical-engineering/volume-19/issue-1/191139/Photometric-Method-For-Determining-Surface-Orientation-From-Multiple-Images/10.1117/12.7972479.short) | Photometric stereo |
| **S5** | A. Laurentini, "The Visual Hull Concept for Silhouette-Based Image Understanding," *IEEE TPAMI* 16(2), 1994 — [doi:10.1109/34.273735](https://dl.acm.org/doi/10.1109/34.273735) | Visual hull |
| **S6** | R. Szeliski, "Rapid Octree Construction from Image Sequences," *CVGIP: Image Understanding* 58(1), 1993 — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1049966083710296) | Voxel carving |
| **S7** | K. N. Kutulakos, S. M. Seitz, "A Theory of Shape by Space Carving," *IJCV*, 2000 — [doi:10.1023/A:1008191222954](https://link.springer.com/article/10.1023/A:1008191222954), [PDF (Toronto)](https://www.cs.toronto.edu/~kyros/pubs/00.ijcv.carve.pdf), [PDF (CMU)](https://www.cs.cmu.edu/~seitz/papers/kutu-ijcv00.pdf) | Space carving |
| **S8** | MVTec HALCON `photometric_stereo` reference — [link](https://www.mvtec.com/doc/halcon/13/en/photometric_stereo.html) | ≥ 3 images, non-coplanar light directions |
| **S9** | A. W. Fitzgibbon, G. Cross, A. Zisserman, "Automatic 3D Model Construction for Turn-Table Sequences," SMILE 1998 — [doi:10.1007/3-540-49437-5_11](https://link.springer.com/chapter/10.1007/3-540-49437-5_11), [open copy](https://ora.ox.ac.uk/objects/uuid:f4e19b7a-4606-4f63-b532-6a0d0bf19845) | Turntable (rotating-object) reconstruction |
| **S10** | Meshroom / AliceVision — [alicevision.org](https://alicevision.org/), [Meshroom](https://alicevision.org/view/meshroom.html), [GitHub](https://github.com/alicevision/meshroom), [licence MPL2](https://github.com/alicevision/meshroom/blob/develop/COPYING.md) | Alternative reconstruction |
| **S11** | OpenCV `solvePnP` — [docs](https://docs.opencv.org/4.13.0/d5/d1f/calib3d_solvePnP.html) | Camera axis convention, pose checks |
| **S12** | OpenCV ChArUco calibration — [tutorial](https://docs.opencv.org/4.13.0/da/d13/tutorial_aruco_calibration.html), [detection](https://docs.opencv.org/4.13.0/df/d4a/tutorial_charuco_detection.html) | Scan-mode intrinsics, scanning mat |
| **S13** | D. Schnieders, K.-Y. K. Wong, "Camera and light calibration from reflections on a sphere," *CVIU*, 2013 — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1077314213001082), [PDF](https://i.cs.hku.hk/~kykwong/publications/dschnieders_cviu2013.pdf) | Chrome-ball light calibration |
| **S14** | Yu, Chen, Da, "Geometric calibration for photometric stereo under near-field point light sources using spheres," *Optics & Laser Technology* 180, 2025 — [link](https://www.sciencedirect.com/science/article/pii/S0030399224010156) | Near-light correction (M6.7) |
| **S15** | D. B. Goldman, B. Curless, A. Hertzmann, S. M. Seitz, "Shape and Spatially-Varying BRDFs from Photometric Stereo," ICCV 2005 — [doi:10.1109/ICCV.2005.219](https://mlanthology.org/iccv/2005/goldman2005iccv-shape/) | On-object SVBRDF + normals (Phase 7) |
| **S16** | Blender manual: [PLY](https://docs.blender.org/manual/en/latest/files/import_export/ply.html), [OBJ](https://docs.blender.org/manual/en/latest/files/import_export/obj.html), [glTF 2.0](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html), [formats](https://docs.blender.org/manual/en/latest/files/import_export/index.html) | Mesh import check |
| **S17** | OpenMVS — [GitHub](https://github.com/cdcseacave/openMVS), [licence AGPL](https://github.com/cdcseacave/openMVS/blob/develop/COPYRIGHT.md) | Optional dense/mesh stage |
| **S18** | RealityScan (formerly RealityCapture) — [licence](https://www.realityscan.com/license), [2.0 rename](https://www.realityscan.com/news/realityscan-20-new-release-brings-powerful-new-features-to-a-rebranded-realitycapture), [CG Channel 2.0](https://www.cgchannel.com/2025/06/epic-games-to-rebrand-realitycapture-as-realityscan-2-0/), [CG Channel 2.2](https://www.cgchannel.com/2026/06/epic-games-releases-realityscan-2-2-with-amd-gpu-support/) | Optional reconstruction (free under $1M revenue, students) |
| **S19** | QuakeHold! museum putty — [SOS Products](https://www.sosproducts.com/quakehold-museum-putty-p/64810.htm), [Fire Supply Depot](https://www.firesupplydepot.com/quakehold-museum-putty-white-22111.html) | Heavier-object option |
| **S20** | Loctite Fun-Tak 2 oz — [Staples](https://www.staples.com/Loctite-Fun-Tak-2-oz-Mounting-Adhesive-Putty-1270884/product_1480018), [Amazon](https://www.amazon.com/Loctite-Fun-Tak-Mounting-2-Ounce-1270884-12/dp/B074R72PSH) | $3.49 object mount |

Note: [R1] (Ansari-Asl et al. 2024) covers flat samples only; the scanner phase extends beyond that paper.

## Firmware, protocols, software

| ID | Source | Used for |
|---|---|---|
| **R20** | FluidNC wiki, Axes — [link](http://wiki.fluidnc.com/en/config/axes) | Axis/homing keys, degrees as units, shared limits |
| **R21** | FluidNC wiki, Trinamic drivers — [link](http://wiki.fluidnc.com/en/config/trinamic_drivers) | tmc_2209 keys |
| **R22** | FluidNC UART sections — [md](https://raw.githubusercontent.com/bdring/fluidnc-wiki-content/main/config/uart_sections.md) | uart1 block |
| **R23** | FluidNC example TMC2209 config — [yaml](https://github.com/bdring/fluidnc-config-files/blob/main/official/TMC2209_corexy.yaml) | Config template |
| **R24** | FluidNC WiFi/Bluetooth — [md](https://raw.githubusercontent.com/bdring/fluidnc-wiki-content/main/features/wifi_bt.md) | WiFi modes, telnet :23, BT build |
| **R25** | FluidNC Web API — [md](https://raw.githubusercontent.com/bdring/fluidnc-wiki-content/main/features/WebAPI.md) | Websocket port |
| **R26** | FluidNC user outputs — [md](https://raw.githubusercontent.com/bdring/fluidnc-wiki-content/main/config/user_outputs.md) | M62/M63 light control |
| **R27** | FluidNC control pins — [link](http://wiki.fluidnc.com/en/config/control) | Feed-hold (PAUSE) pin |
| **R28** | FluidNC commands and settings — [md](https://raw.githubusercontent.com/bdring/fluidnc-wiki-content/main/features/commands_and_settings.md) | $H, $HX, $MD, $ME |
| **R29** | FluidNC serial protocol — [md](https://raw.githubusercontent.com/bdring/fluidnc-wiki-content/main/support/serial_protocol.md) | Status report format |
| **R30** | FluidNC serial port usage (old wiki) — [link](https://github.com/bdring/FluidNC/wiki/Serial-Port-Usage/29e7ed734b79534bf9c8e59aa6ca9fba6ba8c96f) | 115200 8N1 |
| **R31** | FluidNC hardware list — [link](https://github.com/bdring/FluidNC/wiki/Hardware-that-Runs-FluidNC/a1d2287bd26a527c9c327af35360ff75a36d6f93) | E4 supported |
| **R32** | fluidnc-config-files — [GitHub](https://github.com/bdring/fluidnc-config-files) | Searched for an E4 config |
| **R33** | V1E forum, FluidNC config for FYSETC E4 — [thread](https://forum.v1e.com/t/fluidnc-primo-config-for-fysetc-e4-board/34096) | E4 TMC addresses |
| **R34** | FluidNC issue #1311 (E4 config) — [link](https://github.com/bdring/FluidNC/issues/1311) | E4 notes |
| **R35** | OnStepX E4 pin map — [link](https://github.com/hjd1964/OnStepX/blob/main/src/pinmaps/Pins.FYSETC_E4.h) | E0 UART address |
| **R36** | Arduino-ESP32 Bluetooth docs — [link](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/bluetooth.html) | BT serial is classic-ESP32 only |
| **R42** | MicroPython rp2 quick reference — [link](https://docs.micropython.org/en/latest/rp2/quickref.html) | SoftI2C, pins (download page micropython.org/download, not fetched) |
| **R43** | MicroPython machine.PWM — [link](https://docs.micropython.org/en/latest/library/machine.PWM.html) | Servo PWM (Phase 5 option) |
| **R44** | pyserial — [API](https://pyserial.readthedocs.io/en/latest/pyserial_api.html), [intro](https://pyserial.readthedocs.io/en/latest/shortintro.html) | Serial transport |
| **R45** | Bluetooth COM ports on Windows — [Microsoft Q&A](https://learn.microsoft.com/en-gb/answers/questions/1166304/standard-serial-over-bluetooth-link-select-com-por), [In The Hand](https://inthehand.com/2020/11/22/bluetooth-virtual-com-ports/) | BT link |
| **R46** | rfcomm(1) — [man page](https://manpages.debian.org/testing/bluez/rfcomm.1.en.html) | BT link on Linux |
| **R47** | OpenCV video I/O flags — [link](https://docs.opencv.org/4.x/d4/d15/group__videoio__flags__base.html) | Camera properties |
| **R48** | OpenCV issue #17019 — [link](https://github.com/opencv/opencv/issues/17019) | Backend-dependent properties |
| **R49** | OpenCV HDR tutorial — [link](https://docs.opencv.org/4.13.0/d2/df0/tutorial_py_hdr.html), [photo.hpp](https://docs.opencv.org/4.13.0/dc/d81/photo_8hpp.html) | CalibrateDebevec / MergeDebevec |
| **R50** | v4l2-ctl(1) — [man page](https://www.mankier.com/1/v4l2-ctl) | Manual camera controls |
| **R51** | Linux V4L2 camera controls — [link](https://dri.freedesktop.org/docs/drm/media/uapi/v4l/ext-ctrls-camera.html) | Exposure units |
| **R52** | Arducam, minimum exposure time — [link](https://docs.arducam.com/UVC-Camera/Adjust-the-minimum-exposure-time/) | Exposure units |
| **R53** | DirectShow exposure table — [link](https://www.principiaprogramatica.com/2017/06/11/setting-manual-exposure-in-opencv/) | Windows exposure values |
| **R54** | SpellSight PR (V4L2 control names) — [link](https://github.com/mtaylor45/-SpellSight/pull/14) | Control names by kernel |
| **R70** | GitHub CLI Linux install — [link](https://github.com/cli/cli/blob/trunk/docs/install_linux.md) | PUBLISH.md commands |
| **R73** | KaTeX — [katex.org](https://katex.org/) (loaded from cdn.jsdelivr.net) | Equations on the Pages site |
| **R81** | FluidNC web installer — [installer.fluidnc.com](https://installer.fluidnc.com/); install walkthrough — [Hackaday.io log](https://hackaday.io/project/194302-convert-a-mach3-cnc-controller-to-grbl-or-fluidnc/log/226954-installing-fluidnc) | Flashing steps |

## Considered and replaced (v0.1 Raspberry Pi / Klipper design, alternatives)

| ID | Source | Used for |
|---|---|---|
| **R55** | grblHAL RP2040 — [SKR Pico map](https://github.com/grblHAL/RP2040/blob/master/boards/btt_skr_pico_10_map.h), [README](https://github.com/grblHAL/RP2040/blob/master/README.md) | Alternative firmware |
| **R56** | BTT SKR Pico — [BIQU](https://biqu.equipment/products/btt-skr-pico-v1-0) ($39.85) | Alternative board |
| **R57** | Klipper Config Reference — [link](https://www.klipper3d.org/Config_Reference.html) | v0.1 firmware |
| **R58** | Moonraker printer API — [link](https://moonraker.readthedocs.io/en/latest/external_api/printer/) | v0.1 host API |
| **R59** | KIAUH — [GitHub](https://github.com/dw-0/kiauh) | v0.1 install |
| **R60** | Raspberry Pi overlays README — [link](https://github.com/raspberrypi/linux/blob/rpi-6.12.y/arch/arm/boot/dts/overlays/README) | v0.1 I2C buses |
| **R61** | Raspberry Pi camera software — [link](https://www.raspberrypi.com/documentation/computers/camera_software.html) | v0.1 camera |
| **R62** | Hackster, Raspberry Pi price rises — [link](https://www.hackster.io/news/raspberry-pi-hikes-prices-by-up-to-150-as-the-ai-bubble-hits-hard-confirms-raspberry-pi-6-plans-711d4384a4dd) | Decision to avoid buying compute |
| **R63** | PiShop Raspberry Pi 5 prices — [link](https://www.pishop.us/product-category/raspberry-pi/raspberry-pi-5/raspberry-pi-5-boards/) | Decision to avoid buying compute |
| **R64** | BTT SKR Mini E3 V3 — [BIQU](https://biqu.equipment/products/bigtreetech-skr-mini-e3-v2-0-32-bit-control-board-for-ender-3), [GitHub](https://github.com/bigtreetech/BIGTREETECH-SKR-mini-E3/tree/master/hardware/BTT%20SKR%20MINI%20E3%20V3.0) | v0.1 controller |
| **R65** | MKS DLC32 — [eBay](https://www.ebay.com/itm/237008535637), [FluidNC #751](https://github.com/bdring/FluidNC/issues/751), [store](https://www.cnccontroller.store/mks-dlc32-v2-1-cnc-controller-with-ts24-touchscreen-32-bit-wifi-grbl-board/) | Alternative board |
| **R66** | BTT Rodent — [BIQU](https://biqu.equipment/products/bigtreetech-rodent), [Rat Rig](https://ratrig.com/products/bigtreetech-rat-rig-rodent-cnc-controller-tmc2160) | Alternative board |
| **R67** | MKS TinyBee — [store](https://makerparts3d.com/products/mks-tinybee-3d-printer-control-board-with-esp32-wifi), [GitHub](https://github.com/makerbase-mks/MKS-TinyBee), [FluidNC config](https://github.com/bdring/fluidnc-config-files/blob/main/official/MKS_TinyBee_1_XYZAB.yaml) | Alternative board |
| **R68** | ESP32-DevKitC-32E — [Grid Connect](https://www.gridconnect.com/products/esp32-devkitc-32e-wroom-module-development-kit) | DIY alternative |
| **R69** | BTT TMC2209 module — [BIQU](https://biqu.equipment/products/bigtreetech-tmc2209-stepper-motor-driver-for-3d-printer-board-vs-tmc2208) | DIY alternative |
| **R79** | Seeed XIAO ESP32S3 Sense — [link](https://www.seeedstudio.com/XIAO-ESP32S3-Sense-p-5639.html), [OV5640 add-on](https://www.seeedstudio.com/OV5640-Camera-for-XIAO-ESP32S3-Sense-With-Heat-Sink-p-5739.html) | Wireless camera alternative (rejected: autofocus) |
| **R80** | Freenove FNK0085 — [store](https://store.freenove.com/products/fnk0085); [espressif issue #10792](https://github.com/espressif/arduino-esp32/issues/10792) | Wireless camera alternative |
| **R82** | Mean Well STEP files FAQ — [link](https://meanwellpowersupplies.com/technical-articles/faq/where-to-find-mean-well-step-files-3d-files/) | Where Mean Well CAD lives |

## Licences and publishing

| ID | Source | Used for |
|---|---|---|
| **R71** | SPDX license-list-data — [GitHub](https://github.com/spdx/license-list-data) | Licence texts in `LICENSES/` |
| **R72** | OSHWA certification — [certification.oshwa.org](https://certification.oshwa.org/) | Certification checklist |

## Parts: power and electrical

| ID | Source | Used for |
|---|---|---|
| **P1** | MEAN WELL GST60A24-P1J — [Mouser](https://www.mouser.com/ProductDetail/MEAN-WELL/GST60A24-P1J?qs=odmYgEirbwyH6XaEPxnETQ%3D%3D) | $19.40, STEP listing |
| **P2** | GST60A spec — [PDF](https://www.meanwell.com/Upload/PDF/GST60A/GST60A-SPEC.PDF); [MEAN WELL UK](https://www.meanwell.co.uk/power-supplies/external-power-supplies/gst60a-series) | Plug, efficiency, Level VI, UL |
| **P3** | GST60A24-P1J — [TRC](https://trcelectronics.com/products/mean-well-gst60a24-p1j), [Jameco](https://www.jameco.com/z/GST60A24-P1J-MEAN-WELL-24-Volt-2500mA-60-Watt-3-Wire-Regulated-Switching-Desktop-Power-Adapter-2-1mm-Plug-Level-VI_2224411.html), [Bravo](https://www.bravoelectro.com/gst60a24-p1j.html), [Digi-Key](https://www.digikey.com/en/products/detail/mean-well-usa-inc/GST60A24-P1J/7703715) | No-load power, price cross-check, cord sold separately |
| **P4** | Switchcraft 721A — [product](https://www.switchcraft.com/dc-power-jack-0-084-2-1mm-pin-solder-lugs-termination/721a/) | 2.1 mm, 5 A / 24 V |
| **P5** | Switchcraft 721A — [Octopart](https://octopart.com/721a-switchcraft-89444436), [Digi-Key](https://www.digikey.com/en/products/detail/switchcraft-inc/721A/8571716) | $4.03 |
| **P6** | Littelfuse 01500274ZXU — [Mouser](https://www.mouser.com/ProductDetail/Littelfuse/01500274ZXU?qs=HS3fcsxbgMwxzHo3fy8LGg%3D%3D) | $3.27 |
| **P7** | Infineon IRF4905PBF — [Mouser](https://www.mouser.com/ProductDetail/Infineon-Technologies/IRF4905PBF?qs=9%2BKlkBgLFf39l0HsWdxvdw%3D%3D) | $2.73 |
| **P8** | IRF4905 — [datasheet](https://www.infineon.com/dgdl/irf4905pbf.pdf?fileId=5546d462533600a4015355e329b1197e), [Digi-Key](https://www.digikey.com/en/products/detail/infineon-technologies/IRF4905PBF/812139), [SnapEDA](https://www.snapeda.com/parts/IRF4905PBF/Infineon/view-part/) | Rds(on), Vgs |
| **P9** | onsemi 1N4742A — [Mouser](https://www.mouser.com/ProductDetail/onsemi/1N4742A?qs=SSucg2PyLi71ahupZUxJzg%3D%3D) | $0.28 |
| **P10** | P6KE30A (Littelfuse via Verical, chosen; ST at Mouser compared) — [Mouser](https://www.mouser.com/ProductDetail/STMicroelectronics/P6KE30A?qs=5Uvc6lfWVJxhgPKxz%252Bj4DQ%3D%3D), [Octopart](https://octopart.com/p6ke30a-littelfuse-348661) | $0.94 |
| **P11** | Nichicon UFW1H101MPD1TD — [Mouser](https://www.mouser.com/ProductDetail/Nichicon/UFW1H101MPD1TD?qs=WJSLByB5Mu30jPPJ2KiG3A%3D%3D) | $0.59 |
| **P12** | Vishay BAT85S-TAP — [Mouser](https://www.mouser.com/ProductDetail/Vishay-Semiconductors/BAT85S-TAP?qs=yIvl1B2wDi5bZOHuqaPTHw%3D%3D) | Considered for the sense clamp (replaced by an optocoupler) |
| **P13** | Bulgin C1353ABNAB — [Digi-Key](https://www.digikey.com/en/products/detail/bulgin/C1353ABNAB/9598373) | 10 A DC rating |
| **P14** | Arcolectric C1300ALAAA — [Newark](https://www.newark.com/arcolectric-bulgin-limited/c1300alaaa/rocker-switch-spst-on-off-black/dp/48W5536), [Octopart](https://octopart.com/part/arcolectric/C1300ALAAA) | Rocker alternative |
| **P15** | IDEC YW1B-V4E01R — [TME](https://www.tme.com/us/en-us/details/yw1b-v4e01r/panel-mount-switches-standard-22mm/idec/) | $9.96 |
| **P16** | IDEC YW series — [datasheet](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6163/D004450YWapem.pdf) | DC ratings |
| **P17** | Eaton M22-PV / M22-K01 — [IMC](https://www.imc-direct.com/product_p/m22-pv.htm), [TME](https://www.tme.com/us/en-us/details/m22-k01/panel-mount-accessories/eaton-electric/), [IMC kit](https://www.imc-direct.com/product_p/m22-pv-k01.htm), [Mouser](https://www.mouser.com/en/ProductDetail/Eaton-Electrical/M22-PV-K01?qs=HFfMDpzxxd0QRHbJBijxWA%3D%3D) | E-stop price comparison |
| **P18** | AMASS XT30U — [rcbattery](https://rcbattery.com/genuine-amass-xt30u-male-female-pair-plugs-5-pairs.html) | $2.19 / 5 pairs |
| **P19** | realthunder/Connectors_Amass.3dshapes — [GitHub](https://github.com/realthunder/Connectors_Amass.3dshapes) | XT30 STEP |
| **P20** | 18 AWG silicone pair — [Walmart](https://www.walmart.com/ip/2-Conductor-Parallel-Silicone-Wire-18AWG-18-Gauge-Red-Black-Electrical-Wire-Tinned-Copper-1m-3-3ft/2401235173), [BNTECHGO](https://www.amazon.com/BNTECHGO-Silicone-Flexible-Strands-Stranded/dp/B01AQOI36M) | $8.09 |
| **P21** | Adafruit perfboard 4783 — [link](https://www.adafruit.com/product/4783) | $2.25 |
| **P22** | Keszoox JST-XH kit — [Amazon](https://www.amazon.com/Keszoox-Connector-Pre-Crimped-Housing-Socket%EF%BC%8810/dp/B09SX4LC13) | Listing (price not confirmed) |
| **P23** | Schneider XB5AS8442 — [TME](https://www.tme.com/us/en-us/details/xb5as8442/panel-mount-switches-standard-22mm/schneider-electric/), [RSP Supply](https://rspsupply.com/p-83740-schneider-electric-xb5as8442-red-40-emergency-stop-switching-off-pushbutton-22-latching-turn-release.aspx); XB2BS542C — [LCSC](https://www.lcsc.com/product-detail/Pushbutton-Switches_Schneider-XB2BS542C_C5122145.html) | Rejected (0.5 A DC-13) |
| **P24** | Omron A22E-M-01 — [Octopart](https://octopart.com/a22e-m-01-omron-35187) | Rejected (price) |
| **P25** | Pololu rocker #1406 — [link](https://www.pololu.com/product/1406) | Rejected (AC only) |
| **P26** | CW Industries GRB112B802BR1 — [Octopart](https://octopart.com/grb112b802br1-cw+industries-19058098) | Rejected (14 V DC) |
| **P27** | Switchcraft 722A — [Mouser](https://www.mouser.com/ProductDetail/Switchcraft/722A?qs=MI16PYk8XEPiQCOy7frM9Q%3D%3D) | Rejected (2.0 mm pin) |
| **P28** | Same Sky PJ-002BH — [link](https://www.sameskydevices.com/product/interconnect/connectors/dc-power-connectors/jacks/pj-002bh) | Rejected (2.5 mm pin) |
| **P29** | Same Sky PJ-009A — [Octopart](https://octopart.com/part/same-sky/PJ-009A) | Rejected (2.5 A) |
| **P30** | GST90A24-P1M — [Jameco](https://www.jameco.com/z/GST90A24-P1M-MEAN-WELL-24-Volt-3750mA-90-Watt-3-Wire-Regulated-Switching-Desktop-Power-Adapter-2-5mm-Plug-Level-VI_2223494.html), [Digi-Key](https://www.digikey.com/en/products/detail/mean-well-usa-inc/GST90A24-P1M/7703720) | Comparison |
| **P31** | GST120A24-P1M (v0.1) — [Mouser](https://www.mouser.com/en/ProductDetail/MEAN-WELL/GST120A24-P1M?qs=V113mesSgrhUmhAWUz3R2A%3D%3D), [TRC](https://www.trcelectronics.com/products/mean-well-gst120a24-p1m), [spec](https://www.meanwell.com/Upload/PDF/GST120A/GST120A-SPEC.PDF) | v0.1 supply |
| **P32** | Pololu regulators (v0.1) — [D42V55F5](https://www.pololu.com/product/5571), [D42V55F5.3](https://www.pololu.com/product/5572), [D36V50F5](https://www.pololu.com/product/4091), [resources/STEP](https://www.pololu.com/product/4091/resources), [D24V50F5](https://www.pololu.com/product/2851) | v0.1 5 V rail (removed: no Pi) |
| **P33** | Same Sky PJ-005B (v0.1) — [Digi-Key](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/PJ-005B/172263), [datasheet](https://www.sameskydevices.com/product/resource/pj-005b.pdf), [Octopart](https://octopart.com/part/same-sky/PJ-005B); Switchcraft 712A — [Newark](https://www.newark.com/switchcraft/712a/connector-dc-power-jack-5a/dp/37F2993) | v0.1 jack |
| **P34** | Littelfuse (v0.1) — [03455LS1H](https://www.newark.com/littelfuse/03455ls1h/fuse-holder-5-x-20mm-panel-mount/dp/67K0280), [021806.3MXP](https://www.newark.com/littelfuse/021806-3mxp/fuse-cartridge-6-3a-5x20mm-slow/dp/42K9390), [03453LS1H](https://www.digikey.com/en/products/detail/littelfuse-inc/03453LS1H/553765) | v0.1 fuse |
| **P35** | Jameco SRC1-1B-DC-1-B (v0.1) | Rejected (momentary) |
| **P40** | StepperOnline 17HS19-2004S1 — [product](https://www.omc-stepperonline.com/nema-17-bipolar-59ncm-84oz-in-2a-42x48mm-4-wires-w-1m-cable-connector-17hs19-2004s1), [datasheet](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1_Full_Datasheet.pdf), [STEP](https://www.omc-stepperonline.com/index.php?route=product/product/get_file&file=110/17HS19-2004S1.STEP) | $9.62, coil data |
| **P41** | Kingroon GT2 closed belts — [link](https://kingroon.com/products/gt2-closed-loop-timing-belt-rubber-2gt-6mm-3d-printers-parts-110-112-122-158-200-280-300-400-610-852-mm-synchronous-belts) | $1.88 |
| **P42** | ZYLtech GT2 20T pulley — [link](https://www.zyltech.com/2gt-gt2-6mm-wide-20t-pulley-5mm-6-35mm-or-8mm-bore/) | $2.95 |
| **P43** | TCST2103 optical endstop — [eBay](https://www.ebay.com/itm/182778778905) | $2.93 |
| **P44** | ZYLtech GT2 belt per metre — [link](https://www.zyltech.com/fiber-glass-reinforced-2gt-gt2-timing-belt-custom-length-price-per-meter/) | $2.50/m |

## Parts: controller

| ID | Source | Used for |
|---|---|---|
| **C1** | FYSETC E4 — [GitHub README](https://github.com/FYSETC/FYSETC-E4), [schematic](https://github.com/FYSETC/FYSETC-E4/blob/main/hardware/FYSETC%20E4_V1.0%20SCH.pdf), [hardware](https://github.com/FYSETC/FYSETC-E4/tree/main/hardware) | Pin map, specs |
| **C2** | FYSETC E4 wiki — [link](https://wiki.fysetc.com/docs/E4) | Drivers, CH340, size |
| **C3** | FYSETC E4 store — [link](https://www.fysetc.com/products/fysetc-e4-board-with-built-in-wi-fi-and-bluetooth-4-pcs-tmc2209-240mhz-16m-flash-3d-printer-control-board-based-for-3d-printer) | $32.00 |
| **C4** | E4 listings — [AliExpress 1](https://www.aliexpress.com/item/1005001703930983.html), [AliExpress 2](https://www.aliexpress.com/item/1005001704413148.html), [Amazon.ca](https://www.amazon.ca/Compatible-Bluetooth-TMC2209-Printer-Control/dp/B0FDWPRKS5) | Availability |
| **C5** | Raspberry Pi Pico — [product](https://www.raspberrypi.com/products/raspberry-pi-pico/), [SparkFun](https://www.sparkfun.com/raspberry-pi-pico.html) | $4.00 |
| **C6** | Pico files — [STEP](https://datasheets.raspberrypi.com/pico/Pico-R3-step.zip), [pinout](https://datasheets.raspberrypi.com/pico/Pico-2-Pinout.pdf), [datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf), [docs](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html) | CAD, pins |
| **C7** | Adafruit USB cables — [4474](https://www.adafruit.com/product/4474), [898](https://www.adafruit.com/product/898) | Cable prices |

## Parts: camera

| ID | Source | Used for |
|---|---|---|
| **K1** | Arducam B0433 (IMX477 USB, M12) — [product](https://www.arducam.com/12mp-usb-camera-module-with-m12-lens-1-2-3-3840hx3032v-4k30fps-for-windows-linux-macos-and-android.html) | $59.99, controls |
| **K2** | Arducam UVC selection guide — [link](https://docs.arducam.com/UVC-Camera/USB2-UVC-Camera-Kit/Specs-and-Selection-Guide/) | Sensor = IMX477 |
| **K3** | B0433 datasheet — [PDF](https://www.uctronics.com/download/Amazon/B0433_Arducam_12MP_USB_Camera_Module_Datasheet.pdf) | Mechanical drawing |
| **K4** | Arducam B0446 (IMX179) — [product](https://www.arducam.com/8mp-imx179-usb-camera-module-with-wide-angle-115h-m12-lens-for-windows-linux-android-and-mac-os.html) | Fallback ($54.99, manual WB) |
| **K5** | VA Imaging 16 mm M12 lens — [link](https://va-imaging.com/en-us/products/lens-m12-5mp-16mm-f2-0-1-2-va-lm12-5mp-16mm-f2-0-020) | $21.00 |
| **K6** | Arducam forum, B0433 exposure via v4l2 — [link](https://forum.arducam.com/t/b0433-camera-unable-to-change-exposure-time-from-v4l2/7522) | Discard frames after a change |
| **K7** | Arducam forum, IMX477 UVC max exposure — [link](https://forum.arducam.com/t/arducam-imx477-uvc-camera-adapter-board-max-exposure-time/1387) | ~0.5 s limit |
| **K8** | Arducam forum, IMX477 USB 12-bit — [link](https://forum.arducam.com/t/imx477-usb-12bit-capabilities/2466) | No RAW over UVC |
| **K9** | Arducam USB3.0 Camera Shield Plus — [link](https://docs.arducam.com/USB-Industrial-Camera/USB3.0-Camera-Shield-Plus/USB3.0-Camera-Shield-Plus-Datasheet/) | RAW option (SDK) |
| **K10** | Arducam B0459 — [link](https://www.arducam.com/arducam-12mp-usb-3-0-camera-with-m12-manual-focus-lens.html) | Step-up option |
| **K11** | Arducam B0280 — [link](https://www.arducam.com/arducam-high-quality-complete-usb-camera-bundle-12mp-1-2-3-inch-imx477-camera-module-with-6mm-cs-mount-lens-metal-enclosure-tripod-and-usb-cable-b0280.html) | Compared |
| **K12** | ELP IMX179 — [link](http://www.webcamerausb.com/elpusb30w04mtl36-p-149.html) | Compared |
| **K13** | Arducam B0304 IMX708 — [link](https://www.uctronics.com/12mp-imx708-usb-uvc-fixed-focus-camera-module-3.html) | Compared |
| **K14** | Arducam B0362 IMX291 — [link](https://www.arducam.com/arducam-imx291-usb-camera-with-2-8-12mm-lens-b0362.html) | Compared |
| **K15** | TraceParts Arducam models — [link](https://www.traceparts.com/en/search/arducam-usb-uvc-camera?CatalogPath=ARDUCAM_1206236589:ARDUCAM.020) | CAD search |
| **K16** | Arducam forum, 3D model request — [link](https://forum.arducam.com/t/searching-for-3d-model-of-b0202/809) | CAD search |
| **K17** | InnoMaker IMX298 USB — [Amazon](https://www.amazon.com/InnoMaker-4656x3496-Detection-Auto-Focus-Raspberry/dp/B0G2VZP6SL) | Rejected (autofocus) |
| **K18** | Commonlands CIL160 16 mm — [link](https://commonlands.com/products/16mm-m12-lens) | Lens upgrade |
| **K19** | Raspberry Pi HQ Camera (v0.1) — [CS](https://www.pishop.us/product/raspberry-pi-hq-camera-cs/), [M12](https://www.pishop.us/product/raspberry-pi-hq-camera-m12/), [brief](https://pip-assets.raspberrypi.com/categories/659-raspberry-pi-high-quality-camera/documents/RP-008202-DS-1-hq-camera-product-brief.pdf), [M12 drawing](https://pip-assets.raspberrypi.com/categories/659-raspberry-pi-high-quality-camera/documents/RP-008201-DS-1-hq-camera-m12-mechanical-drawing.pdf) | v0.1 camera |
| **K20** | Raspberry Pi Camera Module 3 (v0.1) — [PiShop](https://www.pishop.us/product/raspberry-pi-camera-module-3/), [STEP](https://pip-assets.raspberrypi.com/categories/1207-design-files/documents/RP-008154-DS-1-camera-module-3-step.zip) | v0.1 fallback |
| **K21** | Pi 5 camera cable (v0.1) — [PiShop](https://www.pishop.us/product/camera-cable-for-raspberry-pi-5/) | v0.1 |
| **K22** | Arducam LN036 (v0.1) — [link](https://www.arducam.com/arducam-telephoto-20-degree-1-2-3-m12-mount-with-lens-adapter-for-raspberry-pi-high-quality-camera.html) | v0.1 lens note |

## Parts: light

| ID | Source | Used for |
|---|---|---|
| **L1** | Cree CXA1304-0000-000C0Y9430H — [Mouser](https://www.mouser.com/ProductDetail/Cree-LED/CXA1304-0000-000C0Y9430H?qs=G0uBbFPHMulh2b3olRHR4A%3D%3D) | $2.66, CRI 93, 9 V |
| **L2** | Luminus CXM-4 Gen 4 — [datasheet](https://download.luminus.com/datasheets/Luminus_CXM-4_GEN4_Datasheet.pdf) | 18 V class, CRI 95 options |
| **L3** | CXM-4 availability — [Octopart CXM-4-30-95-18](https://octopart.com/part/luminus-devices/CXM-4-30-95-18-AC40-F5-3), [Mouser -50-95-18](https://www.mouser.com/ProductDetail/Luminus-Devices/CXM-4-50-95-18-AC40-F5-3?qs=DPoM0jnrROW%252BbPFMtDMVfQ%3D%3D), [Mouser -30-90-18](https://www.mouser.com/en/ProductDetail/Luminus-Devices/CXM-4-30-90-18-AC40-F5-3?qs=DPoM0jnrROVkRRFTMvUU3g%3D%3D), [Digi-Key -27-80-18](https://www.digikey.com/en/products/detail/luminus-devices-inc/CXM-4-27-80-18-TE60-F7-2/21348065) | Preferred-if-stocked option |
| **L4** | MEAN WELL NLDD-350H — [Power Supply Mall](https://powersupplymall.com/products/mean-well-nldd-350h-dc-dc-led-driver-cc-350ma-step-down) | $4.81 |
| **L5** | NLDD-350H — [TRC](https://trcelectronics.com/products/mean-well-nldd-350h) | $5.55, ranges |
| **L6** | NLDD-H spec — [PDF](https://www.meanwell.com/Upload/PDF/NLDD-H/NLDD-H-SPEC.PDF) | Efficiency, DIM |
| **L7** | Easycargo 40 mm heatsinks — [Amazon](https://www.amazon.com/Easycargo-40x40x11mm-TEC1-12706-Thermoelectric-40mmx40mmx11mm/dp/B07WR7MPB1) | Listing |
| **L8** | Yuji LEDs — [HD5 CRI 95](https://store.yujiintl.com/products/yujileds-cri-95-5mm-9w-cob-led-2700k-3200k-4000k-hd5), [CRI 98 9 W](https://store.yujiintl.com/products/yujileds-cri-98-9w-cob-led-135l) | High-CRI upgrade |
| **L9** | Luminus CXM-9 (v0.1) — [datasheet](https://download.luminus.com/datasheets/Luminus_CXM-9_GEN6_Datasheet.pdf), [Mouser](https://www.mouser.com/ProductDetail/Luminus-Devices/CXM-9-30-95-36-AA00-F2-3?qs=Qlzq7FOrON4Xiqce7VRkYw%3D%3D) | Rejected (36 V) |
| **L10** | Bridgelux Vero SE 13 Thrive — [datasheet](https://www.bridgelux.com/sites/default/files/resource_media/Bridgelux%20DS346%20Gen%207%20Vero%20SE%2013%20Thrive%20Array%20Datasheet%20RevA%2020220331.pdf) | Compared |
| **L11** | LEDiL C13658 clamp — [Digi-Key](https://azcus.digikey.com/en/products/detail/ledil/C13658-CLAMP-VERO13-18/4490851) | Compared |
| **L12** | LEDSupply heatsinks — [link](https://www.ledsupply.com/led-housing-heatsinks) | Compared |
| **L13** | MEAN WELL LDD-H — [LEDSupply](https://www.ledsupply.com/led-drivers/mean-well-ldd-h-series-cc-step-down-mode); [LDD-700H Octopart](https://octopart.com/ldd-700h-mean+well-20023764) | v0.1 driver |
| **L14** | NLDD-350H — [RapidLED](https://rapidled.com/products/mean-well-ldd-350h-dimmable-driver) | v0.1 price |
| **L15** | LEDiL ANGELA-S — [Digi-Key](https://www.digikey.com/en/products/detail/ledil/F13379-ANGELA-S/4946614) | Optic option |
| **L16** | LEDiL Angelina — [cobkits](https://cobkits.com/product/ledil-angelina-reflector-f13838-for-ideal/) | Rejected (90 deg) |
| **L17** | Generic COB reflector — [Amazon](https://www.amazon.com/10W-100W-Adapter-Reflector-Collimator-Bracket/dp/B00VSNYNCY) | Compared |
| **L18** | Cree CXA1507 — [Newark](https://www.newark.com/cree-led/cxa1507-0000-000n0ye230g/led-array-cob-warm-wht-3000k-590lm/dp/49AC0147) | Rejected (35 V) |
| **L19** | 24 V COB strip CRI 90 — [ledupdates](https://ledupdates.com/products/24v-cob-series-cri-90-4000k-natural-white-color-led-strip-light) | Rejected (roll price) |
| **L20** | Edmund XP42 polarizer film — [link](https://www.edmundoptics.com/p/100-x-100mm-linear-polarizing-film-xp42-40/52988/) | Compared |

## Parts: mechanics and frame

| ID | Source | Used for |
|---|---|---|
| **M1** | Bear Woods LZ-12 — [link](https://www.bearwood.com/en-us/products/12-round-lazy-susan-turntable-bearings) | $13.90 |
| **M2** | VXB 12 in aluminium turntable — [link](https://vxb.com/products/12-inch-aluminum-lazy-susan-turntable-bearing) | Upgrade |
| **M3** | KW12-3 roller micro switches — [Walmart](https://www.walmart.com/ip/10Pcs-Roller-Lever-Arm-Open-Close-Limit-Switch-Kw12-3-Pcb-Microswitch/1344341711) | $7.00 / 10 |
| **M4** | Woodpeckers bearings — [12C](https://woodpeckerscrafts.com/products/12c-ls-bearing), [4 in](https://woodpeckerscrafts.com/products/4c-ls-bearing) | Compared |
| **M5** | VXB 12 in steel, VXB 4 in — [12 in](https://vxb.com/products/12-inch-lazy-susan-bearing-1000lb-usa), [4 in](https://vxb.com/products/300-lbs-capacity-4-lazy-susan-bearing-5-16-thick-t) | Compared |
| **M6** | 3 x 3 in turntable (McMaster 6031K16) — [RobotShop](https://www.robotshop.com/en/3x3-ball-bearing-turntable.html) | Corrected v0.1 assumption |
| **M7** | VXB bearings — [608 10-pack](https://vxb.com/products/10-pack-skateboard-bearing-608-2rs-sealed-8x22x7mm), [6806](https://vxb.com/products/6806-2rs-bearing-30x42x7-sealed) | Compared |
| **M8** | TNutz LF-015-A foot — [link](https://www.tnutz.com/product/lf-015-a/) | v0.1 feet |
| **M9** | ZYLtech extrusion and T-nuts — [2020](https://www.zyltech.com/store/aluminum-extrusion-hardware/2020-t-slot/), [T-nuts](https://www.zyltech.com/100x-zyltech-spring-loaded-t-nuts-for-2020-aluminum-extrusion-m4-or-m5/) | v0.1 |
| **F1** | Birch plywood 2 x 2 ft — [Lowe's](https://www.lowes.com/pd/1-2-in-Birch-Plywood-Application-as-2-x-2/1000066183) | Base (price not confirmed) |
| **F2** | OpenBuilds V-Slot 20x20 — [link](https://us.openbuilds.com/v-slot-20x20-linear-rail/) | $3.29 / 500 mm |
| **F3** | KB-3D M5 T-nut — [link](https://kb-3d.com/store/extrusion-framing/252-t-nut-drop-inroll-in-20-series-6mm-slot-width-m5-threads-1657989339400.html) | $0.17 |
| **F4** | M8 tee nut — [Albany County Fasteners](https://www.albanycountyfasteners.com/metric-t-nuts-zinc-plated-steel-m8-x-125-4-prong-5602-010-042/) | $0.45 |
| **F5** | Glarks screw kit — [Amazon](https://www.amazon.com/Glarks-510Pcs-Socket-Screws-Assortment/dp/B08HHZHXTP) | Listing |
| **F6** | M3 heat-set inserts — [Adafruit 4255](https://www.adafruit.com/product/4255), [CNC Kitchen](https://cnckitchenus.store/products/heat-set-insert-m3-x-5-7-100-pieces) | $5.95 |
| **F7** | 608-2RS 10-pack — [Walmart](https://www.walmart.com/ip/10Pcs-set-608-2RS-Bearing-Deep-Groove-Steel-Sealed-Ball-Bearings-608RS-608-2RS/3999331773) | $9.90 |

## Parts: enclosure, calibration, multispectral

| ID | Source | Used for |
|---|---|---|
| **E1** | Roc-lon blackout fabric — [Walmart](https://www.walmart.com/ip/Roc-lon-54-Blackout-White-Fabric-per-Yard/164714653) | $6.62 / yd |
| **E2** | Protostar FlockBoard — [link](https://www.fpi-protostar.com/flockboard.htm); flocking — [First Light Optics](https://www.firstlightoptics.com/telescope-flocking-material/protostar-self-adhesive-hi-tack-flocking-material-1m-roll.html) | Backdrop upgrade |
| **E3** | Oak dowel 1/2 x 36 in — [Home Depot](https://www.homedepot.com/p/Builder-s-Choice-1-2-in-x-36-in-Oak-Round-Dowel-HDDO1236/206184685) | $4.04 |
| **E4** | PTFE plate — [OnlineMetals](https://www.onlinemetals.com/en/buy/plastic-sheet-plate-ptfe); [Online Metal Supply block](https://onlinemetalsupply.com/2-x-2-5-x-2-5-ptfe-teflon-plastic-sheet-white/) | $22.97 |
| **E5** | Edmund #43-876 first-surface mirror — [link](https://www.edmundoptics.com/p/50-x-50mm-enhanced-aluminum-4-6lambda-mirror/5362); also [BMI Surplus](https://bmisurplus.com/product/first-surface-mirror-4-inch-square/), [firstsurfacemirror.com](https://www.firstsurfacemirror.com/product/4-x-4-1-4-wave-glass-first-surface-mirror-13-64-5mm-thickness/) | Mirror upgrade / price check |
| **E6** | BC Precision 1 in G25 balls — [link](https://www.bcprecision.com/products/1-inch-chrome-steel-ball-bearings-g25) | $9.95 |
| **E7** | Colour targets — [Calibrite CC Mini (B&H)](https://www.bhphotovideo.com/c/product/1649333-REG/calibrite_ccc_mini_colorchecker_classic_mini.html), [SpyderCHECKR 24 (B&H)](https://www.bhphotovideo.com/c/product/1070560-REG/datacolor_sck24_sypdercheckr_24.html) | Optional, borrow |
| **E8** | Linear polarizer film 10-pack — [Walmart](https://www.walmart.com/ip/5466199163) | $8.95 |
| **E9** | Neewer 18 % gray card — [link](https://neewer.com/products/neewer-18-gray-white-card-set-for-white-balance-exposure-value-66600656) | Optional |
| **E10** | Opal acrylic 12 x 12 — [Walmart](https://www.walmart.com/ip/1-8-3mm-Milky-White-Acrylic-12-x12-Sheet-Translucent-Plexiglass-Cast-AZM/1515407359) | Diffuser option |
| **E11** | Micro servos — [Adafruit SG92R](https://www.adafruit.com/product/169), [Pololu FS90](https://www.pololu.com/product/2818) | Phase 5 option |
