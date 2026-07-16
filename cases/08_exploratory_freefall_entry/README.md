# Exploratory free-fall ring entry

Run date: 2026-07-16. Status: **the L6/L7 comparison and an uninterrupted deep-domain L7 run to 530 ms are complete; the result remains qualitative and does not produce a credible Worthington jet**.

## Scope and interpretation

This case replaces prescribed translation with one-degree-of-freedom, force-coupled vertical rigid-body motion. The ring remains horizontal and has the validated rectangular meridional section `Ri=2.5 mm`, `Ro=15 mm`, and `h=4 mm`. Its density is the user-confirmed `7.8 g/cm^3 = 7800 kg/m^3`, giving a volume of `2.7488935718910665e-6 m^3`, mass of `0.02144136986075032 kg`, and weight of `0.21033983833396064 N`.

The geometry is still a fixed embedded boundary in a frame accelerating with the ring. The model integrates the ring's laboratory position and speed, transforms fluid velocity back to the laboratory frame, and adds the corresponding fictitious frame acceleration. It is not a moving-cut-cell implementation. This preserves the previously tested fixed contact geometry but does not validate moving-embed conservation.

The lower ring face starts `50.9684 mm` above the undisturbed water surface. In vacuum this gives `U=sqrt(2 g H)=1 m/s` at first contact. The main contact angle remains the uncalibrated 75 deg engineering assumption. No experimental splash height or timing was used to tune this run.

## Force and frame model

The official Cartesian `embed_force()` does not include the axisymmetric `2*pi*r` area factor. The private project source therefore integrates pressure and viscous traction over each embedded segment with area `2*pi*r*ds`. Because `reduced.h` stores reduced pressure, physical pressure at the embedded barycentre is reconstructed from the local phase density and hydrostatic reference before integration.

With upward axial coordinate `x` and positive ring speed downward,

```text
a_down = g - F_fluid_up/m_ring
u_lab,x = u_frame,x - U_ring
```

The accelerating frame receives a uniform fictitious acceleration `+a_down` in the axial equation. A separate air-only gate reproduces analytical free fall before contact, and a submerged hydrostatic gate reproduces buoyancy under refinement.

The force presently omits an explicit solid contact-line capillary line reaction. Its simple upper-bound scale, `2*pi*sigma*(Ri + Ro)`, is about `0.008 N`, or four percent of ring weight. This and the uncalibrated contact angle preclude quantitative force validation.

## Numerical route

The solver uses uniform multigrid, axisymmetry, fixed embed, centered two-phase VOF, physical water/air density and viscosity, surface tension, gravity, and the privately isolated Tavares fixed embedded contact-line header. Quadtree remains rejected because the viscous AXI+EMBED probe receives `SIGFPE` and the external contact implementation does not support AMR reliably.

The main 330 ms domain is `600 x 120 mm`. Its axial origin is `-150 mm` in ring coordinates, giving about `97 mm` of initial water below the undisturbed surface and `450 mm` above the ring. L6 and L7 have `Delta=1.875` and `0.9375 mm`. The L7 sequence is the main visual branch; L6 is only a topology and grid-sensitivity control because the 4 mm ring thickness spans about 2.1 L6 cells.

The longer-domain implementation uses a `16:1` rectangular multigrid domain, `1920 x 120 mm`, with axial origin `-300 mm`. It provides about `247 mm` of initial water depth and `1.673 m` of initial laboratory-frame headroom. The power-of-two aspect ratio also avoids the current Basilisk multigrid `restore()` depth failure observed for a `15:1` rectangle, although dump restart was ultimately rejected after a separate continuity regression.

## Diagnostics

Axisymmetric water volume is integrated as `2*pi*integral(f*dv())`; `dv()` already contains the `cm=y*cs` metric, so multiplying by `cs` again would double-count cut-cell volume. The translating frame has a lower liquid inlet, so conservation is the residual against initial water plus `pi*R_domain^2*ring_drop`.

Intentional contact-method liquid in a thin solid ghost layer is reported separately. Only liquid in full-solid cells more than `2.5 Delta` inside the ring is classified as deep-solid leakage.

