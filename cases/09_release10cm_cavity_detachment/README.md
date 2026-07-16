# Release-height and cavity-detachment constraint

Run date: 2026-07-16. Status: **the original fixed-contact-line L7 route is
rejected against the new experiment; a separate experiment-constrained
topology branch is numerically stable but remains non-predictive**.

## New experimental constraint

The ring was released from `100 mm` above the undisturbed water surface. The
user reports that, after the initial entry cavity, the ring is completely
surrounded by water at an underwater location of about `100 mm` or deeper and
no longer directly carries an air cavity.

For the current geometry this release height gives

```text
vacuum impact time  = 0.142784312293 s
vacuum impact speed = 1.40071410359 m/s
```

Using outer diameter `D=30 mm`, the impact reference values are
`Re=41937.4`, `We=815.865`, `Fr=2.582`, `Bo=122.380`, and `Ca=0.01945`.
The L7 first-wetting time is `0.142417 s`.

The reported closure depth is not yet a frame-by-frame measurement. This case
uses lower-ring-face depth `100 mm` as the first provisional interpretation of
the observation, not as a calibrated physical constant.

## Detachment metric

For every saved VOF interface, the minimum Euclidean distance to the validated
rectangular ring section is computed in the ring frame. A zero distance means
that an interface still intersects the ring and the gas cavity remains
attached. Detachment requires a positive distance that remains positive for
all later samples.

The original 10 cm-release L7 run remains attached through `300 ms`, when the
lower ring face is `305.6 mm` below the original surface. Its minimum interface
distance is still exactly zero. This directly contradicts the experiment and
is not repaired by changing only the release height.

## Parameter audit

Water surface tension remains `0.072 N/m`. It was not tuned. The following L6
diagnostics all retain a directly attached cavity after the lower face passes
`100 mm` depth:

- constant contact angles from 30 to 120 deg;
- half and double water surface tension, `0.036` and `0.144 N/m`;
- no-slip and free-slip embedded tangential velocity.

The full numerical table is `screening_summary.tsv`. Doubling surface tension
does not change the attachment topology, so the mismatch is not evidence that
the physical water surface-tension value is too small. The tested static
contact-angle route also cannot represent the observed wetting transition.

Possible causes include contact-line pinning or self-sustaining solid ghost
fractions in the fixed embedded implementation, the absence of a validated
dynamic advancing-contact-line law, and axisymmetric suppression of
azimuthally local cavity rupture. These are hypotheses, not separately proven
mechanisms.

## Experiment-constrained topology branch

A separate hybrid branch applies one explicitly disclosed operation:

1. Evolve the original 75 deg, no-slip, `sigma=0.072 N/m` model unchanged.
2. When the lower ring face first reaches `100 mm` underwater, set the water
   fraction to one once within a `1.25 Delta` shell around the ring.
3. Measure the added mobile-water volume and include it in the subsequent
   water-budget reference.
4. Do not continue forcing the interface after this single event.

This is not a contact-angle formula, dynamic wetting model, or prediction of
closure depth. It is an experiment-constrained topology correction intended
to test whether later cavity evolution can proceed once the known attachment
error is removed.

## L6/L7 comparison

| route | grid | event / final state | added water | max budget residual | max lab speed | invalid |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| original | L7 | attached at 305.6 mm depth | 0 | 0.2504% | 9.842 m/s | 0 |
| constrained | L6 | detached at 100 mm; final distance 217.5 mm | 1.290 mL | 0.2930% | 7.907 m/s | 0 |
| constrained | L7 | detached at 100 mm; final distance 319.6 mm | 0.547 mL | 0.1663% | 8.024 m/s | 0 |

The L7 transition occurs at `t=0.20495 s`. The last attached sample has lower
face depth `99.710 mm`; the next sample has interface distance `1.204 mm`.
There is no reattachment through `320 ms`. Maximum speed and maximum fluid
force both occur before the imposed transition, so the operation does not
create a new recorded impulse peak.

The correction volume decreases under refinement because the shell thickness
scales with `Delta`, but the operation itself remains grid-dependent and
empirical. The contact-method ghost-liquid diagnostic rises because the solid
ghost layer is intentionally marked as water; this is not reclassified as
physical water inside the metal.

## Morphology

- `review/L6_detachment_compare_190-250ms.png` verifies the transition before
  spending on L7.
- `review/L7_detachment_compare_190-298ms.png` compares original and
  constrained L7 at identical times in the ring frame.
- `review/L7_empirical_lab_surface_180-318ms.png` shows the constrained
  laboratory-frame surface and residual detached cavity.

The constrained branch satisfies only the new observation that the ring stops
directly carrying the cavity. At `318 ms`, residual bubbles/fragments and a
central surface rise remain. This case does not identify a Worthington jet,
validate cavity-closure timing, or establish a real wetting mechanism.

## License boundary

All solver variants were compiled and run in the isolated private evaluation
directory. No private source, executable, Basilisk source, or unlicensed
external contact header is included here.

## Decision

Reject surface-tension tuning, constant-angle tuning, and free-slip as fixes.
Reject the original 10 cm-release L7 branch against the experiment. Accept the
single-transition L7 branch only as an explicitly empirical topology scaffold
for later qualitative work.

The only next recommendation is to extract the actual detachment time and
ring depth from high-speed experimental video. That measurement should replace
the provisional `100 mm` trigger before extending this branch to later jet
events.
