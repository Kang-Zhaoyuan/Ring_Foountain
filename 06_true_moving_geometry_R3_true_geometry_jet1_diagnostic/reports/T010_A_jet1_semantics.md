# T010-A Jet1 Diagnostic Semantics

- Run id: `20260620_164644`
- Scope: narrow true-geometry Jet1 diagnostic evidence only.
- `JET1_DIAGNOSTIC_SEMANTICS_RECOVERED = YES`
- Stage 6 logic is excluded.
- Real Hmax output is excluded.
- Jet1/Jet2 physical conclusions are excluded.

## Definition Sources

- Fixed-geometry 5C ROI definition only: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5C_jet1_extraction\reports\B_jet1_definition_and_ROI_report.md`.
- Fixed-geometry 5C candidate-diagnostic exclusion rules: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5C_jet1_extraction\reports\D_jet1_candidate_detection_report.md`.
- True-geometry D-ladder state: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\reports\T008_final_report.md`.
- T008 visual audit gate: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\reports\T009_t008_visual_audit_report.md`.

## ROI Semantics Reused Only As Diagnostic Geometry

- Center-hole ROI: `0 <= r <= 0.006` and `z >= 0.0`.
- Inner-edge ROI: `0.0039000000000000003 <= r <= 0.0081` and `z >= 0.0`.
- The ROI is used to compute auditable shape indicators, not to assert physical Jet1 detection.

## Case Definitions

| case | source | Vring | expected displacement | model | difference from J0 |
|---|---|---|---:|---|---|
| `J0_static_baseline_for_jet1_diagnostic` | `D0_zero_motion_regression` | `0[m/s]` | `-0.0` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R1_diagnostic_repair\03_zero_motion_regression\models\D0_20260619_165307.mph` | static baseline |
| `J1_true_geometry_jet1_diagnostic` | `D5_diagnostic_displacement_5e_minus_5m` | `1e-2[m/s]` | `-5e-05` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\models\T008_D5_20260620_161207.mph` | uses T008 D5 moving true-geometry diagnostic model |
