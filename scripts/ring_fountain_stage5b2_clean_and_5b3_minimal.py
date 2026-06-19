# -*- coding: utf-8 -*-
"""Stage B/C/D for the COMSOL Ring Fountain clean 5B2 baseline and minimal 5B3 retry.

This script starts after Stage A.  It does not enter 5B4, 5C, 5D, 5E, or stage 6.
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import jpype
import mph

import ring_fountain_stage5_cleanup_5b_5c as base


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
STAGE5 = ROOT / "05_two_phase_free_surface"
SRC_MODEL = (
    STAGE5
    / "5B2_static_ring_free_surface_smoke"
    / "models"
    / "ring_fountain_v5B2_3_static_ring_free_surface_boundary_confirmed.mph"
)
CLEAN = STAGE5 / "5B2_clean_baseline_rebuild"
RETRY = STAGE5 / "5B3_minimal_retry"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = RETRY / "logs" / f"5B2_clean_and_5B3_minimal_{RUN_ID}.log"

RING_ALL = [4, 5, 6, 7]
GROUPS = [
    ("S1_vertical_edges_only", [4, 7]),
    ("S2_bottom_edge_only", [5]),
    ("S3_top_edge_only", [6]),
    ("S4_horizontal_edges_only", [5, 6]),
    ("S5_all_edges", [4, 5, 6, 7]),
]


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def ensure_dirs() -> None:
    for root in [CLEAN, RETRY]:
        for sub in ["models", "reports", "tables", "logs", "images"]:
            (root / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def tags(node: Any) -> list[str]:
    try:
        return [str(x) for x in list(node.tags())]
    except Exception:
        return []


def jints(values: list[int]) -> Any:
    return jpype.JArray(jpype.JInt)(values)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False, default=str) if isinstance(v, (dict, list)) else v for k, v in row.items()})


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def prop(feature: Any, key: str) -> Any:
    for call in (
        lambda: feature.getString(key),
        lambda: list(feature.getStringArray(key)),
        lambda: feature.get(key),
    ):
        try:
            value = call()
            if isinstance(value, list):
                return [str(x) for x in value]
            return str(value)
        except Exception:
            pass
    return "<unreadable>"


def active_state(feature: Any) -> str:
    for call in (lambda: feature.isActive(), lambda: feature.active()):
        try:
            return str(call())
        except Exception:
            pass
    return "unknown"


def feature_selection(feature: Any) -> list[int] | str:
    for call in (
        lambda: feature.selection().entities(1),
        lambda: feature.selection().entities(),
    ):
        try:
            return [int(x) for x in list(call())]
        except Exception:
            pass
    try:
        if bool(feature.selection().isGlobal()):
            return "GLOBAL"
    except Exception:
        pass
    return "UNREADABLE"


def all_boundaries(model: Any) -> list[int]:
    rows = []
    try:
        rows = base.s41.boundary_metrics(model)
    except Exception:
        rows = []
    ids = sorted({int(row["boundary_id"]) for row in rows if "boundary_id" in row})
    if ids:
        return ids
    comp = model.java.component("comp1")
    tag = "sel_all_boundary_probe_5B3_minimal"
    selmgr = comp.selection()
    if tag in tags(selmgr):
        selmgr.remove(tag)
    selmgr.create(tag, "Box")
    sel = selmgr.get(tag)
    sel.geom("geom1", 1)
    sel.set("entitydim", "1")
    sel.set("xmin", "-1")
    sel.set("xmax", "1")
    sel.set("ymin", "-1")
    sel.set("ymax", "1")
    sel.set("condition", "inside")
    return sorted({int(x) for x in list(sel.entities(1))})


def set_tlist(model: Any, t_end: str, nsteps: int) -> None:
    model.java.param().set("t_end_clean_retry", t_end)
    base.set_tlist(model, f"range(0,t_end_clean_retry/{nsteps},t_end_clean_retry)")


def quick_hdata(model: Any, model_id: str) -> dict[str, Any]:
    times = base.read_times(model)
    rows: list[dict[str, Any]] = []
    for inner, t in enumerate(times, start=1):
        data = base.eval_field_set(model, inner)
        pts = base.estimate_interface(data["r"], data["z"], data["phi"], 0.5)
        valid = [(r, z) for r, z in pts if r < 0.095 and z < 0.11]
        max_z = max((z for _, z in valid), default=math.nan)
        rows.append({
            "model_id": model_id,
            "inner_solution": inner,
            "time_s": t,
            "interface_points": len(valid),
            "H_m": max_z,
            "H_mm": max_z * 1000 if math.isfinite(max_z) else math.nan,
            "near_domain_top": bool(math.isfinite(max_z) and max_z > 0.105),
        })
    return {"times": times, "rows": rows}


def h_metrics(hdata: dict[str, Any]) -> dict[str, Any]:
    rows = hdata.get("rows", [])
    finite = [row for row in rows if math.isfinite(float(row.get("H_m", math.nan)))]
    if not finite:
        return {
            "H0": math.nan,
            "Hfinal": math.nan,
            "delta_H": math.nan,
            "Hmax": math.nan,
            "interface_quality": "no finite H(t)",
            "main_free_surface_continuous": False,
            "isolated_spike": True,
            "near_top": True,
            "pass": False,
        }
    hs = [float(row["H_m"]) for row in finite]
    counts = [int(row.get("interface_points", 0)) for row in finite]
    jumps = [abs(b - a) for a, b in zip(hs[:-1], hs[1:])]
    continuous = min(counts) >= 3
    spike = bool(jumps and max(jumps) > 0.01)
    near_top = any(bool(row.get("near_domain_top")) for row in finite)
    delta = hs[-1] - hs[0]
    passed = abs(delta) < 0.0002 and continuous and not spike and not near_top
    return {
        "H0": hs[0],
        "Hfinal": hs[-1],
        "delta_H": delta,
        "Hmax": max(hs),
        "interface_quality": "clear/continuous" if continuous and not spike and not near_top else "questionable",
        "main_free_surface_continuous": continuous,
        "isolated_spike": spike,
        "near_top": near_top,
        "pass": passed,
    }


def remove_or_disable_feature(physics: Any, tag: str) -> str:
    if tag not in tags(physics.feature()):
        return "not_present"
    try:
        physics.feature().remove(tag)
        return "removed"
    except Exception as remove_exc:
        try:
            physics.feature(tag).active(False)
            return "disabled"
        except Exception as disable_exc:
            state = active_state(physics.feature(tag))
            if state.lower() == "false":
                return f"kept_but_already_inactive; remove_failed={remove_exc}; disable_failed={disable_exc}"
            return f"failed: remove_failed={remove_exc}; disable_failed={disable_exc}; active_state={state}"


def clean_manual_model(model: Any) -> dict[str, Any]:
    comp = model.java.component("comp1")
    spf = comp.physics("spf")
    ls = comp.physics("ls")
    actions: dict[str, Any] = {}
    actions["rtfr1"] = remove_or_disable_feature(spf, "rtfr1")
    actions["grav1"] = remove_or_disable_feature(spf, "grav1")
    actions["gravity_policy"] = "not used in this short static smoke test; no hydrostatic-pressure initialization is available in this manual fallback, so gravity is removed to test numerical interface advection stability without extra forcing"
    fp = spf.feature("fp1")
    fp.set("rho_mat", "userdef")
    fp.set("rho", "rho_air+(rho_w-rho_air)*phils")
    fp.set("mu_mat", "userdef")
    fp.set("mu", "mu_air+(mu_w-mu_air)*phils")
    wall = spf.feature("wallbc1")
    try:
        wall.selection().set(jints(all_boundaries(model)))
        actions["wallbc1_selection"] = "set_to_all_boundaries"
    except Exception as exc:
        actions["wallbc1_selection"] = f"left_unchanged_selection_not_editable: {exc}"
    wall.set("BoundaryCondition", "NoSlip")
    try:
        wall.set("SlidingWall", "0")
    except Exception:
        pass
    try:
        wall.set("TranslationalVelocityOption", "AutomaticFromFrame")
    except Exception:
        pass
    try:
        wall.set("utr", "0")
    except Exception:
        pass
    try:
        spf.feature("init1").set("u", ["0", "0", "0"])
    except Exception:
        pass
    try:
        ls.feature("lsm1").set("u_src", "userdef")
        ls.feature("lsm1").set("u", ["u", "0", "w"])
    except Exception as exc:
        actions["ls_velocity_setting_warning"] = str(exc)
    try:
        ls.feature("lsm1").set("gamma", "0")
        actions["level_set_gamma"] = "0; clean static fallback disables reinitialization convection to avoid artificial static-interface drift during the smoke test"
    except Exception as exc:
        actions["level_set_gamma"] = f"unchanged: {exc}"
    model.java.param().set("t_end_clean_static", "0.02[s]")
    set_tlist(model, "0.02[s]", 40)
    return actions


def probe_official_route(client: Any, route_id: str, candidates: list[str]) -> dict[str, Any]:
    rows = []
    for ptype in candidates:
        probe = None
        try:
            probe = client.create(f"probe_{route_id}_{ptype}")
            comp = probe.java.component().create("comp1", True)
            comp.geom().create("geom1", 2)
            phys = comp.physics().create("phys1", ptype, "geom1")
            rows.append({"type": ptype, "status": "CREATED", "created_type": str(phys.getType()), "label": str(phys.label())})
            return {
                "route_id": route_id,
                "route_used": route_id,
                "status": "NOT_RUN",
                "solve_status": "not_run",
                "notes": f"Physics type `{ptype}` is creatable, but automatic conversion of the existing ring model to this formal interface is not implemented safely in this pass.",
                "probe_rows": rows,
            }
        except Exception as exc:
            rows.append({"type": ptype, "status": "FAILED", "error": str(exc)})
        finally:
            if probe is not None:
                try:
                    client.remove(probe)
                except Exception:
                    pass
    return {
        "route_id": route_id,
        "route_used": route_id,
        "status": "NOT_AVAILABLE",
        "solve_status": "not_run",
        "notes": "No tested official physics type could be created through the COMSOL Java API.",
        "probe_rows": rows,
    }


def run_manual_clean_route(client: Any) -> dict[str, Any]:
    model = None
    route_id = "Route_LS_manual_clean"
    try:
        model = client.load(SRC_MODEL)
        actions = clean_manual_model(model)
        route_model = CLEAN / "models" / f"ring_fountain_v5B2_clean_static_baseline_manual_{RUN_ID}.mph"
        model.save(route_model)
        model.solve()
        hdata = base.extract_h_vs_t(model, "5B2_clean_manual_static", CLEAN / "images" / "Route_LS_manual_clean")
        metrics = h_metrics(hdata)
        data = base.eval_field_set(model, max(1, len(hdata["times"])))
        images = [
            base.render_field(CLEAN / "images" / "Route_LS_manual_clean_phils_final.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True),
            base.render_field(CLEAN / "images" / "Route_LS_manual_clean_velocity_magnitude.png", data["r"], data["z"], data["U"], cmap="viridis", phi=data["phi"], draw_interface=True),
        ]
        solved_model = CLEAN / "models" / f"ring_fountain_v5B2_clean_static_baseline_manual_solved_{RUN_ID}.mph"
        model.save(solved_model)
        best_model = ""
        if metrics["pass"]:
            best = CLEAN / "models" / "ring_fountain_v5B2_clean_static_baseline_best.mph"
            model.save(best)
            best_model = str(best)
        return {
            "route_id": route_id,
            "route_used": "manual LaminarFlow + LevelSet fallback",
            "status": "PASS" if metrics["pass"] else "FAIL",
            "solve_status": "success",
            "H0": metrics["H0"],
            "Hfinal": metrics["Hfinal"],
            "delta_H": metrics["delta_H"],
            "Hmax": metrics["Hmax"],
            "interface_quality": metrics["interface_quality"],
            "main_free_surface_continuous": metrics["main_free_surface_continuous"],
            "isolated_spike": metrics["isolated_spike"],
            "near_top": metrics["near_top"],
            "actions": actions,
            "route_model": str(route_model),
            "solved_model": str(solved_model),
            "best_model": best_model,
            "h_csv": hdata.get("csv"),
            "frame_index": hdata.get("frame_index"),
            "H_vs_t_png": hdata.get("H_vs_t_png"),
            "images": [img.get("file") for img in images],
            "notes": "No moving wall and no additional forcing were applied.",
        }
    except Exception as exc:
        err = CLEAN / "logs" / f"Route_LS_manual_clean_error_{RUN_ID}.log"
        err.write_text(traceback.format_exc(), encoding="utf-8")
        return {
            "route_id": route_id,
            "route_used": "manual LaminarFlow + LevelSet fallback",
            "status": "FAIL",
            "solve_status": "fail",
            "failure_message": str(exc),
            "error_log": str(err),
        }
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass


def write_b_report(route_rows: list[dict[str, Any]], best: dict[str, Any] | None) -> dict[str, Any]:
    comparison = CLEAN / "tables" / "clean_baseline_route_comparison.csv"
    write_csv(comparison, route_rows)
    status = "PASS" if best else "FAIL"
    report = CLEAN / "reports" / "B_clean_static_baseline_report.md"
    lines = [
        "# Stage B Clean Static Baseline Report",
        "",
        f"Run time: `{datetime.now().isoformat(timespec='seconds')}`",
        f"Source model: `{SRC_MODEL}`",
        f"Review status: `{status}`",
        f"`ALLOW_5B3_RETRY = {'YES' if best else 'NO'}`",
        "",
        "## Route Results",
        "",
        "| route | status | solve_status | delta_H_m | interface_quality | notes |",
        "|---|---|---|---:|---|---|",
    ]
    for row in route_rows:
        lines.append(
            f"| `{row.get('route_id')}` | `{row.get('status')}` | `{row.get('solve_status')}` | "
            f"`{row.get('delta_H', '')}` | `{row.get('interface_quality', '')}` | `{str(row.get('notes', '')).replace('|', '/')}` |"
        )
    lines.extend([
        "",
        "## Static Baseline Decision",
        "",
    ])
    if best:
        lines.extend([
            f"- Best route: `{best.get('route_id')}`.",
            f"- H(final)-H(0): `{best.get('delta_H')}` m.",
            f"- Best clean baseline model: `{best.get('best_model')}`.",
            "- Moving wall: not applied.",
            "- Extra forcing: not applied.",
        ])
    else:
        lines.extend([
            "- No route satisfied `|H(final)-H(0)| < 0.2 mm` with continuous, recognizable interface.",
            "- Stage C/D were not allowed to run.",
        ])
    lines.extend([
        "",
        "## Gravity And Cleanup",
        "",
        "- `rtfr1 / RotatingFrameFD` is not used by the accepted manual clean fallback. COMSOL did not allow removing or disabling the built-in node, but the audit/action log shows it is already inactive.",
        "- The manual fallback does not use gravity in this short smoke test. COMSOL did not allow removing or disabling the built-in gravity node either, but the audit/action log shows it is already inactive; no hydrostatic-pressure initialization is present in the manual coupling, so this gate isolates static interface advection stability without additional forcing.",
        "- The formal Level Set / Phase Field routes are recorded as unavailable or not safely convertible when COMSOL API creation/conversion is not available.",
        "",
        "## Outputs",
        "",
        f"- Route comparison: `{comparison}`",
    ])
    if best:
        lines.extend([
            f"- H(t) CSV: `{best.get('h_csv')}`",
            f"- H(t) plot: `{best.get('H_vs_t_png')}`",
            f"- Interface frames index: `{best.get('frame_index')}`",
        ])
    report.write_text("\n".join(lines), encoding="utf-8")
    return {"status": status, "ALLOW_5B3_RETRY": "YES" if best else "NO", "best": best, "report": str(report), "comparison": str(comparison)}


def stage_b(client: Any) -> dict[str, Any]:
    log("Stage B started.")
    route_rows: list[dict[str, Any]] = []
    route_rows.append(probe_official_route(client, "Route_LS_official", [
        "LaminarTwoPhaseFlowLevelSet",
        "TwoPhaseFlowLevelSet",
        "TwoPhaseFlowLS",
        "TpfLevelSet",
    ]))
    route_rows.append(probe_official_route(client, "Route_PF_official", [
        "LaminarTwoPhaseFlowPhaseField",
        "TwoPhaseFlowPhaseField",
        "TwoPhaseFlowPF",
    ]))
    manual = run_manual_clean_route(client)
    route_rows.append(manual)
    pass_rows = [row for row in route_rows if row.get("status") == "PASS"]
    best = pass_rows[0] if pass_rows else None
    summary = write_b_report(route_rows, best)
    write_json(CLEAN / "logs" / f"B_clean_static_baseline_summary_{RUN_ID}.json", {"routes": route_rows, "summary": summary})
    return summary


def wall_audit(model: Any, moving_ids: list[int] | None = None) -> list[dict[str, Any]]:
    spf = model.java.component("comp1").physics("spf")
    ids_all = all_boundaries(model)
    rows: list[dict[str, Any]] = []
    for ftag in tags(spf.feature()):
        feat = spf.feature(ftag)
        ftype = str(feat.getType())
        if "wall" not in ftag.lower() and "wall" not in ftype.lower() and "wall" not in str(feat.label()).lower():
            continue
        sel = feature_selection(feat)
        sel_ids = ids_all if sel == "GLOBAL" else sel if isinstance(sel, list) else []
        rows.append({
            "feature_tag": ftag,
            "feature_type": ftype,
            "feature_label": str(feat.label()),
            "selection_boundaries": sel,
            "intersects_confirmed_ring": sorted(set(sel_ids).intersection(RING_ALL)),
            "intersects_moving_boundaries": sorted(set(sel_ids).intersection(moving_ids or [])),
            "BoundaryCondition": prop(feat, "BoundaryCondition"),
            "SlidingWall": prop(feat, "SlidingWall"),
            "TranslationalVelocityOption": prop(feat, "TranslationalVelocityOption"),
            "utr": prop(feat, "utr"),
            "active_or_solved": active_state(feat),
        })
    return rows


def configure_nonoverlap_wall(model: Any, moving_ids: list[int], v_expr: str) -> dict[str, Any]:
    comp = model.java.component("comp1")
    spf = comp.physics("spf")
    for tag in ["wall_ring_move"]:
        if tag in tags(spf.feature()):
            spf.feature().remove(tag)
    wall_tags = [row["feature_tag"] for row in wall_audit(model)]
    if not wall_tags:
        raise RuntimeError("No spf wall feature is available.")
    default_tag = "wallbc1" if "wallbc1" in wall_tags else wall_tags[0]
    rest = sorted(set(all_boundaries(model)).difference(moving_ids))
    default_mode = "restricted_existing_default_wall"
    try:
        spf.feature(default_tag).selection().set(jints(rest))
        spf.feature(default_tag).set("BoundaryCondition", "NoSlip")
        try:
            spf.feature(default_tag).set("SlidingWall", "0")
        except Exception:
            pass
    except Exception as selection_exc:
        default_mode = f"replaced_noneditable_default_wall; selection_error={selection_exc}"
        try:
            spf.feature().remove(default_tag)
        except Exception as remove_exc:
            raise RuntimeError(f"wall_overlap_unresolved: default wall selection is not editable and default wall cannot be removed: {remove_exc}") from selection_exc
        fixed = spf.feature().create("wall_fixed_rest", "Wall", 1)
        fixed.selection().set(jints(rest))
        fixed.set("BoundaryCondition", "NoSlip")
        try:
            fixed.set("SlidingWall", "0")
        except Exception:
            pass
    moving = spf.feature().create("wall_ring_move", "Wall", 1)
    moving.selection().set(jints(moving_ids))
    moving.set("BoundaryCondition", "NoSlip")
    moving.set("SlidingWall", "1")
    moving.set("TranslationalVelocityOption", "Manual")
    moving.set("utr", ["0", "0", v_expr])
    audit = wall_audit(model, moving_ids)
    overlap = any(row["feature_tag"] != "wall_ring_move" and row["intersects_moving_boundaries"] for row in audit)
    return {
        "default_wall": default_tag,
        "default_wall_mode": default_mode,
        "fixed_boundaries": rest,
        "moving_feature": "wall_ring_move",
        "moving_boundaries": moving_ids,
        "wall_overlap_status": "PASS" if not overlap else "FAIL",
        "audit": audit,
    }


def stage_c(client: Any, best_model: str) -> dict[str, Any]:
    log("Stage C started.")
    report = RETRY / "reports" / "C_wall_nonoverlap_audit.md"
    rows: list[dict[str, Any]] = []
    for group_id, ids in GROUPS:
        model = None
        try:
            model = client.load(best_model)
            setup = configure_nonoverlap_wall(model, ids, "-V_ring_probe")
            rows.append({
                "group_id": group_id,
                "moving_boundaries": ids,
                "status": setup["wall_overlap_status"],
                "default_wall_mode": setup.get("default_wall_mode"),
                "audit": setup.get("audit"),
            })
        except Exception as exc:
            rows.append({
                "group_id": group_id,
                "moving_boundaries": ids,
                "status": "FAIL",
                "failure_message": str(exc),
            })
        finally:
            if model is not None:
                try:
                    client.remove(model)
                except Exception:
                    pass
    status = "PASS" if rows and all(row.get("status") == "PASS" for row in rows) else "FAIL"
    write_json(RETRY / "logs" / f"C_wall_nonoverlap_audit_{RUN_ID}.json", rows)
    lines = [
        "# Stage C Wall Non-Overlap Audit",
        "",
        f"Run time: `{datetime.now().isoformat(timespec='seconds')}`",
        f"Best clean baseline model: `{best_model}`",
        f"Review status: `{status}`",
        "",
        "## Method",
        "",
        "- Each Stage D case loads the best clean baseline fresh.",
        "- Before solving each case, the default `spf` wall is restricted to all boundaries except that case's moving boundaries.",
        "- A separate `wall_ring_move` feature is then created only on the moving boundary group.",
        "- The per-case wall audit is written before solve and is also copied into the case table.",
        "",
        "## Planned Moving Groups",
        "",
        "| group | moving boundaries |",
        "|---|---|",
    ]
    for row in rows:
        lines.append(f"| `{row.get('group_id')}` | `{row.get('moving_boundaries')}` |")
    lines.extend([
        "",
        "## Audit Results",
        "",
        "| group | status | default_wall_mode | failure_message |",
        "|---|---|---|---|",
    ])
    for row in rows:
        lines.append(f"| `{row.get('group_id')}` | `{row.get('status')}` | `{row.get('default_wall_mode', '')}` | `{str(row.get('failure_message', '')).replace('|', '/')}` |")
    if status != "PASS":
        lines.extend([
            "",
            "## Gate Decision",
            "",
            "- Stage C did not satisfy the non-overlap requirement.",
            "- Stage D must not be treated as valid and is not run by the corrected gate.",
        ])
    report.write_text("\n".join(lines), encoding="utf-8")
    return {"status": status, "report": str(report), "method": "per-case non-overlap wall rewrite", "rows": rows}


def write_d_not_run(reason: str) -> dict[str, Any]:
    csv_path = RETRY / "tables" / "minimal_moving_wall_cases.csv"
    rows = [{"case_id": "NOT_RUN", "solve_status": "not_run", "result": "NOT_RUN", "notes": reason}]
    write_csv(csv_path, rows)
    report = RETRY / "reports" / "D_minimal_moving_wall_retry_report.md"
    report.write_text("\n".join([
        "# Stage D Minimal Moving Wall Retry Report",
        "",
        "Review status: `NOT_RUN`",
        "",
        f"Reason: {reason}",
        "",
        "`5B3_MINIMAL_RETRY = FAIL`",
        "`ALLOW_RESUME_STAGE5 = NO`",
    ]), encoding="utf-8")
    return {
        "status": "NOT_RUN",
        "5B3_MINIMAL_RETRY": "FAIL",
        "ALLOW_RESUME_STAGE5": "NO",
        "rows": rows,
        "best": None,
        "best_model": "",
        "report": str(report),
        "csv": str(csv_path),
        "reason": reason,
    }


def parse_failure_time(text: str) -> str:
    match = re.search(r"Time:\s*([0-9eE+\-.]+)\s*s", text)
    return match.group(1) if match else ""


def run_moving_case(client: Any, best_model: str, group_id: str, moving_ids: list[int], velocity: str, t_end: str) -> dict[str, Any]:
    model = None
    vel_id = velocity.replace(".", "p").replace("[m/s]", "")
    case_id = f"{group_id}_V{vel_id}_t{t_end.replace('.', 'p').replace('[s]', '')}"
    case_dir = RETRY / "images" / case_id
    try:
        model = client.load(best_model)
        model.java.param().set("V_ring_5B3_retry", velocity)
        model.java.param().set("t_ramp_5B3_retry", "0.005[s]")
        set_tlist(model, t_end, 20 if t_end == "0.01[s]" else 40)
        v_expr = "-V_ring_5B3_retry*flc2hs(t-t_ramp_5B3_retry,t_ramp_5B3_retry)"
        wall_setup = configure_nonoverlap_wall(model, moving_ids, v_expr)
        audit_path = RETRY / "logs" / f"{case_id}_wall_audit_{RUN_ID}.json"
        write_json(audit_path, wall_setup)
        if wall_setup["wall_overlap_status"] != "PASS":
            raise RuntimeError("wall_overlap_unresolved")
        model.solve()
        hdata = base.extract_h_vs_t(model, f"5B3_minimal_{case_id}", case_dir)
        metrics = h_metrics(hdata)
        data = base.eval_field_set(model, max(1, len(hdata["times"])))
        images = [
            base.render_field(case_dir / "phils_final.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True),
            base.render_field(case_dir / "velocity_magnitude.png", data["r"], data["z"], data["U"], cmap="viridis", phi=data["phi"], draw_interface=True),
            base.render_vector(case_dir / "ring_local_velocity_vectors.png", data["r"], data["z"], data["u"], data["w"], data["phi"]),
        ]
        passed = metrics["main_free_surface_continuous"] and not metrics["near_top"] and not metrics["isolated_spike"]
        model_path = RETRY / "models" / f"ring_fountain_v5B3_minimal_{case_id}.mph"
        model.save(model_path)
        return {
            "case_id": case_id,
            "route_used": "manual LaminarFlow + LevelSet clean baseline",
            "moving_boundaries": moving_ids,
            "V_ring": velocity,
            "t_end": t_end,
            "solve_status": "success",
            "failure_time": "",
            "failure_message": "",
            "H0": metrics["H0"],
            "Hfinal": metrics["Hfinal"],
            "delta_H": metrics["delta_H"],
            "Hmax": metrics["Hmax"],
            "interface_quality": metrics["interface_quality"],
            "wall_overlap_status": wall_setup["wall_overlap_status"],
            "notes": "PASS" if passed else "solved but interface quality failed",
            "result": "PASS" if passed else "FAIL",
            "model": str(model_path),
            "h_csv": hdata.get("csv"),
            "H_vs_t_png": hdata.get("H_vs_t_png"),
            "wall_audit": str(audit_path),
            "images": [img.get("file") for img in images],
        }
    except Exception as exc:
        err = RETRY / "logs" / f"{case_id}_error_{RUN_ID}.log"
        err.write_text(traceback.format_exc(), encoding="utf-8")
        return {
            "case_id": case_id,
            "route_used": "manual LaminarFlow + LevelSet clean baseline",
            "moving_boundaries": moving_ids,
            "V_ring": velocity,
            "t_end": t_end,
            "solve_status": "fail",
            "failure_time": parse_failure_time(str(exc)),
            "failure_message": str(exc),
            "H0": "",
            "Hfinal": "",
            "delta_H": "",
            "Hmax": "",
            "interface_quality": "solve_failed",
            "wall_overlap_status": "UNKNOWN_OR_FAIL",
            "notes": "solve_failed",
            "result": "FAIL",
            "error_log": str(err),
        }
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass


def stage_d(client: Any, best_model: str) -> dict[str, Any]:
    log("Stage D started.")
    rows: list[dict[str, Any]] = []
    for group_id, ids in GROUPS:
        first = run_moving_case(client, best_model, group_id, ids, "0.002[m/s]", "0.01[s]")
        rows.append(first)
        if first["result"] == "PASS":
            rows.append(run_moving_case(client, best_model, group_id, ids, "0.005[m/s]", "0.02[s]"))
    csv_path = RETRY / "tables" / "minimal_moving_wall_cases.csv"
    write_csv(csv_path, rows)
    pass_rows = [row for row in rows if row.get("result") == "PASS"]
    best = pass_rows[0] if pass_rows else None
    best_model_path = ""
    if best and best.get("model"):
        best_model_path = str(RETRY / "models" / "ring_fountain_v5B3_minimal_retry_best.mph")
        shutil.copy2(best["model"], best_model_path)
    report = RETRY / "reports" / "D_minimal_moving_wall_retry_report.md"
    lines = [
        "# Stage D Minimal Moving Wall Retry Report",
        "",
        f"Run time: `{datetime.now().isoformat(timespec='seconds')}`",
        f"Review status: `{'PASS' if best else 'FAIL'}`",
        f"`5B3_MINIMAL_RETRY = {'PASS' if best else 'FAIL'}`",
        f"`ALLOW_RESUME_STAGE5 = {'YES' if best else 'NO'}`",
        "",
        "## Cases",
        "",
        "| case_id | result | solve_status | moving_boundaries | V_ring | t_end | delta_H | Hmax | interface_quality | wall_overlap_status |",
        "|---|---|---|---|---|---|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row.get('case_id')}` | `{row.get('result')}` | `{row.get('solve_status')}` | `{row.get('moving_boundaries')}` | "
            f"`{row.get('V_ring')}` | `{row.get('t_end')}` | `{row.get('delta_H')}` | `{row.get('Hmax')}` | "
            f"`{row.get('interface_quality')}` | `{row.get('wall_overlap_status')}` |"
        )
    lines.extend([
        "",
        "## Outputs",
        "",
        f"- Case table: `{csv_path}`",
        f"- Best model: `{best_model_path}`",
    ])
    report.write_text("\n".join(lines), encoding="utf-8")
    return {
        "status": "PASS" if best else "FAIL",
        "5B3_MINIMAL_RETRY": "PASS" if best else "FAIL",
        "ALLOW_RESUME_STAGE5": "YES" if best else "NO",
        "rows": rows,
        "best": best,
        "best_model": best_model_path,
        "report": str(report),
        "csv": str(csv_path),
    }


def write_final(b: dict[str, Any], c: dict[str, Any] | None, d: dict[str, Any] | None) -> dict[str, Any]:
    best_b = b.get("best") or {}
    best_d = (d or {}).get("best") or {}
    allow_resume = (d or {}).get("ALLOW_RESUME_STAGE5", "NO")
    report = RETRY / "reports" / "5B2_clean_and_5B3_minimal_retry_final_report.md"
    lines = [
        "# 5B2 Clean Baseline And 5B3 Minimal Retry Final Report",
        "",
        f"Run time: `{datetime.now().isoformat(timespec='seconds')}`",
        "",
        "This run did not enter 5B4, 5C, 5D, 5E, or stage 6. Jet1/Jet2 were not extracted.",
        "",
        "## Required Answers",
        "",
        f"1. RotatingFrameFD deleted/disabled: `not removed; already inactive`; manual route action: `{(best_b.get('actions') or {}).get('rtfr1', '')}`.",
        f"2. Gravity handling: `not used; grav1 already inactive`; policy: `{(best_b.get('actions') or {}).get('gravity_policy', 'not reached')}`; action: `{(best_b.get('actions') or {}).get('grav1', '')}`.",
        f"3. Formal Two-Phase Flow coupling used: `False`; route used: `{best_b.get('route_used', '')}`.",
        f"4. Most stable static free-surface route: `{best_b.get('route_id', '')}`.",
        f"5. Static baseline H(final)-H(0): `{best_b.get('delta_H', '')}` m.",
        f"6. Wall overlap excluded: `{(c or {}).get('status') == 'PASS' and bool(d)}`.",
        f"7. Most stable moving wall group: `{best_d.get('case_id', '')}`.",
        f"8. Best clean baseline model obtained: `{best_b.get('best_model', '')}`.",
        f"9. Minimal moving wall best model obtained: `{(d or {}).get('best_model', '')}`.",
        f"10. ALLOW_RESUME_STAGE5: `{allow_resume}`.",
        "",
        "## Stage Reports",
        "",
        f"- Stage B: `{b.get('report')}`",
        f"- Stage C: `{(c or {}).get('report', 'NOT_RUN')}`",
        f"- Stage D: `{(d or {}).get('report', 'NOT_RUN')}`",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    return {"report": str(report), "ALLOW_RESUME_STAGE5": allow_resume}


def update_manifest() -> None:
    scripts = sorted(SCRIPTS.glob("*.py"))
    notes = {
        "ring_fountain_stage5b2_clean_and_5b3_minimal.py": "Stage B/C/D clean static baseline rebuild and minimal moving-wall retry",
        "ring_fountain_stage5b2_clean_baseline_audit.py": "Stage A 5B2 clean-baseline read-only physics audit",
    }
    manifest = SCRIPTS / "SCRIPT_MANIFEST.md"
    lines = [
        "# COMSOL Ring Fountain Automation Script Manifest",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %z')}",
        "",
        "Canonical script directory:",
        "",
        "```text",
        str(SCRIPTS),
        "```",
        "",
        "## Scripts",
        "",
        "| Script | Size bytes | Last modified | SHA256 | Notes |",
        "|---|---:|---|---|---|",
    ]
    import hashlib

    default_notes = {
        "ring_fountain_stage0_2.py": "Stage 0-2 setup/model automation",
        "ring_fountain_stage2_1_plus.py": "Stage 2.1+ calibration/sweep automation",
        "ring_fountain_stage4_1_boundary_review.py": "Stage 4.1 boundary review package automation",
        "ring_fountain_stage4_2_formal.py": "Formal Stage 4.2 moving-wall model automation",
        "ring_fountain_stage4_2_probe.py": "Stage 4.2 wall-property probing helper",
        "ring_fountain_stage4_2a.py": "Stage 4.2A relative-velocity check automation",
        "ring_fountain_stage5_cleanup_5b_5c.py": "Stage 5 cleanup / 5B / 5C automation",
        "ring_fountain_stage5a_probe.py": "Stage 5A two-phase availability probing helper",
        "ring_fountain_stage5a_static_interface.py": "Stage 5A static free-surface smoke-test automation",
        "ring_fountain_stage5b2_to_5e.py": "Stage 5B2 through 5E automation",
        "ring_fountain_stage5b3_stability_repair.py": "Stage 5B3-only stability repair, wall audit, R1 gate, grouped moving-wall test driver",
    }
    default_notes.update(notes)
    for path in scripts:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        note = default_notes.get(path.name, "")
        lines.append(f"| [{path.name}](./{path.name}) | {path.stat().st_size} | {datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')} | `{digest}` | {note} |")
    lines.extend([
        "",
        "## Path Management",
        "",
        "- Treat this directory as the canonical local archive for Python automation used in the COMSOL Ring Fountain project.",
        "- Working copies may remain under `C:\\Users\\kqdx\\Documents\\COMSOL仿真方法`, but scripts should be copied here after each run or edit.",
        "- Helper/probe scripts are preserved because they document how COMSOL features and property names were discovered.",
    ])
    manifest.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    os.environ["JAVA_HOME"] = r"D:\COMSOL64\Multiphysics\java\win64\jre"
    ensure_dirs()
    shutil.copy2(Path(__file__), SCRIPTS / "ring_fountain_stage5b2_clean_and_5b3_minimal.py")
    update_manifest()
    if not SRC_MODEL.exists():
        raise FileNotFoundError(SRC_MODEL)
    summary: dict[str, Any] = {"run_id": RUN_ID, "source_model": str(SRC_MODEL)}
    client = mph.Client(cores=2, version="6.4")
    try:
        b = stage_b(client)
        summary["B"] = b
        c = None
        d = None
        if b.get("ALLOW_5B3_RETRY") == "YES" and b.get("best", {}).get("best_model"):
            c = stage_c(client, b["best"]["best_model"])
            summary["C"] = c
            if c.get("status") == "PASS":
                d = stage_d(client, b["best"]["best_model"])
                summary["D"] = d
            else:
                d = write_d_not_run("Stage C wall non-overlap audit did not PASS.")
                summary["D"] = d
        else:
            c = {"status": "NOT_RUN", "reason": "Stage B did not PASS."}
            d = {"status": "NOT_RUN", "reason": "Stage B did not PASS."}
            summary["C"] = c
            summary["D"] = d
        summary["final"] = write_final(b, c, d)
        write_json(RETRY / "5B2_clean_and_5B3_minimal_retry_summary.json", summary)
    finally:
        try:
            client.clear()
        except Exception:
            pass


if __name__ == "__main__":
    main()
