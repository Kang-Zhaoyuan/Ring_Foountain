# T010 — True-Geometry Jet1 Diagnostic Evidence Task

Generated time: 2026-06-20 16:45 Asia/Shanghai

Active: YES

Source review: `reviews/20260620_164500_R010_review_and_plan.md`

## 0. Current repository state to respect

T004/T005/T006 repaired and validated the raw-array extraction/postprocessing path over nine baseline/contactline rows.

T007 recovered and validated D0/D1/D2 zero/micro-motion displacement semantics.

T008 passed a narrow D3/D4/D5 diagnostic displacement ladder numerically:

- D3 expected `-1e-05 m`, measured approximately `-1e-05 m`
- D4 expected `-2.5e-05 m`, measured approximately `-2.5e-05 m`
- D5 expected `-5e-05 m`, measured approximately `-5e-05 m`

T009 completed the visual/SVG/CSV-backed audit of T008 figures:

- `T008_DISPLACEMENT_RESPONSE_FIGURE_AUDITED = YES`
- `T008_ERROR_SUMMARY_FIGURE_AUDITED = YES`
- `T008_INTERFACE_QUALITY_FIGURE_AUDITED = YES`
- `T008_FIGURES_MATCH_SOURCE_TABLES = YES`
- `T008_NUMERIC_EVIDENCE_UNCHANGED = YES`

R010 therefore opens only one narrow next step: true-geometry Jet1 diagnostic evidence generation.

## 1. Hard gates

- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_PARAMETER_SWEEP = NO`
- `ALLOW_JET1_PHYSICAL_CONCLUSION = NO`
- `ALLOW_STAGE_ADVANCEMENT = NO`
- Do not claim physical fountain height.
- Do not output validated real Hmax.
- Do not run Stage 6.
- Do not run a broad parameter sweep.
- Do not produce Jet1/Jet2 physical conclusions.
- Do not overwrite previous T004/T005/T006/T007/T008/T009 evidence.

Allowed scope:

- `ALLOW_TRUE_GEOMETRY_JET1_DIAGNOSTIC = YES_NARROW_ONLY`
- `ALLOW_RAW_ARRAY_EXTRACTION = YES`
- `ALLOW_POSTPROCESSING_RECOMPUTE = YES`
- `ALLOW_AUDIT_FIGURES = YES`

This task may output `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = YES/NO` only as a recommendation for Review Agent. It must not open Stage 6 or real Hmax.

## 2. Required input files

Read these before doing any work:

1. `reviews/20260620_164500_R010_review_and_plan.md`
2. `reviews/20260620_164500_R010_run_trace.md`
3. `tasks/20260620_160000_T008_narrow_diagnostic_displacement_ladder.md`
4. `tasks/20260620_163000_T009_t008_visual_audit_completion.md`
5. `06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T008_final_report.md`
6. `06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T009_t008_visual_audit_report.md`
7. `06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T008_recomputed_metrics.csv`
8. `06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T009_t008_figure_manifest.csv`
9. Relevant R3 true-moving-geometry scripts and saved models needed to define a Jet1 diagnostic consistently.

If a required file is missing, record it explicitly and continue with available evidence. If Jet1 diagnostic semantics are ambiguous, stop and write `HUMAN_REQUIRED` rather than inventing definitions.

## 3. Output directory convention

Create a new T010-specific diagnostic directory:

```text
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/
├── reports/
├── tables/
├── images/
├── logs/
├── arrays/
├── models/
└── scripts/
```

Do not delete or overwrite previous evidence.

## 4. Main objective

Generate a narrow, auditable true-geometry Jet1 diagnostic evidence package.

This is not Stage 6. It is not a real Hmax task. It is not a Jet1 physical-conclusion task.

The diagnostic should answer only:

1. Can a true-geometry Jet1 diagnostic case be defined unambiguously from existing R3 semantics?
2. Can the case be run or loaded under bounded runtime?
3. Can raw arrays be extracted with the repaired postprocessing pipeline?
4. Are interface quality, displacement consistency, and diagnostic shape indicators auditable?
5. Is there enough evidence for Review Agent to decide whether a later, still-bounded Jet1 track is justified?

## 5. Required case scope

Run at most two diagnostic cases:

1. `J0_static_baseline_for_jet1_diagnostic`
2. `J1_true_geometry_jet1_diagnostic`

If model semantics are not recoverable, produce the semantics report and stop with `T010_STATUS = HUMAN_REQUIRED`.

If runtime is limited, complete J0 first and write durable progress before attempting J1.

## 6. Required work plan

### Phase A — Jet1 diagnostic semantics

Produce:

```text
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T010_A_jet1_semantics.md
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T010_case_manifest.csv
```

The semantics report must specify:

- source files used to recover Jet1 diagnostic definitions,
- exact model or script base,
- how J0 and J1 differ,
- whether any Stage 6 logic is excluded,
- whether real Hmax is excluded,
- whether the definitions are diagnostic-only,
- whether any ambiguity remains.

If ambiguity remains, stop before running models and write `T010_STATUS = HUMAN_REQUIRED`.

### Phase B — Build diagnostic script

Produce:

```text
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/scripts/T010_true_geometry_jet1_diagnostic.py
```

Requirements:

- Reuse repaired raw-array extraction/postprocessing functions where possible.
- Process one case at a time.
- Write per-case logs immediately.
- Write per-case raw or compact sampled arrays immediately under `arrays/`.
- Preserve exact exception class and message.
- Do not collapse failures into generic `extraction_failed`.
- Do not run Stage 6.
- Do not output real Hmax.

### Phase C — Execute bounded diagnostic

Run only J0/J1 if semantics are clear and COMSOL access is available.

Required outputs:

```text
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T010_progress.csv
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T010_recomputed_metrics.csv
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/logs/T010_*.log
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/arrays/T010_*.npz
```

### Phase D — Reviewer figures

If diagnostic metrics exist, generate both PNG and SVG/CSV-backed audit figures:

```text
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/images/T010_interface_quality_summary.png
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/images/T010_interface_quality_summary.svg
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/images/T010_diagnostic_shape_summary.png
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/images/T010_diagnostic_shape_summary.svg
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/images/T010_case_status_summary.png
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/images/T010_case_status_summary.svg
```

Also produce:

```text
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T010_figure_manifest.csv
```

Each figure manifest row must include original path, SVG path, source table, source columns, visual audit status, and notes.

### Phase E — Final report

Produce:

```text
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T010_final_report.md
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T010_gate_summary.json
```

The final report must explicitly state:

- `T010_STATUS = PASS/FAIL/PARTIAL/HUMAN_REQUIRED`
- `JET1_DIAGNOSTIC_SEMANTICS_RECOVERED = YES/NO/PARTIAL`
- `J0_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `J1_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `RAW_ARRAY_EXTRACTION_COMPLETED = YES/NO/PARTIAL`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED = YES/NO/PARTIAL`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED = YES/NO/PARTIAL`
- `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`
- `JET1_PHYSICAL_CONCLUSION_MADE = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = YES/NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## 7. README and task-index updates

Update README only in a bounded section if useful:

```text
<!-- TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC:START -->
...
<!-- TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC:END -->
```

Update `tasks/BUILDER_POLLING_LOG.csv` as usual.

Do not overwrite archived task files.

## 8. Final Codex response requirements

At the end of your run, report:

1. changed files,
2. generated files,
3. exact report paths,
4. exact table paths,
5. exact array paths,
6. exact image paths,
7. Jet1 diagnostic semantics source,
8. per-case diagnostic status,
9. whether MemoryError was resolved,
10. whether `interface_quality=extraction_failed` was resolved,
11. figure manifest path,
12. gate values,
13. next recommended task.

Do not answer only in chat. Push all generated outputs to GitHub.
