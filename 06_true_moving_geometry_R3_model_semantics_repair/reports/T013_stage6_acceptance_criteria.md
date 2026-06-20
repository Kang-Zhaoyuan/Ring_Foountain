# T013 Stage 6 Acceptance Criteria

- Run id: `20260620_173514`
- Scope: acceptance criteria only. No COMSOL, Stage 6, real Hmax, parameter sweep, or Jet1 continuation was performed.

## Required YES/NO Criteria Before Any Future `ALLOW_STAGE6 = YES`

### 1. Physical Ring Motion Validity

- Required answer for future Stage 6: `YES`.
- Current T013 answer: `PARTIAL`.
- Must show ALE `PrescribedMeshDisplacement` on the confirmed ring boundaries and measured ring displacement matching the intended physical motion within a stated tolerance.
- Must document that WettedWall `utr` is a contactline/wall-frame condition, not double-counted geometry translation.

### 2. Boundary / Contactline Validity

- Required answer for future Stage 6: `YES`.
- Current T013 answer: `UNKNOWN`.
- Must classify WettedWall, contact angle, and slip settings as physically justified for the intended experiment, not only numerical stabilizers.
- Must include a static/control comparison showing the contactline setting does not introduce nonphysical free-surface artifacts.

### 3. Interface Extraction Validity

- Required answer for future Stage 6: `YES`.
- Current T013 answer: `PARTIAL`.
- Must use the main connected air-water interface, exclude outer-wall/top/bottom/ring-near contamination, and pass visual checks on representative frames.
- Must not use raw global crossings as physical height.

### 4. Real Hmax Validity

- Required answer for future Stage 6: `YES`.
- Current T013 answer: `NO`.
- Candidate real-Hmax definition: maximum vertical elevation of the validated connected air-water interface above the documented initial free-surface reference `z0`, inside a physically justified domain or ROI, after excluding boundary/mesh/contactline artifacts.
- Must include units, sign convention, time window, initial reference, extraction method, artifact exclusions, mesh/time-step sensitivity, and figure/table/log audit.

### 5. Image / Table / Log Audit Completeness

- Required answer for future Stage 6: `YES`.
- Current T013 answer: `CRITERIA_DEFINED`.
- Every future candidate must have a manifest of source models, scripts, logs, arrays/tables, and CSV-backed figures. Claims must trace to tables, not only images.

### 6. Minimum Control-Case Requirements

- Required answer for future Stage 6: `YES`.
- Current T013 answer: `CRITERIA_DEFINED`.
- Minimum controls: zero-motion baseline, micro-motion baseline, static/no-ring or ring-position controls, contactline/slip controls, mesh/time-step sensitivity, fixed-geometry negative-control context, and visual audit of interface continuity.

### 7. Is Jet1 Required For Stage 6?

- Required answer for future Stage 6: `NO, not categorically`.
- Current T013 answer: `CURRENT_JET1_BRANCH_ALLOWED = NO`.
- Stage 6 may later be entered through a non-Jet1 physical mechanism only if the mechanism has an explicit Review Agent definition and passes the same real-Hmax acceptance criteria. The current Jet1 ROI/threshold branch remains closed.

## Gate Result

- `ALLOW_STAGE6_NOW = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_BOUNDED_STAGE6_PRECHECK = YES`
