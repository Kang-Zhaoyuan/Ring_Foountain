# ADR-002: Fixed ring and translating frame

Status: proposed default for the first dynamic model

The first moving-ring experiment will keep the embedded annular geometry fixed and formulate constant ring speed through a translating Galilean reference frame. This keeps the cut-cell topology stable while retaining axisymmetric VOF and adaptive mesh refinement. A true moving embedded boundary remains an isolated experimental branch. Acceleration, pressure-force integration, and contact-line behavior must be validated before extending to variable-speed motion.

The static geometry gate completed without fluid physics. It does not authorize a moving ring or a free-surface case; those remain the next explicitly gated stages.
