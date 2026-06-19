# Stage C Wall Non-Overlap Audit

Run time: `2026-06-18T15:56:28`
Best clean baseline model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_clean_baseline_rebuild\models\ring_fountain_v5B2_clean_static_baseline_best.mph`
Review status: `FAIL`

## Method

- Each Stage D case loads the best clean baseline fresh.
- Before solving each case, the default `spf` wall is restricted to all boundaries except that case's moving boundaries.
- A separate `wall_ring_move` feature is then created only on the moving boundary group.
- The per-case wall audit is written before solve and is also copied into the case table.

## Planned Moving Groups

| group | moving boundaries |
|---|---|
| `S1_vertical_edges_only` | `[4, 7]` |
| `S2_bottom_edge_only` | `[5]` |
| `S3_top_edge_only` | `[6]` |
| `S4_horizontal_edges_only` | `[5, 6]` |
| `S5_all_edges` | `[4, 5, 6, 7]` |

## Audit Results

| group | status | default_wall_mode | failure_message |
|---|---|---|---|
| `S1_vertical_edges_only` | `FAIL` | `` | `wall_overlap_unresolved: default wall selection is not editable and default wall cannot be removed: Exception:
	com.comsol.util.exceptions.FlException: Object cannot be removed.
Messages:
	Object cannot be removed.
	- Feature: Wall 1 (wallbc1)
` |
| `S2_bottom_edge_only` | `FAIL` | `` | `wall_overlap_unresolved: default wall selection is not editable and default wall cannot be removed: Exception:
	com.comsol.util.exceptions.FlException: Object cannot be removed.
Messages:
	Object cannot be removed.
	- Feature: Wall 1 (wallbc1)
` |
| `S3_top_edge_only` | `FAIL` | `` | `wall_overlap_unresolved: default wall selection is not editable and default wall cannot be removed: Exception:
	com.comsol.util.exceptions.FlException: Object cannot be removed.
Messages:
	Object cannot be removed.
	- Feature: Wall 1 (wallbc1)
` |
| `S4_horizontal_edges_only` | `FAIL` | `` | `wall_overlap_unresolved: default wall selection is not editable and default wall cannot be removed: Exception:
	com.comsol.util.exceptions.FlException: Object cannot be removed.
Messages:
	Object cannot be removed.
	- Feature: Wall 1 (wallbc1)
` |
| `S5_all_edges` | `FAIL` | `` | `wall_overlap_unresolved: default wall selection is not editable and default wall cannot be removed: Exception:
	com.comsol.util.exceptions.FlException: Object cannot be removed.
Messages:
	Object cannot be removed.
	- Feature: Wall 1 (wallbc1)
` |

## Gate Decision

- Stage C did not satisfy the non-overlap requirement.
- Stage D must not be treated as valid and is not run by the corrected gate.