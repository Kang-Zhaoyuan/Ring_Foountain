# T008 Final Report

- Run id: `20260620_161207`
- Scope: narrow diagnostic displacement ladder D3/D4/D5 only.
- No Stage 6, broad parameter sweep, Jet1/Jet2 detection, or real physical Hmax output was performed.

## Gate Values

- `T008_STATUS = PASS`
- `D3_STATUS = PASS`
- `D4_STATUS = PASS`
- `D5_STATUS = PASS`
- `D_LADDER_SEMANTICS_CLEAR = YES`
- `RAW_ARRAY_EXTRACTION_COMPLETED = YES`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED = YES`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED = YES`
- `DISPLACEMENT_RESPONSE_MONOTONIC_OR_EXPLAINED = YES`
- `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = YES`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## Case Results

| case_id | Vring | expected_displacement_m | measured_ring_displacement_m | displacement_error_m | interface_quality | status | array_path |
|---|---|---:|---:|---:|---|---|---|
| `D3_diagnostic_displacement_1e_minus_5m` | `2e-3[m/s]` | `-1e-05` | `-1.0000000000000026e-05` | `-2.541098841762901e-20` | `clear` | `PASS` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\arrays\T008_D3_diagnostic_displacement_1e_minus_5m_20260620_161207.npz` |
| `D4_diagnostic_displacement_2p5e_minus_5m` | `5e-3[m/s]` | `-2.5e-05` | `-2.5000000000000282e-05` | `-2.812149384884277e-19` | `clear` | `PASS` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\arrays\T008_D4_diagnostic_displacement_2p5e_minus_5m_20260620_161207.npz` |
| `D5_diagnostic_displacement_5e_minus_5m` | `1e-2[m/s]` | `-5e-05` | `-5.000000000000013e-05` | `-1.2874900798265365e-19` | `clear` | `PASS` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\arrays\T008_D5_diagnostic_displacement_5e_minus_5m_20260620_161207.npz` |

## Displacement Monotonicity

- `Measured displacement becomes more negative monotonically with expected diagnostic displacement.`

## Figures

- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\images\T008_ladder_displacement_response.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\images\T008_ladder_error_summary.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\images\T008_interface_quality_summary.png`

## Semantics Source

- `06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T007_A_d0_d1_d2_semantics.md`
- `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/models/D2_20260619_165307.mph`
- New D3/D4/D5 cases changed only `Vring` relative to the D2 template.

## Next Recommended Task

- Review T008 diagnostic ladder. If accepted, Review Agent may decide whether a true-geometry Jet1 diagnostic task is justified; Stage 6 and real Hmax remain blocked.
