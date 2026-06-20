# Spike Spatial Localization Report

- Phase 2 status: `PASS_WITH_MEMORY_GUARD`
- Principal spike/roughness location: `global`.
- D0/C1/C2/C3 localization used R2 exported CSV metrics because direct R2 model reload caused memory/ComsolUI instability.
- This is sufficient to classify the failure as ring-present static/global ROI roughness, but not sufficient for publication-quality spatial maps.
- Fresh geometry controls in Phase 3 are used for the actionable root-cause split.