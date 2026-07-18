# Audit tools

These two files were created during the independent 2026-07-18 audit. They are
not copied from CoMPhy Drop-Impact and do not contain its solver implementation.
No executable is tracked.

`snapshot_metrics.c` restores a Basilisk dump read-only and reports the
axisymmetric VOF volume, a kinetic-energy proxy, maximum velocity, leaf-cell
count, finest cell width, VOF range, and invalid-value count. It must be built
against the isolated Basilisk installed inside the independent reproduction
when regenerating the scientific audit:

```sh
source /home/kqdx/basilisk_work/reproductions/drop_impact_20260718/upstream/.project_config
cd /home/kqdx/basilisk_work/ring_fountain/cases/13_comphy_drop_impact_reproduction/tools
qcc -disable-dimensions \
  -I/home/kqdx/basilisk_work/reproductions/drop_impact_20260718/upstream/src-local \
  -O2 -Wall snapshot_metrics.c -o /tmp/drop-impact-snapshot-metrics -lm
```

The include path must refer to the independent Drop-Impact clone. Do not put
the resulting binary in Git. As a migration check, this source was also
compiled with the Ring Fountain authority `/home/kqdx/basilisk/src/qcc` and read
the same snapshot successfully with identical output. That compatibility check
does not replace the pinned qcc for the archived reproduction.

`analyze_results.py` aggregates the snapshot tables and independent solver
logs, then regenerates convergence tables and plots. It was adjusted during
migration to take the independent reproduction root explicitly:

```sh
python3 -m venv /tmp/drop-impact-audit-venv
/tmp/drop-impact-audit-venv/bin/pip install -r tools/requirements.txt
/tmp/drop-impact-audit-venv/bin/python tools/analyze_results.py \
  --reproduction-root /home/kqdx/basilisk_work/reproductions/drop_impact_20260718
```

This command overwrites the derived tables and figures in the case directory.
Run it only when intentionally refreshing the evidence and then review the
diff. The tracked tables and figures are sufficient for reading the audit;
these optional packages are not added to the repository-wide requirements.
