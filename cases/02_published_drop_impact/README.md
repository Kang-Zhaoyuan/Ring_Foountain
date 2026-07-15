# Publication-linked drop impact

The source originates at `references/vendor/DropImpactViscousPool`, commit `c049c42fad7afb9cc49e590b812c386921f7ee0b`, and is MIT-licensed. This case keeps the original source in `source_original.c`, applies only a documented case-local compatibility/headless patch in `source_run.c`, and preserves `LICENSE-MIT`.

The smoke test uses `-grid=quadtree -disable-dimensions`, base `LEVEL=4`, runtime `MAXLEVEL=4`, serial execution, no OpenGL video event, and the original short end time `t=0.25`. `-disable-dimensions` is required because the legacy source's dimensionless `size()` and current `tension.h` checker are incompatible; it disables static unit checking but does not alter the flow equations.

The case retains three-phase VOF, surface tension, adaptivity, pressure/stress logs, energy logs, interface facets, Gerris snapshots, and a final dump. It is a headless smoke test, not a quantitative reproduction of the publication's high-resolution output.
