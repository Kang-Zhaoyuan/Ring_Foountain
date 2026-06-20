# R3-A Evidence Consolidation

- Run id: `20260620_113028`
- Latest trusted model branch: `true-moving-geometry diagnostic branch; R2 terminal state FAIL_PHASE3`
- Exact R2 failure point: `Phase 3 level-set/solver stabilization failed: all attempted B0/B1 single-factor cases solved but remained weak_or_spiky under ROI-aware interface diagnostics.`
- Best available prior model path: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_campaign\03_true_moving_ring_smoke\models\true_moving_ring_smoke_best.mph`

## R2 Phase Table

| Phase | Status |
|---|---|
| Phase0 | PASS |
| Phase1 | PASS |
| Phase2 | PASS |
| Phase3 | FAIL |
| Phase4 | SKIPPED |
| Phase5 | SKIPPED |

## R2 Phase-3 Failure Evidence

- Phase-3 case count: `20`
- Phase-3 pass count: `0`
- Failure meaning: diagnostic gate failure, not a broad physical conclusion and not a real Hmax result.
- Typical terminal diagnostic: `pseudo_spike_ROI_flag = True`, `interface_quality = weak_or_spiky`, with finite solve results.

## Suspected Cause Categories

- interface pseudo-spike or level-set/static relaxation noise remains supported
- velocity-amplified ALE-LS oscillation is not supported by R2
- mesh inversion/ALE displacement instability is not supported by R2 mesh metrics
- ring geometry, WettedWall contact line, and initialization semantics remain plausible
- script/API construction failure is lower probability because R2 cases solve repeatedly

## Evidence Files Used

- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\README.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\tasks\README.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\tasks\TASK_INDEX.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\tasks\NEXT_TASK.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\tasks\20260620_110300_T001_true_geometry_R3_phase3_repair.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R2_interface_noise_isolation\reports\06_R2_true_moving_geometry_interface_noise_isolation_final_report.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R2_interface_noise_isolation\reports\06_R2_true_moving_geometry_interface_noise_isolation_summary.json`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R2_interface_noise_isolation\logs\06_R2_interface_noise_isolation_20260619_210233.log`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R2_interface_noise_isolation\03_levelset_solver_stabilization\tables\stabilization_cases.csv`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R2_interface_noise_isolation\02_static_control_decomposition\reports\static_control_decomposition_report.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R2_interface_noise_isolation\01_extraction_algorithm_audit\reports\interface_extraction_algorithm_audit.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R2_interface_noise_isolation\00_R1_audit\reports\R1_failure_reinterpretation_report.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R1_diagnostic_repair\reports\06_R1_true_moving_geometry_diagnostic_repair_final_report.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R1_diagnostic_repair\03_zero_motion_regression\reports\D_zero_and_micro_motion_regression_report.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_campaign\reports\true_moving_geometry_campaign_final_report.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_campaign\03_true_moving_ring_smoke\reports\true_moving_ring_smoke_report.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_campaign\04_true_moving_ring_stability\reports\true_moving_ring_stability_report.md`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\scripts\ring_fountain_06_R2_interface_noise_isolation.py`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\scripts\ring_fountain_06_R1_true_moving_geometry_diagnostic_repair.py`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\scripts\ring_fountain_stage6_true_moving_geometry_campaign.py`
