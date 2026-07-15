# Architecture

## Coordinate convention

The axisymmetric meridional plane uses `x` as the axial (vertical) coordinate and `y` as radius. The domain must satisfy `y >= 0`; `bottom` is the symmetry axis. The flat ring section is the rectangle `Ri <= y <= Ro`, `-h/2 <= x <= h/2`.

## Candidate motion models

| Model | Strengths | Risks | Decision |
| --- | --- | --- | --- |
| Moving embedded boundary | Direct physical frame and natural acceleration history | Moving cut-cell geometry, contact-line treatment, conservation, and limited public validation | Separate experimental branch |
| Fixed ring in a translating frame | Keeps the cut geometry fixed, compatible with axisymmetric VOF and adaptive refinement, and supports constant speed cleanly | Requires careful frame acceleration and boundary-condition bookkeeping for variable speed | Default first dynamic route |
| Brinkman or volume penalization | Easy geometry motion and complex solids | Penalization error, stiffness, force interpretation, and less direct cut-cell validation | Not the first model |

The first dynamic target is therefore a fixed embedded ring in a Galilean frame with axisymmetric VOF. Variable-speed extensions add the appropriate non-inertial acceleration only after the constant-speed case is validated. This round does not implement motion.

## Decision matrix

| Dimension | Moving embedded boundary | Fixed ring + translating frame | Brinkman penalization |
| --- | --- | --- | --- |
| Axi compatibility | Possible but geometry/metric coupling is delicate | Direct fixed `embed` plus `axi` | Possible, with porosity metric choices |
| VOF and contact line | Direct physical contact line, hardest numerically | Compatible, but contact line is a later boundary-condition task | Diffuse interface/contact line is model-dependent |
| Adaptive mesh | Tracks moving cut cells and topology | Stable geometry, simpler boundary-focused refinement | Refines penalty layers and interfaces |
| Conservation | Requires moving-cut-cell flux care | Best controlled for constant speed | Penalization introduces model error |
| Pressure force | Direct but time-dependent cut integration | Direct fixed-surface integration in frame | Requires volume-force interpretation |
| Surface entry/exit | Natural target, highest risk | Represented through translating free surface relative to fixed ring | Natural motion, diffuse solid transition |
| Variable speed | Native kinematics | Add non-inertial frame acceleration | Native forcing but stiff |
| Fluid-structure coupling | Best extension point | Needs force feedback in fixed-frame formulation | Coupling is indirect |
| Stability | Moving topology and small cells are risky | Most stable first route | Stiff penalty parameter can limit dt |
| Complexity | High | Moderate | Moderate, with calibration burden |
| Public validation | Limited for this exact geometry | Closest to verified fixed-embed building blocks | Fewer directly comparable cases |

The current recommendation is fixed geometry plus a constant-speed Galilean frame, followed by a separate variable-speed frame-acceleration study. A moving embedded boundary should remain an experimental branch until conservation, pressure force, and contact-line tests exist.
