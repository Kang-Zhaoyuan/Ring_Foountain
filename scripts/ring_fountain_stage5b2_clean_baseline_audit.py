# -*- coding: utf-8 -*-
"""Stage A audit for 5B2 clean-baseline rebuild.

This script is intentionally read-only with respect to the source COMSOL model.
It opens the current 5B2 static ring/free-surface model, exports a broad
physics/feature audit, and stops before any rebuild, solve, or moving-wall work.
"""

from __future__ import annotations

import csv
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import mph


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
STAGE5 = ROOT / "05_two_phase_free_surface"
SRC_MODEL = (
    STAGE5
    / "5B2_static_ring_free_surface_smoke"
    / "models"
    / "ring_fountain_v5B2_3_static_ring_free_surface_boundary_confirmed.mph"
)
OUT = STAGE5 / "5B2_clean_baseline_rebuild"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = OUT / "logs" / f"5B2_clean_baseline_audit_{RUN_ID}.log"

RING_ALL = [4, 5, 6, 7]


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def ensure_dirs() -> None:
    for sub in ["reports", "tables", "logs"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def tags(node: Any) -> list[str]:
    try:
        return [str(x) for x in list(node.tags())]
    except Exception:
        return []


def try_call(obj: Any, method: str, *args: Any) -> Any:
    try:
        return getattr(obj, method)(*args)
    except Exception as exc:
        return f"<unreadable: {exc}>"


def safe_string(value: Any) -> str:
    try:
        if isinstance(value, (list, tuple)):
            return "[" + ", ".join(safe_string(v) for v in value) + "]"
        return str(value)
    except Exception as exc:
        return f"<unprintable: {exc}>"


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


def prop_names(feature: Any) -> list[str]:
    for method in ("properties", "propertyNames"):
        try:
            return [str(x) for x in list(getattr(feature, method)())]
        except Exception:
            pass
    return []


def prop_value(feature: Any, key: str) -> Any:
    for call in (
        lambda: feature.getString(key),
        lambda: list(feature.getStringArray(key)),
        lambda: feature.getDouble(key),
        lambda: list(feature.getDoubleArray(key)),
        lambda: feature.getInt(key),
        lambda: list(feature.getIntArray(key)),
        lambda: feature.get(key),
    ):
        try:
            val = call()
            if isinstance(val, list):
                return [safe_string(v) for v in val]
            return safe_string(val)
        except Exception:
            pass
    return "<unreadable>"


def active_state(feature: Any) -> str:
    for call in (
        lambda: feature.isActive(),
        lambda: feature.active(),
    ):
        try:
            return safe_string(call())
        except Exception:
            pass
    return "unknown"


def key_props(feature: Any) -> dict[str, Any]:
    interesting = [
        "BoundaryCondition",
        "SlidingWall",
        "TranslationalVelocityOption",
        "utr",
        "u0",
        "U0",
        "p0",
        "rho",
        "mu",
        "rho_mat",
        "mu_mat",
        "epsilon_ls",
        "eps_ls",
        "gamma",
        "sigma",
        "g",
        "gravity",
        "Gravitation",
        "FrameMotion",
        "Omega",
        "phase",
        "initmethod",
        "phi0",
        "ls0",
    ]
    available = set(prop_names(feature))
    result: dict[str, Any] = {}
    for name in interesting:
        if name in available:
            result[name] = prop_value(feature, name)
    for name in sorted(available):
        low = name.lower()
        if any(token in low for token in ("wall", "grav", "rot", "rho", "mu", "sigma", "epsilon", "phase", "level")):
            result.setdefault(name, prop_value(feature, name))
    return result


def audit_physics(model: Any) -> list[dict[str, Any]]:
    comp = model.java.component("comp1")
    rows: list[dict[str, Any]] = []
    for ptag in tags(comp.physics()):
        phys = comp.physics(ptag)
        for ftag in tags(phys.feature()):
            feat = phys.feature(ftag)
            selection = feature_selection(feat)
            rows.append(
                {
                    "physics_tag": ptag,
                    "physics_type": safe_string(try_call(phys, "getType")),
                    "physics_label": safe_string(try_call(phys, "label")),
                    "feature_tag": ftag,
                    "feature_type": safe_string(try_call(feat, "getType")),
                    "feature_label": safe_string(try_call(feat, "label")),
                    "selection_boundaries": selection,
                    "intersects_ring": sorted(set(selection).intersection(RING_ALL)) if isinstance(selection, list) else [],
                    "active_or_solved": active_state(feat),
                    "key_properties": key_props(feat),
                    "property_names": prop_names(feat),
                }
            )
    return rows


def audit_multiphysics(model: Any) -> list[dict[str, Any]]:
    comp = model.java.component("comp1")
    rows: list[dict[str, Any]] = []
    try:
        mtags = tags(comp.multiphysics())
    except Exception:
        mtags = []
    for mtag in mtags:
        try:
            feat = comp.multiphysics(mtag)
        except Exception as exc:
            rows.append({"tag": mtag, "error": safe_string(exc)})
            continue
        rows.append(
            {
                "tag": mtag,
                "type": safe_string(try_call(feat, "getType")),
                "label": safe_string(try_call(feat, "label")),
                "active_or_solved": active_state(feat),
                "selection": feature_selection(feat),
                "key_properties": key_props(feat),
                "property_names": prop_names(feat),
            }
        )
    return rows


def audit_variables(model: Any) -> list[dict[str, Any]]:
    comp = model.java.component("comp1")
    rows: list[dict[str, Any]] = []
    try:
        vtags = tags(comp.variable())
    except Exception:
        vtags = []
    for vtag in vtags:
        try:
            var = comp.variable(vtag)
        except Exception as exc:
            rows.append({"variable_tag": vtag, "error": safe_string(exc)})
            continue
        rows.append(
            {
                "variable_tag": vtag,
                "label": safe_string(try_call(var, "label")),
                "property_names": prop_names(var),
                "key_properties": key_props(var),
            }
        )
    return rows


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
            flat = {key: json.dumps(value, ensure_ascii=False, default=str) if isinstance(value, (dict, list)) else value for key, value in row.items()}
            writer.writerow(flat)


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        vals = []
        for col in columns:
            val = row.get(col, "")
            text = json.dumps(val, ensure_ascii=False, default=str) if isinstance(val, (dict, list)) else safe_string(val)
            vals.append("`" + text.replace("|", "\\|") + "`")
        lines.append("| " + " | ".join(vals) + " |")
    return lines


def summarize(rows: list[dict[str, Any]], multiphysics_rows: list[dict[str, Any]], variable_rows: list[dict[str, Any]]) -> dict[str, Any]:
    feature_types = {str(row.get("feature_type")) for row in rows}
    physics_types = {str(row.get("physics_type")) for row in rows}
    rotating = [row for row in rows if "rotatingframefd" in str(row.get("feature_type", "")).lower() or str(row.get("feature_tag", "")).lower().startswith("rtfr")]
    gravity = [row for row in rows if "grav" in str(row.get("feature_type", "")).lower() or "grav" in str(row.get("feature_tag", "")).lower()]
    walls = [row for row in rows if "wall" in str(row.get("feature_type", "")).lower() or "wall" in str(row.get("feature_tag", "")).lower()]
    level_set = [row for row in rows if "level" in str(row.get("physics_type", "")).lower() or str(row.get("physics_tag", "")).lower() in {"ls", "tpf"}]
    two_phase_mp = [
        row
        for row in multiphysics_rows
        if any(token in (str(row.get("type", "")) + " " + str(row.get("label", ""))).lower() for token in ("two", "phase", "level", "fluid"))
    ]
    variable_text = json.dumps(variable_rows, ensure_ascii=False, default=str).lower()
    return {
        "rotating_frame_present": bool(rotating),
        "rotating_frame_tags": [row.get("feature_tag") for row in rotating],
        "gravity_present": bool(gravity),
        "gravity_tags": [row.get("feature_tag") for row in gravity],
        "wall_features": [row.get("feature_tag") for row in walls],
        "wall_ring_overlap": [
            {"feature_tag": row.get("feature_tag"), "intersects_ring": row.get("intersects_ring"), "selection_boundaries": row.get("selection_boundaries")}
            for row in walls
            if row.get("intersects_ring")
        ],
        "physics_types": sorted(physics_types),
        "feature_types": sorted(feature_types),
        "level_set_like_features": [row.get("feature_tag") for row in level_set],
        "multiphysics_tags": [row.get("tag") for row in multiphysics_rows],
        "two_phase_coupling_detected": bool(two_phase_mp),
        "rho_mu_definitions_detected_in_variables": ("rho" in variable_text or "mu" in variable_text),
        "surface_tension_like_definition_detected": ("sigma" in variable_text or "surface" in variable_text or any("sigma" in json.dumps(row, ensure_ascii=False, default=str).lower() for row in rows)),
    }


def write_report(physics_rows: list[dict[str, Any]], multiphysics_rows: list[dict[str, Any]], variable_rows: list[dict[str, Any]], summary: dict[str, Any]) -> Path:
    report = OUT / "reports" / "A_physics_audit.md"
    lines = [
        "# Stage A Physics Audit",
        "",
        f"Run time: `{datetime.now().isoformat(timespec='seconds')}`",
        f"Source model: `{SRC_MODEL}`",
        "",
        "This audit is read-only. It did not solve, save, or modify the source model.",
        "",
        "## Required Findings",
        "",
        f"- `RotatingFrameFD / rtfr1` present: `{summary['rotating_frame_present']}`; tags: `{summary['rotating_frame_tags']}`.",
        "- Default judgement: unless a later report documents a specific physical reason, RotatingFrameFD should be deleted or disabled before the clean static baseline because this stage is a static free-surface baseline, not a rotating-frame problem.",
        f"- Gravity present: `{summary['gravity_present']}`; tags: `{summary['gravity_tags']}`.",
        f"- Wall features: `{summary['wall_features']}`.",
        f"- Wall features intersecting confirmed ring boundaries `[4,5,6,7]`: `{summary['wall_ring_overlap']}`.",
        f"- Level Set-like physics/features detected: `{summary['level_set_like_features']}`.",
        f"- Multiphysics tags detected: `{summary['multiphysics_tags']}`.",
        f"- Formal Two-Phase Flow coupling detected by multiphysics inventory: `{summary['two_phase_coupling_detected']}`.",
        f"- rho/mu definitions detected in variable inventory: `{summary['rho_mu_definitions_detected_in_variables']}`.",
        f"- surface-tension-like definition detected: `{summary['surface_tension_like_definition_detected']}`.",
        "",
        "## Interpretation For Stage B",
        "",
    ]
    if summary["rotating_frame_present"]:
        lines.append("- `RotatingFrameFD` exists in the current input model. With no explicit rotating-frame physics requirement in this static baseline task, it is treated as an unintended feature to remove or disable in Stage B.")
    else:
        lines.append("- `RotatingFrameFD` was not found.")
    if summary["two_phase_coupling_detected"]:
        lines.append("- The model appears to contain a formal multiphysics coupling related to two-phase/level-set flow; Stage B should verify it can be reused cleanly.")
    else:
        lines.append("- No formal two-phase multiphysics coupling was detected by the Java multiphysics inventory. Current evidence points to a manual Laminar Flow + Level Set setup or a coupling represented outside the multiphysics node.")
    if summary["wall_ring_overlap"]:
        lines.append("- `spf` wall selection currently overlaps the confirmed ring boundaries. Any later moving-wall retry must first create non-overlapping wall selections.")
    lines.extend([
        "",
        "## Complete Physics Feature Audit",
        "",
    ])
    lines.extend(md_table(physics_rows, ["physics_tag", "physics_type", "physics_label", "feature_tag", "feature_type", "feature_label", "selection_boundaries", "intersects_ring", "active_or_solved", "key_properties"]))
    lines.extend([
        "",
        "## Multiphysics Inventory",
        "",
    ])
    if multiphysics_rows:
        lines.extend(md_table(multiphysics_rows, ["tag", "type", "label", "active_or_solved", "selection", "key_properties"]))
    else:
        lines.append("- No multiphysics nodes were readable under `comp1.multiphysics()`.")
    lines.extend([
        "",
        "## Variable Inventory",
        "",
    ])
    if variable_rows:
        lines.extend(md_table(variable_rows, ["variable_tag", "label", "key_properties", "property_names"]))
    else:
        lines.append("- No component variable nodes were readable under `comp1.variable()`.")
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def main() -> None:
    os.environ["JAVA_HOME"] = r"D:\COMSOL64\Multiphysics\java\win64\jre"
    ensure_dirs()
    script_dst = SCRIPTS / "ring_fountain_stage5b2_clean_baseline_audit.py"
    shutil.copy2(Path(__file__), script_dst)
    if not SRC_MODEL.exists():
        raise FileNotFoundError(SRC_MODEL)

    log("Starting Stage A physics audit.")
    client = mph.Client(cores=2, version="6.4")
    model = None
    try:
        model = client.load(SRC_MODEL)
        physics_rows = audit_physics(model)
        multiphysics_rows = audit_multiphysics(model)
        variable_rows = audit_variables(model)
        summary = summarize(physics_rows, multiphysics_rows, variable_rows)
        payload = {
            "run_id": RUN_ID,
            "source_model": str(SRC_MODEL),
            "summary": summary,
            "physics_features": physics_rows,
            "multiphysics": multiphysics_rows,
            "variables": variable_rows,
        }
        write_csv(OUT / "tables" / "A_physics_feature_audit.csv", physics_rows)
        write_csv(OUT / "tables" / "A_multiphysics_audit.csv", multiphysics_rows)
        write_csv(OUT / "tables" / "A_variable_audit.csv", variable_rows)
        (OUT / "logs" / f"A_physics_audit_{RUN_ID}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        report = write_report(physics_rows, multiphysics_rows, variable_rows, summary)
        (OUT / "5B2_clean_baseline_audit_summary.json").write_text(
            json.dumps({"run_id": RUN_ID, "report": str(report), "script": str(script_dst), **summary}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        log(f"Stage A audit complete: {report}")
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
