# ADR-002: Fixed ring and translating frame

Status: accepted only for constrained constant-speed exploration

The first ring-entry experiment keeps the embedded annular geometry fixed and formulates constant ring speed through a translating Galilean reference frame. This keeps the cut-cell topology fixed and supports axisymmetric VOF. The present viscous `AXI + TREE + EMBED` route raises `SIGFPE`, and the external contact header leaves adaptation unresolved, so the accepted exploration uses uniform multigrid only. A true moving embedded boundary remains a separate experimental branch. Acceleration, pressure-force integration, and contact-line behavior must be validated before extending to variable-speed motion.

The static geometry gate completed without fluid physics. A later user-authorized exploration reached 120 ms at uniform level 7, but level-8 velocity amplification and level-7 half-cell phase sensitivity prevent quantitative acceptance. This ADR authorizes only the fixed-frame, prescribed-speed qualitative branch; it does not authorize free fall, moving embed, or fluid-structure coupling.
