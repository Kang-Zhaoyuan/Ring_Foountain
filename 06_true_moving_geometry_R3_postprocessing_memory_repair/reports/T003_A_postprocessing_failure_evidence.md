# T003-A Postprocessing Failure Evidence

- Run id: `20260620_131742`
- Blocker type: postprocessing/regional metrics extraction failure.
- COMSOL solve status is `PASS` for G2/G3 and all seven wetted-wall/contactline affected rows; therefore the blocker is likely postprocessing extraction, not COMSOL solving.
- Script reference: `scripts/ring_fountain_06_R3_ring_contactline_isolation.py`.
- Function references: `region_of` around line 269, `regional_metrics_from_arrays` around line 334, `evaluate_model` around line 423.
- Failure trace points to `regional_metrics_from_arrays(...): by.setdefault(region_of(...), []).append(p)` around line 350.

## Affected Ring Geometry Rows

- `G2_ring_deeper_submerged`: solve_status=`PASS`, interface_quality=`extraction_failed`, MemoryError=`True`, model=`D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\03_ring_geometry_position_controls\models\G2_ring_deeper_submerged_20260620_022152.mph`
- `G3_ring_far_below_surface`: solve_status=`PASS`, interface_quality=`extraction_failed`, MemoryError=`True`, model=`D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\03_ring_geometry_position_controls\models\G3_ring_far_below_surface_20260620_022152.mph`
- `G4_ring_above_surface_air_side`: solve_status=`SKIP`, interface_quality=``, MemoryError=`False`, model=``
- `G5_ring_thinner_or_smaller_gap_control`: solve_status=`SKIP`, interface_quality=``, MemoryError=`False`, model=``

## Affected Wetted-Wall/Contactline Rows

- `W0_current_wettedwall`: solve_status=`PASS`, interface_quality=`extraction_failed`, MemoryError=`True`, model=`D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W0_current_wettedwall.mph`
- `W2_contact_angle_60deg`: solve_status=`PASS`, interface_quality=`extraction_failed`, MemoryError=`True`, model=`D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W2_contact_angle_60deg.mph`
- `W3_contact_angle_120deg`: solve_status=`PASS`, interface_quality=`extraction_failed`, MemoryError=`True`, model=`D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W3_contact_angle_120deg.mph`
- `W4_contact_angle_150deg`: solve_status=`PASS`, interface_quality=`extraction_failed`, MemoryError=`True`, model=`D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W4_contact_angle_150deg.mph`
- `W7_user_defined_slip_0p1mm`: solve_status=`PASS`, interface_quality=`extraction_failed`, MemoryError=`True`, model=`D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W7_user_defined_slip_0p1mm.mph`
- `W8_user_defined_slip_0p5mm`: solve_status=`PASS`, interface_quality=`extraction_failed`, MemoryError=`True`, model=`D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W8_user_defined_slip_0p5mm.mph`
- `W10_plain_wall_no_wettedwall_diagnostic`: solve_status=`PASS`, interface_quality=`extraction_failed`, MemoryError=`True`, model=`D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W10_plain_wall_no_wettedwall_diagnostic.mph`
