# COMSOL Ring Fountain Simulation

Project goal: build staged COMSOL numerical models for the IYPT 2026 Ring Fountain problem.

## Current Trusted Stage Status

- Stage 0 audit: completed.
- Stage 1 checked copy: completed.
- Stage 2 parameter sweep and calibrated continuation: completed.
- Stage 3 relative-flow model: `PASS`.
- Stage 4 fixed-geometry moving-wall ring model: `PASS`.
- Stage 5A static air-water interface smoke test: `PASS`.
- Stage 5B1 reduced center-forcing pipeline demo: `PASS`, approximate only.
- Stage 5B2 rebuilt static ring + free-surface smoke test: `PASS`.
- Stage 5B3 fixed geometry + moving wall + free surface: `FAIL` after original cases and three repair attempts.
- Stage 5B4/5C/5D/5E and Stage 6: `NOT_RUN` because 5B3 did not pass.
- `ALLOW_STAGE_6 = NO`.

## Key Models

- V0 GUI baseline: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\ring_fountain_v0_single_phase\ring_fountain_v0_single_phase.mph`.
- Stage 3 relative-flow model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\03_relative_flow_model\models\ring_fountain_v2_relative_flow.mph`.
- Stage 4 moving-wall model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\models\ring_fountain_v3_moving_ring.mph`.
- Stage 5A static interface model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\models\ring_fountain_v4_5A_static_interface.mph`.
- Stage 5B2-1 static ring model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\models\ring_fountain_v5B2_1_static_ring_free_surface.mph`.
- Stage 5B2-3 boundary-confirmed model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\models\ring_fountain_v5B2_3_static_ring_free_surface_boundary_confirmed.mph`.

## Stage 4 Boundary Confirmation

- Manual review result: `PASS`.
- Confirmed ring-wall boundaries: `[4, 5, 6, 7]`.
- Named selections written into the Stage 4 model: `sel_ring_wall_inner`, `sel_ring_wall_outer`, `sel_ring_wall_top`, `sel_ring_wall_bottom`, `sel_ring_wall_confirmed`.
- Stage 4 is a fixed-geometry moving-wall velocity model. The ring outline does not physically translate.

## Stage 5A Static Interface Smoke Test

- Stage 5A status: `PASS`.
- 5A is not a ring-fountain model and does not extract `Hmax`.
- The tested API exposed standalone `LaminarFlow` and `LevelSet`; the combined `Laminar Two-Phase Flow, Level Set` type was not available through tested type names. 5A therefore uses minimal manual `LaminarFlow + LevelSet` coupling.

## Stage 5B2 Rebuild

- 5B2-0 route diagnosis: `PASS`; prior `Unsupported geometry` was traced to an old `IntLine` boundary-metric API call, not to a failed boolean geometry or physics solve.
- 5B2-1 static ring/free-surface smoke test: `PASS`.
- 5B2-2 ring boundary review: `PASS`; `AUTO_BOUNDARY_REVIEW = PASS`.
- Confirmed rebuilt-model ring boundaries: `[4, 5, 6, 7]`, selected by coordinate-based COMSOL `Box` selections and written to `sel_5B2_ring_wall_confirmed`.
- 5B2-3 boundary-confirmed static model: `PASS`.

## Stage 5B3 Stop

