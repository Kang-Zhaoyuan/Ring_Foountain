# T007 — Diagnostic D0/D1/D2 Displacement Regression with Repaired Postprocessing

Generated time: 2026-06-20 15:45 Asia/Shanghai

Active: YES

Source review: `reviews/20260620_154500_R007_review_and_plan.md`

## 0. Current repository state to respect

T006 completed the R3 raw-array extraction/postprocessing repair track for the targeted static/contactline baseline set.

T004/T005/T006 now provide nine recomputed PASS rows:

- `G2_ring_deeper_submerged`
- `G3_ring_far_below_surface`
- `W10_plain_wall_no_wettedwall_diagnostic`
- `W0_current_wettedwall`
- `W2_contact_angle_60deg`
- `W3_contact_angle_120deg`
- `W4_contact_angle_150deg`
- `W7_user_defined_slip_0p1mm`
- `W8_user_defined_slip_0p5mm`

For all nine rows, extraction and postprocess passed, `interface_quality = clear`, and `memory_error_resolved = YES`.

Historical R1 zero/micro-motion regression failed:

- `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/reports/D_zero_and_micro_motion_regression_report.md`
- D0/D1/D2 case pass flags were all false.
- `Hmax` remained `not_real_Hmax`.
- `ALLOW_DISPLACEMENT_LADDER = NO`.

The purpose of T007 is not to advance physics, but to revisit that narrow D0/D1/D2 regression using the repaired R3 raw-array extraction/postprocessing workflow.

## 1. Hard gates

- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_TRUE_GEOMETRY_JET1_DETECTION = NO`
- `ALLOW_PARAMETER_SWEEP = NO`
- Do not claim physical fountain height.
- Do not run Stage 6.
- Do not run a broad parameter sweep.
- Do not generate Jet1/Jet2 physical conclusions.
- Do not overwrite previous T004/T005/T006 evidence.

Allowed scope:

- `ALLOW_DIAGNOSTIC_D0_D1_D2_RERUN = YES`
- `ALLOW_RAW_ARRAY_EXTRACTION = YES`
- `ALLOW_POSTPROCESSING_RECOMPUTE = YES`

This task may output `ALLOW_NEXT_DISPLACEMENT_LADDER = YES/NO` only as a recommendation to the Review Agent. It must not open Stage 6 or real Hmax.

## 2. Required input files

Read these before doing any work:

1. `reviews/20260620_154500_R007_review_and_plan.md`
2. `reviews/20260620_154500_R007_run_trace.md`
3. `tasks/20260620_153000_T006_finish_remaining_contact_angle_slip_extraction.md`
4. `06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T006_final_report.md`
5. `06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T006_merged_T004_T005_T006_metrics.csv`
6. `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/reports/D_zero_and_micro_motion_regression_report.md`
7. The script that generated the old R1 D0/D1/D2 regression, if available.
8. Relevant R1/R2/R3 true-moving-geometry scripts and logs needed to reproduce D0/D1/D2 definitions.

If a required file is missing, record it explicitly and continue with available evidence.

## 3. Output directory convention

Create a new T007-specific output directory:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/
├── reports/
├── tables/
├── images/
├── logs/
├── arrays/
├── models/
└── scripts/
```

Do not delete or overwrite previous R1/R2/R3/T004/T005/T006 outputs.

## 4. Main objective

Reproduce or rebuild only the D0/D1/D2 zero/micro-motion diagnostic regression, using the repaired R3 raw-array extraction and postprocessing method.

This is a diagnostic regression rerun. It is not Stage 6 and not a physical Hmax result.

## 5. Required case scope

Use the original D0/D1/D2 definitions if they can be recovered from prior scripts/reports. If the exact definitions cannot be recovered, stop and write `HUMAN_REQUIRED` rather than inventing new amplitudes.

Required cases:

1. `D0_zero_motion_regression`
2. `D1_micro_motion_regression`
3. `D2_micro_motion_regression`

Recommended baseline source:

- Use the repaired R3 baseline/contactline evidence from T004/T005/T006 to select the cleanest static baseline candidate.
- Record which baseline candidate is used and why.

## 6. Required work plan

### Phase A — Recover D0/D1/D2 semantics

Produce:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T007_A_d0_d1_d2_semantics.md
06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T007_case_manifest.csv
```

The semantics report must specify:

- source files used to recover D0/D1/D2 definitions,
- displacement or motion settings for each case,
- baseline model/case used,
- whether the definitions exactly match historical R1 semantics,
- whether any ambiguity remains.

If definitions are ambiguous, stop before running new models and write `T007_STATUS = HUMAN_REQUIRED`.

### Phase B — Build or patch diagnostic script

Produce:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/scripts/T007_d0_d1_d2_displacement_regression.py
```

Requirements:

- Reuse the repaired raw-array extraction/postprocessing functions where possible.
- Process exactly one D case at a time.
- Write per-case logs immediately.
- Write per-case raw or compact sampled arrays immediately under `arrays/`.
- Preserve exact exception class and message.
- Do not collapse failures into generic `extraction_failed`.
- Do not run Stage 6.
- Do not output real Hmax.

### Phase C — Execute bounded diagnostic regression

Run only D0/D1/D2 if COMSOL access is available.

Required outputs:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T007_progress.csv
06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T007_recomputed_metrics.csv
06_true_moving_geometry_R3_diagnostic_displacement_regression/logs/T007_*.log
06_true_moving_geometry_R3_diagnostic_displacement_regression/arrays/T007_*.npz
```

### Phase D — Reviewer figures

If diagnostic metrics exist, generate:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T007_d0_d1_d2_status_summary.png
06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T007_displacement_response_summary.png
06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T007_interface_quality_summary.png
```

If images cannot be generated, write the exact reason and commands in the final report.

### Phase E — Final report

Produce:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T007_final_report.md
06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T007_gate_summary.json
```

The final report must explicitly state:

- `T007_STATUS = PASS/FAIL/PARTIAL/HUMAN_REQUIRED`
- `D0_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `D1_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `D2_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `D0_D1_D2_SEMANTICS_RECOVERED = YES/NO/PARTIAL`
- `RAW_ARRAY_EXTRACTION_COMPLETED = YES/NO/PARTIAL`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED = YES/NO/PARTIAL`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED = YES/NO/PARTIAL`
- `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = YES/NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## 7. README and task-index updates

Update README only in a bounded section if useful:

```text
<!-- TRUE_GEOMETRY_R3_DIAGNOSTIC_DISPLACEMENT_REGRESSION:START -->
...
<!-- TRUE_GEOMETRY_R3_DIAGNOSTIC_DISPLACEMENT_REGRESSION:END -->
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
6. exact image paths or reason images were not generated,
7. D0/D1/D2 semantics source,
8. per-case diagnostic status,
9. whether MemoryError was resolved,
10. whether `interface_quality=extraction_failed` was resolved,
11. gate values,
12. next recommended task.

Do not answer only in chat. Push all generated outputs to GitHub.
