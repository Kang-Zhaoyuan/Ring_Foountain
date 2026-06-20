# T003 Raw Array Recompute Manifest

- Run id: `20260620_131742`
- The memory-safe regional metrics implementation is present in `scripts/T003_postprocessing_memory_repair.py`.
- Existing CSV/JSON/image artifacts do not contain raw `r`, `z`, and `phils` result arrays.
- A direct COMSOL reload attempt in this Builder run exceeded the bounded runtime after completing/entering early model reloads.
- Full recomputation requires loading each saved `.mph` model and evaluating `r`, `z`, `phils`, and `t` at initial/final inner solutions.
- Command for full attempt:

```powershell
$env:T003_ATTEMPT_COMSOL='1'
.venv\Scripts\python.exe 06_true_moving_geometry_R3_postprocessing_memory_repair\scripts\T003_postprocessing_memory_repair.py
```

## Deferred Rows

- `G2_ring_deeper_submerged`: postprocess_status=`RECOMPUTE_DEFERRED_COMSOL_RELOAD_TIMEOUT`, required=`COMSOL result arrays from D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\03_ring_geometry_position_controls\models\G2_ring_deeper_submerged_20260620_022152.mph`
- `G3_ring_far_below_surface`: postprocess_status=`RECOMPUTE_DEFERRED_COMSOL_RELOAD_TIMEOUT`, required=`COMSOL result arrays from D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\03_ring_geometry_position_controls\models\G3_ring_far_below_surface_20260620_022152.mph`
- `G4_ring_above_surface_air_side`: postprocess_status=`SKIP_RAW_MODEL_UNAVAILABLE`, required=`A solved model artifact for this skipped case`
- `G5_ring_thinner_or_smaller_gap_control`: postprocess_status=`SKIP_RAW_MODEL_UNAVAILABLE`, required=`A solved model artifact for this skipped case`
- `W0_current_wettedwall`: postprocess_status=`RECOMPUTE_DEFERRED_COMSOL_RELOAD_TIMEOUT`, required=`COMSOL result arrays from D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W0_current_wettedwall.mph`
- `W2_contact_angle_60deg`: postprocess_status=`RECOMPUTE_DEFERRED_COMSOL_RELOAD_TIMEOUT`, required=`COMSOL result arrays from D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W2_contact_angle_60deg.mph`
- `W3_contact_angle_120deg`: postprocess_status=`RECOMPUTE_DEFERRED_COMSOL_RELOAD_TIMEOUT`, required=`COMSOL result arrays from D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W3_contact_angle_120deg.mph`
- `W4_contact_angle_150deg`: postprocess_status=`RECOMPUTE_DEFERRED_COMSOL_RELOAD_TIMEOUT`, required=`COMSOL result arrays from D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W4_contact_angle_150deg.mph`
- `W7_user_defined_slip_0p1mm`: postprocess_status=`RECOMPUTE_DEFERRED_COMSOL_RELOAD_TIMEOUT`, required=`COMSOL result arrays from D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W7_user_defined_slip_0p1mm.mph`
- `W8_user_defined_slip_0p5mm`: postprocess_status=`RECOMPUTE_DEFERRED_COMSOL_RELOAD_TIMEOUT`, required=`COMSOL result arrays from D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W8_user_defined_slip_0p5mm.mph`
- `W10_plain_wall_no_wettedwall_diagnostic`: postprocess_status=`RECOMPUTE_DEFERRED_COMSOL_RELOAD_TIMEOUT`, required=`COMSOL result arrays from D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W10_plain_wall_no_wettedwall_diagnostic.mph`
