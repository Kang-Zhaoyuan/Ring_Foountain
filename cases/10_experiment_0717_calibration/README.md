# 17 July experiment: two-repeat calibration intake

Intake date: 2026-07-17. Status: **timing and height observations accepted;
a provisional literal-parameter L7 run is stable but fails the quantitative
jet-height comparison**.

## Source and transcription

The original workbook remains in Windows storage and is not copied into this
repository. `source_lock.tsv` freezes its path, size, modification time, and
SHA256. It was read directly as OOXML using Python standard-library ZIP and XML
parsers; no formulas or embedded images were present. Only Sheet1 contains
measurements. Sheets2 and 3 are empty.

The workbook template has four repeat rows per experimental group, but only
the first two repeats of group 1 are populated. `measurements.tsv` is a direct
ASCII transcription. The high-speed frame rate supplied by the user is
`2000 fps`, hence one frame is `0.5 ms`. `event_observations.tsv` subtracts the
contact frame from each event frame. Absolute frame numbers are not compared
between repeats.

## Observations

| event | repeat 1: time / height | repeat 2: time / height | mean height |
| --- | ---: | ---: | ---: |
| crown maximum | 55.0 ms / 8.95 mm | 33.0 ms / 9.90 mm | 9.425 mm |
| first-jet maximum | 62.5 ms / 68.37 mm | 76.0 ms / 63.90 mm | 66.135 mm |
| Worthington maximum | 146.0 ms / 52.77 mm | 177.5 ms / 63.90 mm | 58.335 mm |

With only two repeats, the sample standard deviations in `event_summary.tsv`
describe repeat spread only; they are not population uncertainties. Crown
timing has the largest relative spread. No parameter is fitted to these six
observations at this stage.

## Height definition

The workbook heights are human observations of the highest relatively
unbroken water column, not the highest isolated water pixel or droplet. This
is retained as the primary experimental definition.

`tools/coherent_height.py` supplies a first reproducible CFD-side proxy from
the existing uniformly sampled fields:

1. Threshold water at `f >= 0.5` outside predominantly solid samples
   (`cs >= 0.5`).
2. Seed the main pool at the lowest axial sample.
3. Use face-connected, four-neighbour flood filling by default.
4. Report the highest main-pool-connected sample, the highest sample of any
   water, and the highest disconnected sample separately.

This detector deliberately excludes detached droplets. It is a conservative
"coherent core" measure and does not yet reproduce the user's allowance for a
partly fragmented but visually unified jet. It operates on 1 mm sampled fields,
not the native VOF mesh, so threshold and sampling error must be reported.
Human-labelled source frames will be needed before promoting it to a calibrated
experimental image metric.

The complete old-geometry L7 scan is in
`existing_l7_coherent_height.tsv`. Its connected-core maximum is `7.913 mm`
at `131.583 ms` after first wetting. The all-water maximum is `29.167 mm` at
`175.583 ms`, but only two sampled water points are disconnected from the
pool at that frame. `existing_l7_event_samples.tsv` gives the nearest 2 ms
sample to each experimental event. This confirms that a raw maximum is
droplet-sensitive; it does not validate the old CFD result.

`review/old_l7_height_workflow_check.png` plots the distinction and the six
experimental observations. The old and experimental geometries differ, so
the vertical discrepancy in this workflow plot is not treated as a calibrated
model error.

## Authoritative specimen parameters

The spreadsheet labels `5.2 mm` and `12.6 mm` as inner and outer diameter,
with thickness `5.02 mm` and measured mass `5.35 g`. Interpreted literally as
diameters, the rectangular annulus volume is `519.332 mm3` and its inferred
density is `10.302 g/cm3`; density `7.8 g/cm3` would instead give `4.051 g`.
Interpreting the two entries as radii gives `2.575 g/cm3`, so that alternative
does not resolve the mismatch.

The user subsequently identified this workbook as the latest reference. The
working specimen is therefore frozen as `Ri=2.6 mm`, `Ro=6.3 mm`,
`h=5.02 mm`, measured mass `5.35 g`, and release height `105 mm`. The motion
equation uses the measured mass directly. The inconsistent density inferred
from a rectangular annulus remains a metadata warning; it is not used to
replace the measured mass with the earlier `7.8 g/cm3` material value.

