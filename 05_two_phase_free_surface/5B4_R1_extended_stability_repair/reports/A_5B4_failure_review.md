# A 5B4 Failure Review

Run ID: `20260618_225535`

- `5B4 = FAIL`.
- `E extended stability solve_status = PASS`.
- `E extended stability case_pass = FAIL`.
- `E diagnostic H(final)-H(0) = 0.0002340315 m`.
- `ALLOW_5C = NO`.
- `ALLOW_STAGE6 = NO`.

## H(t) Audit

- Rows: `201`.
- Original diagnostic delta: `0.0002340314889688338` m.
- Max single-step H jump: `0.000124261838429175` m.
- Interface point count range: `11..17`.
- Max interface point jump: `1`.
- near_top ever true: `False`.
- Discrete-step behavior likely: `True`.

The original table indicates a step-like diagnostic change rather than a smooth monotonic displacement.