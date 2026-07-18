# Handoff

Date: 2026-07-18

## Current state

- The project remains under `/home/kqdx/basilisk_work/ring_fountain` in WSL2 Ubuntu. Basilisk is read-only at `/home/kqdx/basilisk/src`, and `/home/kqdx/basilisk/src/qcc` remains compilation authority.
- The general fixed embedded VOF contact-line gate remains failed. The Tavares header is still unlicensed evaluation material outside the repository; only project-authored descriptions, diagnostics, tables, and results are tracked.
- Root `requirements.txt` records that all tracked Python analysis tools use only the standard library. It also freezes the verified Python/system-tool versions and Basilisk Darcs weak hash; the unlicensed external contact header remains intentionally unavailable through pip or this repository.
- The earlier ring uses user-confirmed density `7800 kg/m^3`, dimensions `Ri=2.5 mm`, `Ro=15 mm`, `h=4 mm`, and derived mass `21.441 g`. The 17 July workbook describes a different specimen and must not be mixed with it.
- The free-fall exploration uses a fixed embedded ring in an accelerating ring frame, uniform multigrid, axisymmetric two-phase VOF, gravity, surface tension, and the uncalibrated 75 deg contact-angle assumption. It integrates laboratory ring position and speed from an axisymmetric fluid-traction estimate. It is not moving-cut-cell geometry.
- Hydrostatic force, air-only free fall, dynamic hydrostatic stability, and prescribed-speed regression gates passed. Dump restart was rejected because it introduces a spurious pressure impulse and velocity disturbance.
- Tall-domain L6 and L7 runs completed to 330 ms. The user manually identified a central first-jet candidate with a surrounding annular cavity; neither grid is claimed to be more physically accurate.
- Deep 16:1 L6 and L7 runs completed to 530 ms. The final L7 run was rerun from `t=0` after the host power loss and completed uninterrupted; no partial dump was stitched.
- Deep L7 ends with ring drop `1.118686 m`, downward speed `3.972879 m/s`, maximum water-budget residual `0.2356%`, zero deep-solid liquid, zero invalid values, minimum `dt=9.091e-6 s`, and 262,144 cells.
- No coherent annular-cavity closure or credible Worthington jet appears by 530 ms. The central first-jet candidate persists, while the long cavity develops strong corrugation and detached fragments after roughly 390 ms.
- L7 maximum laboratory speed is `22.629 m/s`; saved 458--464 ms field samples place the rising high-speed path in full-fluid interface cells about 38 mm above the ring, not solely in embedded cut cells. Large late force oscillations coexist, so the late branch is not quantitatively credible.
- A reproducible fixed-laboratory-frame animation workflow is tracked in `cases/08_exploratory_freefall_entry/tools/`. The resulting H.264 video shows the moving ring and water speed on a fixed `0--10 m/s` scale, with larger values saturated red.
- Review material is in `cases/08_exploratory_freefall_entry/review/`, including the 330--530 ms L7 interface sheet, full animation, and decoded-video audit sheet.
- A new 10 cm-release experiment reports that the ring becomes fully surrounded by water rather than carrying a cavity to large depth.
- The matching 10 cm-release original L7 run remains attached through lower-face depth `305.6 mm`; this directly rejects the case-08 topology against experiment.
- L6 controls spanning 30--120 deg, half/double surface tension, and no-slip/free-slip all remain attached. Water surface tension is not tuned.
- A separate one-time experiment-constrained wetting event at provisional lower-face depth `100 mm` detaches the cavity without a new force or speed peak. A later audit found that its historical one-sided level-set condition filled the entire solid interior; those full-fill runs are superseded.
- The historical constrained L7 run completes to 320 ms with `0.1663%` maximum budget residual, zero invalid values, `0.547 mL` added mobile water, and no reattachment. Its reported deep-solid zero is now an under-resolved false negative, not evidence that the full-fill condition was healthy.
- The 17 July workbook was read in place and frozen by SHA256. It contains two populated repeats of one group at `2000 fps`, not two independently parameterized groups.
- Measured mean crown, first-jet, and Worthington heights are `9.425`, `66.135`, and `58.335 mm`; mean post-contact times are `44.0`, `69.25`, and `161.75 ms`.
- For cases 10 and 11, the workbook is the specimen authority: `Ri=2.6 mm`, `Ro=6.3 mm`, thickness `5.02 mm`, measured mass `5.35 g`, and release height `105 mm`. Literal rectangular geometry implies `10.302 g/cm3`, but this is only a metadata warning; the measured mass is used directly and the earlier `7.8 g/cm3` value is not substituted.
- The first literal-geometry L7 run completed uninterrupted to 340 ms with `0.1123%` maximum budget residual, `9.607 m/s` maximum laboratory speed, and zero invalid values. Its deep-solid zero is unresolved because only `3.95` cells span the radial metal width.
- Its empirical transition occurs `59.702 ms` after first wetting and adds `0.1755 mL`, contaminating first-jet timing as an independent prediction.
- A new connected-water height detector finds only `8.575 mm` maximum coherent rise. At the six experimental event times the model gives `1.333--7.901 mm`, so this stable L7 preflight fails the first/Worthington height comparison.
- The run is under-resolved: only `3.95` L7 cells span the radial metal width. No contact-angle or surface-tension fit was attempted.
- The user reports that the measured first jet is approximately equal diameter rather than the simulated L7 mushroom shape. Native-facet profiles confirm L7 upper/lower mean-radius ratios `1.060` at 62.5 ms and `1.122` at 76 ms.
- Disabling the empirical event at L7 does not improve the shape and raises maximum speed to `16.023 m/s`; this control is rejected.
- The project-authored empirical event is corrected in isolation to the thin band `-1.25 Delta <= ring_levelset <= 1.25 Delta`. Corrected L7 and L8 qcc builds both complete uninterrupted to 240 ms with zero deep-solid liquid, zero invalid values, final dumps, and dense interfaces.
- Corrected L7 retains the mushroom shape. Corrected L8 gives upper/lower ratio `0.962` at 62.5 ms and a visibly straighter central body, but develops broad shoulders/multiple interfaces by 76 ms and returns to ratio `1.231` at 90 ms.
- Corrected L8 has lower maximum budget residual (`0.0933%`) but maximum laboratory speed `19.973 m/s`, twice corrected L7 (`9.615 m/s`). Its maximum coherent height is only `8.295 mm`; it is a shape diagnostic, not a quantitative replacement for L7.
- Case 12 is a separate video specimen and must not be mixed with the workbook specimen. Its title gives `Ri=5.05 mm`, `Ro=20.07 mm`, thickness `2.86 mm`, and measured mass `26.15 g`; the literal equivalent density is `7713.76 kg/m3`.
- The read-only 660-frame laboratory video was frozen by SHA256. Physical timing uses the user-supplied `2000 fps` source rate and frame 300 as contact; the encoded `30 fps` is only playback timing. No video or decoded frame is tracked.
- Independent pre-contact labels give impact speed `1.34555 m/s` and equivalent vacuum release height `92.279 mm`. The force-feedback L7 baseline is rejected because it reaches `61.42/77.60 mm` depth at frames 384/405 instead of `38.064/45.806 mm` and accelerates after entry.
- A prescribed post-contact trajectory fitted only to ring positions reproduces frames 384/405 within `0.0042 mm`. It is a kinematic calibration, not predictive free fall; fluid force remains diagnostic.
- The video morphology was held out from the trajectory fit. Additional holdout frames 335, 360, 430, 455, 520, 550, and 620 independently cover crown growth, the thin first jet, cavity taper/separation, and the later jet.
- At frame 405 (`52.5 ms`), the measured thin first jet is `105.80 mm`, while connected CFD rise is only `1.436 mm` at L7 and `0.392 mm` at L8. L8 smooths the attached cavity wall but does not create the jet.
- At frame 492 the experiment has a closed hourglass air shape with the first jet still present. L7 retains paired corrugated cavity walls toward the ring and a broad `10.299 mm` pedestal. The empirical trigger depth comes from this frame, so timing is not independently predicted and geometry fails.
- Frames 520--620 show a separated ring, mostly relaxed surrounding surface, and a thin later jet. L7 instead retains fragmented cavity remnants and a broad `12.210--17.188 mm` pedestal.
- Over the common `t<=0.2 s` interval, L7/L8 budget drifts are `0.2085%/0.2542%`, maximum laboratory speeds are `5.387/18.645 m/s`, deep-solid liquid and invalid values are zero, and both runs have final dumps. The L8 saved-field speed peak is below the free surface, not in an upward jet.

