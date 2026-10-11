#!/usr/bin/env bash
# Publish an update to the existing private repo. Safe to re-run.
#   bash scripts/update.sh "message"                 commit your own edits, push, sync milestones/issues
#   bash scripts/update.sh "message" path/to.zip     first copy in a new zip (keeps your git history)
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
cd "$(dirname "$0")/.."
MSG=${1:-update}
ZIP=${2:-}

git pull -q --rebase --autostash 2>/dev/null || echo "note: could not pull (offline, or first push)"   # get PARTS.md edits made on GitHub
FIRST_PARTS=""; [ -f PARTS.md ] || FIRST_PARTS=1

if [ -n "$ZIP" ]; then
  TMP=$(mktemp -d)
  OLD=$(mktemp -d); cp -r phases "$OLD/" 2>/dev/null || true          # your old bom.csv (Own / Paid) for the first PARTS.md
  unzip -q "$ZIP" -d "$TMP"
  SRC=$(dirname "$(find "$TMP" -maxdepth 3 -name phases.yml -path '*/.github/*' | head -1)")/..
  chmod -R u+w "$TMP"
  rm -rf "$SRC/.git"
  mkdir -p papers/personal
  cp -n "$SRC"/papers/personal/* papers/personal/ 2>/dev/null || true   # never overwrite your PDFs
  rm -rf "$SRC/papers/personal" "$SRC/papers/open"
  [ -f PARTS.md ] && rm -f "$SRC/PARTS.md"                            # your parts decisions always win
  git ls-files -z | xargs -0 rm -f          # drop old tracked files (removed ones stay removed)
  cp -a "$SRC/." ./                         # your .git, .venv and papers stay as they are
  rm -rf "$TMP"
  echo "copied $ZIP"
  if [ -n "$FIRST_PARTS" ] && [ -d "$OLD/phases" ]; then rm -f PARTS.md; .venv/bin/python tools/parts_doc.py --seed "$OLD/phases" 2>/dev/null || true; fi
  rm -rf "$OLD"
fi

.venv/bin/python -c "import yaml, numpy, opengonio" 2>/dev/null || make setup
REPO=$(git remote get-url origin | sed -E 's#\.git$##; s#.*[:/]([^/:]+/[^/]+)$#\1#')
if [ -z "${NO_GITHUB:-}" ]; then        # closed issues -> .github/progress.json (ticks + figures)
  .venv/bin/python tools/roadmap.py --progress --repo "$REPO" >/dev/null 2>&1 || echo "note: progress not refreshed (offline?)"
fi
make -s build >/dev/null 2>&1 || echo "note: make build failed (run: make setup)"   # keep generated files in step
make -s paper >/dev/null 2>&1 || echo "note: paper not built (needs latexmk + biber: see paper/README.md)"   # commit a fresh PDF
git add -A
git diff --cached --quiet && echo "nothing new to commit" || git commit -qm "$MSG"
if [ -z "${NO_CI:-}" ]; then                                         # same checks as GitHub, on a clean clone
  bash scripts/ci_local.sh || { echo "checks failed: not pushed. Fix and re-run, or NO_CI=1 bash scripts/update.sh \"$MSG\" to push anyway"; exit 1; }
fi
git push -q origin HEAD
bash scripts/publish_wiki.sh 2>/dev/null || echo "note: wiki not published (create the first wiki page on GitHub once)"
echo "pushed: $(git log -1 --format='%h %s')"

if [ -z "${NO_GITHUB:-}" ]; then
  .venv/bin/python tools/roadmap.py --github --repo "$REPO" --prune   # milestones + issues match .github/phases.yml
  echo "https://github.com/$REPO"
fi
