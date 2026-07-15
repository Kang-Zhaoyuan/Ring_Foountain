#!/usr/bin/env bash
set -euo pipefail
case_dir=${1:?usage: validate_case.sh CASE_DIR}
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
latest=$(find "$root/runs" -maxdepth 1 -mindepth 1 -type d -name "*_$(basename "$case_dir")" | sort | tail -n 1)
[[ -n "$latest" ]] || { echo "no run found for $case_dir" >&2; exit 2; }
if rg -n -i '\b(nan|inf|sigfpe|segmentation fault)\b' "$latest"; then
  echo "validation: FAIL (invalid numerical marker)"
  exit 1
fi
echo "validation: PASS (no invalid numerical marker in $latest)"

