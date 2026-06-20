# T008 — Narrow Diagnostic Displacement Ladder

Generated time: 2026-06-20 16:00 Asia/Shanghai

Active: YES

Source review: `reviews/20260620_160000_R008_review_and_plan.md`

## 0. Current repository state to respect

T007 successfully recovered and reran D0/D1/D2 displacement regression semantics using the repaired R3 raw-array/postprocessing path.

T007 evidence:

- `D0_zero_motion_regression`: expected approximately `0`, measured `-2.6020852139652106e-18`, PASS
- `D1_micro_motion_regression`: expected `-5e-07`, measured `-5.000000000000664e-07`, PASS
- `D2_micro_motion_regression`: expected `-5e-06`, measured `-5.00000000000023e-06`, PASS

All three D cases passed extraction and postprocessing, had `interface_quality=clear`, and had `memory_error_resolved=YES`.

T007 also explicitly states:

- `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

The purpose of T008 is not to advance physics, but to test a slightly larger diagnostic displacement ladder under the repaired extraction/postprocessing path.

## 1. Hard gates

- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_TRUE_GEOMETRY_JET1_DETECTION = NO`
- `ALLOW_PARAMETER_SWEEP = NO`
- Do not claim physical fountain height.
- Do not run Stage 6.
- Do not run a broad parameter sweep.
- Do not generate Jet1/Jet2 physical conclusions.
- Do not overwrite previous T004/T005/T006/T007 evidence.
- `HMAX_IS_REAL_PHYSICAL_OUTPUT` must remain `NO` for all T008 outputs.

Allowed scope:

- `ALLOW_NARROW_DIAGNOSTIC_DISPLACEMENT_LADDER = YES`
- `ALLOW_RAW_ARRAY_EXTRACTION = YES`
- `ALLOW_POSTPROCESSING_RECOMPUTE = YES`

This task may output `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = YES/NO` only as a recommendation to the Review Agent if, and only if, the diagnostic ladder is clean. It must not open Stage 6 or real Hmax.

## 2. Required input files

Read these before doing any work:

1. `reviews/20260620_160000_R008_review_and_plan.md`
2. `reviews/20260620_160000_R008_run_trace.md`
3. `tasks/20260620_154500_T007_diagnostic_d0_d1_d2_displacement_regression.md`
4. `06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T007_final_report.md`
5. `06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T007_A_d0_d1_d2_semantics.md`
6. `06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T007_recomputed_metrics.csv`
7. `06_true_moving_geometry_R3_diagnostic_displacement_regression/scripts/T007_d0_d1_d2_displacement_regression.py`
8. Relevant R1/R2/R3 scripts and model/export paths needed to build D-ladder cases consistently with D0/D1/D2.

If a required file is missing, record it explicitly and continue with available evidence.

## 3. Output directory convention

Continue using the diagnostic displacement regression output family, but use T008 filenames:

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

Do not delete or overwrite previous T007 rows, arrays, logs, images, or scripts.

## 4. Main objective

Run a narrow diagnostic displacement ladder extending D0/D1/D2 by no more than three new displacement amplitudes.

This is a diagnostic ladder only. It is not Stage 6, not Jet1 detection, not a broad parameter sweep, and not a real Hmax task.

## 5. Required case scope

Anchor cases already validated:

- D0: `Vring = 0[m/s]`, expected displacement `0`
- D1: `Vring = 1e-4[m/s]`, expected displacement `-5e-07[m]`
- D2: `Vring = 1e-3[m/s]`, expected displacement `-5e-06[m]`

Do not rerun D0/D1/D2 unless needed for verification. Preserve their existing evidence.

Add at most three new diagnostic ladder cases. Recommended default cases:

1. `D3_diagnostic_displacement_1e_minus_5m`: `Vring = 2e-3[m/s]`, `t_end = 0.005[s]`, expected displacement `-1e-05[m]`
2. `D4_diagnostic_displacement_2p5e_minus_5m`: `Vring = 5e-3[m/s]`, `t_end = 0.005[s]`, expected displacement `-2.5e-05[m]`
3. `D5_diagnostic_displacement_5e_minus_5m`: `Vring = 1e-2[m/s]`, `t_end = 0.005[s]`, expected displacement `-5e-05[m]`

If those amplitudes are inconsistent with recoverable prior semantics or model stability constraints, do not invent alternatives silently. Write the exact reason and either reduce the ladder or mark `HUMAN_REQUIRED`.

## 6. Required work plan

### Phase A — Ladder semantics and manifest

Produce:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T008_A_ladder_semantics.md
06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T008_case_manifest.csv
```

The semantics report must specify:

- D0/D1/D2 semantics reused from T007,
- new D3/D4/D5 semantics,
- exact `Vring`, `t_end`, `dt`, expected displacement,
- model creation or model reuse path,
- whether each new case is diagnostic-only,
- whether any ambiguity remains.

If definitions are ambiguous, stop before running new models and write `T008_STATUS = HUMAN_REQUIRED`.

### Phase B — Build or patch diagnostic ladder script

Produce:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/scripts/T008_narrow_displacement_ladder.py
```

Requirements:

- Reuse the repaired raw-array extraction/postprocessing functions where possible.
- Process exactly one new D-ladder case at a time.
- Write per-case logs immediately.
- Write per-case raw or compact sampled arrays immediately under `arrays/`.
- Preserve exact exception class and message.
- Do not collapse failures into generic `extraction_failed`.
- Do not run Stage 6.
- Do not output real Hmax.

### Phase C — Execute bounded diagnostic ladder

Run only the new D3/D4/D5 diagnostic cases if COMSOL access is available and semantics are clear.

Required outputs:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T008_progress.csv
06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T008_recomputed_metrics.csv
06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T008_merged_T007_T008_metrics.csv
06_true_moving_geometry_R3_diagnostic_displacement_regression/logs/T008_*.log
06_true_moving_geometry_R3_diagnostic_displacement_regression/arrays/T008_*.npz
```

### Phase D — Reviewer figures

If diagnostic metrics exist, generate:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T008_ladder_displacement_response.png
06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T008_ladder_error_summary.png
06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T008_interface_quality_summary.png
```

If images cannot be generated, write the exact reason and commands in the final report.

### Phase E — Final report

Produce:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T008_final_report.md
06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T008_gate_summary.json
```

The final report must explicitly state:

- `T008_STATUS = PASS/FAIL/PARTIAL/HUMAN_REQUIRED`
- `D3_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `D4_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `D5_STATUS = PASS/FAIL/UNKNOWN/NOT_ATTEMPTED`
- `D_LADDER_SEMANTICS_CLEAR = YES/NO/PARTIAL`
- `RAW_ARRAY_EXTRACTION_COMPLETED = YES/NO/PARTIAL`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED = YES/NO/PARTIAL`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED = YES/NO/PARTIAL`
- `DISPLACEMENT_RESPONSE_MONOTONIC_OR_EXPLAINED = YES/NO/PARTIAL`
- `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = YES/NO`
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
7. D3/D4/D5 semantics source,
8. per-case diagnostic status,
9. whether MemoryError was resolved,
10. whether `interface_quality=extraction_failed` was resolved,
11. whether displacement response is monotonic or otherwise explained,
12. gate values,
13. next recommended task.

Do not answer only in chat. Push all generated outputs to GitHub.
