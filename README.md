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
