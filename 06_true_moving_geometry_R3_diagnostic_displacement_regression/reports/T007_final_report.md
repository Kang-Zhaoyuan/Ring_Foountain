# T007 Final Report

- Run id: `20260620_155039`
- Scope: diagnostic D0/D1/D2 displacement regression using repaired raw-array/postprocessing only.
- No COMSOL study, Stage 6, broad parameter sweep, Jet1/Jet2 detection, or real Hmax output was performed.

## Gate Values

- `T007_STATUS = PASS`
- `D0_STATUS = PASS`
- `D1_STATUS = PASS`
- `D2_STATUS = PASS`
- `D0_D1_D2_SEMANTICS_RECOVERED = YES`
- `RAW_ARRAY_EXTRACTION_COMPLETED = YES`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED = YES`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED = YES`
- `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = YES`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## Case Results

| case_id | Vring | expected_displacement_m | measured_ring_displacement_m | interface_quality | status | array_path |
|---|---|---:|---:|---|---|---|
| `D0_zero_motion_regression` | `0[m/s]` | `-0.0` | `-2.6020852139652106e-18` | `clear` | `PASS` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\arrays\T007_D0_zero_motion_regression_20260620_155039.npz` |
| `D1_micro_motion_regression` | `1e-4[m/s]` | `-5e-07` | `-5.000000000000664e-07` | `clear` | `PASS` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\arrays\T007_D1_micro_motion_regression_20260620_155039.npz` |
| `D2_micro_motion_regression` | `1e-3[m/s]` | `-5e-06` | `-5.00000000000023e-06` | `clear` | `PASS` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\arrays\T007_D2_micro_motion_regression_20260620_155039.npz` |

## Semantics Source

- `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/tables/D_zero_and_micro_motion_cases.csv`
- `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/exports/D0_20260619_165307.java`
- `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/exports/D1_20260619_165307.java`
- `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/exports/D2_20260619_165307.java`

## Next Recommended Task

- Review T007 diagnostics. If accepted, the next task may be a narrow diagnostic displacement ladder; Stage 6, Jet1, and real Hmax remain blocked.
