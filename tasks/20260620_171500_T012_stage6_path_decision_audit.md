# T012 — Stage 6 Path Decision and Model-Semantics Audit

Generated time: 2026-06-20 17:15 Asia/Shanghai

Active: YES

Source review: `reviews/20260620_171500_R012_review_and_plan.md`

## 0. Current repository state to respect

T011 completed the Jet1 threshold/ROI audit and returned a negative result for the current true-geometry Jet1 continuation path.

T011 key findings:

- `T011_STATUS = PASS`
- `JET1_THRESHOLD_SOURCES_RECOVERED = YES`
- fixed-geometry 5C threshold recovered as `delta > 5e-5 m`
- fixed-geometry rules are true-geometry diagnostic analogues only, not physical validation rules
- J0 ROI max delta: `6.0691962701962614e-06 m`
- J1 ROI max delta: `4.34916959663216e-06 m`
- J1 minus J0: `-1.7200266735641012e-06 m`
- `J1_VS_J0_EVIDENCE = NEGATIVE`
- `T010_ALLOW_NEXT_TRUE_GEOMETRY_JET1_CONSISTENT_WITH_THRESHOLD = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

Therefore the current issue is not a runtime blocker. It is an evidence/physics-criteria blocker.

## 1. Hard gates

- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_PARAMETER_SWEEP = NO`
- `ALLOW_JET1_PHYSICAL_CONCLUSION = NO`
- `ALLOW_TRUE_GEOMETRY_JET1_DETECTION = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- `ALLOW_STAGE_ADVANCEMENT = NO`
- Do not claim physical fountain height.
- Do not output validated real Hmax.
- Do not run Stage 6.
- Do not run COMSOL unless Review Agent later issues a separate task permitting it.
- Do not produce another Jet1 diagnostic expansion under the current ROI/threshold metric.
- Do not overwrite previous evidence.

Allowed scope:

- `ALLOW_STAGE6_PATH_DECISION_AUDIT = YES`
- `ALLOW_EVIDENCE_SYNTHESIS = YES`
- `ALLOW_MODEL_SEMANTICS_REPAIR_PLAN = YES`
- `ALLOW_NO_COMSOL_TABLE_RECOMPUTE_FROM_EXISTING_EVIDENCE = YES`

## 2. Required input files

Read these before doing any work:

1. `reviews/20260620_171500_R012_review_and_plan.md`
2. `reviews/20260620_171500_R012_run_trace.md`
3. `tasks/20260620_170000_T011_jet1_threshold_roi_audit.md`
4. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T011_final_report.md`
5. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T011_A_threshold_source_audit.md`
6. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T011_threshold_recompute.csv`
7. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T010_final_report.md`
8. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T010_recomputed_metrics.csv`
9. `06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T008_final_report.md`
10. `06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T008_recomputed_metrics.csv`
11. `06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T006_final_report.md`
12. `06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T006_merged_T004_T005_T006_metrics.csv`
13. Any README bounded sections summarizing true-geometry R3 / Stage 6 state.

If a required file is missing, record it explicitly and continue with available evidence.

## 3. Output directory convention

Create or reuse a Stage-6 decision directory:

```text
06_true_moving_geometry_R3_stage6_decision_audit/
├── reports/
├── tables/
├── images/
└── scripts/
```

Do not delete or overwrite prior artifacts.

## 4. Main objective

Produce a clear, evidence-grounded decision about the fastest scientifically defensible path toward Stage 6.

This is not a new simulation task. It is a gate and model-semantics decision audit.

T012 must answer:

1. Which blocker currently prevents Stage 6?
2. Is the blocker numerical, postprocessing, image-audit, Jet1-threshold, model-semantics, or physical-interpretation related?
3. Is the current true-geometry Jet1 branch falsified under its current ROI/threshold metric?
4. Can Stage 6 be entered through any other evidence-backed route, or must model semantics be repaired first?
5. What is the single next narrow task most likely to restore a valid Stage 6 path?

## 5. Required work plan

### Phase A — Evidence ledger

Produce:

```text
06_true_moving_geometry_R3_stage6_decision_audit/tables/T012_stage6_evidence_ledger.csv
```

Required columns:

```text
evidence_block,source_task,source_file,status,key_values,stage6_effect,next_action
```

At minimum include blocks for:

- raw-array/postprocess repair,
- baseline/contactline extraction,
- D0/D1/D2 semantics,
- D3/D4/D5 ladder,
- T008 visual audit,
- T010 Jet1 diagnostic,
- T011 threshold/ROI audit,
- real Hmax status,
- Stage 6 gate.

### Phase B — Decision matrix

Produce:

```text
06_true_moving_geometry_R3_stage6_decision_audit/tables/T012_stage6_path_decision_matrix.csv
```

Required candidate paths:

1. `enter_stage6_now`
2. `continue_current_jet1_branch`
3. `repair_true_geometry_model_semantics`
4. `redefine_jet1_roi_threshold_with_explicit_review_approval`
5. `redirect_to_non_jet1_stage6_mechanism`

Required columns:

```text
candidate_path,allowed_now,reason,evidence_for,evidence_against,required_next_task,reviewer_gate
```

### Phase C — Final report

Produce:

```text
06_true_moving_geometry_R3_stage6_decision_audit/reports/T012_final_report.md
06_true_moving_geometry_R3_stage6_decision_audit/reports/T012_gate_summary.json
```

The final report must explicitly state:

- `T012_STATUS = PASS/FAIL/PARTIAL/HUMAN_REQUIRED`
- `CURRENT_PRIMARY_BLOCKER = ...`
- `CURRENT_TRUE_GEOMETRY_JET1_BRANCH_STATUS = VIABLE/NEGATIVE/AMBIGUOUS/REPAIR_REQUIRED`
- `FASTEST_STAGE6_PATH = ...`
- `ALLOW_STAGE6_NOW = YES/NO`
- `ALLOW_REAL_HMAX_OUTPUT = YES/NO`
- `ALLOW_CONTINUE_CURRENT_JET1_BRANCH = YES/NO`
- `ALLOW_MODEL_SEMANTICS_REPAIR_TASK = YES/NO`
- `ALLOW_REDEFINE_JET1_THRESHOLD_TASK = YES/NO`
- `ALLOW_REDIRECT_TO_NON_JET1_STAGE6_MECHANISM = YES/NO`
- `RECOMMENDED_NEXT_TASK = ...`

## 6. README and task-index updates

Update README only in a bounded section if useful:

```text
<!-- TRUE_GEOMETRY_R3_STAGE6_DECISION_AUDIT:START -->
...
<!-- TRUE_GEOMETRY_R3_STAGE6_DECISION_AUDIT:END -->
```

Update `tasks/BUILDER_POLLING_LOG.csv` as usual.

Do not overwrite archived task files.

## 7. Final Codex response requirements

At the end of your run, report:

1. changed files,
2. generated files,
3. exact report paths,
4. exact table paths,
5. current primary blocker,
6. fastest Stage 6 path,
7. whether current Jet1 branch is viable or negative,
8. gate values,
9. exact next recommended task.

Do not answer only in chat. Push all generated outputs to GitHub.
