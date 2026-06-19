# A C4 Import Review

Run ID: `20260618_202100`

- C4 PASS: `PASS`
- `ALLOW_5B4 = YES`
- `ALLOW_5C = NO`
- `ALLOW_STAGE6 = NO`
- C4 best model exists: `True`
- C4 best Java exists: `True`
- This run may enter 5B4 only.
- This run must not enter 5C or Stage 6.
- No Jet1/Jet2, parameter sweep, or real Hmax extraction is performed.

## C4 Report Snippet

```text
# 5B3-C4 Seed-based Ring Smoke Final Report

Run ID: `20260618_182058`

## Required Answers

1. GUI-auto-seed imported: `True`.
2. Reused `TwoPhaseFlowLevelSet`: `True`.
3. Reused `WettedWall`: `True`.
4. Set `TranslationalVelocityOption = Manual`: `True` if C passed; see C report.
5. Set `utr = {"0", "-Vwall", "0"}`: `True` if C passed; see C report.
6. Built ring geometry: `True`.
7. Static `Vwall=0` baseline passed: `True`.
8. `Vwall=1e-4[m/s]` smoke passed: `True`.
9. `Vwall=5e-4[m/s]` passed: `True`.
10. Generated `ring_fountain_v5B3_C4_best.mph`: `True`.
11. Exported `ring_fountain_v5B3_C4_best.java`: `True`.
12. Allow 5B4: `YES`.
13. Allow 5C: `NO`.
14. Allow Stage 6: `NO`.

## Gates

- `ALLOW_5B4 = YES`
- `ALLOW_5C = NO`
- `ALLOW_STAGE6 = NO`

This run did not enter 5B4, 5C, 5D, 5E, Stage 6, Jet1/Jet2 extraction, parameter sweep, or real Hmax extraction.

Stop reason: ``
```