## Evidence and storage

- Tracked summaries: `cases/08_exploratory_freefall_entry/model_parameters.tsv`, `gate_summary.tsv`, `run_summary.tsv`, and `speed_peak_samples.tsv`.
- The detachment audit, screening table, source hashes, and review images are tracked in `cases/09_release10cm_cavity_detachment/`.
- The workbook transcription, timing statistics, coherent-height tool, provisional run summaries, and review plots are tracked in `cases/10_experiment_0717_calibration/`.
- First-jet native-facet profiles, health/shape comparison tables, source hashes, and manual-review images are tracked in `cases/11_first_jet_shape_correction/`.
- Video metadata, transcribed labels, trajectory constraints, L7/L8 health and geometry tables, project-authored analysis tools, and simulation-only review images are tracked in `cases/12_video_26p15g_calibration/`.
- Complete ignored case-11 evidence is in `runs/20260717_160533_11_first_jet_shape/` (four uninterrupted runs, about 4.3 GiB). Its 4,861-entry relative manifest verifies and has SHA256 `f76a03085e1a5a7b3b33ac87246f0da568f2f29f8dba30318293dc5c600535df`. No solver source, executable, or external header is stored there.
- Complete ignored L7 evidence is in `runs/20260717_124703_10_experiment_0717/` (about 1.4 GiB, 340 sampled fields, 1,362 interface files, dumps, and exit status 0). Its 1,719-entry manifest hash is `1023ff66450ecd3c5c2f004c2e3c97d5762a99d2a4ffc31c67574f6efc7c39b5`. No solver source, binary, or external contact header is stored there.
- Complete ignored evidence is in `runs/20260716_200718_09_release10cm_detachment/`; its 6,589-entry SHA256 manifest verifies with hash `b6d119fb39f7cbac9414ffa5ca2d6907d1f4f09de54d76545d9c641a387ea7da`.
- Tracked interpretation and limitations: `cases/08_exploratory_freefall_entry/README.md` and `docs/VALIDATION.md`.
- Ignored numerical evidence archive: `runs/20260716_173500_08_exploratory_freefall_entry/`. It contains complete diagnostics, interfaces, field samples, dumps, and rendering evidence but no private source, external header, or executable.
- The final L7 run directory is about 850 MiB and contains 1,346 files before archive integration. Its service result is success with exit status 0.
- Complete ignored case-12 evidence is in `runs/20260717_213534_12_video_26p15g_calibration/` (three uninterrupted runs, about 3.4 GiB, dense interfaces, sampled fields, final dumps, and private local review sheets). Its 4,055-entry relative manifest verifies and has SHA256 `720a31ba3396e4ce6adee754bfaca7ad0ce7b0bd4c7b37851db9fa26d8429ebb`. It contains no solver source, executable, external header, raw video, or decoded source frame.
- Git is writable. The experimental-data intake is committed locally as `09374ba`, the shape-correction round as `12b4302`, and the case-12 video audit is the current local HEAD. Push remains manual by project rule and user choice.

