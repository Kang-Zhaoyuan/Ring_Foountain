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
- cumulative accounting of liquid introduced by the closure;
- connected-main-liquid and centerline height diagnostics adapted from the
  method exercised in the Bursting-Bubble baseline;
- native PLIC facets, final dump, mass budget, kinetic energy and safety data.

The initial wetting speed is

```text
0.00286 m / 0.096 s = 0.0297917 m/s
```

so the experimental contact-to-hourglass interval supplies one disclosed
calibration. It is not an independent closure-time prediction. Unlike the old
single depth event, the new state advances locally from physical liquid contact
or a wetted neighbouring shell cell, is monotone, and has a grid-scaled finite
propagation speed.

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

Both initial calculations compile without warnings and exit normally:

| input | cells | end time | wet shell | budget residual | max speed | invalid |
|---|---:|---:|---:|---:|---:|---:|
| `smoke.params` | 32,768 | 2 ms | 2.052% | -0.02225% | 1.717 m/s | 0 |
| `default.params` | 131,072 | 6 ms | 10.671% | -0.06858% | 1.714 m/s | 0 |

Both runs write non-empty native PLIC streams and final dumps. The wetting
source is nonzero and remains explicitly included in the expected-volume
budget. These are functional results, not convergence evidence.

## Present boundary

This round asks only whether the new closure compiles, starts from first
contact, propagates wetting locally and preserves finite fields. It does not
repeat the external benchmarks and does not claim grid convergence. After the
smoke run, `entry_110ms.params` extends the same L7 case to 110 ms so it crosses
the calibrated cavity-detachment interval, without changing any other physical
parameter.
