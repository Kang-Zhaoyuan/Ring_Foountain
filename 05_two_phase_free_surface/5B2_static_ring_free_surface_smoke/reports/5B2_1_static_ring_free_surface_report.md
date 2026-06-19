# Stage 5B2-1 Static Ring Free-Surface Smoke Test

Run time: 2026-06-17T22:04:09

Review status: `PASS`

## Model

- Geometry: axisymmetric tank with boolean-subtracted rectangular ring hole.
- Physics route: manual fallback `LaminarFlow + LevelSet` with mixture properties.
- Moving wall: not applied in 5B2-1.

## Automatic Repair Log

- 5B2-1_attempt_1: Duplicate parameter/variable name: g_const -> Removed explicit g_const parameter from the rebuilt 5B2 static smoke model; gravity is not used in this static smoke equation set. -> repair_applied_before_current_run.

## Boundary IDs From New Geometry

- Candidate IDs: `[4, 5, 6, 7]`.
- Total theoretical ring perimeter: `0.028` m.

## Stability

- H(0): `0.00016578850821326202` m.
- H(final): `0.001230258302551709` m.
- Stable short-time interface: `True`.

## Outputs

- Model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\models\ring_fountain_v5B2_1_static_ring_free_surface.mph`
- Timestamp model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\models\ring_fountain_v5B2_1_static_ring_free_surface_20260617_220333.mph`
- Boundary table: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\tables\5B2_1_boundary_table.csv`
- H(t): `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\tables\5B2_1_static_ring_H_vs_t.csv`
- Image: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\images\5B2_1_phils_cloud_with_colorbar.png`
- Image: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\images\5B2_1_phils_interface_line.png`
- Image: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\images\5B2_1_density_rho.png`
- Image: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\images\5B2_1_viscosity_mu.png`
- Boundary number map: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\images\5B2_1_boundary_number_map.png`
- Ring local map: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\images\5B2_1_ring_boundary_local_map.png`