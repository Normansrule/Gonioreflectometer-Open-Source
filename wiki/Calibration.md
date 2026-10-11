<!-- generated from wiki/src/Calibration.md by tools/refs_bib.py - edit the source -->

# Calibration

| Quantity                 | Method                                                                             | Pass            |
|--------------------------|------------------------------------------------------------------------------------|-----------------|
| Angle offset             | mirror peak must sit at M3 = M4 / 2 (Ansari-Asl et al., 2024)                      | residual ≤ 0.1° |
| Dark level $C_d$         | lamp-off frame                                                                     | —               |
| Camera response $\gamma$ | exposure series (Debevec & Malik, 1997)                                            | linear fit      |
| Absolute BRDF            | PTFE (polytetrafluoroethylene) tile, ≈ 99 % diffuse, at 45° (Weidner & Hsia, 1981) | —               |
| Lamp drift               | repeat the first pose at the end                                                   | ≤ 2 %           |

``` math
f_r=\frac{C_{\mathrm{lin}}}{C_{w,\mathrm{lin}}}\cdot\frac{\rho_w}{\pi}\cdot\frac{\cos 45^\circ}{\cos\theta_i},\qquad C_{\mathrm{lin}}=(C-C_d)^{\gamma}
```

$C$ camera counts, $C_w$ white tile, $\rho_w$ its reflectance. Steps: stage [07](https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main/phases/07-calibrate).

## References

Ansari-Asl, M., Barbieri, M., Obein, G., & Hardeberg, J. Y. (2024). Optical and electromechanical design and implementation of an advanced multispectral device to capture material appearance. *Journal of Imaging*, *10*(3), 55. <https://doi.org/10.3390/jimaging10030055>

Debevec, P., & Malik, J. (1997). Recovering high dynamic range radiance maps from photographs. *Proc. SIGGRAPH ’97*. <https://pauldebevec.com/Research/HDR/debevec-siggraph97.pdf>

Weidner, V. R., & Hsia, J. J. (1981). Reflection properties of pressed polytetrafluoroethylene powder. *Journal of the Optical Society of America*, *71*(7), 856–861. <https://doi.org/10.1364/JOSA.71.000856>
