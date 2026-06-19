# C Ring Twophase Geometry and Boundary Report

Model: `ring_fountain_v5B3_C4_ring_twophase_smoke`

## Geometry

- 2D axisymmetric fixed geometry.
- Fluid domain = tank rectangle minus ring rectangle.
- Ring rectangle: `Ri <= r <= Ro`, `z_ring-h_ring/2 <= z <= z_ring+h_ring/2`.

## Boundary Selections

- `axis`: `[1]`
- `top_open`: `[3]`
- `bottom_wall`: `[2]`
- `outer_wall`: `[8]`
- `ring_inner`: `[4]`
- `ring_outer`: `[7]`
- `ring_top`: `[6]`
- `ring_bottom`: `[5]`
- `ring_wettedwall_confirmed`: `[4, 5, 6, 7]`

## WettedWall

- WettedWall boundaries: `[4, 5, 6, 7]`
- `TranslationalVelocityOption = Manual`
- `utr = {"0", "-Vwall", "0"}`

- Base model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C4_seed_based_ring_smoke\models\ring_fountain_v5B3_C4_ring_twophase_smoke_base.mph`
- Timestamp model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C4_seed_based_ring_smoke\models\ring_fountain_v5B3_C4_ring_twophase_smoke_base_20260618_182058.mph`
- Boundary map: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C4_seed_based_ring_smoke\images\C_boundary_map.png`