## Model limits

- The 75 deg contact angle is an uncalibrated engineering assumption, not measured metal wetting.
- The fluid force omits an explicit solid contact-line capillary line reaction; a simple upper bound is about four percent of ring weight.
- Uniform L7 is only the selected qualitative branch. L6/L7 morphology is not converged, quadtree viscous AXI+EMBED fails, and earlier L8/phase controls showed sensitivity.
- The corrected empirical thin band is still a topology scaffold, not a physical moving contact-line or dynamic-wetting law. Historical one-sided full-fill results must not be reused.
- The numerical domain is an open moving window, not a literal finite tank. The animation border must not be interpreted as a physical wall.
- The workbook branch still has no raw imagery or measured trajectory. The separate case-12 video has ring-position labels and morphology, but no measured dynamic contact angle, calibrated water silhouette, pressure, or force history.
- The coherent-height proxy is measured on 1 mm sampled CFD fields and conservatively excludes disconnected droplets. It is not yet calibrated to the user's partly fragmented visual criterion.
- The case-12 experiment develops about `5 deg` of depth-direction tilt and a left-curved first jet. Axisymmetry can compare symmetric height and cavity topology but cannot reproduce those three-dimensional asymmetries.
- The case-12 post-contact path is prescribed from experiment. It isolates morphology error but cannot validate the fluid-force feedback or predict a new release condition.

## Next gate

The only next action is to develop a project-owned, license-clear dynamic
wetting/detachment closure for the fixed embedded ring and validate it first
against the held-out cavity topology. Do not change contact angle, surface
tension, or the empirical trigger to force agreement with the video.
