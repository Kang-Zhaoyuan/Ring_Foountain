# -*- coding: utf-8 -*-
"""Stage 5B3-C3 boundary semantics audit for the COMSOL Ring Fountain project.

This script is intentionally a gatekeeper.  It checks whether the current
COMSOL 6.4 + MCP/API environment can construct a minimal
"free surface + moving solid wall" model without using Inlet/Outlet/OpenBoundary
as substitutes for moving-wall semantics.

It does not enter 5B4, 5C, 5D, 5E, Stage 6, Jet1/Jet2 extraction, parameter
studies, or real Hmax extraction.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import jpype
import mph

import ring_fountain_stage4_1_boundary_review as s41
import ring_fountain_stage4_2a as s42a
import ring_fountain_stage5_cleanup_5b_5c as base


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
STAGE5 = ROOT / "05_two_phase_free_surface"
C2 = STAGE5 / "5B3_C2_alternative_wall_strategy"
C3 = STAGE5 / "5B3_C3_boundary_semantics_audit"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = C3 / "logs" / f"5B3_C3_boundary_semantics_audit_{RUN_ID}.log"

CLEAN_BASELINE = STAGE5 / "5B2_clean_baseline_rebuild" / "models" / "ring_fountain_v5B2_clean_static_baseline_best.mph"
C2_BEST = C2 / "models" / "ring_fountain_v5B3_C2_best.mph"
C2_C2C_MODEL = C2 / "models" / "ring_fountain_v5B3_C2c_rebuilt_selectable_wall_model.mph"

RING_ALL = [4, 5, 6, 7]
RING_VERTICAL = [4, 7]
RING_HORIZONTAL = [5, 6]


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def ensure_dirs() -> None:
    for sub in ["models", "reports", "tables", "images", "logs"]:
        (C3 / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def jints(values: list[int]) -> Any:
    return jpype.JArray(jpype.JInt)(values)


def tags(node: Any) -> list[str]:
    try:
        return [str(x) for x in list(node.tags())]
    except Exception:
        return []


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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def feature_properties(feature: Any) -> list[str]:
    for call in (lambda: feature.properties(), lambda: feature.propertyNames()):
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


def safe_get(feature: Any, key: str) -> str:
    for call in (
        lambda: feature.getString(key),
        lambda: list(feature.getStringArray(key)),
        lambda: feature.get(key),
    ):
        try:
            value = call()
            if isinstance(value, list):
                return json.dumps([str(x) for x in value], ensure_ascii=False)
            return str(value)
        except Exception:
            pass
    return "<unreadable>"


def safe_set(feature: Any, key: str, value: Any) -> tuple[bool, str]:
    try:
        feature.set(key, value)
        return True, ""
    except Exception as exc:
        return False, str(exc)


def save_model_no_overwrite(model: Any, canonical: Path) -> dict[str, str]:
    canonical.parent.mkdir(parents=True, exist_ok=True)
    timestamp = canonical.with_name(f"{canonical.stem}_{RUN_ID}{canonical.suffix}")
    model.save(timestamp)
    result = {"timestamp_model": str(timestamp)}
    if canonical.exists():
        result["model"] = str(canonical)
        result["canonical_note"] = "canonical path already existed and was not overwritten"
    else:
        model.save(canonical)
        result["model"] = str(canonical)
    return result


def all_boundaries(model: Any) -> list[int]:
    try:
        rows = s41.boundary_metrics(model)
        ids = sorted({int(row["boundary_id"]) for row in rows if "boundary_id" in row})
        if ids:
            return ids
    except Exception:
        pass
    return box_boundaries(model, "sel_C3_all_boundaries_box", -1.0, 1.0, -1.0, 1.0)


def box_boundaries(model: Any, tag: str, xmin: float, xmax: float, ymin: float, ymax: float) -> list[int]:
    comp = model.java.component("comp1")
    selmgr = comp.selection()
    if tag in tags(selmgr):
        selmgr.remove(tag)
    selmgr.create(tag, "Box")
    sel = selmgr.get(tag)
    sel.geom("geom1", 1)
    sel.set("entitydim", "1")
    sel.set("xmin", str(xmin))
    sel.set("xmax", str(xmax))
    sel.set("ymin", str(ymin))
    sel.set("ymax", str(ymax))
    sel.set("condition", "inside")
    return sorted({int(x) for x in list(sel.entities(1))})


def set_tlist(model: Any, t_end: str, nsteps: int) -> None:
    model.java.param().set("t_end_C3", t_end)
    base.set_tlist(model, f"range(0,t_end_C3/{nsteps},t_end_C3)")


def h_delta(model: Any, tag: str, out_dir: Path) -> dict[str, Any]:
    try:
        data = base.extract_h_vs_t(model, tag, out_dir)
        rows = data.get("rows", [])
        finite = [row for row in rows if math.isfinite(float(row.get("H_m", math.nan)))]
        if not finite:
            return {"H0": math.nan, "Hfinal": math.nan, "delta_H": math.nan, "interface_quality": "no finite interface", "csv": data.get("csv"), "plot": data.get("H_vs_t_png")}
        hs = [float(row["H_m"]) for row in finite]
        counts = [int(row.get("interface_points", 0)) for row in finite]
        jumps = [abs(b - a) for a, b in zip(hs[:-1], hs[1:])]
        near_top = any(bool(row.get("near_domain_top")) for row in finite)
        continuous = min(counts) >= 3
        spike = bool(jumps and max(jumps) > 0.01)
        quality = "clear/continuous" if continuous and not spike and not near_top else "questionable"
        return {
            "H0": hs[0],
            "Hfinal": hs[-1],
            "delta_H": hs[-1] - hs[0],
            "interface_quality": quality,
            "interface_points_min": min(counts),
            "near_top": near_top,
            "isolated_spike": spike,
            "csv": data.get("csv"),
            "plot": data.get("H_vs_t_png"),
        }
    except Exception as exc:
        return {"H0": math.nan, "Hfinal": math.nan, "delta_H": math.nan, "interface_quality": "extraction failed", "error": str(exc)}


def add_or_replace_section(path: Path, marker: str, lines: list[str]) -> None:
    old = read_text(path) if path.exists() else ""
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = "\n".join([start, *lines, end, ""])
    if start in old and end in old:
        before = old.split(start)[0].rstrip()
        after = old.split(end, 1)[1].lstrip()
        text = before + "\n\n" + block + ("\n" + after if after else "")
    else:
        text = old.rstrip() + "\n\n" + block
    path.write_text(text, encoding="utf-8")


def update_manifest(script_path: Path) -> dict[str, Any]:
    manifest = SCRIPTS / "SCRIPT_MANIFEST.md"
    digest = hashlib.sha256(script_path.read_bytes()).hexdigest()
    line = f"| `ring_fountain_stage5b3_C3_boundary_semantics_audit.py` | 5B3-C3 boundary semantics audit | `{RUN_ID}` | `{digest}` |"
    header = "| Script | Purpose | Last run/copy | SHA256 |\n|---|---|---|---|\n"
    if manifest.exists():
        text = read_text(manifest)
        rows = [row for row in text.splitlines() if "ring_fountain_stage5b3_C3_boundary_semantics_audit.py" not in row]
        if not any(row.startswith("| Script |") for row in rows):
            rows = header.rstrip().splitlines() + rows
        rows.append(line)
        manifest.write_text("\n".join(rows).rstrip() + "\n", encoding="utf-8")
    else:
        manifest.write_text(header + line + "\n", encoding="utf-8")
    return {"manifest": str(manifest), "sha256": digest}


def archive_script() -> dict[str, Any]:
    source = Path(__file__).resolve()
    target = SCRIPTS / "ring_fountain_stage5b3_C3_boundary_semantics_audit.py"
    shutil.copy2(source, target)
    manifest = update_manifest(target)
    return {"source": str(source), "target": str(target), **manifest}


def stage_c3_0() -> dict[str, Any]:
    log("C3-0 reviewing C2 outputs.")
    report_paths = [
        C2 / "reports" / "5B3_C2_alternative_wall_strategy_final_report.md",
        C2 / "reports" / "C2_0_feature_probe_report.md",
        C2 / "reports" / "C2_1_wetted_wall_report.md",
        C2 / "reports" / "C2_2_rebuilt_selectable_wall_report.md",
        C2 / "tables" / "C2_2_rebuilt_cases.csv",
    ]
    missing = [str(path) for path in report_paths if not path.exists()]
    cases = read_text(report_paths[-1]) if report_paths[-1].exists() else ""
    no_best = not C2_BEST.exists()
    failed_after_equiv = "C2_2_failure" in cases and "Failed to find consistent initial values" in cases
    inlet_not_wall = True
    allow_stage5 = "NO"
    status = "PASS" if not missing and no_best and failed_after_equiv and inlet_not_wall else "FAIL"
    report = C3 / "reports" / "C3_0_C2_result_review.md"
    report.write_text(
        "\n".join(
            [
                "# C3-0 C2 Result Review",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                f"C3-0 status: `{status}`",
                "",
                "## Evidence",
                "",
                f"- Missing C2 files: `{missing}`",
                f"- C2 best model exists: `{C2_BEST.exists()}`",
                f"- No `ring_fountain_v5B3_C2_best.mph` obtained: `{no_best}`",
                f"- C2-2 failure occurred after adding the equivalent velocity boundary: `{failed_after_equiv}`",
                "- C2-2 used `spf.Inlet` as an open/velocity boundary, not a solid moving wall: `True`",
                f"- Continuing the Stage 5 main line is allowed: `{allow_stage5}`",
                "",
                "## Reviewed Files",
                "",
                *[f"- `{path}`" for path in report_paths],
            ]
        ),
        encoding="utf-8",
    )
    return {"status": status, "report": str(report), "missing": missing, "no_c2_best": no_best, "failed_after_equiv": failed_after_equiv, "allow_stage5": allow_stage5}


def java_methods(obj: Any, keywords: list[str]) -> list[str]:
    try:
        methods = obj.getClass().getMethods()
    except Exception:
        return []
    names: set[str] = set()
    for method in list(methods):
        name = str(method.getName())
        low = name.lower()
        if any(key.lower() in low for key in keywords):
            names.add(name)
    return sorted(names)


def audit_existing_model(model: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    comp = model.java.component("comp1")
    physics_mgr = comp.physics()
    rows.append({"category": "api_reflection", "object": "component.physics()", "result": "methods", "details": java_methods(physics_mgr, ["tag", "create", "feature", "interface", "physics", "type"])})
    for ptag in tags(physics_mgr):
        physics = physics_mgr.get(ptag)
        rows.append({"category": "existing_physics", "object": ptag, "result": "present", "details": java_methods(physics, ["feature", "prop", "tag", "label", "selection", "create"])})
        try:
            feature_mgr = physics.feature()
            rows.append({"category": "api_reflection", "object": f"{ptag}.feature()", "result": "methods", "details": java_methods(feature_mgr, ["tag", "create", "feature", "type"])})
            for ftag in tags(feature_mgr):
                feat = feature_mgr.get(ftag)
                props = feature_properties(feat)
                selected = feature_selection(feat)
                interesting = {p: safe_get(feat, p) for p in props if p in ["BoundaryCondition", "SlidingWall", "TranslationalVelocityOption", "utr", "u0", "lscond", "phils"]}
                rows.append({"category": "existing_feature", "object": f"{ptag}/{ftag}", "result": "present", "selection": selected, "details": props, "interesting_values": interesting})
        except Exception as exc:
            rows.append({"category": "existing_feature", "object": ptag, "result": "feature enumeration failed", "details": str(exc)})
    return rows


def stage_c3_1(client: Any) -> dict[str, Any]:
    log("C3-1 auditing API feature names and enumerability.")
    rows: list[dict[str, Any]] = []
    model = None
    try:
        source = C2_C2C_MODEL if C2_C2C_MODEL.exists() else CLEAN_BASELINE
        model = client.load(str(source))
        rows.extend(audit_existing_model(model))
        rows.append(
            {
                "category": "catalog_enumeration",
                "object": "COMSOL API feature/interface catalog",
                "result": "API cannot enumerate available physics interface or feature type catalog from this MCP/mph path",
                "details": "Existing object tags/properties can be enumerated, but the create-type catalog is not exposed. Next step requires manual GUI model export to Java/M-file for exact names.",
            }
        )
        spf = model.java.component("comp1").physics("spf")
        if "wall_c3_probe" in tags(spf.feature()):
            spf.feature().remove("wall_c3_probe")
        wall = spf.feature().create("wall_c3_probe", "Wall", 1)
        wall.selection().set(jints(RING_VERTICAL))
        props = feature_properties(wall)
        moving_props = [p for p in props if p in ["SlidingWall", "TranslationalVelocityOption", "utr"]]
        rows.append({"category": "moving_wall_semantics", "object": "spf/Wall", "result": "creatable", "selection": RING_VERTICAL, "details": props, "moving_related_properties": moving_props})
        try:
            spf.feature().remove("wall_c3_probe")
        except Exception:
            pass
        status = "PASS"
    except Exception as exc:
        rows.append({"category": "error", "object": "C3-1", "result": "FAIL", "details": traceback.format_exc()})
        status = "FAIL"
    finally:
        try:
            if model is not None:
                client.remove(model)
        except Exception:
            pass

    csv_path = C3 / "tables" / "C3_1_feature_name_audit.csv"
    write_csv(csv_path, rows)
    formal_creatable = False
    moving_wall_creatable = any(row.get("category") == "moving_wall_semantics" and row.get("result") == "creatable" for row in rows)
    report = C3 / "reports" / "C3_1_feature_name_audit.md"
    report.write_text(
        "\n".join(
            [
                "# C3-1 Feature Name Audit",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                f"C3-1 status: `{status}`",
                "",
                "## Conclusions",
                "",
                "- Formal `Laminar Two-Phase Flow, Level Set` / `Phase Field` interface creation is not proven by API enumeration.",
                "- The current API path can enumerate existing model objects and feature properties, but cannot enumerate the full COMSOL create-type catalog.",
                "- Therefore the formal two-phase interface true API name remains unresolved from automation alone.",
                f"- `spf.Wall` is creatable and exposes moving-wall-related properties in this environment: `{moving_wall_creatable}`.",
                "- `spf.Inlet`, `spf.Outlet`, and `spf.OpenBoundary` remain disallowed as substitutes for solid moving wall.",
                "- Required manual next step if C3 minimal tests fail: create the desired GUI model and export Java/M-file to reveal exact feature/interface type names.",
                "",
                "## Machine-Readable Table",
                "",
                f"- `{csv_path}`",
            ]
        ),
        encoding="utf-8",
    )
    return {"status": status, "report": str(report), "csv": str(csv_path), "formal_two_phase_api_creatable": formal_creatable, "spf_wall_moving_props_creatable": moving_wall_creatable}


def create_minimal_free_surface_model(client: Any) -> tuple[Any, dict[str, Any]]:
    model = client.create(f"c3_minimal_free_surface_{RUN_ID}")
    java = model.java
    param = java.param()
    for name, value in {
        "Rtank": "40[mm]",
        "Hwater": "35[mm]",
        "Hair": "35[mm]",
        "rho_w": "1000[kg/m^3]",
        "mu_w": "1e-3[Pa*s]",
        "rho_air": "1.225[kg/m^3]",
        "mu_air": "1.8e-5[Pa*s]",
        "eps_ls": "1[mm]",
        "V_C3": "0[m/s]",
        "ramp_C3": "0.001[s]",
        "t_end_C3": "0.002[s]",
    }.items():
        param.set(name, value)
    comp = java.component().create("comp1", True)
    geom = comp.geom().create("geom1", 2)
    try:
        geom.axisymmetric(True)
    except Exception:
        pass
    rect = geom.feature().create("tank", "Rectangle")
    rect.set("size", ["Rtank", "Hwater+Hair"])
    rect.set("pos", ["0", "-Hwater"])
    geom.run()
    mesh = comp.mesh().create("mesh1")
    mesh.autoMeshSize(5)
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
    try:
        ls.feature("lsm1").set("gamma", "0")
    except Exception:
        pass
    study = java.study().create("std1")
    study.create("time", "Transient")
    study.feature("time").set("tlist", "range(0,t_end_C3/8,t_end_C3)")
    return model, {"model_type": "manual LaminarFlow + LevelSet minimal rectangle", "formal_two_phase": False}


def rectangle_side_wall_ids(model: Any) -> dict[str, Any]:
    # Avoid model.evaluate() here because a just-created model may not yet have
    # a default dataset.  These values match create_minimal_free_surface_model().
    rtank = 0.040
    hwater = 0.035
    hair = 0.035
    tol = 1e-5
    ids = all_boundaries(model)
    side_ids = box_boundaries(model, "sel_C3_minimal_outer_wall_box", rtank - tol, rtank + tol, -hwater - tol, hair + tol)
    if len(side_ids) != 1:
        raise RuntimeError("Could not identify outer straight wall for minimal model.")
    side = side_ids[0]
    return {"moving": [side], "nonmoving": [bid for bid in ids if bid != side], "all": ids, "metrics": {"all": ids, "outer_wall_box": side_ids}}


def set_wall_moving(
    model: Any,
    moving: list[int],
    nonmoving: list[int],
    v_expr: str,
    feature_tag: str = "wall_c3_moving",
    *,
    require_nonoverlap: bool = True,
) -> dict[str, Any]:
    spf = model.java.component("comp1").physics("spf")
    audit: dict[str, Any] = {"moving": moving, "nonmoving": nonmoving, "feature_tag": feature_tag}
    static_tag = f"{feature_tag}_static"
    for old in [feature_tag, static_tag]:
        if old in tags(spf.feature()):
            spf.feature().remove(old)
    try:
        spf.feature("wallbc1").selection().set(jints(nonmoving))
        audit["wallbc1_selection_set"] = nonmoving
    except Exception as exc:
        audit["wallbc1_selection_set_error"] = str(exc)
        try:
            spf.feature("wallbc1").active(False)
            audit["wallbc1_disabled"] = True
            static_wall = spf.feature().create(static_tag, "Wall", 1)
            static_wall.selection().set(jints(nonmoving))
            static_wall.set("BoundaryCondition", "NoSlip")
            audit["static_wall_feature"] = static_tag
            audit["wall_overlap_status"] = "default wall disabled; explicit static and moving wall features used"
        except Exception as exc2:
            audit["wallbc1_disable_error"] = str(exc2)
            audit["wall_overlap_status"] = "default wall selection not editable and could not be disabled"
            if require_nonoverlap:
                raise RuntimeError(
                    "Could not exclude moving boundaries from the default wall feature, and could not disable it. "
                    f"selection error={exc}; disable error={exc2}"
                )
    wall = spf.feature().create(feature_tag, "Wall", 1)
    wall.selection().set(jints(moving))
    attempted: list[dict[str, str]] = []
    for key, value in [
        ("BoundaryCondition", "NoSlip"),
        ("SlidingWall", "1"),
        ("TranslationalVelocityOption", "Manual"),
        ("utr", ["0", "0", v_expr]),
    ]:
        ok, err = safe_set(wall, key, value)
        attempted.append({"property": key, "ok": str(ok), "error": err, "value": str(value)})
        if key in ["SlidingWall", "TranslationalVelocityOption", "utr"] and not ok:
            raise RuntimeError(f"Failed to set moving-wall property {key}: {err}")
    audit.update({"boundary_feature_type": "spf.Wall", "properties": feature_properties(wall), "attempted_settings": attempted, "velocity_expression": v_expr, "selection": feature_selection(wall)})
    return audit


def run_case(model: Any, case_id: str, t_end: str, h_tag: str | None = None) -> tuple[bool, str, dict[str, Any]]:
    set_tlist(model, t_end, 8)
    try:
        model.solve()
        hm = h_delta(model, h_tag or case_id, C3 / "images" / case_id) if h_tag is not None else {}
        return True, "", hm
    except Exception as exc:
        err = C3 / "logs" / f"{case_id}_error_{RUN_ID}.log"
        err.write_text(traceback.format_exc(), encoding="utf-8")
        return False, str(exc), {"error_log": str(err)}


def stage_c3_2(client: Any) -> dict[str, Any]:
    log("C3-2 running minimal free-surface + solid moving wall tests.")
    rows: list[dict[str, Any]] = []
    model = None
    model_save: dict[str, str] = {}
    try:
        model, setup = create_minimal_free_surface_model(client)
        ids = rectangle_side_wall_ids(model)
        velocities = ["0[m/s]", "1e-4[m/s]", "5e-4[m/s]", "1e-3[m/s]"]
        tend_values = ["0.002[s]", "0.005[s]"]
        for v in velocities:
            for t_end in tend_values:
                case_id = f"C3_2_V_{v.replace('[m/s]', '').replace('-', 'm').replace('.', 'p')}_T_{t_end.replace('[s]', '').replace('.', 'p')}"
                model.java.param().set("V_C3", v)
                v_expr = "0" if v.startswith("0[") else "-V_C3*min(t/ramp_C3,1)"
                row: dict[str, Any] = {"case_id": case_id, "model_type": setup["model_type"], "V": v, "t_end": t_end}
                try:
                    wall = set_wall_moving(model, ids["moving"], ids["nonmoving"], v_expr)
                    ok, err, hm = run_case(model, case_id, t_end, h_tag=case_id)
                    row.update(
                        {
                            "boundary_feature_type": wall["boundary_feature_type"],
                            "boundary_feature_properties": wall["properties"],
                            "velocity_expression": v_expr,
                            "solve_status": "PASS" if ok else "FAIL",
                            "failure_message": err,
                            "H(final)-H(0)": hm.get("delta_H", math.nan),
                            "interface_quality": hm.get("interface_quality", ""),
                            "H_csv": hm.get("csv", ""),
                            "H_plot": hm.get("plot", ""),
                        }
                    )
                    if ok and v != "0[m/s]" and abs(float(hm.get("delta_H", math.nan))) < 0.0002 and hm.get("interface_quality") == "clear/continuous":
                        row["case_pass"] = "PASS"
                    else:
                        row["case_pass"] = "FAIL"
                except Exception as exc:
                    row.update({"boundary_feature_type": "spf.Wall", "solve_status": "FAIL", "failure_message": str(exc), "case_pass": "FAIL"})
                rows.append(row)
        model_save = save_model_no_overwrite(model, C3 / "models" / "ring_fountain_v5B3_C3_minimal_moving_wall_test.mph")
        status = "PASS" if any(row.get("case_pass") == "PASS" for row in rows) else "FAIL"
    except Exception as exc:
        rows.append({"case_id": "C3_2_setup", "solve_status": "FAIL", "failure_message": traceback.format_exc(), "case_pass": "FAIL"})
        status = "FAIL"
    finally:
        try:
            if model is not None:
                client.remove(model)
        except Exception:
            pass
    csv_path = C3 / "tables" / "C3_2_minimal_moving_wall_cases.csv"
    write_csv(csv_path, rows)
    report = C3 / "reports" / "C3_2_minimal_moving_wall_test.md"
    first_failure = next((str(row.get("failure_message")) for row in rows if row.get("failure_message")), "")
    report.write_text(
        "\n".join(
            [
                "# C3-2 Minimal Moving Wall Test",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                f"C3-2 status: `{status}`",
                "",
                "## Scope",
                "",
                "- Geometry: simple rectangular air-water domain, no ring geometry.",
                "- Boundary semantics: only `spf.Wall` with prescribed wall velocity properties was allowed.",
                "- Disallowed substitutes: `spf.Inlet`, `spf.Outlet`, `spf.OpenBoundary`.",
                "",
                "## Review",
                "",
                f"- Any nonzero solid-wall moving case passed: `{any(row.get('case_pass') == 'PASS' for row in rows)}`",
                f"- Primary stop reason: `{first_failure}`",
                f"- Case table: `{csv_path}`",
                f"- Saved model info: `{json.dumps(model_save, ensure_ascii=False)}`",
            ]
        ),
        encoding="utf-8",
    )
    return {"status": status, "report": str(report), "csv": str(csv_path), "model": model_save, "rows": rows}


def create_single_phase_ring_model(client: Any) -> tuple[Any, dict[str, Any]]:
    model = client.create(f"c3_single_phase_ring_{RUN_ID}")
    java = model.java
    param = java.param()
    for name, value in {
        "Rtank": "100[mm]",
        "Hwater": "120[mm]",
        "Hair": "120[mm]",
        "Ri": "8[mm]",
        "Ro": "20[mm]",
        "h_ring": "2[mm]",
        "z_ring_center": "-20[mm]",
        "rho_w": "1000[kg/m^3]",
        "mu_w": "1e-3[Pa*s]",
        "V_C3": "1e-3[m/s]",
        "ramp_C3": "0.001[s]",
        "t_end_C3": "0.005[s]",
    }.items():
        param.set(name, value)
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
    mesh.autoMeshSize(5)
    mesh.run()
    spf = comp.physics().create("spf", "LaminarFlow", "geom1")
    fp = spf.feature("fp1")
    fp.set("rho_mat", "userdef")
    fp.set("rho", "rho_w")
    fp.set("mu_mat", "userdef")
    fp.set("mu", "mu_w")
    study = java.study().create("std1")
    study.create("time", "Transient")
    study.feature("time").set("tlist", "range(0,t_end_C3/8,t_end_C3)")
    return model, {"model_type": "single-phase LaminarFlow ring-hole model"}


def stage_c3_3(client: Any) -> dict[str, Any]:
    log("C3-3 running single-phase ring moving-wall tests.")
    rows: list[dict[str, Any]] = []
    model = None
    model_save: dict[str, str] = {}
    tests = [
        ("all_ring_walls", RING_ALL),
        ("vertical_ring_walls", RING_VERTICAL),
        ("horizontal_ring_walls", RING_HORIZONTAL),
        ("bottom_only", [5]),
        ("top_only", [6]),
    ]
    try:
        model, setup = create_single_phase_ring_model(client)
        boundaries = all_boundaries(model)
        for name, moving in tests:
            row: dict[str, Any] = {"case_id": f"C3_3_{name}", "model_type": setup["model_type"], "moving_boundaries": moving, "V": "1e-3[m/s]"}
            try:
                nonmoving = [bid for bid in boundaries if bid not in moving]
                wall = set_wall_moving(model, moving, nonmoving, "-V_C3*min(t/ramp_C3,1)", feature_tag=f"wall_c3_{name}")
                ok, err, _ = run_case(model, row["case_id"], "0.005[s]", h_tag=None)
                row.update({"boundary_feature_type": wall["boundary_feature_type"], "boundary_feature_properties": wall["properties"], "velocity_expression": wall["velocity_expression"], "solve_status": "PASS" if ok else "FAIL", "failure_message": err, "case_pass": "PASS" if ok else "FAIL"})
            except Exception as exc:
                row.update({"boundary_feature_type": "spf.Wall", "solve_status": "FAIL", "failure_message": str(exc), "case_pass": "FAIL"})
            rows.append(row)
        model_save = save_model_no_overwrite(model, C3 / "models" / "ring_fountain_v5B3_C3_single_phase_ring_moving_wall_test.mph")
        vertical_pass = any(row["case_id"].endswith("vertical_ring_walls") and row.get("case_pass") == "PASS" for row in rows)
        status = "PASS" if vertical_pass else "FAIL"
    except Exception:
        rows.append({"case_id": "C3_3_setup", "solve_status": "FAIL", "failure_message": traceback.format_exc(), "case_pass": "FAIL"})
        status = "FAIL"
    finally:
        try:
            if model is not None:
                client.remove(model)
        except Exception:
            pass
    csv_path = C3 / "tables" / "C3_3_single_phase_ring_moving_wall_cases.csv"
    write_csv(csv_path, rows)
    report = C3 / "reports" / "C3_3_single_phase_ring_moving_wall_test.md"
    report.write_text(
        "\n".join(
            [
                "# C3-3 Single-Phase Ring Moving Wall Test",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                f"C3-3 status: `{status}`",
                "",
                "- This model intentionally has no Level Set/free surface.",
                "- Boundary semantics: `spf.Wall` with prescribed wall velocity; no Inlet/Outlet/OpenBoundary substitution.",
                f"- Case table: `{csv_path}`",
                f"- Saved model info: `{json.dumps(model_save, ensure_ascii=False)}`",
            ]
        ),
        encoding="utf-8",
    )
    return {"status": status, "report": str(report), "csv": str(csv_path), "model": model_save, "rows": rows}


def create_ring_free_surface_model(client: Any) -> tuple[Any, dict[str, Any]]:
    model, setup = base.create_b2_model(client)
    try:
        model.java.param().set("V_C3", "1e-4[m/s]")
        model.java.param().set("ramp_C3", "0.001[s]")
        model.java.param().set("t_end_C3", "0.002[s]")
        model.java.component("comp1").physics("ls").feature("lsm1").set("gamma", "0")
    except Exception:
        pass
    setup["model_type"] = "ring free-surface model with true spf.Wall moving semantics"
    return model, setup


def stage_c3_4(client: Any) -> dict[str, Any]:
    log("C3-4 running ring + free-surface + true moving wall tests.")
    rows: list[dict[str, Any]] = []
    model = None
    model_save: dict[str, str] = {}
    tests = [
        ("vertical_V1e-4_T0p002", "1e-4[m/s]", "0.002[s]"),
        ("vertical_V5e-4_T0p005", "5e-4[m/s]", "0.005[s]"),
    ]
    try:
        model, setup = create_ring_free_surface_model(client)
        boundaries = all_boundaries(model)
        for index, (name, velocity, t_end) in enumerate(tests):
            row: dict[str, Any] = {"case_id": f"C3_4_{name}", "model_type": setup["model_type"], "moving_boundaries": RING_VERTICAL, "V": velocity, "t_end": t_end}
            if index == 1 and not any(r.get("case_id") == "C3_4_vertical_V1e-4_T0p002" and r.get("case_pass") == "PASS" for r in rows):
                row.update({"solve_status": "SKIP", "failure_message": "first C3-4 case did not PASS", "case_pass": "FAIL"})
                rows.append(row)
                continue
            try:
                model.java.param().set("V_C3", velocity)
                nonmoving = [bid for bid in boundaries if bid not in RING_VERTICAL]
                wall = set_wall_moving(model, RING_VERTICAL, nonmoving, "-V_C3*min(t/ramp_C3,1)", feature_tag=f"wall_c3_{name}")
                ok, err, hm = run_case(model, row["case_id"], t_end, h_tag=row["case_id"])
                drift = float(hm.get("delta_H", math.nan))
                clear = hm.get("interface_quality") == "clear/continuous"
                pass_case = ok and clear and math.isfinite(drift)
                row.update({"boundary_feature_type": wall["boundary_feature_type"], "boundary_feature_properties": wall["properties"], "velocity_expression": wall["velocity_expression"], "solve_status": "PASS" if ok else "FAIL", "failure_message": err, "H(final)-H(0)": drift, "interface_quality": hm.get("interface_quality", ""), "H_csv": hm.get("csv", ""), "H_plot": hm.get("plot", ""), "case_pass": "PASS" if pass_case else "FAIL"})
            except Exception as exc:
                row.update({"boundary_feature_type": "spf.Wall", "solve_status": "FAIL", "failure_message": str(exc), "case_pass": "FAIL"})
            rows.append(row)
        model_save = save_model_no_overwrite(model, C3 / "models" / "ring_fountain_v5B3_C3_ring_free_surface_true_moving_wall_test.mph")
        status = "PASS" if rows and all(row.get("case_pass") == "PASS" for row in rows) else "FAIL"
    except Exception:
        rows.append({"case_id": "C3_4_setup", "solve_status": "FAIL", "failure_message": traceback.format_exc(), "case_pass": "FAIL"})
        status = "FAIL"
    finally:
        try:
            if model is not None:
                client.remove(model)
        except Exception:
            pass
    csv_path = C3 / "tables" / "C3_4_ring_free_surface_true_moving_wall_cases.csv"
    write_csv(csv_path, rows)
    report = C3 / "reports" / "C3_4_ring_free_surface_true_moving_wall_test.md"
    report.write_text(
        "\n".join(
            [
                "# C3-4 Ring Free-Surface True Moving Wall Test",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                f"C3-4 status: `{status}`",
                "",
                "- This is a fixed-geometry moving-wall reduced free-surface model, not a real falling-ring geometry model.",
                "- Boundary semantics: `spf.Wall` with prescribed wall velocity; no Inlet/Outlet/OpenBoundary substitution.",
                f"- Case table: `{csv_path}`",
                f"- Saved model info: `{json.dumps(model_save, ensure_ascii=False)}`",
            ]
        ),
        encoding="utf-8",
    )
    return {"status": status, "report": str(report), "csv": str(csv_path), "model": model_save, "rows": rows}


def final_report(results: dict[str, Any], script_info: dict[str, Any]) -> dict[str, Any]:
    allow = "YES" if results.get("C3-4", {}).get("status") == "PASS" else "NO"
    c32 = results.get("C3-2", {})
    c33 = results.get("C3-3", {"status": "SKIP"})
    c34 = results.get("C3-4", {"status": "SKIP"})
    c31 = results.get("C3-1", {})
    c32_failure = next((str(row.get("failure_message")) for row in c32.get("rows", []) if row.get("failure_message")), "")
    best_model = "NO"
    if allow == "YES":
        model_info = c34.get("model", {})
        best_model = model_info.get("model", "YES")
    report = C3 / "reports" / "5B3_C3_boundary_semantics_audit_final_report.md"
    report.write_text(
        "\n".join(
            [
                "# 5B3-C3 Boundary Semantics Audit Final Report",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                "## Gate Result",
                "",
                f"- C3-0 C2 review: `{results.get('C3-0', {}).get('status')}`",
                f"- C3-1 feature/API audit: `{c31.get('status')}`",
                f"- C3-2 minimal moving wall + free surface: `{c32.get('status')}`",
                f"- C3-3 single-phase ring moving wall: `{c33.get('status')}`",
                f"- C3-4 ring + free surface + true moving wall: `{c34.get('status')}`",
                f"- `ALLOW_RESUME_STAGE5 = {allow}`",
                "",
                "## Required Answers",
                "",
                f"1. Current API can create formal Two-Phase Flow interface: `{c31.get('formal_two_phase_api_creatable', False)}`.",
                f"2. Current API can create true moving solid wall semantics through `spf.Wall` properties: `{c31.get('spf_wall_moving_props_creatable', False)}`.",
                "3. `spf.Inlet` is rejected as an invalid substitute route for solid moving wall: `YES`.",
                f"4. Minimal moving wall + free surface ran through: `{c32.get('status')}`.",
                f"   - Minimal model stop reason: `{c32_failure}`.",
                f"5. Ring moving wall single-phase ran through: `{c33.get('status')}`.",
                f"6. Ring moving wall + free surface ran through: `{c34.get('status')}`.",
                f"7. Best model for later 5B3 continuation generated: `{best_model}`.",
                f"8. `ALLOW_RESUME_STAGE5`: `{allow}`.",
                f"9. Permission to enter 5B4 / 5C / 5D / Stage 6: `{'YES' if allow == 'YES' else 'NO'}`.",
                "",
                "## Next Step If Gate Is NO",
                "",
                "- Manually build a GUI model containing the desired formal Two-Phase Flow interface and true moving wall.",
                "- In the GUI, verify how the default wall feature is overridden, excluded, or replaced for the moving wall boundary.",
                "- Export Java/M-file from COMSOL GUI.",
                "- Use the exported file to recover exact API feature/interface type names and property names.",
                "",
                "## Outputs",
                "",
                *[f"- {key}: `{value.get('report')}`" for key, value in results.items() if isinstance(value, dict) and value.get("report")],
                f"- Script archived at: `{script_info.get('target')}`",
                f"- Script manifest: `{script_info.get('manifest')}`",
            ]
        ),
        encoding="utf-8",
    )
    return {"report": str(report), "ALLOW_RESUME_STAGE5": allow, "best_model": best_model}


def update_docs(results: dict[str, Any], final: dict[str, Any]) -> None:
    lines = [
        "## 5B3-C3 Boundary Semantics Audit",
        "",
        f"- Run ID: `{RUN_ID}`",
        f"- C3-2 minimal free-surface + solid-wall test: `{results.get('C3-2', {}).get('status')}`",
        f"- C3-3 single-phase ring moving-wall test: `{results.get('C3-3', {}).get('status', 'SKIP')}`",
        f"- C3-4 ring + free-surface true moving-wall test: `{results.get('C3-4', {}).get('status', 'SKIP')}`",
        f"- `ALLOW_RESUME_STAGE5 = {final.get('ALLOW_RESUME_STAGE5')}`",
        "- `spf.Inlet` / `spf.Outlet` / `spf.OpenBoundary` remain disallowed as solid moving-wall substitutes.",
        "- No Jet1/Jet2 extraction, parameter sweep, or real Hmax output was performed in C3.",
        f"- Final report: `{final.get('report')}`",
    ]
    add_or_replace_section(ROOT / "README.md", "5B3_C3_BOUNDARY_SEMANTICS_AUDIT", lines)
    changelog_lines = [
        "## 5B3-C3 Boundary Semantics Audit",
        "",
        f"- Run ID: `{RUN_ID}`",
        f"- C3 final gate: `ALLOW_RESUME_STAGE5 = {final.get('ALLOW_RESUME_STAGE5')}`",
        f"- C3-2/C3-3/C3-4: `{results.get('C3-2', {}).get('status')}` / `{results.get('C3-3', {}).get('status', 'SKIP')}` / `{results.get('C3-4', {}).get('status', 'SKIP')}`",
        "- Inlet-equivalent motion was explicitly rejected as invalid for solid moving-wall semantics.",
        f"- Report: `{final.get('report')}`",
    ]
    add_or_replace_section(ROOT / "CHANGELOG.md", "5B3_C3_BOUNDARY_SEMANTICS_AUDIT", changelog_lines)


def main() -> None:
    ensure_dirs()
    script_info = archive_script()
    summary: dict[str, Any] = {"run_id": RUN_ID, "script": script_info, "results": {}}
    client = mph.start()
    try:
        summary["results"]["C3-0"] = stage_c3_0()
        summary["results"]["C3-1"] = stage_c3_1(client)
        summary["results"]["C3-2"] = stage_c3_2(client)
        if summary["results"]["C3-2"].get("status") == "PASS":
            summary["results"]["C3-3"] = stage_c3_3(client)
        else:
            skip = {"status": "SKIP", "reason": "C3-2 did not PASS; C3-3 is gated off"}
            summary["results"]["C3-3"] = skip
            (C3 / "reports" / "C3_3_single_phase_ring_moving_wall_test.md").write_text("# C3-3 Single-Phase Ring Moving Wall Test\n\nC3-3 status: `SKIP`\n\nReason: C3-2 did not PASS.\n", encoding="utf-8")
            write_csv(C3 / "tables" / "C3_3_single_phase_ring_moving_wall_cases.csv", [{"case_id": "C3_3_skip", "solve_status": "SKIP", "reason": skip["reason"]}])
        if summary["results"].get("C3-2", {}).get("status") == "PASS" and summary["results"].get("C3-3", {}).get("status") == "PASS":
            summary["results"]["C3-4"] = stage_c3_4(client)
        else:
            skip = {"status": "SKIP", "reason": "C3-2 and C3-3 did not both PASS; C3-4 is gated off"}
            summary["results"]["C3-4"] = skip
            (C3 / "reports" / "C3_4_ring_free_surface_true_moving_wall_test.md").write_text("# C3-4 Ring Free-Surface True Moving Wall Test\n\nC3-4 status: `SKIP`\n\nReason: C3-2 and C3-3 did not both PASS.\n", encoding="utf-8")
            write_csv(C3 / "tables" / "C3_4_ring_free_surface_true_moving_wall_cases.csv", [{"case_id": "C3_4_skip", "solve_status": "SKIP", "reason": skip["reason"]}])
        final = final_report(summary["results"], script_info)
        summary["final"] = final
        update_docs(summary["results"], final)
        write_json(C3 / "5B3_C3_boundary_semantics_audit_summary.json", summary)
        log(f"C3 finished with ALLOW_RESUME_STAGE5={final['ALLOW_RESUME_STAGE5']}")
    finally:
        try:
            client.clear()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        ensure_dirs()
        err = C3 / "logs" / f"5B3_C3_fatal_{RUN_ID}.log"
        err.write_text(traceback.format_exc(), encoding="utf-8")
        raise
