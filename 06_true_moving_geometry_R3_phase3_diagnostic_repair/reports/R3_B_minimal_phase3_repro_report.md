# R3-B Minimal Phase-3 Reproduction Report

- Run id: `20260620_113028`
- Phase 3 failure reproduced: `True`
- Deterministic across repeat: `YES`
- Minimal reproduction case: `B_repro_micro_displacement`, generated with `Vring = 1e-3[m/s]`, `t_end = 0.005[s]`, `dt = 1e-4[s]`.
- Failure step/time: diagnostic evaluation at final inner solution, `t = 0.005 s`, after successful transient solve.
- Failure type: diagnostic gate failure, not a solver crash.

## Exact Error / Failure Messages

- `No COMSOL solver exception. Failure is reproduced as a deterministic diagnostic gate failure: pseudo_spike_ROI_flag remains True / interface_quality remains weak_or_spiky.`

## Reproduction Rows

- `B_repro_micro_displacement`: status=`FAIL_DIAGNOSTIC`, model=`D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_phase3_diagnostic_repair\models\B_repro_micro_displacement_20260620_113028.mph`, pseudo_spike_ROI_flag=True, interface_roughness_final=0.001057994360024874
- `B_repro_micro_displacement_repeat`: status=`FAIL_DIAGNOSTIC`, model=`D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_phase3_diagnostic_repair\models\B_repro_micro_displacement_repeat_20260620_113028.mph`, pseudo_spike_ROI_flag=True, interface_roughness_final=0.0010579943600248932
