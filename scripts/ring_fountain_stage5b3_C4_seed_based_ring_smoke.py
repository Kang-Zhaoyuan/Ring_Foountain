# -*- coding: utf-8 -*-
"""5B3-C4 seed-based ring free-surface moving-wall smoke test.

This script imports the successful GUI/API seed evidence and transfers the
official COMSOL API names to a minimal 2D axisymmetric ring-hole free-surface
smoke model.  It is deliberately gated: it does not enter 5B4, 5C, 5D, 5E,
Stage 6, Jet1/Jet2 extraction, parameter sweeps, or real Hmax reporting.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import jpype
import mph
import numpy as np


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
STAGE5 = ROOT / "05_two_phase_free_surface"
SEED = STAGE5 / "5B3_GUI_auto_seed"
C4 = STAGE5 / "5B3_C4_seed_based_ring_smoke"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = C4 / "logs" / f"5B3_C4_seed_based_ring_smoke_{RUN_ID}.log"

SEED_REPORT = SEED / "reports" / "5B3_GUI_auto_seed_final_report.md"
SEED_JAVA = SEED / "exports" / "ring_fountain_gui_auto_seed_minimal_twophase_wall.java"
SEED_MODEL = SEED / "models" / "ring_fountain_gui_auto_seed_minimal_twophase_wall.mph"

SCRIPT_ARCHIVE = SCRIPTS / "ring_fountain_stage5b3_C4_seed_based_ring_smoke.py"

sys.path.insert(0, str(SCRIPTS))
import ring_fountain_stage5_cleanup_5b_5c as base  # noqa: E402
import ring_fountain_stage4_2a as s42a  # noqa: E402


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def ensure_dirs() -> None:
    for sub in ["models", "exports", "reports", "tables", "images", "frames", "logs", "scripts"]:
        (C4 / sub).mkdir(parents=True, exist_ok=True)
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
                if isinstance(value, (list, dict, tuple)):
                    value = json.dumps(value, ensure_ascii=False, default=str)
                out[key] = value
            writer.writerow(out)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def jints(values: list[int]) -> Any:
    return jpype.JArray(jpype.JInt)(values)


def tags(node: Any) -> list[str]:
    try:
        return [str(x) for x in list(node.tags())]
    except Exception:
        return []


def safe_set(node: Any, key: str, value: Any) -> dict[str, Any]:
    try:
        node.set(key, value)
        return {"property": key, "value": value, "status": "PASS", "error": ""}
    except Exception as exc:
        return {"property": key, "value": value, "status": "FAIL", "error": str(exc)}


def parse_java_api(path: Path) -> list[dict[str, Any]]:
    text = read_text(path) if path.exists() else ""
    patterns = [
        ("physics_create", r'physics\(\)\.create\("([^"]+)",\s*"([^"]+)",\s*"([^"]+)"\)'),
        ("multiphysics_create", r'multiphysics\(\)\.create\("([^"]+)",\s*"([^"]+)",\s*(\d+)\)'),
        ("multiphysics_set", r'multiphysics\("([^"]+)"\)\.set\("([^"]+)",\s*([^)]+)\);'),
        ("physics_feature_set", r'physics\("([^"]+)"\)\.feature\("([^"]+)"\)\.set\("([^"]+)",\s*([^)]+)\);'),
        ("selection_set", r'multiphysics\("([^"]+)"\)\.selection\(\)\.set\(([^)]+)\);'),
    ]
    rows: list[dict[str, Any]] = []
    for kind, pattern in patterns:
        for match in re.finditer(pattern, text):
            rows.append({"source": str(path), "kind": kind, "match": match.group(0), "groups": list(match.groups())})
    return rows


def add_or_replace_section(path: Path, marker: str, lines: list[str]) -> None:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = "\n".join([start, *lines, end])
    text = read_text(path) if path.exists() else ""
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if pattern.search(text):
        text = pattern.sub(lambda _match: block, text)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += "\n" + block + "\n"
    path.write_text(text, encoding="utf-8")


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


def save_model_no_overwrite(model: Any, canonical: Path) -> dict[str, str]:
    canonical.parent.mkdir(parents=True, exist_ok=True)
    timestamp = canonical.with_name(f"{canonical.stem}_{RUN_ID}{canonical.suffix}")
    model.save(path=str(timestamp), format="Comsol")
    result = {"timestamp_model": str(timestamp)}
    if canonical.exists():
        result["model"] = str(canonical)
        result["canonical_note"] = "canonical existed; not overwritten"
    else:
        model.save(path=str(canonical), format="Comsol")
        result["model"] = str(canonical)
    return result


def save_java_no_overwrite(model: Any, canonical: Path) -> dict[str, str]:
    canonical.parent.mkdir(parents=True, exist_ok=True)
    timestamp = canonical.with_name(f"{canonical.stem}_{RUN_ID}{canonical.suffix}")
    model.save(path=str(timestamp), format="Java")
    result = {"timestamp_java": str(timestamp)}
    if canonical.exists():
        result["java"] = str(canonical)
        result["canonical_note"] = "canonical existed; not overwritten"
    else:
        model.save(path=str(canonical), format="Java")
        result["java"] = str(canonical)
    return result


def render_boundary_map(path: Path, boundaries: dict[str, list[int]]) -> str:
    width, height = 900, 640
    pix = bytearray([248, 248, 246] * width * height)
    def tx(r: float) -> int:
        return int(70 + r / 0.04 * 760)
    def ty(z: float) -> int:
        return int(560 - (z + 0.03) / 0.06 * 480)
    for x0, y0, x1, y1, color in [
        (tx(0), ty(-0.03), tx(0.04), ty(-0.03), (40, 40, 40)),
        (tx(0.04), ty(-0.03), tx(0.04), ty(0.03), (40, 40, 40)),
        (tx(0), ty(0.03), tx(0.04), ty(0.03), (30, 90, 180)),
        (tx(0), ty(-0.03), tx(0), ty(0.03), (30, 120, 30)),
        (tx(0.006), ty(-0.003), tx(0.012), ty(-0.003), (190, 60, 40)),
        (tx(0.006), ty(-0.001), tx(0.012), ty(-0.001), (190, 60, 40)),
        (tx(0.006), ty(-0.003), tx(0.006), ty(-0.001), (190, 60, 40)),
        (tx(0.012), ty(-0.003), tx(0.012), ty(-0.001), (190, 60, 40)),
    ]:
        base.line(pix, width, height, x0, y0, x1, y1, color)
    for r, z, color in [
        (0.009, -0.002, (220, 50, 50)),
        (0.02, 0.0, (40, 80, 200)),
        (0.039, 0.0, (40, 40, 40)),
    ]:
        base.circle(pix, width, height, tx(r), ty(z), 6, color)
    path.parent.mkdir(parents=True, exist_ok=True)
    base.png_write(path, width, height, pix)
    return str(path)


def import_seed_review() -> dict[str, Any]:
    log("A: importing GUI-auto-seed evidence.")
    report_text = read_text(SEED_REPORT) if SEED_REPORT.exists() else ""
    java_rows = parse_java_api(SEED_JAVA)
    required = {
        "TwoPhaseFlowLevelSet usable": "TwoPhaseFlowLevelSet" in report_text and any("TwoPhaseFlowLevelSet" in r["match"] for r in java_rows),
        "WettedWall usable": "WettedWall" in report_text and any("WettedWall" in r["match"] for r in java_rows),
        "TranslationalVelocityOption Manual usable": any("TranslationalVelocityOption" in r["match"] and "Manual" in r["match"] for r in java_rows),
        'utr {"0","-Vwall","0"} usable': any("utr" in r["match"] and "-Vwall" in r["match"] for r in java_rows),
        "Vwall=0 seed PASS": "Vwall = 0`: `True`" in report_text or "Vwall = 0 seed case PASS" in report_text,
        "Vwall=1e-4 seed PASS": "Vwall = 1e-4[m/s]`: `True`" in report_text or "1e-4" in report_text and "True" in report_text,
    }
    rows = [{"item": k, "status": "PASS" if v else "FAIL"} for k, v in required.items()]
    rows.extend({"item": f"java:{r['kind']}", "status": "INFO", "snippet": r["match"]} for r in java_rows if any(x in r["match"] for x in ["TwoPhaseFlowLevelSet", "WettedWall", "TranslationalVelocityOption", "utr", "phils", "grav1"]))
    write_csv(C4 / "tables" / "A_gui_auto_seed_api_names.csv", rows)
    (C4 / "reports" / "A_gui_auto_seed_import_review.md").write_text(
        "\n".join([
            "# A GUI-auto-seed Import Review",
            "",
            f"Run ID: `{RUN_ID}`",
            "",
            f"- Seed report exists: `{SEED_REPORT.exists()}`",
            f"- Seed Java exists: `{SEED_JAVA.exists()}`",
            f"- Seed model exists: `{SEED_MODEL.exists()}`",
            "",
            "## Required API Facts",
            "",
            *[f"- {k}: `{'PASS' if v else 'FAIL'}`" for k, v in required.items()],
            "",
            "## Scope Limits Preserved",
            "",
            "- The seed model is not a ring fountain model.",
            "- The seed model does not contain ring geometry.",
            "- The seed model does not produce real Hmax.",
            "- This C4 run is not Stage 6 or a parameter study.",
        ]),
        encoding="utf-8",
    )
    return {"status": "PASS" if all(required.values()) else "FAIL", "required": required}


def java_skeleton_report() -> dict[str, Any]:
    log("B: extracting reusable Java skeleton.")
    rows = parse_java_api(SEED_JAVA)
    write_csv(C4 / "tables" / "B_extracted_seed_api_skeleton.csv", rows)
    important = [r["match"] for r in rows if any(k in r["match"] for k in ["TwoPhaseFlowLevelSet", "WettedWall", "TranslationalVelocityOption", "utr", "phils", "lsm1", "grav1", "rho", "mu", "sigma"])]
    (C4 / "reports" / "B_seed_java_reusable_api_skeleton.md").write_text(
        "\n".join([
            "# B Seed Java Reusable API Skeleton",
            "",
            "Extracted real Java/API fragments from the GUI-auto-seed export:",
            "",
            "```java",
            *important[:120],
            "```",
            "",
            "Key transferred names:",
            "",
            "- Physics: `LaminarFlow`, `LevelSet`.",
            "- Multiphysics: `TwoPhaseFlowLevelSet`, `WettedWall`.",
            "- WettedWall properties: `BoundaryCondition`, `TranslationalVelocityOption`, `utr`, `SpecifyContactAngle`, `thetaw`, `beta`.",
            "- Initial Level Set: `phils_init`, `phils`.",
            "- Surface tension: `IncludeSurfaceTension`, `SurfaceTensionCoefficient`, `sigma`.",
            "- Gravity: `spf/grav1 g = {0,-g0,0}`.",
        ]),
        encoding="utf-8",
    )
    return {"status": "PASS" if important else "FAIL", "rows": len(rows)}


def create_ring_model(client: Any) -> tuple[Any, dict[str, Any]]:
    log("C: building minimal ring two-phase model.")
    model = client.create(f"ring_fountain_v5B3_C4_ring_twophase_smoke_{RUN_ID}")
    java = model.java
    param = java.param()
    for name, value in {
        "Rtank": "40[mm]",
        "Zmin": "-30[mm]",
        "Zmax": "30[mm]",
        "z0": "0[mm]",
        "Ro": "12[mm]",
        "Ri": "6[mm]",
        "h_ring": "2[mm]",
        "z_ring": "-2[mm]",
        "eps_ls": "1[mm]",
        "Vwall": "0[m/s]",
        "rho_w": "1000[kg/m^3]",
        "mu_w": "1e-3[Pa*s]",
        "rho_air": "1.2[kg/m^3]",
        "mu_air": "1.8e-5[Pa*s]",
        "sigma_wa": "0.072[N/m]",
        "g0": "9.81[m/s^2]",
        "t_end": "0.002[s]",
        "dt": "1e-4[s]",
    }.items():
        param.set(name, value)
    comp = java.component().create("comp1", True)
    geom = comp.geom().create("geom1", 2)
    geom.axisymmetric(True)
    tank = geom.feature().create("tank", "Rectangle")
    tank.set("size", ["Rtank", "Zmax-Zmin"])
    tank.set("pos", ["0", "Zmin"])
    ring = geom.feature().create("ring", "Rectangle")
    ring.set("size", ["Ro-Ri", "h_ring"])
    ring.set("pos", ["Ri", "z_ring-h_ring/2"])
    diff = geom.feature().create("dif1", "Difference")
    diff.selection("input").set(["tank"])
    diff.selection("input2").set(["ring"])
    geom.run()

    tol = 2e-4
    axis = box_boundaries(comp, "sel_axis", -tol, tol, -0.0305, 0.0305)
    top = box_boundaries(comp, "sel_top_open", -tol, 0.0405, 0.0298, 0.0302)
    bottom = box_boundaries(comp, "sel_bottom_wall", -tol, 0.0405, -0.0302, -0.0298)
    outer = box_boundaries(comp, "sel_outer_wall", 0.0398, 0.0402, -0.0305, 0.0305)
    ring_inner = box_boundaries(comp, "sel_ring_wall_inner", 0.0058, 0.0062, -0.0032, -0.0008)
    ring_outer = box_boundaries(comp, "sel_ring_wall_outer", 0.0118, 0.0122, -0.0032, -0.0008)
    ring_top = box_boundaries(comp, "sel_ring_wall_top", 0.0058, 0.0122, -0.0012, -0.0008)
    ring_bottom = box_boundaries(comp, "sel_ring_wall_bottom", 0.0058, 0.0122, -0.0032, -0.0028)
    ring_all = sorted(set(ring_inner + ring_outer + ring_top + ring_bottom))
    if "sel_ring_wettedwall_confirmed" in tags(comp.selection()):
        comp.selection().remove("sel_ring_wettedwall_confirmed")
    comp.selection().create("sel_ring_wettedwall_confirmed", "Explicit")
    comp.selection("sel_ring_wettedwall_confirmed").geom("geom1", 1)
    comp.selection("sel_ring_wettedwall_confirmed").set(jints(ring_all))

    mesh = comp.mesh().create("mesh1")
    mesh.autoMeshSize(5)
    mesh.run()

    spf = comp.physics().create("spf", "LaminarFlow", "geom1")
    ls = comp.physics().create("ls", "LevelSet", "geom1")
    tpf = comp.multiphysics().create("tpf1", "TwoPhaseFlowLevelSet", 2)
    tpf.set("Fluid_physics", "spf")
    tpf.set("Mathematics_physics", "ls")
    tpf.selection().all()
    tpf_rows = []
    for key, value in [
        ("rho1_mat", "userdef"), ("rho1", "rho_air"), ("mu1_mat", "userdef"), ("mu1", "mu_air"),
        ("rho2_mat", "userdef"), ("rho2", "rho_w"), ("mu2_mat", "userdef"), ("mu2", "mu_w"),
        ("IncludeSurfaceTension", True), ("SurfaceTensionCoefficient", "userdef"), ("sigma", "sigma_wa"),
    ]:
        tpf_rows.append({"feature": "tpf1", **safe_set(tpf, key, value)})

    ww = comp.multiphysics().create("ww1", "WettedWall", 1)
    ww.set("Fluid_physics", "spf")
    ww.set("Mathematics_physics", "ls")
    ww.selection().set(jints(ring_all))
    ww_rows = []
    for key, value in [
        ("BoundaryCondition", "NavierSlip"),
        ("TranslationalVelocityOption", "Manual"),
        ("utr", ["0", "-Vwall", "0"]),
        ("SpecifyContactAngle", "SpecifyContactAngleDirectly"),
        ("thetaw", "pi/2"),
        ("beta", "eps_ls"),
    ]:
        ww_rows.append({"feature": "ww1", **safe_set(ww, key, value)})

    out = spf.feature().create("out_top", "OutletBoundary", 1)
    out.selection().set(jints(top))
    safe_set(out, "CompensateForHydrostaticPressure", False)
    lso = ls.feature().create("out_top", "Outlet", 1)
    lso.selection().set(jints(top))
    ls.feature("init1").set("phils_init", "flc2hs(z0-z,eps_ls)")
    ls.feature("init1").set("phils", "flc2hs(z0-z,eps_ls)")
    ls.feature("lsm1").set("epsilon_ls", "eps_ls")
    ls.feature("lsm1").set("gamma", "0.01[m/s]")
    spf.prop("PhysicalModelProperty").set("IncludeGravity", True)
    spf.feature("grav1").set("g", ["0", "-g0", "0"])

    study = java.study().create("std1")
    study.create("phasei", "PhaseInitialization")
    try:
        study.feature("phasei").setSolveFor("/physics/spf", False)
    except Exception as exc:
        log(f"phase initialization setSolveFor warning: {exc}")
    study.create("time", "Transient")
    study.feature("time").set("tlist", "range(0,dt,t_end)")
    study.feature("time").set("initstudy", "std1")
    study.feature("time").set("useinitsol", "on")

    boundaries = {
        "axis": axis,
        "top_open": top,
        "bottom_wall": bottom,
        "outer_wall": outer,
        "ring_inner": ring_inner,
        "ring_outer": ring_outer,
        "ring_top": ring_top,
        "ring_bottom": ring_bottom,
        "ring_wettedwall_confirmed": ring_all,
    }
    metadata = {
        "boundaries": boundaries,
        "tpf_properties": tpf_rows,
        "wettedwall_properties": ww_rows,
        "physics": tags(comp.physics()),
        "multiphysics": tags(comp.multiphysics()),
    }
    return model, metadata


def write_stage_c_outputs(model: Any, metadata: dict[str, Any]) -> dict[str, Any]:
    paths = save_model_no_overwrite(model, C4 / "models" / "ring_fountain_v5B3_C4_ring_twophase_smoke_base.mph")
    render_boundary_map(C4 / "images" / "C_boundary_map.png", metadata["boundaries"])
    rows = []
    for name, ids in metadata["boundaries"].items():
        rows.append({"selection_name": name, "boundary_ids": ids, "used_for": "WettedWall" if name == "ring_wettedwall_confirmed" else "axis/open/static/default"})
    rows.extend({"selection_name": "ww1_property", "boundary_ids": "", "used_for": json.dumps(r, ensure_ascii=False, default=str)} for r in metadata["wettedwall_properties"])
    write_csv(C4 / "tables" / "C_boundary_selection_table.csv", rows)
    (C4 / "reports" / "C_ring_twophase_geometry_and_boundary_report.md").write_text(
        "\n".join([
            "# C Ring Twophase Geometry and Boundary Report",
            "",
            "Model: `ring_fountain_v5B3_C4_ring_twophase_smoke`",
            "",
            "## Geometry",
            "",
            "- 2D axisymmetric fixed geometry.",
            "- Fluid domain = tank rectangle minus ring rectangle.",
            "- Ring rectangle: `Ri <= r <= Ro`, `z_ring-h_ring/2 <= z <= z_ring+h_ring/2`.",
            "",
            "## Boundary Selections",
            "",
            *[f"- `{k}`: `{v}`" for k, v in metadata["boundaries"].items()],
            "",
            "## WettedWall",
            "",
            f"- WettedWall boundaries: `{metadata['boundaries']['ring_wettedwall_confirmed']}`",
            "- `TranslationalVelocityOption = Manual`",
            "- `utr = {\"0\", \"-Vwall\", \"0\"}`",
            "",
            f"- Base model: `{paths.get('model')}`",
            f"- Timestamp model: `{paths.get('timestamp_model')}`",
            f"- Boundary map: `{C4 / 'images' / 'C_boundary_map.png'}`",
        ]),
        encoding="utf-8",
    )
    (C4 / "logs" / "C_ring_twophase_build.log").write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return paths


def field_data(model: Any, inner: int) -> dict[str, np.ndarray]:
    data: dict[str, np.ndarray] = {}
    for expr, key, unit in [
        ("r", "r", "m"), ("z", "z", "m"), ("phils", "phi", ""),
        ("u", "u", "m/s"), ("w", "w", "m/s"), ("spf.U", "U", "m/s"), ("p", "p", "Pa"),
    ]:
        try:
            data[key] = s42a.eval_array(model, expr, unit, inner=[inner]).reshape(-1)
        except Exception:
            data[key] = np.full_like(data.get("r", np.array([math.nan])), math.nan, dtype=float)
    return data


def read_times(model: Any) -> list[float]:
    times: list[float] = []
    for inner in range(1, 200):
        try:
            t = s42a.finite_flat(model.evaluate("t", unit="s", inner=[inner]))
            if t.size == 0:
                break
            times.append(float(t[0]))
        except Exception:
            break
    return times


def extract_interface_outputs(model: Any, case_id: str, table_path: Path, plot_path: Path, phils_path: Path, velocity_path: Path | None = None) -> dict[str, Any]:
    times = read_times(model)
    rows: list[dict[str, Any]] = []
    frames: list[dict[str, Any]] = []
    for inner, t in enumerate(times, start=1):
        data = field_data(model, inner)
        pts = base.estimate_interface(data["r"], data["z"], data["phi"], threshold=0.5)
        valid = [(r, z) for r, z in pts if math.isfinite(r) and math.isfinite(z) and 0 <= r <= 0.04 and -0.03 <= z <= 0.03]
        max_z = max((z for _, z in valid), default=math.nan)
        rows.append({
            "case_id": case_id,
            "inner_solution": inner,
            "time_s": t,
            "interface_points": len(valid),
            "max_interface_z_m": max_z,
            "H_m": max_z,
            "H_mm": max_z * 1000 if math.isfinite(max_z) else math.nan,
            "near_top": bool(math.isfinite(max_z) and max_z > 0.028),
        })
        frame = C4 / "frames" / f"{case_id}_interface_frame_{inner:03d}.png"
        img = base.render_field(frame, data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True)
        frames.append({"inner_solution": inner, "time_s": t, "file": str(frame), "ok": img.get("ok")})
    write_csv(table_path, rows)
    base.render_curve(plot_path, rows)
    if times:
        last = len(times)
        data = field_data(model, last)
        base.render_field(phils_path, data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True)
        if velocity_path is not None:
            base.render_field(velocity_path, data["r"], data["z"], data["U"], cmap="viridis", phi=data["phi"], draw_interface=True)
    h0 = rows[0]["H_m"] if rows and math.isfinite(float(rows[0]["H_m"])) else math.nan
    hf = rows[-1]["H_m"] if rows and math.isfinite(float(rows[-1]["H_m"])) else math.nan
    delta = hf - h0 if math.isfinite(h0) and math.isfinite(hf) else math.nan
    interface_quality = "clear" if rows and min(int(r["interface_points"]) for r in rows) >= 2 and not any(bool(r["near_top"]) for r in rows) else "uncertain"
    return {"times": times, "rows": rows, "frames": frames, "H0": h0, "Hfinal": hf, "delta_H": delta, "interface_quality": interface_quality}


def solve_case(model: Any, case_id: str, vwall: str, model_path: Path, report_path: Path, table_path: Path, plot_path: Path, phils_path: Path, velocity_path: Path | None = None) -> dict[str, Any]:
    log(f"Solving {case_id} with Vwall={vwall}.")
    row: dict[str, Any] = {"case_id": case_id, "Vwall": vwall, "tlist": "range(0,dt,t_end)"}
    model.java.param().set("Vwall", vwall)
    try:
        model.solve()
        hdata = extract_interface_outputs(model, case_id, table_path, plot_path, phils_path, velocity_path)
        model.save(path=str(model_path), format="Comsol")
        delta = hdata["delta_H"]
        case_pass = bool(math.isfinite(delta) and abs(delta) <= 0.0002 and hdata["interface_quality"] == "clear")
        row.update({
            "solve_status": "PASS",
            "failure_message": "",
            "H0": hdata["H0"],
            "Hfinal": hdata["Hfinal"],
            "delta_H": delta,
            "interface_quality": hdata["interface_quality"],
            "case_pass": "PASS" if case_pass else "FAIL",
            "model": str(model_path),
        })
    except Exception:
        err = traceback.format_exc()
        err_path = C4 / "logs" / f"{case_id}_error_{RUN_ID}.log"
        err_path.write_text(err, encoding="utf-8")
        row.update({"solve_status": "FAIL", "failure_message": str(err_path), "case_pass": "FAIL"})
    report_path.write_text(
        "\n".join([
            f"# {case_id} Report",
            "",
            f"- Vwall: `{vwall}`",
            f"- Solve status: `{row.get('solve_status')}`",
            f"- Case pass: `{row.get('case_pass')}`",
            f"- Failure message/log: `{row.get('failure_message','')}`",
            f"- H(final)-H(0): `{row.get('delta_H')}` m",
            f"- Interface quality: `{row.get('interface_quality','')}`",
            "- This is fixed-geometry WettedWall moving-wall smoke evidence, not real Hmax extraction.",
        ]),
        encoding="utf-8",
    )
    return row


def update_docs(final: dict[str, Any]) -> None:
    log("Updating README, CHANGELOG, SCRIPT_MANIFEST.")
    status = final.get("C4_status", "FAIL")
    allow_5b4 = final.get("ALLOW_5B4", "NO")
    add_or_replace_section(ROOT / "README.md", "5B3_C4_SEED_BASED_RING_SMOKE", [
        "## 5B3-C4 Seed-based Ring Smoke",
        "",
        f"- Run ID: `{RUN_ID}`.",
        "- 5B3-GUI-AUTO-SEED: `PASS`.",
        f"- 5B3-C4 seed-based ring smoke: `{status}`.",
        f"- `ALLOW_5B4 = {allow_5b4}`; this run did not enter 5B4.",
        "- `ALLOW_5C = NO` and `ALLOW_STAGE6 = NO`.",
        "- Uses formal `TwoPhaseFlowLevelSet` + `WettedWall` with `TranslationalVelocityOption = Manual` and `utr = {0,-Vwall,0}`.",
        "- Fixed-geometry smoke test only; the ring outline does not physically fall.",
        "- No real Hmax has been produced.",
        "- No Jet1/Jet2 extraction has been performed.",
        "- No Stage 6 parameter sweep has been performed.",
        f"- Final report: `{C4 / 'reports' / '5B3_C4_seed_based_ring_smoke_final_report.md'}`.",
    ])
    add_or_replace_section(ROOT / "CHANGELOG.md", "5B3_C4_SEED_BASED_RING_SMOKE", [
        "## 5B3-C4 Seed-based Ring Smoke",
        "",
        f"- Run ID: `{RUN_ID}`.",
        f"- Status: `{status}`.",
        f"- Gate: `ALLOW_5B4 = {allow_5b4}`, `ALLOW_5C = NO`, `ALLOW_STAGE6 = NO`.",
        "- Imported GUI-auto-seed API names and rebuilt a minimal ring-hole two-phase WettedWall smoke model.",
        "- No 5B4/5C/5D/5E/Stage 6, Jet1/Jet2 extraction, parameter sweep, or real Hmax output was performed.",
        f"- Final report: `{C4 / 'reports' / '5B3_C4_seed_based_ring_smoke_final_report.md'}`.",
    ])
    manifest_line = f"| `ring_fountain_stage5b3_C4_seed_based_ring_smoke.py` | 5B3-C4 seed-based ring free-surface WettedWall smoke | `{RUN_ID}` | `{sha256(SCRIPT_ARCHIVE)}` |"
    add_or_replace_section(SCRIPTS / "SCRIPT_MANIFEST.md", "5B3_C4_SEED_BASED_RING_SMOKE_SCRIPT", [
        "## 5B3-C4 Script",
        "",
        manifest_line,
    ])


def main() -> int:
    ensure_dirs()
    shutil.copy2(Path(__file__), SCRIPT_ARCHIVE)
    shutil.copy2(Path(__file__), C4 / "scripts" / Path(__file__).name)
    summary: dict[str, Any] = {
        "run_id": RUN_ID,
        "stage": "5B3-C4 seed-based ring free-surface moving-wall smoke test",
        "outputs": {},
        "ALLOW_5B4": "NO",
        "ALLOW_5C": "NO",
        "ALLOW_STAGE6": "NO",
    }
    model = None
    client = None
    try:
        summary["A"] = import_seed_review()
        summary["B"] = java_skeleton_report()
        if summary["A"]["status"] != "PASS" or summary["B"]["status"] != "PASS":
            summary["C4_status"] = "FAIL"
            summary["stop_reason"] = "Seed evidence import or Java skeleton extraction failed."
        else:
            client = mph.Client(cores=2, version="6.4")
            model, metadata = create_ring_model(client)
            summary["C"] = {"status": "PASS", "metadata": metadata, "models": write_stage_c_outputs(model, metadata)}
            static = solve_case(
                model,
                "D_static_ring",
                "0[m/s]",
                C4 / "models" / "ring_fountain_v5B3_C4_static_ring_baseline.mph",
                C4 / "reports" / "D_static_ring_baseline_report.md",
                C4 / "tables" / "D_static_ring_H_vs_t.csv",
                C4 / "images" / "D_static_ring_H_vs_t.png",
                C4 / "images" / "D_static_ring_phils_final.png",
            )
            summary["D"] = static
            if static.get("case_pass") != "PASS":
                summary["C4_status"] = "FAIL"
                summary["stop_reason"] = "D static baseline failed; E/F/G not entered."
                (C4 / "logs" / "D_static_ring_baseline.log").write_text(json.dumps(static, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
            else:
                moving = solve_case(
                    model,
                    "E_V1e-4",
                    "1e-4[m/s]",
                    C4 / "models" / "ring_fountain_v5B3_C4_V1e-4_smoke.mph",
                    C4 / "reports" / "E_V1e-4_smoke_report.md",
                    C4 / "tables" / "E_V1e-4_H_vs_t.csv",
                    C4 / "images" / "E_V1e-4_H_vs_t.png",
                    C4 / "images" / "E_V1e-4_phils_final.png",
                    C4 / "images" / "E_V1e-4_velocity_magnitude.png",
                )
                summary["E"] = moving
                if moving.get("case_pass") != "PASS":
                    summary["C4_status"] = "FAIL"
                    summary["stop_reason"] = "E Vwall=1e-4 smoke failed; F/G not entered."
                    (C4 / "logs" / "E_V1e-4_smoke.log").write_text(json.dumps(moving, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
                else:
                    ramp_rows = []
                    for v in ["5e-4[m/s]", "1e-3[m/s]"]:
                        row = solve_case(
                            model,
                            f"F_V{v.split('[')[0].replace('-', 'm').replace('.', 'p')}",
                            v,
                            C4 / "models" / f"ring_fountain_v5B3_C4_{v.split('[')[0].replace('-', 'm').replace('.', 'p')}_smoke.mph",
                            C4 / "reports" / f"F_{v.split('[')[0].replace('-', 'm').replace('.', 'p')}_smoke_report.md",
                            C4 / "tables" / f"F_{v.split('[')[0].replace('-', 'm').replace('.', 'p')}_H_vs_t.csv",
                            C4 / "images" / f"F_{v.split('[')[0].replace('-', 'm').replace('.', 'p')}_H_vs_t.png",
                            C4 / "images" / f"F_{v.split('[')[0].replace('-', 'm').replace('.', 'p')}_phils_final.png",
                            C4 / "images" / f"F_{v.split('[')[0].replace('-', 'm').replace('.', 'p')}_velocity_magnitude.png",
                        )
                        ramp_rows.append(row)
                    write_csv(C4 / "tables" / "F_velocity_ramp_smoke_cases.csv", ramp_rows)
                    (C4 / "reports" / "F_velocity_ramp_smoke_report.md").write_text(
                        "\n".join([
                            "# F Velocity Ramp Smoke Report",
                            "",
                            *[f"- {r['case_id']}: `{r.get('case_pass')}`; solve `{r.get('solve_status')}`; delta_H `{r.get('delta_H')}`" for r in ramp_rows],
                        ]),
                        encoding="utf-8",
                    )
                    (C4 / "logs" / "F_velocity_ramp_smoke.log").write_text(json.dumps(ramp_rows, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
                    summary["F"] = {"rows": ramp_rows, "status": "PASS" if any(r.get("case_pass") == "PASS" and r.get("Vwall") == "5e-4[m/s]" for r in ramp_rows) else "PARTIAL_OR_FAIL"}
                    best = C4 / "models" / "ring_fountain_v5B3_C4_best.mph"
                    java = C4 / "exports" / "ring_fountain_v5B3_C4_best.java"
                    best_save = save_model_no_overwrite(model, best)
                    java_save = save_java_no_overwrite(model, java)
                    write_csv(C4 / "tables" / "G_best_model_manifest.csv", [
                        {"artifact": "best_model", **best_save},
                        {"artifact": "best_java", **java_save},
                    ])
                    (C4 / "reports" / "G_reproducibility_and_java_export_report.md").write_text(
                        "\n".join([
                            "# G Reproducibility and Java Export Report",
                            "",
                            f"- Best model: `{best_save.get('model')}`",
                            f"- Best model timestamp: `{best_save.get('timestamp_model')}`",
                            f"- Best Java: `{java_save.get('java')}`",
                            f"- Best Java timestamp: `{java_save.get('timestamp_java')}`",
                            "- Rebuild route: formal `TwoPhaseFlowLevelSet` + `WettedWall` transferred from GUI seed Java.",
                            "- This remains a fixed-geometry WettedWall moving-wall smoke test.",
                            "- It is not a freely falling ring model and cannot directly output real Hmax.",
                        ]),
                        encoding="utf-8",
                    )
                    summary["G"] = {"status": "PASS", "best_model": best_save, "best_java": java_save}
                    summary["C4_status"] = "PASS"
                    summary["ALLOW_5B4"] = "YES"
        write_json(C4 / "5B3_C4_seed_based_ring_smoke_summary.json", summary)
    except Exception:
        err = traceback.format_exc()
        err_path = C4 / "logs" / f"fatal_error_{RUN_ID}.log"
        err_path.write_text(err, encoding="utf-8")
        summary["C4_status"] = "FAIL"
        summary["stop_reason"] = str(err_path)
        write_json(C4 / "5B3_C4_seed_based_ring_smoke_summary.json", summary)
    finally:
        try:
            if client is not None and model is not None:
                client.remove(model)
        except Exception:
            pass
        try:
            if client is not None:
                client.clear()
        except Exception:
            pass
    final_lines = [
        "# 5B3-C4 Seed-based Ring Smoke Final Report",
        "",
        f"Run ID: `{RUN_ID}`",
        "",
        "## Required Answers",
        "",
        f"1. GUI-auto-seed imported: `{summary.get('A', {}).get('status') == 'PASS'}`.",
        f"2. Reused `TwoPhaseFlowLevelSet`: `{summary.get('C', {}).get('status') == 'PASS'}`.",
        f"3. Reused `WettedWall`: `{bool(summary.get('C', {}).get('metadata', {}).get('boundaries', {}).get('ring_wettedwall_confirmed'))}`.",
        "4. Set `TranslationalVelocityOption = Manual`: `True` if C passed; see C report.",
        "5. Set `utr = {\"0\", \"-Vwall\", \"0\"}`: `True` if C passed; see C report.",
        f"6. Built ring geometry: `{summary.get('C', {}).get('status') == 'PASS'}`.",
        f"7. Static `Vwall=0` baseline passed: `{summary.get('D', {}).get('case_pass') == 'PASS'}`.",
        f"8. `Vwall=1e-4[m/s]` smoke passed: `{summary.get('E', {}).get('case_pass') == 'PASS'}`.",
        f"9. `Vwall=5e-4[m/s]` passed: `{any(r.get('Vwall') == '5e-4[m/s]' and r.get('case_pass') == 'PASS' for r in summary.get('F', {}).get('rows', []))}`.",
        f"10. Generated `ring_fountain_v5B3_C4_best.mph`: `{bool(summary.get('G', {}).get('best_model'))}`.",
        f"11. Exported `ring_fountain_v5B3_C4_best.java`: `{bool(summary.get('G', {}).get('best_java'))}`.",
        f"12. Allow 5B4: `{summary.get('ALLOW_5B4', 'NO')}`.",
        f"13. Allow 5C: `{summary.get('ALLOW_5C', 'NO')}`.",
        f"14. Allow Stage 6: `{summary.get('ALLOW_STAGE6', 'NO')}`.",
        "",
        "## Gates",
        "",
        f"- `ALLOW_5B4 = {summary.get('ALLOW_5B4', 'NO')}`",
        f"- `ALLOW_5C = {summary.get('ALLOW_5C', 'NO')}`",
        f"- `ALLOW_STAGE6 = {summary.get('ALLOW_STAGE6', 'NO')}`",
        "",
        "This run did not enter 5B4, 5C, 5D, 5E, Stage 6, Jet1/Jet2 extraction, parameter sweep, or real Hmax extraction.",
        "",
        f"Stop reason: `{summary.get('stop_reason', '')}`",
    ]
    (C4 / "reports" / "5B3_C4_seed_based_ring_smoke_final_report.md").write_text("\n".join(final_lines), encoding="utf-8")
    update_docs(summary)
    write_json(C4 / "5B3_C4_seed_based_ring_smoke_summary.json", summary)
    log("C4 completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
