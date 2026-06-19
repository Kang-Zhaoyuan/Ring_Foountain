# 5B3-R0 Wall Feature Audit

Run time: 2026-06-18T11:38:15
Source model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_static_ring_free_surface_smoke\models\ring_fountain_v5B2_3_static_ring_free_surface_boundary_confirmed.mph`

## Confirmed Ring Boundaries

- `sel_5B2_ring_wall_confirmed = [4, 5, 6, 7]`

## All Boundary IDs Detected

- `[1, 2, 3, 4, 5, 6, 7, 8]`

## spf Wall Features

| feature_tag | feature_type | selection_boundaries | BoundaryCondition | SlidingWall | TranslationalVelocityOption | utr | intersects [4,5,6,7] |
|---|---|---|---|---|---|---|---|
| `wallbc1` | `WallBC` | `[2, 3, 4, 5, 6, 7, 8]` | `NoSlip` | `0` | `AutomaticFromFrame` | `0` | `[4, 5, 6, 7]` |

## Full spf Feature Inventory

| feature_tag | feature_type | feature_label | selection_boundaries | BoundaryCondition | SlidingWall | TranslationalVelocityOption | utr |
|---|---|---|---|---|---|---|---|
| `fp1` | `FluidProperties` | `Fluid Properties 1` | `[]` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` |
| `init1` | `init` | `Initial Values 1` | `[]` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` |
| `axi1` | `AxialSymmetry` | `Axial Symmetry 1` | `[1]` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` |
| `wallbc1` | `WallBC` | `Wall 1` | `[2, 3, 4, 5, 6, 7, 8]` | `NoSlip` | `0` | `AutomaticFromFrame` | `0` |
| `grav1` | `Gravity` | `Gravity 1` | `[]` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` |
| `rtfr1` | `RotatingFrameFD` | `Rotating Frame 1` | `[]` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` |
| `dcont1` | `Continuity` | `Flow Continuity 1` | `[]` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` | `<unreadable: 'com.comsol.clientapi.physics.impl.PhysicsFeatureCl' object has no attribute 'get'>` |

## Conflict Review

- Wall features intersecting the confirmed ring boundaries: `['wallbc1']`.
- Any unreadable wall selection: `False`.
- Repair strategy for R2: if a default/global wall covers the ring, set that default wall to the non-moving remainder boundaries and create a separate `wall_ring_move` only on the moving test group.
- If the default wall selection cannot be changed, the script stops that case as `wall_overlap_unresolved` instead of treating it as a valid moving-wall model.