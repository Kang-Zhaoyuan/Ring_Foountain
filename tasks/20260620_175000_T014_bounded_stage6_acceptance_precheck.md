# T014 — Bounded No-Stage6 Acceptance Precheck

Generated time: 2026-06-20 17:50 Asia/Shanghai

Active: YES

Source review: `reviews/20260620_175000_R014_review_and_plan.md`

## 0. Current repository state to respect

T013 completed the true-geometry model-semantics repair package and defined explicit Stage 6 acceptance criteria.

T013 gate values:

- `T013_STATUS = PASS`
- `MODEL_SEMANTICS_REPAIRED = PARTIAL`
- `ALE_RING_MOTION_SEMANTICS_VALID = PARTIAL`
- `WETTEDWALL_CONTACTLINE_SEMANTICS_VALID = UNKNOWN`
- `INTERFACE_EXTRACTION_PHYSICAL_VALIDITY = PARTIAL`
- `REAL_HMAX_DEFINITION_READY = PARTIAL`
- `STAGE6_ACCEPTANCE_CRITERIA_READY = YES`
- `CURRENT_JET1_BRANCH_ALLOWED = NO`
- `ALLOW_STAGE6_NOW = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_BOUNDED_STAGE6_PRECHECK = YES`

The current task is to execute the T013 acceptance criteria as a bounded precheck against existing candidate evidence. This is not Stage 6.

## 1. Hard gates

- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_PARAMETER_SWEEP = NO`
- `ALLOW_CONTINUE_CURRENT_JET1_BRANCH = NO`
- `ALLOW_JET1_PHYSICAL_CONCLUSION = NO`
- `ALLOW_STAGE_ADVANCEMENT = NO`
- Do not claim physical fountain height.
- Do not output validated real Hmax.
- Do not run Stage 6.
- Do not run a broad parameter sweep.
- Do not continue the current Jet1 ROI/threshold branch.
- Do not overwrite previous T004–T013 evidence.

Allowed scope:

- `ALLOW_BOUNDED_STAGE6_ACCEPTANCE_PRECHECK = YES`
- `ALLOW_EXISTING_EVIDENCE_AUDIT = YES`
- `ALLOW_NO_STAGE6_METADATA_CHECKS = YES`
- `ALLOW_NO_REAL_HMAX_TABLE_RECOMPUTE = YES`

If a small script-based check is needed, it must use existing models/tables/scripts only and must not output real Hmax. Any height-like values must be labeled diagnostic until Review Agent explicitly changes the gate.

## 2. Required input files

Read these before doing any work:

1. `reviews/20260620_175000_R014_review_and_plan.md`
2. `reviews/20260620_175000_R014_run_trace.md`
3. `tasks/20260620_173000_T013_true_geometry_model_semantics_repair.md`
4. `06_true_moving_geometry_R3_model_semantics_repair/reports/T013_final_report.md`
5. `06_true_moving_geometry_R3_model_semantics_repair/reports/T013_stage6_acceptance_criteria.md`
6. `06_true_moving_geometry_R3_model_semantics_repair/tables/T013_semantics_consistency_matrix.csv`
7. `06_true_moving_geometry_R3_model_semantics_repair/tables/T013_semantics_source_inventory.csv`
8. `06_true_moving_geometry_R3_stage6_decision_audit/reports/T012_final_report.md`
9. `06_true_moving_geometry_R3_stage6_decision_audit/tables/T012_stage6_evidence_ledger.csv`
10. `06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T006_merged_T004_T005_T006_metrics.csv`
11. `06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T008_recomputed_metrics.csv`
12. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T011_threshold_recompute.csv`
13. Any scripts/reports used by T013 to identify ALE boundaries, wall-frame/contactline convention, interface extraction, and candidate Hmax definition.

If a required file is missing, record it explicitly and continue with available evidence.

## 3. Output directory convention

Create or reuse:

```text
06_true_moving_geometry_R3_stage6_acceptance_precheck/
├── reports/
├── tables/
├── images/
└── scripts/
```

Do not delete or overwrite prior artifacts.

## 4. Main objective

Execute a bounded no-Stage6 acceptance precheck using the criteria defined by T013.

T014 must determine whether any existing true-geometry candidate evidence is close enough to justify a future narrowly bounded Stage 6 candidate task.

This task must not itself enter Stage 6 and must not output real Hmax.

## 5. Required work plan

### Phase A — Candidate evidence selection

Produce:

```text
06_true_moving_geometry_R3_stage6_acceptance_precheck/tables/T014_candidate_evidence_manifest.csv
```

Required columns:

