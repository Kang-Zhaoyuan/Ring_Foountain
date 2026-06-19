# Stage 4.1 Ring Boundary Manual Review Package

Run time: 2026-06-17T19:33:59

This package only identifies candidate ring-wall boundaries and creates `sel_ring_wall_candidate` for manual review. No moving-wall, wall-movement, ALE, or time-dependent motion setting has been applied.

## 候选圆环边界编号：

`[4, 5, 6, 7]`

Role mapping:
- `inner_vertical_r_eq_Ri`: boundary `4`
- `outer_vertical_r_eq_Ro`: boundary `7`
- `top_horizontal_z_eq_plus_h_over_2`: boundary `6`
- `bottom_horizontal_z_eq_minus_h_over_2`: boundary `5`

## 候选边界坐标：

| role | boundary | center (r,z) m | endpoint/range 1 m | endpoint/range 2 m |
| --- | ---: | --- | --- | --- |
| `inner_vertical_r_eq_Ri` | 4 | (0.008, 6.6174449e-21) | (0.008, -0.001) | (0.008, 0.001) |
| `outer_vertical_r_eq_Ro` | 7 | (0.02, -2.64697796e-20) | (0.02, -0.001) | (0.02, 0.001) |
| `top_horizontal_z_eq_plus_h_over_2` | 6 | (0.014, 0.001) | (0.008, 0.001) | (0.02, 0.001) |
| `bottom_horizontal_z_eq_minus_h_over_2` | 5 | (0.014, -0.001) | (0.008, -0.001) | (0.02, -0.001) |

## 候选边界长度：

| role | boundary | length m | length mm |
| --- | ---: | ---: | ---: |
| `inner_vertical_r_eq_Ri` | 4 | 0.002 | 2 |
| `outer_vertical_r_eq_Ro` | 7 | 0.002 | 2 |
| `top_horizontal_z_eq_plus_h_over_2` | 6 | 0.012 | 12 |
| `bottom_horizontal_z_eq_minus_h_over_2` | 5 | 0.012 | 12 |

## 理论圆环边界位置：

- `Ri = 0.008 m`
- `Ro = 0.02 m`
- `h_ring = 0.002 m`
- Inner side: `r = Ri = 0.008 m`, `z in [-0.001, 0.001] m`
- Outer side: `r = Ro = 0.02 m`, `z in [-0.001, 0.001] m`
- Top side: `z = +h_ring/2 = 0.001 m`, `r in [0.008, 0.02] m`
- Bottom side: `z = -h_ring/2 = -0.001 m`, `r in [0.008, 0.02] m`
- Theoretical 2D perimeter: `0.028 m`
- Candidate summed length: `0.028 m`

## 几何一致性检查：

- `candidate_count_is_4`: `True`
- `total_length_close_to_theory`: `True`
- `all_positions_match_theory`: `True`
- `all_candidates_are_internal_hole_boundaries`: `True`
- `no_outer_tank_boundaries_selected`: `True`

## 全部 boundary 导出：

| boundary | center (r,z) m | endpoint/range 1 m | endpoint/range 2 m | length m | candidate match | internal hole? |
| ---: | --- | --- | --- | ---: | --- | --- |
| 1 | (0, 6.26804381e-18) | (0, -0.12) | (0, 0.12) | 0.24 | `` | `False` |
| 2 | (0.05, -0.12) | (0, -0.12) | (0.1, -0.12) | 0.1 | `` | `False` |
| 3 | (0.05, 0.12) | (0, 0.12) | (0.1, 0.12) | 0.1 | `` | `False` |
| 4 | (0.008, 6.6174449e-21) | (0.008, -0.001) | (0.008, 0.001) | 0.002 | `inner_vertical_r_eq_Ri` | `True` |
| 5 | (0.014, -0.001) | (0.008, -0.001) | (0.02, -0.001) | 0.012 | `bottom_horizontal_z_eq_minus_h_over_2` | `True` |
| 6 | (0.014, 0.001) | (0.008, 0.001) | (0.02, 0.001) | 0.012 | `top_horizontal_z_eq_plus_h_over_2` | `True` |
| 7 | (0.02, -2.64697796e-20) | (0.02, -0.001) | (0.02, 0.001) | 0.002 | `outer_vertical_r_eq_Ro` | `True` |
| 8 | (0.1, 2.30675306e-17) | (0.1, -0.12) | (0.1, 0.12) | 0.24 | `` | `False` |

## 输出文件：

- Boundary table CSV: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\tables\ring_boundary_all_boundaries.csv`
- Boundary table XLSX: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\tables\ring_boundary_all_boundaries.xlsx`
- Review model with `sel_ring_wall_candidate`: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\models\ring_fountain_v3_boundary_review_package.mph`
- Timestamp model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\models\ring_fountain_v3_boundary_review_package_20260617_193341.mph`
- Full boundary ID image: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\ring_boundary_full_model_ids.png`
- Ring-local boundary ID image: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\ring_boundary_local_ids.png`
- Candidate-highlight image: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\ring_boundary_candidate_highlight.png`

## 需要用户确认的问题：

请人工确认：这些边界是否确实是圆环表面？

如果确认，请回复：

`人工确认通过，圆环边界为：[4, 5, 6, 7]，可以继续阶段 4.2。`

如果不确认，请指出错误边界编号或上传截图。

## Structured Data

```json
{
  "stage": "4.1",
  "status": "AWAITING_MANUAL_CONFIRMATION",
  "candidate_ids": [
    4,
    5,
    6,
    7
  ],
  "checks": {
    "candidate_count_is_4": true,
    "total_length_close_to_theory": true,
    "all_positions_match_theory": true,
    "all_candidates_are_internal_hole_boundaries": true,
    "no_outer_tank_boundaries_selected": true
  },
  "outputs": {
    "boundary_csv": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\tables\\ring_boundary_all_boundaries.csv",
    "boundary_xlsx": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\tables\\ring_boundary_all_boundaries.xlsx",
    "model": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\models\\ring_fountain_v3_boundary_review_package.mph",
    "timestamp_model": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\models\\ring_fountain_v3_boundary_review_package_20260617_193341.mph",
    "full_image": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\images\\ring_boundary_full_model_ids.png",
    "local_image": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\images\\ring_boundary_local_ids.png",
    "highlight_image": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\images\\ring_boundary_candidate_highlight.png",
    "report": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\reports\\ring_boundary_manual_review_package.md",
    "log": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\logs\\stage4_1_boundary_review_20260617_193341.log"
  }
}
```
