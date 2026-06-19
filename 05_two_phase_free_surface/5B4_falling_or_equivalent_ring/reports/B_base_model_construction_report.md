# B Base Model Construction Report

Run ID: `20260618_202100`

- Input C4 model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C4_seed_based_ring_smoke\models\ring_fountain_v5B3_C4_best.mph`
- Base model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\models\ring_fountain_v5B4_equivalent_falling_ring_base.mph`
- Timestamp base model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\models\ring_fountain_v5B4_equivalent_falling_ring_base_20260618_202100.mph`
- Formal route retained: `TwoPhaseFlowLevelSet + WettedWall`.
- Ring boundaries `[4,5,6,7]` are assigned to `ww1`.
- `TranslationalVelocityOption = Manual`.
- `utr = {"0", "-Vwall_eff", "0"}`.
- `Vwall_eff = Vtarget*(1-exp(-(t/t_ramp)^2))`.
- No Inlet, Outlet, or OpenBoundary route is used to impersonate ring motion.
- This remains a fixed-geometry equivalent falling-ring model, not a geometrically falling ring.
- Boundary map: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B4_falling_or_equivalent_ring\images\B_boundary_map.png`