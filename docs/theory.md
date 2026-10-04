# Theory and equations

Sources: Hanrahan, CS348b Lecture 10 [R2]; Ansari-Asl et al. 2024 [R1]; Debevec & Malik [R5]; GGX [R6]; Schlick [R7]; Cook-Torrance [R8]. Notation: $\theta$ from the surface normal, $\varphi$ azimuth; $\omega_i$ toward the light, $\omega_r$ toward the camera.

## 1. Reflectance (CS348b [R2])

**BRDF**

$$f_r(\omega_i \to \omega_r) \equiv \frac{dL_r(\omega_i \to \omega_r)}{dE_i} \qquad [\mathrm{sr}^{-1}]$$

**Reflection equation**

$$L_r(x,\omega_r) = \int_{H^2} f_r(x,\omega_i \to \omega_r)\, L_i(x,\omega_i)\cos\theta_i \, d\omega_i$$

**Linearity** — lobes add: $f_r = \sum_k f_{r,k}$ (diffuse + specular fit).

**Reciprocity** — swap light and camera, same value (our calibration check):

$$f_r(\omega_r \to \omega_i) = f_r(\omega_i \to \omega_r)$$

**Isotropy** (and with reciprocity):

$$f_r(\theta_i,\varphi_i;\theta_r,\varphi_r) = f_r(\theta_i,\theta_r,\varphi_r-\varphi_i) = f_r(\theta_i,\theta_r,|\varphi_r-\varphi_i|)$$

**Energy conservation** (fits that break it are rejected):

$$\frac{d\Phi_r}{d\Phi_i} = \frac{\int_{\Omega_r} L_r(\omega_r)\cos\theta_r\,d\omega_r}{\int_{\Omega_i} L_i(\omega_i)\cos\theta_i\,d\omega_i} \le 1$$

**Law of reflection** — mirror peak used for geometric calibration:

$$\theta_r = \theta_i, \qquad \varphi_r = (\varphi_i + \pi) \bmod 2\pi, \qquad \hat R = \hat I - 2(\hat I\cdot\hat N)\hat N$$

**Ideal mirror BRDF**

$$f_{r,m}(\theta_i,\varphi_i;\theta_r,\varphi_r) = \frac{\delta(\cos\theta_i - \cos\theta_r)}{\cos\theta_i}\,\delta(\varphi_i - \varphi_r \pm \pi), \qquad L_{r,m}(\theta_r,\varphi_r) = L_i(\theta_r,\varphi_r \pm \pi)$$

**Snell's law** and the refraction vector ($\mu = \eta_i/\eta_t$, $\hat I$ toward the surface):

$$\eta_i\sin\theta_i = \eta_t\sin\theta_t, \qquad \eta_i\,\hat N\times\hat I = \eta_t\,\hat N\times\hat T, \qquad \varphi_t = \varphi_i \pm \pi$$

$$\hat T = \mu\hat I + \gamma\hat N, \qquad \gamma = -\mu(\hat I\cdot\hat N) - \sqrt{1-\mu^2\left(1-(\hat I\cdot\hat N)^2\right)} = \mu\cos\theta_i - \cos\theta_t$$

**Total internal reflection** when $1-\mu^2\left(1-(\hat I\cdot\hat N)^2\right) < 0$.

**Fresnel (Schlick)** — $F(0)=0.04$ for glass $\eta=1.5$; metals: gold 0.82, silver 0.95:

$$F(\theta) = F(0) + \big(1-F(0)\big)(1-\cos\theta)^5, \qquad F(0) = \left(\frac{\eta-1}{\eta+1}\right)^2$$

**Cook-Torrance colour shift** (metal colour vs angle):

$$R = R(0) + R(\pi/2)\left[\frac{F(\theta)-F(0)}{F(\pi/2)-F(0)}\right]$$

**Ideal diffuse (Lambert)** — PTFE white reference:

