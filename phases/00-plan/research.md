# 00 · Research

## Equations

Sources: [R2] [R1] [G1] [R5] [R6] [R7] [R8] [T11] [T17] [T35] [T40]. $\theta$ from the surface normal, $\varphi$ azimuth; $\omega_i$ toward the light, $\omega_r$ toward the camera.

### 1. Reflectance (CS348b [R2])

**BRDF** [G1]

$$f_r(\omega_i \to \omega_r) \equiv \frac{dL_r(\omega_i \to \omega_r)}{dE_i} \qquad [\mathrm{sr}^{-1}]$$

**Reflection equation**

$$L_r(x,\omega_r) = \int_{H^2} f_r(x,\omega_i \to \omega_r)\, L_i(x,\omega_i)\cos\theta_i \, d\omega_i$$

**Linearity:** $f_r = \sum_k f_{r,k}$

**Reciprocity** (calibration check):

$$f_r(\omega_r \to \omega_i) = f_r(\omega_i \to \omega_r)$$

**Isotropy:**

$$f_r(\theta_i,\varphi_i;\theta_r,\varphi_r) = f_r(\theta_i,\theta_r,\varphi_r-\varphi_i) = f_r(\theta_i,\theta_r,|\varphi_r-\varphi_i|)$$

**Energy conservation:**

$$\frac{d\Phi_r}{d\Phi_i} = \frac{\int_{\Omega_r} L_r(\omega_r)\cos\theta_r\,d\omega_r}{\int_{\Omega_i} L_i(\omega_i)\cos\theta_i\,d\omega_i} \le 1$$

**Law of reflection** (mirror calibration):

$$\theta_r = \theta_i, \qquad \varphi_r = (\varphi_i + \pi) \bmod 2\pi, \qquad \hat R = \hat I - 2(\hat I\cdot\hat N)\hat N$$

**Ideal mirror BRDF**

$$f_{r,m}(\theta_i,\varphi_i;\theta_r,\varphi_r) = \frac{\delta(\cos\theta_i - \cos\theta_r)}{\cos\theta_i}\,\delta(\varphi_i - \varphi_r \pm \pi), \qquad L_{r,m}(\theta_r,\varphi_r) = L_i(\theta_r,\varphi_r \pm \pi)$$

**Snell's law, refraction vector** ($\mu = \eta_i/\eta_t$):

$$\eta_i\sin\theta_i = \eta_t\sin\theta_t, \qquad \eta_i\,\hat N\times\hat I = \eta_t\,\hat N\times\hat T, \qquad \varphi_t = \varphi_i \pm \pi$$

$$\hat T = \mu\hat I + \gamma\hat N, \qquad \gamma = -\mu(\hat I\cdot\hat N) - \sqrt{1-\mu^2\left(1-(\hat I\cdot\hat N)^2\right)} = \mu\cos\theta_i - \cos\theta_t$$

**Total internal reflection** when $1-\mu^2\left(1-(\hat I\cdot\hat N)^2\right) < 0$.

**Fresnel (Schlick):** $F(0)=0.04$ glass, 0.82 gold, 0.95 silver

$$F(\theta) = F(0) + \big(1-F(0)\big)(1-\cos\theta)^5, \qquad F(0) = \left(\frac{\eta-1}{\eta+1}\right)^2$$

**Cook-Torrance colour shift:**

$$R = R(0) + R(\pi/2)\left[\frac{F(\theta)-F(0)}{F(\pi/2)-F(0)}\right]$$

**Lambert** (PTFE reference):

$$L_{r,d} = f_{r,d}\,E_i, \qquad M = \int L_r\cos\theta_r\,d\omega_r = \pi L_r, \qquad \rho_d = \frac{M}{E} = \pi f_{r,d} \;\Rightarrow\; f_{r,d} = \frac{\rho_d}{\pi}$$

**Lambert's cosine law:** $M = \rho_d\,E = \rho_d\,E_s\cos\theta$.

### 2. Fitted model

$$f_r = (1-m)(1-F)\frac{\rho}{\pi} + \frac{D(h)\,G_2(\omega_i,\omega_r)\,F(\omega_i\cdot h)}{4\cos\theta_i\cos\theta_r}, \qquad D(h) = \frac{\alpha^2}{\pi\left((h\cdot n)^2(\alpha^2-1)+1\right)^2}, \quad \alpha = r^2$$

$h = (\omega_i+\omega_r)/\|\omega_i+\omega_r\|$, $D$ GGX [R6][T11], $G_2$ height-correlated Smith [T17], $F$ Schlick with $F(0) = 0.04(1-m) + \rho\,m$; metallic-roughness as in [T35][T40].

