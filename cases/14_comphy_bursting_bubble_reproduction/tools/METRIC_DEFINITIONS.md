# Frozen local jet metrics

These definitions were frozen after the three L8 runs completed but before any
snapshot geometry was extracted.

- Basilisk AXI coordinates are `x=z` (axial) and `y=r` (radial), with `y=0`
  the symmetry axis. The undisturbed free surface is `z=0`.
- `f=1` is liquid and `f=0` is gas. Liquid connectivity uses face-connected
  cells with `f > 1e-4`; the component with the largest cell count is the main
  liquid pool. This intentionally excludes detached droplets.
- `z_all` is the largest axial coordinate of any PLIC endpoint. `z_main` is the
  largest endpoint belonging to the main liquid component. `z_center` is the
  largest main-component endpoint in `r <= 2*Delta_min`.
- The existing upstream `getBase` definition supplies the continuous outer
  surface's cavity/base location: pure-liquid and pure-gas components use
  thresholds `1-1e-4` and `1e-4`, face connectivity, and only the largest of
  each phase. Its search radius is `r < 1.2`; its near-axis tip band is
  `r < 0.25`.
- First coherent central jet inception is the first stored common solver time
  at which `z_center > max(0.02, 2*Delta_min)` and the outer-surface base has
  `r_base > 2*Delta_min`. The threshold therefore has an explicit grid-scale
  part; raw event-time differences are reported at the snapshot cadence.
- Jet height is `H=z_center-0`. Tip speed is the second-order centered finite
  difference of `H` at interior common snapshots (one-sided second-order at
  endpoints), with no time smoothing.
- The post-inception jet-base radius is `r_j=r_base`. Upstream `getJetFoot`
  additionally reports `q_jet=int_0^rj u_z*r*dr`, `q_l=int_0^rj u_z*dr`, and
  `Q_j=2*pi*q_jet`; these are used only where the candidate matches the robust
  outer-surface base.
- A topology change is the first stored time where the number of liquid
  components (`f>1e-4`) exceeds one. Snapshot cadence limits event-time
  precision.

PLIC distances are computed only at solver times present in every compared
case. Binary dump identity is neither expected nor required.
