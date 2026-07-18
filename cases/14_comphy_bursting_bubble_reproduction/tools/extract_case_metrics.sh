#!/bin/bash
set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "usage: $0 CASE_NO OUTPUT_PREFIX [INDEPENDENT_REPRODUCTION_ROOT]" >&2
  exit 2
fi

case_root=$(cd "$(dirname "$0")/.." && pwd)
root=${3:-/home/kqdx/basilisk_work/reproductions/bursting_bubble_20260718}
case_no=$1
prefix=$2
case_dir="$root/upstream/simulationCases/$case_no"
audit="$case_root/tools/audit_snapshot"
get_base="$root/upstream/postProcess/getBase"
get_foot="$root/upstream/postProcess/getJetFoot"

test -x "$audit" && test -x "$get_base" && test -x "$get_foot"
test -d "$case_dir/intermediate"

metrics_out="${prefix}_snapshot_metrics.tsv"
base_out="${prefix}_base.tsv"
foot_out="${prefix}_jetfoot.tsv"
printf 'case\ttime\tvolume\tke\tumax\tz_umax\tr_umax\tleaves\tdelta_min\tn_liquid\tz_all\tz_main\tz_center\n' > "$metrics_out"
printf 'case\ttime\tz_base\tr_base\tz_tip\tr_tip\tn_out\n' > "$base_out"
printf 'case\ttime\tz_low\tr_low\tz_maxk\tr_maxk\tqjet_low\tql_low\tqjet_maxk\tql_maxk\tz_jet\n' > "$foot_out"

while IFS= read -r snapshot; do
  # The upstream helpers use an 80-byte filename buffer. Run from the
  # reproduction root and pass a short relative path to avoid overflow.
  snapshot_rel=${snapshot#"$root"/}
  (cd "$root" && "$audit" "$snapshot_rel") | tail -n 1 | awk -v c="$case_no" 'BEGIN{OFS="\t"}{print c,$0}' >> "$metrics_out"
  (cd "$root" && "$get_base" "$snapshot_rel") 2>&1 >/dev/null | awk -v c="$case_no" 'BEGIN{OFS="\t"}{print c,$1,$2,$3,$4,$5,$6}' >> "$base_out"
  (cd "$root" && "$get_foot" "$snapshot_rel") 2>&1 >/dev/null | awk -v c="$case_no" 'BEGIN{OFS="\t"}{print c,$1,$2,$3,$4,$5,$6,$7,$8,$9,$10}' >> "$foot_out"
done < <(find "$case_dir/intermediate" -maxdepth 1 -type f -name 'snapshot-*' | sort -V)
