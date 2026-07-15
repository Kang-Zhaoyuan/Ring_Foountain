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

## Repository status

- Git is no longer blocked. The repository is initialized on `main`, tracks `origin/main`, and local Git metadata is writable.
- The repository history begins with `fb92e59` (`Initial commit - full overwrite`).
- Historical note: the requested seven stage-by-stage commits were not created during the original setup window. The current history starts from a single initial commit instead.
- Push remains manual by user choice; this workspace should not push automatically.

## Next gate

Do not proceed to the translating-frame or any moving-ring stage. The only next action is to identify and license-review a maintained Basilisk implementation that explicitly supports VOF contact lines on fixed embedded boundaries, then validate it in an isolated canonical case with `/home/kqdx/basilisk/src/qcc`. The ring geometry may be revisited only after that gate passes.
