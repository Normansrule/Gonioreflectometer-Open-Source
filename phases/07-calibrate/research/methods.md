# Methods

| Step | Method | Refs |
|---|---|---|
| HDR | exposure bracket → camera response → linear radiance | [R5][R49] |
| Angles | mirror peak position per arm angle | [R2] |
| Light direction | highlights on two chrome balls | [S13] |
| Brightness | PTFE ≈ Lambertian below 60° | [R2] |
| Check | swap light and camera (reciprocity) | [R2] |
| Fit | Lambert + GGX + Schlick, energy ≤ 1 | [R6][R7] |
| Export | metallic-roughness (roughness = √α) | — |

Equations: [theory.md](../../00-plan/research/theory.md).
