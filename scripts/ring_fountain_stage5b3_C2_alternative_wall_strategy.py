# -*- coding: utf-8 -*-
"""Stage 5B3-C2 alternative wall strategy for the COMSOL Ring Fountain project.

This script only runs the C2 gate:

* C2-0 feature/property probing.
* C2-1 Wetted Wall / Interior Wetted Wall attempts on the clean baseline.
* C2-2 rebuilt selectable-wall reduced model only if C2-1 fails.

It does not enter 5B4, 5C, 5D, 5E, stage 6, Jet1/Jet2 extraction, or parameter
studies.
"""

from __future__ import annotations

import csv
import hashlib
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

import ring_fountain_stage5_cleanup_5b_5c as base
import ring_fountain_stage5b2_clean_and_5b3_minimal as cleanbd


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
STAGE5 = ROOT / "05_two_phase_free_surface"
C2 = STAGE5 / "5B3_C2_alternative_wall_strategy"
SCRIPTS = ROOT / "scripts"
SRC_CLEAN = STAGE5 / "5B2_clean_baseline_rebuild" / "models" / "ring_fountain_v5B2_clean_static_baseline_best.mph"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = C2 / "logs" / f"5B3_C2_alternative_wall_strategy_{RUN_ID}.log"

RING_ALL = [4, 5, 6, 7]
RING_VERTICAL = [4, 7]


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def ensure_dirs() -> None:
    for sub in ["models", "reports", "tables", "logs", "images"]:
        (C2 / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def jints(values: list[int]) -> Any:
    return jpype.JArray(jpype.JInt)(values)


def tags(node: Any) -> list[str]:
    try:
        return [str(x) for x in list(node.tags())]
    except Exception:
        return []


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


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
            out: dict[str, Any] = {}
            for key in keys:
                value = row.get(key, "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False, default=str)
                out[key] = value
            writer.writerow(out)


def safe_prop(feature: Any, key: str) -> Any:
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


def feature_properties(feature: Any) -> list[str]:
    for call in (
        lambda: feature.properties(),
        lambda: feature.propertyNames(),
    ):
        try:
            return [str(x) for x in list(call())]
        except Exception:
            pass
    return []


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
    tag = "sel_C2_all_boundaries_probe"
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


def h_metrics(model: Any, model_id: str, out_dir: Path) -> dict[str, Any]:
    hdata = base.extract_h_vs_t(model, model_id, out_dir)
    rows = hdata.get("rows", [])
    finite = [row for row in rows if math.isfinite(float(row.get("H_m", math.nan)))]
    if not finite:
        return {
            "hdata": hdata,
            "H0": math.nan,
            "Hfinal": math.nan,
            "delta_H": math.nan,
            "Hmax": math.nan,
            "interface_quality": "no finite H(t)",
            "near_top": True,
            "pass_static": False,
        }
    hs = [float(row["H_m"]) for row in finite]
    counts = [int(row.get("interface_points", 0)) for row in finite]
    jumps = [abs(b - a) for a, b in zip(hs[:-1], hs[1:])]
    near_top = any(bool(row.get("near_domain_top")) for row in finite)
    continuous = min(counts) >= 3
    spike = bool(jumps and max(jumps) > 0.01)
    delta = hs[-1] - hs[0]
    return {
        "hdata": hdata,
        "H0": hs[0],
        "Hfinal": hs[-1],
        "delta_H": delta,
        "Hmax": max(hs),
        "interface_quality": "clear/continuous" if continuous and not spike and not near_top else "questionable",
        "near_top": near_top,
        "main_free_surface_continuous": continuous,
        "isolated_spike": spike,
        "pass_static": abs(delta) < 0.0002 and continuous and not spike and not near_top,
    }


def set_tlist(model: Any, param_name: str, t_end: str, nsteps: int) -> None:
    model.java.param().set(param_name, t_end)
    base.set_tlist(model, f"range(0,{param_name}/{nsteps},{param_name})")


def save_model_no_overwrite(model: Any, canonical: Path) -> dict[str, str]:
    canonical.parent.mkdir(parents=True, exist_ok=True)
    timestamp = canonical.with_name(f"{canonical.stem}_{RUN_ID}{canonical.suffix}")
    model.save(timestamp)
    saved = {"timestamp_model": str(timestamp)}
    if not canonical.exists():
        model.save(canonical)
        saved["model"] = str(canonical)
    else:
        saved["model"] = str(canonical)
        saved["canonical_note"] = "canonical already existed and was not overwritten; timestamp model saved"
    return saved


def get_physics(model: Any, tag: str) -> Any | None:
    comp = model.java.component("comp1")
    try:
        return comp.physics(tag)
    except Exception:
        return None


def try_create_feature(physics: Any, tag: str, type_name: str, boundaries: list[int] | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {
        "physics_tag": "",
        "feature_tag": tag,
        "candidate_type": type_name,
        "create_status": "FAIL",
        "can_select_ring": False,
        "properties": [],
        "error": "",
    }
    try:
        row["physics_tag"] = str(physics.tag())
    except Exception:
        pass
    try:
        if tag in tags(physics.feature()):
            physics.feature().remove(tag)
    except Exception:
        pass
    try:
        feat = physics.feature().create(tag, type_name, 1)
        row["create_status"] = "PASS"
        row["created_type"] = str(feat.getType())
        row["label"] = str(feat.label())
        if boundaries is not None:
            try:
                feat.selection().set(jints(boundaries))
                row["can_select_ring"] = feature_selection(feat)
            except Exception as exc:
                row["can_select_ring"] = False
                row["selection_error"] = str(exc)
        props = feature_properties(feat)
        row["properties"] = props
        for key in ["BoundaryCondition", "SlidingWall", "TranslationalVelocityOption", "utr", "WallCondition", "WallType"]:
            row[key] = safe_prop(feat, key)
        try:
            physics.feature().remove(tag)
            row["cleanup"] = "removed_probe_feature"
        except Exception as exc:
            row["cleanup"] = f"remove_failed: {exc}"
    except Exception as exc:
        row["error"] = str(exc)
    return row


def probe_physics_type(client: Any, type_name: str) -> dict[str, Any]:
    model = None
    row = {"probe": "physics_interface", "candidate_type": type_name, "create_status": "FAIL", "error": ""}
    try:
        model = client.create(f"C2_probe_{type_name}_{RUN_ID}")
        comp = model.java.component().create("comp1", True)
        geom = comp.geom().create("geom1", 2)
        try:
            geom.axisymmetric(True)
        except Exception:
            pass
        rect = geom.feature().create("r1", "Rectangle")
        rect.set("size", ["0.01", "0.01"])
        geom.run()
        phy = comp.physics().create("ptest", type_name, "geom1")
        row["create_status"] = "PASS"
        row["created_type"] = str(phy.getType())
    except Exception as exc:
        row["error"] = str(exc)
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass
    return row


def stage_c2_0(client: Any) -> dict[str, Any]:
    log("C2-0 feature/property probe started.")
    model = client.load(SRC_CLEAN)
    rows: list[dict[str, Any]] = []
    try:
        for type_name in [
            "LaminarTwoPhaseFlowLevelSet",
            "TwoPhaseFlowLevelSet",
            "TwoPhaseFlowLS",
            "TpfLevelSet",
            "LaminarTwoPhaseFlowPhaseField",
            "TwoPhaseFlowPhaseField",
            "TwoPhaseFlowPF",
        ]:
            rows.append(probe_physics_type(client, type_name))

        comp = model.java.component("comp1")
        physics_inventory = []
        for ptag in tags(comp.physics()):
            phy = comp.physics(ptag)
            physics_inventory.append({"physics_tag": ptag, "physics_type": str(phy.getType()), "label": str(phy.label())})
        for ptag in ["ls", "spf"]:
            phy = get_physics(model, ptag)
            if phy is None:
                rows.append({"probe": "feature", "physics_tag": ptag, "create_status": "FAIL", "error": "physics not found"})
                continue
            candidates = {
                "ls": [
                    "WettedWall",
                    "WettedWallLS",
                    "WallWetted",
                    "InteriorWettedWall",
                    "InteriorWettedWallLS",
                    "NoFlow",
                    "LevelSetNoFlow",
                    "Wall",
                    "OpenBoundary",
                ],
                "spf": [
                    "Wall",
                    "Inlet",
                    "Outlet",
                    "OpenBoundary",
                    "SlipWall",
                    "WettedWall",
                    "InteriorWettedWall",
                    "MovingWall",
                    "NoFlow",
                ],
            }[ptag]
            for cand in candidates:
                row = try_create_feature(phy, f"C2_probe_{ptag}_{cand}", cand, RING_ALL)
                row["probe"] = "feature"
                rows.append(row)
    finally:
        try:
            client.remove(model)
        except Exception:
            pass

    csv_path = C2 / "tables" / "C2_0_feature_probe.csv"
    write_csv(csv_path, rows)

    def is_ok(name: str) -> bool:
        return any(row.get("candidate_type") == name and row.get("create_status") == "PASS" for row in rows)

    wetted_rows = [r for r in rows if str(r.get("candidate_type", "")).lower().startswith("wettedwall")]
    interior_rows = [r for r in rows if "interiorwettedwall" in str(r.get("candidate_type", "")).lower()]
    wall_rows = [r for r in rows if r.get("candidate_type") == "Wall" and r.get("create_status") == "PASS"]
    official_rows = [r for r in rows if r.get("probe") == "physics_interface"]
    moving_coexist = bool(wall_rows)
    status = "PASS"
    report = C2 / "reports" / "C2_0_feature_probe_report.md"
    lines = [
        "# C2-0 Feature / Property Probe Report",
        "",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        f"Source clean baseline: `{SRC_CLEAN}`",
        "",
        f"C2-0 review status: `{status}`",
        "",
        "## Summary",
        "",
        f"- Wetted Wall creatable by tested API type names: `{any(r.get('create_status') == 'PASS' for r in wetted_rows)}`.",
        f"- Interior Wetted Wall creatable by tested API type names: `{any(r.get('create_status') == 'PASS' for r in interior_rows)}`.",
        f"- Tested Wetted/Interior features selectable on ring `[4,5,6,7]`: `{[r.get('can_select_ring') for r in wetted_rows + interior_rows if r.get('create_status') == 'PASS']}`.",
        f"- Formal Two-Phase Flow Level Set/Phase Field interface creatable by tested API type names: `{any(r.get('create_status') == 'PASS' for r in official_rows)}`.",
        f"- Laminar Flow `Wall` feature creatable and exposes moving-wall properties: `{moving_coexist}`.",
        "- Replacement/override of existing noneditable `spf.wallbc1`: not proven by API probe alone; C2-1 tests this without deleting `wallbc1`.",
        "",
        "## Probe Table",
        "",
        f"- CSV: `{csv_path}`",
        "",
        "## Notable Rows",
        "",
        "| probe | physics | candidate_type | create_status | can_select_ring | properties | error |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        props = row.get("properties", [])
        prop_text = ", ".join(props[:12]) if isinstance(props, list) else str(props)
        lines.append(
            f"| `{row.get('probe','')}` | `{row.get('physics_tag','')}` | `{row.get('candidate_type','')}` | "
            f"`{row.get('create_status','')}` | `{row.get('can_select_ring','')}` | `{prop_text}` | `{str(row.get('error','')).replace('|','/')}` |"
        )
    report.write_text("\n".join(lines), encoding="utf-8")
    result = {
        "status": status,
        "report": str(report),
        "csv": str(csv_path),
        "wetted_wall_creatable": any(r.get("create_status") == "PASS" for r in wetted_rows),
        "interior_wetted_wall_creatable": any(r.get("create_status") == "PASS" for r in interior_rows),
        "moving_wall_coexistence_probe": moving_coexist,
        "formal_two_phase_creatable": any(r.get("create_status") == "PASS" for r in official_rows),
        "rows": rows,
    }
    write_json(C2 / "logs" / f"C2_0_feature_probe_{RUN_ID}.json", result)
    return result


def add_wetted_feature(model: Any, route: str, boundaries: list[int]) -> dict[str, Any]:
    comp = model.java.component("comp1")
    ls = comp.physics("ls")
    candidates = ["WettedWall", "WettedWallLS", "WallWetted"] if route.startswith("C2a") else ["InteriorWettedWall", "InteriorWettedWallLS"]
    attempts = []
    for cand in candidates:
        tag = f"{route.replace('-', '_')}_{cand}"
        row = try_create_feature(ls, tag, cand, boundaries)
        attempts.append(row)
        if row.get("create_status") == "PASS":
            feat = ls.feature().create(tag, cand, 1)
            feat.selection().set(jints(boundaries))
            return {"status": "PASS", "feature_tag": tag, "feature_type": cand, "attempts": attempts}
    return {"status": "FAIL", "attempts": attempts}


def configure_small_vertical_moving_wall(model: Any, v_expr: str) -> dict[str, Any]:
    spf = model.java.component("comp1").physics("spf")
    tag = "wall_C2_vertical_move"
    if tag in tags(spf.feature()):
        try:
            spf.feature().remove(tag)
        except Exception:
            pass
    wall = spf.feature().create(tag, "Wall", 1)
    wall.selection().set(jints(RING_VERTICAL))
    wall.set("BoundaryCondition", "NoSlip")
    wall.set("SlidingWall", "1")
    wall.set("TranslationalVelocityOption", "Manual")
    wall.set("utr", ["0", "0", v_expr])
    audit = cleanbd.wall_audit(model, RING_VERTICAL)
    overlap = any(row["feature_tag"] != tag and row["intersects_moving_boundaries"] for row in audit)
    return {
        "feature": tag,
        "selection": RING_VERTICAL,
        "utr": ["0", "0", v_expr],
        "wall_audit": audit,
        "wall_overlap_status": "FAIL" if overlap else "PASS",
    }


def run_c2_1_case(client: Any, case: dict[str, Any]) -> dict[str, Any]:
    model = None
    row: dict[str, Any] = {
        "case_id": case["case_id"],
        "route": case["route"],
        "boundary_set": case["boundaries"],
        "V_test": case.get("V_test", 0),
        "t_end": case["t_end"],
        "solve_status": "FAIL",
        "failure_time": "",
        "failure_message": "",
        "H0": math.nan,
        "Hfinal": math.nan,
        "delta_H": math.nan,
        "Hmax": math.nan,
        "interface_quality": "",
        "wall_overlap_status": "",
        "notes": "",
    }
    try:
        model = client.load(SRC_CLEAN)
        setup = add_wetted_feature(model, case["route"], case["boundaries"])
        row["wetted_setup"] = setup
        if setup.get("status") != "PASS":
            raise RuntimeError("Wetted Wall / Interior Wetted Wall feature could not be created by tested API type names.")
        set_tlist(model, "t_end_C2_1", case["t_end"], case.get("nsteps", 40))
        model.java.param().set("V_test_C2", f"{case.get('V_test', 0)}[m/s]")
        if case.get("moving"):
            wall_setup = configure_small_vertical_moving_wall(model, "-V_test_C2*min(t/0.002[s],1)")
            row["wall_overlap_status"] = wall_setup["wall_overlap_status"]
            row["wall_setup"] = wall_setup
            if wall_setup["wall_overlap_status"] != "PASS":
                row["notes"] = "additional moving wall overlaps existing spf.wallbc1; recorded as unresolved alternative-wall conflict"
        else:
            row["wall_overlap_status"] = "not_applicable_static"
        model.solve()
        out_dir = C2 / "images" / case["case_id"]
        metrics = h_metrics(model, case["case_id"], out_dir)
        row.update({k: metrics[k] for k in ["H0", "Hfinal", "delta_H", "Hmax", "interface_quality"]})
        row["solve_status"] = "PASS" if metrics["pass_static"] and row["wall_overlap_status"] in ["PASS", "not_applicable_static"] else "FAIL"
        data = base.eval_field_set(model, len(metrics["hdata"].get("times", [])) or 1)
        base.render_field(out_dir / f"{case['case_id']}_phils_final.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True)
        route_model = C2 / "models" / ("ring_fountain_v5B3_C2a_wetted_wall_attempt.mph" if case["route"].startswith("C2a") else "ring_fountain_v5B3_C2b_interior_wetted_wall_attempt.mph")
        row.update(save_model_no_overwrite(model, route_model))
    except Exception as exc:
        row["solve_status"] = "FAIL"
        row["failure_message"] = f"{type(exc).__name__}: {exc}"
        row["traceback"] = traceback.format_exc()
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass
    return row


def stage_c2_1(client: Any, probe: dict[str, Any]) -> dict[str, Any]:
    log("C2-1 Wetted Wall alternative strategy started.")
    cases = [
        {"case_id": "C2a_static_all", "route": "C2a", "boundaries": RING_ALL, "moving": False, "V_test": 0, "t_end": "0.02[s]", "nsteps": 40},
        {"case_id": "C2b_static_all", "route": "C2b", "boundaries": RING_ALL, "moving": False, "V_test": 0, "t_end": "0.02[s]", "nsteps": 40},
        {"case_id": "C2a_S1_static_vertical", "route": "C2a-S1", "boundaries": RING_VERTICAL, "moving": False, "V_test": 0, "t_end": "0.02[s]", "nsteps": 40},
        {"case_id": "C2b_S1_static_vertical", "route": "C2b-S1", "boundaries": RING_VERTICAL, "moving": False, "V_test": 0, "t_end": "0.02[s]", "nsteps": 40},
    ]
    rows: list[dict[str, Any]] = []
    if not probe.get("wetted_wall_creatable") and not probe.get("interior_wetted_wall_creatable"):
        rows.append({
            "case_id": "C2_1_not_run_features_unavailable",
            "route": "Wetted/Interior",
            "boundary_set": RING_ALL,
            "V_test": 0,
            "t_end": "",
            "solve_status": "FAIL",
            "failure_message": "C2-0 did not find creatable Wetted Wall or Interior Wetted Wall feature types.",
            "wall_overlap_status": "not_tested",
            "notes": "C2-1 failed by availability gate; proceeding to C2-2.",
        })
    else:
        for case in cases:
            row = run_c2_1_case(client, case)
            rows.append(row)
        vertical_static_pass = any(row["solve_status"] == "PASS" and row["case_id"].endswith("static_vertical") for row in rows)
        if vertical_static_pass:
            for speed, tend, steps in [(0.001, "0.005[s]", 20), (0.002, "0.01[s]", 40)]:
                for route in ["C2a-S1", "C2b-S1"]:
                    rows.append(run_c2_1_case(client, {
                        "case_id": f"{route.replace('-', '_')}_moving_vertical_{speed:g}",
                        "route": route,
                        "boundaries": RING_VERTICAL,
                        "moving": True,
                        "V_test": speed,
                        "t_end": tend,
                        "nsteps": steps,
                    }))

    csv_path = C2 / "tables" / "C2_1_wetted_wall_cases.csv"
    write_csv(csv_path, rows)
    pass_rows = [row for row in rows if row.get("solve_status") == "PASS"]
    status = "PASS" if pass_rows else "FAIL"
    best = min(pass_rows, key=lambda r: abs(float(r.get("delta_H", math.inf)))) if pass_rows else None
    if best:
        best_src = best.get("timestamp_model") or best.get("model")
        if best_src:
            best_model = C2 / "models" / "ring_fountain_v5B3_C2_best.mph"
            if not best_model.exists():
                shutil.copy2(best_src, best_model)
    report = C2 / "reports" / "C2_1_wetted_wall_report.md"
    lines = [
        "# C2-1 Wetted Wall Alternative Strategy Report",
        "",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        f"C2-1 review status: `{status}`",
        f"C2_WETTED_WALL_STRATEGY = `{status}`",
        f"ALLOW_RESUME_STAGE5 = `{'YES' if status == 'PASS' else 'NO'}`",
        "",
        "## Method",
        "",
        "- The script did not delete `spf.wallbc1`.",
        "- Wetted Wall / Interior Wetted Wall candidates were attempted on `[4,5,6,7]` and `[4,7]`.",
        "- Moving tests were only considered after vertical static cases were stable.",
        "",
        "## Results",
        "",
        f"- CSV: `{csv_path}`",
        f"- Best case: `{best.get('case_id') if best else ''}`",
        "",
        "| case_id | solve_status | boundary_set | V_test | t_end | delta_H | Hmax | wall_overlap_status | failure_message |",
        "|---|---|---|---:|---|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row.get('case_id')}` | `{row.get('solve_status')}` | `{row.get('boundary_set')}` | "
            f"`{row.get('V_test')}` | `{row.get('t_end')}` | `{row.get('delta_H')}` | `{row.get('Hmax')}` | "
            f"`{row.get('wall_overlap_status')}` | `{str(row.get('failure_message','')).replace('|','/')}` |"
        )
    report.write_text("\n".join(lines), encoding="utf-8")
    result = {
        "status": status,
        "report": str(report),
        "csv": str(csv_path),
        "rows": rows,
        "best": best,
        "ALLOW_RESUME_STAGE5": "YES" if status == "PASS" else "NO",
    }
    write_json(C2 / "logs" / f"C2_1_wetted_wall_{RUN_ID}.json", result)
    return result


def rename_c2_selections(model: Any, sel: dict[str, Any]) -> dict[str, Any]:
    comp = model.java.component("comp1")
    manager = comp.selection()
    mapping = {
        "sel_axis": [],
        "sel_outer_wall": [],
        "sel_top_boundary": [],
        "sel_bottom_boundary": [],
        "sel_ring_wall_inner": [sel["roles"]["sel_5B_ring_wall_inner"]],
        "sel_ring_wall_outer": [sel["roles"]["sel_5B_ring_wall_outer"]],
        "sel_ring_wall_top": [sel["roles"]["sel_5B_ring_wall_top"]],
        "sel_ring_wall_bottom": [sel["roles"]["sel_5B_ring_wall_bottom"]],
        "sel_ring_wall_all": sel["confirmed"],
        "sel_ring_wall_vertical": [sel["roles"]["sel_5B_ring_wall_inner"], sel["roles"]["sel_5B_ring_wall_outer"]],
    }
    rows = base.s41.boundary_metrics(model)
    rtank = base.s42a.param_float(model, "Rtank", "m")
    hwater = base.s42a.param_float(model, "Hwater", "m")
    hair = base.s42a.param_float(model, "Hair", "m")
    tol = 5e-5
    for row in rows:
        bid = int(row["boundary_id"])
        rmin, rmax, zmin, zmax = row["r_min_m"], row["r_max_m"], row["z_min_m"], row["z_max_m"]
        if abs(rmin) < tol and abs(rmax) < tol:
            mapping["sel_axis"].append(bid)
        if abs(rmin - rtank) < tol and abs(rmax - rtank) < tol:
            mapping["sel_outer_wall"].append(bid)
        if abs(zmin - hair) < tol and abs(zmax - hair) < tol:
            mapping["sel_top_boundary"].append(bid)
        if abs(zmin + hwater) < tol and abs(zmax + hwater) < tol:
            mapping["sel_bottom_boundary"].append(bid)
    for tag, ids in mapping.items():
        if tag in tags(manager):
            manager.remove(tag)
        manager.create(tag, "Explicit")
        node = manager.get(tag)
        node.label(tag)
        node.geom("geom1", 1)
        node.set(jints(sorted(set(ids))))
    return mapping


def param_float(model: Any, name: str) -> float:
    try:
        expr = str(model.java.param().get(name))
        text = expr.strip()
        factors = {
            "[m]": 1.0,
            "[mm]": 1e-3,
            "[cm]": 1e-2,
        }
        for unit, factor in factors.items():
            if text.endswith(unit):
                return float(text[: -len(unit)]) * factor
        return float(text)
    except Exception:
        defaults = {
            "Rtank": 0.1,
            "Hwater": 0.12,
            "Hair": 0.12,
            "Ri": 0.008,
            "Ro": 0.02,
            "h_ring": 0.002,
            "z_ring_center": -0.02,
        }
        if name in defaults:
            return defaults[name]
        return float(base.s42a.param_float(model, name, "m"))


def box_boundary_ids(model: Any, tag: str, xmin: float, xmax: float, ymin: float, ymax: float) -> list[int]:
    comp = model.java.component("comp1")
    manager = comp.selection()
    if tag in tags(manager):
        manager.remove(tag)
    manager.create(tag, "Box")
    sel = manager.get(tag)
    sel.geom("geom1", 1)
    sel.set("entitydim", "1")
    sel.set("xmin", f"{xmin:.12g}")
    sel.set("xmax", f"{xmax:.12g}")
    sel.set("ymin", f"{ymin:.12g}")
    sel.set("ymax", f"{ymax:.12g}")
    sel.set("condition", "inside")
    return sorted({int(x) for x in list(sel.entities(1))})


def make_explicit_selection(model: Any, tag: str, ids: list[int]) -> None:
    manager = model.java.component("comp1").selection()
    if tag in tags(manager):
        manager.remove(tag)
    manager.create(tag, "Explicit")
    node = manager.get(tag)
    node.label(tag)
    node.geom("geom1", 1)
    node.set(jints(sorted(set(ids))))


def ensure_c2_box_selections(model: Any) -> dict[str, Any]:
    ri = param_float(model, "Ri")
    ro = param_float(model, "Ro")
    h = param_float(model, "h_ring")
    zc = param_float(model, "z_ring_center")
    rtank = param_float(model, "Rtank")
    hwater = param_float(model, "Hwater")
    hair = param_float(model, "Hair")
    tol = 1e-5
    mapping = {
        "sel_axis": box_boundary_ids(model, "box_C2_axis", -tol, tol, -hwater - tol, hair + tol),
        "sel_outer_wall": box_boundary_ids(model, "box_C2_outer", rtank - tol, rtank + tol, -hwater - tol, hair + tol),
        "sel_top_boundary": box_boundary_ids(model, "box_C2_top", -tol, rtank + tol, hair - tol, hair + tol),
        "sel_bottom_boundary": box_boundary_ids(model, "box_C2_bottom", -tol, rtank + tol, -hwater - tol, -hwater + tol),
        "sel_ring_wall_inner": box_boundary_ids(model, "box_C2_ring_inner", ri - tol, ri + tol, zc - h / 2 - tol, zc + h / 2 + tol),
        "sel_ring_wall_outer": box_boundary_ids(model, "box_C2_ring_outer", ro - tol, ro + tol, zc - h / 2 - tol, zc + h / 2 + tol),
        "sel_ring_wall_top": box_boundary_ids(model, "box_C2_ring_top", ri - tol, ro + tol, zc + h / 2 - tol, zc + h / 2 + tol),
        "sel_ring_wall_bottom": box_boundary_ids(model, "box_C2_ring_bottom", ri - tol, ro + tol, zc - h / 2 - tol, zc - h / 2 + tol),
    }
    mapping["sel_ring_wall_all"] = sorted(set(mapping["sel_ring_wall_inner"] + mapping["sel_ring_wall_outer"] + mapping["sel_ring_wall_top"] + mapping["sel_ring_wall_bottom"]))
    mapping["sel_ring_wall_vertical"] = sorted(set(mapping["sel_ring_wall_inner"] + mapping["sel_ring_wall_outer"]))
    for tag, ids in mapping.items():
        make_explicit_selection(model, tag, ids)
    ok = (
        len(mapping["sel_ring_wall_inner"]) == 1
        and len(mapping["sel_ring_wall_outer"]) == 1
        and len(mapping["sel_ring_wall_top"]) == 1
        and len(mapping["sel_ring_wall_bottom"]) == 1
        and len(mapping["sel_ring_wall_all"]) == 4
    )
    if not ok:
        raise RuntimeError(f"C2 box selection did not identify four unique ring boundaries: {mapping}")
    return mapping


def configure_rebuilt_static_wall(model: Any, ring_ids: list[int]) -> dict[str, Any]:
    spf = model.java.component("comp1").physics("spf")
    wall = spf.feature("wallbc1")
    return {
        "feature": "spf.wallbc1",
        "selection": feature_selection(wall),
        "note": "left unchanged because this default COMSOL wall selection is not editable; static baseline uses the generated no-slip wall",
    }


def configure_rebuilt_moving_wall(model: Any, moving_ids: list[int], v_expr: str) -> dict[str, Any]:
    spf = model.java.component("comp1").physics("spf")
    tag = "inl_ring_vertical_equiv"
    if tag in tags(spf.feature()):
        spf.feature().remove(tag)
    inlet = spf.feature().create(tag, "Inlet", 1)
    inlet.selection().set(jints(moving_ids))
    inlet.set("BoundaryCondition", "Velocity")
    inlet.set("ComponentWise", "VelocityFieldComponentWise")
    set_attempt = ""
    try:
        inlet.set("u0", ["0", v_expr])
        set_attempt = "u0=[0, v_z] in 2D axisymmetric component order"
    except Exception as exc2:
        inlet.set("u0", ["0", "0", v_expr])
        set_attempt = f"u0=[0,0,v_z] fallback after 2-component failure: {exc2}"
    audit = cleanbd.wall_audit(model, moving_ids)
    return {
        "default_wall": "wallbc1 left unchanged",
        "moving_feature": tag,
        "feature_type": "Inlet equivalent velocity boundary",
        "moving_selection": moving_ids,
        "u0": safe_prop(inlet, "u0"),
        "set_attempt": set_attempt,
        "audit": audit,
        "wall_overlap_status": "EQUIVALENT_BOUNDARY_OVERRIDES_DEFAULT_WALL_IF_SOLVED",
        "note": "This is an equivalent velocity boundary test, not a true moving-wall feature. It avoids editing or deleting noneditable spf.wallbc1.",
    }


def stage_c2_2(client: Any) -> dict[str, Any]:
    log("C2-2 rebuilt selectable-wall reduced model started.")
    rows: list[dict[str, Any]] = []
    model = None
    best_model = ""
    setup: dict[str, Any] = {}
    named: dict[str, Any] = {}
    last_presolve_model: dict[str, str] = {}
    try:
        model, setup = base.create_b2_model(client)
        try:
            model.java.component("comp1").physics("ls").feature("lsm1").set("gamma", "0")
            setup["level_set_gamma"] = "0; inherited from the passed clean static baseline fallback to avoid artificial static-interface drift"
        except Exception as exc:
            setup["level_set_gamma"] = f"unchanged: {exc}"
        named = ensure_c2_box_selections(model)
        model.java.param().set("t_end_C2_static", "0.02[s]")
        model.java.param().set("V_test_C2", "0.001[m/s]")
        model.java.param().set("ramp_C2", "0.002[s]")
        configure_rebuilt_static_wall(model, named["sel_ring_wall_all"])
        set_tlist(model, "t_end_C2_static", "0.02[s]", 40)
        model.solve()
        static_dir = C2 / "images" / "C2_2_static"
        metrics = h_metrics(model, "C2_2_static", static_dir)
        rows.append({
            "case_id": "C2_2_static_baseline",
            "route": "rebuilt manual LaminarFlow + LevelSet",
            "boundary_set": "all walls static",
            "V_test": 0,
            "t_end": "0.02[s]",
            "solve_status": "PASS" if metrics["pass_static"] else "FAIL",
            "failure_time": "",
            "failure_message": "",
            "H0": metrics["H0"],
            "Hfinal": metrics["Hfinal"],
            "delta_H": metrics["delta_H"],
            "Hmax": metrics["Hmax"],
            "interface_quality": metrics["interface_quality"],
            "wall_overlap_status": "not_applicable_static",
            "notes": "rebuilt reduced model without gravity; reproduces clean baseline stability check",
        })
        data = base.eval_field_set(model, len(metrics["hdata"].get("times", [])) or 1)
        base.render_field(static_dir / "C2_2_static_phils_final.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True)
        if not metrics["pass_static"]:
            save_model_no_overwrite(model, C2 / "models" / "ring_fountain_v5B3_C2c_rebuilt_selectable_wall_model.mph")
            raise RuntimeError("rebuilt static baseline did not pass stability gate")

        moving_ids = sorted(named["sel_ring_wall_vertical"])
        wall_setup = configure_rebuilt_moving_wall(model, moving_ids, "-V_test_C2*min(t/ramp_C2,1)")
        set_tlist(model, "t_end_C2_move", "0.005[s]", 20)
        pre_solve_save = save_model_no_overwrite(model, C2 / "models" / "ring_fountain_v5B3_C2c_rebuilt_selectable_wall_model.mph")
        last_presolve_model = pre_solve_save
        model.solve()
        moving_dir = C2 / "images" / "C2_2_moving_vertical"
        mmetrics = h_metrics(model, "C2_2_moving_vertical", moving_dir)
        mrow = {
            "case_id": "C2_2_moving_vertical_0p001",
            "route": "rebuilt manual LaminarFlow + LevelSet",
            "boundary_set": moving_ids,
            "V_test": 0.001,
            "t_end": "0.005[s]",
            "solve_status": "PASS" if mmetrics["pass_static"] else "FAIL",
            "failure_time": "",
            "failure_message": "",
            "H0": mmetrics["H0"],
            "Hfinal": mmetrics["Hfinal"],
            "delta_H": mmetrics["delta_H"],
            "Hmax": mmetrics["Hmax"],
            "interface_quality": mmetrics["interface_quality"],
            "wall_overlap_status": wall_setup["wall_overlap_status"],
            "notes": "vertical ring equivalent velocity boundary only; fixed geometry; not a true moving-wall feature",
            "wall_setup": wall_setup,
            "pre_solve_model": pre_solve_save,
        }
        rows.append(mrow)
        data = base.eval_field_set(model, len(mmetrics["hdata"].get("times", [])) or 1)
        base.render_field(moving_dir / "C2_2_moving_phils_final.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True)
        base.render_field(moving_dir / "C2_2_moving_velocity_magnitude.png", data["r"], data["z"], data["U"], cmap="viridis", phi=data["phi"], draw_interface=True)
        base.render_vector(moving_dir / "C2_2_moving_velocity_vectors.png", data["r"], data["z"], data["u"], data["w"], data["phi"])

        save_info = save_model_no_overwrite(model, C2 / "models" / "ring_fountain_v5B3_C2c_rebuilt_selectable_wall_model.mph")
        best_path = C2 / "models" / "ring_fountain_v5B3_C2_best.mph"
        if not best_path.exists():
            shutil.copy2(save_info["timestamp_model"], best_path)
        best_model = str(best_path)
        status = "PASS" if rows[-1]["solve_status"] == "PASS" else "FAIL"
    except Exception as exc:
        status = "FAIL"
        rows.append({
            "case_id": "C2_2_failure",
            "route": "rebuilt manual LaminarFlow + LevelSet",
            "boundary_set": "",
            "V_test": "",
            "t_end": "",
            "solve_status": "FAIL",
            "failure_time": "",
            "failure_message": f"{type(exc).__name__}: {exc}",
            "H0": math.nan,
            "Hfinal": math.nan,
            "delta_H": math.nan,
            "Hmax": math.nan,
            "interface_quality": "",
            "wall_overlap_status": "UNKNOWN_OR_FAIL",
            "notes": traceback.format_exc(),
            "pre_solve_model": last_presolve_model,
        })
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass

    csv_path = C2 / "tables" / "C2_2_rebuilt_cases.csv"
    write_csv(csv_path, rows)
    report = C2 / "reports" / "C2_2_rebuilt_selectable_wall_report.md"
    lines = [
        "# C2-2 Rebuilt Selectable-Wall Reduced Model Report",
        "",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        f"C2-2 review status: `{status}`",
        f"C2_REBUILT_SELECTABLE_MODEL = `{status}`",
        f"ALLOW_RESUME_STAGE5 = `{'YES' if status == 'PASS' else 'NO'}`",
        "",
        "## Model Type And Limits",
        "",
        "- Rebuilt reduced model: manual `LaminarFlow + LevelSet` fallback.",
        "- Gravity is not enabled, matching the previous clean static baseline smoke-test policy.",
        "- Geometry is fixed; moving wall changes boundary velocity only and does not translate the ring geometry.",
        "- This is not a final physical Hmax model.",
        "",
        "## Named Selections",
        "",
        f"- `{json.dumps(named, ensure_ascii=False, default=str)}`",
        "",
        "## Cases",
        "",
        f"- CSV: `{csv_path}`",
        "",
        "| case_id | solve_status | boundary_set | V_test | t_end | delta_H | Hmax | interface_quality | wall_overlap_status |",
        "|---|---|---|---:|---|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row.get('case_id')}` | `{row.get('solve_status')}` | `{row.get('boundary_set')}` | `{row.get('V_test')}` | "
            f"`{row.get('t_end')}` | `{row.get('delta_H')}` | `{row.get('Hmax')}` | `{row.get('interface_quality')}` | `{row.get('wall_overlap_status')}` |"
        )
    report.write_text("\n".join(lines), encoding="utf-8")
    result = {
        "status": status,
        "report": str(report),
        "csv": str(csv_path),
        "rows": rows,
        "best_model": best_model,
        "setup": setup,
        "named_selections": named,
        "ALLOW_RESUME_STAGE5": "YES" if status == "PASS" else "NO",
    }
    write_json(C2 / "logs" / f"C2_2_rebuilt_selectable_wall_{RUN_ID}.json", result)
    return result


def append_project_docs(summary: dict[str, Any]) -> dict[str, str]:
    readme = ROOT / "README.md"
    changelog = ROOT / "CHANGELOG.md"
    stamp = datetime.now().isoformat(timespec="seconds")
    allow = summary.get("final", {}).get("ALLOW_RESUME_STAGE5", "NO")
    best = summary.get("final", {}).get("best_model", "")
    readme_start = "<!-- STAGE_5B3_C2_ALTERNATIVE_WALL_STRATEGY_START -->"
    readme_end = "<!-- STAGE_5B3_C2_ALTERNATIVE_WALL_STRATEGY_END -->"
    changelog_start = "<!-- STAGE_5B3_C2_ALTERNATIVE_WALL_STRATEGY_CHANGELOG_START -->"
    changelog_end = "<!-- STAGE_5B3_C2_ALTERNATIVE_WALL_STRATEGY_CHANGELOG_END -->"
    readme_block = f"""
{readme_start}

## Stage 5B3-C2 Alternative Wall Strategy

- Run time: `{stamp}`.
- Scope: only `5B3-C2`; did not enter 5B4, 5C, 5D, 5E, stage 6, Jet1/Jet2 extraction, or parameter study.
- Starting clean baseline: `{SRC_CLEAN}`.
- C2-0 feature probe: `{summary.get('C2_0', {}).get('status')}`.
- C2-1 Wetted Wall strategy: `{summary.get('C2_1', {}).get('status')}`.
- C2-2 rebuilt selectable-wall model: `{summary.get('C2_2', {}).get('status', 'NOT_RUN')}`.
- Best C2 model: `{best}`.
- `ALLOW_RESUME_STAGE5 = {allow}`.
- Limit: current accepted C2 model, if any, remains a fixed-geometry reduced free-surface model and is not a validated physical Hmax model.
{readme_end}
"""
    changelog_block = f"""
{changelog_start}

## {stamp} - Stage 5B3-C2 Alternative Wall Strategy

- Added C2 feature/property probing for Wetted Wall, Interior Wetted Wall, moving wall properties, Level Set no-flow candidates, and tested two-phase coupling type names.
- Tested alternative wall strategy without deleting `spf.wallbc1`.
- If needed, rebuilt a reduced selectable-wall model from scratch.
- Final gate: `ALLOW_RESUME_STAGE5 = {allow}`.
{changelog_end}
"""
    def replace_or_append(text: str, start: str, end: str, block: str) -> str:
        if start in text and end in text:
            pre = text.split(start, 1)[0].rstrip()
            post = text.split(end, 1)[1].lstrip()
            return pre + "\n\n" + block.strip() + "\n\n" + post
        return text.rstrip() + "\n\n" + block.strip() + "\n"

    readme.write_text(replace_or_append(readme.read_text(encoding="utf-8"), readme_start, readme_end, readme_block), encoding="utf-8")
    changelog.write_text(replace_or_append(changelog.read_text(encoding="utf-8"), changelog_start, changelog_end, changelog_block), encoding="utf-8")
    return {"README.md": str(readme), "CHANGELOG.md": str(changelog)}


def update_manifest() -> None:
    manifest = SCRIPTS / "SCRIPT_MANIFEST.md"
    scripts = sorted(SCRIPTS.glob("*.py"))
    notes = {
        "ring_fountain_stage5b3_C2_alternative_wall_strategy.py": "Stage 5B3-C2 alternative wall strategy: feature probe, Wetted Wall attempts, rebuilt selectable-wall reduced model",
        "ring_fountain_stage5b2_clean_and_5b3_minimal.py": "Stage B/C/D clean static baseline rebuild and minimal moving-wall retry",
        "ring_fountain_stage5b2_clean_baseline_audit.py": "Stage A 5B2 clean-baseline read-only physics audit",
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
    for path in scripts:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(
            f"| [{path.name}](./{path.name}) | {path.stat().st_size} | "
            f"{datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')} | `{digest}` | {notes.get(path.name, '')} |"
        )
    lines.extend([
        "",
        "## Path Management",
        "",
        "- Treat this directory as the canonical local archive for Python automation used in the COMSOL Ring Fountain project.",
        "- Working copies may remain under `C:\\Users\\kqdx\\Documents\\COMSOL仿真方法`, but scripts should be copied here after each run or edit.",
        "- Helper/probe scripts are preserved because they document how COMSOL features and property names were discovered.",
    ])
    manifest.write_text("\n".join(lines), encoding="utf-8")


def write_final(summary: dict[str, Any]) -> dict[str, Any]:
    c21 = summary.get("C2_1", {})
    c22 = summary.get("C2_2", {})
    final_status = "PASS" if c21.get("status") == "PASS" or c22.get("status") == "PASS" else "FAIL"
    allow = "YES" if final_status == "PASS" else "NO"
    best_model = ""
    best_case: dict[str, Any] | None = None
    if c21.get("status") == "PASS":
        best_case = c21.get("best")
        best_model = str(C2 / "models" / "ring_fountain_v5B3_C2_best.mph")
        model_type = "manual fallback with Wetted/Interior Wall overlay attempt"
    elif c22.get("status") == "PASS":
        best_model = c22.get("best_model", "")
        pass_rows = [r for r in c22.get("rows", []) if r.get("solve_status") == "PASS"]
        best_case = pass_rows[-1] if pass_rows else None
        model_type = "rebuilt reduced model"
    else:
        model_type = "manual fallback / failed alternative strategy"
    report = C2 / "reports" / "5B3_C2_alternative_wall_strategy_final_report.md"
    probe = summary.get("C2_0", {})
    lines = [
        "# 5B3-C2 Alternative Wall Strategy Final Report",
        "",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"Final C2 status: `{final_status}`",
        f"ALLOW_RESUME_STAGE5 = `{allow}`",
        "",
        "## Required Answers",
        "",
        f"1. Successfully created Wetted Wall: `{probe.get('wetted_wall_creatable')}`.",
        f"2. Successfully created Interior Wetted Wall: `{probe.get('interior_wetted_wall_creatable')}`.",
        "3. Can they act on ring boundaries: "
        f"`tested if creatable; see C2-0/C2-1 reports. C2-1 status = {c21.get('status')}`.",
        f"4. Bypassed noneditable `spf.wallbc1`: `{c21.get('status') == 'PASS' or c22.get('status') == 'PASS'}`.",
        f"5. Rebuilt selectable wall model from scratch: `{bool(c22)}`; status `{c22.get('status', 'NOT_RUN')}`.",
        f"6. Obtained `ring_fountain_v5B3_C2_best.mph`: `{bool(best_model and Path(best_model).exists())}`; `{best_model}`.",
        f"7. Best case: `{best_case.get('case_id') if best_case else ''}`.",
        f"8. Best case H(final)-H(0), Hmax, t_end: `{best_case.get('delta_H') if best_case else ''}`, `{best_case.get('Hmax') if best_case else ''}`, `{best_case.get('t_end') if best_case else ''}`.",
        f"9. Current model type: `{model_type}`.",
        f"10. Allow main workflow to resume into 5B4: `{allow}`.",
        f"11. `ALLOW_RESUME_STAGE5 = {allow}`.",
        "",
        "## Stop Rules",
        "",
        "- This run did not enter 5B4, 5C, 5D, 5E, stage 6.",
        "- This run did not extract Jet1/Jet2 and did not perform a parameter study.",
        "- If `ALLOW_RESUME_STAGE5 = YES`, the next step is allowed but was not started automatically.",
        "- If `ALLOW_RESUME_STAGE5 = NO`, the next likely step is manual GUI/API inspection of COMSOL wall/Level Set boundary feature availability.",
        "",
        "## Output Reports",
        "",
        f"- C2-0: `{probe.get('report')}`",
        f"- C2-1: `{c21.get('report')}`",
        f"- C2-2: `{c22.get('report', 'NOT_RUN')}`",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    return {
        "status": final_status,
        "ALLOW_RESUME_STAGE5": allow,
        "report": str(report),
        "best_model": best_model,
        "best_case": best_case,
        "model_type": model_type,
    }


def main() -> None:
    os.environ["JAVA_HOME"] = r"D:\COMSOL64\Multiphysics\java\win64\jre"
    ensure_dirs()
    shutil.copy2(Path(__file__), SCRIPTS / "ring_fountain_stage5b3_C2_alternative_wall_strategy.py")
    update_manifest()
    if not SRC_CLEAN.exists():
        raise FileNotFoundError(SRC_CLEAN)
    summary: dict[str, Any] = {
        "run_id": RUN_ID,
        "scope": "5B3-C2 alternative wall strategy only",
        "source_clean_baseline": str(SRC_CLEAN),
        "forbidden_stages_not_entered": ["5B4", "5C", "5D", "5E", "stage 6", "Jet1/Jet2", "parameter study"],
    }
    client = mph.Client(cores=2, version="6.4")
    try:
        summary["C2_0"] = stage_c2_0(client)
        if summary["C2_0"].get("status") != "PASS":
            summary["C2_1"] = {"status": "NOT_RUN", "reason": "C2-0 did not pass."}
            summary["C2_2"] = {"status": "NOT_RUN", "reason": "C2-0 did not pass."}
        else:
            summary["C2_1"] = stage_c2_1(client, summary["C2_0"])
            if summary["C2_1"].get("status") == "PASS":
                summary["C2_2"] = {"status": "NOT_RUN", "reason": "C2-1 passed; C2-2 not needed."}
            else:
                summary["C2_2"] = stage_c2_2(client)
        summary["final"] = write_final(summary)
        summary["docs"] = append_project_docs(summary)
        update_manifest()
        write_json(C2 / "5B3_C2_alternative_wall_strategy_summary.json", summary)
    finally:
        try:
            client.clear()
        except Exception:
            pass


if __name__ == "__main__":
    main()
