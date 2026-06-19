# Stage 5A Static Interface Report

Run time: 2026-06-17T20:11:10

5A review status: `PASS`

## Scope

- Static free-surface smoke test only.
- No moving ring.
- No `Hmax` extraction.

## Interface Attempt

- Preferred combined physics type names were probed separately; standalone `LevelSet` and `LaminarFlow` were available.
- This script attempted a minimal `LaminarFlow + LevelSet` model on a fixed 2D/axisymmetric rectangle.
- Setup details: `{"axisym_status": "geom.axisymmetric(True)", "level_set_attempts": [{"key": "phi", "value": "flc2hs(-z,eps_ls)", "status": "failed", "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown parameter phi.\r\nMessages:\r\n\tUnknown parameter phi.\r\n\t- Feature: Level Set (ls)\r\n"}, {"key": "Phi", "value": "flc2hs(-z,eps_ls)", "status": "failed", "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown parameter Phi.\r\nMessages:\r\n\tUnknown parameter Phi.\r\n\t- Feature: Level Set (ls)\r\n"}, {"key": "phils", "value": "flc2hs(-z,eps_ls)", "status": "ok"}, {"key": "ls", "value": "flc2hs(-z,eps_ls)", "status": "failed", "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown parameter ls.\r\nMessages:\r\n\tUnknown parameter ls.\r\n\t- Feature: Level Set (ls)\r\n"}, {"key": "u", "value": "flc2hs(-z,eps_ls)", "status": "failed", "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown parameter u.\r\nMessages:\r\n\tUnknown parameter u.\r\n\t- Feature: Level Set (ls)\r\n"}, {"key": "epsilon", "value": "eps_ls", "status": "failed", "error": "'com.comsol.clientapi.physics.impl.PhysicsClient' object has no attribute 'set'"}, {"key": "eps", "value": "eps_ls", "status": "failed", "error": "'com.comsol.clientapi.physics.impl.PhysicsClient' object has no attribute 'set'"}, {"key": "interfaceThickness", "value": "eps_ls", "status": "failed", "error": "'com.comsol.clientapi.physics.impl.PhysicsClient' object has no attribute 'set'"}, {"key": "lsinit", "value": "eps_ls", "status": "failed", "error": "'com.comsol.clientapi.physics.impl.PhysicsClient' object has no attribute 'set'"}], "spf_attempts": [{"key": "rho_mat", "value": "userdef", "status": "ok"}, {"key": "rho", "value": "rho_air+(rho_w-rho_air)*phils", "status": "ok"}, {"key": "mu_mat", "value": "userdef", "status": "ok"}, {"key": "mu", "value": "mu_air+(mu_w-mu_air)*phils", "status": "ok"}]}`

## Outputs