Every complete run records water-budget residual, ghost and deep-solid liquid, frame and laboratory speed maxima, minimum timestep, cell count, invalid values, first wetting, fluid force, radial outlet water, interface facets, checkpoints, and final dump. Laboratory coordinates use

```text
z_lab = x_ring_frame + z_ring_center_lab
```

## Completed 330 ms comparison

Both levels complete without `nan`, `inf`, `SIGFPE`, segmentation fault, deep-solid liquid, or radial outlet water. The user manually identifies the late central upward structure as a first-jet candidate surrounded by an annular cavity. This classification is retained as manual morphology, not as an automatic mechanism label.

| grid | completion | final drop / speed | max water residual | max lab speed | deep leakage | cells | result |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| L6 | 330 ms | 449.740 mm / 2.531 m/s | 0.6909% | 10.056 m/s | 0 | 20,480 | coarse control; fragmented cavity wall |
| L7 | 330 ms | 464.619 mm / 2.609 m/s | 0.3078% | 11.282 m/s | 0 | 81,920 | main qualitative branch |

At 322--324 ms, the sampled L7 speed-field peak is about `8.9 m/s` in a full-fluid interface cell at laboratory position approximately `z=-0.26 m`, `r=6 mm`, on the long open cavity wall. The sampled cut-cell peak near the ring is about `3.5 m/s`. The global diagnostic maximum of `11.282 m/s` is therefore associated with the late open-cavity interface rather than a resolved cut-cell jet.

The two grids agree on the broad sequence through the central upward structure and surrounding open annular cavity. They do not agree on detailed cavity-wall breakup: L6 develops substantially more fragments after roughly 200 ms. Neither level shows cavity closure by 330 ms.

Current manual-review images:

- `review/L6-L7_surface_110-330ms.png`: fixed laboratory-surface comparison; neither grid is claimed to be more realistic.
- `review/L7_lab_track_100-330ms.png`: fixed laboratory-coordinate ring trajectory and full connected cavity.
- `review/L7_surface_100-330ms.png`: L7 surface/cavity detail through 330 ms.
- `review/L6_deep_surface_330-530ms.png`: coarse deep-domain scout; no coherent closure by 530 ms and substantial cavity-wall fragmentation.

## Deep-domain extension to 530 ms

The final level-7 extension was rerun from `t=0` after a host power loss and completed as one uninterrupted `systemd --user` process. No pre-shutdown dump was stitched into the accepted result. Both deep-domain grids complete without `nan`, `inf`, `SIGFPE`, segmentation fault, deep-solid liquid, or radial outlet water.

| grid | completion | final drop / speed | max water residual | max lab speed | force range | deep leakage | cells | morphology |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| L6 | 530 ms | 1092.831 mm / 3.821 m/s | 0.5434% | 12.462 m/s | -0.0312 to 0.1506 N | 0 | 65,536 | no closure; strongly fragmented cavity wall |
| L7 | 530 ms | 1118.686 mm / 3.973 m/s | 0.2356% | 22.629 m/s | -0.1176 to 0.4688 N | 0 | 262,144 | no closure; persistent cavity, late corrugation and detached fragments |

L7 has the smaller water-budget residual and preserves a more coherent long cavity than L6, but this does not establish that L7 is physically more accurate. From roughly 390 ms onward it develops increasing interface corrugation, isolated droplets, large force oscillations, and a global laboratory-speed maximum of `22.629 m/s`. The user-requested central first-jet candidate remains visible near the free surface, but the surrounding gas cavity does not close into a flat surface by 530 ms. No later structure is classified as a credible Worthington jet.

The saved `2 ms` field samples in `speed_peak_samples.tsv` localize the rising high-speed path away from the embedded cut cells. At 458--464 ms, sampled maxima of `13.55--15.20 m/s` occur in full-fluid interface cells about `38 mm` above the ring at `r` near `4 mm`; sampled cut-cell maxima are about `6.5--7.4 m/s`. By 500 ms the sampled full-liquid maximum is `15.96 m/s` about `76 mm` above the ring. Contact-region force oscillations occur at the same late stage, so the evidence is consistent with a cavity/contact reconstruction disturbance propagating into the resolved fluid, not simply a single bad cut cell.

