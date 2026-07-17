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

## External embedded contact-line candidate audit

Audit date: 2026-07-15. Status: **failed; gate remains blocked**.

The Popinet and Tavares Basilisk sandbox `contact-embed.h` implementations were identified as the only directly relevant fixed embedded VOF contact-angle route with published validation examples. Their source files have no explicit license grant, are outside the officially maintained `/src` tree, and the Tavares version is marked under testing with an adaptive-mesh fixme. They were therefore not copied into this repository.

For preliminary compatibility evidence only, read-only copies under `/tmp` were exercised with a project-authored 90-degree sessile-drop probe using the installed qcc. Both headers compiled without warnings and produced identical results. Uniform levels 5, 6, and 7 completed to `t=0.5`, generated interface/solid facets and final dumps, and contained no invalid numerical markers. Initial semicircle geometry converged and the imposed contact normal was exact in detected contact cells. Maximum volume drift was non-monotone and terminal velocity increased from `2.5904474e-3` to `8.4098333e-3` between levels 5 and 7.

The complete short-time comparison is in `cases/05_contact_embed_candidate_audit/validation.tsv`. Relative to the paper's long static relaxations (`T=15` or `T=20`), `t=0.5` is too short to treat terminal velocity as an equilibrium metric, so this probe is not the final numerical rejection. The independent license and maintenance failures remain. No ring geometry, axisymmetric extension, AMR, or motion was attempted with this code.

## Author-source reproduction and long-time port

Reproduction date: 2026-07-15. Status: **partially reproduced; general gate failed**.

The user-supplied Tavares et al. PDF was read in place and hashed. The full public implementation/test listing and Popinet predecessor were downloaded to ignored, read-only vendor directories and frozen in `references/contact_embed_sources.lock`. No source file has an explicit license grant. Exact-source qcc object compilation succeeds for five of the seven author test files; the current 2-D sessile page fails on a duplicate `tag` and two undeclared old APIs, while the slot page includes a nonexistent filename. An exact cylinder build reaches the native link stage but this local Basilisk installation lacks the optional View libraries. A headless-only cylinder copy compiles without warnings and runs.

The author cylinder setup was instrumented and run at `N=32,64,128` for 30, 90, and 150 degrees. All nine runs completed, wrote diagnostics/facets/dumps, and had zero invalid values. Total-volume drift decreased for the extreme angles, but 30-degree terminal velocity worsened from `9.96e-4` to `2.31e-2`, and its curvature standard deviation reached 2.96 at `N=128`. The 90-degree runs were stable, with terminal velocities near `1e-6`.

The broken flat sessile page was minimally ported to the current header API outside the project and run to the paper's `T=20` at the same three levels for 45, 75, and 120 degrees. Again, all nine runs completed with no invalid values. The 75-degree terminal velocity converged to negligible values, but relative radius error increased from 1.58% to 3.99% for 45 degrees, its maximum total-volume drift increased from 3.24% to 3.42%, and the 120-degree results were non-monotonic.

| geometry / angle | N=32 max drift / final speed | N=64 max drift / final speed | N=128 max drift / final speed | result |
| --- | ---: | ---: | ---: | --- |
| cylinder 30 deg | 4.99e-2 / 9.96e-4 | 2.48e-2 / 2.04e-2 | 1.29e-2 / 2.31e-2 | fail: velocity/curvature worsen |
| cylinder 90 deg | 6.90e-3 / 5.72e-7 | 1.15e-4 / 2.53e-6 | 1.20e-4 / 1.23e-6 | locally stable, drift non-monotonic |
| sessile 45 deg | 3.24e-2 / 7.27e-5 | 3.55e-2 / 5.17e-4 | 3.42e-2 / 1.70e-4 | fail: radius error and drift do not converge |
| sessile 75 deg | 1.14e-2 / 4.35e-6 | 1.15e-2 / 1.44e-7 | 1.03e-2 / 5.24e-14 | locally stable, radius error worsens |
| sessile 120 deg | 7.91e-3 / 2.50e-14 | 1.39e-2 / 3.24e-5 | 1.40e-2 / 4.80e-5 | fail: drift and speed worsen |

Complete tables are in `cases/06_author_contact_embed_reproduction/`. The 147 generated logs, time series, interfaces, solid facets, and dumps are retained under `runs/20260715_233000_06_author_contact_embed_reproduction/`. The paper confirms technical compatibility for selected moderate angles, but it also explains the observed porous-layer mass absorption, pinning, and non-monotonic convergence. The general fixed embedded VOF contact-line gate remains closed.

