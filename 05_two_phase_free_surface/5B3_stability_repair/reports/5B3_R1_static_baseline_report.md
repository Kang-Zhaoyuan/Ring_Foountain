# 5B3-R1 Static Baseline Report

Review status: `FAIL`

Source model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\models\ring_fountain_v5B2_3_static_ring_free_surface_boundary_confirmed.mph`

## Criteria

- `|H(final)-H(0)| < 0.2 mm`
- Main free surface continuous
- No obvious isolated spike
- Interface does not reach the top boundary

## Baseline Result

- H(0): `0.00016578850821326202 m` = `0.166 mm`
- H(final): `0.001230258302551709 m` = `1.230 mm`
- H(final)-H(0): `0.001064469794338447 m` = `1.064 mm`
- Main interface: `continuous`
- Isolated spike: `False`
- Touches top: `False`

The tightened 5B3-R1 gate fails because the static free-surface baseline drifts by about `1.064 mm`, which is greater than the allowed `0.2 mm`.

## Automatic Repair Attempts

- Attempt 1: decreased output/time spacing to `0.0002 s`; result reproduced the same drift and failed the `0.2 mm` criterion.
- Attempt 2: reduced Level Set interface thickness to `eps_ls = 1 mm`; COMSOL/mph run did not finish within the 30 minute automation timeout.
- Attempt 3: planned `eps_ls = 0.5 mm` plus mesh refinement; not executed because Attempt 2 timed out and the running process had to be stopped.
- Phase Field smoke test: not executed because R1 repair already exceeded the safe automation time budget for this turn.

## Outputs

- H(t): `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_stability_repair\tables\static_baseline_H_vs_t.csv`
- Free-surface frames: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_stability_repair\images\R1_static_baseline\frames`
- H(t) plot: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_stability_repair\images\R1_static_baseline\5B3_R1_static_baseline_H_vs_t.png`

## Stop Decision

`5B2_baseline_not_stable`

R2 grouped moving-wall tests were not run because R1 did not PASS.
