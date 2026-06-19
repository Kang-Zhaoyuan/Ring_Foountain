# Stage 5A Visual Review Package

Run time: 2026-06-17T21:04:53

5A-cleanup review status: `PASS`

## Meaning Of The Visuals

- Deep blue points in the `phils` plots represent water-rich samples (`phils` close to 1).
- Light blue/near-white points represent air-rich samples (`phils` close to 0).
- The black horizontal reference line is `z=0`, the intended initial still-water level.
- The black interface curve is extracted from `phils=0.5` and used as the free-surface threshold.
- The `phils_sample_scatter` figure is a sampled point cloud, not a mesh plot.

## Checks

- Water phase in `z<0`: `True`.
- Air phase in `z>0`: `True`.
- Interface short-time stability: `True`.
- 5A is suitable as a reduced-model starting point for 5B, but it is not itself a fountain model.

## Coupling Note

- Current 5A is a minimal manual coupling: standalone `LaminarFlow + LevelSet`.
- The combined `Laminar Two-Phase Flow, Level Set` multiphysics type could not be created through the tested COMSOL API type names in the previous probe.
- The manual coupling sets mixture properties using `phils`: `rho_air+(rho_w-rho_air)*phils` and `mu_air+(mu_w-mu_air)*phils`.

## Outputs

- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5A_review\5A_phils_cloud_with_colorbar.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5A_review\5A_phils_0p5_interface_line.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5A_review\5A_phils_sample_scatter.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5A_review\5A_density_rho.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5A_review\5A_viscosity_mu.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5A_review\5A_interface_overlay_frame_001.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5A_review\5A_interface_overlay_frame_002.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5A_review\5A_interface_overlay_frame_003.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5A_review\5A_interface_overlay_frame_004.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5A_review\5A_interface_overlay_frame_005.png`