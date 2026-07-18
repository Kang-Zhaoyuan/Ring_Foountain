# Licence and repository boundary

The independent upstream checkout, its local Basilisk installation, compiled
binaries, dumps, and simulation output remain only under
`/home/kqdx/basilisk_work/reproductions/bursting_bubble_20260718/`. This
Ring Fountain case is an evidence-only archive.

- Bursting-Bubble source and scripts are GPL-3.0. The compiled upstream
  post-processors and copied capsule scripts remain inside this independent
  audit tree.
- SingularJets2026 data, extracted arrays, metadata, and rendered figures are
  CC BY 4.0 under its `LICENSE-DATA.md`; capsule scripts remain GPL-3.0.
- `tools/audit_snapshot.c`, metric definitions, extraction orchestration, and
  analysis code were created for this audit and are archived here in source
  form. They are audit utilities, not Ring Fountain solver code. No compiled
  helper is distributed.
- Ring Fountain and the frozen Drop-Impact reproduction were read only. No GPL
  solver source, Basilisk installation, binary, dump, numerical result, or
  physical assumption was migrated to Ring Fountain.

Only methods are candidates for later physics-work migration: source/ref locking, isolated
toolchains, unique case identifiers, dump-derived conservation/resource
audits, and common-time PLIC comparison. Any code reuse requires a separate
licence review.
