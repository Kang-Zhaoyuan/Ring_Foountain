# 5B2 Clean Baseline And 5B3 Minimal Retry Final Report

Run time: `2026-06-18T15:56:28`

This run did not enter 5B4, 5C, 5D, 5E, or stage 6. Jet1/Jet2 were not extracted.

## Required Answers

1. RotatingFrameFD deleted/disabled: `not removed; already inactive`; manual route action: `kept_but_already_inactive; remove_failed=Exception:
	com.comsol.util.exceptions.FlException: Object cannot be removed.
Messages:
	Object cannot be removed.
	- Feature: Rotating Frame 1 (rtfr1)
; disable_failed=Exception:
	com.comsol.util.exceptions.FlException: Object cannot be disabled.
Messages:
	Object cannot be disabled.
	- Tag: rtfr1
`.
2. Gravity handling: `not used; grav1 already inactive`; policy: `not used in this short static smoke test; no hydrostatic-pressure initialization is available in this manual fallback, so gravity is removed to test numerical interface advection stability without extra forcing`.
3. Formal Two-Phase Flow coupling used: `False`; route used: `manual LaminarFlow + LevelSet fallback`.
4. Most stable static free-surface route: `Route_LS_manual_clean`.
5. Static baseline H(final)-H(0): `0.0` m.
6. Wall overlap excluded: `False`.
7. Most stable moving wall group: ``.
8. Best clean baseline model obtained: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_clean_baseline_rebuild\models\ring_fountain_v5B2_clean_static_baseline_best.mph`.
9. Minimal moving wall best model obtained: ``.
10. ALLOW_RESUME_STAGE5: `NO`.

## Stage Reports

- Stage B: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_clean_baseline_rebuild\reports\B_clean_static_baseline_report.md`
- Stage C: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_minimal_retry\reports\C_wall_nonoverlap_audit.md`
- Stage D: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_minimal_retry\reports\D_minimal_moving_wall_retry_report.md`
