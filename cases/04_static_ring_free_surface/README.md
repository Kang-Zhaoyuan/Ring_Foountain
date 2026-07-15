# Static ring/free-surface compatibility gate

## Decision

The requested route is rejected for the installed Basilisk tree. This directory contains only a minimal compile-and-initialization probe; it is not an accepted simulation case.

The header stack `grid/quadtree.h + embed.h + axi.h + navier-stokes/centered.h + two-phase.h + tension.h` compiles with the project qcc, but no inspected official source provides a contact-angle or contact-line condition on an internal embedded boundary. The only available contact-angle implementation applies height-function boundary conditions on domain boundaries. Using it as though `embed` were an ordinary domain boundary would be an unverified replacement implementation and is not done here.

The probe uses the already validated rectangular meridional ring section, `Ri=2.5e-3 m`, `Ro=15e-3 m`, `h=4e-3 m`, with `x` axial, `y >= 0` radial, and `bottom` the symmetry axis. Its initial planar interface is `x=0`, so the intended liquid/solid/gas neighborhoods occur at the inner and outer vertical ring faces. No contact angle is prescribed and no claim is made about equilibrium wetting on a real metal surface.

## Official source audit

| Path | API or evidence | Relevance and limitation |
| --- | --- | --- |
| `/home/kqdx/basilisk/src/axi.h` | `AXI`, `cm_update()`, `fm_update()`, `metric_embed_factor` | Explicitly combines axisymmetric metrics with fixed embedded fractions. |
| `/home/kqdx/basilisk/src/embed.h` | `solid()`, `fractions_cleanup()`, `[embed]` scalar/vector boundary conditions | Supports fixed cut-cell geometry and velocity boundary conditions, but defines no VOF contact-angle condition. |
| `/home/kqdx/basilisk/src/vof.h` | `vof_advection()` under `#if EMBED` | Uses a documented simple approximation that ignores the solid fraction in partial-cell VOF updates. It does not supply embedded contact-line curvature or wetting physics. |
| `/home/kqdx/basilisk/src/contact.h` | `contact_angle(theta)`, height functions | Applies tangential height-function conditions on domain boundaries. It also states that the normal-component equivalent is not defined, limiting accessible angles. No embedded-boundary API is present. |
| `/home/kqdx/basilisk/src/test/sessile.c` | `h.t[bottom] = contact_angle(...)` | Official 2-D contact-angle test, but the solid is the domain boundary, not an embedded boundary. |
| `/home/kqdx/basilisk/src/test/sessile3D.c` | `h.t[back]`, `h.r[back]` | Same domain-boundary limitation in 3-D. |
| `/home/kqdx/basilisk/src/test/missing_metric.c` | `embed.h + axi.h + vof.h` | Official compatibility test, but it resets `cs=1` and `fs=1`; there is no actual solid or contact line. |
| `/home/kqdx/basilisk/src/examples/gaussian-ns.c` | `embed.h + centered.h + two-phase.h` | Fixed embedded bump and VOF coexist, but the free surface is separated from the bump and surface tension/contact-line treatment is absent. |

Repository-wide intersection searches found no official C source including both `embed.h` and `tension.h`, and no file named `contact-embed.h` or equivalent. Searches of `curvature.h`, `heights.h`, and `fractions.h` found no `EMBED`, `cs`, or `fs` branch for contact-line curvature.

## Minimal probe evidence

Source: `compatibility_probe.c`.

Compilation command:

```sh
/home/kqdx/basilisk/src/qcc -O2 -Wall cases/04_static_ring_free_surface/compatibility_probe.c -o /tmp/ring_fountain_case04_probe -lm
```

Compilation completed with exit code 0 and no diagnostics. The executable then terminated on its first solver step with exit code 136 (`SIGFPE`). A debug build and read-only `gdb` run located the signal in `/home/kqdx/basilisk/src/viscosity-embed.h:116`, called by `mg_solve()`, `viscosity()`, and the centered solver's `viscous_term()` at iteration zero. The concise result and backtrace are stored in `probe_results.tsv` and `gdb_backtrace.txt`.

This failed initialization probe is not used to infer a physical contact angle. No parameter tuning, alternate contact-line formula, three-level dynamic run, moving ring, entry, cavity, jet, or fountain stage was attempted.

## Gate status and limitations

The gate is **blocked/rejected**, not passed. Consequently there are no valid water-volume drift, solid-liquid leakage, maximum velocity, minimum timestep, leaf-cell convergence, interface evolution, or `final.dump` results to compare. Reporting zeros for these quantities would be misleading because the solver did not complete one step.

The only admissible next step is to identify and license-review a maintained Basilisk implementation that explicitly supports VOF contact lines on fixed embedded boundaries, then validate that implementation in an isolated canonical test with the installed qcc before returning to this ring geometry.
