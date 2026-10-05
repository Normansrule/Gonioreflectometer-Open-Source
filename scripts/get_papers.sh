#!/usr/bin/env bash
# Download the gonioreflectometer PDFs listed in papers/papers.tsv.
# Open-licence / public-domain → papers/open/ (committed). Others → papers/personal/ (git-ignored).
# SPDX-License-Identifier: GPL-3.0-or-later
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p papers/open papers/personal
fail=()
while IFS=$'\t' read -r id lic file url; do
  [ "$id" = id ] && continue
  dir=papers/personal; [ "$lic" != personal ] && dir=papers/open
  out="$dir/$file"
  [ -s "$out" ] && { echo "have  $id"; continue; }
  if curl -fsSL --retry 2 -A "Mozilla/5.0" -o "$out" "$url" && head -c 4 "$out" | grep -q '%PDF'; then
    echo "got   $id → $out"
  else
    rm -f "$out"; fail+=("$id $url")
  fi
done < papers/papers.tsv
if [ ${#fail[@]} -gt 0 ]; then
  echo; echo "Open these in a browser and save into papers/ with the name from papers.tsv:"
  printf '  %s\n' "${fail[@]}"
fi
