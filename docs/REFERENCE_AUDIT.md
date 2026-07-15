# Reference audit

Audit date: 2026-07-14. GitHub statistics are community signals only and are not used as a technical acceptance criterion. The installed Basilisk source and official tests remain the compatibility authority.

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

## Official Basilisk sources

The installed official files used by this project are `/home/kqdx/basilisk/src/test/missing_metric.c`, `/home/kqdx/basilisk/src/test/missing_metric.ref`, `/home/kqdx/basilisk/src/test/rising.c`, and the axisymmetric references under `/home/kqdx/basilisk/src/test/rising-axi*`. They are read-only inputs; no vendor copy is modified.

## License decision

No GPL source has been copied into the project. The only copied official test source is from the local Basilisk installation and is retained as an unmodified validation fixture, with its origin recorded in the case README. The MIT publication case remains in the ignored vendor tree until the required wrapper and attribution are reviewed.

