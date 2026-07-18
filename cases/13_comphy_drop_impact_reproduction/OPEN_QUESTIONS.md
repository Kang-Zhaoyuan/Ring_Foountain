# Open questions

1. What physical wetting/contact-angle model is intended at the solid plane? The solver applies `f[left] = 0` but defines no static or dynamic contact angle. This can materially affect the lamella and footprint, so it needs an upstream physics decision before long-time validation.
2. Which time convention should be public? Solver time is `tU/R`, while the input `tmax` is multiplied by `sqrt(We)` and is therefore naturally capillary-inertial time. The current comments call the input convective time.
3. Should `tsnap` be wired into the solver? It is parsed and printed, but the source uses compile-time `TSNAP = 0.01`.
4. Is `Ohs` meant to be a conventional gas Ohnesorge number? The code sets `mu2 = Ohs/sqrt(We)` while `rho2 = rho_ratio`; a gas-density-based definition would scale differently.
5. Should footprint be measured at a fixed dimensional height, a fixed `x/R`, or relative to local finest-cell width? At L8 the native cutoffs 0.001--0.01 lie below the first cell center and return zero; this audit uses `x/R <= 0.05`.
6. What duration defines the true maximum spreading? The present `tmax=0.1` grid study only reaches solver time 0.316 and the largest footprint is still at the final snapshot.
7. Should the default L14 run proceed? The short-run extrapolation is about 21.7 hours; the default `tmax=1` extrapolation is about 9 days and may generate 6.5--23.5 GB. Confirmation is required by the stated resource gate.
8. Should upstream documentation be corrected in a separate contribution? `axi.h` uses axial `x`, radial `y`, with `y=0` as the axis; several Drop-Impact comments reverse these labels.
9. Should an explicit scalar volume diagnostic and maximum-CFL/velocity diagnostic be added upstream? This audit computed them read-only from snapshots, but native logs only contain iteration, `dt`, time and kinetic energy.
