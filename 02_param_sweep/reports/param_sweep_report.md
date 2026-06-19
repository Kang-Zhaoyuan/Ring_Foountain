# Parameter Sweep Report

Run time: 2026-06-17T12:41:59

Saved sweep model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\02_param_sweep\models\ring_fountain_v1_param_sweep.mph`.
Saved timestamped model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\02_param_sweep\models\ring_fountain_v1_param_sweep_20260617_123632.mph`.
Planned one-dimensional sweep points: 11.
Successful solves: 11.
This remains a single-phase fixed-ring model and does not compute a true fountain height.

## Structured Data

```json
{
  "sweep_plan": [
    [
      "U0",
      "0.01[m/s]",
      "U0_sweep"
    ],
    [
      "U0",
      "0.02[m/s]",
      "U0_sweep"
    ],
    [
      "U0",
      "0.05[m/s]",
      "U0_sweep"
    ],
    [
      "U0",
      "0.10[m/s]",
      "U0_sweep"
    ],
    [
      "h_ring",
      "1[mm]",
      "h_ring_sweep"
    ],
    [
      "h_ring",
      "2[mm]",
      "h_ring_sweep"
    ],
    [
      "h_ring",
      "4[mm]",
      "h_ring_sweep"
    ],
    [
      "Ri",
      "0.3*Ro",
      "Ri_Ro_sweep"
    ],
    [
      "Ri",
      "0.4*Ro",
      "Ri_Ro_sweep"
    ],
    [
      "Ri",
      "0.5*Ro",
      "Ri_Ro_sweep"
    ],
    [
      "Ri",
      "0.6*Ro",
      "Ri_Ro_sweep"
    ]
  ],
  "rows": [
    {
      "group": "U0_sweep",
      "parameter": "U0",
      "value": "0.01[m/s]",
      "solve_status": "ok",
      "u_max_maxop": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 8\r\n",
      "u_max_max": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Function called with wrong number of arguments.\r\nMessages:\r\n\tFunction called with wrong number of arguments.\r\n\t- Function name: max\r\n\t- Number of arguments used: 1\r\n\t- Number of arguments expected: 2\r\n\t- Feature: Evaluation 9\r\n",
      "p_max_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 10\r\n",
      "p_max_spf_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 11\r\n",
      "vz_max_v": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 12\r\n",
      "vz_max_w": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 13\r\n",
      "u_max_field": 0.04155219620920075,
      "p_max_field": 303350.5628194233,
      "p_max_spf_field": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 14\r\n",
      "vz_max_v_field": 0.0,
      "vz_max_w_field": 0.03910605371959097,
      "U0": "0.01[m/s]",
      "Ro": "20[mm]",
      "Ri": "8[mm]",
      "Ri/Ro": "see Ri and Ro expressions",
      "h_ring": "2[mm]"
    },
    {
      "group": "U0_sweep",
      "parameter": "U0",
      "value": "0.02[m/s]",
      "solve_status": "ok",
      "u_max_maxop": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 15\r\n",
      "u_max_max": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Function called with wrong number of arguments.\r\nMessages:\r\n\tFunction called with wrong number of arguments.\r\n\t- Function name: max\r\n\t- Number of arguments used: 1\r\n\t- Number of arguments expected: 2\r\n\t- Feature: Evaluation 16\r\n",
      "p_max_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 17\r\n",
      "p_max_spf_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 18\r\n",
      "vz_max_v": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 19\r\n",
      "vz_max_w": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 20\r\n",
      "u_max_field": 0.0679017194449792,
      "p_max_field": 606700.6894202254,
      "p_max_spf_field": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 21\r\n",
      "vz_max_v_field": 0.0,
      "vz_max_w_field": 0.06414448455102804,
      "U0": "0.02[m/s]",
      "Ro": "20[mm]",
      "Ri": "8[mm]",
      "Ri/Ro": "see Ri and Ro expressions",
      "h_ring": "2[mm]"
    },
    {
      "group": "U0_sweep",
      "parameter": "U0",
      "value": "0.05[m/s]",
      "solve_status": "ok",
      "u_max_maxop": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 22\r\n",
      "u_max_max": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Function called with wrong number of arguments.\r\nMessages:\r\n\tFunction called with wrong number of arguments.\r\n\t- Function name: max\r\n\t- Number of arguments used: 1\r\n\t- Number of arguments expected: 2\r\n\t- Feature: Evaluation 23\r\n",
      "p_max_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 24\r\n",
      "p_max_spf_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 25\r\n",
      "vz_max_v": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 26\r\n",
      "vz_max_w": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 27\r\n",
      "u_max_field": 0.15455714210574548,
      "p_max_field": 1516731.4729773216,
      "p_max_spf_field": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 28\r\n",
      "vz_max_v_field": 0.0,
      "vz_max_w_field": 0.15455054356783307,
      "U0": "0.05[m/s]",
      "Ro": "20[mm]",
      "Ri": "8[mm]",
      "Ri/Ro": "see Ri and Ro expressions",
      "h_ring": "2[mm]"
    },
    {
      "group": "U0_sweep",
      "parameter": "U0",
      "value": "0.10[m/s]",
      "solve_status": "ok",
      "u_max_maxop": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 29\r\n",
      "u_max_max": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Function called with wrong number of arguments.\r\nMessages:\r\n\tFunction called with wrong number of arguments.\r\n\t- Function name: max\r\n\t- Number of arguments used: 1\r\n\t- Number of arguments expected: 2\r\n\t- Feature: Evaluation 30\r\n",
      "p_max_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 31\r\n",
      "p_max_spf_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 32\r\n",
      "vz_max_v": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 33\r\n",
      "vz_max_w": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 34\r\n",
      "u_max_field": 0.3093352780740281,
      "p_max_field": 3033323.1890210197,
      "p_max_spf_field": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 35\r\n",
      "vz_max_v_field": 0.0,
      "vz_max_w_field": 0.3093281588891502,
      "U0": "0.10[m/s]",
      "Ro": "20[mm]",
      "Ri": "8[mm]",
      "Ri/Ro": "see Ri and Ro expressions",
      "h_ring": "2[mm]"
    },
    {
      "group": "h_ring_sweep",
      "parameter": "h_ring",
      "value": "1[mm]",
      "solve_status": "ok",
      "u_max_maxop": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 36\r\n",
      "u_max_max": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Function called with wrong number of arguments.\r\nMessages:\r\n\tFunction called with wrong number of arguments.\r\n\t- Function name: max\r\n\t- Number of arguments used: 1\r\n\t- Number of arguments expected: 2\r\n\t- Feature: Evaluation 37\r\n",
      "p_max_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 38\r\n",
      "p_max_spf_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 39\r\n",
      "vz_max_v": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 40\r\n",
      "vz_max_w": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 41\r\n",
      "u_max_field": 0.31200385155064797,
      "p_max_field": 3032735.355830053,
      "p_max_spf_field": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 42\r\n",
      "vz_max_v_field": 0.0,
      "vz_max_w_field": 0.3114490700813717,
      "U0": "0.10[m/s]",
      "Ro": "20[mm]",
      "Ri": "8[mm]",
      "Ri/Ro": "see Ri and Ro expressions",
      "h_ring": "1[mm]"
    },
    {
      "group": "h_ring_sweep",
      "parameter": "h_ring",
      "value": "2[mm]",
      "solve_status": "ok",
      "u_max_maxop": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 43\r\n",
      "u_max_max": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Function called with wrong number of arguments.\r\nMessages:\r\n\tFunction called with wrong number of arguments.\r\n\t- Function name: max\r\n\t- Number of arguments used: 1\r\n\t- Number of arguments expected: 2\r\n\t- Feature: Evaluation 44\r\n",
      "p_max_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 45\r\n",
      "p_max_spf_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 46\r\n",
      "vz_max_v": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 47\r\n",
      "vz_max_w": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 48\r\n",
      "u_max_field": 0.3093352780735367,
      "p_max_field": 3033323.1890212125,
      "p_max_spf_field": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 49\r\n",
      "vz_max_v_field": 0.0,
      "vz_max_w_field": 0.30932815888865833,
      "U0": "0.10[m/s]",
      "Ro": "20[mm]",
      "Ri": "8[mm]",
      "Ri/Ro": "see Ri and Ro expressions",
      "h_ring": "2[mm]"
    },
    {
      "group": "h_ring_sweep",
      "parameter": "h_ring",
      "value": "4[mm]",
      "solve_status": "ok",
      "u_max_maxop": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 50\r\n",
      "u_max_max": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Function called with wrong number of arguments.\r\nMessages:\r\n\tFunction called with wrong number of arguments.\r\n\t- Function name: max\r\n\t- Number of arguments used: 1\r\n\t- Number of arguments expected: 2\r\n\t- Feature: Evaluation 51\r\n",
      "p_max_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 52\r\n",
      "p_max_spf_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 53\r\n",
      "vz_max_v": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 54\r\n",
      "vz_max_w": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 55\r\n",
      "u_max_field": 0.2721046932177755,
      "p_max_field": 3031953.6984160305,
      "p_max_spf_field": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 56\r\n",
      "vz_max_v_field": 0.0,
      "vz_max_w_field": 0.26585204135884016,
      "U0": "0.10[m/s]",
      "Ro": "20[mm]",
      "Ri": "8[mm]",
      "Ri/Ro": "see Ri and Ro expressions",
      "h_ring": "4[mm]"
    },
    {
      "group": "Ri_Ro_sweep",
      "parameter": "Ri",
      "value": "0.3*Ro",
      "solve_status": "ok",
      "u_max_maxop": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 57\r\n",
      "u_max_max": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Function called with wrong number of arguments.\r\nMessages:\r\n\tFunction called with wrong number of arguments.\r\n\t- Function name: max\r\n\t- Number of arguments used: 1\r\n\t- Number of arguments expected: 2\r\n\t- Feature: Evaluation 58\r\n",
      "p_max_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 59\r\n",
      "p_max_spf_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 60\r\n",
      "vz_max_v": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 61\r\n",
      "vz_max_w": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 62\r\n",
      "u_max_field": 0.3056771574805851,
      "p_max_field": 3048662.5814777617,
      "p_max_spf_field": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 63\r\n",
      "vz_max_v_field": 0.0,
      "vz_max_w_field": 0.30551598477779013,
      "U0": "0.10[m/s]",
      "Ro": "20[mm]",
      "Ri": "0.3*Ro",
      "Ri/Ro": "see Ri and Ro expressions",
      "h_ring": "4[mm]"
    },
    {
      "group": "Ri_Ro_sweep",
      "parameter": "Ri",
      "value": "0.4*Ro",
      "solve_status": "ok",
      "u_max_maxop": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 64\r\n",
      "u_max_max": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Function called with wrong number of arguments.\r\nMessages:\r\n\tFunction called with wrong number of arguments.\r\n\t- Function name: max\r\n\t- Number of arguments used: 1\r\n\t- Number of arguments expected: 2\r\n\t- Feature: Evaluation 65\r\n",
      "p_max_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 66\r\n",
      "p_max_spf_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 67\r\n",
      "vz_max_v": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 68\r\n",
      "vz_max_w": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 69\r\n",
      "u_max_field": 0.27210469321778197,
      "p_max_field": 3031953.6984159593,
      "p_max_spf_field": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 70\r\n",
      "vz_max_v_field": 0.0,
      "vz_max_w_field": 0.2658520413588503,
      "U0": "0.10[m/s]",
      "Ro": "20[mm]",
      "Ri": "0.4*Ro",
      "Ri/Ro": "see Ri and Ro expressions",
      "h_ring": "4[mm]"
    },
    {
      "group": "Ri_Ro_sweep",
      "parameter": "Ri",
      "value": "0.5*Ro",
      "solve_status": "ok",
      "u_max_maxop": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 71\r\n",
      "u_max_max": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Function called with wrong number of arguments.\r\nMessages:\r\n\tFunction called with wrong number of arguments.\r\n\t- Function name: max\r\n\t- Number of arguments used: 1\r\n\t- Number of arguments expected: 2\r\n\t- Feature: Evaluation 72\r\n",
      "p_max_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 73\r\n",
      "p_max_spf_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 74\r\n",
      "vz_max_v": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 75\r\n",
      "vz_max_w": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 76\r\n",
      "u_max_field": 0.271832125793387,
      "p_max_field": 3048521.850001046,
      "p_max_spf_field": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 77\r\n",
      "vz_max_v_field": 0.0,
      "vz_max_w_field": 0.2653254461601563,
      "U0": "0.10[m/s]",
      "Ro": "20[mm]",
      "Ri": "0.5*Ro",
      "Ri/Ro": "see Ri and Ro expressions",
      "h_ring": "4[mm]"
    },
    {
      "group": "Ri_Ro_sweep",
      "parameter": "Ri",
      "value": "0.6*Ro",
      "solve_status": "ok",
      "u_max_maxop": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 78\r\n",
      "u_max_max": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Function called with wrong number of arguments.\r\nMessages:\r\n\tFunction called with wrong number of arguments.\r\n\t- Function name: max\r\n\t- Number of arguments used: 1\r\n\t- Number of arguments expected: 2\r\n\t- Feature: Evaluation 79\r\n",
      "p_max_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 80\r\n",
      "p_max_spf_p": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 81\r\n",
      "vz_max_v": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 82\r\n",
      "vz_max_w": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 83\r\n",
      "u_max_field": 0.27085305791643244,
      "p_max_field": 3028096.10908914,
      "p_max_spf_field": "failed: Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 84\r\n",
      "vz_max_v_field": 0.0,
      "vz_max_w_field": 0.26459684241178,
      "U0": "0.10[m/s]",
      "Ro": "20[mm]",
      "Ri": "0.6*Ro",
      "Ri/Ro": "see Ri and Ro expressions",
      "h_ring": "4[mm]"
    }
  ],
  "exports": [
    {
      "kind": "plot",
      "node": "Velocity (spf)",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\images\\param_sweep_Velocity__spf_.png",
      "ok": true,
      "value": "created Image2D export",
      "created_export": "img_Velocity__spf_3"
    },
    {
      "kind": "plot",
      "node": "Pressure (spf)",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\images\\param_sweep_Pressure__spf_.png",
      "ok": true,
      "value": "created Image2D export",
      "created_export": "img_Pressure__spf_3"
    },
    {
      "kind": "plot",
      "node": "Velocity, 3D (spf)",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\images\\param_sweep_Velocity__3D__spf_.png",
      "ok": true,
      "value": "created Image3D export",
      "created_export": "img_Velocity__3D__spf_3"
    },
    {
      "kind": "plot",
      "node": "3D Plot Group 4",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\images\\param_sweep_3D_Plot_Group_4.png",
      "ok": true,
      "value": "created Image3D export",
      "created_export": "img_3D_Plot_Group_43"
    },
    {
      "kind": "export",
      "node": "Image 1",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\tables\\param_sweep_Image_1.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 1a",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\tables\\param_sweep_Image_1a.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 1b",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\tables\\param_sweep_Image_1b.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 41",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\tables\\param_sweep_Image_41.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 2",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\tables\\param_sweep_Image_2.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 2a",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\tables\\param_sweep_Image_2a.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 2b",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\tables\\param_sweep_Image_2b.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 42",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\tables\\param_sweep_Image_42.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 3",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\tables\\param_sweep_Image_3.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 3a",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\tables\\param_sweep_Image_3a.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 3b",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\tables\\param_sweep_Image_3b.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 43",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_param_sweep\\tables\\param_sweep_Image_43.txt",
      "ok": true,
      "value": null
    }
  ]
}
```
