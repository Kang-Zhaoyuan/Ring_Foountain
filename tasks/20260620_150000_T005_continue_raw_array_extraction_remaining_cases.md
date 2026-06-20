# T005 — Continue Raw-Array Extraction for Remaining R3 Priority Cases

Generated time: 2026-06-20 15:00 Asia/Shanghai

Active: YES

Source review: `reviews/20260620_150000_R005_review_and_plan.md`

## 0. Current repository state to respect

T004 made partial but real progress. It successfully extracted raw arrays and recomputed postprocessing metrics for two ring-geometry cases:

- `G2_ring_deeper_submerged`: extraction PASS, postprocess PASS, `interface_quality = clear`, `memory_error_resolved = YES`
- `G3_ring_far_below_surface`: extraction PASS, postprocess PASS, `interface_quality = clear`, `memory_error_resolved = YES`

T004 remains incomplete:

- `T004_STATUS = PARTIAL`
- `RAW_ARRAY_EXTRACTION_COMPLETED = PARTIAL`
- `CREDIBLE_STATIC_BASELINE_AFTER_RECOMPUTE = NO`
- `CREDIBLE_MICRO_MOTION_BASELINE_AFTER_RECOMPUTE = UNKNOWN`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

The current task is to continue T004, not to begin a new physics phase.

## 1. Hard gates

- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_TRUE_GEOMETRY_JET1_DETECTION = NO`
- `ALLOW_PARAMETER_SWEEP = NO`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = NO` at task start
- Do not claim physical fountain height.
- Do not run Stage 6.
- Do not run a broad parameter sweep.
- Do not generate Jet1/Jet2 physical conclusions.
- Do not overwrite previous T004 evidence.

Allowed scope:

- `ALLOW_RAW_ARRAY_EXTRACTION_CONTINUATION = YES`
- `ALLOW_POSTPROCESSING_RECOMPUTE = YES`

Only `ALLOW_NEXT_DISPLACEMENT_LADDER` may become YES at the end, and only if the remaining baseline-discriminating cases are extracted/recomputed well enough to establish a credible static/micro-motion baseline. If in doubt, keep it NO.

## 2. Required input files

Read these before doing any work:

1. `reviews/20260620_150000_R005_review_and_plan.md`
2. `reviews/20260620_150000_R005_run_trace.md`
3. `tasks/20260620_132000_T004_raw_array_extraction_recompute.md`
4. `06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T004_final_report.md`
5. `06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T004_case_manifest.csv`
6. `06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T004_progress.csv`
7. `06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T004_recomputed_metrics.csv`
8. `06_true_moving_geometry_R3_raw_array_extraction_recompute/scripts/T004_raw_array_extraction_recompute.py`
9. Existing T004 logs and arrays under `06_true_moving_geometry_R3_raw_array_extraction_recompute/logs/` and `arrays/`

If a required file is missing, record it explicitly and continue with available evidence.

## 3. Output directory convention

Continue using the T004 output family, but put all T005-specific reports/tables under clear T005 filenames:

```text
06_true_moving_geometry_R3_raw_array_extraction_recompute/
├── reports/
├── tables/
├── images/
├── logs/
├── arrays/
└── scripts/
```

Do not delete or overwrite existing T004 rows. Append or generate T005-specific merged outputs.

## 4. Main objective

Continue resumable raw-array extraction and postprocessing recompute for the remaining priority cases that T004 did not attempt. Process one `.mph` model at a time. Write persistent outputs immediately after each case.

This is not a new physics run. It is raw-array extraction plus postprocessing recompute from existing saved models.

## 5. Required case priority

Skip G2/G3 unless you are only verifying existing outputs. Process remaining cases in this priority order:

1. `W10_plain_wall_no_wettedwall_diagnostic`
2. `W0_current_wettedwall`
3. `W2_contact_angle_60deg`
4. `W3_contact_angle_120deg`
5. `W4_contact_angle_150deg`
6. `W7_user_defined_slip_0p1mm`
7. `W8_user_defined_slip_0p5mm`

If runtime is limited, complete at least W10 and W0. Prefer durable partial progress over a long run that writes nothing.

## 6. Required work plan

### Phase A — Continuation manifest

Produce:

```text
06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T005_case_manifest.csv
06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T005_A_continuation_plan.md
```

The manifest must include:

```text
case_id,priority,model_path,model_exists,previous_t004_status,attempted_t005,extraction_status,postprocess_status,output_array_path,notes
```

### Phase B — Continue or patch extraction script

Either reuse the T004 script directly or create a T005 wrapper:

```text
06_true_moving_geometry_R3_raw_array_extraction_recompute/scripts/T005_continue_raw_array_extraction.py
```

Requirements:

- Reuse the successful T004 method for G2/G3.
- Process exactly one model at a time.
- Do not re-run solved studies.
- After each model, immediately write:
  - per-case log,
  - per-case raw or compact sampled array file under `arrays/`,
  - one row appended to T005 progress CSV.
- Use deterministic bounded sampling if arrays are too large.
- Preserve exact exception class and message.
- Do not collapse failures into generic `extraction_failed`.
- Do not overwrite T004 arrays/logs.

### Phase C — Execute bounded continuation

Run with COMSOL access enabled if available:

```powershell
$env:T004_ATTEMPT_COMSOL='1'
```

or:

```powershell
$env:T005_ATTEMPT_COMSOL='1'
```

Required outputs:

```text
06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T005_progress.csv
06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T005_recomputed_metrics.csv
06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T005_merged_T004_T005_metrics.csv
06_true_moving_geometry_R3_raw_array_extraction_recompute/logs/T005_*.log
```

### Phase D — Reviewer figures

If recomputed metrics exist, generate:

```text
06_true_moving_geometry_R3_raw_array_extraction_recompute/images/T005_extraction_status_summary.png
06_true_moving_geometry_R3_raw_array_extraction_recompute/images/T005_interface_quality_summary.png
06_true_moving_geometry_R3_raw_array_extraction_recompute/images/T005_baseline_discrimination_summary.png
```

If images cannot be generated, write the exact reason and commands in the final report.

### Phase E — Final report

Produce:

```text
06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T005_final_report.md
```

It must explicitly state:

- `T005_STATUS = PASS/FAIL/PARTIAL`
- `RAW_ARRAY_EXTRACTION_COMPLETED_REMAINING_CASES = YES/NO/PARTIAL`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED_REMAINING_CASES = YES/NO/PARTIAL`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED_REMAINING_CASES = YES/NO/PARTIAL`
- `W10_PLAIN_WALL_BASELINE_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `W0_CURRENT_WETTEDWALL_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `CREDIBLE_STATIC_BASELINE_AFTER_T005 = YES/NO/UNKNOWN`
- `CREDIBLE_MICRO_MOTION_BASELINE_AFTER_T005 = YES/NO/UNKNOWN`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = YES/NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## 7. README and task-index updates

Update README only in a bounded section if useful:

```text
<!-- TRUE_GEOMETRY_R3_RAW_ARRAY_EXTRACTION_RECOMPUTE:START -->
...
<!-- TRUE_GEOMETRY_R3_RAW_ARRAY_EXTRACTION_RECOMPUTE:END -->
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
7. per-case extraction status,
8. whether MemoryError was resolved for remaining cases,
9. whether `interface_quality=extraction_failed` was resolved for remaining cases,
10. gate values,
11. next recommended task.

Do not answer only in chat. Push all generated outputs to GitHub.