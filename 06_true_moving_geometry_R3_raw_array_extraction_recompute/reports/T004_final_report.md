# T004 Final Report

- Run id: `20260620_142426`
- Scope: raw-array extraction and postprocessing recompute from saved models only.
- No COMSOL study, Stage 6, parameter sweep, Jet1/Jet2 detection, or real Hmax output was performed.

## Gate Values

- `T004_STATUS = PARTIAL`
- `RAW_ARRAY_EXTRACTION_COMPLETED = PARTIAL`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED = YES`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED = YES`
- `CREDIBLE_STATIC_BASELINE_AFTER_RECOMPUTE = NO`
- `CREDIBLE_MICRO_MOTION_BASELINE_AFTER_RECOMPUTE = UNKNOWN`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## Case Results

- Attempted cases: `2`
- Extraction PASS cases: `2`
- Postprocess PASS cases: `2`

| case_id | extraction_status | postprocess_status | interface_quality | memory_error_resolved | array_path |
|---|---|---|---|---|---|
| `G2_ring_deeper_submerged` | `PASS` | `PASS` | `clear` | `YES` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\arrays\01_G2_ring_deeper_submerged_20260620_134239.npz` |
| `G3_ring_far_below_surface` | `PASS` | `PASS` | `clear` | `YES` | `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\arrays\02_G3_ring_far_below_surface_20260620_134239.npz` |

## Next Recommended Task

- Continue resumable T004 extraction for remaining priority cases if Review Agent needs W10/W0/contact-angle/slip rows. Stage advancement remains blocked.
