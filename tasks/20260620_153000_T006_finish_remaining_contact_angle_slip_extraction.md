# T006 — Finish Remaining Contact-Angle/Slip Raw-Array Extraction

Generated time: 2026-06-20 15:30 Asia/Shanghai

Active: YES

Source review: `reviews/20260620_153000_R006_review_and_plan.md`

## 0. Current repository state to respect

T005 made partial but real progress. It successfully extracted raw arrays and recomputed postprocessing metrics for two wetted-wall/contactline baseline cases:

- `W10_plain_wall_no_wettedwall_diagnostic`: extraction PASS, postprocess PASS, `interface_quality = clear`, `memory_error_resolved = YES`
- `W0_current_wettedwall`: extraction PASS, postprocess PASS, `interface_quality = clear`, `memory_error_resolved = YES`

Together with T004, four recomputed rows are now available:

- `G2_ring_deeper_submerged`
- `G3_ring_far_below_surface`
- `W10_plain_wall_no_wettedwall_diagnostic`
- `W0_current_wettedwall`

T005 remains incomplete:

- `T005_STATUS = PARTIAL`
- `RAW_ARRAY_EXTRACTION_COMPLETED_REMAINING_CASES = PARTIAL`
- `CREDIBLE_STATIC_BASELINE_AFTER_T005 = UNKNOWN`
- `CREDIBLE_MICRO_MOTION_BASELINE_AFTER_T005 = UNKNOWN`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

The current task is to finish the remaining raw-array extraction/recompute cases, not to begin a new physics phase.

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
- Do not overwrite previous T004/T005 evidence.

Allowed scope:

- `ALLOW_RAW_ARRAY_EXTRACTION_CONTINUATION = YES`
- `ALLOW_POSTPROCESSING_RECOMPUTE = YES`

Only `ALLOW_NEXT_DISPLACEMENT_LADDER` may become YES at the end, and only if W2/W3/W4/W7/W8 plus existing G2/G3/W10/W0 evidence are enough to establish a credible static/micro-motion baseline. If in doubt, keep it NO.

## 2. Required input files

Read these before doing any work:

1. `reviews/20260620_153000_R006_review_and_plan.md`
2. `reviews/20260620_153000_R006_run_trace.md`
3. `tasks/20260620_150000_T005_continue_raw_array_extraction_remaining_cases.md`
4. `06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T005_final_report.md`
5. `06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T005_gate_summary.json`
6. `06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T005_recomputed_metrics.csv`
7. `06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T005_merged_T004_T005_metrics.csv`
8. `06_true_moving_geometry_R3_raw_array_extraction_recompute/scripts/T005_continue_raw_array_extraction.py`
9. Existing T004/T005 logs and arrays under `06_true_moving_geometry_R3_raw_array_extraction_recompute/logs/` and `arrays/`

If a required file is missing, record it explicitly and continue with available evidence.

## 3. Output directory convention

Continue using the same raw-array extraction/recompute output family, but put all T006-specific reports/tables under clear T006 filenames:

```text
06_true_moving_geometry_R3_raw_array_extraction_recompute/
├── reports/
├── tables/
├── images/
├── logs/
├── arrays/
└── scripts/
```

Do not delete or overwrite existing T004/T005 rows. Append or generate T006-specific merged outputs.

## 4. Main objective

Finish resumable raw-array extraction and postprocessing recompute for the remaining contact-angle/slip cases that T005 did not attempt. Process one `.mph` model at a time. Write persistent outputs immediately after each case.

This is not a new physics run. It is raw-array extraction plus postprocessing recompute from existing saved models.

## 5. Required case priority

Skip G2/G3/W10/W0 unless you are only verifying existing outputs. Process remaining cases in this priority order:

1. `W2_contact_angle_60deg`
2. `W3_contact_angle_120deg`
3. `W4_contact_angle_150deg`
4. `W7_user_defined_slip_0p1mm`
5. `W8_user_defined_slip_0p5mm`

If runtime is limited, complete at least W2 and W3. Prefer durable partial progress over a long run that writes nothing.

## 6. Required work plan

### Phase A — Remaining-case manifest

Produce:

```text
06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T006_case_manifest.csv
06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T006_A_remaining_case_plan.md
```

The manifest must include:

```text
case_id,priority,model_path,model_exists,previous_t005_status,attempted_t006,extraction_status,postprocess_status,output_array_path,notes
```

### Phase B — Continue or patch extraction script

Either reuse the T005 script directly or create a T006 wrapper:

```text
06_true_moving_geometry_R3_raw_array_extraction_recompute/scripts/T006_finish_remaining_extraction.py
```

Requirements:

- Reuse the successful T004/T005 method.
- Process exactly one model at a time.
- Do not re-run solved studies.
- After each model, immediately write:
  - per-case log,
  - per-case raw or compact sampled array file under `arrays/`,
  - one row appended to T006 progress CSV.
- Use deterministic bounded sampling if arrays are too large.
- Preserve exact exception class and message.
- Do not collapse failures into generic `extraction_failed`.
- Do not overwrite T004/T005 arrays/logs.

### Phase C — Execute bounded continuation

Run with COMSOL access enabled if available:

```powershell
$env:T006_ATTEMPT_COMSOL='1'
```

Required outputs:

```text
06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T006_progress.csv
06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T006_recomputed_metrics.csv
06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T006_merged_T004_T005_T006_metrics.csv
06_true_moving_geometry_R3_raw_array_extraction_recompute/logs/T006_*.log
```

### Phase D — Reviewer figures

If recomputed metrics exist, generate:

```text
06_true_moving_geometry_R3_raw_array_extraction_recompute/images/T006_extraction_status_summary.png
06_true_moving_geometry_R3_raw_array_extraction_recompute/images/T006_interface_quality_summary.png
06_true_moving_geometry_R3_raw_array_extraction_recompute/images/T006_baseline_discrimination_summary.png
```

If images cannot be generated, write the exact reason and commands in the final report.

### Phase E — Final report

Produce:

```text
06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T006_final_report.md
06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T006_gate_summary.json
```

The final report must explicitly state:

- `T006_STATUS = PASS/FAIL/PARTIAL`
- `RAW_ARRAY_EXTRACTION_COMPLETED_REMAINING_CASES = YES/NO/PARTIAL`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED_REMAINING_CASES = YES/NO/PARTIAL`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED_REMAINING_CASES = YES/NO/PARTIAL`
- `W2_CONTACT_ANGLE_60_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `W3_CONTACT_ANGLE_120_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `W4_CONTACT_ANGLE_150_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `W7_SLIP_0P1MM_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `W8_SLIP_0P5MM_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `CREDIBLE_STATIC_BASELINE_AFTER_T006 = YES/NO/UNKNOWN`
- `CREDIBLE_MICRO_MOTION_BASELINE_AFTER_T006 = YES/NO/UNKNOWN`
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
