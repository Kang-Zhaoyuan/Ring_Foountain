# First-jet shape correction

Date: 2026-07-17. Status: **the hidden full-solid fill is corrected; L8
partly straightens the first jet near 62.5 ms but is not accepted as a
quantitative replacement for L7**.

## Question and frozen inputs

The latest experiment reports that the first jet is approximately columnar:
its upper and lower diameters are not visibly distinct. The six earlier CFD
event panels instead showed a top-wide, bottom-narrow central rise. This round
tests that mismatch without fitting surface tension or contact angle.

The 17 July workbook is the current specimen authority. All new runs use
`Ri=2.6 mm`, `Ro=6.3 mm`, `h=5.02 mm`, measured mass `5.35 g`, and release
height `105 mm`. They retain `theta=75 deg` and `sigma=0.072 N/m`. The angle is
still an uncalibrated engineering assumption. The measured mass is used
directly; the density inferred from the rectangular dimensions is only a
consistency diagnostic.

The two experimental first-jet maxima are `62.5 ms / 68.37 mm` and
`76.0 ms / 63.90 mm` after first water contact. Human height means the highest
relatively unbroken column, not the highest droplet.

## Shape measurement

`tools/jet_width_profile.py` reads native VOF facets and the saved
`snapshots.tsv`; no rasterized image is measured. It samples horizontal
crossings every `0.25 mm` above the undisturbed surface and reports:

- maximum radius divided by the radius at the undisturbed surface;
- mean radius over 55--80% of jet height divided by the mean over 10--35%;
- layers with more than one central crossing.

A ratio of one is an equal-width reference, not a fitted acceptance band.
When wide shoulders, cavity remnants, or multiple interfaces cross the same
height, the scalar ratio is explicitly marked as confounded and the native
facet plot takes precedence. The method measures the axisymmetric CFD
silhouette; it is not yet calibrated to an experimental image contour.

## Isolated implementation and license boundary

The solver modifications are project-authored but remain in `/tmp` because
they include an unlicensed external `contact-embed.h`. No solver source,
binary, or external header is copied into this repository or the run archive.
`source_hashes.tsv` freezes the isolated source, binary, and header hashes.
Compilation used `/home/kqdx/basilisk/src/qcc` from the source directory of
each isolated build and completed with no diagnostics. Basilisk source was not
modified.

## Causal checks

Four changes were separated rather than combined:

1. Disabling the empirical cavity-detachment event at L7 leaves the 62.5 ms
   profile unchanged and makes the 76--90 ms top/bottom imbalance worse. It
   also raises maximum speed from `9.61` to `16.02 m/s` and budget residual
   from `0.1123%` to `0.1469%`. This route is rejected.
2. Auditing the event found that `ring_levelset <= 1.25 Delta` filled every
   full-solid cell, not just a boundary shell. L7 could not expose this because
   the radial metal width is only 3.95 cells and the deep-leak threshold was
   wider than half the metal section.
3. The corrected project rule is
   `-1.25 Delta <= ring_levelset <= 1.25 Delta`. It retains only the thin
   two-sided ghost band needed by the empirical topology scaffold. The L7 and
   L8 reruns both report zero deep-solid liquid.
4. Applying that correction at L7 leaves the mushroom profile essentially
   unchanged. Applying it at L8 resolves a narrower, straighter central body
   around 62.5 ms, so that local change is a grid-resolution effect rather
   than a consequence of liquid hidden inside the solid.

All accepted comparison runs start at `t=0` and complete in one process.
Dump restart is not used.

## Numerical health

| route | grid | max budget residual | max lab speed | min dt | cells | deep solid | invalid | max coherent height |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| historical full fill | L7 | 0.1123% | 9.607 m/s | 9.091e-6 s | 131,072 | unresolved false zero | 0 | 8.575 mm |
| no transition | L7 | 0.1469% | 16.023 m/s | 9.091e-6 s | 131,072 | 0 | 0 | 10.711 mm |
| corrected shell band | L7 | 0.1123% | 9.615 m/s | 9.091e-6 s | 131,072 | 0 | 0 | 8.228 mm |
| historical full fill | L8 | 0.0933% | 19.973 m/s | 7.353e-6 s | 524,288 | 1.107e-7 m3 | 0 | 8.597 mm |
| corrected shell band | L8 | 0.0933% | 19.973 m/s | 7.353e-6 s | 524,288 | 0 | 0 | 8.295 mm |

Both corrected runs exit normally and contain no `nan`, `inf`, `SIGFPE`,
segmentation fault, radial-outlet water, or invalid field values. The L8 speed
peak precedes the empirical event. The nearest 1 mm field sample places it in
full liquid near the lower inner ring edge, not in the upward free-surface
jet. L8 therefore remains a contact-edge resolution warning despite its lower
volume-budget residual.

## Shape result

At `62.5 ms`, corrected L7 has upper/lower mean-radius ratio `1.060`; corrected
L8 gives `0.962`. The L8 profile is visibly narrower and more nearly parallel
sided, although its local maximum/base ratio is still `1.203`. At `76 ms`,
L8 develops a broad shoulder and 11 sampled layers have multiple central
crossings, so a single whole-profile diameter ratio is not physically useful.
At `90 ms`, its upper/lower ratio is back to `1.231`, close to or worse than
the L7 value `1.208`.

The connected-height scan gives only `8.295 mm` maximum for corrected L8,
versus the measured `63.90--68.37 mm` first jets. Grid refinement changes the
silhouette but does not repair the order-of-magnitude height error.

Review files:

- `review/L7_vs_L8_shell_band_interfaces.png` is the primary manual-review
  sheet at 33, 62.5, and 76 ms in the fixed laboratory frame.
- `review/L8_shell_band_profile_62.5ms.png` overlays native-facet radial
  profiles and shows the local straightening directly.
- `review/L7_shell_band_shape_ratios.png` shows that the shell correction alone
  does not alter the L7 morphology.
- `review/L7_baseline_vs_no_transition_interfaces.png` documents the rejected
  event-removal control.

Exact values are in `health_comparison.tsv`, `shape_comparison.tsv`, and the
per-run width/coherent-height tables.

## Decision and limit

Adopt the thin shell-band condition as a correctness repair to the disclosed
empirical topology scaffold. Retain corrected L7 as the working exploratory
branch because its speed behavior is less severe. Use corrected L8 only as
evidence that refinement can reduce the early mushroom bias; do not use it to
predict jet height, speed, or a complete first-jet history. Reject event
removal and every full-solid-fill result for future continuation.

The only next recommendation is to extract calibrated silhouettes from the
raw experimental frames at 62.5 and 76 ms, including the waterline and scale,
then compare diameter-versus-height curves directly before changing any
physical parameter.