### 3. Measured quantities ([R1])

$$Y^{\mathrm{SVBRDF}} = \mathrm{SVBRDF}(x,y,\theta_i,\varphi_i,\theta_r,\varphi_r,\lambda), \qquad Y^{\mathrm{BTF}} = \mathrm{BTF}(x,y,\theta_i,\varphi_i,\theta_r,\varphi_r,\lambda)$$

### 4. Kinematics [R1]

Camera $\hat c = (\cos e, 0, \sin e)$ fixed; light $\hat l = R_z(M_4)\,\hat x$; sample orientation by extrinsic x-y-z Tait-Bryan rotations:

$$R = R_z(M_3)\,R_y(-M_2)\,R_x(M_1), \qquad \omega^{s} = R^{\top}\omega^{w}, \qquad \theta = \arccos(\omega^{s}\cdot\hat n_s)$$

$$R_x(a)=\begin{bmatrix}1&0&0\\0&\cos a&-\sin a\\0&\sin a&\cos a\end{bmatrix},\; R_y(b)=\begin{bmatrix}\cos b&0&\sin b\\0&1&0\\-\sin b&0&\cos b\end{bmatrix},\; R_z(c)=\begin{bmatrix}\cos c&-\sin c&0\\ \sin c&\cos c&0\\0&0&1\end{bmatrix}$$

**Per-pixel directions** ($p = R\,[0,u,v]^{\top}$) [R1]:

$$\omega_i(p) = \frac{P_L - p}{\|P_L - p\|}, \qquad \omega_r(p) = \frac{P_C - p}{\|P_C - p\|}$$

**In-plane** ($M_2 = 0$, $e = 0$): $\theta_r = M_3$, $\theta_i = M_4 - M_3$, specular at $M_3 = M_4/2$.

**Step size** (16 microsteps, gear $G$): $\Delta\theta = 360^\circ/(200 \cdot 16 \cdot G)$ → 0.0047° (M4, $G = 24$), 0.0225° (M3, M2), 0.028° (M1).

### 5. Optics [R1]

$$\frac{1}{p'} - \frac{1}{p} = \frac{1}{f}, \qquad m = \frac{p'}{p}, \qquad d_{\mathrm{Airy}} = 2.44\,\lambda N, \qquad \mathrm{DOF} \approx \frac{2Nc(1+m)}{m^2}$$

Numbers: [optics.md](../06-camera-light/optics.md).

### 6. HDR [R5][V19][V20]

$$g(Z_{ij}) = \ln E_i + \ln\Delta t_j$$

### 7. Repeatability check

Lamp's mirror image shifts $s$ px (pitch $p_{px}$, path $P$, lens $f$, light radius $D_L$):

$$\Delta\theta_L = \frac{s\,p_{px}\,P}{f\,D_L}$$

≈ 8 px per 0.1°: the camera can check the 0.1° target ([R1] Fig. 12).

### 8. 3D scanning

See [12-scan-mesh/research.md](../12-scan-mesh/research.md).

## Part choices

Cheapest credible option; prices checked 2026-10-04.

| Need | Chosen | Rejected |
|---|---|---|
| Compute | Your laptop ($0) | Raspberry Pi 5, $110–175 [R63] |
| Motor board | FYSETC E4, $32: 4 × TMC2209, WiFi, BT, USB [C3] | SKR Pico $39.85 [R56]; DIY ESP32 ~$36 [R68][R69]; SKR Mini E3 $49.85 [R64] |
| Power | GST60A24 60 W, $19.40 [P1] | 120 W + 5 V buck, ~$85 (only for a Pi) [P31][P32] |
| Camera | Arducam B0433 + 16 mm lens, $80.99 [K1][K5] | Pi HQ (needs a Pi) [K19]; ESP32 cameras (autofocus) [R79][R80] |
| White light | Citizen CLU7A3-0403E1 CRI 97, 12.2 V, $5.91, in a TE Z35 holder $3.50 + NLDD-350H [L22][L23][L4] | 36 V COBs need 48 V [L9][L18]; Cree CXA1304 (first draft [L1]): holders obsolete [L21] |
| E-stop | IDEC YW1B $9.96 [P15] | Schneider XB5 (0.5 A DC) [P23]; Eaton $19.90 [P17] |
| Mirror | Glass tile ~$3 | Edmund first-surface $45.75 [E5] |
| Colour | 7 pre-wired LEDs + 1 driver, ≈ $82 (one 20-pc pack per band) | Filter cameras of [R1] |
| 3D scan | Reuse the machine + putty $3.49 [S20] | Separate scanner |
| Mesh software | COLMAP (free) [S3] | RealityScan (free for students) [S18] |
