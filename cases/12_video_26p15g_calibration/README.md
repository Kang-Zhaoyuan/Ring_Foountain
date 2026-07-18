# 26.15 g laboratory-video calibration

Date: 2026-07-17. Status: **ring trajectory reproduced kinematically;
axisymmetric water and air-cavity morphology rejected at L7 and in the short
L8 check**.

## Scope and evidence boundary

The read-only source video is
`E:\Ring_Inner_r5.05mm_Ring_outter_R20.07mm_Ring_Thickness_2.86mm_Ring_mass_26.15g_C001H001S0001.mp4`.
It was read through the WSL `E:` mount, never copied into the repository, and
has SHA256
`c5982c4ee7c2332d9798de1cc61a57400bb9acb694d9bfbb5473dba189ab8c07`.
`video_source_lock.tsv` records its metadata. The encoded video is a slowed
30 fps presentation, while the physical source rate supplied by the user is
2000 fps; all physical times therefore use `0.5 ms` per source frame and
frame 300 as first contact.

The isolated solver is project-authored but includes the unlicensed external
`contact-embed.h`. Solver source, binary, header, and the complete video remain
outside Git. At the project owner's explicit request, 15 selected decoded
laboratory frames and project-authored annotations are now tracked in
`experiment_frames/`; their provenance, SHA256 hashes, and media-rights limit
are documented there. `source_hashes.tsv` freezes the numerical-source hashes.
Compilation used `/home/kqdx/basilisk/src/qcc -O2 -Wall` and completed without
diagnostics. Basilisk source was not modified.

## Model and specimen

The video title gives `Ri=5.05 mm`, `Ro=20.07 mm`, thickness `2.86 mm`, and
mass `26.15 g`. The literal rectangular annulus has volume `3.390045 mL` and
equivalent density `7713.76 kg/m3`, consistent with the earlier nominal metal
density but not substituted for the measured mass.

The fluid model is axisymmetric, uniform multigrid, two-phase VOF, fixed
embedded rectangular ring section, gravity, surface tension
`0.072 N/m`, and the inherited uncalibrated `75 deg` contact-angle assumption.
The fixed ring is viewed in a translating non-inertial frame and plotted in a
fixed laboratory frame. This is not moving-cut-cell geometry and the selected
run is not a predictive free-fall solution.

The earlier force-feedback L7 run correctly reproduces the pre-contact fall
but reaches `61.42` and `77.60 mm` depth at frames 384 and 405 instead of
`38.064` and `45.806 mm`; its insufficient drag then lets the ring accelerate.
It is rejected. To separate kinematic error from water-shape error, the
selected branch prescribes a continuous post-contact trajectory,

`U(tau) = U_terminal + (U_impact - U_terminal) exp(-k tau)`,

with `U_impact=1.345550 m/s`, `U_terminal=0.720415 m/s`, and
`k=76.9112 1/s`. Frames 103 and 155 determine the impact speed; frames 384
and 405 determine the two post-contact constants. The equivalent vacuum
release height is `92.279 mm`. The L7 trajectory errors are at most
`0.216 mm` before contact and `0.0042 mm` after contact. The L8 errors are at
most `0.216 mm` and `0.0037 mm` respectively.

Using outer diameter and impact speed gives `Re=5.390e4`, `We=1007.34`,
`Fr=2.144`, `Bo=219.09`, `Ca=0.01869`, and `Oh=5.888e-4`. These numbers
describe the prescribed-impact scale; they do not validate the contact-line
model.

## Fit and holdout split

Only ring positions in frames 103, 155, 384, and 405 were fitted. The water
shape in frame 405 was not used. Frame 492 supplies the one-time empirical
wetting depth `77.283 mm`; closure timing is consequently not an independent
prediction.

