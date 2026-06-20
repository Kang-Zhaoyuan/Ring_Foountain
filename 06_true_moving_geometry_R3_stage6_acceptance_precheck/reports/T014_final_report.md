# T014 Final Report

- Run id: `20260620_180015`
- Scope: bounded no-Stage6 acceptance precheck against existing evidence.
- No COMSOL run, Stage 6, parameter sweep, current Jet1 continuation, Jet1 physical conclusion, or real Hmax output was performed.

## Gate Values

- `T014_STATUS = PASS`
- `ACCEPTANCE_PRECHECK_COMPLETED = YES`
- `PHYSICAL_RING_MOTION_VALIDITY = PARTIAL`
- `ALE_WETTEDWALL_NON_DOUBLE_COUNTING = PARTIAL`
- `BOUNDARY_CONTACTLINE_VALIDITY = NO`
- `CONNECTED_INTERFACE_EXTRACTION_VALIDITY = PARTIAL`
- `REAL_HMAX_EXECUTABLE_NOW = NO`
- `MINIMUM_CONTROLS_COMPLETE = PARTIAL`
- `CURRENT_JET1_BRANCH_ALLOWED = NO`
- `ALLOW_STAGE6_NOW = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_BOUNDED_STAGE6_CANDIDATE_TASK = NO`

## Precheck Decision

No existing true-geometry candidate evidence is currently close enough to justify a bounded Stage 6 candidate task. T008/T007 provide useful diagnostic ALE motion evidence, and T004-T006 provide repaired extraction/control evidence, but the acceptance precheck fails the decisive physical-contactline and real-Hmax executability criteria.

The current Jet1 branch remains closed. T011/T014 may be used only as negative-control/reference evidence, not as positive Jet1 evidence and not as a real-Hmax route.

## Outputs

- Candidate manifest: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_stage6_acceptance_precheck\tables\T014_candidate_evidence_manifest.csv`
- Acceptance precheck matrix: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_stage6_acceptance_precheck\tables\T014_acceptance_precheck_matrix.csv`
- Non-real-Hmax extractor feasibility: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_stage6_acceptance_precheck\tables\T014_nonreal_hmax_extractor_feasibility.csv`
- Decision map: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_stage6_acceptance_precheck\images\T014_acceptance_precheck_decision_map.svg`
- Gate summary: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_stage6_acceptance_precheck\reports\T014_gate_summary.json`

## Input Coverage

Missing inputs: `none`

## Next Recommended Task

Run a bounded no-Stage6 contactline/control-completeness repair task: classify WettedWall/contactline physical validity, verify dx/utr non-double-counting, and add or identify mesh/time-step sensitivity evidence without outputting real Hmax.
