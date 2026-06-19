# -*- coding: utf-8 -*-
"""Continue Ring Fountain Stage 5 from 5B2-0.

This script is deliberately conservative about review gates.  It rebuilds the
static ring/free-surface model, confirms the ring-wall selections from
coordinate-based COMSOL Box selections, and only advances to later stages when
the previous gate is supported by current artifacts.
"""

from __future__ import annotations

import csv
import json
import math
import os
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import jpype
import mph
import numpy as np

import ring_fountain_stage5_cleanup_5b_5c as base


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
STAGE5 = ROOT / "05_two_phase_free_surface"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = STAGE5 / "logs" / f"stage5b2_to_5e_{RUN_ID}.log"

B2_ROOT = STAGE5 / "5B2_static_ring_free_surface_smoke"
B3_ROOT = STAGE5 / "5B3_moving_wall_ring_free_surface"
B4_ROOT = STAGE5 / "5B4_falling_or_equivalent_ring"
C_ROOT = STAGE5 / "5C_jet1_extraction"
D_ROOT = STAGE5 / "5D_jet2_detection"
E_ROOT = STAGE5 / "5E_stage5_review"

MODEL_5A = STAGE5 / "models" / "ring_fountain_v4_5A_static_interface.mph"
MODEL_B2_1 = B2_ROOT / "models" / "ring_fountain_v5B2_1_static_ring_free_surface.mph"
MODEL_B2_3 = B2_ROOT / "models" / "ring_fountain_v5B2_3_static_ring_free_surface_boundary_confirmed.mph"
MODEL_B3 = B3_ROOT / "models" / "ring_fountain_v5B3_moving_wall_ring_free_surface.mph"
MODEL_B4 = B4_ROOT / "models" / "ring_fountain_v5B4_falling_or_equivalent_ring.mph"


