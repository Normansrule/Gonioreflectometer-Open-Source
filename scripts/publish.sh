#!/usr/bin/env bash
# Private repo + push + one milestone per phase, one issue per step. Safe to re-run.
# Optional: OWNER=<github user>  REMOTE=<git URL, e.g. an SSH host alias>  bash scripts/publish.sh
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
gh auth status >/dev/null || { echo "Run: gh auth login --web --scopes workflow"; exit 1; }
cd "$(dirname "$0")/.."
NAME=Gonioreflectometer-Open-Source
OWNER=${OWNER:-$(gh api user --jq .login)}
REMOTE=${REMOTE:-https://github.com/$OWNER/$NAME.git}

[ -d .git ] || git init -q
git config user.name  >/dev/null || git config user.name  "$(gh api user --jq '.name // .login')"
git config user.email >/dev/null || git config user.email "$(gh api user --jq .id)+${OWNER}@users.noreply.github.com"
git add -A
git diff --cached --quiet || git commit -qm "OpenGonio update"
git branch -M main

if ! gh repo view "$OWNER/$NAME" >/dev/null 2>&1; then
  gh repo create "$OWNER/$NAME" --private \
    --description "OpenGonio: low-cost open-source multispectral gonioreflectometer (laptop-controlled)"
fi
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
git push -u origin main

python3 -m venv .venv
. .venv/bin/activate
pip install -q pyyaml numpy pytest
python3 tools/roadmap.py --github --repo "$OWNER/$NAME"

if gh api "repos/$OWNER/$NAME/pages" >/dev/null 2>&1 \
   || gh api -X POST "repos/$OWNER/$NAME/pages" -f "source[branch]=main" -f "source[path]=/docs" >/dev/null 2>&1; then
  echo "Pages: https://$OWNER.github.io/$NAME/"
else
  echo "Pages not enabled (private repos need a paid plan). Open docs/index.html locally."
fi

gh repo edit "$OWNER/$NAME" --add-topic gonioreflectometer --add-topic brdf --add-topic open-hardware \
  --add-topic fluidnc --add-topic multispectral >/dev/null
pip install -q -e "./software[dev]" && python -m pytest -q software
echo "Done: https://github.com/$OWNER/$NAME  (milestones: /milestones)"