- Model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\models\ring_fountain_v4_5A_static_interface.mph`
- Timestamp model: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\models\ring_fountain_v4_5A_static_interface_20260617_201044.mph`
- Interface variable: `phils`
- Final image: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\images\5A_static_interface_final.png`
- Metrics CSV: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\tables\5A_static_interface_metrics.csv`
- Frame index CSV: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\tables\5A_static_interface_frame_index.csv`

## Review

- Interface stability smoke pass: `True`
- This is only a smoke test of static interface initialization, not a ring-fountain free-surface simulation.

## Structured Data

```json
{
  "status": "PASS",
  "setup": {
    "axisym_status": "geom.axisymmetric(True)",
    "level_set_attempts": [
      {
        "key": "phi",
        "value": "flc2hs(-z,eps_ls)",
        "status": "failed",
        "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown parameter phi.\r\nMessages:\r\n\tUnknown parameter phi.\r\n\t- Feature: Level Set (ls)\r\n"
      },
      {
        "key": "Phi",
        "value": "flc2hs(-z,eps_ls)",
        "status": "failed",
        "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown parameter Phi.\r\nMessages:\r\n\tUnknown parameter Phi.\r\n\t- Feature: Level Set (ls)\r\n"
      },
      {
        "key": "phils",
        "value": "flc2hs(-z,eps_ls)",
        "status": "ok"
      },
      {
        "key": "ls",
        "value": "flc2hs(-z,eps_ls)",
        "status": "failed",
        "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown parameter ls.\r\nMessages:\r\n\tUnknown parameter ls.\r\n\t- Feature: Level Set (ls)\r\n"
      },
      {
        "key": "u",
        "value": "flc2hs(-z,eps_ls)",
        "status": "failed",
        "error": "Exception:\r\n\tcom.comsol.util.exceptions.FlException: Unknown parameter u.\r\nMessages:\r\n\tUnknown parameter u.\r\n\t- Feature: Level Set (ls)\r\n"
      },
      {
        "key": "epsilon",
        "value": "eps_ls",
        "status": "failed",
        "error": "'com.comsol.clientapi.physics.impl.PhysicsClient' object has no attribute 'set'"
      },
      {
        "key": "eps",
        "value": "eps_ls",
        "status": "failed",
        "error": "'com.comsol.clientapi.physics.impl.PhysicsClient' object has no attribute 'set'"
      },
      {
        "key": "interfaceThickness",
        "value": "eps_ls",
        "status": "failed",
        "error": "'com.comsol.clientapi.physics.impl.PhysicsClient' object has no attribute 'set'"
      },
      {
        "key": "lsinit",
        "value": "eps_ls",
        "status": "failed",
        "error": "'com.comsol.clientapi.physics.impl.PhysicsClient' object has no attribute 'set'"
      }
    ],
    "spf_attempts": [
      {
        "key": "rho_mat",
        "value": "userdef",
        "status": "ok"
      },
      {
        "key": "rho",
        "value": "rho_air+(rho_w-rho_air)*phils",
        "status": "ok"
      },
      {
        "key": "mu_mat",
        "value": "userdef",
        "status": "ok"
      },
      {
        "key": "mu",
        "value": "mu_air+(mu_w-mu_air)*phils",
        "status": "ok"
      }
    ]
  },
  "outputs": {
    "chosen_interface_variable": "phils",
    "final_image": {
      "ok": true,
      "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\images\\5A_static_interface_final.png",
      "phi_min": -1.1003907984148822e-11,
      "phi_max": 1.0000000000187053,
      "interface_reference": 0.5,
      "method": "Python rendering of COMSOL Level Set field samples; black line is z=0 reference"
    },
    "metrics_csv": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\tables\\5A_static_interface_metrics.csv",
    "frame_index_csv": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\tables\\5A_static_interface_frame_index.csv",
    "frames": [
      {
        "inner_solution": 1,
        "time_s": 0.0,
        "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\images\\frames\\5A_static_interface_frame_001.png",
        "ok": true
      },
      {
        "inner_solution": 2,
        "time_s": 0.005,
        "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\images\\frames\\5A_static_interface_frame_002.png",
        "ok": true
      },
      {
        "inner_solution": 3,
        "time_s": 0.01,
        "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\images\\frames\\5A_static_interface_frame_003.png",
        "ok": true
      },
      {
        "inner_solution": 4,
        "time_s": 0.015,
        "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\images\\frames\\5A_static_interface_frame_004.png",
        "ok": true
      },
      {
        "inner_solution": 5,
        "time_s": 0.02,
        "file": "D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\images\\frames\\5A_static_interface_frame_005.png",
        "ok": true
      }
    ],
    "metrics": [
      {
        "inner_solution": 1,
        "time_s": 0.0,
        "phi_mean_below_z_minus_1cm": 0.9999999943157827,
        "phi_mean_above_z_plus_1cm": 4.46661682704075e-09,
        "phi_min": -0.00016106305722898796,
        "phi_max": 1.0002126881968756
      },
      {
        "inner_solution": 2,
        "time_s": 0.005,
        "phi_mean_below_z_minus_1cm": 0.9997287462564091,
        "phi_mean_above_z_plus_1cm": 0.0002678963554671559,
        "phi_min": -7.892986511894106e-06,
        "phi_max": 1.0000089391470148
      },
      {
        "inner_solution": 3,
        "time_s": 0.01,
        "phi_mean_below_z_minus_1cm": 0.9989729909432256,
        "phi_mean_above_z_plus_1cm": 0.0010184214033957413,
        "phi_min": -3.6022440883609515e-08,
        "phi_max": 1.000000045186894
      },
      {
        "inner_solution": 4,
        "time_s": 0.015,
        "phi_mean_below_z_minus_1cm": 0.9983471369879189,
        "phi_mean_above_z_plus_1cm": 0.0016409998767018407,
        "phi_min": -4.4615088684836095e-10,
        "phi_max": 1.0000000006795255
      },
      {
        "inner_solution": 5,
        "time_s": 0.02,
        "phi_mean_below_z_minus_1cm": 0.9978932993807208,
        "phi_mean_above_z_plus_1cm": 0.002092775377499193,
        "phi_min": -1.1003907984148822e-11,
        "phi_max": 1.0000000000187053
      }
    ],
    "interface_stability_smoke_pass": true
  }
}
```
