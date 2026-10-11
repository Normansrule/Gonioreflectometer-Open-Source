#!/usr/bin/env bash
# Replay the GitHub checks before pushing: a clean clone of HEAD, a fresh Python venv with only the CI packages,
# then the ci job (check, test, build without pandoc) and the docs job (build, paper, export).
#   bash scripts/ci_local.sh          (or: make ci)       commit first: it tests HEAD, not uncommitted edits
# SPDX-License-Identifier: GPL-3.0-or-later
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
PYBIN=$(command -v python3.12 || command -v python3)
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
git clone -q . "$T/repo" && cd "$T/repo"
"$PYBIN" -m venv "$T/venv" && "$T/venv/bin/pip" install -q -e "./software[dev]" pyyaml numpy openpyxl pillow
fail=0
step() { local name=$1; shift; if "$@" > "$T/out" 2>&1; then echo "PASS $name"; else echo "FAIL $name"; tail -n 20 "$T/out"; fail=1; fi; }
# PATH without pandoc: folders holding it are mirrored (every other program symlinked) into $T/nopandoc-N
nopandoc() {
  local p="" d i=0
  while read -r d; do
    if [ -x "$d/pandoc" ]; then
      i=$((i + 1)); mkdir -p "$T/nopandoc-$i"
      for f in "$d"/*; do [ "$(basename "$f")" = pandoc ] || ln -sf "$f" "$T/nopandoc-$i/"; done
      d="$T/nopandoc-$i"
    fi
    p="${p:+$p:}$d"
  done < <(echo "$PATH" | tr ':' '\n')
  PATH="$p" "$@"
}
export PATH="$T/venv/bin:$PATH"   # venv python3 first (Makefile PY falls back to python3)
echo "== ci job ($("$PYBIN" --version), no pandoc)"
step "make check test" nopandoc make check test
step "make build" nopandoc make build
git diff --quiet || { echo "WARN generated files differ after make build:"; git diff --stat | tail -5; }
git checkout -q .
echo "== docs job"
for t in build paper export; do step "make $t" make "$t"; done
changed=$(git status --short | wc -l)
[ "$changed" -eq 0 ] && echo "PASS docs output identical to the commit" || { echo "NOTE docs job would commit $changed file(s) (normal after a source change):"; git status --short | head -10; }
exit $fail
