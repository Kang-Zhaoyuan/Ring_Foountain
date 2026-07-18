# Audit tools

These sources were written during the independent Bursting-Bubble audit. They
do not contain the upstream solver implementation, and no executable is
tracked here.

## Rebuild tables and figures

Create an isolated environment with the optional versions in
`requirements.txt`, then run from the Ring Fountain root:

```sh
python cases/14_comphy_bursting_bubble_reproduction/tools/analyze_results.py
```

The script reads the migrated `tables/case*_*.tsv` and PLIC streams and writes
case-local summary tables and figures. It does not need the external clone.

## Re-extract dumps

Dump restoration requires the pinned independent workspace and its isolated
Basilisk. Compile the helper outside the repository or to a temporary path:

```sh
source /home/kqdx/basilisk_work/reproductions/bursting_bubble_20260718/upstream/.project_config
cd /home/kqdx/basilisk_work/ring_fountain/cases/14_comphy_bursting_bubble_reproduction/tools
qcc -O2 -Wall -disable-dimensions audit_snapshot.c -o /tmp/bursting_audit_snapshot -lm
```

`extract_case_metrics.sh` expects a helper named `audit_snapshot` beside the
script, so for a full refresh use a temporary working copy of the tools or a
temporary symlink; do not commit the executable. The third argument can select
a different independent reproduction root.

The pinned isolated qcc is the scientific reproduction authority. Ring
Fountain's main qcc may be used only for a separate compatibility check.