- 5B3 status: `FAIL`.
- Original moving-wall cases at `0.02`, `0.05`, and `0.10 m/s` failed to find consistent initial values.
- Three repair attempts were executed: lower speed, shorter simulation time, and smoothed wall velocity ramp. The repair cases still failed near `t?0.004 s`.
- No 5B3 `H(t)` or jet result is valid.
- Stop report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_moving_wall_ring_free_surface\reports\5B3_stop_report.md`.

## Known Limitations

- Stage 4 is single-phase and cannot output a true free-surface fountain height.
- Stage 5A and 5B2 are smoke tests, not validated fountain-height models.
- Stage 5B1 and any reduced forcing result must remain labelled approximate/reduced.
- Current ring velocity is an imposed parameter, not the result of density, gravity, buoyancy, or fluid-structure interaction.
- No Stage 6 parameter study is allowed until a future Stage 5E review explicitly writes `ALLOW_STAGE_6 = YES`.

<!-- STAGE_5B3_C2_ALTERNATIVE_WALL_STRATEGY_START -->

## Stage 5B3-C2 Alternative Wall Strategy

- Run time: `2026-06-18T16:47:47`.
- Scope: only `5B3-C2`; did not enter 5B4, 5C, 5D, 5E, stage 6, Jet1/Jet2 extraction, or parameter study.
- Starting clean baseline: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_clean_baseline_rebuild\models\ring_fountain_v5B2_clean_static_baseline_best.mph`.
- C2-0 feature probe: `PASS`.
- C2-1 Wetted Wall strategy: `FAIL`.
- C2-2 rebuilt selectable-wall model: `FAIL`.
- Best C2 model: ``.
- `ALLOW_RESUME_STAGE5 = NO`.
- Limit: current accepted C2 model, if any, remains a fixed-geometry reduced free-surface model and is not a validated physical Hmax model.
<!-- STAGE_5B3_C2_ALTERNATIVE_WALL_STRATEGY_END -->

<!-- 5B3_C3_BOUNDARY_SEMANTICS_AUDIT:START -->
## 5B3-C3 Boundary Semantics Audit

- Run ID: `20260618_171450`
- C3-2 minimal free-surface + solid-wall test: `FAIL`
- C3-3 single-phase ring moving-wall test: `SKIP`
- C3-4 ring + free-surface true moving-wall test: `SKIP`
- `ALLOW_RESUME_STAGE5 = NO`
- `spf.Inlet` / `spf.Outlet` / `spf.OpenBoundary` remain disallowed as solid moving-wall substitutes.
- No Jet1/Jet2 extraction, parameter sweep, or real Hmax output was performed in C3.
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C3_boundary_semantics_audit\reports\5B3_C3_boundary_semantics_audit_final_report.md`
<!-- 5B3_C3_BOUNDARY_SEMANTICS_AUDIT:END -->

<!-- 5B3_GUI_AUTO_SEED:START -->
## 5B3-GUI-AUTO-SEED

- Run ID: `20260618_174704`
- Scope: GUI/API seed model discovery only; not a Stage 5 resume.
- Final gate: `ALLOW_RESUME_STAGE5 = YES`.
- Stage 5 is still gated unless 5B3-GUI-AUTO-SEED passes.
- No real Hmax has been produced.
- The GUI/API seed model is only for discovering official COMSOL feature/interface/property names.
- Seed model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_GUI_auto_seed\models\ring_fountain_gui_auto_seed_minimal_twophase_wall.mph`
- Exported Java: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_GUI_auto_seed\exports\ring_fountain_gui_auto_seed_minimal_twophase_wall.java`
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_GUI_auto_seed\reports\5B3_GUI_auto_seed_final_report.md`
<!-- 5B3_GUI_AUTO_SEED:END -->

<!-- 5B3_C4_SEED_BASED_RING_SMOKE:START -->
## 5B3-C4 Seed-based Ring Smoke

