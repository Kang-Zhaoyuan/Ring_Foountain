# CoMPhy Bursting-Bubble independent reproduction report

> Migration note (2026-07-18): this report and its project-created audit
> evidence are archived in Ring Fountain case 14. Paths beginning with
> `upstream/` or `report/capsule_work/` still refer to the independent external
> workspace `/home/kqdx/basilisk_work/reproductions/bursting_bubble_20260718`,
> not to vendored content in this repository. No external GPL source, Basilisk
> install, binary, dump, restart, virtual environment, or capsule payload was
> migrated.

Date: 2026-07-18 (Asia/Shanghai)

Pinned upstream: `fb6090bf287afa5bd8c238272a95df27b9bcec4d`

Pinned Basilisk: `v2026-01-13`, installed under `upstream/basilisk/src`

## Conclusion

The three independent acceptance results are:

| Gate | Status | Conclusion |
|---|---|---|
| A. Capsule reproduction | **PASS** | 211/211 payload hashes, frozen Python environment, primary Fig. 2 generation, and 7/7 offline frozen regressions passed. |
| B. Minimum solver reproduction | **PASS** | Unchanged plain solver compiled; three L8 and one L10 two-stage runs completed; repeatability and Oh response were demonstrated with dump metrics and PLIC. |
| C. Scientific jet baseline | **PARTIAL** | L8 and L10 show a jet but disagree strongly. Estimated L11 cost exceeds the 60-minute gate, so the required L10/L11/L12 convergence series was not completed. |

Thus the capsule can be reproduced offline and the default **plain solver
source** can repeatedly produce cavity collapse and a central jet at reduced
resolution. The unchanged full default L12, `tmax=1.5` case was not run, and no
scientific grid-convergence claim is supported.

## 1. Boundaries and frozen sources

Ring Fountain was checked read only and remained at the expected
`ed903d56101332309651d8decc51831e3596570d`; its branch status remained clean.
The frozen Drop-Impact directory was not used or modified. Bursting-Bubble is a
detached checkout at the requested commit; `git diff --exit-code` still passes.

The installer SHA-256 is `72bb2460...e9aa`; independent qcc SHA-256 is
`a44e1d1f...315c`. `.project_config` resolves both `BASILISK` and qcc under this
worktree, never under `/home/kqdx/basilisk/src`. The applied lock patch is
`2026-01-13-mpi-tree-dump-header-fix.patch`. Full paths and hashes are in
`source_lock.tsv` and the raw platform record is in `environment.txt`.

## 2. Capsule reproduction versus local solving

Offline capsule reproduction used already archived L13--L15 logs, fields,
facets, figures, and provenance. None of those expensive HPC simulations was
rerun locally. Details and renderer limitations are in `CAPSULE_REPORT.md`.

Local solving used only the unchanged current
`simulationCases/burstingBubble.c` (SHA-256 `5d0f9ea8...1afd5`), not the paper's
archived `burstingBubble-drillResolution.c`. Every local case source copy is
byte-identical to that plain solver.

The three solver families must not be conflated:

- the local plain solver uses wavelet AMR with a fixed maximum level;
- adaptive/drill variants contain additional diagnostics and, for the drill,
  a dynamically varying local maximum plus singular-focus safeguards;
- paper L13--L15 results came from the archived drill solver at commit
  `e35ebdc...22b1` on HPC hardware.

The many `drill*` keys in `default.params` are parsed into the shared parameter
structure but never consumed by the plain solver used here.

## 3. Physics and implementation audit

Basilisk AXI uses `x` as axial `z`, `y` as radial `r`, and `y=0` as the
symmetry axis. `f=1` is liquid and `f=0` is gas. The default liquid/gas
densities are 1 and `10^-3`; surface tension is 1; liquid viscosity is `Oh`
and gas viscosity is `OhRatio*Oh`. Therefore solver time is the capillary time
scale `sqrt(rho R^3/sigma)` under the code's `rho=R=sigma=1` normalization.

The initial interface is loaded from `simulationCases/DataFiles/Bo0.0010.dat`
for the requested `Bond=0.001`. A `Bo0.0000.dat` file also exists. `Bond` is
used only to format that filename. There is no acceleration/gravity event or
body-force term in the plain, adaptive, or drill solver search results.
Changing Bond would select a precomputed initial geometry; it would not test a
dynamic gravity response.

`zWall=4` gives `L0=min(zWall+6,16)=10`, origin `(-6,0)`, and a no-slip liquid
wall on the left boundary. `tmax` and `tsnap` are capillary-time values. Stage
1 evolves serially to `t=0.1` to create `restart`; Stage 2 restores it and
continues to the requested horizon.

## 4. Default compilation

`./runSimulation.sh --verbose --compile-only default.params` exited 0 in
16.94 s with no solver warning. It created the documented CaseNo 1000 side
effect and compiled Stage 1 with the effective command:

```text
/home/kqdx/basilisk_work/reproductions/bursting_bubble_20260718/upstream/basilisk/src/qcc \
  -O2 -Wall -disable-dimensions -I../../src-local burstingBubble.c \
  -o burstingBubble -lm
```

The Case 1000 parameter/source copies have exactly the upstream hashes.
Compile-only stops after the Stage-1 target; the Stage-2 serial command uses
the same source and flags. Tracked upstream diff remains clean.

## 5. Minimum solver reproduction

Cases 2808 and 2809 are identical L8 inputs; Case 2820 changes only
`Oh=0.02`. All use `Bond=0.001`, `zWall=4`, and `tmax=0.7`. Both stages exited
0, each final restart is non-empty, and each case has 70 non-empty snapshots.
No NaN, Inf, signal, segmentation fault, KE gate, or solver warning occurred.

