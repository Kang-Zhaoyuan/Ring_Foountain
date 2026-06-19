# Stage 4 Moving Ring Model Report

Run time: 2026-06-17T20:01:15

Stage 4.2 review status: `PASS`

## Boundary And Wall Setting

- Manually confirmed ring boundaries: `[4, 5, 6, 7]`.
- Final named selection: `sel_ring_wall_confirmed`.
- Wall feature / property name: `{'feature': 'spf/wallbc1', 'BoundaryCondition': 'NoSlip', 'SlidingWall': '1', 'TranslationalVelocityOption': 'Manual', 'selection': [4, 5, 6, 7], 'selection_binding': "wallbc1 uses COMSOL's existing noneditable explicit selection; verified equal to sel_ring_wall_confirmed [4,5,6,7]", 'utr_set': ['0', '0', '-V_ring']}`
- Flow inlet/outlet setting: `{'inlet_feature': 'spf/inl1', 'inlet_ids': [2], 'outlet_feature': 'spf/out1', 'outlet_ids': [3], 'U0in': 'U0', 'inlet_boundary_direction': 'boundary 2 bottom inlet is +z/upward; boundary 3 top inlet is -z/downward'}`
- Moving direction: negative `z`.
- `V_ring = 0.10[m/s]`.
- `t_end_move = 0.02[s]`.
- `u_r = 0`, `u_z = -V_ring` via `utr=[0,0,-V_ring]`.

## Fixed-Geometry Limitation

- Moving Wall changes the wall velocity boundary condition, not the ring geometry position.
- If the frame sequence shows the ring outline staying fixed, that is expected.
- Current model is still single-phase, has no free liquid surface, and cannot output true `Hmax`.

## Outputs

- Model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\models\ring_fountain_v3_moving_ring.mph`
- Timestamp model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\models\ring_fountain_v3_moving_ring_20260617_200014.mph`
- Center-hole `w(t)`: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\tables\moving_ring_center_hole_w_t.csv`
- Frame index: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\tables\moving_ring_frame_index.csv`
- Images:
  - velocity_magnitude: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\moving_ring_velocity_magnitude_spfU.png` (`ok=True`)
  - pressure: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\moving_ring_pressure.png` (`ok=True`)
  - axial_velocity_w: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\moving_ring_axial_velocity_w.png` (`ok=True`)
  - ring_near_velocity_vectors: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\moving_ring_ring_near_velocity_vectors.png` (`ok=True`)
- Frames:
  - `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\frames\moving_ring_velocity_frame_001.png` (`ok=True`)
  - `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\frames\moving_ring_velocity_frame_002.png` (`ok=True`)
  - `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\frames\moving_ring_velocity_frame_003.png` (`ok=True`)
  - `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\frames\moving_ring_velocity_frame_004.png` (`ok=True`)
  - `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\frames\moving_ring_velocity_frame_005.png` (`ok=True`)

## Solve Review

- Solve success: `True`
- Stage 3 scale-parameter cleanup before solve: `{'removed': ['U_impact', 'g_const', 'H_drop'], 'adjusted': [], 'reason': 'Stage 3 scale-only parameters caused a duplicate global name with the Gravity feature during transient equation compilation.'}`
- Current model can be used as Stage 5 input: `True` for single-phase fixed-geometry moving-wall context only.

## Structured Data

```json
{
  "status": "PASS",
  "wall": {
    "feature": "spf/wallbc1",
    "BoundaryCondition": "NoSlip",
    "SlidingWall": "1",
    "TranslationalVelocityOption": "Manual",
    "selection": [
      4,
      5,
      6,
      7
    ],
    "selection_binding": "wallbc1 uses COMSOL's existing noneditable explicit selection; verified equal to sel_ring_wall_confirmed [4,5,6,7]",
    "utr_set": [
      "0",
      "0",
      "-V_ring"
    ]
  },
  "flow": {
    "inlet_feature": "spf/inl1",
    "inlet_ids": [
      2
    ],
    "outlet_feature": "spf/out1",
    "outlet_ids": [
      3
    ],
    "U0in": "U0",
    "inlet_boundary_direction": "boundary 2 bottom inlet is +z/upward; boundary 3 top inlet is -z/downward"
  },
  "cleanup": {
    "removed": [
      "U_impact",
      "g_const",
      "H_drop"
    ],
    "adjusted": [],
    "reason": "Stage 3 scale-only parameters caused a duplicate global name with the Gravity feature during transient equation compilation."
  },
  "outputs": {
    "images": {
      "velocity_magnitude": {
        "ok": true,
        "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\images\\moving_ring_velocity_magnitude_spfU.png",
        "title": "spf.U",
        "vmin": 0.0,
        "vmax": 0.13890493247619204,
        "method": "Python rendering of COMSOL solved field samples near the ring"
      },
      "pressure": {
        "ok": true,
        "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\images\\moving_ring_pressure.png",
        "title": "p",
        "vmin": -20.177300168122486,
        "vmax": 2.345083798938347,
        "method": "Python rendering of COMSOL solved field samples near the ring"
      },
      "axial_velocity_w": {
        "ok": true,
        "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\images\\moving_ring_axial_velocity_w.png",
        "title": "w",
        "vmin": -0.09903585907552326,
        "vmax": 0.09622906054013494,
        "method": "Python rendering of COMSOL solved field samples near the ring"
      },
      "ring_near_velocity_vectors": {
        "ok": true,
        "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\images\\moving_ring_ring_near_velocity_vectors.png",
        "title": "velocity vectors",
        "vmin": 0.0,
        "vmax": 0.13890493247619204,
        "method": "Python rendering of COMSOL solved field samples near the ring"
      }
    },
    "times": {
      "w_t_csv": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\tables\\moving_ring_center_hole_w_t.csv",
      "frame_index_csv": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\tables\\moving_ring_frame_index.csv",
      "frames": [
        {
          "inner_solution": 1,
          "time_s": 0.0,
          "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\images\\frames\\moving_ring_velocity_frame_001.png",
          "ok": true
        },
        {
          "inner_solution": 2,
          "time_s": 0.005,
          "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\images\\frames\\moving_ring_velocity_frame_002.png",
          "ok": true
        },
        {
          "inner_solution": 3,
          "time_s": 0.01,
          "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\images\\frames\\moving_ring_velocity_frame_003.png",
          "ok": true
        },
        {
          "inner_solution": 4,
          "time_s": 0.015,
          "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\images\\frames\\moving_ring_velocity_frame_004.png",
          "ok": true
        },
        {
          "inner_solution": 5,
          "time_s": 0.02,
          "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\images\\frames\\moving_ring_velocity_frame_005.png",
          "ok": true
        }
      ]
    }
  }
}
```
