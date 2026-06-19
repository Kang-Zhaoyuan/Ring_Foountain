# C2-1 Wetted Wall Alternative Strategy Report

Run time: 2026-06-18T16:46:26
C2-1 review status: `FAIL`
C2_WETTED_WALL_STRATEGY = `FAIL`
ALLOW_RESUME_STAGE5 = `NO`

## Method

- The script did not delete `spf.wallbc1`.
- Wetted Wall / Interior Wetted Wall candidates were attempted on `[4,5,6,7]` and `[4,7]`.
- Moving tests were only considered after vertical static cases were stable.

## Results

- CSV: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C2_alternative_wall_strategy\tables\C2_1_wetted_wall_cases.csv`
- Best case: ``

| case_id | solve_status | boundary_set | V_test | t_end | delta_H | Hmax | wall_overlap_status | failure_message |
|---|---|---|---:|---|---:|---:|---|---|
| `C2_1_not_run_features_unavailable` | `FAIL` | `[4, 5, 6, 7]` | `0` | `` | `None` | `None` | `not_tested` | `C2-0 did not find creatable Wetted Wall or Interior Wetted Wall feature types.` |