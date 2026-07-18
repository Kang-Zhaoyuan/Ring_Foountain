# Impact-driven through-hole jet

Case 16 status (2026-07-18):

- **A. Diagnostic integrity: PASS**
- **B. Through-hole mechanism: FAIL** (the tested wetting changes did not strengthen it)
- **C. Jet-height improvement: FAIL**
- **D. L7/L8 sensitivity: NOT RUN** (no L7 candidate passed the gate)
- **E. Human visual comparison: NOT IMPROVED**

## Result first

The first jet at 52.5 ms is an impact-stage through-hole jet, not the 96 ms
cavity-collapse Worthington jet. The diagnostic-only Case 15 regression
reproduces `6.717300 mm` exactly; its PLIC tip is `7.152196 mm`, compared with
the experimental `105.80 mm`. Contact-triggered and instant-inner ghost-cell
wetting leave PLIC, pressure, aperture flux, and jet metrics unchanged.
Improvement is `1.00x`; the cell-metric deficit remains `99.0827 mm` (PLIC
deficit `98.6478 mm`).

## Runs and numerical evidence

All runs used `/home/kqdx/basilisk/src/qcc` (SHA-256
`6dc8de0ecb2ed366c48cd379387dfc6bae50844c9ef4df3e232d8ff6ceed0dee`),
Basilisk Darcs patch `586963ed3f4e8704f89b314b8d1f9e8a475a4065`, and the
project wrapper. Completed-run source SHA-256 is
`3244c2d639db4c96a59ffaa3517d6547ae59871950a0296a39a75ad56efe8544`.

- no-ring L6, 5 ms: normal exit, no spontaneous jet or invalid values;
- legacy L7, 80 ms: 52.5 ms regression differs from Case 15 by less than
  `3e-11 mm`;
- closed disk L7, 52.5 ms: zero mid-plane liquid area/flux,
  `jet_detected=0`, heights NA;
- contact-driven-inner L7, 80 ms: flow diagnostics identical to legacy;
- instant-inner bracket L7, 80 ms: jet, flux, and pressure files byte-identical
  to legacy.

Legacy L7 peak absolute volume-budget residual is `0.7573%`, wetting source is
zero, minimum dt is `6.011 us`, and no invalid value occurs. Maximum speed is
`18.146 m/s`, but at a pure-gas full-fluid cell (`f=0`, `cs=1`), so it is not
claimed as liquid focusing.

At 52.5 ms the mid-hole liquid flux is `1.77471e-4 m3/s`, axial momentum flux
is `0.23364 N`, inner lower-to-upper pressure difference is `47.955 Pa`, and
region-average axial velocity is `1.294 m/s`. These are nonzero, but PLIC shows
a broad low connected rise, not the experimental thin column. Missing physics
is therefore insufficient early inward/upward concentration, not simply “no
aperture flow”.

## Interpretation and next gate

Case 15 does use one slow front for early inner wetting and late upper-face
release, so its state architecture couples two stages. Case 16 shows that
decoupling only the full-solid ghost state does not change early physical
cut-cell flow. The coupling is not supported as the primary height-deficit
cause. A validated arbitrary-EMBED contact-line condition or measured
inner-edge geometry is still missing.

No 1/2 mm pre-impact gap was run: neither inner-wetting candidate survived the
mechanism/height gate, and incompressible gas cannot validate air compression.
This is `NOT TESTED`, not “no effect”. L8 was not run because height improvement
was 0%, below the factor-two or 25%-error-reduction gate.

Measure the inner lower-edge chamfer/radius first, then lower/upper aperture
diameters. The next solver task is a source-free arbitrary-EMBED contact-line
validation, followed by independently measured edge geometry. Do not
prioritise 96 ms closure, 3-D tilt, or Case 17 yet.

```sh
make build CASE=cases/16_impact_driven_through_hole_jet
./scripts/run_case.sh cases/16_impact_driven_through_hole_jet \
  params/baseline_l7_80ms.params
```

Metrics are frozen in `METRICS.md`; visual review starts at `HUMAN_REVIEW.md`.
Large outputs remain in ignored timestamped `runs/` and were never overwritten.