## Exploratory constant-speed ring entry

Exploration date: 2026-07-16. Status: **stable qualitative level-7 sequences obtained; grid, cut-cell phase, and contact-line convergence failed**.

Following an explicit strategy change, the moderate-angle Tavares route was used only in an isolated local directory. The ring remains fixed while the free surface and both phases translate upward at `U=1 m/s`, equivalent to horizontal prescribed-speed entry. Water and air use `rho=998/1.2 kg/m^3`, `mu=1e-3/1.8e-5 Pa s`, `sigma=0.072 N/m`, and `g=9.81 m/s^2`. The 75 deg angle is uncalibrated; 90 deg is only a short comparison.

The qcc quadtree build succeeded, but the viscous level-6 smoke run received `SIGFPE` at iteration zero in `/home/kqdx/basilisk/src/viscosity-embed.h:116`. A zero-viscosity quadtree control and viscous uniform-grid control reached 5 ms. Combined with the external header's adaptive-mesh fixme, this rejects quadtree for the present implementation. Basilisk source was not modified.

Because the Galilean-frame domain has a liquid inlet, volume conservation is the relative residual against initial water plus analytical inlet volume. No run had outlet water. Intentional contact ghost liquid is reported separately from liquid more than `2.5 Delta` inside full-solid ring cells; only the latter is treated as leakage.

| angle / grid / control | completion | max budget residual | max ghost liquid (m3) | deep-solid liquid (m3) | max frame/lab speed (m/s) | min dt (s) | cells | invalid |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 75 deg / L7 / no-slip, 120 x 60 mm | 60 ms | 1.8564% | 1.385e-6 | 0 | 3.830 / 2.831 | 9.091e-6 | 32,768 | 0 |
| 75 deg / L8 / no-slip, 120 x 60 mm | 60 ms | 3.5939% | 8.264e-7 | 0 | 18.280 / 17.311 | 6.201e-6 | 131,072 | 0 |
| 75 deg / L7 / no-slip, 180 x 60 mm | 120 ms | 1.8183% | 1.516e-6 | 0 | 7.301 / 6.593 | 9.091e-6 | 49,152 | 0 |
| 90 deg / L7 / no-slip, 60 x 60 mm | 12 ms | 1.0712% | 7.281e-7 | 0 | 1.659 / 0.659 | 9.091e-6 | 16,384 | 0 |
| 75 deg / L7 / free-slip control | 30 ms | 1.7815% | 1.314e-6 | 0 | 3.604 / 2.612 | 9.091e-6 | 32,768 | 0 |
| 75 deg / L8 / free-slip control | 30 ms | 2.2935% | 5.244e-7 | 0 | 6.385 / 5.966 | 5.669e-6 | 131,072 | 0 |
| 75 deg / L7 / half-cell phase control | 30 ms | 2.6719% | 1.028e-6 | 0 | 2.244 / 1.355 | 9.091e-6 | 32,768 | 0 |

The no-slip L8 lab-frame speed reaches 17.311 m/s at 43.49 ms in liquid on the lower embedded face (`cs=0.467`); it is not a resolved free jet. Over the first 30 ms, changing to free-slip reduces the L8 peak from 11.807 to 5.966 m/s, but free-slip L8 remains 2.28 times L7 and its budget residual still worsens. The strongest full-liquid velocity moves about one L8 cell from the inner edge, while a 4.940 m/s interface/cut peak remains on the ring. Wall treatment influences but does not eliminate the instability.

The no-slip level-7 half-cell axial phase control preserves `Delta` and physical ring/free-surface coordinates. It stays close to the base bulk interface through roughly 16 ms, then follows a different cavity path from 20 to 30 ms. Its lab speed drops from the base L7 value of 2.831 to 1.355 m/s while the budget residual rises from 1.856% to 2.672%. Level 7 is therefore not independently robust to cut-cell phase even though its base sequence looks more plausible.

The user manually accepted the base L7 4--60 ms sequence as qualitatively consistent with the expected early crown and first-upward-event development. That review supports continued observation at L7 but is not numerical validation. The long L7 run reaches 120 ms and shows a progressively flatter translated far surface, central deformation, and detached interface fragments. No automated height or mechanism detector is used, and the sequence is not labeled as cavity closure or a Worthington jet without manual experimental comparison.

