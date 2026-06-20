# T011 — Jet1 Threshold and ROI Semantics Audit

Generated time: 2026-06-20 17:00 Asia/Shanghai

Active: YES

Source review: `reviews/20260620_170000_R011_review_and_plan.md`

## 0. Current repository state to respect

T010 generated a narrow true-geometry Jet1 diagnostic evidence package from saved J0/J1 models.

T010 diagnostic pipeline status:

- `T010_STATUS = PASS`
- `JET1_DIAGNOSTIC_SEMANTICS_RECOVERED = YES`
- `J0_STATUS = PASS`
- `J1_STATUS = PASS`
- `RAW_ARRAY_EXTRACTION_COMPLETED = YES`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED = YES`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED = YES`
- `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`
- `JET1_PHYSICAL_CONCLUSION_MADE = NO`

T010 shape evidence:

- J0 `jet1_roi_max_delta_m = 6.0691962701962614e-06`, `shape_threshold_crossed=False`
- J1 `jet1_roi_max_delta_m = 4.34916959663216e-06`, `shape_threshold_crossed=False`

J1 does not exceed J0 under the reported ROI max-delta metric. Therefore T010 is not evidence of physical Jet1 detection.

The purpose of T011 is to audit Jet1 ROI and threshold semantics before any further Jet1 diagnostic expansion.

## 1. Hard gates

- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_PARAMETER_SWEEP = NO`
- `ALLOW_JET1_PHYSICAL_CONCLUSION = NO`
- `ALLOW_TRUE_GEOMETRY_JET1_DETECTION = NO`
- `ALLOW_STAGE_ADVANCEMENT = NO`
- Do not claim physical fountain height.
- Do not output validated real Hmax.
- Do not run Stage 6.
- Do not run a broad parameter sweep.
- Do not produce Jet1/Jet2 physical conclusions.
- Do not overwrite previous T004/T005/T006/T007/T008/T009/T010 evidence.

Allowed scope:

- `ALLOW_JET1_THRESHOLD_AUDIT = YES`
- `ALLOW_TABLE_RECOMPUTE_FROM_EXISTING_CSV = YES`
- `ALLOW_SVG_CSV_BACKED_AUDIT_FIGURES = YES`

This task should not run COMSOL unless strictly necessary to read already-saved metadata. Prefer report/table/script audit and deterministic recomputation from existing CSV/JSON/SVG evidence.

## 2. Required input files

Read these before doing any work:

1. `reviews/20260620_170000_R011_review_and_plan.md`
2. `reviews/20260620_170000_R011_run_trace.md`
3. `tasks/20260620_164500_T010_true_geometry_jet1_diagnostic.md`
4. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T010_final_report.md`
5. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T010_A_jet1_semantics.md`
6. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T010_gate_summary.json`
7. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T010_recomputed_metrics.csv`
8. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T010_figure_manifest.csv`
9. Fixed-geometry 5C ROI report: `05_two_phase_free_surface/5C_jet1_extraction/reports/B_jet1_definition_and_ROI_report.md`
10. Fixed-geometry 5C candidate/exclusion report: `05_two_phase_free_surface/5C_jet1_extraction/reports/D_jet1_candidate_detection_report.md`
11. Any available 5C tables/scripts defining threshold constants or exclusion logic.

If a required file is missing, record it explicitly and continue with available evidence.

## 3. Output directory convention

Continue using the T010 diagnostic directory, but use T011 filenames:

```text
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/
├── reports/
├── tables/
├── images/
├── logs/
└── scripts/
```

Do not delete or overwrite T010 outputs.

## 4. Main objective

Audit whether the current Jet1 ROI/threshold semantics are coherent and whether T010 supports any further true-geometry Jet1 diagnostic expansion.

This is an audit task only. It is not Stage 6, not a real Hmax task, and not a Jet1 detection task.

T011 should answer:

1. What exactly is the fixed-geometry 5C Jet1 ROI and threshold/exclusion logic?
2. Which parts of 5C logic are valid to reuse in true geometry, and which are only diagnostic analogues?
3. Why did T010 set `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = YES` despite `shape_threshold_crossed=False` for both J0 and J1?
4. Is J1-vs-J0 evidence positive, neutral, or negative under the current ROI metric?
5. What exact evidence would be required before any further Jet1 diagnostic run is justified?

## 5. Required work plan

### Phase A — Collect Jet1 threshold sources

Produce:

```text
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T011_A_threshold_source_audit.md
```

Include:

- all files inspected,
- ROI definitions found,
- threshold constants found,
- exclusion rules found,
- whether each source is fixed-geometry-only or true-geometry-compatible.

### Phase B — Recompute T010 threshold interpretation from existing table

Produce:

```text
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T011_threshold_recompute.csv
```

Required columns:

```text
case_id,legacy_case_id,source_case,roi_max_delta_m,shape_threshold_crossed,interface_quality,case_pass_after_recompute,HMAX_IS_REAL_PHYSICAL_OUTPUT,JET1_PHYSICAL_CONCLUSION_MADE,J1_minus_J0_delta_m,normalized_vs_J0,interpretation
```

The interpretation must be one of:

- `positive_diagnostic_evidence`
- `neutral_diagnostic_evidence`
- `negative_or_no_jet1_evidence`
- `ambiguous_requires_human_review`

### Phase C — Figure audit from existing CSV

Produce SVG/CSV-backed figures only:

```text
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/images/T011_j0_j1_roi_delta_comparison.svg
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/images/T011_threshold_decision_summary.svg
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T011_figure_manifest.csv
```

No new COMSOL run is required.

### Phase D — Final report and gate summary

Produce:

```text
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T011_final_report.md
06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T011_gate_summary.json
```

The final report must explicitly state:

- `T011_STATUS = PASS/FAIL/PARTIAL/HUMAN_REQUIRED`
- `JET1_THRESHOLD_SOURCES_RECOVERED = YES/NO/PARTIAL`
- `T010_THRESHOLD_INTERPRETATION_RECOMPUTED = YES/NO`
- `J1_VS_J0_EVIDENCE = POSITIVE/NEUTRAL/NEGATIVE/AMBIGUOUS`
- `T010_ALLOW_NEXT_TRUE_GEOMETRY_JET1_CONSISTENT_WITH_THRESHOLD = YES/NO/PARTIAL`
- `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`
- `JET1_PHYSICAL_CONCLUSION_MADE = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = YES/NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## 6. README and task-index updates

Update README only in a bounded section if useful:

```text
<!-- TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC:START -->
...
<!-- TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC:END -->
```

Update `tasks/BUILDER_POLLING_LOG.csv` as usual.

Do not overwrite archived task files.

## 7. Final Codex response requirements

At the end of your run, report:

1. changed files,
2. generated files,
3. exact report paths,
4. exact table paths,
5. exact figure paths,
6. threshold source files inspected,
7. J1-vs-J0 interpretation,
8. whether T010's Jet1 recommendation was consistent with threshold evidence,
9. gate values,
10. next recommended task.

Do not answer only in chat. Push all generated outputs to GitHub.
