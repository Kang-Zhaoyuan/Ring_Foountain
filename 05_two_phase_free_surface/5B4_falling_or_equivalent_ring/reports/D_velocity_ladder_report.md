# D Velocity Ladder Report

- This is a stability-increment ladder, not a parameter sweep.
- All successful cases use the same `WettedWall utr = {0,-Vwall_eff(t),0}` route.
- No Inlet, Outlet, or OpenBoundary route is used to impersonate ring motion.
- Diagnostic `H(t)` is a free-surface smoke-test quantity, not real Hmax.

## Cases

- D1: Vtarget `1e-3[m/s]`, solve `PASS`, case `PASS`, diagnostic delta `6.846528986234649e-05` m, interface `clear`.
- D2: Vtarget `2e-3[m/s]`, solve `PASS`, case `PASS`, diagnostic delta `6.846528986234649e-05` m, interface `clear`.
- D3: Vtarget `5e-3[m/s]`, solve `PASS`, case `PASS`, diagnostic delta `6.846528986234649e-05` m, interface `clear`.
- D4: Vtarget `1e-2[m/s]`, solve `PASS`, case `PASS`, diagnostic delta `6.846528986234649e-05` m, interface `clear`.