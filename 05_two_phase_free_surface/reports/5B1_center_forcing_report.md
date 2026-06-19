# Stage 5B1 Center Forcing Report

Run time: 2026-06-17T21:05:34

B1 review status: `PASS`

## Model Type

- Reduced center-forcing free-surface model.
- This is not a complete true falling-ring model.
- Forcing is local and controlled, intended to validate interface tracking and H(t) extraction.

## Forcing Method

- `{"mode": "kinematic_level_set_velocity", "forcing_type": "localized upward Level Set advection velocity; reduced kinematic forcing", "w_force_kin": "A_force*exp(-(r/r_force)^2)*flc2hs(z-z_force,sigma_z)*flc2hs(t_force-t,t_force/10)", "level_set_velocity": "ls/lsm1 u_src=userdef, u=[0,0,A_force*exp(-(r/r_force)^2)*flc2hs(z-z_force,sigma_z)*flc2hs(t_force-t,t_force/10)]", "note": "Used after the hydrodynamic VolumeForce attempt failed to find consistent initial values."}`
- Velocity plots use the imposed kinematic Level Set velocity field `w_force_kin` at inner solution 3, not solved `spf.w`.

## Review

- Interface identifiable: `True`.
- Observable upstroke: `True`.
- Did not touch domain top: `True`.
- Preliminary H peak: `0.0013953488372092156 m`.

## Outputs

- Model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\models\ring_fountain_v4_5B1_center_forcing.mph`
- Timestamp model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\models\ring_fountain_v4_5B1_center_forcing_20260617_210438.mph`
- H(t) CSV: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\tables\5B1_center_forcing_H_vs_t.csv`
- H(t) plot: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5B1_center_forcing\5B1_center_forcing_H_vs_t.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5B1_center_forcing\5B1_phils_final.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5B1_center_forcing\5B1_velocity_magnitude.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5B1_center_forcing\5B1_axial_velocity_w.png`
- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5B1_center_forcing\5B1_local_velocity_vectors.png`