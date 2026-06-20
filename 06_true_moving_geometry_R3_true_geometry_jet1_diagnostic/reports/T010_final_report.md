# T010 Final Report

- Run id: `20260620_164644`
- Scope: narrow true-geometry Jet1 diagnostic evidence using saved J0/J1 models.
- No Stage 6, broad parameter sweep, Jet1/Jet2 physical conclusion, or real Hmax output was performed.

## Gate Values

- `T010_STATUS = PASS`
- `JET1_DIAGNOSTIC_SEMANTICS_RECOVERED = YES`
- `J0_STATUS = PASS`
- `J1_STATUS = PASS`
- `RAW_ARRAY_EXTRACTION_COMPLETED = YES`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED = YES`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED = YES`
- `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`
- `JET1_PHYSICAL_CONCLUSION_MADE = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = YES`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## Case Results

| case | source | status | interface_quality | roi_max_delta_m | shape_threshold_crossed | array_path |
|---|---|---|---|---:|---|---|
| `J0` | `D0_zero_motion_regression` | `PASS` | `clear` | `6.0691962701962614e-06` | `False` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_true_geometry_jet1_diagnostic\arrays\T010_J0_static_baseline_for_jet1_diagnostic_20260620_164644.npz` |
| `J1` | `D5_diagnostic_displacement_5e_minus_5m` | `PASS` | `clear` | `4.34916959663216e-06` | `False` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_true_geometry_jet1_diagnostic\arrays\T010_J1_true_geometry_jet1_diagnostic_20260620_164644.npz` |

## Interpretation Guardrails

- `jet1_diagnostic_shape_threshold_crossed` is a diagnostic shape flag only.
- It is not `Jet1_detected`, not Jet2, and not real Hmax.
- H values in this report remain non-physical diagnostic postprocessing outputs.

## Semantics Source

- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_true_geometry_jet1_diagnostic\reports\T010_A_jet1_semantics.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5C_jet1_extraction\reports\B_jet1_definition_and_ROI_report.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\reports\T008_final_report.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\reports\T009_t008_visual_audit_report.md`

## Audit Figures

- Figure manifest: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_true_geometry_jet1_diagnostic\tables\T010_figure_manifest.csv`

## Next Recommended Task

- Review T010 diagnostics. If accepted, Review Agent may define the next bounded true-geometry Jet1 track; Stage 6 and real Hmax remain blocked.
