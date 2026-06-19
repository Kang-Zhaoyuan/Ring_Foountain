# Stage B Clean Static Baseline Report

Run time: `2026-06-18T15:56:17`
Source model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\models\ring_fountain_v5B2_3_static_ring_free_surface_boundary_confirmed.mph`
Review status: `PASS`
`ALLOW_5B3_RETRY = YES`

## Route Results

| route | status | solve_status | delta_H_m | interface_quality | notes |
|---|---|---|---:|---|---|
| `Route_LS_official` | `NOT_AVAILABLE` | `not_run` | `` | `` | `No tested official physics type could be created through the COMSOL Java API.` |
| `Route_PF_official` | `NOT_AVAILABLE` | `not_run` | `` | `` | `No tested official physics type could be created through the COMSOL Java API.` |
| `Route_LS_manual_clean` | `PASS` | `success` | `0.0` | `clear/continuous` | `No moving wall and no additional forcing were applied.` |

## Static Baseline Decision

- Best route: `Route_LS_manual_clean`.
- H(final)-H(0): `0.0` m.
- Best clean baseline model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_clean_baseline_rebuild\models\ring_fountain_v5B2_clean_static_baseline_best.mph`.
- Moving wall: not applied.
- Extra forcing: not applied.

## Gravity And Cleanup

- `rtfr1 / RotatingFrameFD` is not used by the accepted manual clean fallback. COMSOL did not allow removing or disabling the built-in node, but the audit/action log shows it is already inactive.
- The manual fallback does not use gravity in this short smoke test. COMSOL did not allow removing or disabling the built-in gravity node either, but the audit/action log shows it is already inactive; no hydrostatic-pressure initialization is present in the manual coupling, so this gate isolates static interface advection stability without additional forcing.
- The formal Level Set / Phase Field routes are recorded as unavailable or not safely convertible when COMSOL API creation/conversion is not available.

## Outputs

- Route comparison: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_clean_baseline_rebuild\tables\clean_baseline_route_comparison.csv`
- H(t) CSV: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\tables\5B2_clean_manual_static_H_vs_t.csv`
- H(t) plot: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_clean_baseline_rebuild\images\Route_LS_manual_clean\5B2_clean_manual_static_H_vs_t.png`
- Interface frames index: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\tables\5B2_clean_manual_static_frame_index.csv`
