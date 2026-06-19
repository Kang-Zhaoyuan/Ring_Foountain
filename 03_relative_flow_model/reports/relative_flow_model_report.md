# Stage 3 Relative Flow Model Report

Run time: 2026-06-17T18:21:51

## Review

Stage 3 review status: `PASS`.

This model is not a laboratory-frame falling ring. It is a fixed-ring reference-frame relative-flow approximation.
`U0` remains an independent relative incoming velocity parameter. `U_impact = sqrt(2*g_const*H_drop)` is added only as a scale comparison.
`H_kin_proxy = vz_max_center_above^2/(2*g_const)` is a kinetic-height proxy, not the true two-phase free-surface `Hmax`.

## Structured Data

```json
{
  "stage": "3",
  "models": [
    "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\03_relative_flow_model\\models\\ring_fountain_v2_relative_flow.mph",
    "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\03_relative_flow_model\\models\\ring_fountain_v2_relative_flow_20260617_181832.mph"
  ],
  "metrics": {
    "u_mag_max": {
      "metric": "u_mag_max",
      "expression": "spf.U",
      "unit": "m/s",
      "value": 0.06790171944503055,
      "status": "ok",
      "method": "calibrated full-domain field sampling fallback",
      "operator_expression": "rfmax_all(spf.U)",
      "operator_error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: rfmax_all\r\n\t- Feature: Evaluation 24\r\n"
    },
    "p_max_global": {
      "metric": "p_max_global",
      "expression": "p",
      "unit": "Pa",
      "value": 606700.6894202387,
      "status": "ok",
      "method": "calibrated full-domain field sampling fallback",
      "operator_expression": "rfmax_all(p)",
      "operator_error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: rfmax_all\r\n\t- Feature: Evaluation 25\r\n"
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
  "H_kin_proxy": {
    "H_drop": "50[mm]",
    "U0": "0.02[m/s]",
    "U_impact_m_per_s": 0.990285312422637,
    "vz_max_center_above_m_per_s": 0.06414448455098092,
    "H_kin_proxy_m": 0.00020978187751734948,
    "model_type": "single-phase fixed-ring relative-flow proxy",
    "notes": "H_kin_proxy is not true two-phase free-surface Hmax."
  },
  "images": [
    {
      "ok": true,
      "plot": "Velocity (spf)",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\03_relative_flow_model\\images\\relative_velocity.png",
      "export_type": "Image2D"
    },
    {
      "ok": true,
      "plot": "Pressure (spf)",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\03_relative_flow_model\\images\\relative_pressure.png",
      "export_type": "Image2D"
    },
    {
      "ok": true,
      "plot": "Vertical velocity metric plot",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\03_relative_flow_model\\images\\relative_vertical_velocity.png"
    }
  ],
  "review": {
    "status": "PASS",
    "images_ok": true
  }
}
```