Repeatability is stronger than the requested tolerance: 2808/2809 have
byte-identical 678-row scalar logs, exact equality of every extracted scalar
and geometry metric, and byte-identical main-body PLIC at `t=0.50, 0.58, 0.64,
0.69`. Binary dump equality was not required.

The event definition was frozen before extracting snapshot geometry. It uses
face-connected `f>10^-4` liquid, the largest component as the main pool,
`r<=2 Delta_min` for the central tip, free-surface zero `z=0`, and first jet
when `H>max(0.02,2 Delta_min)` with a continuous outer base wider than
`2 Delta_min`. Full details are in `tools/METRIC_DEFINITIONS.md`.

At L8, Oh=0.01 issues the first coherent jet at `t=0.58`; Oh=0.02 issues it at
`t=0.60`. At `t=0.60`, connected height changes from 0.3862 to 0.1076. The
lower-Oh case first splits into multiple liquid components at stored time
0.64, while the higher-Oh case has no split by 0.69. This is a plausible
viscous delay/damping response, but only a low-resolution functional test.

## 6. Dump audit and jet observables

Every stored dump was restored independently. Tables contain axisymmetric
liquid volume, KE, maximum speed and location, leaves, minimum Delta, cavity
base, all-liquid top, main-connected top, central-connected top, numerical tip
speed, and liquid component count. Solver logs supply the true minimum dt.

The audit helper initially exposed and then corrected a post-processing density
default (`rho2=1` instead of solver `10^-3`); all formal tables and figures were
regenerated with `rho2=10^-3`. The correction and both compile logs are kept.

Upstream `getBase` was usable after passing short relative paths. Upstream
`getJetFoot` candidates did not coincide with that robust outer-surface base in
these plain-solver dumps, so reporting its flux as the requested base flux
would be misleading. `q_jet`, `q_l`, and `Q_j` are therefore explicitly `NA`,
not silently substituted.

## 7. Grid evidence and resource gate

The common window was frozen at `0<=t<=0.7` from the L8 event. L10 Case 2810
completed in 1139.61 s (18:59.61), used 240.2 MB, reached 45,130 leaf cells,
and had minimum solver dt `1.56525e-6`. KE peaked smoothly near the focus and
then declined; the run exited 0.

L8 versus L10 is not converged:

| metric | L8 | L10 | observation |
|---|---:|---:|---|
| jet event time | 0.58 | 0.51 | raw shift -0.07 |
| H at t=0.60 | 0.3862 | 1.3616 | +252.6% |
| H at t=0.69 | 0.7205 | 2.3917 | +231.9% |
| outer-base radius at t=0.60 | 0.4492 | 0.3955 | -12.0% |
| KE at t=0.60 | 3.7835 | 5.1639 | +36.5% |
| max local speed | 151.35 | 68.23 | -54.9%; non-monotone/unresolved |
| max relative liquid-volume drift | `8.81e-8` | `6.10e-7` | both small, but not decreasing |

Point-set PLIC endpoint Hausdorff distances are 0.688, 1.200, 1.372, and
1.677 R at the four common times. The large distances reflect genuinely
different jet timing/length, not sub-cell agreement.

The measured L8-to-L10 runtime ratio is 20.48 across two level increments,
giving a per-level factor 4.525. It estimates L11 at 5157 s (85.95 min) and
L12 at 23,337 s (6.48 h); both estimated disk sizes stay below 20 GB, but time
alone triggers the mandatory pause. The unchanged L12 `tmax=1.5` run is
optimistically estimated at 50,008 s (13.89 h, 2.53 GB), so it was not started.
Exact pending commands are:

```bash
cd /home/kqdx/basilisk_work/reproductions/bursting_bubble_20260718/upstream
source .project_config
./runSimulation.sh ../report/params/grid_l11.params
./runSimulation.sh ../report/params/grid_l12.params
./runSimulation.sh default.params
```

No pending command should be run without explicit resource approval and a
fresh check that its CaseNo directory does not already exist.

## 8. Implications for Ring Fountain

Methods suitable for migration are source/tag/installer locking, isolated
toolchains, unique CaseNo values, two-stage status capture, read-only dump
audits, a priori event definitions, connected-component exclusion of detached
drops, common-time PLIC comparison, and measured resource gates.

Not suitable for automatic migration are the GPL solver/post-processing code,
the plain solver's wall and bubble geometry, its liquid/gas property ratios,
the absence of dynamic gravity, its capillary nondimensionalization, the L8 or
L10 numerical results, and the paper drill solver's singularity safeguards.

Recommendation: **do not yet enter a minimum Ring Fountain physics model on
the strength of this scientific baseline.** The external code is operational
and the capsule is sound, but the local jet observables are not grid converged.
Proceed only with method migration after deciding whether to fund L11/L12 or
adopt a separately validated, licence-compatible singular-focus strategy.

## 9. Evidence index

- Commands from the independent run: `commands.log`; migration decisions:
  `migration_log.tsv` and `MIGRATION_NOTES.md`
- Environment and hashes: `environment.txt`, `source_lock.tsv`
- Capsule: `CAPSULE_REPORT.md`, `tables/capsule_*`
- Repeatability and response: `tables/repeatability.tsv`,
  `tables/parameter_response.tsv`
- Grid/resource evidence: `tables/grid_convergence.tsv`,
  `tables/resource_estimates.tsv`, `tables/interface_distances.tsv`
- Full time metrics: `tables/jet_metrics.tsv`, `tables/case*_*.tsv`
- Failures and gates: `tables/warnings_and_failures.tsv`
- Required figures: `figures/common_time_interfaces.png`,
  `jet_height_vs_time.png`, `jet_speed_vs_time.png`,
  `cavity_and_jet_events.png`, `volume_conservation.png`, `grid_cost.png`
