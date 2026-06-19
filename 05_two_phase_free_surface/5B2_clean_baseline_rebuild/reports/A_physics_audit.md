# Stage A Physics Audit

Run time: `2026-06-18T12:34:27`
Source model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\models\ring_fountain_v5B2_3_static_ring_free_surface_boundary_confirmed.mph`

This audit is read-only. It did not solve, save, or modify the source model.

## Required Findings

- `RotatingFrameFD / rtfr1` present: `True`; tags: `['rtfr1']`.
- Default judgement: unless a later report documents a specific physical reason, RotatingFrameFD should be deleted or disabled before the clean static baseline because this stage is a static free-surface baseline, not a rotating-frame problem.
- Gravity present: `True`; tags: `['grav1']`.
- Wall features: `['wallbc1']`.
- Wall features intersecting confirmed ring boundaries `[4,5,6,7]`: `[{'feature_tag': 'wallbc1', 'intersects_ring': [4, 5, 6, 7], 'selection_boundaries': [2, 3, 4, 5, 6, 7, 8]}]`.
- Level Set-like physics/features detected: `['lsm1', 'init1', 'initfluid2', 'axi1', 'nf1', 'dcont1']`.
- Multiphysics tags detected: `[]`.
- Formal Two-Phase Flow coupling detected by multiphysics inventory: `False`.
- rho/mu definitions detected in variable inventory: `False`.
- surface-tension-like definition detected: `True`.

## Interpretation For Stage B

- `RotatingFrameFD` exists in the current input model. With no explicit rotating-frame physics requirement in this static baseline task, it is treated as an unintended feature to remove or disable in Stage B.
- No formal two-phase multiphysics coupling was detected by the Java multiphysics inventory. Current evidence points to a manual Laminar Flow + Level Set setup or a coupling represented outside the multiphysics node.
- `spf` wall selection currently overlaps the confirmed ring boundaries. Any later moving-wall retry must first create non-overlapping wall selections.

## Complete Physics Feature Audit

| physics_tag | physics_type | physics_label | feature_tag | feature_type | feature_label | selection_boundaries | intersects_ring | active_or_solved | key_properties |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `spf` | `LaminarFlow` | `Laminar Flow` | `fp1` | `FluidProperties` | `Fluid Properties 1` | `[]` | `[]` | `True` | `{"rho": "rho_air+(rho_w-rho_air)*phils", "mu": "mu_air+(mu_w-mu_air)*phils", "rho_mat": "userdef", "mu_mat": "userdef", "mu0": "1e-3[Pa*s]", "mu0_mat": "from_mat", "mu0c": "1e-3[Pa*s]", "mu0c_mat": "from_mat", "mu0cw": "1e-3[Pa*s]", "mu0cw_mat": "from_mat", "mu0cy": "1e-3[Pa*s]", "mu0cy_mat": "from_mat", "mu0e": "1e-3[Pa*s]", "mu0e_mat": "from_mat", "mu_DK": "1e-3[Pa*s]", "mu_DK_mat": "from_mat", "mu_inf": "0[Pa*s]", "mu_inf_mat": "from_mat", "mu_infc": "0[Pa*s]", "mu_infc_mat": "from_mat", "mu_infcy": "0[Pa*s]", "mu_infcy_mat": "from_mat", "mu_infs": "0[Pa*s]", "mu_infs_mat": "from_mat", "mu_init_app": "spf.mu0e", "mu_p": "1e-3[Pa*s]", "mu_p_mat": "from_mat", "mu_pc": "1e-3[Pa*s]", "mu_pc_mat": "from_mat"}` |
| `spf` | `LaminarFlow` | `Laminar Flow` | `init1` | `init` | `Initial Values 1` | `[]` | `[]` | `True` | `{}` |
| `spf` | `LaminarFlow` | `Laminar Flow` | `axi1` | `AxialSymmetry` | `Axial Symmetry 1` | `[1]` | `[]` | `True` | `{}` |
| `spf` | `LaminarFlow` | `Laminar Flow` | `wallbc1` | `WallBC` | `Wall 1` | `[2, 3, 4, 5, 6, 7, 8]` | `[4, 5, 6, 7]` | `True` | `{"BoundaryCondition": "NoSlip", "SlidingWall": "0", "TranslationalVelocityOption": "AutomaticFromFrame", "utr": "0", "ApplyWallRoughness": "0", "epsilonr": "80", "mueo": "7e-8[m^2/(V*s)]", "sigmat": "0.75"}` |
| `spf` | `LaminarFlow` | `Laminar Flow` | `grav1` | `Gravity` | `Gravity 1` | `[]` | `[]` | `False` | `{"g": "0", "projectGravity": "1"}` |
| `spf` | `LaminarFlow` | `Laminar Flow` | `rtfr1` | `RotatingFrameFD` | `Rotating Frame 1` | `[]` | `[]` | `False` | `{"AxisOfRotation": "zAxis", "RotationalDirection": "CounterClockwise", "RotationalFrequency": "AngularVelocity"}` |
| `spf` | `LaminarFlow` | `Laminar Flow` | `dcont1` | `Continuity` | `Flow Continuity 1` | `[]` | `[]` | `False` | `{}` |
| `ls` | `LevelSet` | `Level Set` | `lsm1` | `LevelSetModel` | `Level Set Model 1` | `[]` | `[]` | `True` | `{"epsilon_ls": "ls.ep_default", "gamma": "1"}` |
| `ls` | `LevelSet` | `Level Set` | `init1` | `init` | `Initial Values 1` | `[]` | `[]` | `True` | `{}` |
| `ls` | `LevelSet` | `Level Set` | `initfluid2` | `initFluid2` | `Initial Values, Fluid 2` | `[]` | `[]` | `True` | `{}` |
| `ls` | `LevelSet` | `Level Set` | `axi1` | `AxialSymmetry` | `Axial Symmetry 1` | `[1]` | `[]` | `True` | `{}` |
| `ls` | `LevelSet` | `Level Set` | `nf1` | `NoFlow` | `No Flow 1` | `[2, 3, 4, 5, 6, 7, 8]` | `[4, 5, 6, 7]` | `True` | `{}` |
| `ls` | `LevelSet` | `Level Set` | `dcont1` | `Continuity` | `Continuity 1` | `[]` | `[]` | `False` | `{}` |

## Multiphysics Inventory

- No multiphysics nodes were readable under `comp1.multiphysics()`.

## Variable Inventory

- No component variable nodes were readable under `comp1.variable()`.