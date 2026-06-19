# -*- coding: utf-8 -*-
"""Automate IYPT 2026 Ring Fountain COMSOL stages 0-2.

Conservative workflow:
- verify the configured MCP server can start;
- open and audit the trusted V0 model without saving over it;
- save checked/sweep copies;
- add parameter descriptions only on copied models;
- attempt existing plot/export/table generation and small one-dimensional
  parameter sweeps;
- record failures instead of guessing boundary IDs or changing physics.
"""

from __future__ import annotations

import asyncio
import csv
import json
import os
import shutil
import subprocess
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
V0 = ROOT / "ring_fountain_v0_single_phase" / "ring_fountain_v0_single_phase.mph"
MCP_ROOT = Path(r"C:\tmp\comsol-mcp-link")
MCP_PYTHON = MCP_ROOT / ".venv" / "Scripts" / "python.exe"

STAGE0 = ROOT / "00_audit_v0"
STAGE1 = ROOT / "01_v0_checked"
STAGE2 = ROOT / "02_param_sweep"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = STAGE0 / "logs" / f"automation_{RUN_ID}.log"

PARAM_DESCRIPTIONS = {
    "Ro": "Outer radius of the ring.",
    "Ri": "Inner radius of the ring opening; Ri/Ro controls the hole ratio.",
    "Rtank": "Radius of the computational water domain.",
    "Zup": "Water-domain height above the ring region.",
    "Zdown": "Water-domain height below the ring region.",
    "U0": "Relative incoming flow speed, or equivalent ring motion speed in the fixed-ring frame.",
    "rho_w": "Water density.",
    "mu_w": "Dynamic viscosity of water.",
    "h_ring": "Ring cross-section thickness in the simplified single-phase model.",
}

METRIC_EXPRESSIONS = [
    ("u_max_maxop", "maxop1(spf.U)", "m/s"),
    ("u_max_max", "max(spf.U)", "m/s"),
    ("p_max_p", "maxop1(p)", "Pa"),
    ("p_max_spf_p", "maxop1(spf.p)", "Pa"),
    ("vz_max_v", "maxop1(v)", "m/s"),
    ("vz_max_w", "maxop1(w)", "m/s"),
]

FIELD_MAX_FALLBACKS = [
    ("u_max_field", "spf.U", "m/s"),
    ("p_max_field", "p", "Pa"),
    ("p_max_spf_field", "spf.p", "Pa"),
    ("vz_max_v_field", "v", "m/s"),
    ("vz_max_w_field", "w", "m/s"),
]


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def safe(label: str, fn, *args, **kwargs) -> dict[str, Any]:
    try:
        value = fn(*args, **kwargs)
        log(f"OK: {label}")
        return {"ok": True, "value": value}
    except Exception as exc:
        tb = traceback.format_exc()
        log(f"FAIL: {label}: {exc}")
        with LOG.open("a", encoding="utf-8") as handle:
            handle.write(tb + "\n")
        return {"ok": False, "error": str(exc)}


