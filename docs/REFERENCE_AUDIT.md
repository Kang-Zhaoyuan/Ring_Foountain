# Reference audit

Audit date: 2026-07-15. Repository metadata below reflects the locked fetch performed on 2026-07-14. GitHub statistics are community signals only and are not used as a technical acceptance criterion. The installed Basilisk source and official tests remain the compatibility authority.

## Trust tiers

| Tier | Sources | Use |
| --- | --- | --- |
| A | Installed `/home/kqdx/basilisk/src`, official tests and headers | API, coordinate conventions, and numerical compatibility |
| B | `rcsc-group/DropImpactViscousPool`, `AndreWeiner/phd_basilisk` | Publication-linked physics and reproducible engineering patterns |
| C | `comphy-lab/Drop-Impact`, reviewed Basilisk sandbox pages | Structure, diagnostics, and experimental comparisons only |

## Repository records

| Repository | URL / branch / locked commit | Stars / forks / commits | Last commit | License | Ring Fountain disposition |
| --- | --- | ---: | --- | --- | --- |
| DropImpactViscousPool | https://github.com/rcsc-group/DropImpactViscousPool.git / `main` / `c049c42fad7afb9cc49e590b812c386921f7ee0b` | 9 / 2 / 23 | 2022-10-27 | MIT (`LICENSE`) | B-tier primary impact reference; wrapper or attribution-preserving copy only |
| phd_basilisk | https://github.com/AndreWeiner/phd_basilisk.git / `master` / `0dff5b4df4483cb20cd0883a587344f19f048bc8` | 21 / 12 / 7 | 2020-03-04 | GPL-3.0 (`LICENSE`) | B-tier architecture and rising-bubble comparison; no source copied |
| Drop-Impact | https://github.com/comphy-lab/Drop-Impact.git / `main` / `ff46c945513367ab3422d81963c39dd11cc2de54` | 1 / 0 / 147 | 2026-07-14 | GPL-3.0 (`LICENSE`) | C-tier current structure and diagnostics; no source copied |

The full lock record, including license SHA256 values, is in `references/references.lock`. All three vendor worktrees were clean at audit time. The vendor directory is ignored and remains independent from this project.

## Detailed assessment

### DropImpactViscousPool

The README provides a Basilisk build command, command-line nondimensional parameters, an example shell runner, and output categories for pressure, stresses, energies, interfaces, and performance. The main source is `code/3phasedroponpoolexample.c`; the three-phase headers are local to the repository. The MIT license permits a case-local attribution-preserving copy if needed. Numerical risks are the custom three-phase VOF API, visual-library dependencies, and version drift against the installed Basilisk. The first reproduction must be serial, headless, low-level, and short.

### phd_basilisk

The README links the work to a 2020 PhD thesis and describes an axisymmetric rising-bubble solver, containerized reproducibility, and diagnostic outputs. The repository is GPL-3.0, so its solver source is reference-only for this project unless a compatible project-license decision is made. Risks include its historical Basilisk/Docker toolchain and MPI/container assumptions.

### Drop-Impact

The README documents an axisymmetric VOF drop-impact code, adaptive refinement, parameter files, serial/MPI runners, and post-processing. It also instructs users to install a separately pinned Basilisk release. The repository is GPL-3.0 and therefore reference-only here. The current commit is a generated search-database update; implementation history and the separate Basilisk pin must be treated cautiously. Risks include release/API mismatch, MPI dependencies, and the fact that its high-resolution workflow is not appropriate for this smoke-test gate.

### Embedded VOF contact-line candidates

The Popinet and Tavares sandbox `contact-embed.h` files explicitly implement a prescribed VOF contact angle on fixed embedded boundaries using reconstructed interface normals and solid ghost-cell fractions. They are technically relevant and are linked to the 2024 Tavares et al. Computers & Fluids paper. They are not accepted dependencies: neither file contains a license notice, the CC BY 4.0 paper license does not establish a code license, and the official Basilisk GPL-3.0 file is under `/src` while the website describes sandbox contributions as independently maintained and unsupported. The Tavares code is also marked under testing with an adaptive-mesh fixme.

The MIT-licensed `rcsc-group/BioReactor` repository was locked for inspection at `abb083e798862c5814f971506133c64b347c4c59`. It combines two-phase VOF, surface tension, and fixed embedded geometry, but its optional contact-angle condition is applied only to ordinary left/right domain boundaries. It is not an embedded contact-line implementation and no source was copied.

Private `/tmp` qcc probes of the Popinet and Tavares headers are documented in `cases/05_contact_embed_candidate_audit/`. Their short `t=0.5` result initially flagged worsening terminal velocity under refinement. Reading and reproducing the paper showed that this short run was not a sufficient equilibrium test, so it is retained as preliminary evidence rather than the final numerical decision.

The user-supplied 2024 paper hash and all 13 files in the public Tavares/Popinet implementation and test listing were subsequently frozen by origin, byte count, and SHA256 in `references/contact_embed_sources.lock`; the source snapshots are ignored, read-only vendor material. Current qcc object compilation passes for the cylinder, gravity, 3-D sessile, fiber-impact, and Navier-slip files, but the current 2-D sessile page and slot page are broken. The Basilisk page history explicitly labels the May 2025 sessile include fix `Fixed header file, but still broken`.

Two static validation families were run at three uniform levels and three angles each. Moderate 75- and 90-degree configurations can relax cleanly, but the general refinement gate fails: extreme cylinder angles retain grid-dependent velocity/curvature, and the horizontal sessile radius error and volume drift are non-monotonic or worsening for some angles. This is consistent with limitations stated in the paper, including mixed-cell mass absorption and contact-line pinning. Full evidence is in `cases/06_author_contact_embed_reproduction/` and `runs/20260715_233000_06_author_contact_embed_reproduction/`.

## Official Basilisk sources

The installed official files used by this project are `/home/kqdx/basilisk/src/test/missing_metric.c`, `/home/kqdx/basilisk/src/test/missing_metric.ref`, `/home/kqdx/basilisk/src/test/rising.c`, and the axisymmetric references under `/home/kqdx/basilisk/src/test/rising-axi*`. They are read-only inputs; no vendor copy is modified.

## License decision

No GPL or unlicensed sandbox source has been copied into the tracked project. Unlicensed sandbox snapshots are confined to ignored, read-only vendor storage. The copied official test sources are retained as validation fixtures, with their origins recorded in the case READMEs. The MIT publication case has been copied case-locally into `cases/02_published_drop_impact/`, with `LICENSE-MIT` preserved and the compatibility edits documented in the case README.
