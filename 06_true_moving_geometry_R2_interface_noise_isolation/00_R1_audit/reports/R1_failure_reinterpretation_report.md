# R1 Failure Reinterpretation Report

- R1 run id: `20260619_165307`
- Phase B repaired `H0 = nan`: YES.
- Phase B repaired `interface_points_initial = 0`: YES.
- Phase C produced `mesh_quality_min`, but the value is constantly 1.0 and requires Phase 4 validation.
- Phase D D0/D1/D2 solve success: `True`.
- Phase D gate failure reason: `pseudo_spike_detected = True`, not COMSOL solver crash: `True`.
- D0 is the zero-velocity static case and also spiky: `True`.
- D0/D1/D2 robust drift approximately similar: `True`.
- `R1_FAILURE_TYPE = extraction_contamination_likely`.

This is a diagnostic reinterpretation only.  It does not output real Hmax and does not support Stage 6.