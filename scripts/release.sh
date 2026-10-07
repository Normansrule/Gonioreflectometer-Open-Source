#!/usr/bin/env bash
# Tag a finished stage and attach every STEP + STL as a zip:  bash scripts/release.sh 06
# Stage 06 -> tag v0.6. Go back to it any time: git checkout v0.6   (return: git checkout main)
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
cd "$(dirname "$0")/.."
N="${1:?usage: bash scripts/release.sh NN   (finished stage number, e.g. 06)}"
DIR=$(ls -d phases/"$N"-* 2>/dev/null | head -1 || true)
[ -n "$DIR" ] || { echo "no folder phases/$N-*"; exit 1; }
make -s all
[ -z "$(git status --porcelain)" ] || { echo "uncommitted changes: run  make publish m=\"...\"  first"; exit 1; }
TAG="v0.$((10#$N))"
ZIP="opengonio-$TAG-3d.zip"
.venv/bin/python - "$ZIP" <<'PY'
import sys, zipfile, pathlib
with zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(pathlib.Path("phases").glob("*/3d/*")):
        if f.suffix.lower() in (".step", ".stl", ".svg", ".md") and "vendor" not in f.parts:
            z.write(f)
    z.write("phases/03-frame/placement-template.svg")
    print(sys.argv[1], len(z.namelist()), "files")
PY
git tag -a "$TAG" -m "Stage $(basename "$DIR") done"
git push origin "$TAG"
if command -v gh >/dev/null; then
  gh release create "$TAG" "$ZIP" --title "$TAG · $(basename "$DIR") done" \
    --notes "Stage $(basename "$DIR") passed its Verify steps. Results: $DIR/design.md. 3D files for every part attached."
else
  echo "tag pushed; gh not installed, so upload $ZIP on GitHub → Releases → $TAG"
fi
rm -f "$ZIP"
