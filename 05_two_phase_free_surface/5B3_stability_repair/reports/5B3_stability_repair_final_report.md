# 5B3 Stability Repair Final Report

Run status: `FAIL`

`ALLOW_RESUME_STAGE5 = NO`

This run stopped inside 5B3 and did not enter 5B4, 5C, 5D, 5E, or stage 6.

## Required Answers

- 5B3 stopped most likely because two issues are present: the original moving-wall setup risked wall-feature overlap, and the tightened static free-surface baseline is not stable enough for moving-wall testing.
- Wall feature overlap exists: `YES`. `spf.wallbc1` is `WallBC` on boundaries `[2,3,4,5,6,7,8]`, so it already covers the confirmed ring boundaries `[4,5,6,7]`. Creating a separate `wall_ring_move` on `[4,5,6,7]` without excluding those boundaries from `wallbc1` is a duplicate wall constraint risk.
- 5B2 static baseline stable enough: `NO` under the new 5B3-R1 criterion. `H(final)-H(0) = 1.064 mm`, exceeding `0.2 mm`.
- Most stable moving-wall boundary group: `NONE TESTED`; R2 was correctly blocked by R1 failure.
- Evidence of normal wall velocity failure: `NOT TESTED IN THIS RUN`; previous 5B3 logs showed solver singularity near `t = 0.004 s`, but R2 grouped tests were not allowed after R1 failed.
- Fillet improves stability: `NOT TESTED`; R3 was blocked by R1 failure.
- Alternative physics route stable: `NOT TESTED`; R4 was blocked by R1 failure/timeout.
- Repaired best model obtained: `NO`.
- Allow resume to 5B4: `NO`.

## Reports

- R0 wall audit: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_stability_repair\reports\5B3_R0_wall_feature_audit.md`
- R1 static baseline: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_stability_repair\reports\5B3_R1_static_baseline_report.md`
- R2 grouped moving wall: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_stability_repair\reports\5B3_R2_grouped_moving_wall_report.md`
- R3 fillet repair: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_stability_repair\reports\5B3_R3_fillet_repair_report.md`
- R4 physics route: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_stability_repair\reports\5B3_R4_physics_route_report.md`

## Next Manual/Repair Step

First stabilize the static free-surface baseline before attempting any moving-wall cases. Recommended next actions are: inspect whether gravity/rotating-frame features are unintentionally active in the 5B2-3 static baseline, try a controlled Phase Field smoke test, and only then re-run R2 with `wallbc1` explicitly excluding the moving ring boundaries.
