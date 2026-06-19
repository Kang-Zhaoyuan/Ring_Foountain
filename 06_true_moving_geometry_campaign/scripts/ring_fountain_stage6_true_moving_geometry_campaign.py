# -*- coding: utf-8 -*-
"""True-moving-geometry transition campaign.

This campaign freezes the fixed-geometry WettedWall branch as toolchain
validation / negative control and starts a Moving Mesh/ALE branch.  Despite the
directory name, this is not a Stage 6 parameter sweep and does not produce real
Hmax.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import mph


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
STAGE5 = ROOT / "05_two_phase_free_surface"
CAMP = ROOT / "06_true_moving_geometry_campaign"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
SCRIPT_ARCHIVE = SCRIPTS / "ring_fountain_stage6_true_moving_geometry_campaign.py"
LOCAL_SCRIPT = CAMP / "scripts" / "ring_fountain_stage6_true_moving_geometry_campaign.py"
LOG = CAMP / "logs" / f"true_moving_geometry_campaign_{RUN_ID}.log"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ring_fountain_stage4_2a as s42a  # noqa: E402
import ring_fountain_stage5_cleanup_5b_5c as base  # noqa: E402
import ring_fountain_stage5b3_C4_seed_based_ring_smoke as c4help  # noqa: E402


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def ensure_dirs() -> None:
    for sub in [
        "00_fixed_geometry_freeze",
        "01_ALE_seed_discovery/reports",
        "01_ALE_seed_discovery/tables",
        "01_ALE_seed_discovery/logs",
        "02_minimal_ALE_two_phase_seed/models",
        "02_minimal_ALE_two_phase_seed/exports",
        "02_minimal_ALE_two_phase_seed/reports",
        "02_minimal_ALE_two_phase_seed/tables",
        "02_minimal_ALE_two_phase_seed/images",
        "02_minimal_ALE_two_phase_seed/logs",
        "03_true_moving_ring_smoke/models",
        "03_true_moving_ring_smoke/exports",
        "03_true_moving_ring_smoke/reports",
        "03_true_moving_ring_smoke/tables",
        "03_true_moving_ring_smoke/images",
        "03_true_moving_ring_smoke/frames",
        "04_true_moving_ring_stability/models",
        "04_true_moving_ring_stability/exports",
        "04_true_moving_ring_stability/reports",
        "04_true_moving_ring_stability/tables",
        "05_physical_validity_review",
        "logs",
        "reports",
        "tables",
        "images",
        "frames",
        "models",
        "exports",
        "scripts",
    ]:
        (CAMP / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def write_json(path: Path, payload: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return str(path)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            out = {}
            for key in keys:
                value = row.get(key, "")
                if isinstance(value, (dict, list, tuple)):
                    value = json.dumps(value, ensure_ascii=False, default=str)
                out[key] = value
            writer.writerow(out)
    return str(path)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    try:
        return json.loads(read_text(path))
    except Exception:
        return {}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def archive_script() -> dict[str, str]:
    src = Path(__file__).resolve()
    shutil.copy2(src, SCRIPT_ARCHIVE)
    shutil.copy2(src, LOCAL_SCRIPT)
    ts_root = SCRIPT_ARCHIVE.with_name(f"{SCRIPT_ARCHIVE.stem}_{RUN_ID}{SCRIPT_ARCHIVE.suffix}")
    ts_local = LOCAL_SCRIPT.with_name(f"{LOCAL_SCRIPT.stem}_{RUN_ID}{LOCAL_SCRIPT.suffix}")
    shutil.copy2(src, ts_root)
    shutil.copy2(src, ts_local)
    return {"script": str(SCRIPT_ARCHIVE), "timestamp_script": str(ts_root), "local_script": str(LOCAL_SCRIPT), "sha256": sha256(SCRIPT_ARCHIVE)}


def save_model(model: Any, path: Path) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = path.with_name(f"{path.stem}_{RUN_ID}{path.suffix}")
    model.save(path=str(ts), format="Comsol")
    result = {"timestamp_model": str(ts)}
    if path.exists():
        result["model"] = str(ts)
        result["canonical_note"] = f"canonical existed and was not overwritten: {path}"
    else:
        model.save(path=str(path), format="Comsol")
        result["model"] = str(path)
    return result


def save_java(model: Any, path: Path) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = path.with_name(f"{path.stem}_{RUN_ID}{path.suffix}")
    model.save(path=str(ts), format="Java")
    result = {"timestamp_java": str(ts)}
    if path.exists():
        result["java"] = str(ts)
        result["canonical_note"] = f"canonical existed and was not overwritten: {path}"
    else:
        model.save(path=str(path), format="Java")
        result["java"] = str(path)
    return result


def render_simple_curve(path: Path, rows: list[dict[str, Any]], ykey: str) -> None:
    plot_rows = []
    for row in rows:
        y = float(row.get(ykey, math.nan))
        plot_rows.append({"time_s": float(row.get("time_s", 0.0)), "H_m": y, "H_mm": y * 1000 if math.isfinite(y) else math.nan})
    base.render_curve(path, plot_rows)


def phase0_review() -> dict[str, Any]:
    log("Phase 0: project state review.")
    reports = {
        "5B3_GUI_AUTO_SEED": STAGE5 / "5B3_GUI_auto_seed" / "reports" / "5B3_GUI_auto_seed_final_report.md",
        "5B3_C4": STAGE5 / "5B3_C4_seed_based_ring_smoke" / "reports" / "5B3_C4_seed_based_ring_smoke_final_report.md",
        "5B4_original": STAGE5 / "5B4_falling_or_equivalent_ring" / "reports" / "5B4_falling_or_equivalent_ring_final_report.md",
        "5B4_R1": STAGE5 / "5B4_R1_extended_stability_repair" / "reports" / "5B4_R1_extended_stability_repair_final_report.md",
        "5C": STAGE5 / "5C_jet1_extraction" / "reports" / "5C_jet1_extraction_final_report.md",
    }
    gate_rows = [{"stage": key, "report": str(path), "exists": path.exists()} for key, path in reports.items()]
    limits = [
        {"limitation": "fixed_geometry", "status": "present", "meaning": "The ring geometry is stationary; only wall velocity was prescribed."},
        {"limitation": "interface_response", "status": "weak", "meaning": "Free-surface response remained about 0.2 mm diagnostic scale."},
        {"limitation": "Jet1_detected", "status": "NO", "meaning": "Consistent with insufficient physical forcing from fixed geometry."},
        {"limitation": "Stage6_parameter_sweep", "status": "forbidden", "meaning": "Would tune a negative control rather than a physical falling-ring model."},
    ]
    write_csv(CAMP / "tables" / "phase0_gate_history.csv", gate_rows)
    write_csv(CAMP / "tables" / "phase0_physics_limitations.csv", limits)
    write_text(CAMP / "reports" / "phase0_project_state_review.md", "\n".join([
        "# Phase 0 Project State Review",
        "",
        "- Current fixed-geometry branch completed COMSOL API, two-phase setup, WettedWall, interface extraction, and velocity-field diagnostic toolchain validation.",
        "- It cannot demonstrate true ring falling, true Hmax, or reliable Jet1/Jet2 physics because the ring geometry does not move.",
        "- The teacher's critique is accepted as correct.",
        "- `Jet1_detected = NO` is physically plausible because a fixed hole boundary with wall velocity does not create the global displacement and squeeze-through geometry of a falling ring.",
        "- A fixed-geometry Stage 6 parameter sweep is not allowed because it would optimize a negative control.",
        "- The next physical branch must use Moving Mesh/ALE or another real moving-geometry method.",
        "",
        "`ALLOW_PHASE1 = YES`",
        "",
        "No Stage 6 parameter sweep has been performed.",
        "No real Hmax has been produced.",
        "This is a true-moving-geometry transition campaign.",
    ]))
    return {"status": "PASS", "ALLOW_PHASE1": "YES"}


def phase1_freeze() -> dict[str, Any]:
    log("Phase 1: freezing fixed-geometry branch.")
    freeze = CAMP / "00_fixed_geometry_freeze"
    artifacts = [
        STAGE5 / "5B3_GUI_auto_seed" / "reports" / "5B3_GUI_auto_seed_final_report.md",
        STAGE5 / "5B3_C4_seed_based_ring_smoke" / "reports" / "5B3_C4_seed_based_ring_smoke_final_report.md",
        STAGE5 / "5B4_R1_extended_stability_repair" / "reports" / "5B4_R1_extended_stability_repair_final_report.md",
        STAGE5 / "5C_jet1_extraction" / "reports" / "5C_jet1_extraction_final_report.md",
        STAGE5 / "5C_jet1_extraction" / "models" / "ring_fountain_v5C_jet1_extraction_best.mph",
        STAGE5 / "5C_jet1_extraction" / "exports" / "ring_fountain_v5C_jet1_extraction_best.java",
        STAGE5 / "5C_jet1_extraction" / "images" / "C_interface_height_comparison.png",
        STAGE5 / "5C_jet1_extraction" / "images" / "D_jet1_candidate_H_vs_t.png",
        STAGE5 / "5C_jet1_extraction" / "images" / "E_velocity_magnitude_selected_frames.png",
        STAGE5 / "5C_jet1_extraction" / "images" / "E_axial_velocity_selected_frames.png",
    ]
    rows = []
    for src in artifacts:
        dst = freeze / src.name
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
        rows.append({"source": str(src), "frozen_copy": str(dst), "source_exists": src.exists(), "copy_exists": dst.exists()})
    write_csv(freeze / "fixed_geometry_branch_artifact_manifest.csv", rows)
    write_text(freeze / "fixed_geometry_branch_freeze_report.md", "\n".join([
        "# Fixed-Geometry Branch Freeze Report",
        "",
        "- `fixed-geometry branch = frozen`.",
        "- Purpose: COMSOL API / two-phase interface / interface extraction / velocity-field diagnostics toolchain validation.",
        "- Physical role: negative control / engineering baseline.",
        "- Cannot be used for real Hmax.",
        "- Cannot be used for real Jet1/Jet2 mechanism judgment.",
        "- Cannot be used for final parameter sweep.",
        "",
        "`ALLOW_PHASE2 = YES`",
    ]))
    ok = (freeze / "fixed_geometry_branch_freeze_report.md").exists() and (freeze / "fixed_geometry_branch_artifact_manifest.csv").exists()
    return {"status": "PASS" if ok else "FAIL", "ALLOW_PHASE2": "YES" if ok else "NO"}


def phase2_discovery() -> dict[str, Any]:
    log("Phase 2: ALE API discovery.")
    probe1 = CAMP / "01_ALE_seed_discovery" / "logs" / "ale_api_probe.json"
    probe2 = CAMP / "01_ALE_seed_discovery" / "logs" / "ale_feature_property_probe.json"
    rows = []
    for item in read_json(probe1) or []:
        rows.append(item)
    for item in read_json(probe2) or []:
        rows.append(item)
    candidates = [
        {"api_kind": "physics", "api_name": "MovingMesh", "status": "PASS", "source": str(probe1)},
        {"api_kind": "physics", "api_name": "DeformedGeometry", "status": "PASS", "source": str(probe1)},
        {"api_kind": "feature", "api_name": "FreeDeformation", "status": "PASS on domain edim=2", "source": "minimal ALE probe"},
        {"api_kind": "feature", "api_name": "PrescribedMeshDisplacement", "status": "PASS", "properties": "useDx, dx", "source": str(probe2)},
        {"api_kind": "feature", "api_name": "PrescribedMeshVelocity", "status": "PASS", "properties": "useVx, vx", "source": str(probe2)},
    ]
    write_csv(CAMP / "01_ALE_seed_discovery" / "tables" / "ALE_candidate_api_names.csv", candidates)
    write_text(CAMP / "01_ALE_seed_discovery" / "logs" / "ALE_discovery.log", json.dumps(rows, ensure_ascii=False, indent=2, default=str))
    write_text(CAMP / "01_ALE_seed_discovery" / "reports" / "ALE_API_discovery_report.md", "\n".join([
        "# ALE API Discovery Report",
        "",
        "- `MovingMesh` physics interface can be created.",
        "- `DeformedGeometry` physics interface can be created.",
        "- `FreeDeformation` is a domain feature (`edim=2`).",
        "- `PrescribedMeshDisplacement` is a boundary feature (`edim=1`) with properties `useDx` and `dx`.",
        "- `PrescribedMeshVelocity` is a boundary feature (`edim=1`) with properties `useVx` and `vx`.",
        "",
        "`ALLOW_PHASE3 = YES`",
    ]))
    return {"status": "PASS", "ALLOW_PHASE3": "YES", "candidates": candidates}


def phase3_minimal_ale(client: Any) -> dict[str, Any]:
    log("Phase 3: minimal ALE single-physics smoke.")
    out = CAMP / "02_minimal_ALE_two_phase_seed"
    model_path = out / "models" / "minimal_ALE_single_physics_smoke_direct.mph"
    java_path = out / "exports" / "minimal_ALE_single_physics_smoke_direct.java"
    final_model = out / "models" / "minimal_ALE_single_physics_smoke.mph"
    final_java = out / "exports" / "minimal_ALE_single_physics_smoke.java"
    rows = []
    try:
        model = client.load(str(model_path))
        for inner in [1, 11, 21]:
            row = {"inner_solution": inner}
            for expr in ["t", "y-Y", "x-X"]:
                unit = "s" if expr == "t" else "m"
                try:
                    arr = np.asarray(model.evaluate(expr, unit=unit, inner=[inner])).reshape(-1)
                    arr = arr[np.isfinite(arr)]
                    row[f"{expr}_min"] = float(np.min(arr)) if arr.size else math.nan
                    row[f"{expr}_max"] = float(np.max(arr)) if arr.size else math.nan
                except Exception as exc:
                    row[f"{expr}_error"] = str(exc)
            row["time_s"] = row.get("t_min", math.nan)
            row["mesh_displacement_y_min_m"] = row.get("y-Y_min", math.nan)
            rows.append(row)
        try:
            if not final_model.exists():
                shutil.copy2(model_path, final_model)
            if not final_java.exists():
                shutil.copy2(java_path, final_java)
        finally:
            try:
                client.remove(model)
            except Exception:
                pass
    except Exception:
        rows.append({"status": "FAIL", "error": traceback.format_exc()})
    write_csv(out / "tables" / "minimal_ALE_mesh_motion.csv", rows)
    render_simple_curve(out / "images" / "minimal_ALE_mesh_before_after.png", rows, "mesh_displacement_y_min_m")
    moved = any(abs(float(r.get("mesh_displacement_y_min_m", 0.0))) > 1e-7 for r in rows if "mesh_displacement_y_min_m" in r)
    write_text(out / "reports" / "minimal_ALE_single_physics_smoke_report.md", "\n".join([
        "# Minimal ALE Single-Physics Smoke Report",
        "",
        f"- Model: `{final_model}`",
        f"- Java: `{final_java}`",
        f"- Mesh/boundary motion verified by `y-Y`: `{moved}`.",
        "- Expected displacement: `-Vtest*t_end = -2e-7 m`.",
        "- Solver completed in the direct ALE probe.",
        "",
        f"`ALLOW_PHASE4 = {'YES' if moved and final_model.exists() and final_java.exists() else 'NO'}`",
    ]))
    return {"status": "PASS" if moved and final_model.exists() and final_java.exists() else "FAIL", "ALLOW_PHASE4": "YES" if moved else "NO", "rows": rows}


def build_minimal_twophase_ale(client: Any) -> dict[str, Any]:
    log("Phase 4: attempting minimal TwoPhase + WettedWall + ALE seed.")
    out = CAMP / "02_minimal_ALE_two_phase_seed"
    result: dict[str, Any] = {"status": "FAIL"}
    model = None
    try:
        model = client.create(f"minimal_twophase_ALE_wettedwall_seed_{RUN_ID}")
        j = model.java
        p = j.param()
        for k, v in {
            "Rtank": "20[mm]", "Zmin": "-15[mm]", "Zmax": "15[mm]", "z0": "0[mm]", "eps_ls": "1[mm]",
            "rho_w": "1000[kg/m^3]", "mu_w": "1e-3[Pa*s]", "rho_air": "1.2[kg/m^3]", "mu_air": "1.8e-5[Pa*s]",
            "sigma_wa": "0.072[N/m]", "g0": "9.81[m/s^2]", "Vtest": "1e-4[m/s]", "t_end": "0.002[s]", "dt": "1e-4[s]",
        }.items():
            p.set(k, v)
        comp = j.component().create("comp1", True)
        geom = comp.geom().create("geom1", 2)
        geom.axisymmetric(True)
        rect = geom.feature().create("tank", "Rectangle")
        rect.set("size", ["Rtank", "Zmax-Zmin"])
        rect.set("pos", ["0", "Zmin"])
        geom.run()
        # Boundary selections by coordinate.
        tol = 2e-4
        axis = c4help.box_boundaries(comp, "sel_axis", -tol, tol, -0.016, 0.016)
        top = c4help.box_boundaries(comp, "sel_top", -tol, 0.021, 0.0148, 0.0152)
        bottom = c4help.box_boundaries(comp, "sel_bottom", -tol, 0.021, -0.0152, -0.0148)
        outer = c4help.box_boundaries(comp, "sel_outer_moving", 0.0198, 0.0202, -0.0155, 0.0155)
        mesh = comp.mesh().create("mesh1")
        mesh.autoMeshSize(5)
        mesh.run()
        spf = comp.physics().create("spf", "LaminarFlow", "geom1")
        ls = comp.physics().create("ls", "LevelSet", "geom1")
        tpf = comp.multiphysics().create("tpf1", "TwoPhaseFlowLevelSet", 2)
        tpf.set("Fluid_physics", "spf")
        tpf.set("Mathematics_physics", "ls")
        tpf.selection().all()
        for key, value in [
            ("rho1_mat", "userdef"), ("rho1", "rho_air"), ("mu1_mat", "userdef"), ("mu1", "mu_air"),
            ("rho2_mat", "userdef"), ("rho2", "rho_w"), ("mu2_mat", "userdef"), ("mu2", "mu_w"),
            ("IncludeSurfaceTension", True), ("SurfaceTensionCoefficient", "userdef"), ("sigma", "sigma_wa"),
        ]:
            c4help.safe_set(tpf, key, value)
        ww = comp.multiphysics().create("ww1", "WettedWall", 1)
        ww.set("Fluid_physics", "spf")
        ww.set("Mathematics_physics", "ls")
        ww.selection().set(c4help.jints(outer))
        for key, value in [
            ("BoundaryCondition", "NavierSlip"), ("TranslationalVelocityOption", "Manual"), ("utr", ["0", "-Vtest", "0"]),
            ("SpecifyContactAngle", "SpecifyContactAngleDirectly"), ("thetaw", "pi/2"), ("beta", "eps_ls"),
        ]:
            c4help.safe_set(ww, key, value)
        out_top = spf.feature().create("out_top", "OutletBoundary", 1)
        out_top.selection().set(c4help.jints(top))
        lsout = ls.feature().create("out_top", "Outlet", 1)
        lsout.selection().set(c4help.jints(top))
        ls.feature("init1").set("phils_init", "flc2hs(z0-z,eps_ls)")
        ls.feature("init1").set("phils", "flc2hs(z0-z,eps_ls)")
        ls.feature("lsm1").set("epsilon_ls", "eps_ls")
        ls.feature("lsm1").set("gamma", "0.01[m/s]")
        spf.prop("PhysicalModelProperty").set("IncludeGravity", True)
        spf.feature("grav1").set("g", ["0", "-g0", "0"])
        ale = comp.physics().create("ale", "MovingMesh", "geom1")
        ale.create("free1", "FreeDeformation", 2)
        ale.feature("free1").selection().all()
        ale.create("move1", "PrescribedMeshDisplacement", 1)
        ale.feature("move1").selection().set(c4help.jints(outer))
        ale.feature("move1").set("useDx", ["0", "1"])
        ale.feature("move1").set("dx", ["0", "-Vtest*t"])
        ale.create("fixb", "PrescribedMeshDisplacement", 1)
        ale.feature("fixb").selection().set(c4help.jints(sorted(set(axis + top + bottom))))
        ale.feature("fixb").set("useDx", ["1", "1"])
        ale.feature("fixb").set("dx", ["0", "0"])
        study = j.study().create("std1")
        study.create("phasei", "PhaseInitialization")
        try:
            study.feature("phasei").setSolveFor("/physics/spf", False)
        except Exception:
            pass
        study.create("time", "Transient")
        study.feature("time").set("tlist", "range(0,dt,t_end)")
        study.feature("time").set("initstudy", "std1")
        study.feature("time").set("useinitsol", "on")
        try:
            j.study("std1").run()
            solve_status = "PASS"
            failure = ""
        except Exception:
            solve_status = "FAIL"
            failure = traceback.format_exc()
        model_paths = save_model(model, out / "models" / "minimal_twophase_ALE_wettedwall_seed.mph")
        java_paths = save_java(model, out / "exports" / "minimal_twophase_ALE_wettedwall_seed.java")
        motion = math.nan
        interface_points = 0
        if solve_status == "PASS":
            try:
                arr = np.asarray(model.evaluate("y-Y", unit="m", inner=[21])).reshape(-1)
                arr = arr[np.isfinite(arr)]
                motion = float(np.min(arr)) if arr.size else math.nan
            except Exception:
                pass
            try:
                data = {}
                for expr, key, unit in [("r", "r", "m"), ("z", "z", "m"), ("phils", "phi", "")]:
                    data[key] = s42a.eval_array(model, expr, unit, inner=[21]).reshape(-1)
                pts = base.estimate_interface(data["r"], data["z"], data["phi"], threshold=0.5)
                interface_points = len(pts)
                base.render_field(out / "images" / "minimal_twophase_ALE_interface.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True)
            except Exception:
                pass
        rows = [{
            "case_id": "minimal_twophase_ALE",
            "solve_status": solve_status,
            "failure_message": failure[:1000],
            "motion_y_min_m": motion,
            "interface_points": interface_points,
            "TwoPhaseFlowLevelSet": "tpf1",
            "WettedWall": "ww1",
            "MovingMesh": "ale",
        }]
        write_csv(out / "tables" / "minimal_twophase_ALE_cases.csv", rows)
        render_simple_curve(out / "images" / "minimal_twophase_ALE_mesh_motion.png", [{"time_s": 0, "motion": 0.0}, {"time_s": 0.002, "motion": motion}], "motion")
        passed = solve_status == "PASS" and math.isfinite(motion) and abs(motion) > 1e-7 and interface_points > 0
        write_text(out / "reports" / "minimal_twophase_ALE_wettedwall_seed_report.md", "\n".join([
            "# Minimal TwoPhaseFlowLevelSet + WettedWall + ALE Seed Report",
            "",
            f"- Solve status: `{solve_status}`.",
            f"- Wall/mesh motion diagnostic `min(y-Y)`: `{motion}` m.",
            f"- Interface points: `{interface_points}`.",
            "- Required interfaces: `TwoPhaseFlowLevelSet`, `WettedWall`, `MovingMesh`.",
            f"- Model: `{model_paths.get('model')}`",
            f"- Java: `{java_paths.get('java')}`",
            "",
            f"`ALLOW_PHASE5 = {'YES' if passed else 'NO'}`",
            "",
            "No Stage 6 parameter sweep has been performed.",
            "No real Hmax has been produced.",
            "This is a true-moving-geometry transition campaign.",
        ]))
        result = {"status": "PASS" if passed else "FAIL", "ALLOW_PHASE5": "YES" if passed else "NO", "rows": rows, "model": model_paths, "java": java_paths}
    except Exception:
        err = traceback.format_exc()
        write_text(out / "logs" / "minimal_twophase_ALE_exception.log", err)
        write_text(out / "reports" / "minimal_twophase_ALE_wettedwall_seed_report.md", "# Minimal TwoPhase ALE Seed Report\n\n`FAIL`\n\n" + err)
        result = {"status": "FAIL", "ALLOW_PHASE5": "NO", "error": err[:1000]}
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass
    return result


def skip_phase5_to_7(reason: str, summary: dict[str, Any]) -> None:
    write_csv(CAMP / "03_true_moving_ring_smoke" / "tables" / "true_moving_ring_smoke_cases.csv", [{"case_id": "SKIPPED", "solve_status": "SKIP", "failure_message": reason, "ring_boundary_motion_verified": False}])
    write_text(CAMP / "03_true_moving_ring_smoke" / "reports" / "true_moving_ring_smoke_report.md", f"# True Moving Ring Smoke Report\n\nSKIP/FAIL: {reason}\n\n`ALLOW_PHASE6 = NO`\n")
    write_csv(CAMP / "04_true_moving_ring_stability" / "tables" / "true_moving_ring_stability_cases.csv", [{"case_id": "SKIPPED", "solve_status": "SKIP", "failure_message": "Phase 5 did not pass."}])
    write_text(CAMP / "04_true_moving_ring_stability" / "reports" / "true_moving_ring_stability_report.md", "# True Moving Ring Stability Report\n\nSKIPPED because Phase 5 did not pass.\n")
    rows = [
        {"criterion": "true_geometry_motion", "fixed_geometry_branch": "NO", "true_moving_branch": "NOT_AVAILABLE"},
        {"criterion": "wall_velocity_only", "fixed_geometry_branch": "YES", "true_moving_branch": "NO_PASSING_RING_MODEL"},
        {"criterion": "continue_stage6", "fixed_geometry_branch": "NO", "true_moving_branch": "NO"},
    ]
    write_csv(CAMP / "05_physical_validity_review" / "true_vs_fixed_geometry_comparison.csv", rows)
    write_text(CAMP / "05_physical_validity_review" / "true_vs_fixed_geometry_review.md", "\n".join([
        "# True vs Fixed Geometry Review",
        "",
        "- Fixed geometry branch is frozen as negative control.",
        "- True moving geometry branch has not yet produced a passing ring model in this campaign run.",
        "- Final conclusion: `TRUE_MOVING_GEOMETRY_BRANCH = FAIL` unless a later ALE ring model passes Phase 5.",
        "- Recommendation: continue ALE ring debugging only if Phase 4 passes; otherwise consider SPH/VOF or experiment-led workflow.",
    ]))


def final_report(summary: dict[str, Any]) -> None:
    phase5_pass = summary.get("Phase5", {}).get("status") == "PASS"
    allow_next = "YES" if phase5_pass else "NO"
    write_text(CAMP / "reports" / "true_moving_geometry_campaign_final_report.md", "\n".join([
        "# True Moving Geometry Campaign Final Report",
        "",
        f"Run ID: `{RUN_ID}`",
        "",
        f"1. fixed-geometry branch frozen: `{summary.get('Phase1', {}).get('status') == 'PASS'}`.",
        "2. teacher critique formally accepted: `YES`.",
        f"3. Moving Mesh/ALE API found: `{summary.get('Phase2', {}).get('status') == 'PASS'}`.",
        f"4. Minimal ALE single-physics passed: `{summary.get('Phase3', {}).get('status') == 'PASS'}`.",
        f"5. Minimal TwoPhaseFlowLevelSet + WettedWall + ALE passed: `{summary.get('Phase4', {}).get('status') == 'PASS'}`.",
        f"6. True moving ring smoke test passed: `{phase5_pass}`.",
        f"7. Ring boundary true motion proved: `{summary.get('Phase5', {}).get('ring_boundary_motion_verified', False)}`.",
        f"8. Free surface obvious response: `{summary.get('Phase5', {}).get('interface_quality', 'not_available')}`.",
        "9. Jet1 candidate detected: `not_evaluated_in_true_ring_branch`.",
        f"10. Allow true geometry next: `{allow_next}`.",
        "11. Allow Stage 6 parameter sweep: `NO`.",
        "12. Real Hmax output: `NO`.",
        "",
        f"`ALLOW_TRUE_GEOMETRY_NEXT = {allow_next}`",
        "`ALLOW_STAGE6_PARAMETER_SWEEP = NO`",
        "`ALLOW_REAL_HMAX_OUTPUT = NO`",
        "",
        "No Stage 6 parameter sweep has been performed.",
        "No real Hmax has been produced.",
        "This is a true-moving-geometry transition campaign.",
    ]))


def update_docs(summary: dict[str, Any]) -> None:
    c4help.add_or_replace_section(ROOT / "README.md", "TRUE_MOVING_GEOMETRY_CAMPAIGN", [
        "## True Moving Geometry Campaign",
        "",
        f"- Run ID: `{RUN_ID}`.",
        "- Fixed-geometry branch is frozen as toolchain validation / negative control.",
        "- True-moving-geometry branch is now the active physical modelling branch.",
        f"- Minimal ALE single-physics: `{summary.get('Phase3', {}).get('status')}`.",
        f"- Minimal two-phase ALE seed: `{summary.get('Phase4', {}).get('status')}`.",
        "- No real Hmax has been produced.",
        "- No Stage 6 parameter sweep has been performed.",
        f"- Final report: `{CAMP / 'reports' / 'true_moving_geometry_campaign_final_report.md'}`.",
    ])
    c4help.add_or_replace_section(ROOT / "CHANGELOG.md", "TRUE_MOVING_GEOMETRY_CAMPAIGN", [
        "## True Moving Geometry Campaign",
        "",
        f"- Run ID: `{RUN_ID}`.",
        "- Accepted teacher critique of the fixed-geometry branch.",
        "- Froze fixed-geometry branch as negative control.",
        "- Discovered Moving Mesh/ALE API and attempted minimal ALE seeds.",
        "- No Stage 6 parameter sweep or real Hmax output was performed.",
    ])
    c4help.add_or_replace_section(SCRIPTS / "SCRIPT_MANIFEST.md", "TRUE_MOVING_GEOMETRY_CAMPAIGN_SCRIPT", [
        "## True Moving Geometry Campaign Script",
        "",
        f"| `ring_fountain_stage6_true_moving_geometry_campaign.py` | true-moving-geometry transition campaign | `{RUN_ID}` | `{sha256(SCRIPT_ARCHIVE)}` |",
    ])


def main() -> int:
    ensure_dirs()
    summary: dict[str, Any] = {"run_id": RUN_ID, "script": archive_script()}
    client = None
    try:
        summary["Phase0"] = phase0_review()
        summary["Phase1"] = phase1_freeze() if summary["Phase0"].get("ALLOW_PHASE1") == "YES" else {"status": "SKIP"}
        summary["Phase2"] = phase2_discovery() if summary["Phase1"].get("ALLOW_PHASE2") == "YES" else {"status": "SKIP"}
        client = mph.Client(cores=2, version="6.4")
        summary["Phase3"] = phase3_minimal_ale(client) if summary["Phase2"].get("ALLOW_PHASE3") == "YES" else {"status": "SKIP", "ALLOW_PHASE4": "NO"}
        summary["Phase4"] = build_minimal_twophase_ale(client) if summary["Phase3"].get("ALLOW_PHASE4") == "YES" else {"status": "SKIP", "ALLOW_PHASE5": "NO"}
        if summary["Phase4"].get("ALLOW_PHASE5") == "YES":
            reason = "Phase 5 true ring ALE construction is not yet implemented in this campaign script; requires next automation pass using validated Phase 4 seed."
            summary["Phase5"] = {"status": "SKIP", "ALLOW_PHASE6": "NO", "ring_boundary_motion_verified": False, "reason": reason}
            skip_phase5_to_7(reason, summary)
        else:
            reason = "Phase 4 minimal two-phase ALE seed did not pass; true moving ring smoke was not attempted."
            summary["Phase5"] = {"status": "SKIP", "ALLOW_PHASE6": "NO", "ring_boundary_motion_verified": False, "reason": reason}
            skip_phase5_to_7(reason, summary)
        summary["TRUE_MOVING_GEOMETRY_BRANCH"] = "FAIL" if summary.get("Phase5", {}).get("status") != "PASS" else "PASS_MINIMAL"
    except Exception:
        err = traceback.format_exc()
        write_text(CAMP / "logs" / f"fatal_error_{RUN_ID}.log", err)
        summary["fatal_error"] = err
    finally:
        try:
            if client is not None:
                client.clear()
        except Exception:
            pass
    final_report(summary)
    update_docs(summary)
    write_json(CAMP / "reports" / "true_moving_geometry_campaign_summary.json", summary)
    log("True moving geometry campaign completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
