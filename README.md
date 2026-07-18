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
12. Workbook-based event-height/timing intake and coherent-height calibration.
13. First-jet shape correction and L7/L8 native-facet audit.
14. Separate 26.15 g video-specimen trajectory/morphology audit and laboratory key-frame atlas.
15. Independent CoMPhy Drop-Impact reproduction audit, with pinned external versions, repeatability and parameter-response smoke tests, native VOF post-processing, and short L10--L12 convergence evidence. Only newly created audit material is tracked; GPL upstream source and run dumps remain outside this repository.
16. Independent CoMPhy Bursting-Bubble reproduction audit: offline SingularJets2026 capsule PASS, minimum plain-solver reproduction PASS, and scientific jet baseline PARTIAL after the measured L11 estimate crossed the resource gate. Case 14 is evidence-only; GPL source, capsule payloads, binaries, environments, and dumps remain external.
