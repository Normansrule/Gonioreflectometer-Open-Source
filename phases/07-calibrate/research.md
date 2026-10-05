# 07 · Research

## Methods

| Step | Method | Refs |
|---|---|---|
| HDR | exposure bracket → camera response → linear radiance | [R5][V19][V20][R49] |
| Angles | mirror peak position per arm angle | [R2] |
| Light direction | highlights on two chrome balls | [S13] |
| Brightness | PTFE ≈ Lambertian below 60° | [R2][N30][N34] |
| Check | swap light and camera (reciprocity) | [R2] |
| Fit | Lambert + GGX + Schlick, energy ≤ 1 | [R6][R7][T17][G16] |
| Intrinsics | ChArUco, Zhang's method | [V1][V7][S12] |
| Export | metallic-roughness (roughness = √α) | [T35][T40][T46][T47] |

Equations: [theory.md](../00-plan/research.md).