- Run ID: `20260618_182058`.
- 5B3-GUI-AUTO-SEED: `PASS`.
- 5B3-C4 seed-based ring smoke: `PASS`.
- `ALLOW_5B4 = YES`; this run did not enter 5B4.
- `ALLOW_5C = NO` and `ALLOW_STAGE6 = NO`.
- Uses formal `TwoPhaseFlowLevelSet` + `WettedWall` with `TranslationalVelocityOption = Manual` and `utr = {0,-Vwall,0}`.
- Fixed-geometry smoke test only; the ring outline does not physically fall.
- No real Hmax has been produced.
- No Jet1/Jet2 extraction has been performed.
- No Stage 6 parameter sweep has been performed.
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C4_seed_based_ring_smoke\reports\5B3_C4_seed_based_ring_smoke_final_report.md`.
<!-- 5B3_C4_SEED_BASED_RING_SMOKE:END -->

<!-- 5B4_FALLING_OR_EQUIVALENT_RING:START -->
## 5B4 Falling-or-Equivalent Ring

- Run ID: `20260618_202100`.
- 5B3-C4: `PASS`.
- 5B4: `FAIL`.
- `ALLOW_5C = NO`; this run did not enter 5C.
- `ALLOW_STAGE6 = NO`; Stage 6 was not entered.
- Route: formal `TwoPhaseFlowLevelSet + WettedWall`.
- Ring motion surrogate: `utr = {0,-Vwall_eff(t),0}` on ring boundaries `[4,5,6,7]`.
- `Vwall_eff = Vtarget*(1-exp(-(t/t_ramp)^2))`.
- The model is fixed-geometry equivalent falling-ring, not a true freely falling ring with moving geometry.
- No real Hmax has been produced.
- No Jet1/Jet2 extraction has been performed.
- No Stage 6 parameter sweep has been performed.
- Static regression diagnostic `H(final)-H(0)`: `6.846528986234649e-05` m.
- Ladder cases: `[('D1', 'PASS'), ('D2', 'PASS'), ('D3', 'PASS'), ('D4', 'PASS')]`.
- Best model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\models\ring_fountain_v5B4_best.mph`.
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\reports\5B4_falling_or_equivalent_ring_final_report.md`.
<!-- 5B4_FALLING_OR_EQUIVALENT_RING:END -->

<!-- 5B4_R1_EXTENDED_STABILITY_REPAIR:START -->
## 5B4-R1 Extended Stability Repair

- Run ID: `20260618_225535`.
- 5B4 original: `FAIL`.
- 5B4-R1: `PASS`.
- `ALLOW_5C = YES`.
- `ALLOW_STAGE6 = NO`.
- Route retained: `TwoPhaseFlowLevelSet + WettedWall`.
- Ring motion remains `utr = {0,-Vwall_eff(t),0}` on boundaries `[4,5,6,7]`.
- This is still a fixed-geometry equivalent falling-ring model, not a true freely falling ring.
- No real Hmax has been produced.
- No Jet1/Jet2 extraction has been performed.
- No Stage 6 parameter sweep has been performed.
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_R1_extended_stability_repair\reports\5B4_R1_extended_stability_repair_final_report.md`.
<!-- 5B4_R1_EXTENDED_STABILITY_REPAIR:END -->

<!-- 5C_JET1_EXTRACTION:START -->
## 5C Jet1 Extraction

- Run ID: `20260618_233323`.
- 5B4-R1: `PASS`.
- 5C: `PASS`.
- Jet1 extraction completed; `Jet1_detected = NO`.
- No Jet2 extraction has been performed.
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- The source model remains a fixed-geometry WettedWall moving-wall equivalent falling-ring model.
- `ALLOW_5D = YES`.
- `ALLOW_STAGE6 = NO`.
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5C_jet1_extraction\reports\5C_jet1_extraction_final_report.md`.
<!-- 5C_JET1_EXTRACTION:END -->

<!-- 5D_JET2_DETECTION:START -->
## 5D Jet2 Detection

- Run ID: `20260619_110135`.
- 5C: `PASS`.
- 5D: `PASS`.
- Jet2 detection completed; `Jet2_detected = NO`.
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- Jet2 candidate, if present, is not a true final fountain height.
- The source model remains a fixed-geometry WettedWall moving-wall equivalent falling-ring model.
- `ALLOW_5E = YES`.
- `ALLOW_STAGE6 = NO`.
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5D_jet2_detection\reports\5D_jet2_detection_final_report.md`.
<!-- 5D_JET2_DETECTION:END -->

<!-- TRUE_MOVING_GEOMETRY_CAMPAIGN:START -->
## True Moving Geometry Campaign