Frames 335, 360, 430, 455, 520, 550, and 620 were selected as morphology
holdouts. They show a continuous sequence: initial crown and open cavity,
appearance and persistence of a thin first jet, cavity taper and separation,
a nearly flat surrounding surface, and onset and growth of the later central
jet. This guards against matching only the three user-labelled event frames.
The approximately `5 deg` rotation toward camera depth and the left bend of
the first jet are recorded as three-dimensional limits and are not fitted by
the axisymmetric calculation.

## Numerical health

The table compares both grids over the same absolute interval ending at
`t=0.2 s`, about 63 ms after contact. The L7 process continued normally to
`0.3 s`; L8 was intentionally stopped after the first-jet window.

| grid | cells through thickness | max budget drift | max lab speed | min dt | cells | deep solid liquid | invalid |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L7 | 3.05 | 0.2085% | 5.387 m/s | 9.091e-6 s | 131,072 | 0 | 0 |
| L8 | 6.10 | 0.2542% | 18.645 m/s | 6.250e-6 s | 524,288 | 0 | 0 |

Both runs exited with status 0 and wrote `final.dump`; no `nan`, `inf`,
`SIGFPE`, segmentation fault, radial outlet water, or deep-solid liquid was
reported. The L8 saved-field peak is `11.5435 m/s` in a full-fluid interface
sample at `z=-36.44 mm`, about `14 mm` above the ring and well below the free
surface. It is not an upward surface jet. L8 therefore repeats the known
refinement-amplified interface/contact-region speed warning.

## Geometry result

At frame 405 (`52.5 ms`), the experiment has a thin, nearly equal-diameter
first jet with reported height `105.80 mm` and a surrounding crown. The L7
connected rise is only `1.436 mm`; L8 is lower at `0.392 mm`. By the end of
the L8 window the rise reaches only `3.831 mm`. L8 makes the attached cavity
walls smoother, but neither grid produces the experimental column.

At frame 492, the experiment shows cavity closure with an hourglass air shape
while the first jet persists. L7 instead has a broad `10.299 mm` central
pedestal and paired corrugated cavity walls extending toward the ring. Its
empirical event is triggered at this depth by construction, so the nominal
time agreement carries no validation weight and the geometry fails.

At frames 520--620, the experiment progresses from a separated ring and
nearly relaxed surface to a thin, prominent later jet. L7 retains fragmented
cavity remnants, broad shoulders, and a short pedestal rising only
`12.210--17.188 mm`. It neither reproduces the mostly flat surrounding surface
nor the narrow later column. `geometry_comparison.tsv` records every target
and holdout verdict.

## Review material

- `experiment_frames/README.md` is the visual laboratory atlas for human
  review. It embeds four overview sheets and links to 15 exact raw frames, 15
  captioned full frames, and five enlarged object/phenomenon callouts.
- `experiment_frames/frame_index.tsv` freezes each selected frame's physical
  time, fitted speed, position/evidence basis, file paths, and hashes.
- `experiment_frames/callout_index.tsv` maps every callout to its exact raw
  frame and hash. The overlays are provisional until project-owner review.
- `review/L7_vs_L8_early_holdout.png` compares L7 and L8 at frames 335, 360,
  and 405.
- `review/L7_holdout_sequence.png` shows all seven L7 holdout times in a fixed
  laboratory frame.
- Additional ignored comparison sheets combining experimental and CFD frames
  are at
  `runs/20260717_213534_12_video_26p15g_calibration/review/video_vs_L7_events.png`
  and `video_vs_L7_holdout.png`; those combined sheets remain local-only.

## Decision

Accept the prescribed trajectory only as a kinematic calibration tool and
accept L8 only as evidence that the cavity wall becomes smoother while the
high-speed instability worsens. Reject both grids as representations of the
observed first jet, hourglass closure, or later jet. Do not tune contact angle,
surface tension, or the empirical trigger to these frames.

The only next recommendation is to replace the one-time wetting scaffold with
a project-owned, license-clear fixed-embed dynamic wetting/detachment closure,
then validate that closure first against the holdout cavity topology before
rerunning the full jet chronology.
