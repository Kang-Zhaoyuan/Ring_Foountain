# Stage 2.1 Metric Calibration Report

Run time: 2026-06-17T18:18:52

## Review

Stage 2.1 review status: `PASS`.

## Variable Confirmation

- Velocity magnitude: `spf.U`.
- Pressure: `p`.
- Vertical/axial velocity: `w`.
- Previous `v = 0` issue is resolved by selecting the nonzero axisymmetric axial component; in this model `w` is the meaningful vertical/axial velocity when available.

## Metric Definitions

- `u_mag_max`: COMSOL full-domain maximum of velocity magnitude.
- `p_max_global`: COMSOL full-domain maximum pressure.
- `p_max_ring_near`: coordinate-masked maximum pressure in a ring-near box, without boundary-ID guessing.
- `vz_max_center_above`: coordinate-masked maximum axial velocity above the center hole.
- `vz_avg_hole_above`: coordinate-masked average axial velocity above the center hole.
- `Q_axisym_hole_above`: `NA`; a reliable 2*pi*r weighted line integration was not implemented in this stage.

## Next Gate

Proceed to stage 2.2 only if this review is `PASS`.

## Structured Data

```json
{
  "stage": "2.1",
  "parameter_descriptions": [
    {
      "parameter": "Ro",
      "status": "ok",
      "description": "Outer radius of the ring."
    },
    {
      "parameter": "Ri",
      "status": "ok",
      "description": "Inner radius of the ring opening."
    },
    {
      "parameter": "Rtank",
      "status": "ok",
      "description": "Radius of the axisymmetric computational water domain."
    },
    {
      "parameter": "Zup",
      "status": "ok",
      "description": "Water-domain height above the ring center plane."
    },
    {
      "parameter": "Zdown",
      "status": "ok",
      "description": "Water-domain height below the ring center plane."
    },
    {
      "parameter": "U0",
      "status": "ok",
      "description": "Relative incoming velocity in the fixed-ring single-phase model."
    },
    {
      "parameter": "rho_w",
      "status": "ok",
      "description": "Water density."
    },
    {
      "parameter": "mu_w",
      "status": "ok",
      "description": "Water dynamic viscosity."
    },
    {
      "parameter": "h_ring",
      "status": "ok",
      "description": "Ring cross-section thickness in the simplified model."
    }
  ],
  "coupling_operators": [
    {
      "tag": "rfmax_all",
      "type": "Maximum",
      "status": "ok",
      "selection": "all domains"
    },
    {
      "tag": "rfavg_all",
      "type": "Average",
      "status": "ok",
      "selection": "all domains"
    },
    {
      "tag": "rfint_all",
      "type": "Integration",
      "status": "ok",
      "selection": "all domains"
    }
  ],
  "variable_probe": {
    "chosen": {
      "velocity_magnitude": "spf.U",
      "pressure": "p",
      "radial_velocity": "u",
      "axial_velocity": "w",
      "radial_coordinate": "r",
      "axial_coordinate": "z"
    },
    "details": {
      "velocity_magnitude": [
        {
          "expression": "spf.U",
          "unit": "m/s",
          "status": "ok",
          "min": 0.0,
          "max": 0.06790171944503055,
          "max_abs": 0.06790171944503055,
          "sample_count": 302787
        },
        {
          "expression": "U",
          "unit": "m/s",
          "status": "failed",
          "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: U\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: U\r\n\t- Feature: Evaluation 8\r\n"
        }
      ],
      "pressure": [
        {
          "expression": "p",
          "unit": "Pa",
          "status": "ok",
          "min": -21747.616740776775,
          "max": 606700.6894202387,
          "max_abs": 606700.6894202387,
          "sample_count": 302787
        },
        {
          "expression": "spf.p",
          "unit": "Pa",
          "status": "failed",
          "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 9\r\n"
        }
      ],
      "radial_velocity": [
        {
          "expression": "u",
          "unit": "m/s",
          "status": "ok",
          "min": -0.05326013731077028,
          "max": 0.05014918188174994,
          "max_abs": 0.05326013731077028,
          "sample_count": 302787
        },
        {
          "expression": "spf.u",
          "unit": "m/s",
          "status": "failed",
          "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.u\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.u\r\n\t- Feature: Evaluation 10\r\n"
        }
      ],
      "axial_velocity": [
        {
          "expression": "w",
          "unit": "m/s",
          "status": "ok",
          "min": -0.008085193081390376,
          "max": 0.06414448455098092,
          "max_abs": 0.06414448455098092,
          "sample_count": 302787
        },
        {
          "expression": "spf.w",
          "unit": "m/s",
          "status": "failed",
          "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.w\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.w\r\n\t- Feature: Evaluation 11\r\n"
        },
        {
          "expression": "v",
          "unit": "m/s",
          "status": "ok",
          "min": 0.0,
          "max": 0.0,
          "max_abs": 0.0,
          "sample_count": 302787
        },
        {
          "expression": "spf.v",
          "unit": "m/s",
          "status": "failed",
          "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.v\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.v\r\n\t- Feature: Evaluation 12\r\n"
        }
      ],
      "radial_coordinate": [
        {
          "expression": "r",
          "unit": "m",
          "status": "ok",
          "min": 0.0,
          "max": 0.10000000000000003,
          "max_abs": 0.10000000000000003,
          "sample_count": 302787
        },
        {
          "expression": "x",
          "unit": "m",
          "status": "failed",
          "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: x\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: x\r\n\t- Feature: Evaluation 13\r\n"
        }
      ],
      "axial_coordinate": [
        {
          "expression": "z",
          "unit": "m",
          "status": "ok",
          "min": -0.12000000000000001,
          "max": 0.12000000000000001,
          "max_abs": 0.12000000000000001,
          "sample_count": 302787
        },
        {
          "expression": "y",
          "unit": "m",
          "status": "failed",
          "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: y\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: y\r\n\t- Feature: Evaluation 14\r\n"
        }
      ]
    }
  },
  "coordinate_meaning": {
    "radial_coordinate": "r",
    "axial_coordinate": "z",
    "axisymmetric_interpretation": "2D axisymmetric r-z model; horizontal coordinate is radius, vertical coordinate is axial z."
  },
  "metric_regions": {
    "values_m": {
      "Ri": 0.008,
      "Ro": 0.02,
      "h_ring": 0.002,
      "Ri_over_Ro": 0.4
    },
    "full_domain": "domain 1, current single-phase fluid domain",
    "ring_near": "r in [0.004, 0.024] m and z in [-0.008, 0.008] m",
    "center_above": "r in [0, 0.008] m and z in [0, 0.008] m",
    "axis_near": "r <= 0.0012 m",
    "hole_above_line": "z = 0.002 m, r in [0, 0.008] m",
    "center_vertical_line": "r = 0 m, z in [0, 0.008] m"
  },
  "metrics": {
    "u_mag_max": {
      "metric": "u_mag_max",
      "expression": "spf.U",
      "unit": "m/s",
      "value": 0.06790171944503055,
      "status": "ok",
      "method": "calibrated full-domain field sampling fallback",
      "operator_expression": "rfmax_all(spf.U)",
      "operator_error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: rfmax_all\r\n\t- Feature: Evaluation 15\r\n"
    },
    "p_max_global": {
      "metric": "p_max_global",
      "expression": "p",
      "unit": "Pa",
      "value": 606700.6894202387,
      "status": "ok",
      "method": "calibrated full-domain field sampling fallback",
      "operator_expression": "rfmax_all(p)",
      "operator_error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: rfmax_all\r\n\t- Feature: Evaluation 16\r\n"
    },
    "p_max_ring_near": {
      "metric": "p_max_ring_near",
      "expression": "p",
      "unit": "Pa",
      "value": 316772.696479486,
      "status": "ok",
      "method": "coordinate-masked field sampling over solved COMSOL data",
      "sample_count": 51459
    },
    "vz_max_center_above": {
      "metric": "vz_max_center_above",
      "expression": "w",
      "unit": "m/s",
      "value": 0.06414448455098092,
      "status": "ok",
      "method": "coordinate-masked field sampling over solved COMSOL data",
      "sample_count": 7089
    },
    "vz_avg_hole_above": {
      "metric": "vz_avg_hole_above",
      "expression": "w",
      "unit": "m/s",
      "value": 0.03095787265893504,
      "status": "ok",
      "method": "coordinate-masked field sampling over solved COMSOL data",
      "sample_count": 7089
    },
    "Q_axisym_hole_above": {
      "metric": "Q_axisym_hole_above",
      "status": "NA",
      "value": "NA",
      "method": "not used",
      "notes": "A reliable axisymmetric line integration requires a cut-line dataset or boundary-normal flux definition; not implemented for stage 2.1."
    }
  },
  "tables": [
    "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_1_metric_calibration\\tables\\metric_calibration_baseline.csv",
    "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_1_metric_calibration\\tables\\metric_calibration_baseline.xlsx"
  ],
  "images": [
    {
      "ok": true,
      "plot": "Velocity (spf)",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_1_metric_calibration\\images\\metric_velocity_magnitude.png",
      "export_type": "Image2D"
    },
    {
      "ok": true,
      "plot": "Pressure (spf)",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_1_metric_calibration\\images\\metric_pressure.png",
      "export_type": "Image2D"
    },
    {
      "ok": true,
      "plot": "Vertical velocity metric plot",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_1_metric_calibration\\images\\metric_vertical_velocity.png"
    },
    {
      "ok": true,
      "plot": "metric regions schematic",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_1_metric_calibration\\images\\metric_regions_schematic.png"
    }
  ],
  "models": [
    "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_1_metric_calibration\\models\\ring_fountain_v0_metric_calibrated.mph",
    "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\02_1_metric_calibration\\models\\ring_fountain_v0_metric_calibrated_20260617_181832.mph"
  ],
  "review": {
    "status": "PASS",
    "checks": [
      true,
      true,
      true,
      true,
      true
    ]
  }
}
```
