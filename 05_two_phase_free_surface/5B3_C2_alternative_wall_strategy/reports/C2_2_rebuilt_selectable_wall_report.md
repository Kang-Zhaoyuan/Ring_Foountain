# C2-2 Rebuilt Selectable-Wall Reduced Model Report

Run time: 2026-06-18T16:47:47
C2-2 review status: `FAIL`
C2_REBUILT_SELECTABLE_MODEL = `FAIL`
ALLOW_RESUME_STAGE5 = `NO`

## Model Type And Limits

- Rebuilt reduced model: manual `LaminarFlow + LevelSet` fallback.
- Gravity is not enabled, matching the previous clean static baseline smoke-test policy.
- Geometry is fixed; moving wall changes boundary velocity only and does not translate the ring geometry.
- This is not a final physical Hmax model.

## Named Selections

- `{"sel_axis": [1], "sel_outer_wall": [8], "sel_top_boundary": [3], "sel_bottom_boundary": [2], "sel_ring_wall_inner": [4], "sel_ring_wall_outer": [7], "sel_ring_wall_top": [6], "sel_ring_wall_bottom": [5], "sel_ring_wall_all": [4, 5, 6, 7], "sel_ring_wall_vertical": [4, 7]}`

## Cases

- CSV: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C2_alternative_wall_strategy\tables\C2_2_rebuilt_cases.csv`

| case_id | solve_status | boundary_set | V_test | t_end | delta_H | Hmax | interface_quality | wall_overlap_status |
|---|---|---|---:|---|---:|---:|---|---|
| `C2_2_static_baseline` | `PASS` | `all walls static` | `0` | `0.02[s]` | `0.0` | `0.00016578850821326205` | `clear/continuous` | `not_applicable_static` |
| `C2_2_failure` | `FAIL` | `` | `` | `` | `nan` | `nan` | `` | `UNKNOWN_OR_FAIL` |