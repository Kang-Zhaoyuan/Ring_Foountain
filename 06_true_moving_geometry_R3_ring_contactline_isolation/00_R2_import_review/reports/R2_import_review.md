# R2 Import Review

- R2 run id: `20260619_210233`
- R2 was not a COMSOL solver crash.
- D0/D1/D2 solved and D0 is the Vring=0 static case.
- C3 no-ring rectangular seed is clear, while C1 no-ALE ring case remains weak_or_spiky.
- Therefore R2 does not support a velocity-amplified ALE-LS instability claim.
- This R3 run keeps Stage 6, real Hmax, and formal Jet1 disabled.

## R2 Internal Inconsistencies

- Phase0 says R1_FAILURE_TYPE=extraction_contamination_likely
- Phase1 says old spike caused by extraction/boundary contamination=False
- Final says old pseudo-spike source=unresolved_or_numerical_static_relaxation