$$L_{r,d} = f_{r,d}\,E_i, \qquad M = \int L_r\cos\theta_r\,d\omega_r = \pi L_r, \qquad \rho_d = \frac{M}{E} = \pi f_{r,d} \;\Rightarrow\; f_{r,d} = \frac{\rho_d}{\pi}$$

**Lambert's cosine law:** $M = \rho_d\,E = \rho_d\,E_s\cos\theta$.

## 2. Fitted model (Unreal / Unity style)

$$f_r = (1-m)(1-F)\frac{\rho}{\pi} + \frac{D(h)\,G_2(\omega_i,\omega_r)\,F(\omega_i\cdot h)}{4\cos\theta_i\cos\theta_r}, \qquad D(h) = \frac{\alpha^2}{\pi\left((h\cdot n)^2(\alpha^2-1)+1\right)^2}, \quad \alpha = r^2$$

$h = (\omega_i+\omega_r)/\|\omega_i+\omega_r\|$, $G_2$ height-correlated Smith [R6], $F$ Schlick with $F(0) = 0.04(1-m) + \rho\,m$.

## 3. Measured quantities ([R1])

$$Y^{\mathrm{SVBRDF}} = \mathrm{SVBRDF}(x,y,\theta_i,\varphi_i,\theta_r,\varphi_r,\lambda), \qquad Y^{\mathrm{BTF}} = \mathrm{BTF}(x,y,\theta_i,\varphi_i,\theta_r,\varphi_r,\lambda)$$

## 4. Machine kinematics (fixed camera, after [R1])

Camera $\hat c = (\cos e, 0, \sin e)$ fixed; light $\hat l = R_z(M_4)\,\hat x$; sample orientation by extrinsic x-y-z Tait-Bryan rotations:

$$R = R_z(M_3)\,R_y(-M_2)\,R_x(M_1), \qquad \omega^{s} = R^{\top}\omega^{w}, \qquad \theta = \arccos(\omega^{s}\cdot\hat n_s)$$

$$R_x(a)=\begin{bmatrix}1&0&0\\0&\cos a&-\sin a\\0&\sin a&\cos a\end{bmatrix},\; R_y(b)=\begin{bmatrix}\cos b&0&\sin b\\0&1&0\\-\sin b&0&\cos b\end{bmatrix},\; R_z(c)=\begin{bmatrix}\cos c&-\sin c&0\\ \sin c&\cos c&0\\0&0&1\end{bmatrix}$$

**Per-pixel directions** — the swatch is finite, so each point $p = R\,[0,u,v]^{\top}$ has its own angles [R1]:

$$\omega_i(p) = \frac{P_L - p}{\|P_L - p\|}, \qquad \omega_r(p) = \frac{P_C - p}{\|P_C - p\|}$$

**Phase 1 in-plane** ($M_2 = 0$, $e = 0$): $\theta_r = M_3$, $\theta_i = M_4 - M_3$, specular at $M_3 = M_4/2$.

**Step resolution** (16 microsteps, reduction $G$): $\Delta\theta = 360^\circ/(200 \cdot 16 \cdot G)$ → 0.0047° (M4, $G = 24$), 0.0225° (M3, M2), 0.028° (M1).

## 5. Optics of the fixed camera ([R1], thin lens, Cartesian convention)

$$\frac{1}{p'} - \frac{1}{p} = \frac{1}{f}, \qquad m = \frac{p'}{p}, \qquad d_{\mathrm{Airy}} = 2.44\,\lambda N, \qquad \mathrm{DOF} \approx \frac{2Nc(1+m)}{m^2}$$

Numbers for this build: [`generated/optics.md`](generated/optics.md).

## 6. HDR from 8-bit UVC frames ([R5])

$$g(Z_{ij}) = \ln E_i + \ln\Delta t_j$$

## 7. Repeatability from the fixed camera

The lamp's mirror image shifts $s$ pixels (pitch $p_{px}$, path $P$, lens $f$, light radius $D_L$):

$$\Delta\theta_L = \frac{s\,p_{px}\,P}{f\,D_L}$$

About 8 px per 0.1° for this build, so the camera can verify the 0.1° target (as in Fig. 12 of [R1]).
