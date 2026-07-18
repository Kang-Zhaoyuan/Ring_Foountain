#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
case_dir="$root/cases/16_impact_driven_through_hole_jet"
baseline=${1:?baseline run directory required}
contact=${2:?contact run directory required}
instant=${3:?instant run directory required}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

times=(01750 03000 04200 05250 06500 07750)
frames=(0335 0360 0384 0405 0430 0455)
surfaces=(0.0171896 0.0275015 0.0366340 0.04437645 0.0534701683 0.0625092048)
labels=(17.5 30.0 42.0 52.5 65.0 77.5)
for idx in "${!times[@]}"; do
  tag=${times[$idx]}
  time_file="00.${tag}"
  gnuplot -e "input='$baseline/interface-${time_file}.dat';output='$tmp/base_${tag}.png';surface=${surfaces[$idx]};title_text='Case 15 physics: ${labels[$idx]} ms'" "$case_dir/tools/interface_panel.gp"
  gnuplot -e "input='$instant/interface-${time_file}.dat';output='$tmp/instant_${tag}.png';surface=${surfaces[$idx]};title_text='Case 16 instant-inner: ${labels[$idx]} ms'" "$case_dir/tools/interface_panel.gp"
done
gnuplot -e "input='$contact/interface-00.05250.dat';output='$tmp/contact_05250.png';surface=0.04437645;title_text='Case 16 contact-driven: 52.5 ms'" "$case_dir/tools/interface_panel.gp"

exp_callout="$root/cases/12_video_26p15g_calibration/experiment_frames/callouts/03_first_jet_and_open_cavity_frame_0405.jpg"
magick "$exp_callout" -resize 720x720 "$tmp/experiment.png"
magick montage "$tmp/experiment.png" "$tmp/base_05250.png" "$tmp/instant_05250.png" -tile 3x1 -geometry 720x720+12+12 -background white "$case_dir/review/00_visual_verdict.png"
magick "$case_dir/review/00_visual_verdict.png" -gravity south -splice 0x110 -pointsize 28 -fill '#111111' -annotate +0+48 'NOT IMPROVED: inner ghost-cell wetting changes state bookkeeping, but not pressure, flux, or the continuous jet.' "$case_dir/review/00_visual_verdict.png"

rows=()
for idx in "${!times[@]}"; do
  frame=${frames[$idx]}
  exp="$root/cases/12_video_26p15g_calibration/experiment_frames/annotated/frame_${frame}_annotated.jpg"
  magick "$exp" -resize 380x380 "$tmp/exp_${times[$idx]}.png"
  rows+=("$tmp/exp_${times[$idx]}.png")
done
for tag in "${times[@]}"; do rows+=("$tmp/instant_${tag}.png"); done
for tag in "${times[@]}"; do rows+=("$tmp/base_${tag}.png"); done
magick montage "${rows[@]}" -tile 6x3 -geometry 380x500+6+6 -background white "$case_dir/review/01_timeline_comparison.png"

magick montage "$tmp/experiment.png" "$tmp/base_05250.png" "$tmp/instant_05250.png" -tile 3x1 -geometry 720x720+12+12 -background white "$case_dir/review/02_frame405_height_comparison.png"
magick "$case_dir/review/02_frame405_height_comparison.png" -gravity south -splice 0x120 -pointsize 30 -fill '#111111' -annotate +0+54 'Experiment 105.80 mm | baseline H_PLIC 7.152 mm | Case 16 H_PLIC 7.152 mm | remaining error 98.648 mm' "$case_dir/review/02_frame405_height_comparison.png"

gnuplot -e "base_flux='$baseline/aperture_flux.tsv';candidate_flux='$instant/aperture_flux.tsv';base_pressure='$baseline/pressure_budget.tsv';candidate_pressure='$instant/pressure_budget.tsv';output='$case_dir/review/03_pressure_velocity_mechanism.png'" "$case_dir/tools/mechanism.gp"
magick "$case_dir/review/03_pressure_velocity_mechanism.png" -gravity south -splice 0x100 -pointsize 26 -fill '#111111' -annotate +0+42 'Curves overlap: earlier inner ghost wetting did not strengthen pressure focusing or aperture flux.' "$case_dir/review/03_pressure_velocity_mechanism.png"

magick "$tmp/base_05250.png" -gravity east -splice 760x0 -pointsize 34 -fill '#111111' -annotate +380+80 'L8 NOT RUN\n\nL7 candidate failed entry gate:\nheight improvement = 1.00x\nerror reduction = 0%\n\nNo grid-stability claim.' "$case_dir/review/04_l7_l8_comparison.png"

magick montage "$tmp/base_05250.png" "$tmp/contact_05250.png" "$tmp/instant_05250.png" -tile 3x1 -geometry 650x720+10+10 -background white "$case_dir/review/05_rejected_candidates.png"
magick "$case_dir/review/05_rejected_candidates.png" -gravity south -splice 0x170 -pointsize 24 -fill '#111111' -annotate +0+70 'legacy: baseline only | contact-driven: identical flow | instant-inner upper bound: identical pressure/flux/jet; rejected. Pre-impact gaps not run after no inner-wetting mechanism survived.' "$case_dir/review/05_rejected_candidates.png"

for file in "$case_dir"/review/0*.png; do identify "$file"; done
