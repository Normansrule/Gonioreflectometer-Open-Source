# Pipeline

```bash
opengonio scan demo --out demo            # offline test: synthetic sphere
opengonio scan run --background --out s   # empty platter
opengonio scan run --out s                # object
cd s && bash run_colmap.sh                # mesh: dense/meshed-poisson.ply (NVIDIA GPU)
```

No NVIDIA GPU: Meshroom [S10] or OpenMVS [S17] on `s/images`, or the visual hull. Output PLY / OBJ / glTF → Blender [S16].
