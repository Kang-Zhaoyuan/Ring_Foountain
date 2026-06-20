# T008-A Ladder Semantics

- Run id: `20260620_161207`
- Source semantics: `06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T007_A_d0_d1_d2_semantics.md`.
- Anchor metrics: `06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T007_recomputed_metrics.csv`.
- Template model for new cases: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R1_diagnostic_repair\03_zero_motion_regression\models\D2_20260619_165307.mph`.
- `D_LADDER_SEMANTICS_CLEAR = YES`
- New cases remain diagnostic-only and keep `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`.
- No Stage 6, Jet1/Jet2 detection, broad parameter sweep, or real Hmax output is allowed.

## Reused Anchor Semantics

- D0/D1/D2 use `dx=[0,-Vring*t]`, `utr=[0,-Vring,0]`, `t_end=0.005[s]`, `dt=1e-4[s]`.
- T008 applies the same equations to D3/D4/D5 and changes only `Vring` relative to the D2 template.

## New Diagnostic Cases

| case_id | legacy_id | Vring | t_end | dt | expected displacement | diagnostic-only |
|---|---|---|---|---|---:|---|
| `D3_diagnostic_displacement_1e_minus_5m` | `D3` | `2e-3[m/s]` | `0.005[s]` | `1e-4[s]` | `-1e-05` | YES |
| `D4_diagnostic_displacement_2p5e_minus_5m` | `D4` | `5e-3[m/s]` | `0.005[s]` | `1e-4[s]` | `-2.5e-05` | YES |
| `D5_diagnostic_displacement_5e_minus_5m` | `D5` | `1e-2[m/s]` | `0.005[s]` | `1e-4[s]` | `-5e-05` | YES |
