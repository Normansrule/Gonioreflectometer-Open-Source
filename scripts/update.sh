#!/usr/bin/env bash
# Publish an update to the existing private repo. Safe to re-run.
#   bash scripts/update.sh "message"                 commit your own edits, push, sync milestones/issues
#   bash scripts/update.sh "message" path/to.zip     first copy in a new zip (keeps your git history)
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
cd "$(dirname "$0")/.."
MSG=${1:-update}
ZIP=${2:-}

if [ -n "$ZIP" ]; then
  TMP=$(mktemp -d)
  unzip -q "$ZIP" -d "$TMP"
  SRC=$(dirname "$(find "$TMP" -maxdepth 3 -name phases.yml -path '*/.github/*' | head -1)")/..
  rm -rf "$SRC/.git"
  git ls-files -z | xargs -0 rm -f          # drop old tracked files (removed ones stay removed)
  cp -a "$SRC/." ./                         # your .git, .venv and papers stay as they are
  rm -rf "$TMP"
  echo "copied $ZIP"
fi

git add -A
git diff --cached --quiet && echo "nothing new to commit" || git commit -qm "$MSG"
git push -q origin HEAD
echo "pushed: $(git log -1 --format='%h %s')"

if [ -z "${NO_GITHUB:-}" ]; then
  REPO=$(git remote get-url origin | sed -E 's#\.git$##; s#.*[:/]([^/:]+/[^/]+)$#\1#')
  [ -d .venv ] || python3 -m venv .venv
  . .venv/bin/activate && pip install -q pyyaml
  python3 tools/roadmap.py --github --repo "$REPO"     # milestones + issues match .github/phases.yml
  echo "https://github.com/$REPO"
fi