def make_dirs() -> None:
    for base in [STAGE0, STAGE1, STAGE2]:
        for sub in ["reports", "images", "logs"]:
            (base / sub).mkdir(parents=True, exist_ok=True)
    for base in [STAGE1, STAGE2]:
        for sub in ["models", "tables"]:
            (base / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


async def mcp_smoke_async() -> dict[str, Any]:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=str(MCP_PYTHON),
        args=["-m", "src.server"],
        cwd=str(MCP_ROOT),
        env={
            "JAVA_HOME": r"D:\COMSOL64\Multiphysics\java\win64\jre",
            "HF_ENDPOINT": "https://hf-mirror.com",
        },
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            resources = (await session.list_resources()).resources
            return {
                "ok": True,
                "tools": len(tools),
                "resources": len(resources),
                "sample_tools": [tool.name for tool in tools[:12]],
            }


def mcp_smoke() -> dict[str, Any]:
    return asyncio.run(mcp_smoke_async())


def safe_text(fn) -> str:
    try:
        return str(fn())
    except Exception as exc:
        return f"unavailable: {exc}"


def props_of(node) -> dict[str, str]:
    try:
        props = node.properties()
        result = {}
        for key, value in props.items():
            text = repr(value)
            result[key] = text[:500] + ("..." if len(text) > 500 else "")
        return result
    except Exception as exc:
        return {"_error": str(exc)}


def selection_of(node) -> Any:
    try:
        selection = node.selection()
        if selection is None:
            return None
        if hasattr(selection, "tolist"):
            return selection.tolist()
        return str(selection)
    except Exception as exc:
        return f"unavailable: {exc}"


def node_summary(node, children: bool = False) -> dict[str, Any]:
    summary = {
        "path": str(node),
        "name": safe_text(node.name),
        "tag": safe_text(node.tag),
        "type": safe_text(node.type),
        "selection": selection_of(node),
        "properties": props_of(node),
    }
    if children:
        try:
            summary["children"] = [node_summary(child, False) for child in node.children()]
        except Exception as exc:
            summary["children_error"] = str(exc)
    return summary


def list_or_error(label: str, fn) -> Any:
    result = safe(label, fn)
    return result["value"] if result["ok"] else {"error": result["error"]}


def audit_model(model) -> dict[str, Any]:
    audit: dict[str, Any] = {
        "name": safe_text(model.name),
        "file": safe_text(model.file),
        "version": safe_text(model.version),
        "modules": list_or_error("used products", model.modules),
        "parameters": list_or_error("parameters", model.parameters),
        "parameter_descriptions": list_or_error("parameter descriptions", model.descriptions),
    }
    for key, fn in [
        ("functions", model.functions),
        ("components", model.components),
        ("geometries", model.geometries),
        ("selections", model.selections),
        ("materials", model.materials),
        ("physics", model.physics),
        ("multiphysics", model.multiphysics),
        ("meshes", model.meshes),
        ("studies", model.studies),
        ("solutions", model.solutions),
        ("datasets", model.datasets),
        ("plots", model.plots),
        ("exports", model.exports),
    ]:
        audit[key] = list_or_error(key, fn)

    for key in [
        "components",
        "geometries",
        "selections",
        "materials",
        "physics",
        "meshes",
        "studies",
        "solutions",
        "datasets",
        "plots",
        "exports",
    ]:
        detail = []
        values = audit.get(key, [])
        if isinstance(values, list):
            for name in values:
                detail.append(node_summary(model / key / name, children=True))
        audit[f"{key}_detail"] = detail

    problems = safe("model problems", model.problems)
    if problems["ok"]:
        audit["problems"] = [
            {
                "message": str(item.get("message")),
                "category": str(item.get("category")),
                "node": str(item.get("node")),
                "selection": str(item.get("selection")),
            }
            for item in problems["value"]
        ]
    else:
        audit["problems"] = {"error": problems["error"]}

    physics_text = json.dumps(audit.get("physics_detail", []), ensure_ascii=False).lower()
    component_text = json.dumps(audit.get("components_detail", []), ensure_ascii=False).lower()
    geometry_text = json.dumps(audit.get("geometries_detail", []), ensure_ascii=False).lower()
    params = audit.get("parameters", {})
    audit["judgement"] = {
        "appears_2d_axisymmetric": any(token in component_text for token in ["axis", "axi", "axisymmetric"]),
        "appears_single_phase_laminar_flow": (
            any(token in physics_text for token in ["laminar", "spf", "single-phase"])
            and not any(token in physics_text for token in ["two-phase", "level set", "phase field", "free surface"])
        ),
        "ring_represented_in_rz_cross_section": (
            "ring" in geometry_text or (isinstance(params, dict) and any(name in params for name in ["Ro", "Ri", "h_ring"]))
        ),
        "free_surface_or_moving_mesh_detected": any(
            token in physics_text for token in ["two-phase", "level set", "phase field", "moving mesh", "ale", "free surface"]
        ),
        "automation_note": "Boundary IDs were audited only; no boundary-condition changes were made.",
    }
    return audit


def sanitize(name: str) -> str:
    clean = "".join(char if char.isalnum() or char in "-_" else "_" for char in str(name))
    return clean[:80] or "node"


def write_audit_reports(audit: dict[str, Any], mcp: dict[str, Any]) -> None:
    json_path = STAGE0 / "reports" / "v0_model_audit.json"
    md_path = STAGE0 / "reports" / "v0_model_audit.md"
    txt_path = STAGE0 / "reports" / "v0_model_audit.txt"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    lines = [
        "# V0 Model Audit",
        "",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## MCP Status",
        "",
        f"- MCP smoke test: {'OK' if mcp.get('ok') else 'FAILED'}",
        f"- Tools: {mcp.get('tools')}",
        f"- Resources: {mcp.get('resources')}",
        "",
        "## Model Identity",
        "",
        f"- Name: `{audit.get('name')}`",
        f"- File: `{audit.get('file')}`",
        f"- COMSOL version: `{audit.get('version')}`",
        f"- Used products/modules: `{audit.get('modules')}`",
        "",
        "## Key Judgement",
        "",
    ]
    for key, value in audit.get("judgement", {}).items():
        lines.append(f"- {key}: {value}")
    lines += ["", "## Parameters", ""]
    params = audit.get("parameters", {})
    descriptions = audit.get("parameter_descriptions", {})
    if isinstance(params, dict):
        for key, value in params.items():
            desc = descriptions.get(key, "") if isinstance(descriptions, dict) else ""
            lines.append(f"- `{key}` = `{value}`; {desc}")
    lines += ["", "## Model Tree Summary", ""]
    for key in ["components", "geometries", "materials", "physics", "meshes", "studies", "solutions", "datasets", "plots", "exports", "selections"]:
        lines.append(f"- {key}: `{audit.get(key)}`")
    lines += [
        "",
        "## Boundary And Selection Notes",
        "",
        "Selections and boundary-condition entities are recorded in the JSON audit. Stage 0 did not modify the original V0 file.",
        "",
        "## Problems",
        "",
        "```json",
        json.dumps(audit.get("problems"), ensure_ascii=False, indent=2, default=str),
        "```",
        "",
        "## Raw Structured Audit",
        "",
        f"- `{json_path}`",
    ]
    text = "\n".join(lines) + "\n"
    md_path.write_text(text, encoding="utf-8")
    txt_path.write_text(text, encoding="utf-8")


def export_existing(model, image_dir: Path, table_dir: Path | None, prefix: str) -> list[dict[str, Any]]:
    results = []
    plots = list_or_error("plots for export", model.plots)
    if isinstance(plots, list):
        for plot in plots:
            output = image_dir / f"{prefix}_{sanitize(plot)}.png"
            result = safe(f"export plot {plot}", model.export, plot, output)
            if not result["ok"]:
                result = create_and_run_image_export(model, plot, output)
            results.append({"kind": "plot", "node": plot, "file": str(output), **result})
    exports = list_or_error("export nodes", model.exports)
    if table_dir and isinstance(exports, list):
        for export in exports:
            output = table_dir / f"{prefix}_{sanitize(export)}.txt"
            result = safe(f"run export {export}", model.export, export, output)
            results.append({"kind": "export", "node": export, "file": str(output), **result})
    return results


def create_and_run_image_export(model, plot_name: str, output: Path) -> dict[str, Any]:
    try:
        plot_node = model / "plots" / plot_name
        plot_tag = plot_node.tag()
        plot_type = plot_node.type() or ""
        export_type_order = ["Image3D", "Image2D"] if "3D" in plot_type or "3D" in plot_name else ["Image2D", "Image3D"]
        last_error = None
        for export_type in export_type_order:
            tag = None
            try:
                exports = model.java.result().export()
                tag = exports.uniquetag(f"img_{sanitize(plot_name)[:24]}")
                exports.create(tag, export_type)
                export = exports.get(tag)
                export.set("plotgroup", plot_tag)
                for key in ["pngfilename", "filename"]:
                    try:
                        export.set(key, str(output))
                    except Exception:
                        pass
                export.run()
                log(f"OK: created {export_type} export for plot {plot_name}")
                return {"ok": True, "value": f"created {export_type} export", "created_export": tag}
            except Exception as exc:
                last_error = exc
                try:
                    if tag:
                        model.java.result().export().remove(tag)
                except Exception:
                    pass
        return {"ok": False, "error": f"image export node creation failed: {last_error}"}
    except Exception as exc:
        return {"ok": False, "error": f"image export setup failed: {exc}"}


def set_parameter_descriptions(model) -> list[dict[str, str]]:
    changes = []
    params = model.parameters()
    for name, description in PARAM_DESCRIPTIONS.items():
        if name not in params:
            changes.append({"parameter": name, "status": "missing", "description": description})
            continue
        try:
            model.description(name, description)
            changes.append({"parameter": name, "status": "updated", "description": description})
        except Exception as exc:
            changes.append({"parameter": name, "status": f"failed: {exc}", "description": description})
    return changes


def evaluate_metrics(model) -> list[dict[str, Any]]:
    rows = []
    for metric, expression, unit in METRIC_EXPRESSIONS:
        try:
            value = model.evaluate(expression, unit=unit)
            if hasattr(value, "tolist"):
                value = value.tolist()
            rows.append({"metric": metric, "expression": expression, "unit": unit, "status": "ok", "value": value})
        except Exception as exc:
            rows.append({"metric": metric, "expression": expression, "unit": unit, "status": "failed", "error": str(exc)})
    for metric, expression, unit in FIELD_MAX_FALLBACKS:
        try:
            import numpy as np

            value = model.evaluate(expression, unit=unit)
            arr = np.asarray(value, dtype=float)
            finite = arr[np.isfinite(arr)]
            if finite.size == 0:
                raise ValueError("no finite values returned")
            rows.append({
                "metric": metric,
                "expression": expression,
                "unit": unit,
                "status": "ok",
                "value": float(np.nanmax(finite)),
                "method": "Python max over evaluated field samples",
            })
        except Exception as exc:
            rows.append({"metric": metric, "expression": expression, "unit": unit, "status": "failed", "error": str(exc), "method": "Python field max fallback"})
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    keys = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                key: json.dumps(row.get(key), ensure_ascii=False) if isinstance(row.get(key), (list, dict)) else row.get(key)
                for key in keys
            })


