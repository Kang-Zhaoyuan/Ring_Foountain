# T007-A D0/D1/D2 Semantics

- Run id: `20260620_155039`
- Historical report: `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/reports/D_zero_and_micro_motion_regression_report.md`.
- Historical table: `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/tables/D_zero_and_micro_motion_cases.csv`.
- Java exports inspected: `D0_20260619_165307.java`, `D1_20260619_165307.java`, `D2_20260619_165307.java`.
- `D0_D1_D2_SEMANTICS_RECOVERED = YES`
- Baseline candidate used for interpretation: repaired R3 raw-array baseline/control package from T004/T005/T006, especially merged table `T006_merged_T004_T005_T006_metrics.csv`.
- No ambiguity remains.

## Recovered Definitions

| case_id | legacy_id | Vring | t_end | dt | ALE displacement | WettedWall velocity | expected displacement |
|---|---|---|---|---|---|---|---|
| `D0_zero_motion_regression` | `D0` | `0[m/s]` | `0.005[s]` | `1e-4[s]` | `dx=[0,-Vring*t]` | `utr=[0,-Vring,0]` | `-0.0` |
| `D1_micro_motion_regression` | `D1` | `1e-4[m/s]` | `0.005[s]` | `1e-4[s]` | `dx=[0,-Vring*t]` | `utr=[0,-Vring,0]` | `-5e-07` |
| `D2_micro_motion_regression` | `D2` | `1e-3[m/s]` | `0.005[s]` | `1e-4[s]` | `dx=[0,-Vring*t]` | `utr=[0,-Vring,0]` | `-5e-06` |
