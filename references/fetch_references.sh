#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
vendor="$root/references/vendor"
lock="$root/references/references.lock"
mkdir -p "$vendor"
repos=(
  "DropImpactViscousPool|https://github.com/rcsc-group/DropImpactViscousPool.git"
  "phd_basilisk|https://github.com/AndreWeiner/phd_basilisk.git"
  "Drop-Impact|https://github.com/comphy-lab/Drop-Impact.git"
)
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
for item in "${repos[@]}"; do
  IFS='|' read -r name url <<< "$item"
  dest="$vendor/$name"
  if [[ -e "$dest/.git" ]]; then
    remote=$(git -C "$dest" remote get-url origin)
    [[ "$remote" == "$url" ]] || { echo "remote mismatch: $dest" >&2; exit 2; }
    [[ -z "$(git -C "$dest" status --short)" ]] || { echo "dirty vendor repo: $dest" >&2; exit 3; }
    git -C "$dest" fetch --prune origin
  else
    git clone "$url" "$dest"
  fi
  commit=$(git -C "$dest" rev-parse HEAD)
  branch=$(git -C "$dest" branch --show-current)
  date=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  license_file=$(find "$dest" -maxdepth 1 -type f \( -iname 'license*' -o -iname 'copying*' \) | sort | head -n 1)
  license=$(basename "${license_file:-UNKNOWN}")
  license_sha256=$(sha256sum "$license_file" 2>/dev/null | awk '{print $1}' || true)
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$url" "$commit" "$branch" "$date" "${license:-UNKNOWN}" "${license_sha256:-UNKNOWN}" "vendor/$name" >> "$tmp"
done
{
  printf '# name\turl\tcommit\tbranch\tfetched_utc\tlicense\tlicense_sha256\tpath\n'
  sort "$tmp"
} > "$lock"
