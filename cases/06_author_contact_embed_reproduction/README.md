# Tavares embedded contact-line reproduction

Reproduction date: 2026-07-15. This is an evidence-only case. It does not vendor, relicense, or accept the external implementation, and it does not return to the Ring Fountain geometry.

## Paper and method

The user-supplied PDF is Mathilde Tavares et al., *A coupled VOF/embedded boundary method to model two-phase flows on arbitrary solid surfaces*, Computers & Fluids 278 (2024), 106317. Its SHA256 is `3f0c22ec21dc9d659cf23cac299a4417ed8f49feae489e8213ab845c8d525b31`. The publication is CC BY 4.0; the PDF was read in place and was not copied into the project.

The method reconstructs the prescribed contact-angle normal in three-phase cells and extrapolates the reconstructed VOF plane into full-solid ghost cells within a two-cell neighborhood. For VOF advection in mixed cells, the paper deliberately ignores the solid volume fraction. The authors interpret this as a porous numerical layer thinner than the grid size, expect at most first-order convergence, and report local mass absorption up to about 5% in severe small-angle configurations. They also report contact-line pinning for unfavorable cut-cell/grid alignments, non-monotonic sessile-shape errors under refinement, and special-treatment limits near angles below 10 degrees or above 170 degrees. Dynamic grid convergence requires a resolved Navier slip length; this round tests only static relaxation and does not adopt a wetting law for metal.

## Frozen public source

The complete public Tavares directory listed by the sandbox, plus the Popinet predecessor header, was downloaded to the ignored directories `references/vendor/basilisk-tavares-20260715/` and `references/vendor/basilisk-popinet-contact-20260715/`. All 13 files are mode `0444`. URLs, byte counts, SHA256 values, fetch time, and license observations are frozen in `references/contact_embed_sources.lock`.

No downloaded source file contains an SPDX identifier, copyright notice, or license grant. The paper's CC BY 4.0 notice does not license separate code by itself. The source therefore remains private, read-only evaluation material and is not present in this case directory. This is an engineering license screen, not legal advice.

The page history also demonstrates source-version drift. The current contact header's latest recorded fix is 2024-05-15. The current 2-D sessile page was restored after deletion in October 2024 and its May 2025 include-path fix has the maintainer message `Fixed header file, but still broken` (patch `9e6e11129f828f90cf796523ba2369f5c6d3812a`). The latest 2025 cylinder change only alters its movie.

## Exact-source qcc screen

`/home/kqdx/basilisk/src/qcc -c -O2 -Wall` was run from an isolated copy with original file hashes. The detailed result is in `compile_matrix.tsv`. Four contact-line cases and the Navier-slip case generated objects; the gravity case emitted two possible-uninitialized warnings and `slip.c` one format warning. The current 2-D sessile page failed because it redefines `tag` from the header and calls undeclared `triple_cell_dectection()` and `fraction_reconstruction()`. The slot page requests the nonexistent `../contact_embed.h` spelling.

The exact cylinder source also reached the native link step. It could not link because this WSL Basilisk installation has no built `libglutils`/framebuffer library required by `view.h`. An isolated headless copy removed only `view.h` and the movie event. That copy compiled without warnings and ran all five author angles at `N=64`, producing the same author summary format. No physics setting was changed.

## Instrumented cylinder reproduction

The headless cylinder copy was then instrumented outside the repository. The author geometry, phase properties, contact angles, uniform grids, convergence event, and `T=15` were preserved. The additions only select level/angle from the command line and record total and physical liquid volume, ghost-cell liquid, velocity, `dt`, cells, invalid values, facets, and dumps. The private patch SHA256 is `9ae3795c7a8ef5a9fa00b1f6d73c2dcf6ef069108eec410d592da86aca7d4e93`.

All nine selected runs completed with no invalid numerical marker. The 90-degree case relaxed well at every level. The extreme angles did not provide a general refinement pass: at 30 degrees the total-volume drift fell from 4.99% to 1.29%, but final velocity rose from `9.96e-4` to `2.31e-2`, and the final curvature standard deviation worsened to 2.96 at `N=128`. Full values are in `cylinder_validation.tsv`.

## Ported flat sessile reproduction

The broken public sessile page was ported only in `/tmp`: the conflicting local `tag` was removed, the prescribed scalar `contact_angle` API from the current header was set before each run, and the obsolete custom contact event was disabled. Final curvature and the same diagnostics were added. Geometry and physical parameters match the author's horizontal embedded-wall case, and every run reached the paper's `T=20`. The private patch SHA256 is `8f2a648b66be47d179889d8916187edf4468ea51fe9a9bdbb5296a4bc4d3fd93`.

All nine runs completed without invalid markers and produced interfaces, solid facets, and final dumps. The 75-degree runs decayed to negligible final velocity. The route still fails a general three-level gate: the 45-degree relative radius error increased from 1.58% to 3.99%, its maximum total-volume drift increased from 3.24% to 3.42%, and the 120-degree drift and terminal velocity were non-monotonic. These observations agree with the paper's warning that sessile-shape convergence can be non-monotonic. Full values are in `sessile_validation.tsv`.

## Evidence and decision

The 147 generated files, including step diagnostics, interfaces, embedded boundaries, `final.dump` files, compiler logs, and author-format output, are retained locally under `runs/20260715_233000_06_author_contact_embed_reproduction/`. The private source copies and patches remain under `/tmp` and are not project dependencies.

Decision: the paper materially advances understanding and confirms that the ghost-cell route is compatible with current qcc for useful moderate-angle configurations. It does not establish a maintained, license-clear, generally grid-convergent dependency. The fixed embedded VOF contact-line gate remains blocked, and no axisymmetric ring, AMR ring, or moving-ring case is attempted.