```text
candidate_id,source_task,source_model_or_table,reason_selected,available_arrays,available_logs,available_figures,allowed_for_precheck,notes
```

At minimum consider:

- best existing ALE/motion candidate from T007/T008,
- best existing static/control baseline from T004/T005/T006,
- T010/T011 Jet1 evidence only as a negative-control/reference, not as positive Jet1 evidence.

### Phase B — Acceptance criteria checklist

Produce:

```text
06_true_moving_geometry_R3_stage6_acceptance_precheck/tables/T014_acceptance_precheck_matrix.csv
```

Required rows:

1. `physical_ring_motion_validity`
2. `ALE_vs_WettedWall_non_double_counting`
3. `boundary_contactline_validity`
4. `contact_angle_slip_control_validity`
5. `connected_interface_extraction_validity`
6. `ROI_extraction_validity`
7. `real_Hmax_definition_executability`
8. `image_table_log_audit_completeness`
9. `minimum_control_case_completeness`
10. `Jet1_requirement_status`

Required columns:

```text
criterion,current_answer,required_for_stage6,evidence_for,evidence_against,blocking_gap,precheck_result,next_action
```

Allowed `precheck_result` values:

- `PASS`
- `FAIL`
- `PARTIAL`
- `UNKNOWN`
- `NOT_APPLICABLE`

### Phase C — Non-real-Hmax extractor feasibility

Produce:

```text
06_true_moving_geometry_R3_stage6_acceptance_precheck/tables/T014_nonreal_hmax_extractor_feasibility.csv
```

This table must not report real Hmax. It should only state whether the real-Hmax definition is executable in principle from existing arrays/tables/logs.

Required columns:

```text
candidate_id,has_connected_interface_source,has_z0_reference,has_artifact_exclusion_rule,has_roi_or_domain_rule,has_time_window,has_visual_audit_support,has_mesh_or_timestep_sensitivity,executable_as_real_hmax_now,reason
```

### Phase D — Optional SVG decision map

If useful, generate:

```text
06_true_moving_geometry_R3_stage6_acceptance_precheck/images/T014_acceptance_precheck_decision_map.svg
```

SVG must be table-backed and must not claim Stage 6 is open.

### Phase E — Final report and gate summary

Produce:

```text
06_true_moving_geometry_R3_stage6_acceptance_precheck/reports/T014_final_report.md
06_true_moving_geometry_R3_stage6_acceptance_precheck/reports/T014_gate_summary.json
```

The final report must explicitly state:

- `T014_STATUS = PASS/FAIL/PARTIAL/HUMAN_REQUIRED`
- `ACCEPTANCE_PRECHECK_COMPLETED = YES/NO/PARTIAL`
- `PHYSICAL_RING_MOTION_VALIDITY = YES/NO/PARTIAL/UNKNOWN`
- `ALE_WETTEDWALL_NON_DOUBLE_COUNTING = YES/NO/PARTIAL/UNKNOWN`
- `BOUNDARY_CONTACTLINE_VALIDITY = YES/NO/PARTIAL/UNKNOWN`
- `CONNECTED_INTERFACE_EXTRACTION_VALIDITY = YES/NO/PARTIAL/UNKNOWN`
- `REAL_HMAX_EXECUTABLE_NOW = YES/NO/PARTIAL/UNKNOWN`
- `MINIMUM_CONTROLS_COMPLETE = YES/NO/PARTIAL/UNKNOWN`
- `CURRENT_JET1_BRANCH_ALLOWED = NO`
- `ALLOW_STAGE6_NOW = YES/NO`
- `ALLOW_REAL_HMAX_OUTPUT = YES/NO`
- `ALLOW_BOUNDED_STAGE6_CANDIDATE_TASK = YES/NO`
- `RECOMMENDED_NEXT_TASK = ...`

## 6. README and task-index updates

Update README only in a bounded section if useful:

```text
<!-- TRUE_GEOMETRY_R3_STAGE6_ACCEPTANCE_PRECHECK:START -->
...
<!-- TRUE_GEOMETRY_R3_STAGE6_ACCEPTANCE_PRECHECK:END -->
```

Update `tasks/BUILDER_POLLING_LOG.csv` as usual.

Do not overwrite archived task files.

## 7. Final Codex response requirements

At the end of your run, report:

1. changed files,
2. generated files,
3. exact report paths,
4. exact table paths,
5. acceptance precheck status,
6. physical ring motion validity,
7. contactline validity,
8. connected-interface extraction validity,
9. real-Hmax executability status,
10. gate values,
11. exact next recommended task.

Do not answer only in chat. Push all generated outputs to GitHub.
