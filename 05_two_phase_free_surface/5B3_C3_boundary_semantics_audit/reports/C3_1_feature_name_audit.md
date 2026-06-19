# C3-1 Feature Name Audit

Run time: 2026-06-18T17:15:12

C3-1 status: `PASS`

## Conclusions

- Formal `Laminar Two-Phase Flow, Level Set` / `Phase Field` interface creation is not proven by API enumeration.
- The current API path can enumerate existing model objects and feature properties, but cannot enumerate the full COMSOL create-type catalog.
- Therefore the formal two-phase interface true API name remains unresolved from automation alone.
- `spf.Wall` is creatable and exposes moving-wall-related properties in this environment: `True`.
- `spf.Inlet`, `spf.Outlet`, and `spf.OpenBoundary` remain disallowed as substitutes for solid moving wall.
- Required manual next step if C3 minimal tests fail: create the desired GUI model and export Java/M-file to reveal exact feature/interface type names.

## Machine-Readable Table

- `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C3_boundary_semantics_audit\tables\C3_1_feature_name_audit.csv`