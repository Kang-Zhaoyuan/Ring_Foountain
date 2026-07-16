# Exploratory constant-speed ring entry

Run date: 2026-07-16. Status: **completed as a constrained exploration; visually useful at level 7, but grid, cut-cell phase, and contact-line convergence all remain unresolved**.

## Model and scope

The ring is fixed in a Galilean frame while both phases and the initially flat free surface enter upward at `U=1 m/s`. This is kinematically equivalent to a horizontal ring descending at a prescribed constant speed. The axisymmetric meridional coordinates are `x` vertical and `y >= 0` radial, with `bottom` as the axis. The rectangular section is `Ri=2.5 mm`, `Ro=15 mm`, and `h=4 mm`.

The isolated model uses current Basilisk `axi`, fixed `embed`, centered two-phase VOF, water/air density and viscosity, surface tension, reduced gravity, and the Tavares fixed embedded contact-line ghost-cell header. The main prescribed angle is 75 deg. It is an uncalibrated engineering assumption, not a measured metal wetting property or dynamic contact-angle law. The 90 deg run is only a short sensitivity comparison.

This stage explores first entry, crown development, cavity evolution, and upward interface motion. It does not include free fall, moving embed, force coupling, a parameter sweep, or a quantitative prediction of jet height. The output is not used to assign mechanisms or names to separate upward events automatically; in particular, no frame is labeled a Worthington jet without experimental and manual morphological review.

## License and source boundary

The Tavares header remains unlicensed evaluation material outside the repository. Its frozen private SHA256 is `eb64fb5398a3247902aa822aae603904f3605f4251c3e1ea903c2f8841f836d1`. No external source, executable, or copied implementation is tracked or archived as a project dependency.

The project-authored private source hashes are:

| variant | SHA256 |
| --- | --- |
| initial 60 mm square | `09a000ff157b5b4e23b429e0451f7682b473d28530406747d48c0d52c5d72a19` |
| 120 x 60 mm extended domain | `de20804e7f2ed5532b5de075130e868355f78406c45531cc75225903df38102f` |
| 180 x 60 mm long domain | `8f5dadad3c5555e6dc0431b9d6d8689a6a4a4b8d47e0da6dee7232b0337ba904` |
| free-slip diagnostic control | `7feeefbd3c1bceeddd16a0221a3b05ecf8aa0f39fa4a1e3e93d9c1a7a57dcd26` |
| level-7 axial half-cell phase control | `dae868fa9a167180228a680a3ed25abf2ef74643610df3728e0ded41d033078d` |

## Grid and domain decisions

The first `grid/quadtree.h` build succeeded with `/home/kqdx/basilisk/src/qcc`, but the viscous level-6 smoke run received `SIGFPE` at iteration zero. GDB placed the first invalid radial velocity in `residual_diffusion()` at `/home/kqdx/basilisk/src/viscosity-embed.h:116`. The same quadtree setup reached 5 ms with zero viscosity, while a viscous `grid/multigrid.h` control reached 5 ms. The external header also marks adaptive mesh support as a fixme. Quadtree is therefore rejected for this exploration; no Basilisk source was modified.

Uniform levels 7 and 8 have cell widths 0.46875 and 0.234375 mm. The initial square domain was sufficient only for the short 28 ms study. The main comparison uses a 120 x 60 mm domain (`256 x 128` cells at level 7 and `512 x 256` at level 8). The level-7 continuation uses a 180 x 60 mm domain (`384 x 128` cells) and reaches 120 ms without outlet liquid.

The ring is no-slip in the main branch. A free-slip embedded-wall run changes only the tangential velocity condition and is diagnostic, not an adopted metal-wall model. A second level-7 control translates the axial domain by half a level-7 cell while preserving the physical ring and free-surface coordinates; it tests cut-cell phase sensitivity without changing `Delta`.

## Parameters and diagnostics

The initial surface is at `x=-6 mm`, 4 mm below the lower ring face. Water enters at the lower axial boundary, gas leaves at the upper axial boundary, and the outer radial boundary is slip. With `D=30 mm`, the prescribed-speed groups are `Re_D=29940`, `We_D=415.833`, `Fr_D=1.84334`, `Bo_D=122.380`, `Ca=0.0138889`, and `Oh_D=6.81095e-4`.

The translating-frame domain is open. The water metric is the relative residual against `V_expected=V_initial+pi*R_domain^2*U*t`; no water reached the upper outlet. Physical water is integrated as `2*pi*integral(f*cs*r dr dx)`. The contact method intentionally writes VOF into a thin full-solid ghost layer. `ghost liquid` records that numerical layer, while `deep-solid liquid` counts only full-solid cells more than `2.5 Delta` inside the ring and is the leakage indicator.

