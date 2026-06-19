# C API Seed Attempt

Run time: 2026-06-18T17:48:33

C status: `PASS`

## Evidence

- Reference Java export: `{'status': 'PASS', 'source_model': 'D:\\COMSOL64\\Multiphysics\\applications\\CFD_Module\\Multiphase_Flow\\capillary_filling_ls.mph', 'java': 'D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\5B3_GUI_auto_seed\\exports\\reference_capillary_filling_ls.java', 'api_rows': 21}`
- Seed model saved: `True` at `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_GUI_auto_seed\models\ring_fountain_gui_auto_seed_minimal_twophase_wall.mph`
- Seed Java exported: `True` at `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_GUI_auto_seed\exports\ring_fountain_gui_auto_seed_minimal_twophase_wall.java`
- Case table: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_GUI_auto_seed\tables\C_api_seed_cases.csv`

## Boundary Semantics

- Formal coupling: `component('comp1').multiphysics().create('tpf1', 'TwoPhaseFlowLevelSet', 2)`.
- Moving wall: `component('comp1').multiphysics().create('ww1', 'WettedWall', 1)`.
- `ww1` uses `TranslationalVelocityOption = Manual` and `utr = ['0', '-Vwall', '0']` on the right boundary.
- `spf.Inlet`, `spf.Outlet`, and `spf.OpenBoundary` were not used as moving solid wall substitutes.