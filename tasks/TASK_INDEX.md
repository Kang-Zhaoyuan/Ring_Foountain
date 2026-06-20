# Task Index

Repository: `Kang-Zhaoyuan/Ring_Foountain`

| Task ID | Generated Time (Asia/Shanghai) | Active | Source Review | Task File | Summary | Stage 6 Gate |
|---|---:|---:|---|---|---|---|
| T001 | 2026-06-20 11:03 | NO | `reviews/20260620_110300_R001_review_and_plan.md` | `tasks/20260620_110300_T001_true_geometry_R3_phase3_repair.md` | Continue from true-moving-geometry R2 `FAIL_PHASE3`; perform a narrow R3 diagnostic/repair on Phase 3 only. | `ALLOW_STAGE6 = NO` |
| T002 | 2026-06-20 12:00 | NO | `reviews/20260620_120000_R002_review_and_plan.md` | `tasks/20260620_120000_T002_audit_completion_r3_outputs.md` | Audit-completion package for latest R3 outputs; index all updated images/tables and prepare contact sheets/manifests for strict Review Agent verification. | `ALLOW_STAGE6 = NO` |
| T003 | 2026-06-20 12:45 | NO | `reviews/20260620_124500_R003_review_and_plan.md` | `tasks/20260620_124500_T003_r3_postprocessing_memory_repair.md` | Repair the R3 postprocessing/regional-metrics extraction blocker causing `MemoryError` and `interface_quality=extraction_failed`; no physics-stage advancement. | `ALLOW_STAGE6 = NO` |
| T004 | 2026-06-20 13:20 | NO | `reviews/20260620_132000_R004_review_and_plan.md` | `tasks/20260620_132000_T004_raw_array_extraction_recompute.md` | Perform resumable raw-array extraction from saved `.mph` models and recompute postprocessing metrics case-by-case; no physics-stage advancement. | `ALLOW_STAGE6 = NO` |
| T005 | 2026-06-20 15:00 | NO | `reviews/20260620_150000_R005_review_and_plan.md` | `tasks/20260620_150000_T005_continue_raw_array_extraction_remaining_cases.md` | Continue T004 raw-array extraction/recompute for remaining W10/W0/contact-angle/slip baseline-discriminating cases; no physics-stage advancement. | `ALLOW_STAGE6 = NO` |
| T006 | 2026-06-20 15:30 | NO | `reviews/20260620_153000_R006_review_and_plan.md` | `tasks/20260620_153000_T006_finish_remaining_contact_angle_slip_extraction.md` | Finish raw-array extraction/recompute for remaining W2/W3/W4/W7/W8 contact-angle/slip cases; no physics-stage advancement. | `ALLOW_STAGE6 = NO` |
| T007 | 2026-06-20 15:45 | NO | `reviews/20260620_154500_R007_review_and_plan.md` | `tasks/20260620_154500_T007_diagnostic_d0_d1_d2_displacement_regression.md` | Diagnostic D0/D1/D2 zero/micro-motion displacement regression using repaired raw-array/postprocessing workflow; no Stage 6 or real Hmax. | `ALLOW_STAGE6 = NO` |
| T008 | 2026-06-20 16:00 | NO | `reviews/20260620_160000_R008_review_and_plan.md` | `tasks/20260620_160000_T008_narrow_diagnostic_displacement_ladder.md` | Narrow diagnostic displacement ladder extending D0/D1/D2 by at most three amplitudes; no Stage 6, real Hmax, Jet1, or broad sweep. | `ALLOW_STAGE6 = NO` |
| T009 | 2026-06-20 16:30 | NO | `reviews/20260620_163000_R009_review_and_plan.md` | `tasks/20260620_163000_T009_t008_visual_audit_completion.md` | Complete visual/SVG/CSV-backed audit of T008 figures before any Jet1 gate release; no COMSOL or physics-stage advancement. | `ALLOW_STAGE6 = NO` |
| T010 | 2026-06-20 16:45 | NO | `reviews/20260620_164500_R010_review_and_plan.md` | `tasks/20260620_164500_T010_true_geometry_jet1_diagnostic.md` | Narrow true-geometry Jet1 diagnostic evidence generation only; no Stage 6, real Hmax, broad parameter sweep, or Jet1 physical conclusions. | `ALLOW_STAGE6 = NO` |
| T011 | 2026-06-20 17:00 | NO | `reviews/20260620_170000_R011_review_and_plan.md` | `tasks/20260620_170000_T011_jet1_threshold_roi_audit.md` | Audit Jet1 ROI/threshold semantics and J1-vs-J0 evidence before any further Jet1 diagnostic expansion; no COMSOL, Stage 6, real Hmax, or Jet1 physical conclusion. | `ALLOW_STAGE6 = NO` |
| T012 | 2026-06-20 17:15 | NO | `reviews/20260620_171500_R012_review_and_plan.md` | `tasks/20260620_171500_T012_stage6_path_decision_audit.md` | Decide the fastest scientifically defensible Stage 6 path after T011 negative Jet1 evidence; no COMSOL, Stage 6, real Hmax, or Jet1 expansion. | `ALLOW_STAGE6 = NO` |
| T013 | 2026-06-20 17:30 | NO | `reviews/20260620_173000_R013_review_and_plan.md` | `tasks/20260620_173000_T013_true_geometry_model_semantics_repair.md` | Repair true-geometry model semantics and define Stage 6 acceptance criteria; no Stage 6, real Hmax, parameter sweep, or current Jet1 continuation. | `ALLOW_STAGE6 = NO` |
| T014 | 2026-06-20 17:50 | YES | `reviews/20260620_175000_R014_review_and_plan.md` | `tasks/20260620_175000_T014_bounded_stage6_acceptance_precheck.md` | Execute the T013 Stage 6 acceptance criteria as a bounded no-Stage6 precheck against existing candidate evidence; no real Hmax or Stage 6. | `ALLOW_STAGE6 = NO` |

