# T003 Final Report

- Run id: `20260620_131742`
- Scope: postprocessing repair only; no COMSOL solve rerun, no Stage 6, no Jet1/Jet2 detection, no real Hmax.

## Gate Values

- `T003_STATUS = PARTIAL`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED = NO`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED = NO`
- `CREDIBLE_STATIC_BASELINE_AFTER_POSTPROCESSING = NO`
- `CREDIBLE_MICRO_MOTION_BASELINE_AFTER_POSTPROCESSING = UNKNOWN`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`

## Summary

- Recomputed rows: `11`
- Postprocess PASS rows: `0`
- Rows without saved model/raw arrays: `2`
- Rows deferred because COMSOL raw arrays are not materialized in repository artifacts: `9`
- Failed postprocess rows after repair: `0`
- MemoryError rows resolved: `0/9`
- Interpretation: the memory-safe implementation is available, but full recomputation could not be completed in this bounded run because raw arrays are only inside `.mph` models and COMSOL reload exceeded runtime. Existing evidence still does not establish a credible static or micro-motion baseline.

## Key Outputs

- Evidence report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_postprocessing_memory_repair\reports\T003_A_postprocessing_failure_evidence.md`
- Ring repaired table: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_postprocessing_memory_repair\tables\T003_ring_geometry_position_cases_repaired.csv`
- Wetted-wall repaired table: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_postprocessing_memory_repair\tables\T003_wettedwall_contactline_cases_repaired.csv`
- Images directory: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_postprocessing_memory_repair\images`
