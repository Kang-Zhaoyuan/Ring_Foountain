# Open questions

1. Approve or reject an approximately 86-minute L11 run. L12 short-window cost
   is estimated at 6.48 hours; the unchanged L12 `tmax=1.5` run is optimistically
   estimated at 13.89 hours.
2. Is the robust outer-surface shoulder from `getBase` the intended manuscript
   jet radius for the plain solver? `getJetFoot`'s lowest/maximum-curvature
   candidates do not match it in these runs, so `Q_j` is deliberately `NA`.
3. The first `f>1e-4` liquid-component split is transient at L10 (`t=0.46`)
   before the coherent jet event (`t=0.51`). Should production topology events
   include a minimum component volume/lifetime threshold?
4. L8 and L10 disagree strongly in jet onset, height, KE, interface distance,
   and local velocity. Does the plain fixed-maximum-level solver cross the
   focus singularity reliably at L11/L12, or should scientific work use the
   separately validated drill solver and its pre-inception cap?
5. `getBase` and `getJetFoot` use fixed-size 80-byte filename buffers. Should
   upstream accept a path-length hardening patch? This audit worked around it
   only by passing short relative paths.
6. Bond currently selects `Bo%5.4f.dat` and is absent from the momentum
   equation. Should future dynamic-gravity studies add and validate an actual
   acceleration term, with a separate experiment from initial-shape response?
7. The default run starts Stage 2 from a Stage-1 state already evolved to
   `t=0.1`. Is that intentional for every production comparison, and should
   Stage-1 cost/output be reported separately from Stage 2?