## Current active task

`tasks/NEXT_TASK.md` is currently synchronized with `tasks/20260620_175000_T014_bounded_stage6_acceptance_precheck.md`.

## Notes

- Codex must treat `tasks/NEXT_TASK.md` as the active instruction source.
- Archived task files are immutable unless a correction is explicitly recorded.
- Review Agent may allow Stage 6 in a future task if evidence supports it, but current T014 does not allow Stage 6.
- T002 passed audit packaging, but did not establish physics validity.
- T003 produced a memory-safe implementation but did not resolve the actual blocker because raw arrays were not materialized and COMSOL reload exceeded runtime.
- T004/T005/T006 repaired and validated the raw-array extraction/postprocessing path over nine baseline/control rows.
- T007 recovered and validated D0/D1/D2 displacement semantics, but Hmax remains non-real.
- T008 passed the narrow D3/D4/D5 diagnostic displacement ladder numerically.
- T009 completed the SVG/CSV-backed visual audit of T008 figures and recommended Jet1 diagnostic consideration.
- T010 completed a narrow true-geometry Jet1 diagnostic pipeline pass, but the reported shape threshold was not crossed for J0 or J1; J1 ROI max delta was lower than J0, and no Jet1 physical conclusion was made.
- T011 recovered Jet1 threshold/ROI semantics and found J1-vs-J0 evidence NEGATIVE; T010's Jet1 continuation recommendation was inconsistent with threshold evidence.
- T012 decided that the current primary blocker is model semantics and physical interpretation, and that the fastest Stage 6 path is true-geometry model-semantics repair.
- T013 defined explicit Stage 6 acceptance criteria, but decisive categories remain PARTIAL/UNKNOWN/NO.
- T014 executes those criteria as a bounded no-Stage6 acceptance precheck against existing evidence.
