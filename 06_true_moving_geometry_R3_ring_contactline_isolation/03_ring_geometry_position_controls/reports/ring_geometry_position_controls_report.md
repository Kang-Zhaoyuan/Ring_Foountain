# Ring Geometry and Position Controls Report

- Phase 3 status: `FAIL_DIAGNOSTIC_MEMORY_GUARD`
- G2/G3 COMSOL solves produced saved models, but ROI/regional postprocessing hit Python `MemoryError`.
- Because the static ring-present baseline cannot be verified, R3 stops before more geometry/contact-line expansion.
- This is a diagnostic/postprocessing blocker, not proof of velocity-amplified ALE-LS oscillation.