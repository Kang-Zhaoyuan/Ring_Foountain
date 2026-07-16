# Handoff

Date: 2026-07-16

## Current state

- WSL2 Ubuntu environment gate passed.
- Project root is `/home/kqdx/basilisk_work/ring_fountain`.
- Basilisk is used read-only from `/home/kqdx/basilisk/src`.
- Stage 1 scaffolding, reference audit, official tests, publication smoke test, and static ring geometry are present.
- The three pre-ring validation gates passed before the static geometry case was entered.
- Static geometry converges from 2.416% to 0.280% relative volume error over maxlevel 5 to 7.
- The general fixed-ring/free-surface/embedded-contact-line validation gate was audited on 2026-07-15 and remains failed. On 2026-07-16 the user authorized a separate constrained exploration using the technically viable moderate-angle Tavares route without claiming license clearance or quantitative convergence.
- The requested header stack compiles, but the installed Basilisk tree has no embedded contact-angle/contact-line API; the minimal initialization probe also terminates with `SIGFPE` in `viscosity-embed.h:116` before completing one step.
- External Popinet/Tavares `contact-embed.h` candidates were license-reviewed and privately tested at three uniform levels. They were not copied into the project: their file-level license is unspecified, they are outside maintained `/src`, and final parasitic velocity worsened with refinement.
- The MIT `rcsc-group/BioReactor` repository was also screened, but its contact-angle option applies to domain boundaries rather than its embedded boundary.
- The user-supplied Tavares et al. 2024 paper was read and hashed. The complete public implementation/test listing was downloaded to ignored read-only vendor storage and frozen in `references/contact_embed_sources.lock`.
- Exact-source qcc object builds pass for the cylinder, gravity, 3-D sessile, impact, and slip tests. The current 2-D sessile page and slot page are broken; page history explicitly describes the sessile include fix as `still broken`.
- The author cylinder case and a current-API flat sessile port were run at three levels and three angles each. All 18 runs completed without invalid values and retained diagnostics, interfaces, solid facets, and dumps. Moderate 75/90-degree cases can relax cleanly, but extreme-angle velocity/curvature and sessile radius/mass metrics fail general refinement convergence.
- The earlier `t=0.5` terminal-velocity result is now treated as preliminary because the paper uses long static relaxation. The long-time reproduction still rejects the route as a general validated dependency.
- A fixed-ring Galilean-frame model with prescribed `U=1 m/s`, physical water/air properties, gravity, surface tension, and 75 deg contact angle was built and run only in an isolated directory. No external header, temporary source, or executable entered the repository.
- The quadtree version compiled but raised `SIGFPE` in `viscosity-embed.h:116` at the first viscous solve. A quadtree inviscid control and a viscous uniform-grid control both reached 5 ms, so the exploratory route is restricted to uniform multigrid.
- The 75 deg no-slip 120 x 60 mm level-7 and level-8 runs completed to 60 ms with zero invalid values, zero deep-solid liquid, and no outlet water. Maximum water-budget residuals were 1.856% and 3.594%; maximum lab-frame speeds were 2.831 and 17.311 m/s. The level-8 peak is in liquid on the lower embedded face, not in a resolved free jet.
- The user manually judged the base level-7 4--60 ms sequence qualitatively consistent with the expected early crown and first-upward-event development. This visual agreement is recorded separately from numerical validation.
- A 180 x 60 mm level-7 continuation completed to 120 ms with zero invalid values and leakage. Its maximum budget residual was 1.818%; the late 6.593 m/s maximum is again an embedded-ring cut cell. The later interface sequence is not automatically labeled as cavity closure, a Worthington jet, or any specific mechanism.
- A 90 deg level-7 run completed to 12 ms. Its 4, 8, and 12 ms interfaces nearly coincide with the 75 deg result, so early bulk shape is not highly sensitive to this moderate angle change on that grid.
- Free-slip embedded-wall controls completed to 30 ms. They reduced the level-8 peak from 11.807 to 5.966 m/s over the same window, but free-slip L8 remained 2.28 times L7 and retained the worse mass residual. Free-slip is not adopted as uncalibrated metal physics.
- A no-slip level-7 half-cell axial grid-phase control also completed to 30 ms. The interface diverged from the base run after about 20 ms; maximum lab speed changed from 2.831 to 1.355 m/s while maximum budget residual changed from 1.856% to 2.672%. The visually preferred base L7 result is therefore also cut-cell-phase dependent.
- The base no-slip level-7 branch is retained only for qualitative manual morphology review. Level 8 is no longer extended, and neither a fabricated Navier length nor free-slip is accepted as an optimization.

## Repository status

- Git is no longer blocked. The repository is initialized on `main`, tracks `origin/main`, and local Git metadata is writable.
- The repository history begins with `fb92e59` (`Initial commit - full overwrite`).
- At the start of this round, local `main` and `origin/main` both pointed to `5dbe594` (`Reproduce embedded contact-line paper cases`).
- Historical note: the requested seven stage-by-stage commits were not created during the original setup window. The current history starts from a single initial commit instead.
- Push remains manual by user choice; this workspace should not push automatically.

## Next gate

Do not add free fall, force coupling, moving embed, a second-jet model, or a parameter sweep. The only next action is to manually classify the existing base level-7 50--120 ms sequence against the laboratory chronology before selecting any denser level-7 output window around an observed cavity-closure interval.
