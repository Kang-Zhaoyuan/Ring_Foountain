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

## Static ring with free surface and embedded contact line

Gate date: 2026-07-15. Status: **blocked/rejected**.

The installed source tree was audited before implementing a dynamic case. `/home/kqdx/basilisk/src/axi.h` explicitly supports axisymmetric embedded metrics, and `/home/kqdx/basilisk/src/vof.h` contains an embedded-boundary advection branch. However, `/home/kqdx/basilisk/src/contact.h` only imposes height-function contact angles on domain boundaries; it provides no condition for an internal embedded boundary. The official `sessile.c` and `sessile3D.c` tests use domain walls, `missing_metric.c` contains no actual solid (`cs=fs=1`), and `gaussian-ns.c` has no free-surface/solid contact or surface tension. No official source includes both `embed.h` and `tension.h`, and no embedded contact-line implementation was found.

A minimal probe in `cases/04_static_ring_free_surface/` combined quadtree, fixed embed, axi, centered two-phase VOF, and surface tension using the validated ring dimensions. The project qcc compiled it with exit code 0 and no diagnostics. The first initialization run terminated with exit code 136 (`SIGFPE`); `gdb` located the signal at `/home/kqdx/basilisk/src/viscosity-embed.h:116` in `residual_diffusion()`, reached through the first viscous solve. No completed timestep or valid `final.dump` was produced.

Because there is neither an official embedded contact-line API nor one successful timestep, the required three-level comparison was not run. Water-volume drift, leakage, maximum velocity, minimum `dt`, maximum leaf count, interface evolution, persistent droplets, and contact-line noise are all marked not available rather than reported as zero.

| maxlevel | completion | invalid markers | volume drift | solid leakage | max velocity | min dt | max leaves | result |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | not run | not applicable | N/A | N/A | N/A | N/A | N/A | blocked before grid study |
| 6 | not run | not applicable | N/A | N/A | N/A | N/A | N/A | blocked before grid study |
| 7 | not run | not applicable | N/A | N/A | N/A | N/A | N/A | blocked before grid study |

No contact angle, contact-line formula, moving boundary, entry motion, cavity, jet, or fountain dynamics was introduced. The gate remains closed until a maintained and license-compatible embedded VOF contact-line implementation is identified and passes a separate canonical qcc validation.
