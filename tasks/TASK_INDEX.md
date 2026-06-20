# Task Index

Repository: `Kang-Zhaoyuan/Ring_Foountain`

| Task ID | Generated Time (Asia/Shanghai) | Active | Source Review | Task File | Summary | Stage 6 Gate |
|---|---:|---:|---|---|---|---|
| T001 | 2026-06-20 11:03 | NO | `reviews/20260620_110300_R001_review_and_plan.md` | `tasks/20260620_110300_T001_true_geometry_R3_phase3_repair.md` | Continue from true-moving-geometry R2 `FAIL_PHASE3`; perform a narrow R3 diagnostic/repair on Phase 3 only. | `ALLOW_STAGE6 = NO` |
| T002 | 2026-06-20 12:00 | NO | `reviews/20260620_120000_R002_review_and_plan.md` | `tasks/20260620_120000_T002_audit_completion_r3_outputs.md` | Audit-completion package for latest R3 outputs; index all updated images/tables and prepare contact sheets/manifests for strict Review Agent verification. | `ALLOW_STAGE6 = NO` |
| T003 | 2026-06-20 12:45 | YES | `reviews/20260620_124500_R003_review_and_plan.md` | `tasks/20260620_124500_T003_r3_postprocessing_memory_repair.md` | Repair the R3 postprocessing/regional-metrics extraction blocker causing `MemoryError` and `interface_quality=extraction_failed`; no physics-stage advancement. | `ALLOW_STAGE6 = NO` |

## Current active task

`tasks/NEXT_TASK.md` is currently synchronized with `tasks/20260620_124500_T003_r3_postprocessing_memory_repair.md`.

## Notes

- Codex must treat `tasks/NEXT_TASK.md` as the active instruction source.
- Archived task files are immutable unless a correction is explicitly recorded.
- Review Agent may allow Stage 6 in a future task if evidence supports it, but current T003 does not allow Stage 6.
- T002 passed audit packaging, but did not establish physics validity.
- T003 targets the most actionable blocker exposed by T002: postprocessing `MemoryError` and `interface_quality=extraction_failed` in ring-geometry and wetted-wall/contactline diagnostics.
