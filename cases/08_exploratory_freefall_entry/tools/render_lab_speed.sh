#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "usage: $0 RUN_DIRECTORY OUTPUT_MP4 [SPEED_CAP_MPS]" >&2
  exit 2
fi

run_dir=$(readlink -f "$1")
output_mp4=$(readlink -m "$2")
speed_cap=${3:-10}
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
plot_script="$script_dir/render_lab_speed.gp"

for command in gnuplot ffmpeg awk; do
  command -v "$command" >/dev/null || {
    echo "required command not found: $command" >&2
    exit 1
  }
done

for required in fields.tsv snapshots.tsv; do
  [[ -s "$run_dir/$required" ]] || {
    echo "missing run index: $run_dir/$required" >&2
    exit 1
  }
done

mkdir -p "$(dirname "$output_mp4")"
frame_dir=$(mktemp -d "${TMPDIR:-/tmp}/ring-fountain-frames.XXXXXX")
trap 'rm -rf "$frame_dir"' EXIT

frame=0
while IFS=$'\t' read -r time_s field_name drop_m speed_down ring_center_m _; do
  [[ $time_s == "time_s" ]] && continue

  field_file="$run_dir/$field_name"
  time_us=$(awk -v t="$time_s" 'BEGIN {printf "%09d", t*1e6 + 0.5}')
  interface_file="$run_dir/interface-${time_us}us.dat"
  [[ -s "$field_file" && -s "$interface_file" ]] || {
    echo "missing frame input at t=$time_s: $field_file or $interface_file" >&2
    exit 1
  }

  output_png=$(printf '%s/frame-%06d.png' "$frame_dir" "$frame")
  gnuplot -e "field_file='$field_file'; \
interface_file='$interface_file'; \
output_file='$output_png'; \
time_ms=$time_s*1000; \
drop_mm=$drop_m*1000; \
speed_down=$speed_down; \
ring_center_mm=$ring_center_m*1000; \
speed_cap=$speed_cap" "$plot_script"

  frame=$((frame + 1))
done < "$run_dir/fields.tsv"

[[ $frame -gt 0 ]] || {
  echo "no frames rendered" >&2
  exit 1
}

ffmpeg -hide_banner -loglevel error -y \
  -framerate 25 -i "$frame_dir/frame-%06d.png" \
  -vf "format=yuv420p,tpad=stop_mode=clone:stop_duration=1" \
  -c:v libx264 -crf 20 -preset medium -movflags +faststart "$output_mp4"

printf 'rendered %d frames to %s\n' "$frame" "$output_mp4"
