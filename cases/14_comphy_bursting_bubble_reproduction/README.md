# Independent CoMPhy Bursting-Bubble reproduction audit

This evidence-only case archives the project-created results of the independent
Bursting-Bubble audit executed on 2026-07-18. It is not a Ring Fountain solve
and does not advance the ring-physics validation gate.

## Outcome

- SingularJets2026 offline capsule: **PASS** — 211 payload hashes, frozen
  Python 3.12 environment, primary Fig. 2 regeneration, and 7/7 offline frozen
  regressions passed.
- Minimum plain-solver reproduction: **PASS** — unchanged source compiled;
  identical L8 cases reproduced logs, dump metrics, and common-time PLIC
  exactly; the Oh control and L10 run completed normally.
- Scientific jet baseline: **PARTIAL** — L8 and L10 disagree strongly in jet
  onset, height, energy, PLIC position, and local speed. L11 was not started
  because its measured-cost estimate is about 86 minutes, above the explicit
  60-minute gate.

`Bond` only selects a precomputed initial shape in the audited solver; the
momentum equation has no gravity term. The paper capsule's L13--L15 drill-solver
data are offline archived evidence, not locally recomputed plain-solver data.

Start with [REPRODUCTION_REPORT.md](REPRODUCTION_REPORT.md), then review
[CAPSULE_REPORT.md](CAPSULE_REPORT.md),
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md), and
[LICENSE_BOUNDARY.md](LICENSE_BOUNDARY.md).

## Included

- complete independent command/environment/status logs, including failed and
  recovered attempts;
- audit-created parameter records, scalar/jet/resource tables, PLIC streams,
  and review figures;
- project-authored read-only audit and analysis source;
- immutable upstream/ref/tool hashes and the historical external-workspace
  checksum manifest.

## Deliberate exclusions

No Bursting-Bubble checkout, Git object, solver/postprocessor source, Basilisk
installer/tree, qcc, executable, object, dump, restart, snapshot, capsule
payload, uv archive, virtual environment, installed package, or HPC source
bundle is tracked. See [MIGRATION_NOTES.md](MIGRATION_NOTES.md) for the exact
boundary.

## Verification

From the Ring Fountain root:

```sh
sha256sum -c cases/14_comphy_bursting_bubble_reproduction/artifact_manifest.sha256
git diff --check
```

The numerical aggregator can be rerun with the optional dependencies listed in
`tools/requirements.txt`; it consumes only the migrated tables and PLIC data.
Dump extraction additionally requires the independent pinned workspace.
