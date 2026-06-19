# Interface Extraction Algorithm Audit

- Phase 1 status: `PASS`
- D0/D1/D2 all-time M1 extraction pass: `{'D0': True, 'D1': True, 'D2': True}`
- Old pseudo-spike present: `True`
- ROI pseudo-spike present: `True`
- Old spike caused by extraction/boundary contamination: `False`

Old algorithm audit:

- `H_raw_global` can include far-field or boundary-adjacent crossings and is not a trusted main free-surface height.
- R1 `pseudo_spike_flag` used a spread-style gate that did not sufficiently separate the main horizontal free surface from contaminating crossings.
- R2 M1 excludes outer-wall, top/bottom, and ring-near points before selecting the main connected interface.
- M4 is diagnostic-only smoothing and is not used to fabricate physical height.