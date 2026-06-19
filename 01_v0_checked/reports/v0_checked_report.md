# V0 Checked Report

Run time: 2026-06-17T12:37:03

Saved checked model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\01_v0_checked\models\ring_fountain_v0_checked.mph`.
Saved timestamped model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\01_v0_checked\models\ring_fountain_v0_checked_20260617_123632.mph`.
Parameter descriptions were updated where matching parameter names existed.
Derived-value metrics were attempted conservatively; failed expressions are recorded in the CSV.
No boundary condition or core physics assumption was changed.

## Structured Data

```json
{
  "parameter_description_changes": [
    {
      "parameter": "Ro",
      "status": "updated",
      "description": "Outer radius of the ring."
    },
    {
      "parameter": "Ri",
      "status": "updated",
      "description": "Inner radius of the ring opening; Ri/Ro controls the hole ratio."
    },
    {
      "parameter": "Rtank",
      "status": "updated",
      "description": "Radius of the computational water domain."
    },
    {
      "parameter": "Zup",
      "status": "updated",
      "description": "Water-domain height above the ring region."
    },
    {
      "parameter": "Zdown",
      "status": "updated",
      "description": "Water-domain height below the ring region."
    },
    {
      "parameter": "U0",
      "status": "updated",
      "description": "Relative incoming flow speed, or equivalent ring motion speed in the fixed-ring frame."
    },
    {
      "parameter": "rho_w",
      "status": "updated",
      "description": "Water density."
    },
    {
      "parameter": "mu_w",
      "status": "updated",
      "description": "Dynamic viscosity of water."
    },
    {
      "parameter": "h_ring",
      "status": "updated",
      "description": "Ring cross-section thickness in the simplified single-phase model."
    }
  ],
  "metrics": [
    {
      "metric": "u_max_maxop",
      "expression": "maxop1(spf.U)",
      "unit": "m/s",
      "status": "failed",
      "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 1\r\n"
    },
    {
      "metric": "u_max_max",
      "expression": "max(spf.U)",
      "unit": "m/s",
      "status": "failed",
      "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Function called with wrong number of arguments.\r\nMessages:\r\n\tFunction called with wrong number of arguments.\r\n\t- Function name: max\r\n\t- Number of arguments used: 1\r\n\t- Number of arguments expected: 2\r\n\t- Feature: Evaluation 2\r\n"
    },
    {
      "metric": "p_max_p",
      "expression": "maxop1(p)",
      "unit": "Pa",
      "status": "failed",
      "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 3\r\n"
    },
    {
      "metric": "p_max_spf_p",
      "expression": "maxop1(spf.p)",
      "unit": "Pa",
      "status": "failed",
      "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 4\r\n"
    },
    {
      "metric": "vz_max_v",
      "expression": "maxop1(v)",
      "unit": "m/s",
      "status": "failed",
      "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 5\r\n"
    },
    {
      "metric": "vz_max_w",
      "expression": "maxop1(w)",
      "unit": "m/s",
      "status": "failed",
      "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown function or operator.\r\nMessages:\r\n\tUnknown function or operator.\r\n\t- Name: maxop1\r\n\t- Feature: Evaluation 6\r\n"
    },
    {
      "metric": "u_max_field",
      "expression": "spf.U",
      "unit": "m/s",
      "status": "ok",
      "value": 0.06790171944503055,
      "method": "Python max over evaluated field samples"
    },
    {
      "metric": "p_max_field",
      "expression": "p",
      "unit": "Pa",
      "status": "ok",
      "value": 606700.6894202387,
      "method": "Python max over evaluated field samples"
    },
    {
      "metric": "p_max_spf_field",
      "expression": "spf.p",
      "unit": "Pa",
      "status": "failed",
      "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Failed to evaluate expression.\r\nMessages:\r\n\tCannot evaluate expression.\r\n\r\n\tUndefined variable.\r\n\t- Variable: spf.p\r\n\t- Geometry: geom1\r\n\t- Domain: 1\r\n\r\n\tFailed to evaluate expression.\r\n\t- Expression: spf.p\r\n\t- Feature: Evaluation 7\r\n",
      "method": "Python field max fallback"
    },
    {
      "metric": "vz_max_v_field",
      "expression": "v",
      "unit": "m/s",
      "status": "ok",
      "value": 0.0,
      "method": "Python max over evaluated field samples"
    },
    {
      "metric": "vz_max_w_field",
      "expression": "w",
      "unit": "m/s",
      "status": "ok",
      "value": 0.06414448455098092,
      "method": "Python max over evaluated field samples"
    }
  ],
  "exports": [
    {
      "kind": "plot",
      "node": "Velocity (spf)",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\01_v0_checked\\images\\v0_checked_Velocity__spf_.png",
      "ok": true,
      "value": "created Image2D export",
      "created_export": "img_Velocity__spf_2"
    },
    {
      "kind": "plot",
      "node": "Pressure (spf)",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\01_v0_checked\\images\\v0_checked_Pressure__spf_.png",
      "ok": true,
      "value": "created Image2D export",
      "created_export": "img_Pressure__spf_2"
    },
    {
      "kind": "plot",
      "node": "Velocity, 3D (spf)",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\01_v0_checked\\images\\v0_checked_Velocity__3D__spf_.png",
      "ok": true,
      "value": "created Image3D export",
      "created_export": "img_Velocity__3D__spf_2"
    },
    {
      "kind": "plot",
      "node": "3D Plot Group 4",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\01_v0_checked\\images\\v0_checked_3D_Plot_Group_4.png",
      "ok": true,
      "value": "created Image3D export",
      "created_export": "img_3D_Plot_Group_42"
    },
    {
      "kind": "export",
      "node": "Image 1",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\01_v0_checked\\tables\\v0_checked_Image_1.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 1a",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\01_v0_checked\\tables\\v0_checked_Image_1a.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 1b",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\01_v0_checked\\tables\\v0_checked_Image_1b.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 41",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\01_v0_checked\\tables\\v0_checked_Image_41.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 2",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\01_v0_checked\\tables\\v0_checked_Image_2.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 2a",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\01_v0_checked\\tables\\v0_checked_Image_2a.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 2b",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\01_v0_checked\\tables\\v0_checked_Image_2b.txt",
      "ok": true,
      "value": null
    },
    {
      "kind": "export",
      "node": "Image 42",
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\01_v0_checked\\tables\\v0_checked_Image_42.txt",
      "ok": true,
      "value": null
    }
  ]
}
```
