# T009 T008 Visual Audit Report

- Run id: `20260620_163005`
- Scope: regenerate T008 figure evidence as SVG/CSV-backed artifacts only.
- COMSOL was not run. T008 numeric CSV files were read but not modified.

## Gate Values

- `T009_STATUS = PASS`
- `T008_DISPLACEMENT_RESPONSE_FIGURE_AUDITED = YES`
- `T008_ERROR_SUMMARY_FIGURE_AUDITED = YES`
- `T008_INTERFACE_QUALITY_FIGURE_AUDITED = YES`
- `T008_FIGURES_MATCH_SOURCE_TABLES = YES`
- `T008_NUMERIC_EVIDENCE_UNCHANGED = YES`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1_RECOMMENDATION = YES`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## Source Files

- T008 report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\reports\T008_final_report.md`
- T008 gate summary: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\reports\T008_gate_summary.json`
- T008 progress table: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\tables\T008_progress.csv`
- T008 metrics table: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\tables\T008_recomputed_metrics.csv`
- Requested T008 script path: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\scripts\T008_narrow_diagnostic_displacement_ladder.py` exists=`False`
- Equivalent T008 script path read: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\scripts\T008_narrow_displacement_ladder.py` exists=`True`
- T009 figure manifest: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\tables\T009_t008_figure_manifest.csv`

## Required File Check

- The task-named script `T008_narrow_diagnostic_displacement_ladder.py` is missing: `True`.
- Equivalent T008 script `T008_narrow_displacement_ladder.py` is present and used for audit context: `True`.

## Figure Audit Summary

- `T008_ladder_displacement_response`: original exists `YES`, status `PASS`, SVG `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\images\T009_ladder_displacement_response.svg`.
- `T008_ladder_error_summary`: original exists `YES`, status `PASS`, SVG `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\images\T009_ladder_error_summary.svg`.
- `T008_interface_quality_summary`: original exists `YES`, status `PASS`, SVG `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\images\T009_interface_quality_summary.svg`.

## CSV-Backed Figure Contents

- Displacement response SVG uses columns `legacy_case_id`, `expected_displacement_m`, and `measured_ring_displacement_m`; D3/D4/D5 measured displacements are -10 um, -25 um, and -50 um to table precision.
- Error summary SVG uses columns `legacy_case_id` and `displacement_error_m`; D3/D4/D5 errors are near 1e-19 m, shown in nm.
- Interface quality SVG uses columns `legacy_case_id` and `interface_quality`; all three T008 cases are `clear`.

## Numeric Evidence Check

| case | expected_m | measured_m | error_m | interface_quality | solve/extract/postprocess | HMAX_IS_REAL_PHYSICAL_OUTPUT |
|---|---:|---:|---:|---|---|---|
| `D3` | `-1e-05` | `-1.0000000000000026e-05` | `-2.541098841762901e-20` | `clear` | `PASS/PASS/PASS` | `NO` |
| `D4` | `-2.5e-05` | `-2.5000000000000282e-05` | `-2.812149384884277e-19` | `clear` | `PASS/PASS/PASS` | `NO` |
| `D5` | `-5e-05` | `-5.000000000000013e-05` | `-1.2874900798265365e-19` | `clear` | `PASS/PASS/PASS` | `NO` |

## Next Recommended Task

- Review the SVG/CSV-backed visual audit package. If accepted, Review Agent may create a separate true-geometry Jet1 diagnostic task. Stage 6 and real Hmax remain blocked.
