# Handoff

Date: 2026-07-16

## Current state

- The project remains under `/home/kqdx/basilisk_work/ring_fountain` in WSL2 Ubuntu. Basilisk is read-only at `/home/kqdx/basilisk/src`, and `/home/kqdx/basilisk/src/qcc` remains compilation authority.
- The general fixed embedded VOF contact-line gate remains failed. The Tavares header is still unlicensed evaluation material outside the repository; only project-authored descriptions, diagnostics, tables, and results are tracked.
- The user-confirmed metal density is exactly `7800 kg/m^3`. With the validated ring dimensions, mass is `0.02144136986075032 kg` and weight is `0.21033983833396064 N`.
- The free-fall exploration uses a fixed embedded ring in an accelerating ring frame, uniform multigrid, axisymmetric two-phase VOF, gravity, surface tension, and the uncalibrated 75 deg contact-angle assumption. It integrates laboratory ring position and speed from an axisymmetric fluid-traction estimate. It is not moving-cut-cell geometry.
- Hydrostatic force, air-only free fall, dynamic hydrostatic stability, and prescribed-speed regression gates passed. Dump restart was rejected because it introduces a spurious pressure impulse and velocity disturbance.
- Tall-domain L6 and L7 runs completed to 330 ms. The user manually identified a central first-jet candidate with a surrounding annular cavity; neither grid is claimed to be more physically accurate.
- Deep 16:1 L6 and L7 runs completed to 530 ms. The final L7 run was rerun from `t=0` after the host power loss and completed uninterrupted; no partial dump was stitched.
- Deep L7 ends with ring drop `1.118686 m`, downward speed `3.972879 m/s`, maximum water-budget residual `0.2356%`, zero deep-solid liquid, zero invalid values, minimum `dt=9.091e-6 s`, and 262,144 cells.
- No coherent annular-cavity closure or credible Worthington jet appears by 530 ms. The central first-jet candidate persists, while the long cavity develops strong corrugation and detached fragments after roughly 390 ms.
- L7 maximum laboratory speed is `22.629 m/s`; saved 458--464 ms field samples place the rising high-speed path in full-fluid interface cells about 38 mm above the ring, not solely in embedded cut cells. Large late force oscillations coexist, so the late branch is not quantitatively credible.
- A reproducible fixed-laboratory-frame animation workflow is tracked in `cases/08_exploratory_freefall_entry/tools/`. The resulting H.264 video shows the moving ring and water speed on a fixed `0--10 m/s` scale, with larger values saturated red.
- Review material is in `cases/08_exploratory_freefall_entry/review/`, including the 330--530 ms L7 interface sheet, full animation, and decoded-video audit sheet.

## Evidence and storage

- Tracked summaries: `cases/08_exploratory_freefall_entry/model_parameters.tsv`, `gate_summary.tsv`, `run_summary.tsv`, and `speed_peak_samples.tsv`.
- Tracked interpretation and limitations: `cases/08_exploratory_freefall_entry/README.md` and `docs/VALIDATION.md`.
- Ignored numerical evidence archive: `runs/20260716_173500_08_exploratory_freefall_entry/`. It contains complete diagnostics, interfaces, field samples, dumps, and rendering evidence but no private source, external header, or executable.
- The final L7 run directory is about 850 MiB and contains 1,346 files before archive integration. Its service result is success with exit status 0.
- Start-of-round Git HEAD was `c9d7393` (`Diagnose grid sensitivity in ring entry`). Git metadata is writable. Push remains manual by project rule and user choice.

## Model limits

- The 75 deg contact angle is an uncalibrated engineering assumption, not measured metal wetting.
- The fluid force omits an explicit solid contact-line capillary line reaction; a simple upper bound is about four percent of ring weight.
- Uniform L7 is only the selected qualitative branch. L6/L7 morphology is not converged, quadtree viscous AXI+EMBED fails, and earlier L8/phase controls showed sensitivity.
- The numerical domain is an open moving window, not a literal finite tank. The animation border must not be interpreted as a physical wall.
- No real splash height, jet time, ring trajectory, or dynamic contact-angle data were used for tuning. No claim is made for real jet height or mechanism.

## Next gate

The only next action is to compare the frozen L7 trajectory and interface chronology against the forthcoming blinded experiment. Do not increase release height or tune contact parameters before that comparison: the current ring already accelerates to nearly 4 m/s, while the missing closure coincides with late numerical instability rather than clear evidence of insufficient impact speed.
