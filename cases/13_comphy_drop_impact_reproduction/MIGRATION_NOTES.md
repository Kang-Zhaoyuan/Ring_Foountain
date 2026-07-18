# Migration notes

Date: 2026-07-18

## Purpose

Move only the material newly created during the independent Drop-Impact audit
into the Ring Fountain history, so the result can be reviewed and pushed
without vendoring a repository that is already available from GitHub.

## Process

1. Confirmed the Ring Fountain worktree was clean at commit
   `90f91c0b17f5402532f3d9b4c56d2e359a1d4ed9` before migration.
2. Reviewed the existing case numbering, README stage list, validation record,
   handoff, requirements policy, ignore rules, and licensing conventions.
3. Created `cases/13_comphy_drop_impact_reproduction/` without modifying or
   overwriting any historical case or `runs/` archive.
4. Copied only audit-created inputs, reports, logs, status records, numerical
   tables, PLIC data, and figures from the independent reproduction report.
5. Added the two audit sources created during that work. No compiled helper was
   copied. `analyze_results.py` was adjusted only to accept an explicit
   `--reproduction-root`, because the pinned clone remains external.
6. Added a source lock, license boundary, inclusion/exclusion log, case-local
   optional Python dependency lock, and a repository-verifiable artifact
   manifest.
7. Updated the root stage list, validation record, handoff, and requirements
   wording. The existing ring-physics next gate was not changed.

## Exclusion decision

Nothing originating from the GitHub checkout was added: no solver or helper
source, shell script, Git object, license file, Basilisk installer/tree, qcc,
binary, object, dump, restart, snapshot, MP4, virtual environment, or installed
package. The full upstream identity is represented by immutable SHA/ref records
instead. `external_run_checksums.sha256` is retained because it was generated
by the audit; it is explicitly labelled as an external historical manifest.

## Migration validation

- The adjusted Python aggregator ran against the independent pinned clone with
  exit status 0. All regenerated tables and figures were byte-identical to the
  pre-migration copies.
- The migrated `snapshot_metrics.c` compiled with the independent pinned qcc
  to a temporary path with exit status 0. Reading case 1808 snapshot `t=0.1`
  also exited 0 and reported volume `4.1876815946826378`, kinetic proxy
  `1.9373986201790088`, maximum speed `5.8071119578513599`, 4,297 leaf cells,
  minimum Delta `0.03125`, and zero invalid values.
- The same migrated source also compiled with the Ring Fountain authority
  `/home/kqdx/basilisk/src/qcc` and read that snapshot with byte-identical
  numerical output. The pinned isolated qcc remains authoritative for the
  scientific reproduction; the second build is only a repository compatibility
  check.
- No executable, dump, MP4, or named upstream Drop-Impact source is present in
  case 13.
- `make env-check`, Markdown relative-link checks, UTF-8 checks,
  `git diff --check`, and the final case artifact-manifest verification passed.

Generated validation outputs are retained in `logs/migrated_*` and
`logs/migration_validation.log`. No Git push was performed.
