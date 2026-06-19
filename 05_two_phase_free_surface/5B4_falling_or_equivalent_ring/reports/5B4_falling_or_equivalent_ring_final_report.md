# 5B4 Falling-or-Equivalent Ring Final Report

Run ID: `20260618_202100`

## Required Answers

1. C4 best imported successfully: `True`.
2. 5B4 base built successfully: `True`.
3. Still using `TwoPhaseFlowLevelSet`: `True`.
4. Still using `WettedWall`: `True`.
5. Still using `utr = {"0", "-Vwall_eff(t)", "0"}`: `True`.
6. Static regression passed: `True`.
7. D1 passed: `True`.
8. D2 passed: `True`.
9. D3 passed: `True`.
10. D4 passed: `True`.
11. E extended stability passed: `False`.
12. ALE probe executed: `False`.
13. ALE probe passed: `False`.
14. Generated `ring_fountain_v5B4_best.mph`: `True`.
15. Exported `ring_fountain_v5B4_best.java`: `True`.
16. Allow 5C: `NO`.
17. Allow Stage 6: `NO`.

## Gates

- `5B4 = FAIL`
- `ALLOW_5C = NO`
- `ALLOW_STAGE6 = NO`

## Scope Notes

- This is a fixed-geometry equivalent falling-ring model.
- `Manual utr` specifies wall velocity semantics; it does not move the ring geometry.
- No Inlet, Outlet, or OpenBoundary route was used to impersonate ring motion.
- Diagnostic interface height is only a smoke-test stability quantity, not real Hmax.
- This run did not enter 5C, 5D, 5E, Stage 6, Jet1/Jet2 extraction, or a parameter sweep.

## Key Paths

- Summary JSON: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\5B4_falling_or_equivalent_ring_summary.json`
- Best model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\models\ring_fountain_v5B4_best.mph`
- Best Java: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\exports\ring_fountain_v5B4_best.java`
- Reports: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\reports`
- Tables: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\tables`
- Images: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\images`
- Frames: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\frames`
- Logs: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\logs`
- Script archive: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\scripts\ring_fountain_stage5b4_falling_or_equivalent_ring.py`

Stop reason: `E extended stability failed; preserving D best only and not allowing 5C.`