| run | max budget residual | deep-solid liquid | max frame/lab speed (m/s) | min dt (s) | cells | invalid | result |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 75 deg, L7, extended, 60 ms | 1.8564% | 0 | 3.830 / 2.831 | 9.091e-6 | 32,768 | 0 | complete; main visual branch |
| 75 deg, L8, extended, 60 ms | 3.5939% | 0 | 18.280 / 17.311 | 6.201e-6 | 131,072 | 0 | complete; near-wall speed worsens |
| 75 deg, L7, long, 120 ms | 1.8183% | 0 | 7.301 / 6.593 | 9.091e-6 | 49,152 | 0 | complete; late peak is a ring cut cell |
| 90 deg, L7, square, 12 ms | 1.0712% | 0 | 1.659 / 0.659 | 9.091e-6 | 16,384 | 0 | complete; short comparison |
| 75 deg, free-slip L7, 30 ms | 1.7815% | 0 | 3.604 / 2.612 | 9.091e-6 | 32,768 | 0 | diagnostic control |
| 75 deg, free-slip L8, 30 ms | 2.2935% | 0 | 6.385 / 5.966 | 5.669e-6 | 131,072 | 0 | diagnostic control; still worsens |
| 75 deg, shifted-phase L7, 30 ms | 2.6719% | 0 | 2.244 / 1.355 | 9.091e-6 | 32,768 | 0 | diagnostic control; morphology changes |

Full run rows are in `run_summary.tsv`; the focused 0--30 ms diagnosis is in `grid_boundary_comparison.tsv`.

## L8 diagnosis and L7 priority

At level 7, the 60 ms maximum lab-frame speed is 2.831 m/s at 28.21 ms in a full-fluid free-interface cell (`x=2.578 mm`, `r=6.328 mm`). At level 8, the speed grows after about 12 ms and reaches 17.311 m/s at 43.49 ms in liquid on the lower embedded face (`x=-1.992 mm`, `r=3.867 mm`, `cs=0.467`). Contact-cell counts and positions also jump. The refined-grid peak is therefore not a resolved free jet.

Changing the embedded tangential condition from no-slip to free-slip reduces the level-8 0--30 ms peak from 11.807 to 5.966 m/s, but the free-slip L8 value remains 2.28 times its L7 counterpart and its water-budget residual still worsens. The strongest free-slip L8 velocity moves to a full-liquid cell about one L8 cell from the inner edge, while the cut/interface peak remains on the ring. Wall treatment affects the amplification but does not remove it.

The contact header reconstructs prescribed-angle normals and writes VOF values into neighboring `cs=0` ghost cells. It contains a special fallback when the solid is mesh-aligned and explicitly leaves adaptive meshes unresolved. Combining that discretization with a moving no-slip contact line and differently cut ring faces is consistent with the observed near-wall amplification, propagation into adjacent fluid, and non-monotonic mass residual. This is evidence for a combined contact-line/cut-cell sensitivity, not proof of a single cause.

The axial half-cell level-7 control reinforces the caution: through 16 ms its bulk interface is close to the base run, but the cavity paths diverge strongly from 20 to 30 ms. Its maximum lab speed falls to 1.355 m/s while its mass residual rises to 2.672%. Thus the visually preferred base L7 result is also grid-phase dependent. It is retained as the main qualitative branch because the user judged its 4--60 ms sequence consistent with the expected early process, not because it is demonstrably more converged.

No uncalibrated Navier length is introduced. The available external `embed-navier.h` is unlicensed experimental material with hard-coded/debug paths and is not a reliable optimization route. Free-slip is likewise not substituted for metal-wall physics.

## Visual observations

The user manually accepted the base L7 4--60 ms sequence as qualitatively consistent with the expected crown and early first-upward-event development. The 75 and 90 deg L7 interfaces nearly coincide at 4, 8, and 12 ms, so the early bulk shape is not highly sensitive to that moderate angle change on this grid.

The long L7 sequence reaches 120 ms. In the translated-surface view, the main surface becomes progressively flatter outside the axial region while detached interface fragments remain below it and a central deformation persists. This is recorded only as morphology. The plots do not establish cavity closure, a Worthington mechanism, or a jet height automatically, and the later sequence still awaits explicit manual classification against the experiment.

Review images:

- `review/75deg_L7_004-060ms.png`: manually accepted base L7 early sequence.
- `review/75deg_L8_004-060ms.png`: refined-grid qualitative contrast.
- `review/75deg_L7_050-120ms.png`: long-domain laboratory-coordinate sequence.
- `review/75deg_L7_surface_050-120ms.png`: translated free-surface view, with no height detector.
- `review/75deg-vs-90deg_L7_004-012ms.png`: short angle comparison.
- `review/grid_boundary_speed_000-030ms.png`: grid, wall, and phase velocity histories.
- `review/L7_grid_phase_004-030ms.png`: base and half-cell-shifted L7 interfaces.

## Evidence and decision

The original 176-file evidence set is retained in `runs/20260716_113000_07_exploratory_constant_speed_entry/`. The extended follow-up contains 932 archived files before its manifest, including interface facets every 0.5 ms, solid facets, diagnostics, contact positions, checkpoints, final dumps, compiler logs, failure evidence, review plots, and its archive note. It is retained in `runs/20260716_121500_07_extended_entry_followup/` with a relative SHA256 manifest. Neither archive contains the private source, executable, or external header.

Decision: continue the base no-slip L7 branch only for explicitly qualitative, manually reviewed morphology. Stop extending L8 and reject free-slip or a fabricated slip length as an optimization. The L7 visual agreement is useful but does not overcome its demonstrated grid-phase and late cut-cell sensitivity.

The only next recommendation is to manually classify the existing base L7 50--120 ms sequence against the laboratory chronology before running a denser L7 time window around any identified cavity-closure interval.
