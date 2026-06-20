# T011-A Threshold Source Audit

- Run id: `20260620_170508`
- Scope: Jet1 ROI/threshold semantics audit only.
- No COMSOL run was performed.

## Key Recovered Semantics

- Fixed-geometry 5C ROI: center-hole or inner-edge region above the initial interface.
- Fixed-geometry threshold constant recovered from script: `delta > 5e-5` m.
- Fixed-geometry exclusion logic: early time, continuous robust/raw height, not isolated component, not near-top, not pseudo-spike.
- In true geometry these are diagnostic analogues only; they are not physical Jet1 validation rules.

## Files Inspected

| file | inspected | scope | true-geometry compatibility |
|---|---|---|---|
| `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5C_jet1_extraction\reports\B_jet1_definition_and_ROI_report.md` | `YES` | `fixed_geometry_definition` | `diagnostic_geometry_only` |
| `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5C_jet1_extraction\reports\D_jet1_candidate_detection_report.md` | `YES` | `fixed_geometry_detection_report` | `diagnostic_exclusion_logic_only` |
| `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5C_jet1_extraction\tables\D_jet1_candidate_timeseries.csv` | `YES` | `fixed_geometry_candidate_timeseries` | `audit_reference_only` |
| `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5C_jet1_extraction\scripts\ring_fountain_stage5c_jet1_extraction.py` | `YES` | `fixed_geometry_implementation` | `threshold_reference_only_not_physical_validation` |
| `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\06_true_moving_geometry_R3_true_geometry_jet1_diagnostic\tables\T010_recomputed_metrics.csv` | `YES` | `true_geometry_diagnostic_table` | `primary_T011_recompute_source` |
