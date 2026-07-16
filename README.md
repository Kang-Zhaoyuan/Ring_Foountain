# Ring Fountain Basilisk workspace

This repository is the reproducible foundation for an axisymmetric Basilisk study of a flat metal ring entering a free surface. The current work is staged: official compatibility tests and static geometry precede constrained, non-quantitative constant-speed and free-fall explorations.

The project uses the installed Basilisk tree read-only:

```text
Basilisk source: /home/kqdx/basilisk/src
qcc:            /home/kqdx/basilisk/src/qcc
project:        /home/kqdx/basilisk_work/ring_fountain
```

The first physical model is two-dimensional axisymmetric. Basilisk uses `x` for the axial coordinate and `y >= 0` for the radial coordinate; `bottom` is the symmetry axis. A flat ring is represented by a rectangular meridional section, not a circle.

## Commands

```sh
make env-check
make build CASE=cases/00_official_missing_metric
make run CASE=cases/00_official_missing_metric
make validate CASE=cases/00_official_missing_metric
```

`scripts/run_case.sh` creates a new timestamped directory below `runs/` for every run, including failed compilations. It never reuses a previous run directory.

## Stages

1. Environment and project scaffolding.
2. Reference audit and immutable vendor snapshots.
3. Official `missing_metric` compatibility test.
4. Official axisymmetric two-phase rising-bubble smoke test.
5. Headless, low-cost publication-linked drop-impact smoke test.
6. Static embedded annular geometry and mesh convergence.
7. Architecture decision and handoff.
8. External fixed embedded contact-line audit and author-case reproduction.
9. Isolated constant-speed Galilean-frame ring-entry exploration.
10. Isolated accelerating-frame free-fall ring-entry exploration and laboratory-frame rendering.
11. Experimental 10 cm-release cavity-detachment constraint and empirical topology scaffold.
