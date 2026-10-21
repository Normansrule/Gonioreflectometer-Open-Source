#!/usr/bin/env bash
# Copy wiki/*.md to the GitHub wiki (a separate git repo: <repo>.wiki.git).
# Once: on GitHub open the repo's Wiki tab and create the first page (GitHub creates the wiki repo then).
# Private repos need a plan with wikis (GitHub Pro / Team); otherwise read the pages in wiki/ in the repo.
#   bash scripts/publish_wiki.sh            # uses the origin remote
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
origin=$(git remote get-url origin)
wiki_url="${origin%.git}.wiki.git"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git clone -q "$wiki_url" "$tmp/wiki"
find "$tmp/wiki" -maxdepth 1 -name '*.md' -delete
for f in wiki/*.md; do
  # wiki links drop the .md: (Page.md) -> (Page), (Page.md#x) -> (Page#x)
  sed -E 's/\]\(([A-Za-z0-9_-]+)\.md(#[^)]*)?\)/](\1\2)/g' "$f" > "$tmp/wiki/$(basename "$f")"
done
cd "$tmp/wiki"
git add -A
git commit -q -m "Sync wiki from main ($(git -C "$OLDPWD" rev-parse --short HEAD))" || { echo "wiki: no changes"; exit 0; }
git push -q
echo "wiki published: ${origin%.git}/wiki"