The existing CFD geometry (`Ri=2.5 mm`, `Ro=15 mm`, `h=4 mm`, mass
`21.441 g`) does not represent this workbook specimen. Its old L7 result may
be used only to test the height-analysis workflow, not compared quantitatively
with the six experimental heights.

The release-height cell reads `100+/-5 (105)`. The current operational value
is the parenthetical `105 mm`, giving a vacuum impact speed of `1.4353 m/s`.

## Literal-parameter L7 preflight

One explicitly provisional run was made rather than silently choosing values:

- `5.2/12.6 mm` were treated as diameters, giving `Ri=2.6 mm` and
  `Ro=6.3 mm`;
- measured mass `5.35 g` was used directly in the motion equation;
- the parenthetical `105 mm` was treated as release height;
- `75 deg`, `sigma=0.072 N/m`, and the earlier one-time lower-face-depth
  constraint at `100 mm` were retained without fitting.

The isolated project-authored solver was compiled without warnings by
`/home/kqdx/basilisk/src/qcc`. The external contact header, solver source, and
binary remain outside the repository and are identified only by hashes in
`solver_hashes.tsv`. The uninterrupted run ended normally after 13 min 56 s.
Interfaces were saved every `0.25 ms` and sampled fields every `1 ms`.
The ignored evidence archive has 1,719 files in its relative manifest;
`SHA256SUMS` itself hashes to
`1023ff66450ecd3c5c2f004c2e3c97d5762a99d2a4ffc31c67574f6efc7c39b5`.

| end / grid | max budget drift | max lab speed | min dt | cells | deep leakage | invalid |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 340 ms / L7 | 0.1123% | 9.607 m/s | 9.091e-6 s | 131,072 | unresolved false zero | 0 |

First wetting occurs at `146.333 ms`, with ring speed close to the provisional
vacuum value. The empirical topology event occurs at `206.036 ms`, or
`59.702 ms` after wetting, and adds `0.1755 mL`. Because that is close to the
observed first-jet maxima at `62.5` and `76.0 ms`, the run is not an independent
prediction of first-jet timing.

The coherent-height detector finds a global post-contact maximum of only
`8.575 mm` at `106.667 ms`. At the six experimental event times, simulated
heights range from `1.333` to `7.901 mm`; the experimental first and
Worthington jets range from `52.77` to `68.37 mm`. All-water and connected-core
heights coincide at those samples, so detached droplets do not explain this
large shortfall. Exact nearest-sample values are in
`provisional_specimen_l7_event_samples.tsv`.

The native-grid maximum laboratory speed occurs at `64.167 ms` after wetting.
The nearest sampled maximum lies in a full-fluid two-phase interface cell
`72.2 mm` below the undisturbed surface, not at the embedded boundary and not
in an upward free-surface jet. See `provisional_specimen_l7_peak_sample.tsv`.

Review files:

- `review/provisional_specimen_l7_height_comparison.png` compares the full
  coherent-height trace with all six measurements.
- `review/provisional_specimen_l7_event_interfaces.png` shows the fixed-surface
  interface at the nearest saved time for each measurement. It shows a small
  central rise and residual cavity fragments, not an experimental-scale jet.

L7 resolves the `3.7 mm` radial metal width with only `3.95` cells. The stable
negative result is therefore a preflight, not a grid-converged rejection of
the physical model. It does reject treating this L7 output as quantitative
agreement and gives no basis for contact-angle or surface-tension fitting. A
later L8 audit showed that the historical empirical event filled the complete
solid interior; L7's `2.5 Delta` deep-leak threshold could not resolve that
error. Case 11 supersedes the event with a two-sided thin band.

## Decision

Accept the two repeats and the literal workbook specimen parameters as the
current quantitative reference. Do not tune surface tension, contact angle,
or the empirical cavity transition to two repeats. Retain the completed L7 run
as a stable negative preflight, and use the same frozen parameters for the L8
resolution check and future experimental-image comparison.