At base level 7, 75 and 90 deg facets nearly coincide at 4, 8, and 12 ms. This supports only a limited statement that early bulk morphology is not highly sensitive to this moderate angle change on that grid. It does not validate either angle as metal wetting.

The tracked tables and review images are in `cases/07_exploratory_constant_speed_entry/`. The original 176-file evidence set remains in `runs/20260716_113000_07_exploratory_constant_speed_entry/`. The 932 follow-up archive files before the manifest are retained in `runs/20260716_121500_07_extended_entry_followup/`; the archive excludes all private source, executable, and external header content and is verified by a relative SHA256 manifest.

Conclusion: accept only the base no-slip uniform L7 branch for constrained, manually reviewed morphology. Reject longer L8 runs, free-slip as an uncalibrated optimization, fabricated slip/contact laws, and all quantitative contact-line, cavity, speed, or jet claims. The only next action is manual classification of the existing L7 50--120 ms sequence against laboratory chronology before selecting a denser L7 interval.

## Exploratory free-fall ring entry

Exploration date: 2026-07-16. Status: **completed to 530 ms on uniform L6 and L7; accepted only for qualitative chronology and rendering**.

The ring density is the user-confirmed `7800 kg/m^3`, giving mass `0.02144136986075032 kg`. Its lower face starts `50.9684 mm` above the water, corresponding to a vacuum contact speed of `1 m/s`. The fixed embedded geometry is retained in an accelerating ring frame. A project-authored axisymmetric pressure/viscous traction integral drives a vertical Newton equation; this is not moving-cut-cell geometry and it omits an explicit solid contact-line capillary line force.

Before water entry, the axisymmetric hydrostatic force converges toward the analytical `0.0269127 N`, air-only free fall agrees with the analytical trajectory to better than 0.05%, and dynamic hydrostatic controls remain stable. A 16:1 dump can be read only after rebuilding fixed metrics, but restart introduces a `0.064 N` impulse and about `0.20 m/s` disturbance, so all accepted long results use uninterrupted processes.

| run | completion | final drop / speed | max budget residual | max lab speed | min dt | cells | deep leakage | invalid | result |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| tall L6 | 330 ms | 449.740 mm / 2.531 m/s | 0.6909% | 10.056 m/s | 9.091e-6 s | 20,480 | 0 | 0 | coarse topology control |
| tall L7 | 330 ms | 464.619 mm / 2.609 m/s | 0.3078% | 11.282 m/s | 9.091e-6 s | 81,920 | 0 | 0 | main qualitative branch |
| deep L6 | 530 ms | 1092.831 mm / 3.821 m/s | 0.5434% | 12.462 m/s | 9.091e-6 s | 65,536 | 0 | 0 | cavity wall fragments strongly |
| deep L7 | 530 ms | 1118.686 mm / 3.973 m/s | 0.2356% | 22.629 m/s | 9.091e-6 s | 262,144 | 0 | 0 | no closure; late high-speed/corrugation warning |

The final deep L7 run was restarted from `t=0` after a host power loss and completed in one process; no partial dump was stitched. It exited normally after 12,694 steps and contains no `nan`, `inf`, `SIGFPE`, segmentation fault, deep-solid liquid, or radial outlet water. Maximum upward fluid force is `0.4688 N`, minimum is `-0.1176 N`, and maximum intentional contact-method ghost liquid is `2.566e-6 m^3`.

Both grids show the manually identified central first-jet candidate and an annular open cavity. Neither shows coherent cavity closure by 530 ms. L7 has lower water-budget residual and less coarse fragmentation, but after roughly 390 ms it develops substantial corrugation, detached fragments, force oscillation, and large local speeds. Saved field samples place the 458--464 ms high-speed path in full-fluid interface cells about 38 mm above the ring rather than solely in embedded cut cells. The result therefore does not support a Worthington-jet claim or quantitative timing/height prediction.

The laboratory-frame H.264 animation was generated from saved `2 ms` fields and decoded for verification. It uses one fixed `0--10 m/s` water-speed scale, saturates larger values red, and includes both a fixed full trajectory and fixed free-surface window. The tracked video SHA256 is `9282f72e5f13dc05b803a67b08709f3502c7c99c7e7736c9d88a7fc177805ecd`.

Conclusion: retain L7 as a frozen qualitative baseline, not as a converged physical prediction. Do not interpret visual agreement as validation, do not infer a second-jet mechanism, and do not raise release height before comparing the current trajectory and morphology with the forthcoming blinded experiment.

