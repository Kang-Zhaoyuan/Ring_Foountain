# T006 Final Report

- Run id: `20260620_153612`
- Scope: finish remaining contact-angle/slip raw-array extraction and postprocessing recompute.
- No COMSOL study, Stage 6, parameter sweep, Jet1/Jet2 detection, or real Hmax output was performed.

## Gate Values

- `T006_STATUS = PASS`
- `RAW_ARRAY_EXTRACTION_COMPLETED_REMAINING_CASES = YES`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED_REMAINING_CASES = YES`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED_REMAINING_CASES = YES`
- `W2_CONTACT_ANGLE_60_STATUS = PASS`
- `W3_CONTACT_ANGLE_120_STATUS = PASS`
- `W4_CONTACT_ANGLE_150_STATUS = PASS`
- `W7_SLIP_0P1MM_STATUS = PASS`
- `W8_SLIP_0P5MM_STATUS = PASS`
- `CREDIBLE_STATIC_BASELINE_AFTER_T006 = UNKNOWN`
- `CREDIBLE_MICRO_MOTION_BASELINE_AFTER_T006 = UNKNOWN`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## T006 Case Results

- Attempted T006 cases: `5`
- Extraction PASS cases: `5`
- Postprocess PASS cases: `5`

| case_id | extraction_status | postprocess_status | interface_quality | memory_error_resolved | array_path |
|---|---|---|---|---|---|
| `W2_contact_angle_60deg` | `PASS` | `PASS` | `clear` | `YES` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\arrays\T006_01_W2_contact_angle_60deg_20260620_153612.npz` |
| `W3_contact_angle_120deg` | `PASS` | `PASS` | `clear` | `YES` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\arrays\T006_02_W3_contact_angle_120deg_20260620_153612.npz` |
| `W4_contact_angle_150deg` | `PASS` | `PASS` | `clear` | `YES` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\arrays\T006_03_W4_contact_angle_150deg_20260620_153612.npz` |
| `W7_user_defined_slip_0p1mm` | `PASS` | `PASS` | `clear` | `YES` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\arrays\T006_04_W7_user_defined_slip_0p1mm_20260620_153612.npz` |
| `W8_user_defined_slip_0p5mm` | `PASS` | `PASS` | `clear` | `YES` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\arrays\T006_05_W8_user_defined_slip_0p5mm_20260620_153612.npz` |

## Merged Evidence

- Merged T004/T005/T006 metrics table: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\tables\T006_merged_T004_T005_T006_metrics.csv`
- Merged rows available: `9`

## Next Recommended Task

- Review the completed raw-array extraction/recompute package and decide whether a diagnostic displacement ladder is justified. Stage 6, Jet1, and real Hmax remain blocked.
