#!/usr/bin/env bash
# Create the PRIVATE GitHub repo, push, and load milestones + checklist issues.
# Run from the repository root on a machine where `gh auth status` shows you logged in.
#   bash scripts/create_private_repo.sh                # uses gh's logged-in account
#   OWNER=Normansrule bash scripts/create_private_repo.sh
set -euo pipefail
NAME="Gonioreflectometer-Open-Source"
OWNER="${OWNER:-$(gh api user --jq .login)}"

gh auth status >/dev/null
if ! gh repo view "$OWNER/$NAME" >/dev/null 2>&1; then
  gh repo create "$OWNER/$NAME" --private \
    --description "OpenGantry Lite: a \$500 open-source gonioreflectometer that grows into a 3D scanner" \
    --source . --remote origin --push
else
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$OWNER/$NAME.git"
  git push -u origin main
fi
python3 -m pip install --quiet pyyaml || python3 -m pip install --quiet --break-system-packages pyyaml
python3 tools/roadmap.py --github --repo "$OWNER/$NAME"
gh repo edit "$OWNER/$NAME" --add-topic gonioreflectometer --add-topic brdf --add-topic open-hardware \
  --add-topic klipper --add-topic raspberry-pi --add-topic photogrammetry
echo "Done: https://github.com/$OWNER/$NAME (private) - milestones: https://github.com/$OWNER/$NAME/milestones"