The initial impact-scale values at `U=1 m/s` and outer diameter `D=30 mm` are `Re=29940`, `We=415.83`, `Fr=1.843`, `Bo=122.38`, `Ca=0.01389`, and `Oh=6.81e-4`. These are reference scales only; the computed ring accelerates after impact and reaches `3.973 m/s` at 530 ms.

## Laboratory-frame animation

`tools/render_lab_speed.sh` and `tools/render_lab_speed.gp` form a reproducible rendering path from `fields.tsv`, sampled field files, and interface facets. The animation uses a fixed laboratory coordinate system, mirrors the axisymmetric half-plane, draws the integrated ring position, and colors water speed with one fixed `0--10 m/s` scale. Values above `10 m/s` saturate red rather than rescaling each frame. The full-window border is a plotting window, not a claim that the open numerical boundaries are literal tank walls.

Review outputs:

- `review/L7_deep_surface_330-530ms.png`: late L7 interface sequence.
- `review/L7_lab_speed_000-528ms.mp4`: 265 computed frames at 2 ms spacing, encoded at 25 fps with a one-second final hold.
- `review/L7_lab_speed_audit_112-528ms.png`: decoded-video audit at 112, 330, 460, and 528 ms.

The MP4 was decoded after encoding and verified as H.264, `1600 x 1000`, 25 fps, 290 frames, and 11.6 s. Its SHA256 is `9282f72e5f13dc05b803a67b08709f3502c7c99c7e7736c9d88a7fc177805ecd`.

## Restart and toolchain evidence

The current qcc invocation is sensitive to path layout: compiling from the private source directory with `-I../frozen` succeeds without warnings, while an absolute `-I` combined with a relative source path caused qcc itself to receive `SIGSEGV`. The successful source-directory invocation remains authoritative.

Two restart limitations were tested rather than assumed:

1. Basilisk multigrid `restore()` rejects a `15:1` rectangular dump with `grid depths do not match`; the official rectangle test uses a power-of-two aspect ratio.
2. A `16:1` dump can be read after reconstructing fixed `cs/fs/cm/fm`, but a direct 12 ms run and a 10-to-12 ms restart differ immediately. The restart produces a spurious `0.064 N` pressure impulse and about `0.20 m/s` disturbance. Dump continuation is therefore rejected for physical results.

Long runs use one uninterrupted process managed by local `systemd --user`, not stitched restart segments. The final L7 530 ms run reports service result `success`, exit status 0, 12,694 timesteps, about 69 minutes wall time, and maximum resident memory about 83.7 MiB.

## License boundary

The external contact header remains unlicensed evaluation material outside the tracked case. Its frozen SHA256 is `eb64fb5398a3247902aa822aae603904f3605f4251c3e1ea903c2f8841f836d1`. No external source, private project source, executable, or copied implementation is included here.

## Current conclusion

The accelerating-frame free-fall route is accepted only as a constrained qualitative exploration. It successfully moves the ring in laboratory coordinates, couples a computed fluid force to vertical ring acceleration, and produces the manually identified first-jet candidate with an annular cavity. It has not demonstrated cavity closure or a credible Worthington jet, and it is not a quantitative prediction of real metal wetting, force, jet timing, or jet height.

The single next recommendation is to compare this frozen L7 baseline, including ring trajectory and interface chronology, against the forthcoming blinded experiment before changing release height. The ring already reaches nearly `4 m/s`; increasing drop height now would add energy to a branch whose late cavity/contact behavior is numerically suspect and would not isolate the cause of the missing closure.

## Subsequent experimental constraint

The later 10 cm-release experiment reports that the ring becomes completely
surrounded by water rather than carrying an attached cavity to large depth.
Case `09_release10cm_cavity_detachment` demonstrates that this case-08 route
does not reproduce that topology even after changing the release height. The
case-08 L7 result is therefore retained as historical evidence of model
failure, not as the branch for later prediction.
