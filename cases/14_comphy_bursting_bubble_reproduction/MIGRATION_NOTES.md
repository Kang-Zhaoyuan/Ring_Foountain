# Migration notes

Date: 2026-07-18

## Purpose

Archive the independently created Bursting-Bubble reproduction evidence in the
Ring Fountain history without vendoring GPL-3.0 source, external capsule
payloads, build products, or large solver output.

## Process

1. Confirmed Ring Fountain was clean at
   `ed903d56101332309651d8decc51831e3596570d`.
2. Read the repository rules and followed the evidence-only structure used by
   case 13.
3. Created `cases/14_comphy_bursting_bubble_reproduction/`; no historical case
   or ignored `runs/` directory was modified.
4. Copied audit-authored reports, parameter records, process/status logs,
   numerical tables, PLIC streams, plots, and source-form audit utilities.
5. Adjusted the migrated analysis path to use the case-local tables/figures.
   Adjusted dump extraction to accept the independent reproduction root.
6. Added this migration record, a human entry-point README, explicit licence
   boundary, tool instructions, requirements lock, inclusion/exclusion ledger,
   and repository-verifiable artifact manifest.
7. Updated the root stage list, validation record, and required handoff without
   changing the ring-physics next gate.
8. Recorded the original `environment.txt` SHA-256, then removed UTF-16 NUL and
   invalid residual bytes emitted by `wsl.exe --version` so the migrated log is
   valid UTF-8. No other environment content was changed.

## Excluded material

- the entire `upstream/` clone and `.git` history;
- all Bursting-Bubble and Basilisk source/install content originating outside
  this audit, including the downloaded installer;
- SingularJets2026 capsule payloads and its GPL scripts, data, Git bundle,
  virtual environment, and installed Python;
- qcc, compiled postprocessors, the compiled audit helper, objects, dumps,
  restarts, snapshots, and simulation case directories;
- the 26 MB uv release archive and downloaded GitHub release JSON.

`external_run_checksums.sha256` is retained as historical provenance for the
independent report tree; it is not expected to verify inside this case.
`artifact_manifest.sha256` is the manifest intended for repository checkout
verification.

## Migration validation

- The migrated analyzer ran against only the case-local TSV/PLIC evidence with
  exit status 0. Five summary tables and six required PNG figures were
  byte-identical before and after regeneration.
- `audit_snapshot.c` compiled to a temporary directory with both the pinned
  isolated qcc and Ring Fountain authority `/home/kqdx/basilisk/src/qcc`.
  Both binaries restored external case 2808 snapshot `t=0.5`, exited 0, and
  emitted byte-identical metrics: volume `1880.8251958975097`, KE
  `4.2869830048629183`, maximum speed `31.219776628808503`, 7,294 leaves, and
  minimum Delta `0.0390625`.
- No executable or external solver/capsule payload is present in case 14. The
  final UTF-8, relative-link, environment, whitespace, and artifact-manifest
  checks are recorded in `logs/migration_validation.log`.

No commit or push was performed by Codex. Push remains manual.