- Run ID: `20260619_125524`.
- Fixed-geometry branch is frozen as toolchain validation / negative control.
- True-moving-geometry branch is now the active physical modelling branch.
- Minimal ALE single-physics: `PASS`.
- Minimal two-phase ALE seed: `PASS`.
- True moving ring smoke: `PASS`.
- Short stability extension: `PASS_MINIMAL`.
- No real Hmax has been produced.
- No Stage 6 parameter sweep has been performed.
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_campaign\reports\true_moving_geometry_campaign_final_report.md`.
<!-- TRUE_MOVING_GEOMETRY_CAMPAIGN:END -->

<!-- TRUE_GEOMETRY_R1_DIAGNOSTIC_REPAIR:START -->
## TRUE_GEOMETRY_R1_DIAGNOSTIC_REPAIR

- Run id: `20260619_165307`.
- Previous true-moving-geometry campaign `20260619_125524`: `PASS_MINIMAL`.
- 06_R1 diagnostic repair: `FAIL`.
- Interface diagnostic repaired: `YES`.
- Mesh quality diagnostic repaired: `YES`.
- Maximum verified physical displacement: `0.0` m.
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- Current outputs remain diagnostic and are not final ring-fountain physics conclusions.
<!-- TRUE_GEOMETRY_R1_DIAGNOSTIC_REPAIR:END -->

## TRUE_GEOMETRY_R2_INTERFACE_NOISE_ISOLATION

- Run id: `20260619_205807`
- 06_R1 diagnostic repair repaired NaN/interface count, but failed on pseudo_spike.
- 06_R2 isolates pseudo_spike source and attempts stabilization.
- R2 branch: `FAIL_PHASE2`
- Phase 1: `PASS`
- Phase 2: `FAIL`
- Phase 3: `SKIPPED`
- Phase 4: `SKIPPED`
- Phase 5: `SKIPPED`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- No true-geometry Jet1 detection has been performed.

## TRUE_GEOMETRY_R2_INTERFACE_NOISE_ISOLATION

- Run id: `20260619_210233`
- 06_R1 diagnostic repair repaired NaN/interface count, but failed on pseudo_spike.
- 06_R2 isolates pseudo_spike source and attempts stabilization.
- R2 branch: `FAIL_PHASE3`
- Phase 1: `PASS`
- Phase 2: `PASS`
- Phase 3: `FAIL`
- Phase 4: `SKIPPED`
- Phase 5: `SKIPPED`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- No true-geometry Jet1 detection has been performed.

## TRUE_GEOMETRY_R3_RING_CONTACTLINE_ISOLATION

- Run id: `20260619_214105`
- 06_R2 found that D0 static ring-present case is also weak_or_spiky.
- R2 does not support a velocity-amplified ALE-LS oscillation claim.
- 06_R3 isolates ring geometry / WettedWall / contact line / mesh / initialization causes.
- R3 branch: `FAIL_EXCEPTION`
- Principal spike region: `unknown`
- Ring-present static baseline: `unknown`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- No true-geometry Jet1 detection has been performed.

## TRUE_GEOMETRY_R3_RING_CONTACTLINE_ISOLATION

- Run id: `20260620_062253`
- 06_R2 found that D0 static ring-present case is also weak_or_spiky.
- R2 does not support a velocity-amplified ALE-LS oscillation claim.
- 06_R3 isolates ring geometry / WettedWall / contact line / mesh / initialization causes.
- R3 branch: `FAIL_NO_CREDIBLE_BASELINE`
- Principal spike region: `global`
- Ring-present static baseline: `NO`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- No true-geometry Jet1 detection has been performed.

<!-- TRUE_GEOMETRY_R3_PHASE3_DIAGNOSTIC_REPAIR:START -->
## TRUE_GEOMETRY_R3_PHASE3_DIAGNOSTIC_REPAIR

- Run id: `20260620_113028`
- Source state: true-moving-geometry R2 `FAIL_PHASE3`.
- Scope: R3 Phase-3 diagnostic repair only.
- R3 status: `FAIL`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_phase3_diagnostic_repair\reports\R3_final_report.md`
- Repair ladder table: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_phase3_diagnostic_repair\tables\R3_C_repair_ladder_summary.csv`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- No true-geometry Jet1 detection has been performed.
<!-- TRUE_GEOMETRY_R3_PHASE3_DIAGNOSTIC_REPAIR:END -->

<!-- TRUE_GEOMETRY_R3_AUDIT_COMPLETION_PACKAGE:START -->
## TRUE_GEOMETRY_R3_AUDIT_COMPLETION_PACKAGE

- Run id: `20260620_123221`
- Scope: audit-completion packaging for existing R3 outputs only.
- Audit package status: `PASS`
- Images indexed: `15`
- Table-like artifacts indexed: `12`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_audit_completion_package\reports\R3_audit_completion_final_report.md`
- Manifest: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_audit_completion_package\manifests\R3_artifact_manifest.csv`
- Image contact sheet: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_audit_completion_package\images\R3_image_contact_sheet.png`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- No true-geometry Jet1 detection has been performed.
<!-- TRUE_GEOMETRY_R3_AUDIT_COMPLETION_PACKAGE:END -->

