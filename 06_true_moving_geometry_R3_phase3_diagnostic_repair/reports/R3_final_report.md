# R3 Final Report

- Run id: `20260620_113028`
- Active task: `tasks/NEXT_TASK.md` / `tasks/20260620_110300_T001_true_geometry_R3_phase3_repair.md`
- R2 source state: `FAIL_PHASE3`
- Scope: Phase-3 diagnostic repair only.
- Stage 6, parameter sweep, Jet1/Jet2 detection, and real Hmax output were not performed.

## Gate Decision

- `R3_STATUS = FAIL`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## Repair Ladder Summary

| case_id | changed_factor | status | max_displacement_m | min_mesh_quality | pseudo_spike_metric |
|---|---|---:|---:|---:|---|
| `C0_zero_displacement_baseline` | C0 zero-displacement baseline check | `FAIL_DIAGNOSTIC` | `1.734723475976807e-17` | `1.0` | `pseudo_spike_ROI_flag=True` |
| `C1_micro_displacement_baseline` | C1 micro-displacement case | `FAIL_DIAGNOSTIC` | `5.00000000000023e-06` | `1.0` | `pseudo_spike_ROI_flag=True` |
| `C2_shorter_time_horizon` | C2 shorter time horizon only | `FAIL_DIAGNOSTIC` | `1.0000000000001327e-06` | `1.0` | `pseudo_spike_ROI_flag=True` |
| `C3_smaller_time_step` | C3 smaller time step only | `FAIL_DIAGNOSTIC` | `5.00000000000023e-06` | `1.0` | `pseudo_spike_ROI_flag=True` |
| `C4_smooth_displacement_ramp` | C4 smoother displacement ramp only | `FAIL_DIAGNOSTIC` | `5.000002301572357e-06` | `1.0` | `pseudo_spike_ROI_flag=True` |
| `C5_levelset_eps_2mm` | C5 level-set interface thickness only | `FAIL_DIAGNOSTIC` | `5.00000000000023e-06` | `1.0` | `pseudo_spike_ROI_flag=True` |

## Interpretation

- R3 keeps the R2 interpretation that Phase-3 failure is a diagnostic interface-quality failure rather than a COMSOL transient-solver crash.
- Mesh quality/ALE inversion remains unsupported as the dominant cause when mesh metrics remain finite and near unity.
- Because no single-factor R3 repair produced both a clear zero-displacement and clear micro-displacement baseline, the branch remains gated.

## Key Paths

- Evidence report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_phase3_diagnostic_repair\reports\R3_A_evidence_consolidation.md`
- Minimal repro report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_phase3_diagnostic_repair\reports\R3_B_minimal_phase3_repro_report.md`
- Repair ladder CSV: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_phase3_diagnostic_repair\tables\R3_C_repair_ladder_summary.csv`
- Raw rows JSON: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_phase3_diagnostic_repair\reports\R3_BC_raw_rows.json`
- Primary log: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_phase3_diagnostic_repair\logs\R3_B_minimal_phase3_repro_20260620_113028.log`
