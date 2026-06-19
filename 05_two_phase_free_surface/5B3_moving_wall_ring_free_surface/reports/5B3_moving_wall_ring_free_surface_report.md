# Stage 5B3 Moving Wall Ring Free-Surface Report

Review status: `FAIL`

## Boundary and Wall Method

- Confirmed 5B2 ring boundaries: `[4, 5, 6, 7]`.
- Moving wall acts only on `sel_5B2_ring_wall_confirmed`.
- COMSOL wall feature/property: `spf/wall_ring_move`, `SlidingWall=1`, `TranslationalVelocityOption=Manual`, `utr=[0,0,-V_ring]`.
- This is fixed geometry + moving wall velocity; the ring geometry does not translate.

## Case Results

- V002_t012: solve=`fail`, quality=`solve_failed`, V=`0.02[m/s]`, ramp=`False`.
- V005_t012: solve=`fail`, quality=`solve_failed`, V=`0.05[m/s]`, ramp=`False`.
- V010_t012: solve=`fail`, quality=`solve_failed`, V=`0.10[m/s]`, ramp=`False`.
- repair1_V001_t003_ramp: solve=`fail`, quality=`solve_failed`, V=`0.01[m/s]`, ramp=`True`.
- repair2_V002_t003_ramp: solve=`fail`, quality=`solve_failed`, V=`0.02[m/s]`, ramp=`True`.
- repair3_V001_t002_ramp: solve=`fail`, quality=`solve_failed`, V=`0.01[m/s]`, ramp=`True`.

## PASS Review

- At least one valid upstroke case: `False`.
- No result is described as true falling geometry.

## Outputs

- Case CSV: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_moving_wall_ring_free_surface\tables\5B3_case_review.csv`
- Canonical model if PASS: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_moving_wall_ring_free_surface\models\ring_fountain_v5B3_moving_wall_ring_free_surface.mph`