<!-- TRUE_GEOMETRY_R3_POSTPROCESSING_MEMORY_REPAIR:START -->
## TRUE_GEOMETRY_R3_POSTPROCESSING_MEMORY_REPAIR

- Run id: `20260620_131742`
- Scope: postprocessing/regional-metrics repair only.
- T003 status: `PARTIAL`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED = NO`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED = NO`
- `CREDIBLE_STATIC_BASELINE_AFTER_POSTPROCESSING = NO`
- `CREDIBLE_MICRO_MOTION_BASELINE_AFTER_POSTPROCESSING = UNKNOWN`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_postprocessing_memory_repair\reports\T003_final_report.md`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- No true-geometry Jet1 detection has been performed.
<!-- TRUE_GEOMETRY_R3_POSTPROCESSING_MEMORY_REPAIR:END -->

<!-- TRUE_GEOMETRY_R3_RAW_ARRAY_EXTRACTION_RECOMPUTE:START -->
## TRUE_GEOMETRY_R3_RAW_ARRAY_EXTRACTION_RECOMPUTE

- Latest run id: `20260620_153612`
- Scope: raw-array extraction plus postprocessing recompute from existing saved models.
- T004 completed G2/G3; T005 completed W10/W0; T006 targets W2/W3/W4/W7/W8.
- T006 attempted remaining cases: `5`
- T006 status: `PASS`
- `RAW_ARRAY_EXTRACTION_COMPLETED_REMAINING_CASES = YES`
- `POSTPROCESSING_MEMORY_ERROR_RESOLVED_REMAINING_CASES = YES`
- `INTERFACE_QUALITY_EXTRACTION_REPAIRED_REMAINING_CASES = YES`
- `ALLOW_NEXT_DISPLACEMENT_LADDER = NO`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- T006 final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\reports\T006_final_report.md`
- T006 merged metrics: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_raw_array_extraction_recompute\tables\T006_merged_T004_T005_T006_metrics.csv`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- No true-geometry Jet1 detection has been performed.
<!-- TRUE_GEOMETRY_R3_RAW_ARRAY_EXTRACTION_RECOMPUTE:END -->

<!-- TRUE_GEOMETRY_R3_DIAGNOSTIC_DISPLACEMENT_REGRESSION:START -->
## TRUE_GEOMETRY_R3_DIAGNOSTIC_DISPLACEMENT_REGRESSION

- Run id: `20260620_163005`
- Scope: T009 SVG/CSV-backed visual audit completion for T008 figures; no COMSOL run.
- T009 status: `PASS`
- `T008_DISPLACEMENT_RESPONSE_FIGURE_AUDITED = YES`
- `T008_ERROR_SUMMARY_FIGURE_AUDITED = YES`
- `T008_INTERFACE_QUALITY_FIGURE_AUDITED = YES`
- `T008_NUMERIC_EVIDENCE_UNCHANGED = YES`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1_RECOMMENDATION = YES`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- T009 visual audit report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\reports\T009_t008_visual_audit_report.md`
- T009 figure manifest: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_diagnostic_displacement_regression\tables\T009_t008_figure_manifest.csv`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- No true-geometry Jet1 detection has been performed in T009.
<!-- TRUE_GEOMETRY_R3_DIAGNOSTIC_DISPLACEMENT_REGRESSION:END -->

<!-- TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC:START -->
## TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC

- Run id: `20260620_164644`
- Scope: T010 narrow true-geometry Jet1 diagnostic evidence only.
- T010 status: `PASS`
- `JET1_DIAGNOSTIC_SEMANTICS_RECOVERED = YES`
- `J0_STATUS = PASS`
- `J1_STATUS = PASS`
- `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`
- `JET1_PHYSICAL_CONCLUSION_MADE = NO`
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = YES`
- `ALLOW_STAGE6 = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_true_geometry_jet1_diagnostic\reports\T010_final_report.md`
- Figure manifest: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_true_geometry_jet1_diagnostic\tables\T010_figure_manifest.csv`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- No Jet1/Jet2 physical conclusion has been made.
<!-- TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC:END -->
