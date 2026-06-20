# T005 Final Report

- Run id: `20260620_150203`
- Scope: continuation of T004 raw-array extraction and postprocessing recompute for remaining cases.
- No COMSOL study, Stage 6, parameter sweep, Jet1/Jet2 detection, or real Hmax output was performed.

## Gate Values

- `T005_STATUS = PARTIAL`
- `RAW_ARRAY_EXTRACTION_COMPLETED_REMAINING_CASES = PARTIAL`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED_REMAINING_CASES = YES`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED_REMAINING_CASES = YES`
- `W10_PLAIN_WALL_BASELINE_STATUS = PASS`
- `W0_CURRENT_WETTEDWALL_STATUS = PASS`
- `CREDIBLE_STATIC_BASELINE_AFTER_T005 = UNKNOWN`
- `CREDIBLE_MICRO_MOTION_BASELINE_AFTER_T005 = UNKNOWN`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## T005 Case Results

- Attempted T005 cases: `2`
- Extraction PASS cases: `2`
- Postprocess PASS cases: `2`

| case_id | extraction_status | postprocess_status | interface_quality | memory_error_resolved | array_path |
|---|---|---|---|---|---|
| `W10_plain_wall_no_wettedwall_diagnostic` | `PASS` | `PASS` | `clear` | `YES` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\arrays\T005_01_W10_plain_wall_no_wettedwall_diagnostic_20260620_150203.npz` |
| `W0_current_wettedwall` | `PASS` | `PASS` | `clear` | `YES` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\arrays\T005_02_W0_current_wettedwall_20260620_150203.npz` |

## Merged Evidence

- Merged T004/T005 metrics table: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\tables\T005_merged_T004_T005_metrics.csv`
- Merged rows available: `4`

## Next Recommended Task

- Continue T005 extraction for the remaining contact-angle/slip cases if Review Agent needs all seven remaining rows before gate review. Stage advancement remains blocked.
