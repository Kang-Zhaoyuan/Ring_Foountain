# T013 — True-Geometry Model-Semantics Repair Before Stage 6

Generated time: 2026-06-20 17:30 Asia/Shanghai

Active: YES

Source review: `reviews/20260620_173000_R013_review_and_plan.md`

## 0. Current repository state to respect

T012 completed the Stage 6 path decision audit and concluded:

- `T012_STATUS = PASS`
- `CURRENT_PRIMARY_BLOCKER = model_semantics_and_physical_interpretation`
- `CURRENT_TRUE_GEOMETRY_JET1_BRANCH_STATUS = NEGATIVE`
- `FASTEST_STAGE6_PATH = repair_true_geometry_model_semantics`
- `ALLOW_STAGE6_NOW = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_CONTINUE_CURRENT_JET1_BRANCH = NO`
- `ALLOW_MODEL_SEMANTICS_REPAIR_TASK = YES`

Therefore the current issue is not runtime, raw-array extraction, postprocessing memory, or image audit. The current issue is whether the true-geometry model outputs have a defensible physical meaning that can support a future Stage 6 task.

## 1. Hard gates

- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_PARAMETER_SWEEP = NO`
- `ALLOW_JET1_PHYSICAL_CONCLUSION = NO`
- `ALLOW_TRUE_GEOMETRY_JET1_DETECTION = NO`
- `ALLOW_CONTINUE_CURRENT_JET1_BRANCH = NO`
- `ALLOW_STAGE_ADVANCEMENT = NO`
- Do not claim physical fountain height.
- Do not output validated real Hmax.
- Do not run Stage 6.
- Do not run a broad parameter sweep.
- Do not continue the current Jet1 branch under the current ROI/threshold metric.
- Do not redefine Jet1 threshold post hoc.
- Do not overwrite previous T004–T012 evidence.

Allowed scope:

- `ALLOW_MODEL_SEMANTICS_REPAIR_TASK = YES`
- `ALLOW_EVIDENCE_SYNTHESIS = YES`
- `ALLOW_STATIC_SCRIPT_AND_REPORT_AUDIT = YES`
- `ALLOW_NO_STAGE6_DIAGNOSTIC_CHECKS = YES`

If a small script-based metadata or consistency check is needed, it must be non-Stage and must not produce real Hmax.

## 2. Required input files

Read these before doing any work:

1. `reviews/20260620_173000_R013_review_and_plan.md`
2. `reviews/20260620_173000_R013_run_trace.md`
3. `tasks/20260620_171500_T012_stage6_path_decision_audit.md`
4. `06_true_moving_geometry_R3_stage6_decision_audit/reports/T012_final_report.md`
5. `06_true_moving_geometry_R3_stage6_decision_audit/tables/T012_stage6_evidence_ledger.csv`
6. `06_true_moving_geometry_R3_stage6_decision_audit/tables/T012_stage6_path_decision_matrix.csv`
7. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T011_final_report.md`
8. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T011_threshold_recompute.csv`
9. `06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T010_final_report.md`
10. `06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T008_final_report.md`
11. `06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T006_final_report.md`
12. Relevant true-geometry R1/R2/R3 scripts and reports describing ALE ring motion, WettedWall/contactline settings, mesh motion, boundary conditions, interface extraction, ROI extraction, and Hmax semantics.
13. README bounded sections for true-geometry R3 and Stage 6 if present.

If a required file is missing, record it explicitly and continue with available evidence.

## 3. Output directory convention

Create or reuse:

```text
06_true_moving_geometry_R3_model_semantics_repair/
├── reports/
├── tables/
├── images/
└── scripts/
```

Do not delete or overwrite prior artifacts.

## 4. Main objective

Produce a bounded true-geometry model-semantics repair package that defines exactly what must be true before Stage 6 can be considered.

This is not a simulation task and not a Stage 6 task. It is a physical/model semantics repair task.

T013 must answer:

1. What exactly is the intended physical meaning of ring motion in the true-geometry model?
2. Are ALE mesh motion, moving boundary, and saved-model displacement semantics consistent with that intended meaning?
3. Are WettedWall/contactline and slip/contact-angle settings physically interpretable in the current branch?
4. Is the interface extraction method valid for physical height measurements, or only for diagnostic postprocessing?
5. What exact definition would make `Hmax` a real physical output rather than a diagnostic artifact?
6. What minimum acceptance criteria must pass before any future `ALLOW_STAGE6 = YES` can be considered?

## 5. Required work plan

### Phase A — Source inventory

Produce:

```text
06_true_moving_geometry_R3_model_semantics_repair/tables/T013_semantics_source_inventory.csv
```

Required columns:

```text
source_file,exists,source_type,semantics_area,key_claim_or_setting,relevance,uncertainty
```

Cover at minimum:

- ALE / moving mesh / ring motion scripts,
- WettedWall/contactline scripts/settings,
- displacement ladder scripts/reports,
- interface extraction scripts/reports,
- Hmax-related scripts/reports,
- README bounded sections.

### Phase B — Semantics consistency audit

Produce:

```text
06_true_moving_geometry_R3_model_semantics_repair/tables/T013_semantics_consistency_matrix.csv
```

Required rows:

1. `ALE_ring_motion_semantics`
2. `moving_boundary_vs_mesh_motion`
3. `wettedwall_contactline_semantics`
4. `contact_angle_slip_semantics`
5. `interface_extraction_physical_validity`
6. `ROI_extraction_physical_validity`
7. `real_Hmax_definition`
8. `Stage6_minimum_acceptance_criteria`

Required columns:

```text
semantics_item,current_status,evidence_for,evidence_against,blocking_uncertainty,repair_action,gate_effect
```

### Phase C — Define Stage 6 acceptance criteria

Produce:

```text
06_true_moving_geometry_R3_model_semantics_repair/reports/T013_stage6_acceptance_criteria.md
```

This report must include explicit YES/NO criteria for:

- physical ring motion validity,
- boundary/contactline validity,
- interface extraction validity,
- real Hmax validity,
- image/table/log audit completeness,
- minimum control-case requirements,
- whether Jet1 is required for Stage 6 or whether Stage 6 can be entered through a non-Jet1 mechanism.

### Phase D — Final report and gate summary

Produce:

```text
06_true_moving_geometry_R3_model_semantics_repair/reports/T013_final_report.md
06_true_moving_geometry_R3_model_semantics_repair/reports/T013_gate_summary.json
```

The final report must explicitly state:

- `T013_STATUS = PASS/FAIL/PARTIAL/HUMAN_REQUIRED`
- `MODEL_SEMANTICS_REPAIRED = YES/NO/PARTIAL`
- `ALE_RING_MOTION_SEMANTICS_VALID = YES/NO/PARTIAL/UNKNOWN`
- `WETTEDWALL_CONTACTLINE_SEMANTICS_VALID = YES/NO/PARTIAL/UNKNOWN`
- `INTERFACE_EXTRACTION_PHYSICAL_VALIDITY = YES/NO/PARTIAL/UNKNOWN`
- `REAL_HMAX_DEFINITION_READY = YES/NO/PARTIAL/UNKNOWN`
- `STAGE6_ACCEPTANCE_CRITERIA_READY = YES/NO/PARTIAL`
- `CURRENT_JET1_BRANCH_ALLOWED = NO`
- `ALLOW_STAGE6_NOW = YES/NO`
- `ALLOW_REAL_HMAX_OUTPUT = YES/NO`
- `ALLOW_BOUNDED_STAGE6_PRECHECK = YES/NO`
- `RECOMMENDED_NEXT_TASK = ...`

## 6. README and task-index updates

Update README only in a bounded section if useful:

```text
<!-- TRUE_GEOMETRY_R3_MODEL_SEMANTICS_REPAIR:START -->
...
<!-- TRUE_GEOMETRY_R3_MODEL_SEMANTICS_REPAIR:END -->
```

Update `tasks/BUILDER_POLLING_LOG.csv` as usual.

Do not overwrite archived task files.

## 7. Final Codex response requirements

At the end of your run, report:

1. changed files,
2. generated files,
3. exact report paths,
4. exact table paths,
5. model-semantics blocker status,
6. real-Hmax definition status,
7. Stage 6 acceptance criteria status,
8. gate values,
9. exact next recommended task.

Do not answer only in chat. Push all generated outputs to GitHub.
