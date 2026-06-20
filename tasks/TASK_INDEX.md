# Task Index

Repository: `Kang-Zhaoyuan/Ring_Foountain`

| Task ID | Generated Time (Asia/Shanghai) | Active | Source Review | Task File | Summary | Stage 6 Gate |
|---|---:|---:|---|---|---|---|
| T001 | 2026-06-20 11:03 | NO | `reviews/20260620_110300_R001_review_and_plan.md` | `tasks/20260620_110300_T001_true_geometry_R3_phase3_repair.md` | Continue from true-moving-geometry R2 `FAIL_PHASE3`; perform a narrow R3 diagnostic/repair on Phase 3 only. | `ALLOW_STAGE6 = NO` |
| T002 | 2026-06-20 12:00 | NO | `reviews/20260620_120000_R002_review_and_plan.md` | `tasks/20260620_120000_T002_audit_completion_r3_outputs.md` | Audit-completion package for latest R3 outputs; index all updated images/tables and prepare contact sheets/manifests for strict Review Agent verification. | `ALLOW_STAGE6 = NO` |
| T003 | 2026-06-20 12:45 | NO | `reviews/20260620_124500_R003_review_and_plan.md` | `tasks/20260620_124500_T003_r3_postprocessing_memory_repair.md` | Repair the R3 postprocessing/regional-metrics extraction blocker causing `MemoryError` and `interface_quality=extraction_failed`; no physics-stage advancement. | `ALLOW_STAGE6 = NO` |
| T004 | 2026-06-20 13:20 | NO | `reviews/20260620_132000_R004_review_and_plan.md` | `tasks/20260620_132000_T004_raw_array_extraction_recompute.md` | Perform resumable raw-array extraction from saved `.mph` models and recompute postprocessing metrics case-by-case; no physics-stage advancement. | `ALLOW_STAGE6 = NO` |
| T005 | 2026-06-20 15:00 | YES | `reviews/20260620_150000_R005_review_and_plan.md` | `tasks/20260620_150000_T005_continue_raw_array_extraction_remaining_cases.md` | Continue T004 raw-array extraction/recompute for remaining W10/W0/contact-angle/slip baseline-discriminating cases; no physics-stage advancement. | `ALLOW_STAGE6 = NO` |

## Current active task

`tasks/NEXT_TASK.md` is currently synchronized with `tasks/20260620_150000_T005_continue_raw_array_extraction_remaining_cases.md`.

## Notes

- Codex must treat `tasks/NEXT_TASK.md` as the active instruction source.
- Archived task files are immutable unless a correction is explicitly recorded.
- Review Agent may allow Stage 6 in a future task if evidence supports it, but current T005 does not allow Stage 6.
- T002 passed audit packaging, but did not establish physics validity.
- T003 produced a memory-safe implementation but did not resolve the actual blocker because raw arrays were not materialized and COMSOL reload exceeded runtime.
- T004 partially resolved the blocker for G2/G3 only: raw extraction and postprocess PASS for those two cases, but W10/W0/contact-angle/slip baselines remain unattempted.
- T005 targets the remaining narrowed blocker: complete durable raw-array extraction and recompute for the baseline-discriminating wetted-wall/contactline cases.