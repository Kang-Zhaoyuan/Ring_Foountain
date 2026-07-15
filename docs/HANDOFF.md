# Handoff

Date: 2026-07-15

## Current state

- WSL2 Ubuntu environment gate passed.
- Project root is `/home/kqdx/basilisk_work/ring_fountain`.
- Basilisk is used read-only from `/home/kqdx/basilisk/src`.
- Stage 1 scaffolding, reference audit, official tests, publication smoke test, and static ring geometry are present.
- The three pre-ring validation gates passed before the static geometry case was entered.
- Static geometry converges from 2.416% to 0.280% relative volume error over maxlevel 5 to 7.
- The fixed-ring/free-surface/embedded-contact-line gate was audited on 2026-07-15 and is blocked/rejected.
- The requested header stack compiles, but the installed Basilisk tree has no embedded contact-angle/contact-line API; the minimal initialization probe also terminates with `SIGFPE` in `viscosity-embed.h:116` before completing one step.
- External Popinet/Tavares `contact-embed.h` candidates were license-reviewed and privately tested at three uniform levels. They were not copied into the project: their file-level license is unspecified, they are outside maintained `/src`, and final parasitic velocity worsened with refinement.
- The MIT `rcsc-group/BioReactor` repository was also screened, but its contact-angle option applies to domain boundaries rather than its embedded boundary.
- The user-supplied Tavares et al. 2024 paper was read and hashed. The complete public implementation/test listing was downloaded to ignored read-only vendor storage and frozen in `references/contact_embed_sources.lock`.
- Exact-source qcc object builds pass for the cylinder, gravity, 3-D sessile, impact, and slip tests. The current 2-D sessile page and slot page are broken; page history explicitly describes the sessile include fix as `still broken`.
- The author cylinder case and a current-API flat sessile port were run at three levels and three angles each. All 18 runs completed without invalid values and retained diagnostics, interfaces, solid facets, and dumps. Moderate 75/90-degree cases can relax cleanly, but extreme-angle velocity/curvature and sessile radius/mass metrics fail general refinement convergence.
- The earlier `t=0.5` terminal-velocity result is now treated as preliminary because the paper uses long static relaxation. The long-time reproduction still rejects the general route on broader evidence.

## Repository status

- Git is no longer blocked. The repository is initialized on `main`, tracks `origin/main`, and local Git metadata is writable.
- The repository history begins with `fb92e59` (`Initial commit - full overwrite`).
- At the start of this round, local `main` and `origin/main` both pointed to `e890cc7` (`Validate static embedded contact-line gate`). The author-source reproduction commit from this round remains local and unpushed.
- Historical note: the requested seven stage-by-stage commits were not created during the original setup window. The current history starts from a single initial commit instead.
- Push remains manual by user choice; this workspace should not push automatically.

## Next gate

Do not proceed to the ring geometry, translating-frame, or any moving-ring stage. The only next action is to ask the implementation authors for an explicitly licensed, immutable source revision matching the 2024 paper together with the original validation inputs/data. Any supplied revision must repeat the isolated multi-angle refinement test and improve the failed extreme-angle and sessile metrics before the ring geometry is revisited.