## Experimental cavity-detachment constraint

Constraint date: 2026-07-16. Status: **original route rejected; empirical
topology scaffold accepted only for qualitative continuation**.

The new experiment uses a `100 mm` release height and reports that the ring
becomes fully surrounded by water after the initial entry cavity. Vacuum
impact speed is `1.400714 m/s`. The original 10 cm-release L7 calculation
remains directly attached to the gas cavity through `300 ms`, when the lower
ring face is `305.6 mm` underwater. Its interface-to-ring distance is still
zero, despite zero invalid values and maximum budget residual `0.2504%`.

L6 screening tested contact angles from 30 to 120 deg, surface tension from
`0.036` to `0.144 N/m`, and no-slip versus free-slip. Every unforced route
remains attached after passing `100 mm` depth. This rejects surface-tension
tuning, static-angle tuning, and free-slip as explanations or fixes.

A separate hybrid branch uses the first available experimental depth as a
single topology constraint. At lower-face depth `100 mm`, it marks water once
within a `1.25 Delta` ring shell and adds the measured mobile-water increment
to the conservation reference. It does not continue forcing the interface.

| grid | event time | added water | last attached depth | final distance | max budget residual | max lab speed | invalid |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L6 | 206.2 ms | 1.290 mL | 99.715 mm | 217.5 mm at 280 ms | 0.2930% | 7.907 m/s | 0 |
| L7 | 204.95 ms | 0.547 mL | 99.710 mm | 319.6 mm at 320 ms | 0.1663% | 8.024 m/s | 0 |

No reattachment, invalid value, deep-solid liquid, outlet water, or new
force/velocity peak occurs after the transition. The added volume decreases
under refinement, but the event remains empirical and grid-dependent. It
corrects only the known topology mismatch; residual cavity fragments and a
central surface rise remain through 318 ms.

Conclusion: reject the original fixed-contact-line branch against the
experiment. Retain the constrained L7 branch only as a disclosed hybrid
scaffold. The next validation datum must be the measured detachment time and
ring depth from high-speed video; no later jet timing should be interpreted
before replacing the provisional 100 mm trigger.

## 17 July quantitative event intake and literal-parameter preflight

Validation date: 2026-07-17. Status: **two repeats accepted as calibration
targets; provisional L7 is numerically stable but does not produce the
measured first or Worthington jet height**.

The read-only workbook SHA256 is
`5f8fcf43438903477c13cbc39ed466ffc050df8f03e40e7014bbe050dc5cddf9`.
Only two repeats in group 1 are populated. At `2000 fps`, observed crown,
first-jet, and Worthington maxima occur respectively at `33--55`, `62.5--76`,
and `146--177.5 ms` after water contact. Mean heights are `9.425`, `66.135`,
and `58.335 mm`. These are human coherent-column heights, not highest-droplet
positions.

A four-neighbour main-pool connectivity detector was applied first to the
frozen old L7 fields and then to a new provisional specimen run. It reports
all water, connected water, detached water, and centerline-connected heights
separately. In the old run, isolated samples raise the late raw maximum from
about `7.2` to `29.2 mm`, confirming that raw VOF height is not the experimental
metric.

The new preflight interprets workbook `5.2/12.6 mm` as inner/outer diameters,
uses measured mass `5.35 g` directly, and interprets `100+/-5 (105)` as
`105 mm`. This implies an inconsistent rectangular-annulus density of
`10.302 g/cm3`; it is recorded as an equivalent density, not a material claim.
At L7, the radial metal width has only `3.95` cells.

| run | completion | max budget residual | max lab speed | min dt | cells | deep leakage | invalid | max coherent height |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| literal specimen L7 | 340 ms | 0.1123% | 9.607 m/s | 9.091e-6 s | 131,072 | 0 | 0 | 8.575 mm |

The one-time empirical topology event occurs `59.702 ms` after first wetting,
near the measured first-jet maxima, so event timing is not independently
predicted. At all six measurement times the computed coherent height is only
`1.333--7.901 mm`. The global speed peak is in a full-fluid interface cell
`72.2 mm` below the surface, not in an embedded cut cell or upward surface jet.
The run therefore fails the quantitative morphology comparison despite clean
health diagnostics.

Conclusion: preserve the negative result and do not tune `75 deg` or water
surface tension to two repeats. Parameter metadata must be resolved before a
costly L8 check; L7 alone is too coarse to close the gate.
