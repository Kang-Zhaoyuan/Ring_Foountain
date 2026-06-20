# T009 — T008 Visual Audit Completion Before Jet1 Gate

Generated time: 2026-06-20 16:30 Asia/Shanghai

Active: YES

Source review: `reviews/20260620_163000_R009_review_and_plan.md`

## 0. Current repository state to respect

T008 completed a narrow diagnostic displacement ladder D3/D4/D5.

T008 data evidence is strong:

- D3/D4/D5 all solve PASS, extraction PASS, postprocess PASS.
- D3/D4/D5 measured displacement matches expected displacement to approximately 1e-19 m or better.
- `interface_quality = clear` for all three cases.
- `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`.
- T008 reports `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = YES`.
- T008 keeps `ALLOW_STAGE6 = NO` and `ALLOW_REAL_HMAX_OUTPUT = NO`.

However, R009 could not reliably render and visually inspect the three T008 PNG figures:

- `06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T008_ladder_displacement_response.png`
- `06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T008_ladder_error_summary.png`
- `06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T008_interface_quality_summary.png`

Therefore Jet1 remains blocked until visual audit evidence is complete.

## 1. Hard gates

- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_TRUE_GEOMETRY_JET1_DETECTION = NO`
- `ALLOW_PARAMETER_SWEEP = NO`
- Do not run COMSOL.
- Do not run Stage 6.
- Do not run Jet1/Jet2 detection.
- Do not claim real physical Hmax.
- Do not modify T008 numeric results.

Allowed scope:

- `ALLOW_T008_VISUAL_AUDIT_COMPLETION = YES`
- `ALLOW_FIGURE_REGENERATION_FROM_EXISTING_T008_TABLES = YES`
- `ALLOW_SVG_OR_TEXT_BASED_FIGURE_EXPORT = YES`

## 2. Required input files

Read these before doing any work:

1. `reviews/20260620_163000_R009_review_and_plan.md`
2. `reviews/20260620_163000_R009_run_trace.md`
3. `06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T008_final_report.md`
4. `06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T008_gate_summary.json`
5. `06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T008_progress.csv`
6. `06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T008_recomputed_metrics.csv`
7. The three T008 PNG figure files if accessible.
8. `06_true_moving_geometry_R3_diagnostic_displacement_regression/scripts/T008_narrow_diagnostic_displacement_ladder.py` or equivalent T008 script if present.

If a required file is missing, record it explicitly.

## 3. Output directory convention

Use the existing T008/T007 diagnostic displacement regression output family, but create T009-specific audit files:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/
├── reports/
├── tables/
├── images/
└── scripts/
```

Do not overwrite T008 PNGs. Add T009-specific outputs.

## 4. Main objective

Create a reviewable visual-audit completion package for T008 figures, without changing the T008 numeric results and without running COMSOL.

The package must allow Review Agent to inspect the displacement response, error summary, and interface quality evidence using text/SVG/CSV-backed artifacts rather than relying only on opaque PNG rendering.

## 5. Required outputs

### Phase A — Figure manifest

Produce:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T009_t008_figure_manifest.csv
```

Columns:

```text
figure_id,original_png_path,exists,source_table,regenerated_svg_path,regenerated_png_path,visual_audit_status,notes
```

### Phase B — Regenerate figures from T008 tables

From `T008_recomputed_metrics.csv`, regenerate these figures as SVG first, PNG optional:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T009_ladder_displacement_response.svg
06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T009_ladder_error_summary.svg
06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T009_interface_quality_summary.svg
```

SVG is required because it is text-readable and easier for Review Agent to inspect. PNG copies may also be generated, but SVG is the gate-critical artifact.

### Phase C — CSV-backed visual audit report

Produce:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T009_t008_visual_audit_report.md
```

The report must explicitly state:

- `T009_STATUS = PASS/FAIL/PARTIAL/HUMAN_REQUIRED`
- `T008_DISPLACEMENT_RESPONSE_FIGURE_AUDITED = YES/NO`
- `T008_ERROR_SUMMARY_FIGURE_AUDITED = YES/NO`
- `T008_INTERFACE_QUALITY_FIGURE_AUDITED = YES/NO`
- `T008_FIGURES_MATCH_SOURCE_TABLES = YES/NO/PARTIAL/UNKNOWN`
- `T008_NUMERIC_EVIDENCE_UNCHANGED = YES/NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1_RECOMMENDATION = YES/NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

The report must summarize, in text, what each figure shows and must cite the source columns used from `T008_recomputed_metrics.csv`.

### Phase D — Optional script

If useful, produce:

```text
06_true_moving_geometry_R3_diagnostic_displacement_regression/scripts/T009_regenerate_t008_visual_audit.py
```

The script must read only existing T008 tables and must not run COMSOL.

## 6. README and task-index updates

Update README only in a bounded section if useful.

Update `tasks/BUILDER_POLLING_LOG.csv` as usual.

Do not overwrite archived task files.

## 7. Final Codex response requirements

At the end of your run, report:

1. changed files,
2. generated files,
3. exact report paths,
4. exact table paths,
5. exact SVG paths,
6. whether each original T008 PNG exists,
7. whether regenerated SVGs match T008 source data,
8. whether `ALLOW_NEXT_TRUE_GEOMETRY_JET1_RECOMMENDATION` is YES or NO,
9. gate values,
10. next recommended task.

Do not answer only in chat. Push all generated outputs to GitHub.
