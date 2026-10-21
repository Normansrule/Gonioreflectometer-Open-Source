# Calibration

| Quantity | Method | Pass |
|---|---|---|
| Angle offset | mirror peak must sit at M3 = M4 / 2 [@R1] | residual ≤ 0.1° |
| Dark level $C_d$ | lamp-off frame | — |
| Camera response $\gamma$ | exposure series [@R5] | linear fit |
| Absolute BRDF | PTFE (polytetrafluoroethylene) tile, ≈ 99 % diffuse, at 45° [@N30] | — |
| Lamp drift | repeat the first pose at the end | ≤ 2 % |

```math
f_r=\frac{C_{\mathrm{lin}}}{C_{w,\mathrm{lin}}}\cdot\frac{\rho_w}{\pi}\cdot\frac{\cos 45^\circ}{\cos\theta_i},\qquad C_{\mathrm{lin}}=(C-C_d)^{\gamma}
```

$C$ camera counts, $C_w$ white tile, $\rho_w$ its reflectance. Steps: stage [07]({{REPO}}/phases/07-calibrate).
