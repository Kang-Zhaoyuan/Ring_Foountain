# 06_R1 True Moving Geometry Diagnostic Repair Final Report

- Run id: `20260619_165307`.
- Final branch: `FAIL`.
- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = NO`.
- `ALLOW_STAGE6_PARAMETER_SWEEP = NO`.
- `ALLOW_REAL_HMAX_OUTPUT = NO`.

## Required Answers

1. Previous campaign imported: `True`.
2. Previous `PASS_MINIMAL` meaning confirmed: ALE true motion ran, but physical ring-fountain response was not proven.
3. `interface_points_initial = 0` cause: diagnostic workflow failure; solved model has t=0 and `phils` crossing 0.5.
4. `H0 = nan` cause: diagnostic extraction did not reliably read solved t=0/interface data.
5. Free-surface diagnostic repaired: `True`.
6. `mesh_quality_min` repaired: `True`.
7. Zero-motion regression passed: `False`.
8. Micro-motion regression passed: `False`.
9. Target displacement ladder maximum passed: `0.0` m.
10. Maximum passed displacement Vring/t_end: see `PhaseE.rows` for best row.
11. Visible free-surface deformation: `False`.
12. Center-hole/inner-edge upward trend: not accepted as final physics unless Phase F/G gates pass.
13. Jet1 detection readiness: `NO`.
14. Best mph generated: `False`.
15. Best java exported: `False`.
16. Stage 6 parameter sweep allowed: `NO`.
17. Real Hmax output allowed: `NO`.

## Self Audit

- H0/interface initial issue covered.
- mesh quality issue covered or failed with reason.
- No Stage 6 parameter sweep performed.
- No real Hmax produced.
- PASS/FAIL gates are data-backed in CSV tables.