# Architecture

Current gate status: the general embedded VOF contact-line gate remains failed, but a user-authorized, isolated exploratory branch now uses the technically viable moderate-angle Tavares route. Its source remains outside the repository because the file-level license is unspecified. Results from this branch are qualitative and do not convert the failed validation gate into a pass.

## Coordinate convention

The axisymmetric meridional plane uses `x` as the axial (vertical) coordinate and `y` as radius. The domain must satisfy `y >= 0`; `bottom` is the symmetry axis. The flat ring section is the rectangle `Ri <= y <= Ro`, `-h/2 <= x <= h/2`.

## Candidate motion models

| Model | Strengths | Risks | Decision |
| --- | --- | --- | --- |
| Moving embedded boundary | Direct physical frame and natural acceleration history | Moving cut-cell geometry, contact-line treatment, conservation, and limited public validation | Separate experimental branch |
| Fixed ring in a translating frame | Keeps the cut geometry fixed, is compatible with axisymmetric VOF, and supports constant speed cleanly | Current tree/embed viscous path raises `SIGFPE`; external contact code also marks AMR as unfinished | Selected only with uniform grids for the first exploration |
| Brinkman or volume penalization | Easy geometry motion and complex solids | Penalization error, stiffness, force interpretation, and less direct cut-cell validation | Not the first model |

The first exploratory model was a fixed embedded ring in a constant-speed Galilean frame with axisymmetric VOF. It was run at `U=1 m/s` on uniform levels 7 and 8. The base level-7 branch is retained for manually reviewed morphology, while level 8 is retained only as evidence of numerical sensitivity.

Following explicit user authorization, the current exploratory extension uses the same fixed embedded geometry in a frame accelerating with the ring. A project-authored axisymmetric traction integral supplies pressure and viscous force to a vertical Newton equation. The laboratory ring position and speed are integrated explicitly, and the fluid receives the corresponding uniform fictitious acceleration. This produces actual laboratory-frame ring motion without changing cut-cell topology, but it is not a moving-embed method and does not validate moving-boundary conservation.

## Decision matrix

| Dimension | Moving embedded boundary | Fixed ring + translating frame | Brinkman penalization |
| --- | --- | --- | --- |
| Axi compatibility | Possible but geometry/metric coupling is delicate | Direct fixed `embed` plus `axi` | Possible, with porosity metric choices |
| VOF and contact line | Direct physical contact line, hardest numerically | Compatible, but contact line is a later boundary-condition task | Diffuse interface/contact line is model-dependent |
| Adaptive mesh | Tracks moving cut cells and topology | Deferred: the current `AXI + TREE + EMBED` viscous smoke test fails and the external contact header marks AMR as a fixme | Refines penalty layers and interfaces |
| Conservation | Requires moving-cut-cell flux care | Open-domain budget is measurable, but contact ghost cells produce non-monotonic residuals | Penalization introduces model error |
| Pressure force | Direct but time-dependent cut integration | Direct fixed-surface integration in frame | Requires volume-force interpretation |
| Surface entry/exit | Natural target, highest risk | Represented through translating free surface relative to fixed ring | Natural motion, diffuse solid transition |
| Variable speed | Native kinematics | Implemented exploratorily with non-inertial frame acceleration | Native forcing but stiff |
| Fluid-structure coupling | Best extension point | One-degree-of-freedom vertical force feedback implemented; full moving-boundary coupling remains unvalidated | Coupling is indirect |
| Stability | Moving topology and small cells are risky | Most stable first route | Stiff penalty parameter can limit dt |
| Complexity | High | Moderate | Moderate, with calibration burden |
| Public validation | Limited for this exact geometry | Closest to verified fixed-embed building blocks | Fewer directly comparable cases |

The level-8 peak has been localized to embedded/contact-line cells and adjacent liquid. A free-slip control reduces but does not remove its refinement amplification, and a half-cell axial phase shift substantially changes the level-7 cavity path after 20 ms. These controls rule out treating the visually preferred level-7 branch as grid-converged or using a wall-condition change as an uncalibrated fix.

The fixed-geometry accelerating-frame model has now completed a deep uniform-L7 run to 530 ms and a fixed-laboratory-frame speed animation. It preserves a long open annular cavity and the manually identified first-jet candidate, but it does not close the cavity or produce a credible Worthington jet. After roughly 390 ms, increasing interface corrugation, detached fragments, force oscillations, and a `22.63 m/s` global laboratory-speed peak make the late branch numerically suspect.

Before the later cavity-detachment experiment, the recommendation was to
freeze this L7 result as a qualitative baseline and compare it with laboratory
data before changing release height. Level 8 remains rejected for extension,
and force, wetting, cavity closure, and jet timing remain non-quantitative.

The subsequent 10 cm-release experiment falsifies the attached-cavity
topology of that baseline: the computed interface remains on the ring beyond
300 mm depth, while the experiment reports a fully wetted ring. Broad static
angle, surface-tension, and slip controls do not remove attachment.

A separate hybrid architecture is therefore admitted for qualitative
continuation. It keeps the original solver until a measured immersion-depth
event, then applies one local, one-time wetting transition and explicitly
accounts for the added mobile water. This is an experiment-constrained
topology scaffold, not a dynamic contact-line model. It must remain a separate
branch until the trigger depth is measured and the operation is replaced by a
validated wetting/detachment treatment.

The transition's historical one-sided level-set condition filled the complete
solid interior and is superseded. The only retained scaffold uses the true
two-sided band `-1.25 Delta <= ring_levelset <= 1.25 Delta`; uninterrupted L7
and L8 audits give zero deep-solid liquid. This correctness repair does not
promote the scaffold to a physical wetting law. L8 locally straightens the
first-jet silhouette near 62.5 ms but retains a doubled contact-edge speed
peak, so corrected L7 remains the exploratory working resolution.

The 26.15 g video audit adds a separate prescribed-trajectory mode to the
isolated fixed-ring frame. Pre-contact motion is ballistic; post-contact speed
is a continuous exponential fit to measured ring positions. This mode is
accepted only to remove trajectory error from a morphology test. It does not
replace the force-feedback model, validate hydrodynamic force, or predict a
new release condition.

The audit rejects the current fluid morphology more strongly than the earlier
height-only comparisons. L7 and short L8 miss a thin first jet already in the
30 ms holdout frame. L8 smooths the attached cavity walls but raises the
maximum laboratory speed from `5.39` to `18.65 m/s` over the common window,
and the speed peak remains below the free surface. L7 also fails the held-out
hourglass closure and later narrow-jet sequence, retaining corrugated cavity
fragments and a broad central pedestal instead.

Consequently, neither finer uniform resolution nor further static-angle or
surface-tension adjustment is the next architecture step. The empirical
one-time shell band remains a disclosed scaffold only. Case 15 now supplies
the first project-owned, license-clear dynamic-wetting branch on the fixed
embedded ring. Its physical-arclength front writes only full-solid ghost cells
and produces delayed detachment without mobile-liquid injection. The remaining
architecture gate is a pressure/geometry-aware gas-neck closure that improves
the video holdout jet and post-detachment topology before force feedback or new
release heights are revisited.
