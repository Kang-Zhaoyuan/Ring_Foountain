# Dynamic-wetting prescribed-trajectory ring entry

Status: **first implementation**. This case starts the new ring-physics branch;
it is not another external-repository reproduction.

## What is implemented

- the 26.15 g video specimen (`Ri=5.05 mm`, `Ro=20.07 mm`, thickness
  `2.86 mm`);
- the measured prescribed trajectory already accepted in case 12;
- a fixed rectangular embedded ring in an axisymmetric translating frame;
- filtered water/air VOF, viscosity, surface tension, gravity and the
  prescribed-frame acceleration;
- a project-owned finite-speed wetting front in a `1.25 Delta` ring shell;
- ghost-cell-only wetting: physical cut-cell VOF is never overwritten;
- cumulative accounting verifies that the closure adds no mobile liquid;
- connected-main-liquid and centerline height diagnostics adapted from the
  method exercised in the Bursting-Bubble baseline;
- native PLIC facets, final dump, mass budget, kinetic energy and safety data.

The initial wetting speed is

```text
0.00286 m / 0.096 s = 0.0297917 m/s
```

so the experimental contact-to-hourglass interval supplies one disclosed
calibration. It is not an independent closure-time prediction. Unlike the old
single depth event, the leading lower face has surface coordinate `s=0`, the
inner/outer sides use `s=x+h/2`, and the trailing face uses
`s=h`. The state is monotone and the front position `s=wetting_speed*t` is
independent of grid spacing. Each newly reached surface relaxes to wet over
`5 ms`; reaching both upper corners therefore releases the complete trailing
face rather than requiring a slow radial sweep across it.

No Tavares/Popinet contact header and no CoMPhy solver source is copied into
this case. CoMPhy supplies the trusted solver organization, filtered two-phase
settings and connected-component measurement pattern; this implementation is
project-authored.

## Run

On the project WSL installation:

```sh
make build CASE=cases/15_dynamic_wetting_ring_entry
./scripts/run_case.sh cases/15_dynamic_wetting_ring_entry smoke.params
```

The run wrapper exposes its unique run directory through `RUN_OUTPUT_DIR`, so
the solver writes diagnostics and facets directly beside the captured compile
and process logs. `default.params` is the first L7 6 ms entry calculation;
`smoke.params` is the L6 2 ms functional check.

## First local result

The source compiles without warnings with the isolated Basilisk verifier. All
three first calculations exit normally, write non-empty native PLIC streams
and final dumps, and contain no invalid values:

| input | cells | solved time | wet shell | max budget residual | max speed | wetting source |
|---|---:|---:|---:|---:|---:|---:|
| `smoke.params` | 32,768 | 2 ms | 40.625% | 0.0223% | 1.761 m/s | 0 |
| `default.params` | 131,072 | 6 ms | 46.875% | 0.0610% | 2.629 m/s | 0 |
| `entry_110ms.params` | 131,072 | 110 ms | 100% | 0.9592% | 18.146 m/s | 0 |

The 110 ms run took 283.4 s. The front reaches the trailing face at 96 ms,
the `5 ms` relaxation makes it fully wet at 101 ms, and native PLIC is last
within one L7 cell of the ring at 102.5 ms; it is more than three cells away
at 103 ms. This is the first source-free delayed-detachment implementation in
the project.

At the held-out 52.5 ms frame, however, the computed connected center rise is
only `6.717 mm`, versus the measured thin-jet height `105.80 mm`. The run also
reaches a local speed of `18.146 m/s`, and the post-detachment interface still
contains fragmented cavity remnants. The closure therefore fixes the timing
mechanism and removes artificial liquid injection, but it does not yet
reproduce the observed jet morphology. The compact numerical record is in
`first_run_summary.tsv`.

These local results verify the implementation path. Project rule still makes
`/home/kqdx/basilisk/src/qcc` in WSL the final compilation authority, so the
same three commands must be rerun there before this branch is merged.

## Present boundary

This round establishes a working new physics branch; it does not repeat the
external benchmarks and does not claim grid convergence or experimental
validation. The next coding task is to replace the simultaneous trailing-face
release with a pressure/geometry-aware gas-neck closure while keeping the
trajectory, fluid properties and source-free ghost-cell rule fixed. A single
L8 sensitivity run should follow that change; broad parameter scans remain
out of scope.
