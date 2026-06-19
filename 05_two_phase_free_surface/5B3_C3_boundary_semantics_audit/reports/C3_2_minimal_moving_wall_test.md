# C3-2 Minimal Moving Wall Test

Run time: 2026-06-18T17:15:17

C3-2 status: `FAIL`

## Scope

- Geometry: simple rectangular air-water domain, no ring geometry.
- Boundary semantics: only `spf.Wall` with prescribed wall velocity properties was allowed.
- Disallowed substitutes: `spf.Inlet`, `spf.Outlet`, `spf.OpenBoundary`.

## Review

- Any nonzero solid-wall moving case passed: `False`
- Primary stop reason: `Could not exclude moving boundaries from the default wall feature, and could not disable it. selection error=Exception:
	com.comsol.util.exceptions.FlException: Selection is not editable.
Messages:
	Selection is not editable.
; disable error=Exception:
	com.comsol.util.exceptions.FlException: Object cannot be disabled.
Messages:
	Object cannot be disabled.
	- Tag: wallbc1
`
- Case table: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C3_boundary_semantics_audit\tables\C3_2_minimal_moving_wall_cases.csv`
- Saved model info: `{"timestamp_model": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\5B3_C3_boundary_semantics_audit\\models\\ring_fountain_v5B3_C3_minimal_moving_wall_test_20260618_171450.mph", "model": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\5B3_C3_boundary_semantics_audit\\models\\ring_fountain_v5B3_C3_minimal_moving_wall_test.mph", "canonical_note": "canonical path already existed and was not overwritten"}`