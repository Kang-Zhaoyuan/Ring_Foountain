# Case 17 iteration log

All tests keep the Case 12 geometry, fitted trajectory and water properties.
The screening runs are diagnostic rejections, not accepted calibrations.

| iteration | change | result at 52.5 ms | decision |
| --- | --- | --- | --- |
| Case 16 rerun | unchanged L7 baseline | `H_through=6.7173 mm`, `H_PLIC=7.1522 mm` | reproducibility PASS; height FAIL |
| axial impulse | compact upward acceleration below the hole | pressure projection removed most of the imposed motion | reject |
| aperture relaxation | relax axial speed in the open centre | did not propagate a resolved thin column | reject |
| converging sheet, `Cd=0.4`, L6 | continuity-scaled radial inflow below annulus | native material height `5.78 mm` | reject as height model |
| converging sheet, `Cd=1`, L6 | stronger radial inflow | native material height `10.1 mm`; peak speed `14.35 m/s` | reject as height model |
| longer early decay | extend forcing duration | no material improvement | reject |
| accepted architecture | L7 bulk CFD plus visible-tip subgrid ODE | first jet `105.80 mm`; later-jet checkpoints within stated uncertainty | accept as calibrated hybrid |

The rejected continuum attempts establish a practical resolution limit: L7 has
`Delta=0.9375 mm`, only 3.05 cells through the ring thickness, while the
experimental tip is a thin, partly disconnected chain.  The accepted model
therefore does not relabel the short connected VOF column as a 105.8 mm jet.
It reports the native CFD and the calibrated visible-tip height separately.

The subgrid trajectory solves

`dv/dt = -g - beta*v`, `dh/dt = v`,

with one pair of coefficients for the impact jet and one for the post-closure
Worthington jet.  The 17.5 ms first-jet launch boundary is fixed by frame 335,
which contains crown splash and an open cavity but no resolved tall centre
column.  The 110 ms later launch is fixed by the observed relaxed surface at
frame 520 and onset at frame 550.  Coefficients are then fit only to the target
pairs in `calibration_targets.tsv`.
