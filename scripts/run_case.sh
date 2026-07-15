#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
case_dir=${1:?usage: run_case.sh CASE_DIR [PROGRAM_ARGS...]}
shift || true
case_dir=$(cd "$case_dir" && pwd)
name=$(basename "$case_dir")
stamp=$(date -u +%Y%m%d_%H%M%S)
run_dir="$root/runs/${stamp}_${name}"
mkdir -p "$run_dir"
if [[ -f "$case_dir/source_run.c" ]]; then
  source="$case_dir/source_run.c"
else
  source=$(find "$case_dir" -maxdepth 1 -type f \( -name 'main.c' -o -name '*.c' \) | sort | head -n 1)
fi
[[ -n "$source" ]] || { echo "no C source in $case_dir" >&2; exit 2; }
program="$run_dir/case.exe"
source_name=$(basename "$source")
qcc_flags=${QCC_FLAGS:-}
cp "$source" "$run_dir/source.c"
sha256sum "$source" > "$run_dir/source.sha256"
printf 'root=%s\ncase=%s\nrun=%s\n' "$root" "$case_dir" "$run_dir" > "$run_dir/parameters.txt"
if git -C "$root" rev-parse HEAD > "$run_dir/git_commit.txt" 2>/dev/null; then :; else echo 'unavailable (git HEAD not resolved)' > "$run_dir/git_commit.txt"; fi
if (cd /home/kqdx/basilisk && darcs changes --last=1) > "$run_dir/basilisk_darcs_patch.txt" 2>&1; then :; else echo 'darcs metadata unavailable' > "$run_dir/basilisk_darcs_patch.txt"; fi
printf 'cd %q && %q ' "$case_dir" /home/kqdx/basilisk/src/qcc > "$run_dir/compile_command.txt"
printf '%q ' -O2 -Wall $qcc_flags "$source_name" -o "$program" -lm >> "$run_dir/compile_command.txt"
printf '\n' >> "$run_dir/compile_command.txt"
if (cd "$case_dir" && /home/kqdx/basilisk/src/qcc -O2 -Wall $qcc_flags "$source_name" -o "$program" -lm) > "$run_dir/compile.log" 2>&1; then
  printf '%q ' "$program" "$@" > "$run_dir/run_command.txt"
  printf '\n' >> "$run_dir/run_command.txt"
  set +e
  (cd "$case_dir" && "$program" "$@") > "$run_dir/stdout.log" 2> "$run_dir/stderr.log"
  status=$?
  set -e
else
  status=125
  : > "$run_dir/run_command.txt"
  : > "$run_dir/stdout.log"
  : > "$run_dir/stderr.log"
fi
for artifact in final.dump solid_facets.dat cs.ppm ring_geometry.tsv; do
  if [[ -f "$case_dir/$artifact" ]]; then
    cp "$case_dir/$artifact" "$run_dir/$artifact"
  fi
done
printf 'exit_code=%s\nrun_dir=%s\n' "$status" "$run_dir" | tee "$run_dir/validation_summary.md"
exit "$status"
