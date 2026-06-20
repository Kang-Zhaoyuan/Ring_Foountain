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
| T008 | 2026-06-20 16:00 | YES | `reviews/20260620_160000_R008_review_and_plan.md` | `tasks/20260620_160000_T008_narrow_diagnostic_displacement_ladder.md` | Narrow diagnostic displacement ladder extending D0/D1/D2 by at most three amplitudes; no Stage 6, real Hmax, Jet1, or broad sweep. | `ALLOW_STAGE6 = NO` |

## Current active task

`tasks/NEXT_TASK.md` is currently synchronized with `tasks/20260620_160000_T008_narrow_diagnostic_displacement_ladder.md`.

## Notes

- Codex must treat `tasks/NEXT_TASK.md` as the active instruction source.
- Archived task files are immutable unless a correction is explicitly recorded.
- Review Agent may allow Stage 6 in a future task if evidence supports it, but current T008 does not allow Stage 6.
- T002 passed audit packaging, but did not establish physics validity.
- T003 produced a memory-safe implementation but did not resolve the actual blocker because raw arrays were not materialized and COMSOL reload exceeded runtime.
- T004 partially resolved the blocker for G2/G3 only.
- T005 resolved W10/W0 raw extraction and postprocess recompute.
- T006 resolved W2/W3/W4/W7/W8 raw extraction and postprocess recompute.
- T007 recovered and validated D0/D1/D2 displacement semantics, but Hmax remains non-real.
- T008 opens only a narrow diagnostic displacement ladder with at most three added amplitudes; Stage 6, real Hmax, Jet1, and broad parameter sweeps remain blocked.
