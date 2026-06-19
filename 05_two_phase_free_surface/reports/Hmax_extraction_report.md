# Stage 5C Hmax Extraction Report

Run time: 2026-06-17T21:05:35

5C review status: `PASS`

## Definition

- Initial free surface: `z0=0`.
- Interface threshold: `phils=0.5`.
- `H(t)=max_z(interface at time t)-z0`.
- `Hmax=max_t H(t)`.

## Result

- Model used: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\models\ring_fountain_v4_5B1_center_forcing.mph`.
- Model type: `approximate reduced center-forcing model`.
- Hmax: `0.0013953488372092156 m` = `1.3953488372092155 mm`.
- t_at_Hmax: `0.01 s`.
- Approximate: `True`.
- Quality status: `valid`.

## Outputs

- H_vs_t.csv: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\tables\H_vs_t.csv`
- Hmax_summary.csv: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\tables\Hmax_summary.csv`
- H_vs_t.png: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5C_Hmax\H_vs_t.png`
- Source frame index: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\tables\5B1_center_forcing_frame_index.csv`