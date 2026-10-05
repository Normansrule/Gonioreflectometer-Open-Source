#!/usr/bin/env bash
# Get the PDFs in papers/papers.tsv. Open licence / public domain -> papers/open/ (committed);
# others -> papers/personal/ (git-ignored).
#   bash scripts/get_papers.sh                                     download what the sites allow
#   bash scripts/get_papers.sh --from /mnt/c/Users/aleks/Downloads    pick up PDFs you saved in a browser
# SPDX-License-Identifier: GPL-3.0-or-later
set -uo pipefail
cd "$(dirname "$0")/.."
FROM=""; [ "${1:-}" = "--from" ] && FROM=${2:?folder}
mkdir -p papers/open papers/personal
fail=()
while IFS=$'\t' read -r id lic file url bname; do
  [ "$id" = id ] && continue
  dir=papers/personal; [ "$lic" != personal ] && dir=papers/open
  out="$dir/$file"
  [ -s "$out" ] && { echo "have  $id"; continue; }
  if [ -n "$FROM" ]; then
    for cand in "$FROM/$bname" "$FROM/$file"; do
      if [ -s "$cand" ] && head -c 4 "$cand" | grep -q '%PDF'; then cp "$cand" "$out"; chmod 644 "$out"; echo "took  $id ← $cand"; continue 2; fi
    done
    fail+=("$id  $url  (save as $bname)"); continue
  fi
  if curl -fsSL --retry 1 -A "Mozilla/5.0 (X11; Linux x86_64)" -o "$out" "$url" 2>/dev/null && head -c 4 "$out" | grep -q '%PDF'; then
    echo "got   $id"
  else
    rm -f "$out"; fail+=("$id  $url")
  fi
done < papers/papers.tsv
if [ ${#fail[@]} -gt 0 ]; then
  echo; echo "Blocked for scripts (${#fail[@]}). Open each in your browser, save to Downloads, then:"
  echo "  bash scripts/get_papers.sh --from /mnt/c/Users/${USER:-you}/Downloads"
  printf '  %s\n' "${fail[@]}"
fi
