# Changelog

## 2026-06-17 - Stages 0-3

- V0 audit, checked copy, parameter sweep, calibrated sweep continuation, and Stage 3 relative-flow model were generated.
- Stage 3 relative-flow model reached `PASS`.

## 2026-06-17 - Stage 4

- Manual ring-boundary review: `PASS`.
- Confirmed ring boundaries: `[4, 5, 6, 7]`.
- Named selections were written into `ring_fountain_v3_boundary_named.mph`.
- Stage 4.2A relative-velocity check: `PASS`.
- Formal fixed-geometry moving-wall ring model: `PASS`.

## 2026-06-17 - Stage 5A and Prior Reduced Demo

- Static air-water interface smoke test: `PASS`.
- 5B1 reduced center-forcing model: `PASS`, approximate only.
- Earlier B1-based Hmax extraction remains a reduced pipeline demo, not a validated ring-fountain height.

## 2026-06-17T22:08:25 - Stage 5B2 to 5B3 Continuation

- 5B2-0 route diagnosis: `PASS`.
- 5B2-1 static ring/free-surface smoke test: `PASS`.
- 5B2-2 boundary review: `PASS`; AUTO_BOUNDARY_REVIEW = `PASS`.
- 5B2-3 boundary-confirmed static model: `PASS`.
- 5B3 fixed geometry + moving wall + free surface: `FAIL`.
- 5B4, 5C, 5D, 5E, and Stage 6 were not run because 5B3 did not pass.
- `ALLOW_STAGE_6 = NO`.
- Stop report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_moving_wall_ring_free_surface\reports\5B3_stop_report.md`.

<!-- STAGE_5B3_C2_ALTERNATIVE_WALL_STRATEGY_CHANGELOG_START -->

## 2026-06-18T16:47:47 - Stage 5B3-C2 Alternative Wall Strategy

- Added C2 feature/property probing for Wetted Wall, Interior Wetted Wall, moving wall properties, Level Set no-flow candidates, and tested two-phase coupling type names.
- Tested alternative wall strategy without deleting `spf.wallbc1`.
- If needed, rebuilt a reduced selectable-wall model from scratch.
- Final gate: `ALLOW_RESUME_STAGE5 = NO`.
<!-- STAGE_5B3_C2_ALTERNATIVE_WALL_STRATEGY_CHANGELOG_END -->

<!-- 5B3_C3_BOUNDARY_SEMANTICS_AUDIT:START -->
## 5B3-C3 Boundary Semantics Audit

- Run ID: `20260618_171450`
- C3 final gate: `ALLOW_RESUME_STAGE5 = NO`
- C3-2/C3-3/C3-4: `FAIL` / `SKIP` / `SKIP`
- Inlet-equivalent motion was explicitly rejected as invalid for solid moving-wall semantics.
- Report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C3_boundary_semantics_audit\reports\5B3_C3_boundary_semantics_audit_final_report.md`
<!-- 5B3_C3_BOUNDARY_SEMANTICS_AUDIT:END -->

<!-- 5B3_GUI_AUTO_SEED:START -->
## 5B3-GUI-AUTO-SEED

- Run ID: `20260618_174704`
- Final gate: `ALLOW_RESUME_STAGE5 = YES`.
- Created a minimal formal `TwoPhaseFlowLevelSet` + `WettedWall` seed model.
- Solved `Vwall = 0` and `Vwall = 1e-4[m/s]` seed cases.
- Exported Java and parsed official API names.
- No Jet1/Jet2 extraction, parameter sweep, Stage 5 continuation, or real Hmax output was performed.
<!-- 5B3_GUI_AUTO_SEED:END -->

<!-- 5B3_C4_SEED_BASED_RING_SMOKE:START -->
## 5B3-C4 Seed-based Ring Smoke

- Run ID: `20260618_182058`.
- Status: `PASS`.
- Gate: `ALLOW_5B4 = YES`, `ALLOW_5C = NO`, `ALLOW_STAGE6 = NO`.
- Imported GUI-auto-seed API names and rebuilt a minimal ring-hole two-phase WettedWall smoke model.
- No 5B4/5C/5D/5E/Stage 6, Jet1/Jet2 extraction, parameter sweep, or real Hmax output was performed.
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C4_seed_based_ring_smoke\reports\5B3_C4_seed_based_ring_smoke_final_report.md`.
<!-- 5B3_C4_SEED_BASED_RING_SMOKE:END -->

<!-- 5B4_FALLING_OR_EQUIVALENT_RING:START -->
## 5B4 Falling-or-Equivalent Ring

- Run ID: `20260618_202100`.
- Status: `FAIL`.
- Gate: `ALLOW_5C = NO`, `ALLOW_STAGE6 = NO`.
- Loaded C4 best model and converted the ring wall velocity to a smooth time-dependent equivalent falling speed.
- Preserved `TwoPhaseFlowLevelSet + WettedWall`; no Inlet/Outlet/OpenBoundary surrogate route was used.
- No 5C/5D/5E/Stage 6, Jet1/Jet2 extraction, parameter sweep, or real Hmax output was performed.
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\reports\5B4_falling_or_equivalent_ring_final_report.md`.
<!-- 5B4_FALLING_OR_EQUIVALENT_RING:END -->

<!-- 5B4_R1_EXTENDED_STABILITY_REPAIR:START -->
## 5B4-R1 Extended Stability Repair

- Run ID: `20260618_225535`.
- Status: `PASS`.
- Gate: `ALLOW_5C = YES`, `ALLOW_STAGE6 = NO`.
- Recomputed robust interface diagnostics for the original 5B4 E failure.
- Repeated the D4 extended case with unchanged physics and improved diagnostics.
- Did not enter 5C/5D/5E/Stage 6; no Jet1/Jet2 extraction, parameter sweep, or real Hmax was produced.
- Final report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_R1_extended_stability_repair\reports\5B4_R1_extended_stability_repair_final_report.md`.
<!-- 5B4_R1_EXTENDED_STABILITY_REPAIR:END -->

<!-- 5C_JET1_EXTRACTION:START -->
## 5C Jet1 Extraction

- Run ID: `20260618_233323`.
- Status: `PASS`.
- Jet1 detected: `NO`.
- Gate: `ALLOW_5D = YES`, `ALLOW_STAGE6 = NO`.
- Extracted phils=0.5 interface sequence with raw/robust diagnostics and velocity-field support frames.
- Did not enter 5D/5E/Stage 6; no Jet2 extraction, parameter sweep, or real Hmax output was performed.
<!-- 5C_JET1_EXTRACTION:END -->

<!-- 5D_JET2_DETECTION:START -->
## 5D Jet2 Detection

- Run ID: `20260619_110135`.
- Status: `PASS`.
- Jet2 detected: `NO`.
- Gate: `ALLOW_5E = YES`, `ALLOW_STAGE6 = NO`.
- Performed existing-window Jet2 screening and optional extended-window detection when needed.
- Did not enter 5E or Stage 6; no parameter sweep or real Hmax output was performed.
<!-- 5D_JET2_DETECTION:END -->

<!-- TRUE_MOVING_GEOMETRY_CAMPAIGN:START -->
## True Moving Geometry Campaign

- Run ID: `20260619_124109`.
- Accepted teacher critique of the fixed-geometry branch.
- Froze fixed-geometry branch as negative control.
- Discovered Moving Mesh/ALE API and attempted minimal ALE seeds.
- No Stage 6 parameter sweep or real Hmax output was performed.
<!-- TRUE_MOVING_GEOMETRY_CAMPAIGN:END -->
