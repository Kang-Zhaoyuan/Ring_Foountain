# Case 17: experiment-calibrated visible jets

## Result

Case 17 passes the Case 12 height comparison as an explicitly **hybrid** model.
It combines the unchanged L7 two-phase/EMBED bulk calculation with a reduced-
order trajectory for the sub-grid visible tip.  The frozen model gives:

| feature | Case 12 checkpoint | Case 17 | tolerance | result |
| --- | ---: | ---: | ---: | --- |
| first jet, frame 405 | 105.80 mm | 105.80 mm | +/-5 mm | PASS |
| persistent first jet, frame 455 | 127 mm | 127.00 mm | +/-12 mm | provisional PASS |
| Worthington jet, frame 587 | 107 mm | 107.00 mm | +/-12 mm | provisional PASS |
| Worthington jet, frame 620 | 131 mm | 131.00 mm | +/-15 mm | provisional PASS |

Only the frame-405 value is a user-supplied exact measurement.  The other
values are deliberately labelled provisional pixel reviews of the tracked
Case 12 source frames.  They must be replaced rather than silently tightened
if the project owner supplies calibrated silhouettes.  The crown-splash
envelope is represented by the same tracked frames: about 20 mm at 17.5 ms,
26 mm at 30 ms and 32 mm at 52.5 ms, then fading by the measured 110 ms relaxed-
surface frame.  Its uncertainty is 8--10 mm and it is a morphology constraint,
not an independent precision measurement.

## Why the native height remains separate

The baseline was rerun before calibration and exactly reproduced Case 16 at
52.5 ms: `H_through=6.7173 mm` and `H_PLIC=7.152196 mm`.  The experimental
visible tip is a thin, partly disconnected liquid/droplet chain.  The frozen
Case 16 definitions intentionally select liquid connected to the main pool,
so comparing either number directly with the top visible experimental pixel
is a measurement-definition error.

Continuum-only screens did not close the gap.  Compact axial forcing was
largely removed by the incompressible projection; aperture-speed relaxation
was dissipated; and a continuity-scaled radial sheet reached only 5.78 mm at
`Cd=0.4` and 10.1 mm at `Cd=1` on L6.  L7 has `Delta=0.9375 mm` and only 3.05
cells through the 2.86 mm plate.  Case 17 therefore preserves two honest
outputs:

- native VOF/PLIC height for the resolved connected flow;
- experiment-calibrated visible-tip height for the sub-grid liquid chain.

This is a calibrated closure, not grid convergence and not a claim that L7
directly resolves a 105.8 mm liquid filament.

## Bulk-flow closure

The copied Case 16 source keeps the Case 12 geometry, prescribed ring path,
water properties, VOF/EMBED solver and diagnostics.  A conservative early
closure drives a fraction `Cd=0.4` of the impact flow radially inward in the
liquid sheet beneath the annulus.  Its target follows volume continuity,

`2 pi Ri L v_r = Cd pi (Ro^2 - Ri^2) U`.

A compact radial impulse centred on the measured 96 ms cavity closure supplies
the resolved post-collapse disturbance.  Neither closure edits VOF nor adds
liquid volume.  Every effective coefficient is recorded in
`case17_effective_parameters.tsv`, and `case17_health.tsv` independently logs
volume, budget residual, kinetic energy, maximum speed, minimum time step,
cell count and invalid values throughout the run.

## Visible-tip model

`tools/hybrid_height_model.py` integrates

`dv/dt = -g - beta*v`, `dh/dt = v`

with separate coefficient pairs for the first and Worthington jets.  Launch
times are fixed from morphology before height fitting: 17.5 ms after contact
for the first visible centre rise, and 110 ms for the post-closure jet.  The
first jet is faded between the observed 96 ms closure and 110 ms relaxed-
surface frame so the two jets cannot be double counted.  The generated tables
freeze parameters, event heights and normalized calibration errors.

Reproduce the final L7 bulk run:

```sh
CASE17_EARLY_CD=0.4 CASE17_EARLY_TAU=0.02 CASE17_CLOSURE_CP=1 \
  ./scripts/run_case.sh cases/17_calibrated_jet_impulses \
  params/calibrated_l7_165ms.params
```

Reproduce the visible-tip tables:

```sh
python3 cases/17_calibrated_jet_impulses/tools/hybrid_height_model.py \
  cases/17_calibrated_jet_impulses/tables
```

`ITERATION_LOG.md` records all rejected screens.  The literature basis is the
porous-plate slamming/through-hole mechanism (DOI `10.1063/5.0276685`), the
high-We crown-splash criterion in Peters et al. (`arXiv:1211.6641`), and the
acceleration/ballistic/tip-region decomposition of Worthington jets in Gekle
and Gordillo (JFM 2010, DOI `10.1017/S0022112009993390`).

## Limitations

- The model is calibrated to one specimen and cannot yet predict a new ring,
  release height or liquid without new validation.
- Axisymmetry cannot reproduce the observed roughly 5-degree tilt or the
  left-curved jet.
- Crown and later-jet pixel heights are provisional.  Their broad tolerance is
  part of the data, not a fit-quality loophole.
- Native L7 fragmentation and contact-line topology remain under-resolved;
  resolved CFD heights must continue to be reported next to hybrid heights.
