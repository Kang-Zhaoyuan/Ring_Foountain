# 5B3-C2 Alternative Wall Strategy Final Report

Run time: 2026-06-18T16:47:47

Final C2 status: `FAIL`
ALLOW_RESUME_STAGE5 = `NO`

## Required Answers

1. Successfully created Wetted Wall: `False`.
2. Successfully created Interior Wetted Wall: `False`.
3. Can they act on ring boundaries: `tested if creatable; see C2-0/C2-1 reports. C2-1 status = FAIL`.
4. Bypassed noneditable `spf.wallbc1`: `False`.
5. Rebuilt selectable wall model from scratch: `True`; status `FAIL`.
6. Obtained `ring_fountain_v5B3_C2_best.mph`: `False`; ``.
7. Best case: ``.
8. Best case H(final)-H(0), Hmax, t_end: ``, ``, ``.
9. Current model type: `manual fallback / failed alternative strategy`.
10. Allow main workflow to resume into 5B4: `NO`.
11. `ALLOW_RESUME_STAGE5 = NO`.

## Stop Rules

- This run did not enter 5B4, 5C, 5D, 5E, stage 6.
- This run did not extract Jet1/Jet2 and did not perform a parameter study.
- If `ALLOW_RESUME_STAGE5 = YES`, the next step is allowed but was not started automatically.
- If `ALLOW_RESUME_STAGE5 = NO`, the next likely step is manual GUI/API inspection of COMSOL wall/Level Set boundary feature availability.

## Output Reports

- C2-0: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C2_alternative_wall_strategy\reports\C2_0_feature_probe_report.md`
- C2-1: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C2_alternative_wall_strategy\reports\C2_1_wetted_wall_report.md`
- C2-2: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C2_alternative_wall_strategy\reports\C2_2_rebuilt_selectable_wall_report.md`