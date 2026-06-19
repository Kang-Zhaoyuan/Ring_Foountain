# -*- coding: utf-8 -*-
"""Stage 5B3 stability repair only.

This script deliberately stops at 5B3.  It audits wall features, re-checks the
static free-surface baseline, and then tests grouped moving-wall cases without
entering 5B4/5C/5D/5E/6.
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
SRC_MODEL = STAGE5 / "5B2_static_ring_free_surface_smoke" / "models" / "ring_fountain_v5B2_3_static_ring_free_surface_boundary_confirmed.mph"
REPAIR = STAGE5 / "5B3_stability_repair"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = REPAIR / "logs" / f"5B3_stability_repair_{RUN_ID}.log"

RING_ALL = [4, 5, 6, 7]
GROUPS = {
    "S1_vertical_edges_only": [4, 7],
    "S2_bottom_edge_only": [5],
    "S3_top_edge_only": [6],
    "S4_horizontal_edges_only": [5, 6],
    "S5_all_edges": [4, 5, 6, 7],
}


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def ensure_dirs() -> None:
    for sub in ["models", "reports", "tables", "logs", "images", "images/frames"]:
        (REPAIR / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def tags(node: Any) -> list[str]:
    try:
        return [str(x) for x in list(node.tags())]
    except Exception:
        return []


def jints(values: list[int]) -> Any:
    return jpype.JArray(jpype.JInt)(values)


def prop(feature: Any, key: str) -> Any:
    try:
        return str(feature.getString(key))
    except Exception:
        try:
            return [str(x) for x in list(feature.getStringArray(key))]
        except Exception:
            try:
                return str(feature.get(key))
            except Exception as exc:
                return f"<unreadable: {exc}>"


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
            return "GLOBAL_ALL_BOUNDARIES"
    except Exception:
        pass
    return "UNREADABLE_SELECTION"


def get_all_boundaries(model: Any) -> list[int]:
    comp = model.java.component("comp1")
    tag = "sel_5B3_all_boundaries_probe"
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
    ids = [int(x) for x in list(sel.entities(1))]
    return sorted(set(ids))


def wall_audit(model: Any) -> tuple[list[dict[str, Any]], list[int]]:
    spf = model.java.component("comp1").physics("spf")
    all_boundaries = get_all_boundaries(model)
    rows: list[dict[str, Any]] = []
    for ftag in tags(spf.feature()):
        feat = spf.feature(ftag)
        ftype = str(feat.getType())
        is_wall = "wall" in ftag.lower() or "wall" in ftype.lower() or "wall" in str(feat.label()).lower()
        if not is_wall:
            continue
        sel = feature_selection(feat)
        if sel == "GLOBAL_ALL_BOUNDARIES":
            sel_for_overlap = all_boundaries
        elif isinstance(sel, list):
            sel_for_overlap = sel
        else:
            sel_for_overlap = []
        rows.append({
            "feature_tag": ftag,
            "feature_type": ftype,
            "selection_boundaries": sel,
            "selection_intersects_ring": sorted(set(sel_for_overlap).intersection(RING_ALL)),
            "BoundaryCondition": prop(feat, "BoundaryCondition"),
            "SlidingWall": prop(feat, "SlidingWall"),
            "TranslationalVelocityOption": prop(feat, "TranslationalVelocityOption"),
            "utr": prop(feat, "utr"),
        })
    return rows, all_boundaries


def spf_feature_inventory(model: Any) -> list[dict[str, Any]]:
    spf = model.java.component("comp1").physics("spf")
    rows: list[dict[str, Any]] = []
    for ftag in tags(spf.feature()):
        feat = spf.feature(ftag)
        rows.append({
            "feature_tag": ftag,
            "feature_type": str(feat.getType()),
            "feature_label": str(feat.label()),
            "selection_boundaries": feature_selection(feat),
            "BoundaryCondition": prop(feat, "BoundaryCondition"),
            "SlidingWall": prop(feat, "SlidingWall"),
            "TranslationalVelocityOption": prop(feat, "TranslationalVelocityOption"),
            "utr": prop(feat, "utr"),
        })
    return rows


def write_r0_report(audit_rows: list[dict[str, Any]], all_boundaries: list[int], inventory: list[dict[str, Any]]) -> dict[str, Any]:
    overlap_features = [row for row in audit_rows if row.get("selection_intersects_ring")]
    unresolved = any(row["selection_boundaries"] == "UNREADABLE_SELECTION" for row in audit_rows)
    report = REPAIR / "reports" / "5B3_R0_wall_feature_audit.md"
    lines = [
        "# 5B3-R0 Wall Feature Audit",
        "",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        f"Source model: `{SRC_MODEL}`",
        "",
        "## Confirmed Ring Boundaries",
        "",
        "- `sel_5B2_ring_wall_confirmed = [4, 5, 6, 7]`",
        "",
        "## All Boundary IDs Detected",
        "",
        f"- `{all_boundaries}`",
        "",
        "## spf Wall Features",
        "",
        "| feature_tag | feature_type | selection_boundaries | BoundaryCondition | SlidingWall | TranslationalVelocityOption | utr | intersects [4,5,6,7] |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in audit_rows:
        lines.append(
            f"| `{row['feature_tag']}` | `{row['feature_type']}` | `{row['selection_boundaries']}` | "
            f"`{row['BoundaryCondition']}` | `{row['SlidingWall']}` | `{row['TranslationalVelocityOption']}` | "
            f"`{row['utr']}` | `{row['selection_intersects_ring']}` |"
        )
    lines.extend([
        "",
        "## Full spf Feature Inventory",
        "",
        "| feature_tag | feature_type | feature_label | selection_boundaries | BoundaryCondition | SlidingWall | TranslationalVelocityOption | utr |",
        "|---|---|---|---|---|---|---|---|",
    ])
    for row in inventory:
        lines.append(
            f"| `{row['feature_tag']}` | `{row['feature_type']}` | `{row['feature_label']}` | `{row['selection_boundaries']}` | "
            f"`{row['BoundaryCondition']}` | `{row['SlidingWall']}` | `{row['TranslationalVelocityOption']}` | `{row['utr']}` |"
        )
    lines.extend([
        "",
        "## Conflict Review",
        "",
        f"- Wall features intersecting the confirmed ring boundaries: `{[row['feature_tag'] for row in overlap_features]}`.",
        f"- Any unreadable wall selection: `{unresolved}`.",
        "- Repair strategy for R2: if a default/global wall covers the ring, set that default wall to the non-moving remainder boundaries and create a separate `wall_ring_move` only on the moving test group.",
        "- If the default wall selection cannot be changed, the script stops that case as `wall_overlap_unresolved` instead of treating it as a valid moving-wall model.",
    ])
    report.write_text("\n".join(lines), encoding="utf-8")
    return {
        "status": "PASS" if not unresolved else "FAIL",
        "report": str(report),
        "overlap_features": [row["feature_tag"] for row in overlap_features],
        "all_boundaries": all_boundaries,
        "wall_feature_count": len(audit_rows),
        "spf_feature_count": len(inventory),
    }


def remove_feature_if_exists(physics: Any, tag: str) -> None:
    if tag in tags(physics.feature()):
        physics.feature().remove(tag)


def set_tlist(model: Any, t_end: str, nsteps: int = 80) -> None:
    model.java.param().set("t_end_5B3_repair", t_end)
    base.set_tlist(model, f"range(0,t_end_5B3_repair/{nsteps},t_end_5B3_repair)")


def solve_model(model: Any) -> None:
    model.solve()


def h_metrics(hdata: dict[str, Any]) -> dict[str, Any]:
    rows = hdata.get("rows", [])
    finite = [row for row in rows if math.isfinite(float(row.get("H_m", math.nan)))]
    if not finite:
        return {
            "interface_identifiable": False,
            "H0_m": math.nan,
            "Hfinal_m": math.nan,
            "Hmax_m": math.nan,
            "delta_H_m": math.nan,
            "near_top": True,
            "main_interface_continuous": False,
            "isolated_spike": True,
            "interface_quality": "no finite H(t)",
        }
    hs = [float(row["H_m"]) for row in finite]
    counts = [int(row.get("interface_points", 0)) for row in finite]
    jumps = [abs(b - a) for a, b in zip(hs[:-1], hs[1:])]
    near_top = any(str(row.get("near_domain_top", "")).lower() == "true" for row in finite)
    continuous = min(counts) >= 3
    spike = bool(jumps and max(jumps) > 0.01)
    return {
        "interface_identifiable": continuous,
        "H0_m": hs[0],
        "Hfinal_m": hs[-1],
        "Hmax_m": max(hs),
        "delta_H_m": hs[-1] - hs[0],
        "near_top": near_top,
        "main_interface_continuous": continuous,
        "isolated_spike": spike,
        "interface_quality": "continuous" if continuous and not spike and not near_top else "questionable",
    }


def copy_h_csv(hdata: dict[str, Any], dest: Path) -> None:
    src = Path(hdata["csv"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


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
            "interface_threshold": 0.5,
            "interface_points": len(valid),
            "max_interface_z_m": max_z,
            "H_m": max_z,
            "H_mm": max_z * 1000 if math.isfinite(max_z) else math.nan,
            "near_domain_top": bool(math.isfinite(max_z) and max_z > 0.105),
        })
    return {"times": times, "rows": rows}


def prepare_r1_attempt(model: Any, attempt: dict[str, Any]) -> None:
    if attempt.get("eps_ls"):
        model.java.param().set("eps_ls", attempt["eps_ls"])
    if attempt.get("mesh_auto_size"):
        mesh = model.java.component("comp1").mesh("mesh1")
        mesh.autoMeshSize(int(attempt["mesh_auto_size"]))
        mesh.run()
    set_tlist(model, "0.02[s]", int(attempt.get("nsteps", 100)))


def run_static_baseline(client: Any) -> dict[str, Any]:
    model = None
    attempts = [
        {"attempt_id": "R1_attempt_1_refined_timestep", "nsteps": 100, "repair_action": "decrease output/time resolution spacing to 0.0002 s"},
        {"attempt_id": "R1_attempt_2_eps_1mm", "nsteps": 120, "eps_ls": "1[mm]", "repair_action": "reduce Level Set interface thickness eps_ls to 1 mm"},
        {"attempt_id": "R1_attempt_3_eps_0p5mm_mesh_refine", "nsteps": 120, "eps_ls": "0.5[mm]", "mesh_auto_size": 3, "repair_action": "reduce eps_ls to 0.5 mm and refine mesh one level"},
    ]
    attempt_results: list[dict[str, Any]] = []
    try:
        chosen: dict[str, Any] | None = None
        for attempt in attempts:
            model = client.load(SRC_MODEL)
            try:
                prepare_r1_attempt(model, attempt)
                solve_model(model)
                qh = quick_hdata(model, attempt["attempt_id"])
                metrics = h_metrics(qh)
                passed = (
                    math.isfinite(metrics["delta_H_m"])
                    and abs(float(metrics["delta_H_m"])) < 0.0002
                    and metrics["main_interface_continuous"]
                    and not metrics["isolated_spike"]
                    and not metrics["near_top"]
                )
                attempt_results.append({**attempt, "status": "PASS" if passed else "FAIL", "metrics": metrics})
                if chosen is None or (math.isfinite(metrics["delta_H_m"]) and abs(float(metrics["delta_H_m"])) < abs(float(chosen["metrics"].get("delta_H_m", 1e9)))):
                    chosen = {"attempt": attempt, "metrics": metrics, "quick_hdata": qh, "status": "PASS" if passed else "FAIL"}
                if passed:
                    break
            except Exception as attempt_exc:
                err = REPAIR / "logs" / f"{attempt['attempt_id']}_error_{RUN_ID}.log"
                err.write_text(traceback.format_exc(), encoding="utf-8")
                attempt_results.append({**attempt, "status": "FAIL", "error": str(attempt_exc), "error_log": str(err)})
            finally:
                try:
                    client.remove(model)
                except Exception:
                    pass
                model = None
        if chosen is None:
            raise RuntimeError("All R1 repair attempts failed before metrics extraction.")
        # Re-run the best/first passing attempt with full frame export for the required artifacts.
        model = client.load(SRC_MODEL)
        prepare_r1_attempt(model, chosen["attempt"])
        solve_model(model)
        out_dir = REPAIR / "images" / "R1_static_baseline"
        hdata = base.extract_h_vs_t(model, "5B3_R1_static_baseline", out_dir)
        copy_h_csv(hdata, REPAIR / "tables" / "static_baseline_H_vs_t.csv")
        metrics = h_metrics(hdata)
        passed = chosen["status"] == "PASS"
        write_json(REPAIR / "logs" / f"5B3_R1_repair_attempts_{RUN_ID}.json", attempt_results)
        report = REPAIR / "reports" / "5B3_R1_static_baseline_report.md"
        report.write_text("\n".join([
            "# 5B3-R1 Static Baseline Report",
            "",
            f"Review status: `{'PASS' if passed else 'FAIL'}`",
            f"Source model: `{SRC_MODEL}`",
            "",
            "## Criteria",
            "",
            "- `|H(final)-H(0)| < 0.2 mm`",
            "- Main free surface continuous",
            "- No obvious isolated spike",
            "- Interface does not reach the top boundary",
            "",
            "## Metrics",
            "",
            f"- H0: `{metrics['H0_m']}` m",
            f"- Hfinal: `{metrics['Hfinal_m']}` m",
            f"- Hmax: `{metrics['Hmax_m']}` m",
            f"- Delta H: `{metrics['delta_H_m']}` m",
            f"- Interface quality: `{metrics['interface_quality']}`",
            f"- Near top: `{metrics['near_top']}`",
            "",
            "## Automatic Repair Attempts",
            "",
            *[f"- `{row.get('attempt_id')}`: status=`{row.get('status')}`, action=`{row.get('repair_action')}`, delta_H=`{row.get('metrics', {}).get('delta_H_m', '')}` m." for row in attempt_results],
            "",
            "## Outputs",
            "",
            f"- H(t): `{REPAIR / 'tables' / 'static_baseline_H_vs_t.csv'}`",
            f"- Frames/index generated by extractor: `{hdata.get('frame_index')}`",
            f"- H(t) plot: `{hdata.get('H_vs_t_png')}`",
        ]), encoding="utf-8")
        return {"status": "PASS" if passed else "FAIL", "metrics": metrics, "hdata": hdata, "report": str(report), "attempts": attempt_results}
    except Exception as exc:
        err = REPAIR / "logs" / f"5B3_R1_static_baseline_error_{RUN_ID}.log"
        err.write_text(traceback.format_exc(), encoding="utf-8")
        return {"status": "FAIL", "error": str(exc), "error_log": str(err), "reason": "5B2_baseline_not_stable"}
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass


def configure_nonoverlap_moving_wall(model: Any, moving_ids: list[int], v_expr: str) -> dict[str, Any]:
    spf = model.java.component("comp1").physics("spf")
    audit_rows, all_boundaries = wall_audit(model)
    wall_tags = [row["feature_tag"] for row in audit_rows]
    if not wall_tags:
        raise RuntimeError("No spf Wall feature found.")
    default_tag = "wallbc1" if "wallbc1" in wall_tags else wall_tags[0]
    default_wall = spf.feature(default_tag)
    remove_feature_if_exists(spf, "wall_ring_move")
    remove_feature_if_exists(spf, "wall_fixed_rest")

    rest_ids = sorted(set(all_boundaries).difference(moving_ids))
    if not rest_ids:
        raise RuntimeError("No non-moving boundaries remain after moving-wall selection.")

    try:
        default_wall.selection().set(jints(rest_ids))
        default_wall.set("BoundaryCondition", "NoSlip")
        try:
            default_wall.set("SlidingWall", "0")
        except Exception:
            pass
    except Exception as exc:
        raise RuntimeError(f"wall_overlap_unresolved: could not restrict default wall `{default_tag}` to non-moving boundaries: {exc}") from exc

    wall = spf.feature().create("wall_ring_move", "Wall", 1)
    wall.selection().set(jints(moving_ids))
    wall.set("BoundaryCondition", "NoSlip")
    wall.set("SlidingWall", "1")
    wall.set("TranslationalVelocityOption", "Manual")
    wall.set("utr", ["0", "0", v_expr])
    after_rows, _ = wall_audit(model)
    return {
        "method": "default wall restricted to non-moving boundaries; separate wall_ring_move on test group",
        "default_wall_feature": default_tag,
        "fixed_boundaries": rest_ids,
        "moving_feature": "wall_ring_move",
        "moving_boundaries": moving_ids,
        "v_expr": v_expr,
        "post_audit": after_rows,
    }


def parse_failure_time(message: str) -> str:
    match = re.search(r"Time:\s*([0-9eE+\-.]+)\s*s", message)
    return match.group(1) if match else ""


def run_moving_case(client: Any, group_id: str, moving_ids: list[int], velocity: str, repair_try: int = 0) -> dict[str, Any]:
    model = None
    case_id = f"{group_id}_V{velocity.replace('.', 'p').replace('[m/s]', '').replace('[', '').replace(']', '')}_try{repair_try}"
    try:
        model = client.load(SRC_MODEL)
        model.java.param().set("V_ring_5B3_repair", velocity)
        model.java.param().set("t_ramp_5B3_repair", "0.005[s]" if repair_try == 0 else "0.01[s]")
        set_tlist(model, "0.02[s]", 120 if repair_try == 0 else 240)
        if repair_try <= 1:
            v_expr = "-V_ring_5B3_repair*flc2hs(t-t_ramp_5B3_repair,t_ramp_5B3_repair/2)"
        else:
            v_expr = "-V_ring_5B3_repair*flc2hs(t-t_ramp_5B3_repair,t_ramp_5B3_repair)"
        wall_setup = configure_nonoverlap_moving_wall(model, moving_ids, v_expr)
        solve_model(model)
        out_dir = REPAIR / "images" / "R2_grouped_moving_wall" / case_id
        hdata = base.extract_h_vs_t(model, f"5B3_R2_{case_id}", out_dir)
        metrics = h_metrics(hdata)
        data = base.eval_field_set(model, max(1, len(hdata["times"])))
        images = [
            base.render_field(out_dir / "phils_final.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True),
            base.render_field(out_dir / "velocity_magnitude.png", data["r"], data["z"], data["U"], cmap="viridis", phi=data["phi"], draw_interface=True),
            base.render_vector(out_dir / "ring_local_velocity_vectors.png", data["r"], data["z"], data["u"], data["w"], data["phi"]),
        ]
        stable = metrics["interface_identifiable"] and not metrics["near_top"] and not metrics["isolated_spike"]
        model_path = REPAIR / "models" / f"ring_fountain_v5B3_R2_{case_id}.mph"
        model.save(model_path)
        return {
            "case_id": case_id,
            "group_id": group_id,
            "moving_boundaries": moving_ids,
            "V_ring": velocity,
            "t_end": "0.02[s]",
            "solve_status": "success",
            "failure_time": "",
            "failure_message": "",
            "Hmax": metrics["Hmax_m"],
            "H(final)-H(0)": metrics["delta_H_m"],
            "interface_quality": metrics["interface_quality"],
            "notes": "stable" if stable else "solved but interface quality did not pass",
            "result": "PASS" if stable else "FAIL",
            "model": str(model_path),
            "h_csv": hdata.get("csv"),
            "images": [img.get("file") for img in images],
            "wall_setup": wall_setup,
            "normal_wall_velocity_failure": False,
        }
    except Exception as exc:
        msg = str(exc)
        err = REPAIR / "logs" / f"{case_id}_error_{RUN_ID}.log"
        err.write_text(traceback.format_exc(), encoding="utf-8")
        normal_failure = group_id in {"S2_bottom_edge_only", "S3_top_edge_only", "S4_horizontal_edges_only", "S5_all_edges"} and ("singularity" in msg.lower() or "not converged" in msg.lower())
        return {
            "case_id": case_id,
            "group_id": group_id,
            "moving_boundaries": moving_ids,
            "V_ring": velocity,
            "t_end": "0.02[s]",
            "solve_status": "fail",
            "failure_time": parse_failure_time(msg),
            "failure_message": msg,
            "Hmax": "",
            "H(final)-H(0)": "",
            "interface_quality": "solve_failed",
            "notes": "normal_wall_velocity_failure" if normal_failure else "solve_failed",
            "result": "FAIL",
            "error_log": str(err),
            "normal_wall_velocity_failure": normal_failure,
        }
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass


def run_grouped_moving_wall(client: Any) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for group_id, ids in GROUPS.items():
        first = run_moving_case(client, group_id, ids, "0.005[m/s]", 0)
        rows.append(first)
        if first["result"] != "PASS":
            rows.append(run_moving_case(client, group_id, ids, "0.005[m/s]", 1))
            if rows[-1]["result"] != "PASS":
                rows.append(run_moving_case(client, group_id, ids, "0.005[m/s]", 2))
            continue
        for vel in ["0.01[m/s]", "0.02[m/s]"]:
            rows.append(run_moving_case(client, group_id, ids, vel, 0))
    flat_rows = []
    for row in rows:
        flat_rows.append({
            "case_id": row.get("case_id"),
            "moving_boundaries": row.get("moving_boundaries"),
            "V_ring": row.get("V_ring"),
            "t_end": row.get("t_end"),
            "solve_status": row.get("solve_status"),
            "failure_time": row.get("failure_time"),
            "failure_message": row.get("failure_message"),
            "Hmax": row.get("Hmax"),
            "H(final)-H(0)": row.get("H(final)-H(0)"),
            "interface_quality": row.get("interface_quality"),
            "notes": row.get("notes"),
            "model": row.get("model", ""),
            "h_csv": row.get("h_csv", ""),
            "error_log": row.get("error_log", ""),
            "normal_wall_velocity_failure": row.get("normal_wall_velocity_failure", ""),
        })
    csv_path = REPAIR / "tables" / "moving_wall_group_tests.csv"
    write_csv(csv_path, flat_rows)
    pass_rows = [row for row in rows if row.get("result") == "PASS"]
    best = pass_rows[0] if pass_rows else None
    if best and best.get("model"):
        shutil.copy2(best["model"], REPAIR / "models" / "ring_fountain_v5B3_repaired_best.mph")
    report = REPAIR / "reports" / "5B3_R2_grouped_moving_wall_report.md"
    report.write_text("\n".join([
        "# 5B3-R2 Grouped Moving Wall Report",
        "",
        f"Review status: `{'PASS' if pass_rows else 'FAIL'}`",
        "",
        "## Method",
        "",
        "- Moving wall was tested by boundary group, not all four edges at once.",
        "- For each case, the default/global wall was restricted to non-moving boundaries before `wall_ring_move` was created.",
        "- Wall velocity direction: negative z.",
        "- Velocity ramp time: `0.005 s` initially, longer/smoother on repair tries.",
        "",
        "## Results",
        "",
        *[f"- `{row.get('case_id')}`: result=`{row.get('result')}`, solve=`{row.get('solve_status')}`, quality=`{row.get('interface_quality')}`, notes=`{row.get('notes')}`." for row in rows],
        "",
        "## Review",
        "",
        f"- At least one moving-wall grouped case stable: `{bool(pass_rows)}`.",
        f"- Best/stable group: `{best.get('group_id') if best else ''}`.",
        f"- Evidence of normal wall velocity failure: `{any(row.get('normal_wall_velocity_failure') for row in rows)}`.",
        "",
        "## Outputs",
        "",
        f"- Case table: `{csv_path}`",
        f"- Repaired best model if PASS: `{REPAIR / 'models' / 'ring_fountain_v5B3_repaired_best.mph' if best else ''}`",
    ]), encoding="utf-8")
    return {
        "status": "PASS" if pass_rows else "FAIL",
        "rows": rows,
        "best_case": best,
        "report": str(report),
        "csv": str(csv_path),
        "normal_wall_velocity_failure": any(row.get("normal_wall_velocity_failure") for row in rows),
    }


def write_not_run_report(path: Path, title: str, reason: str) -> None:
    path.write_text("\n".join([
        f"# {title}",
        "",
        "Review status: `NOT_RUN`",
        "",
        f"Reason: {reason}",
    ]), encoding="utf-8")


def write_final(summary: dict[str, Any]) -> dict[str, Any]:
    r0 = summary.get("R0", {})
    r1 = summary.get("R1", {})
    r2 = summary.get("R2", {})
    r3 = summary.get("R3", {})
    r4 = summary.get("R4", {})
    allow = (
        r2.get("status") == "PASS"
        and r1.get("status") == "PASS"
        and r0.get("status") == "PASS"
        and not any("wall_overlap_unresolved" in str(row.get("failure_message", "")) for row in r2.get("rows", []))
    )
    best = r2.get("best_case") if isinstance(r2.get("best_case"), dict) else None
    final_report = REPAIR / "reports" / "5B3_stability_repair_final_report.md"
    lines = [
        "# 5B3 Stability Repair Final Report",
        "",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        f"Source model: `{SRC_MODEL}`",
        "",
        "## Final Gate",
        "",
        f"`ALLOW_RESUME_STAGE5 = {'YES' if allow else 'NO'}`",
        "",
        "This run did not enter 5B4, 5C, 5D, 5E, or stage 6.",
        "",
        "## Required Answers",
        "",
        f"- Most likely reason 5B3 stopped: `{summary.get('most_likely_reason')}`.",
        f"- Wall feature overlap exists: `{bool(r0.get('overlap_features'))}`; overlapping features: `{r0.get('overlap_features')}`.",
        f"- 5B2 static baseline stable enough: `{r1.get('status') == 'PASS'}`.",
        f"- Most stable moving-wall group: `{best.get('group_id') if best else ''}`.",
        f"- Evidence of normal wall velocity failure: `{r2.get('normal_wall_velocity_failure')}`.",
        f"- Fillet improved stability: `{r3.get('status') if r3 else 'NOT_RUN'}`.",
        f"- Alternative physics route stable: `{r4.get('status') if r4 else 'NOT_RUN'}`.",
        f"- Repaired best model obtained: `{bool(best and best.get('model'))}`.",
        f"- Allow resume to 5B4: `{'YES' if allow else 'NO'}`.",
        "",
        "## Stage Reports",
        "",
        f"- R0 wall audit: `{r0.get('report')}`",
        f"- R1 static baseline: `{r1.get('report')}`",
        f"- R2 grouped moving wall: `{r2.get('report')}`",
        f"- R3 fillet repair: `{r3.get('report', '')}`",
        f"- R4 physics route: `{r4.get('report', '')}`",
        "",
        "## Limitations",
        "",
        "- The model remains fixed geometry with moving-wall velocity conditions; it is not a true falling ring geometry.",
        "- No Jet1/Jet2 extraction was performed in this run.",
        "- Stable grouped/reduced results must not be described as a validated full ring-fall model.",
    ]
    if not allow:
        lines.extend([
            "",
            "## Manual Follow-Up Needed",
            "",
            "- Resolve any remaining wall-feature overlap or solver instability before resuming the main Stage 5 flow.",
            "- Do not enter 5B4 until at least one valid 5B3 moving-wall or reduced moving-wall case is accepted with clear limitations.",
        ])
    final_report.write_text("\n".join(lines), encoding="utf-8")
    summary["final_report"] = str(final_report)
    summary["ALLOW_RESUME_STAGE5"] = "YES" if allow else "NO"
    return summary


def main() -> None:
    os.environ["JAVA_HOME"] = r"D:\COMSOL64\Multiphysics\java\win64\jre"
    ensure_dirs()
    shutil.copy2(Path(__file__), SCRIPTS / "ring_fountain_stage5b3_stability_repair.py")
    if not SRC_MODEL.exists():
        raise FileNotFoundError(SRC_MODEL)
    summary: dict[str, Any] = {"run_id": RUN_ID, "source_model": str(SRC_MODEL)}
    client = mph.Client(cores=2, version="6.4")
    model = None
    try:
        log("R0 wall audit started.")
        model = client.load(SRC_MODEL)
        audit_rows, all_boundaries = wall_audit(model)
        inventory = spf_feature_inventory(model)
        write_json(REPAIR / "logs" / f"5B3_R0_wall_feature_audit_{RUN_ID}.json", {"audit": audit_rows, "all_boundaries": all_boundaries, "spf_feature_inventory": inventory})
        summary["R0"] = write_r0_report(audit_rows, all_boundaries, inventory)
        client.remove(model)
        model = None
        if summary["R0"]["status"] != "PASS":
            summary["stop_reason"] = "wall feature conflict could not be judged safely."
            write_not_run_report(REPAIR / "reports" / "5B3_R1_static_baseline_report.md", "5B3-R1 Static Baseline Report", summary["stop_reason"])
            summary["R1"] = {"status": "NOT_RUN"}
        else:
            log("R1 static baseline started.")
            summary["R1"] = run_static_baseline(client)

        if summary.get("R1", {}).get("status") == "PASS":
            log("R2 grouped moving-wall tests started.")
            summary["R2"] = run_grouped_moving_wall(client)
        else:
            summary["R2"] = {"status": "NOT_RUN", "reason": "R1 did not PASS."}
            summary["stop_reason"] = "5B2_baseline_not_stable"

        if summary.get("R2", {}).get("status") == "PASS":
            summary["R3"] = {"status": "NOT_RUN", "reason": "R2 already PASS; fillet repair not needed.", "report": str(REPAIR / "reports" / "5B3_R3_fillet_repair_report.md")}
            write_not_run_report(REPAIR / "reports" / "5B3_R3_fillet_repair_report.md", "5B3-R3 Fillet Repair Report", "R2 already PASS; fillet repair not needed.")
            summary["R4"] = {"status": "NOT_RUN", "reason": "R2 already PASS; physics-route replacement not needed.", "report": str(REPAIR / "reports" / "5B3_R4_physics_route_report.md")}
            write_not_run_report(REPAIR / "reports" / "5B3_R4_physics_route_report.md", "5B3-R4 Physics Route Report", "R2 already PASS; physics-route replacement not needed.")
        else:
            summary["R3"] = {"status": "NOT_IMPLEMENTED_IN_THIS_RUN", "reason": "R2 failed; fillet geometry rebuild requires a separate geometry regeneration pass.", "report": str(REPAIR / "reports" / "5B3_R3_fillet_repair_report.md")}
            write_not_run_report(REPAIR / "reports" / "5B3_R3_fillet_repair_report.md", "5B3-R3 Fillet Repair Report", "R2 failed; fillet geometry rebuild was not safely automated in this run.")
            summary["R4"] = {"status": "NOT_IMPLEMENTED_IN_THIS_RUN", "reason": "R3 did not produce a best model; alternative route not safely automated in this run.", "report": str(REPAIR / "reports" / "5B3_R4_physics_route_report.md")}
            write_not_run_report(REPAIR / "reports" / "5B3_R4_physics_route_report.md", "5B3-R4 Physics Route Report", "No stable R2/R3 case available; stop before broader route changes.")

        if summary.get("R2", {}).get("status") == "PASS":
            summary["most_likely_reason"] = "previous 5B3 used a separate wall_ring_move while the default/global wall also covered the ring, creating likely overlapping wall constraints; grouped non-overlap repair solved at least one case."
        else:
            summary["most_likely_reason"] = "moving wall plus free surface remained unstable or wall overlap could not be fully resolved."
        write_final(summary)
        write_json(REPAIR / "5B3_stability_repair_summary.json", summary)
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass
        try:
            client.clear()
        except Exception:
            pass


if __name__ == "__main__":
    main()
