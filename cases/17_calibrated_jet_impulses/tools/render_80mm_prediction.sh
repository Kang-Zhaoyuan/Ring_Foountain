#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
case_dir="$root/cases/17_calibrated_jet_impulses"
run_dir=${1:?usage: render_80mm_prediction.sh RUN_DIR [OUTPUT_DIR]}
output_dir=${2:-$case_dir/review/80mm_7800}
params="$run_dir/effective_parameters.tsv"
[[ -f "$params" ]] || { echo "missing $params" >&2; exit 2; }

value() {
  awk -F '\t' -v key="$1" '$1 == key {print $2; exit}' "$params"
}

ri=$(value Ri)
ro=$(value Ro)
thickness=$(value thickness)
impact=$(value impact_speed)
terminal=$(value terminal_speed)
decay=$(value trajectory_decay_rate)
mkdir -p "$output_dir"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

times=(00000 01750 03000 05250 09600 14350 16000)
labels=(0.0 17.5 30.0 52.5 96.0 143.5 160.0)
panels=()
for idx in "${!times[@]}"; do
  tag=${times[$idx]}
  time_file="00.${tag}"
  t=$(awk -v ms="${labels[$idx]}" 'BEGIN {printf "%.9f", ms/1000.}')
  surface=$(awk -v t="$t" -v h="$thickness" -v u0="$impact" -v ut="$terminal" -v k="$decay" 'BEGIN {printf "%.12g", -h/2. + ut*t + (u0-ut)*(1.-exp(-k*t))/k}')
  input="$run_dir/interface-${time_file}.dat"
  [[ -f "$input" ]] || { echo "missing $input" >&2; exit 2; }
  panel="$tmp/panel_${tag}.png"
  gnuplot -e "input='$input';output='$panel';surface=$surface;ri=$ri;ro=$ro;thickness=$thickness;title_text='${labels[$idx]} ms after contact'" "$case_dir/tools/prediction_panel.gp"
  panels+=("$panel")
done

magick montage "${panels[@]}" -tile 4x2 -geometry 700x760+8+8 -background white "$output_dir/01_cfd_timeline.png"
magick "$output_dir/01_cfd_timeline.png" -gravity south -splice 0x130 -pointsize 27 -fill '#111111' -annotate +0+54 'Case 17 L7 predictive extrapolation: Ri 5.05 mm | Ro 20.07 mm | thickness 2.86 mm | density 7.8 g/cm^3 | vacuum release 80 mm' "$output_dir/01_cfd_timeline.png"

cp "$tmp/panel_05250.png" "$output_dir/02_detail_52p5ms.png"
magick "$output_dir/02_detail_52p5ms.png" -gravity south -splice 0x135 -pointsize 20 -fill '#111111' -annotate +0+58 'Resolved VOF/PLIC only.\nThe calibrated visible-tip ODE is not a resolved liquid filament.' "$output_dir/02_detail_52p5ms.png"

identify "$output_dir/01_cfd_timeline.png" "$output_dir/02_detail_52p5ms.png"