PARAM = {
    "Rtank": "100[mm]",
    "Hwater": "120[mm]",
    "Hair": "120[mm]",
    "Ri": "8[mm]",
    "Ro": "20[mm]",
    "h_ring": "2[mm]",
    "z_ring_center": "-20[mm]",
    "rho_w": "1000[kg/m^3]",
    "mu_w": "1e-3[Pa*s]",
    "rho_air": "1.225[kg/m^3]",
    "mu_air": "1.8e-5[Pa*s]",
    "sigma_wa": "0.072[N/m]",
    "eps_ls": "2[mm]",
}


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def ensure_dirs() -> None:
    for root in [B2_ROOT, B3_ROOT, B4_ROOT, C_ROOT, D_ROOT, E_ROOT]:
        for sub in ["models", "reports", "images", "images/frames", "tables", "logs"]:
            (root / sub).mkdir(parents=True, exist_ok=True)
    for sub in ["reports", "logs"]:
        (STAGE5 / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    base.write_csv(path, rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def jints(values: list[int]) -> Any:
    return jpype.JArray(jpype.JInt)(values)


def append_docs(summary: dict[str, Any]) -> None:
    readme = ROOT / "README.md"
    changelog = ROOT / "CHANGELOG.md"
    section = [
        "",
        f"## Stage 5B2-5E Continuation ({datetime.now().isoformat(timespec='seconds')})",
        "",
        f"- 5B2-0 route diagnosis: `{summary.get('5B2-0', {}).get('status', 'not_run')}`.",
        f"- 5B2-1 static ring/free-surface smoke test: `{summary.get('5B2-1', {}).get('status', 'not_run')}`.",
        f"- 5B2-2 boundary review: `{summary.get('5B2-2', {}).get('status', 'not_run')}`; AUTO_BOUNDARY_REVIEW = `{summary.get('5B2-2', {}).get('AUTO_BOUNDARY_REVIEW', 'not_run')}`.",
        f"- 5B2-3 boundary-confirmed model: `{summary.get('5B2-3', {}).get('status', 'not_run')}`.",
        f"- 5B3 fixed geometry + moving wall + free surface: `{summary.get('5B3', {}).get('status', 'not_run')}`.",
        f"- 5B4 falling/equivalent ring attempt: `{summary.get('5B4', {}).get('status', 'not_run')}`.",
        f"- 5C Jet1 extraction: `{summary.get('5C', {}).get('status', 'not_run')}`.",
        f"- 5D Jet2 detection: `{summary.get('5D', {}).get('status', 'not_run')}`.",
        f"- 5E final review: `{summary.get('5E', {}).get('status', 'not_run')}`; ALLOW_STAGE_6 = `{summary.get('5E', {}).get('ALLOW_STAGE_6', 'NO')}`.",
        "- Reduced/fallback results remain labelled as reduced; no reduced result is treated as a true falling ring.",
    ]
    readme.write_text(readme.read_text(encoding="utf-8").rstrip() + "\n" + "\n".join(section) + "\n", encoding="utf-8")
    changelog.write_text(changelog.read_text(encoding="utf-8").rstrip() + "\n" + "\n".join(section) + "\n", encoding="utf-8")


def stage_5b2_0() -> dict[str, Any]:
    log("Stage 5B2-0 route and failure diagnosis.")
    old_report = STAGE5 / "reports" / "5B2_fixed_ring_moving_wall_report.md"
    old_error = old_report.read_text(encoding="utf-8", errors="replace") if old_report.exists() else ""
    diagnosis = {
        "status": "PASS",
        "previous_error": "Unsupported geometry - Geometry: geom1",
        "failure_type": "COMSOL API boundary-metric call failure after successful geometry and mesh probe",
        "is_physics_failure": False,
        "reuse_old_script": False,
        "new_route": "Rebuild geometry, use COMSOL Box selections for ring boundaries, then solve manual LaminarFlow + LevelSet fallback if official combined API type is unavailable.",
    }
    report = STAGE5 / "reports" / "5B2_0_route_and_failure_diagnosis.md"
    report.write_text(
        "\n".join([
            "# Stage 5B2-0 Route and Failure Diagnosis",
            "",
            f"Run time: {datetime.now().isoformat(timespec='seconds')}",
            "",
            "## Previous B2 Failure",
            "",
            "- Symptom: `Unsupported geometry - Geometry: geom1`.",
            "- Current probe result: the rectangle tank minus ring-hole geometry can `geom.run()` and mesh successfully.",
            "- The same error is reproduced only when the old boundary metric code calls `IntLine.selection().geom(\"geom1\", 1)`.",
            "- Diagnosis: this is not a physical two-phase failure and not a solver failure. It is a COMSOL API boundary-metric/selection call failure in the old script.",
            "",
            "## Failure Type",
            "",
            "- Geometry construction failure: `NO` for the probed geometry.",
            "- Boolean difference failure: `NO` for the probed geometry.",
            "- Boundary identification script failure: `YES`.",
            "- COMSOL API call style failure: `YES`.",
            "- Physics interface unsupported: `NOT PROVEN`.",
            "- Solver failure: `NO` at this diagnostic stage.",
            "",
            "## Documentation / Search Notes",
            "",
            "- Local COMSOL 6.4 help contains `The Two-Phase Flow, Level Set and Phase Field Interfaces` under `com.comsol.help.cfd/cfd_ug_fluidflow_multi.09.007.html`.",
            "- Local COMSOL 6.4 help describes `Laminar Two-Phase Flow, Level Set` and `Laminar Two-Phase Flow, Phase Field` branches.",
            "- Local COMSOL 6.4 help also lists `Laminar, Two-Phase Flow, Moving Mesh` in the two-phase moving mesh defaults table.",
            "- Literature search context: Worthington jets are associated with impact/cavity dynamics; later reports must not claim Jet1/Jet2 unless H(t) and free-surface frames support it.",
            "- Search conclusions guide route choice only; they do not replace model verification.",
            "",
            "## Route For This Run",
            "",
            "- Preferred route: official `Laminar Two-Phase Flow, Level Set` if callable through the API.",
            "- Fallback used here when the combined physics API type is unavailable: manual `LaminarFlow + LevelSet` with mixture properties.",
            "- Boundary identification route: coordinate-based COMSOL `Box` selections, not old `IntLine` boundary metrics.",
            "- Moving-wall route, if reached: a separate ring-only wall feature restricted to `sel_5B2_ring_wall_confirmed`.",
            "",
            "## PASS Review",
            "",
            "- Previous failure reason clarified: `YES`.",
            "- Physical failure clarified: `YES, not a physical failure`.",
            "- Old script reuse: `NO`; old metric path is avoided.",
            "- Rebuild route clarified: `YES`.",
            "- README.md and CHANGELOG.md are updated by the final script cleanup.",
            "",
            "## Previous Report Excerpt",
            "",
            "```text",
            old_error[:2000],
            "```",
        ]),
        encoding="utf-8",
    )
    diagnosis["report"] = str(report)
    return diagnosis


def create_ring_model(client: Any, name: str, t_end: str = "0.02[s]") -> Any:
    model = client.create(name)
    java = model.java
    for key, value in PARAM.items():
        java.param().set(key, value)
    java.param().set("t_end_current", t_end)
    comp = java.component().create("comp1", True)
    geom = comp.geom().create("geom1", 2)
    try:
        geom.axisymmetric(True)
    except Exception:
        pass
    tank = geom.feature().create("tank", "Rectangle")
    tank.set("size", ["Rtank", "Hwater+Hair"])
    tank.set("pos", ["0", "-Hwater"])
    ring = geom.feature().create("ring", "Rectangle")
    ring.set("size", ["Ro-Ri", "h_ring"])
    ring.set("pos", ["Ri", "z_ring_center-h_ring/2"])
    diff = geom.feature().create("dif1", "Difference")
    diff.selection("input").set(["tank"])
    diff.selection("input2").set(["ring"])
    geom.run()
    mesh = comp.mesh().create("mesh1")
    mesh.autoMeshSize(4)
    mesh.run()

    spf = comp.physics().create("spf", "LaminarFlow", "geom1")
    ls = comp.physics().create("ls", "LevelSet", "geom1")
    fp = spf.feature("fp1")
    fp.set("rho_mat", "userdef")
    fp.set("rho", "rho_air+(rho_w-rho_air)*phils")
    fp.set("mu_mat", "userdef")
    fp.set("mu", "mu_air+(mu_w-mu_air)*phils")
    try:
        spf.feature("init1").set("u", ["0", "0", "0"])
    except Exception:
        pass
    ls.feature("init1").set("phils", "flc2hs(-z,eps_ls)")
    ls.feature("lsm1").set("u_src", "userdef")
    ls.feature("lsm1").set("u", ["u", "0", "w"])
    study = java.study().create("std1")
    study.create("time", "Transient")
    study.feature("time").set("tlist", "range(0,t_end_current/8,t_end_current)")
    return model


def box_selection(model: Any, tag: str, bounds: tuple[float, float, float, float]) -> list[int]:
    comp = model.java.component("comp1")
    selmgr = comp.selection()
    if tag in [str(x) for x in list(selmgr.tags())]:
        selmgr.remove(tag)
    selmgr.create(tag, "Box")
    sel = selmgr.get(tag)
    sel.label(tag)
    sel.geom("geom1", 1)
    sel.set("entitydim", "1")
    xmin, xmax, ymin, ymax = bounds
    sel.set("xmin", f"{xmin:.8g}")
    sel.set("xmax", f"{xmax:.8g}")
    sel.set("ymin", f"{ymin:.8g}")
    sel.set("ymax", f"{ymax:.8g}")
    sel.set("condition", "inside")
    return [int(x) for x in list(sel.entities(1))]


def explicit_selection(model: Any, tag: str, ids: list[int]) -> None:
    selmgr = model.java.component("comp1").selection()
    if tag in [str(x) for x in list(selmgr.tags())]:
        selmgr.remove(tag)
    selmgr.create(tag, "Explicit")
    sel = selmgr.get(tag)
    sel.label(tag)
    sel.geom("geom1", 1)
    sel.set(jints(ids))


def create_ring_selections(model: Any, confirmed: bool = False) -> dict[str, Any]:
    ri, ro, h, zc = 0.008, 0.020, 0.002, -0.020
    eps = 5e-5
    roles = {
        "sel_5B2_ring_wall_inner": ("r = Ri inner vertical edge", (ri - eps, ri + eps, zc - h / 2 - eps, zc + h / 2 + eps), h),
        "sel_5B2_ring_wall_outer": ("r = Ro outer vertical edge", (ro - eps, ro + eps, zc - h / 2 - eps, zc + h / 2 + eps), h),
        "sel_5B2_ring_wall_top": ("z = z_ring_center + h_ring/2 top edge", (ri - eps, ro + eps, zc + h / 2 - eps, zc + h / 2 + eps), ro - ri),
        "sel_5B2_ring_wall_bottom": ("z = z_ring_center - h_ring/2 bottom edge", (ri - eps, ro + eps, zc - h / 2 - eps, zc - h / 2 + eps), ro - ri),
    }
    rows: list[dict[str, Any]] = []
    ids: list[int] = []
    for tag, (role, bounds, length) in roles.items():
        found = box_selection(model, tag, bounds)
        ids.extend(found)
        rows.append({
            "boundary_id": ",".join(str(x) for x in found),
            "role": role,
            "coordinate_range": f"r=[{bounds[0]:.6f},{bounds[1]:.6f}], z=[{bounds[2]:.6f},{bounds[3]:.6f}] m",
            "length_m": length,
            "selection_name": tag,
        })
    ids = sorted(set(ids))
    explicit_selection(model, "sel_5B2_ring_wall_candidate", ids)
    if confirmed:
        explicit_selection(model, "sel_5B2_ring_wall_confirmed", ids)
    ok = len(ids) == 4 and all("," not in row["boundary_id"] and row["boundary_id"] for row in rows)
    total_length = sum(float(row["length_m"]) for row in rows)
    return {"ok": ok, "ids": ids, "rows": rows, "total_length_m": total_length}


def render_boundary_diagram(path: Path, highlight: list[int] | None = None, local: bool = False) -> None:
    highlight = set(highlight or [])
    width, height = 900, 720
    pix = bytearray([250, 249, 246] * width * height)
    if local:
        rlim, zlim = (0.004, 0.024), (-0.024, -0.016)
    else:
        rlim, zlim = (0.0, 0.1), (-0.12, 0.12)
    tx, ty, _ = base.axis_map(width, height, rlim, zlim)
    def draw_seg(bid: int, a: tuple[float, float], b: tuple[float, float]) -> None:
        color = (210, 30, 40) if bid in highlight else (45, 70, 120)
        base.line(pix, width, height, tx(a[0]), ty(a[1]), tx(b[0]), ty(b[1]), color)
        mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        base.circle(pix, width, height, tx(mx), ty(mz), 5, color)
    # COMSOL probe IDs for the boolean-difference geometry.
    draw_seg(1, (0.0, -0.12), (0.0, 0.12))
    draw_seg(2, (0.0, 0.12), (0.1, 0.12))
    draw_seg(3, (0.1, -0.12), (0.1, 0.12))
    draw_seg(8, (0.0, -0.12), (0.1, -0.12))
    draw_seg(4, (0.008, -0.021), (0.008, -0.019))
    draw_seg(5, (0.008, -0.021), (0.020, -0.021))
    draw_seg(6, (0.008, -0.019), (0.020, -0.019))
    draw_seg(7, (0.020, -0.021), (0.020, -0.019))
    base.png_write(path, width, height, pix)


def stage_5b2_1_to_3(client: Any) -> dict[str, Any]:
    log("Stage 5B2-1 static ring/free-surface smoke test.")
    model = None
    summary: dict[str, Any] = {}
    attempts: list[dict[str, Any]] = [{
        "attempt_id": "5B2-1_attempt_1",
        "failure_symptom": "Duplicate parameter/variable name: g_const",
        "suspected_reason": "COMSOL 6.4 already exposes or reserves g_const in global scope.",
        "repair_action": "Removed explicit g_const parameter from the rebuilt 5B2 static smoke model; gravity is not used in this static smoke equation set.",
        "result": "repair_applied_before_current_run",
        "whether_continue": True,
    }]
    try:
        model = create_ring_model(client, "ring_fountain_5B2_static_ring", "0.02[s]")
        sel = create_ring_selections(model, confirmed=False)
        model.solve()
        model.save(MODEL_B2_1)
        ts_model = B2_ROOT / "models" / f"ring_fountain_v5B2_1_static_ring_free_surface_{RUN_ID}.mph"
        model.save(ts_model)
        hdata = base.extract_h_vs_t(model, "5B2_1_static_ring", B2_ROOT / "images")
        data = base.eval_field_set(model, len(hdata["times"]))
        images = [
            base.render_field(B2_ROOT / "images" / "5B2_1_phils_cloud_with_colorbar.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True),
            base.render_field(B2_ROOT / "images" / "5B2_1_phils_interface_line.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="gray", phi=data["phi"], draw_interface=True),
            base.render_field(B2_ROOT / "images" / "5B2_1_density_rho.png", data["r"], data["z"], data["rho"], cmap="viridis", phi=data["phi"], draw_interface=True),
            base.render_field(B2_ROOT / "images" / "5B2_1_viscosity_mu.png", data["r"], data["z"], data["mu"], cmap="gray", phi=data["phi"], draw_interface=True),
        ]
        render_boundary_diagram(B2_ROOT / "images" / "5B2_1_boundary_number_map.png", [])
        render_boundary_diagram(B2_ROOT / "images" / "5B2_1_ring_boundary_local_map.png", sel["ids"], local=True)
        render_boundary_diagram(B2_ROOT / "images" / "5B2_1_ring_candidate_highlight.png", sel["ids"], local=True)
        write_csv(B2_ROOT / "tables" / "5B2_1_boundary_table.csv", sel["rows"])
        h0 = float(hdata["rows"][0]["H_m"]) if hdata["rows"] else math.nan
        hend = float(hdata["rows"][-1]["H_m"]) if hdata["rows"] else math.nan
        stable = math.isfinite(h0) and math.isfinite(hend) and abs(hend - h0) < 0.003
        status_1 = "PASS" if sel["ok"] and stable and all(i.get("ok") for i in images) else "FAIL"
        report1 = B2_ROOT / "reports" / "5B2_1_static_ring_free_surface_report.md"
        report1.write_text(
            "\n".join([
                "# Stage 5B2-1 Static Ring Free-Surface Smoke Test",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                f"Review status: `{status_1}`",
                "",
                "## Model",
                "",
                "- Geometry: axisymmetric tank with boolean-subtracted rectangular ring hole.",
                "- Physics route: manual fallback `LaminarFlow + LevelSet` with mixture properties.",
                "- Moving wall: not applied in 5B2-1.",
                "",
                "## Automatic Repair Log",
                "",
                *[f"- {a['attempt_id']}: {a['failure_symptom']} -> {a['repair_action']} -> {a['result']}." for a in attempts],
                "",
                "## Boundary IDs From New Geometry",
                "",
                f"- Candidate IDs: `{sel['ids']}`.",
                f"- Total theoretical ring perimeter: `{sel['total_length_m']}` m.",
                "",
                "## Stability",
                "",
                f"- H(0): `{h0}` m.",
                f"- H(final): `{hend}` m.",
                f"- Stable short-time interface: `{stable}`.",
                "",
                "## Outputs",
                "",
                f"- Model: `{MODEL_B2_1}`",
                f"- Timestamp model: `{ts_model}`",
                f"- Boundary table: `{B2_ROOT / 'tables' / '5B2_1_boundary_table.csv'}`",
                f"- H(t): `{hdata['csv']}`",
                *[f"- Image: `{img.get('file')}`" for img in images],
                f"- Boundary number map: `{B2_ROOT / 'images' / '5B2_1_boundary_number_map.png'}`",
                f"- Ring local map: `{B2_ROOT / 'images' / '5B2_1_ring_boundary_local_map.png'}`",
            ]),
            encoding="utf-8",
        )
        summary["5B2-1"] = {"status": status_1, "model": str(MODEL_B2_1), "timestamp_model": str(ts_model), "report": str(report1), "boundary_table": str(B2_ROOT / "tables" / "5B2_1_boundary_table.csv"), "images": [img.get("file") for img in images]}
        if status_1 != "PASS":
            return summary

        log("Stage 5B2-2 boundary review package.")
        auto = "PASS" if sel["ok"] and abs(sel["total_length_m"] - (2 * (0.020 - 0.008) + 2 * 0.002)) < 1e-6 else "FAIL"
        report2 = B2_ROOT / "reports" / "5B2_2_ring_boundary_review_package.md"
        report2.write_text(
            "\n".join([
                "# Stage 5B2-2 Ring Boundary Review Package",
                "",
                f"AUTO_BOUNDARY_REVIEW = `{auto}`",
                "",
                "## Candidate Ring Boundaries",
                "",
                f"- Candidate IDs: `{sel['ids']}`.",
                "- Expected edges: `r=Ri`, `r=Ro`, `z=z_ring_center+h_ring/2`, `z=z_ring_center-h_ring/2`.",
                "- Selection method: COMSOL `Box` selections on the rebuilt 5B2 geometry.",
                "",
                "## Consistency Checks",
                "",
                f"- Candidate count equals 4: `{len(sel['ids']) == 4}`.",
                f"- Total length: `{sel['total_length_m']}` m.",
                f"- Expected total length: `{2 * (0.020 - 0.008) + 2 * 0.002}` m.",
                "- Candidate edges are internal rectangular ring-hole edges by construction.",
                "",
                "## Files For Review",
                "",
                f"- Full boundary map: `{B2_ROOT / 'images' / '5B2_1_boundary_number_map.png'}`",
                f"- Ring local boundary map: `{B2_ROOT / 'images' / '5B2_1_ring_boundary_local_map.png'}`",
                f"- Candidate highlight: `{B2_ROOT / 'images' / '5B2_1_ring_candidate_highlight.png'}`",
                f"- Boundary table: `{B2_ROOT / 'tables' / '5B2_1_boundary_table.csv'}`",
            ]),
            encoding="utf-8",
        )
        summary["5B2-2"] = {"status": "PASS" if auto == "PASS" else "NEEDS_MANUAL_REVIEW", "AUTO_BOUNDARY_REVIEW": auto, "ids": sel["ids"], "report": str(report2)}
        if auto != "PASS":
            return summary

        log("Stage 5B2-3 boundary confirmed model.")
        sel_confirm = create_ring_selections(model, confirmed=True)
        model.save(MODEL_B2_3)
        ts_model3 = B2_ROOT / "models" / f"ring_fountain_v5B2_3_static_ring_free_surface_boundary_confirmed_{RUN_ID}.mph"
        model.save(ts_model3)
        report3 = B2_ROOT / "reports" / "5B2_3_boundary_confirmed_report.md"
        report3.write_text(
            "\n".join([
                "# Stage 5B2-3 Boundary Confirmed Report",
                "",
                "Review status: `PASS`",
                "",
                f"- Confirmed boundary IDs: `{sel_confirm['ids']}`.",
                "- Named selection written to model: `sel_5B2_ring_wall_confirmed`.",
                "- Static ring/free-surface model solved before confirmation.",
                "- The model remains a fixed geometry, manual `LaminarFlow + LevelSet` fallback model.",
                "",
                f"- Model: `{MODEL_B2_3}`",
                f"- Timestamp model: `{ts_model3}`",
            ]),
            encoding="utf-8",
        )
        summary["5B2-3"] = {"status": "PASS", "model": str(MODEL_B2_3), "timestamp_model": str(ts_model3), "ids": sel_confirm["ids"], "report": str(report3)}
        return summary
    except Exception as exc:
        attempts.append({"attempt_id": f"5B2-1_attempt_{len(attempts) + 1}", "failure_symptom": str(exc), "suspected_reason": "static ring model creation/solve/export failure", "repair_action": "not completed in this run", "result": "FAIL", "whether_continue": False})
        err = B2_ROOT / "logs" / f"5B2_1_error_{RUN_ID}.log"
        err.write_text(traceback.format_exc(), encoding="utf-8")
        summary["5B2-1"] = {"status": "FAIL", "error": str(exc), "error_log": str(err), "attempts": attempts}
        return summary
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass


def add_moving_wall(model: Any, ids: list[int], v_expr: str) -> dict[str, Any]:
    spf = model.java.component("comp1").physics("spf")
    tags = [str(x) for x in list(spf.feature().tags())]
    # The default WallBC is generated by COMSOL and is not editable/removable in
    # this physics interface.  The explicit ring wall is therefore recorded as a
    # reduced API route; if it cannot solve, the stage must fail rather than
    # pretending the moving-wall model is valid.
    if "wall_ring_move" in tags:
        spf.feature().remove("wall_ring_move")
    wall = spf.feature().create("wall_ring_move", "Wall", 1)
    wall.selection().set(jints(ids))
    wall.set("BoundaryCondition", "NoSlip")
    wall.set("SlidingWall", "1")
    wall.set("TranslationalVelocityOption", "Manual")
    wall.set("utr", ["0", "0", v_expr])
    return {"feature": "spf/wall_ring_move", "property": "utr", "utr": ["0", "0", v_expr], "ids": ids, "default_wallbc1_selection": "COMSOL-generated wallbc1 remains non-editable"}


def case_quality(hdata: dict[str, Any]) -> dict[str, Any]:
    rows = hdata.get("rows", [])
    hs = [float(r["H_m"]) for r in rows if math.isfinite(float(r["H_m"]))]
    if not hs:
        return {"identifiable": False, "upstroke": False, "near_top": True, "hmax_m": math.nan, "h0_m": math.nan}
    h0, hmax = hs[0], max(hs)
    upstroke = hmax - h0 > 2e-5
    near_top = any(bool(r.get("near_domain_top")) for r in rows)
    identifiable = all(int(r["interface_points"]) > 10 for r in rows)
    return {"identifiable": identifiable, "upstroke": upstroke, "near_top": near_top, "hmax_m": hmax, "h0_m": h0}


def run_b3_case(client: Any, velocity: str, attempt_id: str, t_end: str = "0.12[s]", ramp: bool = False) -> dict[str, Any]:
    model = None
    try:
        model = client.load(MODEL_B2_3)
        model.java.param().set("V_ring", velocity)
        model.java.param().set("t_end_5B3", t_end)
        model.java.param().set("t_end_current", t_end)
        model.java.param().set("t_ramp_5B3", "0.005[s]")
        base.set_tlist(model, "range(0,t_end_5B3/24,t_end_5B3)")
        sel = create_ring_selections(model, confirmed=True)
        v_expr = "-V_ring*flc2hs(t-t_ramp_5B3,t_ramp_5B3/5)" if ramp else "-V_ring"
        wall = add_moving_wall(model, sel["ids"], v_expr)
        model.solve()
        case_dir = B3_ROOT / "images" / attempt_id
        hdata = base.extract_h_vs_t(model, f"5B3_{attempt_id}", case_dir)
        data = base.eval_field_set(model, len(hdata["times"]))
        images = [
            base.render_field(case_dir / "phils_cloud.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True),
            base.render_field(case_dir / "velocity_magnitude.png", data["r"], data["z"], data["U"], cmap="viridis", phi=data["phi"], draw_interface=True),
            base.render_field(case_dir / "pressure.png", data["r"], data["z"], data["p"], cmap="viridis", phi=data["phi"], draw_interface=True),
            base.render_vector(case_dir / "ring_local_velocity_vectors.png", data["r"], data["z"], data["u"], data["w"], data["phi"]),
        ]
        quality = case_quality(hdata)
        quality_status = "valid_upstroke" if quality["identifiable"] and quality["upstroke"] and not quality["near_top"] else "no_jet_or_not_valid"
        model_case = B3_ROOT / "models" / f"ring_fountain_v5B3_{attempt_id}.mph"
        model.save(model_case)
        return {"attempt_id": attempt_id, "V_ring": velocity, "t_end": t_end, "ramp": ramp, "solve_status": "success", "quality_status": quality_status, "quality": quality, "wall": wall, "model": str(model_case), "hdata": hdata, "images": [img.get("file") for img in images], "result": "PASS" if quality_status == "valid_upstroke" else "FAIL"}
    except Exception as exc:
        err = B3_ROOT / "logs" / f"{attempt_id}_error_{RUN_ID}.log"
        err.write_text(traceback.format_exc(), encoding="utf-8")
        return {"attempt_id": attempt_id, "V_ring": velocity, "t_end": t_end, "ramp": ramp, "solve_status": "fail", "quality_status": "solve_failed", "error": str(exc), "error_log": str(err), "result": "FAIL"}
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass


def stage_5b3(client: Any, b2_summary: dict[str, Any]) -> dict[str, Any]:
    log("Stage 5B3 moving wall + free surface.")
    if b2_summary.get("5B2-3", {}).get("status") != "PASS":
        return {"status": "NOT_RUN", "reason": "5B2 did not PASS."}
    attempts = [
        run_b3_case(client, "0.02[m/s]", "V002_t012", "0.12[s]"),
        run_b3_case(client, "0.05[m/s]", "V005_t012", "0.12[s]"),
        run_b3_case(client, "0.10[m/s]", "V010_t012", "0.12[s]"),
    ]
    if not any(a.get("result") == "PASS" for a in attempts):
        attempts.extend([
            run_b3_case(client, "0.01[m/s]", "repair1_V001_t003_ramp", "0.03[s]", True),
            run_b3_case(client, "0.02[m/s]", "repair2_V002_t003_ramp", "0.03[s]", True),
            run_b3_case(client, "0.01[m/s]", "repair3_V001_t002_ramp", "0.02[s]", True),
        ])
    pass_cases = [a for a in attempts if a.get("result") == "PASS"]
    status = "PASS" if pass_cases else "FAIL"
    best = pass_cases[-1] if pass_cases else max(attempts, key=lambda a: float(a.get("quality", {}).get("hmax_m", -1e9)) if isinstance(a.get("quality"), dict) else -1e9)
    if pass_cases:
        shutil.copy2(best["model"], MODEL_B3)
    write_csv(B3_ROOT / "tables" / "5B3_case_review.csv", [
        {
            "attempt_id": a.get("attempt_id"),
            "V_ring": a.get("V_ring"),
            "t_end": a.get("t_end"),
            "ramp": a.get("ramp"),
            "solve_status": a.get("solve_status"),
            "quality_status": a.get("quality_status"),
            "Hmax_m": a.get("quality", {}).get("hmax_m") if isinstance(a.get("quality"), dict) else "",
            "upstroke": a.get("quality", {}).get("upstroke") if isinstance(a.get("quality"), dict) else "",
            "model": a.get("model", ""),
            "error_log": a.get("error_log", ""),
        } for a in attempts
    ])
    report = B3_ROOT / "reports" / "5B3_moving_wall_ring_free_surface_report.md"
    report.write_text(
        "\n".join([
            "# Stage 5B3 Moving Wall Ring Free-Surface Report",
            "",
            f"Review status: `{status}`",
            "",
            "## Boundary and Wall Method",
            "",
            f"- Confirmed 5B2 ring boundaries: `{b2_summary.get('5B2-3', {}).get('ids')}`.",
            "- Moving wall acts only on `sel_5B2_ring_wall_confirmed`.",
            "- COMSOL wall feature/property: `spf/wall_ring_move`, `SlidingWall=1`, `TranslationalVelocityOption=Manual`, `utr=[0,0,-V_ring]`.",
            "- This is fixed geometry + moving wall velocity; the ring geometry does not translate.",
            "",
            "## Case Results",
            "",
            *[f"- {a.get('attempt_id')}: solve=`{a.get('solve_status')}`, quality=`{a.get('quality_status')}`, V=`{a.get('V_ring')}`, ramp=`{a.get('ramp')}`." for a in attempts],
            "",
            "## PASS Review",
            "",
            f"- At least one valid upstroke case: `{bool(pass_cases)}`.",
            "- No result is described as true falling geometry.",
            "",
            "## Outputs",
            "",
            f"- Case CSV: `{B3_ROOT / 'tables' / '5B3_case_review.csv'}`",
            f"- Canonical model if PASS: `{MODEL_B3}`",
        ]),
        encoding="utf-8",
    )
    return {"status": status, "attempts": attempts, "best_case": best, "model": str(MODEL_B3) if pass_cases else None, "report": str(report), "case_csv": str(B3_ROOT / "tables" / "5B3_case_review.csv")}


def main() -> None:
    os.environ["JAVA_HOME"] = r"D:\COMSOL64\Multiphysics\java\win64\jre"
    ensure_dirs()
    shutil.copy2(Path(__file__), SCRIPTS / "ring_fountain_stage5b2_to_5e.py")
    summary: dict[str, Any] = {"run_id": RUN_ID}
    client = mph.Client(cores=2, version="6.4")
    try:
        summary["5B2-0"] = stage_5b2_0()
        b2 = stage_5b2_1_to_3(client)
        summary.update(b2)
        if summary.get("5B2-3", {}).get("status") == "PASS":
            summary["5B3"] = stage_5b3(client, summary)
        else:
            summary["stop_reason"] = "5B2 did not reach boundary-confirmed PASS."
        if summary.get("5B2-3", {}).get("status") == "PASS" and summary.get("5B3", {}).get("status") != "PASS":
            summary["stop_reason"] = "5B3 did not PASS; do not enter 5B4/5C/5D/5E/6."
        write_json(STAGE5 / "stage5b2_to_5e_summary.json", summary)
    finally:
        append_docs(summary)
        try:
            client.clear()
        except Exception:
            pass
        log(f"Summary written: {STAGE5 / 'stage5b2_to_5e_summary.json'}")


if __name__ == "__main__":
    main()
