# Stage 5B2-0 Route and Failure Diagnosis

Run time: 2026-06-17T22:03:37

## Previous B2 Failure

- Symptom: `Unsupported geometry - Geometry: geom1`.
- Current probe result: the rectangle tank minus ring-hole geometry can `geom.run()` and mesh successfully.
- The same error is reproduced only when the old boundary metric code calls `IntLine.selection().geom("geom1", 1)`.
- Diagnosis: this is not a physical two-phase failure and not a solver failure. It is a COMSOL API boundary-metric/selection call failure in the old script.

## Failure Type

- Geometry construction failure: `NO` for the probed geometry.
- Boolean difference failure: `NO` for the probed geometry.
- Boundary identification script failure: `YES`.
- COMSOL API call style failure: `YES`.
- Physics interface unsupported: `NOT PROVEN`.
- Solver failure: `NO` at this diagnostic stage.

## Documentation / Search Notes

- Local COMSOL 6.4 help contains `The Two-Phase Flow, Level Set and Phase Field Interfaces` under `com.comsol.help.cfd/cfd_ug_fluidflow_multi.09.007.html`.
- Local COMSOL 6.4 help describes `Laminar Two-Phase Flow, Level Set` and `Laminar Two-Phase Flow, Phase Field` branches.
- Local COMSOL 6.4 help also lists `Laminar, Two-Phase Flow, Moving Mesh` in the two-phase moving mesh defaults table.
- Literature search context: Worthington jets are associated with impact/cavity dynamics; later reports must not claim Jet1/Jet2 unless H(t) and free-surface frames support it.
- Search conclusions guide route choice only; they do not replace model verification.

## Route For This Run

- Preferred route: official `Laminar Two-Phase Flow, Level Set` if callable through the API.
- Fallback used here when the combined physics API type is unavailable: manual `LaminarFlow + LevelSet` with mixture properties.
- Boundary identification route: coordinate-based COMSOL `Box` selections, not old `IntLine` boundary metrics.
- Moving-wall route, if reached: a separate ring-only wall feature restricted to `sel_5B2_ring_wall_confirmed`.

## PASS Review

- Previous failure reason clarified: `YES`.
- Physical failure clarified: `YES, not a physical failure`.
- Old script reuse: `NO`; old metric path is avoided.
- Rebuild route clarified: `YES`.
- README.md and CHANGELOG.md are updated by the final script cleanup.

## Previous Report Excerpt

```text
# Stage 5B2 Fixed Ring Moving Wall Report

Run time: 2026-06-17T21:05:35

B2 review status: `FAIL`

## Stop Reason

- `Exception:

	com.comsol.util.exceptions.FlException: Unsupported geometry.

Messages:

	Unsupported geometry.

	- Geometry: geom1

`

## Consequence

- B2 was not used for Hmax extraction.
- Because B1 passed, Stage 5C may proceed using the B1 approximate reduced center-forcing model.

## Error Log

- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\logs\5B2_error_20260617_210438.log`
```