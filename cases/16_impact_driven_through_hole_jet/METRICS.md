# Frozen Case 16 metrics

This definition was frozen before running any Case 16 physics candidate.  SI
units are used internally.  Heights are reported relative to the original
laboratory free surface, not the moving ring.

## Fixed classification constants

- liquid cell threshold: `f >= 0.5`;
- connectivity support threshold: `f > 1e-4` and `cs > 1e-6`;
- face-connected components: Basilisk `tag()` (no diagonal-only connection);
- main pool: largest axisymmetric liquid volume among connected components;
- centre region: `r <= Ri - Delta/2`;
- aperture crossing: the main-pool component must occupy the centre region
  below the lower ring face, inside the hole between the faces, and above the
  upper face at the same output time;
- isolated drops: every component other than the main pool, excluded;
- outer crown: all interface at `r > Ri - Delta/2`, excluded;
- numerical filaments: cells below `f=0.5` are excluded from the cell metric;
  the lower connectivity threshold is used only to establish topology;
- persistence: detected at two consecutive 0.5 ms outputs;
- PLIC check: reconstruct the `f=0.5` interface in every qualifying main-pool
  mixed cell and take the highest physical facet endpoint in the centre region.

These constants may not be changed to improve a reported height.

## Four distinct heights

1. `main_connected_height`: legacy maximum of the largest connected liquid
   component (`f > 1e-4`), including the crown.
2. `center_height`: legacy maximum within two cells of the axis.
3. `H_through`: highest `f >= 0.5` main-pool cell centre in the centre region,
   only when the aperture-crossing test passes; otherwise `NA`.
4. `H_PLIC`: highest qualifying reconstructed PLIC facet endpoint, subject to
   the same aperture and connectivity tests; otherwise `NA`.

`H_through` and `H_PLIC` never include isolated drops or the outer crown.
Their expected grid-scale difference is at most approximately one cell.

## Jet shape and continuity

`jet_detected` is the instantaneous aperture-crossing result.  Onset is the
first of two consecutive detections.  Base radius is the maximum liquid
radius within one cell above the upper face; tip radius is the maximum liquid
radius within one cell below the PLIC tip.  Column length is PLIC tip minus the
upper-face base.  Drop inclusion is always false by construction.  Persistence
and main-pool connection are written explicitly.

## Health, flux, and pressure

Every output records volume, expected volume, budget residual, wetting source,
kinetic energy, maximum speed and its `(x,r,f,cs)` location, minimum timestep,
cell count, component count, all four heights, and invalid values.

Liquid aperture flux is sampled in one-cell axial bands at the lower face
minus one cell, ring mid-plane, upper face plus one cell, and upper face plus
two cells.  It records `Q = integral 2*pi*r*f*u_x dr`, positive/negative parts,
liquid mass flow, axial momentum flux, liquid area, ring-frame mean velocity,
and laboratory velocity `u_x - U_ring` (the simulation velocity is in the
ring-fixed frame).

Basilisk `p` has pressure units (Pa in this SI configuration): `centered.h`
solves `du/dt = (-grad(p)+...)/rho + a`.  Its additive reference is fixed by
`p[right]=0`, so mechanism claims use local differences and gradients, not
absolute pressure.  Pressure/velocity bands cover the lower impact face,
inner lower edge, aperture axis, and upper inner edge; the diagnostic records
the inward radial and upward axial velocities and the phase/solid fractions
at the speed maximum.
