# Embedded VOF contact-line candidate audit

Audit date: 2026-07-15. This is an evidence-only case. It does not vendor an external contact-line implementation and is not an accepted Ring Fountain simulation. Follow-up long-time author-case reproduction is recorded in `cases/06_author_contact_embed_reproduction/`; it qualifies the short-time interpretation below without changing the final gate decision.

## Search result

The only directly relevant Basilisk implementation found was the ghost-cell VOF method published as:

- `https://basilisk.fr/sandbox/popinet/contact/contact-embed.h`
- `https://basilisk.fr/sandbox/tavares/contact-embed.h`
- Mathilde Tavares et al., *A coupled VOF/embedded boundary method to model two-phase flows on arbitrary solid surfaces*, Computers & Fluids 278 (2024), 106317.

The implementation explicitly reconstructs the VOF interface normal in liquid/gas/solid cut cells and extrapolates the VOF fraction into full-solid ghost cells to impose a prescribed contact angle. It is therefore technically relevant to a fixed embedded contact line. The Tavares page identifies its file as a modified version of the Popinet sandbox header and provides sessile-drop, cylinder, gravity, 3-D, and impact examples.

The candidate does not meet this project's maintenance requirement. Basilisk documentation guarantees maintenance and test-suite compatibility only for `/src`; sandbox content is user-maintained and explicitly not guaranteed. The Tavares README describes the method as under testing, the header ends with `fixme: adaptive mesh`, and the current `sessile_embed.c` page contains calls to undeclared functions rather than a clean standalone test.

Two newer directions were also screened and rejected before use. The 2026 Tianyang sandbox README still labels its header section "To be done", and the 2025/2026 contact-line papers found in the search did not expose a clearly licensed, directly reusable implementation. The MIT-licensed `rcsc-group/BioReactor` repository was inspected at commit `abb083e798862c5814f971506133c64b347c4c59`; it applies `contact_angle()` only on the left/right domain boundaries and does not implement a contact condition on its embedded boundary.

## License review

Neither sandbox `contact-embed.h` file contains an SPDX identifier, copyright notice, or license grant. The 2024 paper is CC BY 4.0, but that publication license does not by itself license separate source files. Basilisk's `/src/COPYING` is GPL-3.0; because the official site distinguishes `/src` from independently contributed sandbox content, this audit does not assume that `/src/COPYING` supplies the missing file-level grant.

Disposition: license is **not sufficiently explicit for copying into this project**. No candidate source, generated executable, or dump from the candidate was copied into the repository. The two headers were downloaded read-only under `/tmp` solely for private compatibility evaluation. Their SHA256 values were:

| candidate | SHA256 |
| --- | --- |
| Popinet sandbox header | `8e8dfba1bdd8497e8480f36ea41a24b3646d518b1eb3eddfd44f089599839c0c` |
| Tavares sandbox header | `eb64fb5398a3247902aa822aae603904f3605f4251c3e1ea903c2f8841f836d1` |

This is an engineering license screen, not legal advice.

## Private qcc compatibility evaluation

A project-authored 2-D canonical probe was compiled outside the repository with `/home/kqdx/basilisk/src/qcc -O2 -Wall`. It used a uniform multigrid, a fixed horizontal embedded wall at `y=0.26`, a radius-0.25 semicircular drop, a prescribed 90-degree angle, no gravity, equal phase densities and viscosities, and unit surface tension. The deliberately offset wall generated true cut cells. Each run ended at `t=0.5` and wrote diagnostics, interface facets, solid facets, and `final.dump` under `/tmp`.

Both the Popinet and Tavares headers compiled without warnings and produced identical results for this 90-degree case.

| level | cells | initial fluid area | initial geometry error | max relative volume drift | max velocity | final velocity | min dt | contact cells | mean contact-normal error | invalid values |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 1,024 | 9.6334583765e-2 | 1.8743987e-2 | 9.4687708e-4 | 1.9191984e-2 | 2.5904474e-3 | 8.0140566e-4 | 4 | 0 | 0 |
| 6 | 4,096 | 9.7685220533e-2 | 4.9865142e-3 | 1.0498139e-3 | 3.4153956e-2 | 3.8283601e-3 | 2.8333969e-4 | 2 | 0 | 0 |
| 7 | 16,384 | 9.8046426594e-2 | 1.3072995e-3 | 7.7078635e-4 | 3.2668973e-2 | 8.4098333e-3 | 1.0017571e-4 | 4 | 0 | 0 |

The analytical semicircle area is `pi*0.25^2/2 = 9.8174770425e-2`. Geometry error decreases under refinement, all runs complete, no `nan`, `inf`, `SIGFPE`, or segmentation fault occurs, and the reconstructed contact normal matches the imposed 90-degree angle in detected contact cells.

As a short-time screen, the result flags non-monotone volume drift and a terminal velocity increase from `2.5904474e-3` at level 5 to `8.4098333e-3` at level 7. Ghost-cell liquid values are intentional boundary-condition data and were not mislabeled as physical leakage. After reading the paper, `t=0.5` is not treated as an equilibrium endpoint: the author's static cases relax to `T=15` or `T=20`. The broader long-time, multi-angle result in case 06 is the controlling numerical decision.

## Decision

The candidate route remains rejected for Ring Fountain use. It is neither clearly licensed for project inclusion nor maintained in the official Basilisk source. Case 06 confirms useful moderate-angle behavior but fails the broader multi-angle refinement gate. The ring free-surface case remains blocked and no moving-ring work is permitted.
