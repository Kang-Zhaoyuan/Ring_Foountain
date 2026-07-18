# Independent CoMPhy Drop-Impact reproduction audit

This case archives the evidence created during an independent, read-only
reproduction of CoMPhy Lab's Drop-Impact repository on 2026-07-18. It is a
method and evidence baseline for later Ring Fountain work; it is not a ring
simulation and does not change the current ring-physics validation gate.

## Outcome

Status: **PARTIAL**. The minimum reproduction gate passed; the scientific gate
did not.

- Drop-Impact was detached at
  `9fd0db798ec5a05f8410886231bdfbe30fac051d`.
- An isolated Basilisk `v2026-01-13` installation was used. The main project's
  `/home/kqdx/basilisk/src` tree was not used or changed.
- The unchanged default solver compiled without Drop-Impact warnings.
- Identical L8 smoke cases 1808/1809 produced byte-identical scalar logs and
  byte-identical PLIC facets at the compared time.
- The We=20 control spread farther than We=10 at later common times.
- L10/L11/L12 completed to solver time `tU/R=0.316228` with no invalid dump
  values. L11-to-L12 changes were 0.000604% in final volume, about 0.41--0.46%
  in common-time kinetic energy, and 0.0761% in the short-window footprint.
- Maximum snapshot velocity changed by 27.59% from L11 to L12, and the
  footprint was still growing at the last snapshot. Local extrema and true
  maximum spreading are therefore not converged.
- The estimated short L14 cost is about 21.7 hours. The unchanged default L14
  horizon is estimated at about nine days and 6.5--23.5 GB, so it was not
  started without explicit resource approval.

The detailed interpretation is in
[`REPRODUCTION_REPORT.md`](REPRODUCTION_REPORT.md). Open physics and workflow
questions are in [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md).

## What is tracked here

- `params/`: six parameter copies created specifically for smoke, response,
  and short L10--L12 runs.
- `logs/`: complete captured install, compile, run, post-process, dependency,
  failure, and status evidence. Zero-byte stdout logs are retained where the
  corresponding status file records the result.
- `tables/`: newly derived repeatability, parameter-response, volume, energy,
  footprint, interface-distance, AMR, timing, warning, and resource tables.
- `figures/`: newly generated PLIC interface data and review plots.
- `tools/`: two audit sources created in this work round; no executable is
  tracked. The Python tool has a case-local optional dependency lock.
- `commands.log` and `environment.txt`: the complete independent execution
  recipe and frozen environment.
- `external_run_checksums.sha256`: the original 691-entry manifest. It refers
  to the external independent clone and is retained as historical evidence;
  it is not expected to verify in a fresh Ring Fountain checkout.
- `artifact_manifest.sha256`: hashes only files tracked in this case and is the
  manifest intended to verify after clone.

## Deliberate exclusions

No file pulled from the CoMPhy GitHub repository is duplicated here. In
particular this case contains no Drop-Impact solver source, upstream script,
upstream post-processing source, upstream Git object, GPL license text,
Basilisk source/install, binary, object file, restart, intermediate dump, MP4,
virtual environment, or installed Python package. The ignored
`references/vendor/` area is not part of this case and is not required to read
or verify the tracked evidence.

These boundaries are itemized in [`LICENSE_BOUNDARY.md`](LICENSE_BOUNDARY.md)
and [`migration_log.tsv`](migration_log.tsv).

## Verification

From the repository root:

```sh
sha256sum -c cases/13_comphy_drop_impact_reproduction/artifact_manifest.sha256
git diff --check
```

The numerical audit tools can be rerun only when the independent pinned clone
and its isolated Basilisk still exist. See [`tools/README.md`](tools/README.md).
The tracked evidence itself does not require third-party Python packages to
inspect.

## Coordinate and reuse warning

Pinned Basilisk `axi.h` uses axial `x`, radial `y`, and `y=0` as the symmetry
axis. Several upstream comments reverse this convention even though the actual
drop motion and wall locations are mostly consistent. Ring Fountain may reuse
the audit method and metric definitions, but it must not reuse the GPL solver,
the solid-wall `f[left]=0` assumption, or drop-radius-based nondimensional
numbers without a separate license and physics decision.
