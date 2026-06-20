# T013 Final Report

- Run id: `20260620_173514`
- Scope: true-geometry model-semantics repair package and Stage 6 acceptance criteria only.
- No COMSOL run, Stage 6, parameter sweep, current Jet1 continuation, Jet1 physical conclusion, or real Hmax output was performed.

## Gate Values

- `T013_STATUS = PASS`
- `MODEL_SEMANTICS_REPAIRED = PARTIAL`
- `ALE_RING_MOTION_SEMANTICS_VALID = PARTIAL`
- `WETTEDWALL_CONTACTLINE_SEMANTICS_VALID = UNKNOWN`
- `INTERFACE_EXTRACTION_PHYSICAL_VALIDITY = PARTIAL`
- `REAL_HMAX_DEFINITION_READY = PARTIAL`
- `STAGE6_ACCEPTANCE_CRITERIA_READY = YES`
- `CURRENT_JET1_BRANCH_ALLOWED = NO`
- `ALLOW_STAGE6_NOW = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_BOUNDED_STAGE6_PRECHECK = YES`

## Semantics Repair Result

The intended true-geometry ring motion meaning is: the ring boundary geometry is moved by ALE `PrescribedMeshDisplacement` with vertical displacement `-Vring*t` on confirmed ring boundaries `[4, 5, 6, 7]`. WettedWall `utr=[0,-Vring,0]` may remain as a wall-frame/contactline condition, but it is not sufficient proof of geometry motion by itself and must not be double-counted as an additional physical translation.

Current ALE and displacement semantics are consistent enough for diagnostic use, because campaign reports and D-ladder exports show ALE displacement and measured diagnostic displacement. They are not sufficient for Stage 6 or real Hmax because contactline semantics, physical interface-height validity, and real-Hmax acceptance controls have not passed.

WettedWall/contactline semantics remain the weakest area. The code exports contain NavierSlip, contact angle `pi/2`, and `utr=-Vring`, but the R3 contactline report did not find clear physical WettedWall cases. This keeps boundary/contactline validity at `UNKNOWN`.

Interface extraction is `PARTIAL`: repaired extraction avoids known raw-global contamination and passes diagnostic tables, but no output is yet a validated physical height. T013 defines what must be true for real Hmax, but does not produce real Hmax.

## Outputs

- Source inventory: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_model_semantics_repair\tables\T013_semantics_source_inventory.csv`
- Semantics consistency matrix: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_model_semantics_repair\tables\T013_semantics_consistency_matrix.csv`
- Stage 6 acceptance criteria: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_model_semantics_repair\reports\T013_stage6_acceptance_criteria.md`
- Gate summary: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_model_semantics_repair\reports\T013_gate_summary.json`
- Gate map: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_model_semantics_repair\images\T013_model_semantics_gate_map.svg`

## Input Coverage

Missing inputs: `none`

## Next Recommended Task

Run a bounded no-Stage6 acceptance precheck against existing true-geometry candidate evidence: verify ALE/wall-frame non-double-counting, contactline physical classification, connected-interface Hmax extractor criteria, and required control-case checklist without outputting real Hmax.
