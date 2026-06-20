# T004-A Extraction Plan

- Run id: `20260620_142426`
- Scope: raw-array extraction and postprocessing recompute from existing saved `.mph` models only.
- No studies are run; no Stage 6, parameter sweep, Jet1/Jet2 detection, or real Hmax output is performed.
- The script processes one model at a time and appends progress immediately after each case.
- Default case budget: `2` priority cases.

## Priority Order

1. `G2_ring_deeper_submerged` -> `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\03_ring_geometry_position_controls\models\G2_ring_deeper_submerged_20260620_022152.mph` exists=`True`
2. `G3_ring_far_below_surface` -> `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\03_ring_geometry_position_controls\models\G3_ring_far_below_surface_20260620_022152.mph` exists=`True`
3. `W10_plain_wall_no_wettedwall_diagnostic` -> `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W10_plain_wall_no_wettedwall_diagnostic.mph` exists=`True`
4. `W0_current_wettedwall` -> `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W0_current_wettedwall.mph` exists=`True`
5. `W2_contact_angle_60deg` -> `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W2_contact_angle_60deg.mph` exists=`True`
6. `W3_contact_angle_120deg` -> `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W3_contact_angle_120deg.mph` exists=`True`
7. `W4_contact_angle_150deg` -> `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W4_contact_angle_150deg.mph` exists=`True`
8. `W7_user_defined_slip_0p1mm` -> `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W7_user_defined_slip_0p1mm.mph` exists=`True`
9. `W8_user_defined_slip_0p5mm` -> `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_ring_contactline_isolation\04_wettedwall_contactline_controls\models\W8_user_defined_slip_0p5mm.mph` exists=`True`
