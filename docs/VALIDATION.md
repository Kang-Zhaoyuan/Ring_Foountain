# Validation record

This document is updated as each stage produces numerical evidence. An animation is presentation only; acceptance requires logs, conservation checks, solver diagnostics, and mesh or geometry convergence.

## Official `missing_metric`

Source: `/home/kqdx/basilisk/src/test/missing_metric.c`. The qcc command completed with exit code 0 and the run completed with exit code 0. The 23-line reproduced result is an exact match to `missing_metric.ref`; maximum absolute field error is 0. No `nan`, `inf`, `SIGFPE`, or segmentation fault was observed. Archived at `cases/00_official_missing_metric/` and `runs/20260714_145955_00_official_missing_metric/`.

## Official axisymmetric two-phase smoke test

The case is a case-local smoke-test copy of `rising.c`, compiled with `-DAXIS=1 -DADAPT=1 -DLEVEL=5` and `grid/quadtree.h`, with a case-local stop at `t=0.2`. It completed with exit code 0 and no invalid numerical markers. Maximum relative bubble-volume drift was `1.99532e-4`; maximum logged bubble velocity was `0.191239`; minimum dt was `0.00379709`. The log includes multigrid statistics and the final dump. This is a lightweight smoke test, not a quantitative reproduction of the full official `t=3`, level-8 benchmark. Archived at `cases/01_official_rising_axi/` and `runs/20260714_150825_01_official_rising_axi/`.

## Publication-linked drop impact

The MIT source was copied with attribution into the case directory and adapted only for headless execution and current qcc API compatibility. It compiled and ran serially to `t=0.25` at base level 4 and max level 4 with exit code 0. Three-phase VOF, surface tension, adaptivity, interface facets, pressure/stress logs, energy logs, snapshots, and `final.dump` were retained. Current qcc required `-grid=quadtree`, `-disable-dimensions`, removal of the obsolete `output_gfs(t=...)` named argument, and removal of the old `unistd/access` cleanup path. No invalid markers occurred. This is a headless smoke test, not a quantitative publication reproduction. Archived at `cases/02_published_drop_impact/` and `runs/20260714_151228_02_published_drop_impact/`.

## Static annular geometry

Parameters are `Ri=0.0025 m`, `Ro=0.015 m`, `h=0.004 m`; analytical volume is `2.7488935718910665e-6 m^3`. The installed `axi.h` sets `cm=y`; its meridional metric integral is converted with `2*pi`. With explicit boundary-band quadtree refinement from baselevel 3, the results were:

| maxlevel | leaf cells | cut cells | metric integral | converted volume (m^3) | relative error | invalid cs/fs | orphan cut cells |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 448 | 16 | 4.2692871093749972e-7 | 2.6824722037756164e-6 | 2.4162946e-2 | 0 / 0 | 0 |
| 6 | 808 | 32 | 4.3492584228515597e-7 | 2.7327196619587953e-6 | 5.8837891e-3 | 0 / 0 | 0 |
| 7 | 1528 | 62 | 4.3627700805664055e-7 | 2.7412092868817513e-6 | 2.7954102e-3 | 0 / 0 | 0 |

The rectangular section does not cross negative `y`, leaves the axis at `y=0` as the symmetry boundary, and shows decreasing geometry error under refinement. This stage has no fluid physics.