def write_report(path: Path, title: str, body: list[str], data: Any) -> None:
    lines = [f"# {title}", "", f"Run time: {datetime.now().isoformat(timespec='seconds')}", ""]
    lines.extend(body)
    lines += ["", "## Structured Data", "", "```json", json.dumps(data, ensure_ascii=False, indent=2, default=str), "```"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_readme_changelog(status: dict[str, Any]) -> None:
    readme = ROOT / "README.md"
    changelog = ROOT / "CHANGELOG.md"
    readme.write_text(
        f"""# COMSOL Ring Fountain Simulation

Project goal: build staged COMSOL numerical models for the IYPT 2026 Ring Fountain problem.

## Current Model Versions

- Original V0: `{V0}`. Trusted GUI-created baseline; not overwritten.
- Stage 1 checked model: `{STAGE1 / 'models' / 'ring_fountain_v0_checked.mph'}`.
- Stage 2 parameter-sweep model: `{STAGE2 / 'models' / 'ring_fountain_v1_param_sweep.mph'}`.

## Folder Structure

- `ring_fountain_v0_single_phase/`: original single-phase V0 model.
- `00_audit_v0/`: Stage 0 audit reports, logs, and exported existing figures.
- `01_v0_checked/`: copied checked baseline model, reports, images, tables, logs.
- `02_param_sweep/`: small-scale parameter sweep attempts and outputs.
- `scripts/`: automation scripts used to generate outputs.

## Physical Assumptions Of Current V0

The current model is treated as a single-phase water-flow model around a fixed ring in a 2D axisymmetric r-z representation unless the audit reports otherwise. It is not a Moving Mesh/ALE, two-phase-flow, free-surface, or falling-ring model.

## Stage Status

- Stage 0 audit: {status.get('stage0')}.
- Stage 1 checked copy: {status.get('stage1')}.
- Stage 2 parameter sweep: {status.get('stage2')}.

## How To Open Models

Open the `.mph` files above in COMSOL Multiphysics 6.4. The automation used COMSOL's bundled JRE at `D:\\COMSOL64\\Multiphysics\\java\\win64\\jre` and the local MCP server `comsol`.

## How To Rerun Study

Use the Study nodes listed in `00_audit_v0/reports/v0_model_audit.md`, or run `{SCRIPTS / 'ring_fountain_stage0_2.py'}` with the MCP Python environment.

## How To Re-export Figures And Tables

The automation attempts to run existing plot/export nodes through `mph.Model.export`. Export status is recorded in stage reports and logs. If a node fails, open the copied model in COMSOL GUI and confirm that its dataset has a computed solution.

## Known Limitations

- Current model is single-phase flow.
- Current model has no true free surface unless explicitly reported by the audit.
- Current model has no real falling/moving ring.
- Current outputs cannot directly provide a true fountain height `H_max`.
- Boundary IDs were not guessed or changed by automation.

## Next Steps

- Build a controlled moving-ring approximation.
- Add Moving Mesh/ALE only after validating boundary selections.
- Later add a two-phase free-surface model.
- Define a robust extraction method for maximum fountain height `H_max` only after free-surface modeling exists.
""",
        encoding="utf-8",
    )
    old = changelog.read_text(encoding="utf-8") if changelog.exists() else "# Changelog\n"
    entry = f"""
## {datetime.now().isoformat(timespec='seconds')} - Stages 0-2 Automation

- Stage name: V0 audit, V0 checked copy, conservative parameter-sweep preparation.
- Added files: reports/images/tables/logs under `00_audit_v0`, `01_v0_checked`, `02_param_sweep`; script in `scripts`.
- Modified files: `README.md`, `CHANGELOG.md`, copied `.mph` files only.
- Successful solve: {status.get('solve')}.
- Main issues: {status.get('issues')}.
- Next suggestion: validate boundary selections in COMSOL GUI before extending to moving mesh/free-surface physics.
"""
    changelog.write_text(old.rstrip() + "\n" + entry, encoding="utf-8")


def main() -> None:
    os.environ["JAVA_HOME"] = r"D:\COMSOL64\Multiphysics\java\win64\jre"
    make_dirs()
    shutil.copy2(Path(__file__), SCRIPTS / "ring_fountain_stage0_2.py")
    log("Starting Ring Fountain stages 0-2 automation")
    if not V0.exists():
        raise FileNotFoundError(V0)

    mcp_result = safe("MCP smoke test", mcp_smoke)
    mcp_data = mcp_result["value"] if mcp_result["ok"] else {"ok": False, "error": mcp_result["error"]}

    import mph

    client = mph.Client(cores=2, version="6.4")
    log(f"COMSOL client started: version={client.version}, cores={client.cores}, standalone={client.standalone}")
    model = client.load(str(V0))
    log(f"Loaded original V0 model: {model.name()} / {model.version()}")

    audit = audit_model(model)
    audit["mcp"] = mcp_data
    write_audit_reports(audit, mcp_data)
    stage0_exports = export_existing(model, STAGE0 / "images", None, "v0")
    (STAGE0 / "reports" / "v0_export_status.json").write_text(
        json.dumps(stage0_exports, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    stage1_path = STAGE1 / "models" / "ring_fountain_v0_checked.mph"
    stage1_ts = STAGE1 / "models" / f"ring_fountain_v0_checked_{RUN_ID}.mph"
    model.save(stage1_path)
    model.save(stage1_ts)
    log(f"Saved Stage 1 copies: {stage1_path}; {stage1_ts}")
    client.remove(model)
    checked = client.load(str(stage1_path))
    description_changes = set_parameter_descriptions(checked)
    metric_rows = evaluate_metrics(checked)
    write_csv(STAGE1 / "tables" / "derived_values_attempt.csv", metric_rows)
    stage1_exports = export_existing(checked, STAGE1 / "images", STAGE1 / "tables", "v0_checked")
    checked.save(stage1_path)
    checked.save(stage1_ts)
    write_report(
        STAGE1 / "reports" / "v0_checked_report.md",
        "V0 Checked Report",
        [
            f"Saved checked model: `{stage1_path}`.",
            f"Saved timestamped model: `{stage1_ts}`.",
            "Parameter descriptions were updated where matching parameter names existed.",
            "Derived-value metrics were attempted conservatively; failed expressions are recorded in the CSV.",
            "No boundary condition or core physics assumption was changed.",
        ],
        {"parameter_description_changes": description_changes, "metrics": metric_rows, "exports": stage1_exports},
    )

    stage2_path = STAGE2 / "models" / "ring_fountain_v1_param_sweep.mph"
    stage2_ts = STAGE2 / "models" / f"ring_fountain_v1_param_sweep_{RUN_ID}.mph"
    checked.save(stage2_path)
    checked.save(stage2_ts)
    client.remove(checked)
    sweep = client.load(str(stage2_path))
    base_params = sweep.parameters()
    sweep_plan = []
    if "U0" in base_params:
        sweep_plan.extend(("U0", value, "U0_sweep") for value in ["0.01[m/s]", "0.02[m/s]", "0.05[m/s]", "0.10[m/s]"])
    if "h_ring" in base_params:
        sweep_plan.extend(("h_ring", value, "h_ring_sweep") for value in ["1[mm]", "2[mm]", "4[mm]"])
    if "Ri" in base_params and "Ro" in base_params:
        sweep_plan.extend(("Ri", f"{ratio}*Ro", "Ri_Ro_sweep") for ratio in ["0.3", "0.4", "0.5", "0.6"])

    sweep_rows = []
    solve_ok_count = 0
    for parameter, value, group in sweep_plan:
        row = {"group": group, "parameter": parameter, "value": value}
        try:
            sweep.parameter(parameter, value)
            log(f"Sweep set {parameter}={value}")
            try:
                sweep.solve()
                row["solve_status"] = "ok"
                solve_ok_count += 1
            except Exception as exc:
                row["solve_status"] = "failed"
                row["solve_error"] = str(exc)
            for metric in evaluate_metrics(sweep):
                row[metric["metric"]] = metric.get("value") if metric["status"] == "ok" else f"failed: {metric.get('error')}"
            params_now = sweep.parameters()
            row["U0"] = params_now.get("U0")
            row["Ro"] = params_now.get("Ro")
            row["Ri"] = params_now.get("Ri")
            row["Ri/Ro"] = "see Ri and Ro expressions"
            row["h_ring"] = params_now.get("h_ring")
        except Exception as exc:
            row["status"] = "failed_before_solve"
            row["error"] = str(exc)
        sweep_rows.append(row)

    write_csv(STAGE2 / "tables" / "param_sweep_results.csv", sweep_rows)
    try:
        import openpyxl
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "param_sweep_results"
        keys = []
        for row in sweep_rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        sheet.append(keys)
        for row in sweep_rows:
            sheet.append([
                json.dumps(row.get(key), ensure_ascii=False) if isinstance(row.get(key), (list, dict)) else row.get(key)
                for key in keys
            ])
        workbook.save(STAGE2 / "tables" / "param_sweep_results.xlsx")
    except Exception as exc:
        log(f"XLSX export failed: {exc}")

    stage2_exports = export_existing(sweep, STAGE2 / "images", STAGE2 / "tables", "param_sweep")
    safe("save Stage 2 latest copy", sweep.save, stage2_path)
    safe("save Stage 2 timestamp copy", sweep.save, stage2_ts)
    write_report(
        STAGE2 / "reports" / "param_sweep_report.md",
        "Parameter Sweep Report",
        [
            f"Saved sweep model: `{stage2_path}`.",
            f"Saved timestamped model: `{stage2_ts}`.",
            f"Planned one-dimensional sweep points: {len(sweep_plan)}.",
            f"Successful solves: {solve_ok_count}.",
            "This remains a single-phase fixed-ring model and does not compute a true fountain height.",
        ],
        {"sweep_plan": sweep_plan, "rows": sweep_rows, "exports": stage2_exports},
    )

    update_readme_changelog(
        {
            "stage0": "completed",
            "stage1": "completed" if stage1_path.exists() else "failed",
            "stage2": "completed" if stage2_path.exists() else "failed",
            "solve": f"{solve_ok_count}/{len(sweep_plan)} sweep points solved",
            "issues": "See failed metric/export entries in reports and logs.",
        }
    )
    log("Finished automation")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        make_dirs()
        log(f"FATAL: {error}")
        with LOG.open("a", encoding="utf-8") as handle:
            handle.write(traceback.format_exc())
        raise
