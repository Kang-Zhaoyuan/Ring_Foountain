# Stage 5B3 Stop Report

Run time: 2026-06-17T22:08:25

## Stop Decision

- Stop stage: `5B3`.
- Stop reason: no moving-wall/free-surface case reached a successful solve and valid upstroke after the original velocity tests and three automatic repair attempts.
- Per `Traget.txt`, do not enter `5B4`, `5C`, `5D`, `5E`, or Stage 6.
- `ALLOW_STAGE_6 = NO`.

## Completed Gates Before Stop

- 5B2-0 route diagnosis: `PASS`.
- 5B2-1 static ring/free-surface smoke test: `PASS`.
- 5B2-2 boundary review: `PASS`; AUTO_BOUNDARY_REVIEW = `PASS`.
- 5B2-3 boundary-confirmed model: `PASS`.

## 5B3 Attempts

```csv
attempt_id,V_ring,t_end,ramp,solve_status,quality_status,Hmax_m,upstroke,model,error_log
V002_t012,0.02[m/s],0.12[s],False,fail,solve_failed,,,,D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_moving_wall_ring_free_surface\logs\V002_t012_error_20260617_220333.log
V005_t012,0.05[m/s],0.12[s],False,fail,solve_failed,,,,D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_moving_wall_ring_free_surface\logs\V005_t012_error_20260617_220333.log
V010_t012,0.10[m/s],0.12[s],False,fail,solve_failed,,,,D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_moving_wall_ring_free_surface\logs\V010_t012_error_20260617_220333.log
repair1_V001_t003_ramp,0.01[m/s],0.03[s],True,fail,solve_failed,,,,D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_moving_wall_ring_free_surface\logs\repair1_V001_t003_ramp_error_20260617_220333.log
repair2_V002_t003_ramp,0.02[m/s],0.03[s],True,fail,solve_failed,,,,D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_moving_wall_ring_free_surface\logs\repair2_V002_t003_ramp_error_20260617_220333.log
repair3_V001_t002_ramp,0.01[m/s],0.02[s],True,fail,solve_failed,,,,D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_moving_wall_ring_free_surface\logs\repair3_V001_t002_ramp_error_20260617_220333.log
```

## Automatic Repair Attempts Executed

- Original cases: `V_ring=0.02, 0.05, 0.10 m/s`, `t_end=0.12 s`.
- Repair 1: `V_ring=0.01 m/s`, `t_end=0.03 s`, smoothed moving-wall velocity ramp.
- Repair 2: `V_ring=0.02 m/s`, `t_end=0.03 s`, smoothed moving-wall velocity ramp.
- Repair 3: `V_ring=0.01 m/s`, `t_end=0.02 s`, smoothed moving-wall velocity ramp.
- Additional API repair: avoided editing non-editable COMSOL default `wallbc1`; used explicit ring-only `wall_ring_move` and documented that default `wallbc1` is COMSOL-generated and non-editable.

## Failure Evidence

- Original cases failed with `Failed to find consistent initial values`.
- Ramp repair cases failed near `t?0.004 s` with repeated error-test failures / possible singularity.
- No 5B3 H(t), image sequence, or model can be treated as valid because no moving-wall case solved successfully.

## Key Artifacts

- 5B2-1 model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\models\ring_fountain_v5B2_1_static_ring_free_surface.mph`
- 5B2-3 confirmed model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\models\ring_fountain_v5B2_3_static_ring_free_surface_boundary_confirmed.mph`
- 5B2 boundary review report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\reports\5B2_2_ring_boundary_review_package.md`
- 5B3 report: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_moving_wall_ring_free_surface\reports\5B3_moving_wall_ring_free_surface_report.md`
- 5B3 case CSV: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_moving_wall_ring_free_surface\tables\5B3_case_review.csv`

## Manual Review Recommendation

- Review the 5B2 boundary maps and candidate highlight images if the ring boundary interpretation needs visual confirmation.
- Review the 5B3 solver logs before deciding whether to switch to an official COMSOL two-phase interface, Phase Field route, or a different reduced forcing route in a future run.
