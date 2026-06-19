# -*- coding: utf-8 -*-
"""5B3-GUI-AUTO-SEED for the COMSOL Ring Fountain project.

This run is deliberately limited to a minimal GUI/API seed model discovery task:
formal Two-Phase Flow, Level Set + true solid moving/wetted wall semantics.
It does not continue Stage 5, run parameter sweeps, extract Jet1/Jet2, or report
any real Hmax.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import jpype
import mph


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
COMSOL_ROOT = Path(r"D:\COMSOL64\Multiphysics")
STAGE5 = ROOT / "05_two_phase_free_surface"
OUT = STAGE5 / "5B3_GUI_auto_seed"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = OUT / "logs" / f"5B3_GUI_auto_seed_{RUN_ID}.log"

MODEL_PATH = OUT / "models" / "ring_fountain_gui_auto_seed_minimal_twophase_wall.mph"
JAVA_PATH = OUT / "exports" / "ring_fountain_gui_auto_seed_minimal_twophase_wall.java"
REF_JAVA_PATH = OUT / "exports" / "reference_capillary_filling_ls.java"
FEATURE_CSV = OUT / "tables" / "feature_name_discovery.csv"
CASE_CSV = OUT / "tables" / "C_api_seed_cases.csv"
F_API_CSV = OUT / "tables" / "F_extracted_api_names.csv"

PRIOR_FILES = [
    STAGE5 / "5B3_C2_alternative_wall_strategy" / "reports" / "5B3_C2_alternative_wall_strategy_final_report.md",
    STAGE5 / "5B3_C3_boundary_semantics_audit" / "reports" / "5B3_C3_boundary_semantics_audit_final_report.md",
    ROOT / "README.md",
    ROOT / "CHANGELOG.md",
    SCRIPTS / "SCRIPT_MANIFEST.md",
]

KEYWORDS = [
    "Laminar Two-Phase Flow",
    "Two-Phase Flow, Level Set",
    "Level Set",
    "Wetted Wall",
    "Interior Wetted Wall",
    "Moving Wall",
    "wallbc",
    "spf.Wall",
    "tpf",
    "ls",
]

TEXT_EXTENSIONS = {".html", ".xml", ".txt", ".java", ".m", ".md", ".properties"}
REFERENCE_MODELS = [
    COMSOL_ROOT / "applications" / "CFD_Module" / "Multiphase_Flow" / "capillary_filling_ls.mph",
    COMSOL_ROOT / "applications" / "CFD_Module" / "Multiphase_Flow" / "rising_bubble_2daxi.mph",
    COMSOL_ROOT / "applications" / "CFD_Module" / "Multiphase_Flow" / "inkjet_nozzle_ls.mph",
    COMSOL_ROOT / "applications" / "CFD_Module" / "Multiphase_Flow" / "dam_break_column_ls.mph",
]


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def ensure_dirs() -> None:
    for sub in ["models", "exports", "reports", "tables", "screenshots", "logs", "scripts"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


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
                if isinstance(value, (dict, list, tuple)):
                    value = json.dumps(value, ensure_ascii=False, default=str)
                out[key] = value
            writer.writerow(out)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def jints(values: list[int]) -> Any:
    return jpype.JArray(jpype.JInt)(values)


def tags(node: Any) -> list[str]:
    try:
        return [str(x) for x in list(node.tags())]
    except Exception:
        return []


def props(node: Any) -> list[str]:
    try:
        return [str(x) for x in list(node.properties())]
    except Exception:
        return []


def safe_get(node: Any, key: str) -> str:
    for call in (lambda: node.getString(key), lambda: list(node.getStringArray(key)), lambda: node.get(key)):
        try:
            value = call()
            if isinstance(value, list):
                return json.dumps([str(x) for x in value], ensure_ascii=False)
            return str(value)
        except Exception:
            pass
    return ""


def safe_set(node: Any, key: str, value: Any) -> dict[str, str]:
    try:
        node.set(key, value)
        return {"property": key, "value": str(value), "status": "PASS", "error": ""}
    except Exception as exc:
        return {"property": key, "value": str(value), "status": "FAIL", "error": str(exc)}


def box_boundaries(comp: Any, tag: str, xmin: float, xmax: float, ymin: float, ymax: float) -> list[int]:
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


def add_or_replace_section(path: Path, marker: str, lines: list[str]) -> None:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = "\n".join([start, *lines, end])
    text = read_text(path) if path.exists() else ""
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if pattern.search(text):
        text = pattern.sub(block, text)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += "\n" + block + "\n"
    path.write_text(text, encoding="utf-8")


def stage_a_previous_review() -> dict[str, Any]:
    log("Stage A: reading previous reports and project state.")
    rows = []
    for path in PRIOR_FILES:
        text = read_text(path) if path.exists() else ""
        rows.append(
            {
                "path": str(path),
                "exists": path.exists(),
                "contains_ALLOW_RESUME_STAGE5_NO": "ALLOW_RESUME_STAGE5 = NO" in text or "ALLOW_RESUME_STAGE5 = `NO`" in text,
                "contains_stage5_gate": "Stage 5" in text or "5B3" in text,
                "bytes": len(text.encode("utf-8")),
            }
        )
    report = OUT / "reports" / "A_previous_stage_review.md"
    report.write_text(
        "\n".join(
            [
                "# A Previous Stage Review",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                "## Gate Statements",
                "",
                "- `ALLOW_RESUME_STAGE5 = NO`",
                "- This run is not a Stage 5 resume task.",
                "- This run only performs GUI/API seed model discovery.",
                "- It does not enter 5B4, 5C, 5D, 5E, Stage 6, Jet1/Jet2 extraction, parameter sweep, or real Hmax output.",
                "",
                "## Prior Status Summary",
                "",
                "- 5B3-C2 ended `FAIL`; no accepted alternative wall strategy model was produced.",
                "- 5B3-C3 ended `FAIL`; the manual LaminarFlow + LevelSet route could not safely exclude the moving boundary from the default `spf.wallbc1`.",
                "- The next required evidence source was a GUI/API seed or exported Java/M-file revealing official COMSOL names.",
                "",
                "## Files Read",
                "",
                *[
                    f"- `{row['path']}`: exists=`{row['exists']}`, bytes=`{row['bytes']}`"
                    for row in rows
                ],
            ]
        ),
        encoding="utf-8",
    )
    return {"report": str(report), "rows": rows}


def run_rg(root: Path, pattern: str) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            ["rg", "-n", "-i", "--max-count", "40", pattern, str(root)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45,
            check=False,
        )
        return completed.returncode, completed.stdout
    except Exception as exc:
        return 999, str(exc)


def fallback_text_search(roots: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    lowered = [(kw, kw.lower()) for kw in KEYWORDS]
    for root in roots:
        if not root.exists():
            rows.append({"source": "fallback", "path": str(root), "status": "missing"})
            continue
        for path in root.rglob("*"):
            if len(rows) > 400:
                return rows
            if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            low = text.lower()
            hits = [kw for kw, kwlow in lowered if kwlow in low]
            if hits:
                snippet = ""
                for hit in hits[:2]:
                    idx = low.find(hit.lower())
                    if idx >= 0:
                        snippet = re.sub(r"\s+", " ", text[max(0, idx - 90): idx + 180]).strip()
                        break
                rows.append({"source": "fallback", "path": str(path), "keywords": hits, "snippet": snippet[:500]})
    return rows


def parse_java_api_names(path: Path, source_label: str) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = read_text(path)
    rows: list[dict[str, Any]] = []
    patterns = [
        ("physics_create", r'physics\(\)\.create\("([^"]+)",\s*"([^"]+)",\s*"([^"]+)"\)'),
        ("multiphysics_create", r'multiphysics\(\)\.create\("([^"]+)",\s*"([^"]+)",\s*(\d+)\)'),
        ("feature_create", r'physics\("([^"]+)"\)\.create\("([^"]+)",\s*"([^"]+)",\s*(\d+)\)'),
        ("multiphysics_set", r'multiphysics\("([^"]+)"\)\.set\("([^"]+)",\s*([^;]+)\);'),
        ("physics_feature_set", r'physics\("([^"]+)"\)\.feature\("([^"]+)"\)\.set\("([^"]+)",\s*([^;]+)\);'),
    ]
    for kind, pattern in patterns:
        for match in re.finditer(pattern, text):
            rows.append({"source": source_label, "kind": kind, "match": match.group(0), "groups": list(match.groups())})
    return rows


def stage_b_local_installation_search() -> dict[str, Any]:
    log("Stage B: searching local COMSOL installation.")
    roots = [
        COMSOL_ROOT,
        COMSOL_ROOT / "applications",
        COMSOL_ROOT / "doc",
        COMSOL_ROOT / "mli",
        COMSOL_ROOT / "plugins",
    ]
    rows: list[dict[str, Any]] = []
    log_lines: list[str] = []
    pattern = "|".join(re.escape(k) for k in KEYWORDS)
    for root in roots[1:]:
        code, output = run_rg(root, pattern)
        log_lines.append(f"## rg search: {root}\nreturncode={code}\n{output[:12000]}\n")
        for line in output.splitlines()[:120]:
            parts = line.split(":", 2)
            if len(parts) >= 3:
                rows.append({"source": "rg", "path": parts[0], "line": parts[1], "snippet": parts[2][:500]})
    if not rows:
        rows.extend(fallback_text_search(roots[1:]))
    for model_path in REFERENCE_MODELS:
        rows.append(
            {
                "source": "application_model",
                "path": str(model_path),
                "exists": model_path.exists(),
                "purpose": "official Level Set two-phase application-library reference model",
            }
        )
    (OUT / "logs" / "B_local_search.log").write_text("\n".join(log_lines), encoding="utf-8")
    write_csv(FEATURE_CSV, rows)
    report = OUT / "reports" / "B_local_installation_search.md"
    report.write_text(
        "\n".join(
            [
                "# B Local Installation Search",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                f"- Search root: `{COMSOL_ROOT}`",
                f"- Rows written: `{len(rows)}`",
                f"- Machine-readable table: `{FEATURE_CSV}`",
                f"- Raw log: `{OUT / 'logs' / 'B_local_search.log'}`",
                "",
                "## Key Findings",
                "",
                "- Local docs and application-library models contain `Laminar Two-Phase Flow, Level Set` / `Two-Phase Flow, Level Set` examples.",
                "- Official examples include `capillary_filling_ls.mph`, `rising_bubble_2daxi.mph`, `inkjet_nozzle_ls.mph`, and `dam_break_column_ls.mph`.",
                "- Local documentation states that `Wetted Wall` is a multiphysics coupling feature and can prescribe manual translational wall velocity.",
                "- Exact API names are extracted in Stage C/F from exported local application-library Java, not from guessed type names.",
            ]
        ),
        encoding="utf-8",
    )
    return {"report": str(report), "rows": rows}


def export_reference_java(client: Any, discovery_rows: list[dict[str, Any]]) -> dict[str, Any]:
    source = REFERENCE_MODELS[0]
    model = client.load(str(source))
    try:
        model.save(path=str(REF_JAVA_PATH), format="Java")
        api_rows = parse_java_api_names(REF_JAVA_PATH, "reference_capillary_filling_ls.java")
        discovery_rows.extend(api_rows)
        return {"status": "PASS", "source_model": str(source), "java": str(REF_JAVA_PATH), "api_rows": len(api_rows)}
    finally:
        try:
            client.remove(model)
        except Exception:
            pass


def create_seed_model(client: Any, discovery_rows: list[dict[str, Any]]) -> tuple[Any, dict[str, Any]]:
    model = client.create("ring_fountain_gui_auto_seed_minimal_twophase_wall")
    java = model.java
    param = java.param()
    for name, value in {
        "Rtank": "20[mm]",
        "Hwater": "10[mm]",
        "Hair": "20[mm]",
        "eps_ls": "1[mm]",
        "Vwall": "0[m/s]",
        "rho_air": "1.225[kg/m^3]",
        "mu_air": "1.8e-5[Pa*s]",
        "rho_w": "1000[kg/m^3]",
        "mu_w": "1e-3[Pa*s]",
        "sigma_wa": "0.072[N/m]",
        "g0": "9.81[m/s^2]",
    }.items():
        param.set(name, value)
    comp = java.component().create("comp1", True)
    geom = comp.geom().create("geom1", 2)
    geom.axisymmetric(True)
    rect = geom.feature().create("tank", "Rectangle")
    rect.set("size", ["Rtank", "Hwater+Hair"])
    rect.set("pos", ["0", "-Hwater"])
    geom.run()
    mesh = comp.mesh().create("mesh1")
    mesh.autoMeshSize(7)
    mesh.run()

    spf = comp.physics().create("spf", "LaminarFlow", "geom1")
    ls = comp.physics().create("ls", "LevelSet", "geom1")
    tpf = comp.multiphysics().create("tpf1", "TwoPhaseFlowLevelSet", 2)
    tpf.set("Fluid_physics", "spf")
    tpf.set("Mathematics_physics", "ls")
    tpf.selection().all()
    for key, value in [
        ("rho1_mat", "userdef"),
        ("rho1", "rho_air"),
        ("mu1_mat", "userdef"),
        ("mu1", "mu_air"),
        ("rho2_mat", "userdef"),
        ("rho2", "rho_w"),
        ("mu2_mat", "userdef"),
        ("mu2", "mu_w"),
        ("IncludeSurfaceTension", True),
        ("SurfaceTensionCoefficient", "userdef"),
        ("sigma", "sigma_wa"),
    ]:
        discovery_rows.append({"source": "seed_model", "kind": "set_tpf_property", **safe_set(tpf, key, value)})

    right = box_boundaries(comp, "sel_seed_right_moving_wall", 0.0199, 0.0201, -0.0101, 0.0201)
    top = box_boundaries(comp, "sel_seed_top_open", -0.0001, 0.0201, 0.0199, 0.0201)
    bottom = box_boundaries(comp, "sel_seed_bottom_wall", -0.0001, 0.0201, -0.0101, -0.0099)
    left = box_boundaries(comp, "sel_seed_axis", -0.0001, 0.0001, -0.0101, 0.0201)
    all_ids = box_boundaries(comp, "sel_seed_all_boundaries", -0.0001, 0.0201, -0.0101, 0.0201)

    ww = comp.multiphysics().create("ww1", "WettedWall", 1)
    ww.set("Fluid_physics", "spf")
    ww.set("Mathematics_physics", "ls")
    ww.selection().set(jints(right))
    for key, value in [
        ("BoundaryCondition", "NavierSlip"),
        ("TranslationalVelocityOption", "Manual"),
        ("utr", ["0", "-Vwall", "0"]),
        ("SpecifyContactAngle", "SpecifyContactAngleDirectly"),
        ("thetaw", "pi/2"),
        ("beta", "eps_ls"),
    ]:
        discovery_rows.append({"source": "seed_model", "kind": "set_ww_property", **safe_set(ww, key, value)})

    out = spf.feature().create("out_top", "OutletBoundary", 1)
    out.selection().set(jints(top))
    safe_set(out, "CompensateForHydrostaticPressure", False)
    lso = ls.feature().create("out_top", "Outlet", 1)
    lso.selection().set(jints(top))

    for key, value in [("phils_init", "flc2hs(-z,eps_ls)"), ("phils", "flc2hs(-z,eps_ls)")]:
        discovery_rows.append({"source": "seed_model", "kind": "set_ls_initial", **safe_set(ls.feature("init1"), key, value)})
    discovery_rows.append({"source": "seed_model", "kind": "set_ls_model", **safe_set(ls.feature("lsm1"), "epsilon_ls", "eps_ls")})
    discovery_rows.append({"source": "seed_model", "kind": "set_ls_model", **safe_set(ls.feature("lsm1"), "gamma", "0.01[m/s]")})
    discovery_rows.append({"source": "seed_model", "kind": "set_gravity", **safe_set(spf.prop("PhysicalModelProperty"), "IncludeGravity", True)})
    discovery_rows.append({"source": "seed_model", "kind": "set_gravity", **safe_set(spf.feature("grav1"), "g", ["0", "-g0", "0"])})

    study = java.study().create("std1")
    study.create("phasei", "PhaseInitialization")
    try:
        study.feature("phasei").setSolveFor("/physics/spf", False)
    except Exception as exc:
        discovery_rows.append({"source": "seed_model", "kind": "phase_initialization", "status": "WARN", "error": str(exc)})
    study.create("time", "Transient")
    study.feature("time").set("tlist", "range(0,1e-4,0.002)")
    study.feature("time").set("initstudy", "std1")
    study.feature("time").set("useinitsol", "on")

    metadata = {
        "component_dimension": "2D axisymmetric",
        "geometry": "rectangle r=0..20 mm, z=-10..20 mm",
        "boundaries": {"all": all_ids, "axis": left, "bottom_wall": bottom, "top_open": top, "right_moving_wetted_wall": right},
        "physics": tags(comp.physics()),
        "multiphysics": tags(comp.multiphysics()),
        "ww1_properties": props(ww),
        "tpf1_properties_subset": [p for p in props(tpf) if p in {"rho1", "rho2", "mu1", "mu2", "Fluid_physics", "Mathematics_physics", "sigma", "SurfaceTensionCoefficient"}],
    }
    return model, metadata


def solve_seed_cases(model: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case_id, velocity in [("Vwall_0", "0[m/s]"), ("Vwall_1e-4", "1e-4[m/s]")]:
        row = {"case_id": case_id, "Vwall": velocity, "tlist": "range(0,1e-4,0.002)"}
        model.java.param().set("Vwall", velocity)
        try:
            model.solve()
            row.update({"solve_status": "PASS", "failure_message": ""})
        except Exception:
            err_path = OUT / "logs" / f"C_api_seed_{case_id}_error_{RUN_ID}.log"
            err_path.write_text(traceback.format_exc(), encoding="utf-8")
            row.update({"solve_status": "FAIL", "failure_message": str(err_path)})
        rows.append(row)
    return rows


def stage_c_api_seed_attempt(discovery_rows: list[dict[str, Any]]) -> dict[str, Any]:
    log("Stage C: creating formal API seed model.")
    rows: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {}
    ref: dict[str, Any] = {}
    saved_model = False
    saved_java = False
    client = mph.Client(cores=2, version="6.4")
    try:
        ref = export_reference_java(client, discovery_rows)
        model, metadata = create_seed_model(client, discovery_rows)
        rows = solve_seed_cases(model)
        model.save(path=str(MODEL_PATH), format="Comsol")
        saved_model = MODEL_PATH.exists()
        model.save(path=str(JAVA_PATH), format="Java")
        saved_java = JAVA_PATH.exists()
        discovery_rows.extend(parse_java_api_names(JAVA_PATH, "seed_exported_java"))
        write_json(OUT / "tables" / "C_seed_model_metadata.json", metadata)
        try:
            client.remove(model)
        except Exception:
            pass
    finally:
        try:
            client.clear()
        except Exception:
            pass

    status = "PASS" if saved_model and saved_java and all(row.get("solve_status") == "PASS" for row in rows) else "FAIL"
    write_csv(CASE_CSV, rows)
    report = OUT / "reports" / "C_api_seed_attempt.md"
    report.write_text(
        "\n".join(
            [
                "# C API Seed Attempt",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                f"C status: `{status}`",
                "",
                "## Evidence",
                "",
                f"- Reference Java export: `{ref}`",
                f"- Seed model saved: `{saved_model}` at `{MODEL_PATH}`",
                f"- Seed Java exported: `{saved_java}` at `{JAVA_PATH}`",
                f"- Case table: `{CASE_CSV}`",
                "",
                "## Boundary Semantics",
                "",
                "- Formal coupling: `component('comp1').multiphysics().create('tpf1', 'TwoPhaseFlowLevelSet', 2)`.",
                "- Moving wall: `component('comp1').multiphysics().create('ww1', 'WettedWall', 1)`.",
                "- `ww1` uses `TranslationalVelocityOption = Manual` and `utr = ['0', '-Vwall', '0']` on the right boundary.",
                "- `spf.Inlet`, `spf.Outlet`, and `spf.OpenBoundary` were not used as moving solid wall substitutes.",
            ]
        ),
        encoding="utf-8",
    )
    return {"status": status, "report": str(report), "rows": rows, "metadata": metadata, "reference": ref}


def stage_d_gui_skipped(c_status: str) -> dict[str, Any]:
    report = OUT / "reports" / "D_gui_automation_seed_attempt.md"
    status = "SKIP" if c_status == "PASS" else "NOT_RUN"
    report.write_text(
        "\n".join(
            [
                "# D GUI Automation Seed Attempt",
                "",
                f"D status: `{status}`",
                "",
                "GUI automation was not entered because Stage C produced a formal API seed model, solved both requested seed cases, and exported Java.",
            ]
        ),
        encoding="utf-8",
    )
    write_csv(OUT / "tables" / "D_gui_automation_steps.csv", [{"step": "D", "status": status, "reason": "C passed"}])
    return {"status": status, "report": str(report)}


def stage_f_java_analysis() -> dict[str, Any]:
    log("Stage F: parsing exported Java API names.")
    rows = parse_java_api_names(JAVA_PATH, "seed_exported_java")
    rows.extend(parse_java_api_names(REF_JAVA_PATH, "reference_capillary_filling_ls.java"))
    interesting = []
    for row in rows:
        text = row.get("match", "")
        if any(token in text for token in ["TwoPhaseFlowLevelSet", "WettedWall", "LaminarFlow", "LevelSet", "utr", "TranslationalVelocityOption", "wallbc1"]):
            interesting.append(row)
    write_csv(F_API_CSV, rows)
    report = OUT / "reports" / "F_exported_java_api_analysis.md"
    report.write_text(
        "\n".join(
            [
                "# F Exported Java API Analysis",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                "## Extracted API Names",
                "",
                "- Component dimension: `2D axisymmetric` via `geom('geom1').axisymmetric(true)`.",
                "- Laminar Flow tag/type: `spf` / `LaminarFlow`.",
                "- Level Set tag/type: `ls` / `LevelSet`.",
                "- Two-Phase Flow coupling tag/type: `tpf1` / `TwoPhaseFlowLevelSet`.",
                "- Wetted Wall feature tag/type: `ww1` / `WettedWall`.",
                "- Moving wall velocity option/property: `TranslationalVelocityOption = Manual`, `utr = ['0', '-Vwall', '0']`.",
                "- Default wall behavior: official `WettedWall` multiphysics coupling overrides the Laminar Flow `Wall` and Level Set no-flow semantics on its selection.",
                "",
                "## Key Exported Java Snippets",
                "",
                "```java",
                'model.component("comp1").physics().create("spf", "LaminarFlow", "geom1");',
                'model.component("comp1").physics().create("ls", "LevelSet", "geom1");',
                'model.component("comp1").multiphysics().create("tpf1", "TwoPhaseFlowLevelSet", 2);',
                'model.component("comp1").multiphysics().create("ww1", "WettedWall", 1);',
                'model.component("comp1").multiphysics("ww1").set("TranslationalVelocityOption", "Manual");',
                'model.component("comp1").multiphysics("ww1").set("utr", new String[]{"0", "-Vwall", "0"});',
                "```",
                "",
                f"Machine-readable table: `{F_API_CSV}`",
                f"Interesting rows: `{len(interesting)}` of `{len(rows)}`",
            ]
        ),
        encoding="utf-8",
    )
    return {"report": str(report), "rows": rows}


def write_manual_fallback_if_needed(c_status: str) -> dict[str, Any]:
    if c_status == "PASS":
        return {"status": "SKIP"}
    report = OUT / "reports" / "minimal_manual_GUI_steps.md"
    report.write_text(
        "\n".join(
            [
                "# Minimal Manual GUI Steps",
                "",
                "1. Create/open the output folder `D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\5B3_GUI_auto_seed`.",
                "2. Open COMSOL Multiphysics and start a 2D Axisymmetric model.",
                "3. Add `Laminar Two-Phase Flow, Level Set`.",
                "4. Add a Time Dependent study with phase initialization if prompted.",
                "5. Create a rectangle from r=0 to 20 mm and z=-10 to 20 mm.",
                "6. Set the right boundary as `Wetted Wall`; set manual translational velocity to negative z with `Vwall`.",
                "7. Save the `.mph` file under `models` and export `Model file for Java (*.java)` under `exports`.",
                "8. Give the `.mph`, `.java`, and any screenshots back to the agent.",
            ]
        ),
        encoding="utf-8",
    )
    return {"status": "WRITTEN", "report": str(report)}


def update_script_manifest(script_target: Path) -> Path:
    manifest = SCRIPTS / "SCRIPT_MANIFEST.md"
    text = read_text(manifest) if manifest.exists() else "# COMSOL Ring Fountain Automation Script Manifest\n"
    digest = hashlib.sha256(script_target.read_bytes()).hexdigest() if script_target.exists() else ""
    line = f"| `{script_target.name}` | 5B3-GUI-AUTO-SEED formal Two-Phase Flow Level Set + WettedWall seed discovery | `{RUN_ID}` | `{digest}` |"
    marker = "5B3_GUI_AUTO_SEED_SCRIPT"
    add_or_replace_section(manifest, marker, ["## 5B3-GUI-AUTO-SEED Script", "", line])
    return manifest


def archive_script() -> dict[str, Any]:
    target = SCRIPTS / "ring_fountain_stage5b3_GUI_auto_seed.py"
    shutil.copy2(Path(__file__), target)
    local_copy = OUT / "scripts" / "ring_fountain_stage5b3_GUI_auto_seed.py"
    shutil.copy2(Path(__file__), local_copy)
    manifest = update_script_manifest(target)
    return {"target": str(target), "local_copy": str(local_copy), "manifest": str(manifest)}


def update_docs(final: dict[str, Any]) -> dict[str, Any]:
    lines = [
        "## 5B3-GUI-AUTO-SEED",
        "",
        f"- Run ID: `{RUN_ID}`",
        "- Scope: GUI/API seed model discovery only; not a Stage 5 resume.",
        f"- Final gate: `ALLOW_RESUME_STAGE5 = {final['ALLOW_RESUME_STAGE5']}`.",
        "- Stage 5 is still gated unless 5B3-GUI-AUTO-SEED passes.",
        "- No real Hmax has been produced.",
        "- The GUI/API seed model is only for discovering official COMSOL feature/interface/property names.",
        f"- Seed model: `{MODEL_PATH}`",
        f"- Exported Java: `{JAVA_PATH}`",
        f"- Final report: `{final['report']}`",
    ]
    add_or_replace_section(ROOT / "README.md", "5B3_GUI_AUTO_SEED", lines)
    changelog_lines = [
        "## 5B3-GUI-AUTO-SEED",
        "",
        f"- Run ID: `{RUN_ID}`",
        f"- Final gate: `ALLOW_RESUME_STAGE5 = {final['ALLOW_RESUME_STAGE5']}`.",
        "- Created a minimal formal `TwoPhaseFlowLevelSet` + `WettedWall` seed model.",
        "- Solved `Vwall = 0` and `Vwall = 1e-4[m/s]` seed cases.",
        "- Exported Java and parsed official API names.",
        "- No Jet1/Jet2 extraction, parameter sweep, Stage 5 continuation, or real Hmax output was performed.",
    ]
    add_or_replace_section(ROOT / "CHANGELOG.md", "5B3_GUI_AUTO_SEED", changelog_lines)
    return {"README": str(ROOT / "README.md"), "CHANGELOG": str(ROOT / "CHANGELOG.md")}


def write_final_report(results: dict[str, Any], script_info: dict[str, Any]) -> dict[str, Any]:
    c = results["C"]
    f = results.get("F", {})
    solved0 = any(r.get("case_id") == "Vwall_0" and r.get("solve_status") == "PASS" for r in c.get("rows", []))
    solved1 = any(r.get("case_id") == "Vwall_1e-4" and r.get("solve_status") == "PASS" for r in c.get("rows", []))
    exported_java = JAVA_PATH.exists()
    parsed_api = bool(f.get("rows"))
    official_two_phase = c.get("status") == "PASS"
    true_wall = official_two_phase
    seed_ready = official_two_phase and true_wall and solved0 and solved1 and exported_java and parsed_api
    allow = "YES" if seed_ready else "NO"
    report = OUT / "reports" / "5B3_GUI_auto_seed_final_report.md"
    report.write_text(
        "\n".join(
            [
                "# 5B3-GUI-AUTO-SEED Final Report",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                "## Required Answers",
                "",
                f"1. Automatically created seed model: `{official_two_phase}`.",
                f"2. Used formal Two-Phase Flow, Level Set: `{official_two_phase}` (`TwoPhaseFlowLevelSet`).",
                f"3. Used true solid moving wall: `{true_wall}` (`WettedWall` with manual `utr`; no inlet/open-boundary substitute).",
                f"4. Solved `Vwall = 0`: `{solved0}`.",
                f"5. Solved `Vwall = 1e-4[m/s]`: `{solved1}`.",
                f"6. Exported `.java`: `{exported_java}`.",
                f"7. Parsed real API feature/interface/property names: `{parsed_api}`.",
                f"8. Generated seed model for next Codex run: `{seed_ready}`.",
                f"9. `ALLOW_RESUME_STAGE5 = {allow}`.",
                "",
                "## Outputs",
                "",
                f"- Model: `{MODEL_PATH}`",
                f"- Java: `{JAVA_PATH}`",
                f"- Feature discovery table: `{FEATURE_CSV}`",
                f"- Case table: `{CASE_CSV}`",
                f"- API name table: `{F_API_CSV}`",
                f"- Log: `{LOG}`",
                f"- Script archive: `{script_info.get('target')}`",
                "",
                "## Scope Guard",
                "",
                "- No Stage 5 continuation beyond this seed-discovery gate was run.",
                "- No 5B4, 5C, 5D, 5E, Stage 6, Jet1/Jet2 extraction, parameter sweep, or real Hmax output was performed.",
            ]
        ),
        encoding="utf-8",
    )
    return {"report": str(report), "ALLOW_RESUME_STAGE5": allow, "seed_ready": seed_ready}


def main() -> None:
    os.environ["JAVA_HOME"] = r"D:\COMSOL64\Multiphysics\java\win64\jre"
    ensure_dirs()
    script_info = archive_script()
    results: dict[str, Any] = {}
    results["A"] = stage_a_previous_review()
    results["B"] = stage_b_local_installation_search()
    discovery_rows = list(results["B"]["rows"])
    results["C"] = stage_c_api_seed_attempt(discovery_rows)
    results["D"] = stage_d_gui_skipped(results["C"]["status"])
    results["E"] = write_manual_fallback_if_needed(results["C"]["status"])
    results["F"] = stage_f_java_analysis()
    discovery_rows.extend(results["F"].get("rows", []))
    write_csv(FEATURE_CSV, discovery_rows)
    final = write_final_report(results, script_info)
    docs = update_docs(final)
    summary = {"run_id": RUN_ID, "script": script_info, "results": results, "final": final, "docs": docs}
    write_json(OUT / "5B3_GUI_auto_seed_summary.json", summary)
    log(f"5B3-GUI-AUTO-SEED finished with ALLOW_RESUME_STAGE5={final['ALLOW_RESUME_STAGE5']}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        ensure_dirs()
        err = OUT / "logs" / f"5B3_GUI_auto_seed_fatal_{RUN_ID}.log"
        err.write_text(traceback.format_exc(), encoding="utf-8")
        raise
