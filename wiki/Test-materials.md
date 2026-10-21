<!-- generated from wiki/src/Test-materials.md by tools/refs_bib.py - edit the source -->

# Test materials

θi = M4 − M3 (light from the normal), θr = M3 (camera from the normal), in-plane. Isotropic needs 3 angles (M4, M3, M2); anisotropic needs 4 (adds M1).

| Material                          | Type                | Light (M4) · camera (θr = M3)                                 | What to look for                                            |
|-----------------------------------|---------------------|---------------------------------------------------------------|-------------------------------------------------------------|
| PTFE white reference              | isotropic, diffuse  | 45° · 0° (CIE 45°:0°)                                         | flat response; calibrates brightness (Weidner & Hsia, 1981) |
| Matte paper                       | isotropic, diffuse  | 60° · sweep M3                                                | ≈ cos θr                                                    |
| First-surface mirror              | isotropic, specular | 60° · 30°                                                     | peak at M3 = M4/2; calibrates angles                        |
| Glossy plastic (acrylic, LEGO)    | isotropic, glossy   | 40/80/120° · M4/2 ± 10°                                       | lobe width → roughness                                      |
| Metallic car paint                | isotropic, flake    | 90° · 35° (15° off specular)                                  | sparkle, colour shift (ASTM International, 2025)            |
| Brushed aluminium                 | **anisotropic**     | 60° · 30°, spin M1 0–180°                                     | highlight stretches across the brushing (Ward, 1992)        |
| Satin ribbon                      | **anisotropic**     | 70° · 35°, M2 15°, M1 15° steps                               | two lobes vs direction                                      |
| Velvet / retroreflective tape     | back-scatter        | 20° (closest allowed) · 10°                                   | peak toward the light                                       |
| 3D scan: matte print, painted toy | object              | lamp 30°, scan camera 650 mm / 15° up, M2 85→25°, M1 36 steps | spray shiny parts matte                                     |

## References

ASTM International. (2025). *Standard test method for multiangle color measurement of metal flake pigmented materials*. <https://doi.org/10.1520/E2194-14R25>

Ward, G. J. (1992). Measuring and modeling anisotropic reflection. *ACM SIGGRAPH Computer Graphics*, *26*(2), 265–272. <https://doi.org/10.1145/142920.134078>

Weidner, V. R., & Hsia, J. J. (1981). Reflection properties of pressed polytetrafluoroethylene powder. *Journal of the Optical Society of America*, *71*(7), 856–861. <https://doi.org/10.1364/JOSA.71.000856>
