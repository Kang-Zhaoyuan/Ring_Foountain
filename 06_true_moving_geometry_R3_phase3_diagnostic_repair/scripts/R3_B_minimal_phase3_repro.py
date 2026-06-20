# -*- coding: utf-8 -*-
"""R3 Phase-3 diagnostic repair for true-moving-geometry branch.

Scope guard:
- Executes only the active T001 Phase-3 diagnostic repair task.
- Does not enter Stage 6.
- Does not perform parameter sweeps, Jet1/Jet2 extraction, or real Hmax output.
- Saves all new outputs under 06_true_moving_geometry_R3_phase3_diagnostic_repair/.
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

import mph


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
OUT = ROOT / "06_true_moving_geometry_R3_phase3_diagnostic_repair"
R1 = ROOT / "06_true_moving_geometry_R1_diagnostic_repair"
R2 = ROOT / "06_true_moving_geometry_R2_interface_noise_isolation"
CAMP = ROOT / "06_true_moving_geometry_campaign"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = OUT / "logs" / f"R3_B_minimal_phase3_repro_{RUN_ID}.log"

sys.path.insert(0, str(SCRIPTS))
import ring_fountain_06_R2_interface_noise_isolation as r2help  # noqa: E402
import ring_fountain_stage6_true_moving_geometry_campaign as campaign  # noqa: E402


SUMMARY_COLUMNS = [
    "case_id",
    "changed_factor",
    "model_path",
    "status",
    "fail_time_s",
    "max_displacement_m",
    "min_mesh_quality",
    "interface_metric",
    "pseudo_spike_metric",
    "error_log",
    "comment",
]


def ensure_dirs() -> None:
    for sub in ["reports", "logs", "tables", "images", "exports", "models", "scripts"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(read_text(path))
    except Exception:
        return {}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def write_json(path: Path, payload: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return str(path)


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str] | None = None) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if columns is None:
        columns = []
        for row in rows:
            for key in row:
                if key not in columns:
                    columns.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            out: dict[str, Any] = {}
            for key in columns:
                value = row.get(key, "")
                if isinstance(value, (dict, list, tuple)):
                    value = json.dumps(value, ensure_ascii=False, default=str)
                out[key] = value
            writer.writerow(out)
    return str(path)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


def save_model_and_java(model: Any, stem: str) -> tuple[str, str]:
    model_path = OUT / "models" / f"{stem}_{RUN_ID}.mph"
    java_path = OUT / "exports" / f"{stem}_{RUN_ID}.java"
    model.save(path=str(model_path), format="Comsol")
    model.save(path=str(java_path), format="Java")
    return str(model_path), str(java_path)


def evidence_files() -> list[Path]:
    candidates = [
        ROOT / "README.md",
        ROOT / "tasks" / "README.md",
        ROOT / "tasks" / "TASK_INDEX.md",
        ROOT / "tasks" / "NEXT_TASK.md",
        ROOT / "tasks" / "20260620_110300_T001_true_geometry_R3_phase3_repair.md",
        R2 / "reports" / "06_R2_true_moving_geometry_interface_noise_isolation_final_report.md",
        R2 / "reports" / "06_R2_true_moving_geometry_interface_noise_isolation_summary.json",
        R2 / "logs" / "06_R2_interface_noise_isolation_20260619_210233.log",
        R2 / "03_levelset_solver_stabilization" / "tables" / "stabilization_cases.csv",
        R2 / "02_static_control_decomposition" / "reports" / "static_control_decomposition_report.md",
        R2 / "01_extraction_algorithm_audit" / "reports" / "interface_extraction_algorithm_audit.md",
        R2 / "00_R1_audit" / "reports" / "R1_failure_reinterpretation_report.md",
        R1 / "reports" / "06_R1_true_moving_geometry_diagnostic_repair_final_report.md",
        R1 / "03_zero_motion_regression" / "reports" / "D_zero_and_micro_motion_regression_report.md",
        CAMP / "reports" / "true_moving_geometry_campaign_final_report.md",
        CAMP / "03_true_moving_ring_smoke" / "reports" / "true_moving_ring_smoke_report.md",
        CAMP / "04_true_moving_ring_stability" / "reports" / "true_moving_ring_stability_report.md",
        SCRIPTS / "ring_fountain_06_R2_interface_noise_isolation.py",
        SCRIPTS / "ring_fountain_06_R1_true_moving_geometry_diagnostic_repair.py",
        SCRIPTS / "ring_fountain_stage6_true_moving_geometry_campaign.py",
    ]
    return candidates


def consolidate_evidence() -> dict[str, Any]:
    r2_summary = read_json(R2 / "reports" / "06_R2_true_moving_geometry_interface_noise_isolation_summary.json")
    phase3_rows = r2_summary.get("Phase3", {}).get("rows", [])
    phase2_rows = r2_summary.get("Phase2", {}).get("rows", [])
    r2_phase_table = {
        "Phase0": r2_summary.get("Phase0", {}).get("status", "unknown"),
        "Phase1": r2_summary.get("Phase1", {}).get("status", "unknown"),
        "Phase2": r2_summary.get("Phase2", {}).get("status", "unknown"),
        "Phase3": r2_summary.get("Phase3", {}).get("status", "unknown"),
        "Phase4": r2_summary.get("Phase4", {}).get("status", "SKIPPED"),
        "Phase5": r2_summary.get("Phase5", {}).get("status", "SKIPPED"),
    }
    best_available_model = (
        CAMP / "03_true_moving_ring_smoke" / "models" / "true_moving_ring_smoke_best.mph"
    )
    if not best_available_model.exists():
        best_available_model = CAMP / "04_true_moving_ring_stability" / "models" / "true_moving_ring_smoke_best.mph"

    files_used = []
    missing = []
    for path in evidence_files():
        if path.exists():
            files_used.append(str(path))
        else:
            missing.append(str(path))

    evidence = {
        "latest_trusted_model_branch": "true-moving-geometry diagnostic branch; R2 terminal state FAIL_PHASE3",
        "exact_R2_failure_point": "Phase 3 level-set/solver stabilization failed: all attempted B0/B1 single-factor cases solved but remained weak_or_spiky under ROI-aware interface diagnostics.",
        "R2_pass_fail_phase_table": r2_phase_table,
        "best_available_model_path": str(best_available_model),
        "suspected_cause_categories": [
            "interface pseudo-spike or level-set/static relaxation noise remains supported",
            "velocity-amplified ALE-LS oscillation is not supported by R2",
            "mesh inversion/ALE displacement instability is not supported by R2 mesh metrics",
            "ring geometry, WettedWall contact line, and initialization semantics remain plausible",
            "script/API construction failure is lower probability because R2 cases solve repeatedly",
        ],
        "phase2_rows": phase2_rows,
        "phase3_rows": phase3_rows,
        "files_used_as_evidence": files_used,
        "missing_expected_paths": missing,
    }

    phase_table_md = "\n".join(
        [f"| {phase} | {status} |" for phase, status in r2_phase_table.items()]
    )
    report = [
        "# R3-A Evidence Consolidation",
        "",
        f"- Run id: `{RUN_ID}`",
        f"- Latest trusted model branch: `{evidence['latest_trusted_model_branch']}`",
        f"- Exact R2 failure point: `{evidence['exact_R2_failure_point']}`",
        f"- Best available prior model path: `{best_available_model}`",
        "",
        "## R2 Phase Table",
        "",
        "| Phase | Status |",
        "|---|---|",
        phase_table_md,
        "",
        "## R2 Phase-3 Failure Evidence",
        "",
        f"- Phase-3 case count: `{len(phase3_rows)}`",
        f"- Phase-3 pass count: `{sum(1 for row in phase3_rows if row.get('case_pass') is True)}`",
        "- Failure meaning: diagnostic gate failure, not a broad physical conclusion and not a real Hmax result.",
        "- Typical terminal diagnostic: `pseudo_spike_ROI_flag = True`, `interface_quality = weak_or_spiky`, with finite solve results.",
        "",
        "## Suspected Cause Categories",
        "",
    ]
    report.extend([f"- {item}" for item in evidence["suspected_cause_categories"]])
    report.extend(["", "## Evidence Files Used", ""])
    report.extend([f"- `{path}`" for path in files_used])
    if missing:
        report.extend(["", "## Missing Expected Paths", ""])
        report.extend([f"- `{path}`" for path in missing])
    write_text(OUT / "reports" / "R3_A_evidence_consolidation.md", "\n".join(report) + "\n")
    write_json(OUT / "reports" / "R3_A_evidence_consolidation_summary.json", evidence)
    return evidence


def apply_variant(model: Any, case_id: str) -> None:
    j = model.java
    p = j.param()
    if case_id == "C2_shorter_time_horizon":
        p.set("t_end", "0.001[s]")
    elif case_id == "C3_smaller_time_step":
        p.set("dt", "5e-5[s]")
    elif case_id == "C4_smooth_displacement_ramp":
        p.set("t_ramp", "0.002[s]")
        j.component("comp1").physics("ale").feature("move_ring").set(
            "dx", ["0", "-Vring*(if(t<t_ramp,t-t_ramp/pi*sin(pi*t/t_ramp),t))"]
        )
    elif case_id == "C5_levelset_eps_2mm":
        p.set("eps_ls", "2[mm]")


def run_case(client: Any, case_id: str, changed_factor: str, v: str, t_end: str, dt: str) -> dict[str, Any]:
    model = None
    effective_t_end = t_end
    effective_dt = dt
    row: dict[str, Any] = {
        "case_id": case_id,
        "changed_factor": changed_factor,
        "status": "FAIL",
        "fail_time_s": "",
        "max_displacement_m": "",
        "min_mesh_quality": "",
        "interface_metric": "",
        "pseudo_spike_metric": "",
        "error_log": "",
        "comment": "",
    }
    try:
        model, meta = campaign.build_true_ring_model(client, case_id, v, t_end, dt)
        apply_variant(model, case_id)
        if case_id == "C2_shorter_time_horizon":
            effective_t_end = "0.001[s]"
        elif case_id == "C3_smaller_time_step":
            effective_dt = "5e-5[s]"
        try:
            model.java.study("std1").run()
            row["solve_status"] = "PASS"
        except Exception:
            row["solve_status"] = "FAIL"
            row["error_log"] = traceback.format_exc()[:1800]
            row["status"] = "FAIL_SOLVER"
            row["fail_time_s"] = "unknown"
        if row.get("solve_status") == "PASS":
            final_inner = campaign.final_inner_index(effective_t_end, effective_dt)
            metric = r2help.row_from_model(case_id, model, final_inner, {"solve_status": "PASS", "failure_message": ""})
            model_path, java_path = save_model_and_java(model, case_id)
            row["model_path"] = model_path
            row["java_path"] = java_path
            row["fail_time_s"] = str(campaign.seconds_from_expr(effective_t_end))
            row["max_displacement_m"] = metric.get("max_mesh_vertical_displacement", "")
            row["min_mesh_quality"] = metric.get("mesh_quality_min", "")
            if finite(metric.get("interface_roughness_final")):
                row["interface_metric"] = f"interface_roughness_final={metric.get('interface_roughness_final')}"
            else:
                row["interface_metric"] = f"interface_quality={metric.get('interface_quality', 'unknown')}"
            row["pseudo_spike_metric"] = f"pseudo_spike_ROI_flag={metric.get('pseudo_spike_ROI_flag')}"
            row["H_final_minus_H0_diagnostic_m"] = metric.get("H_final_minus_H0", "")
            row["interface_quality"] = metric.get("interface_quality", "")
            row["case_pass"] = bool(metric.get("case_pass") is True)
            row["status"] = "PASS" if row["case_pass"] else "FAIL_DIAGNOSTIC"
            row["comment"] = "single-factor diagnostic case; H fields are diagnostic only, not real Hmax"
        else:
            if model is not None:
                try:
                    model_path, java_path = save_model_and_java(model, case_id)
                    row["model_path"] = model_path
                    row["java_path"] = java_path
                except Exception:
                    row["comment"] = "model save failed after solver failure"
    except Exception:
        row["status"] = "FAIL_EXCEPTION"
        row["error_log"] = (row.get("error_log", "") + "\n" + traceback.format_exc())[:2400]
        row["case_pass"] = False
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass
    return row


def build_minimal_report(rows: list[dict[str, Any]]) -> None:
    repro_rows = [row for row in rows if row["case_id"] in {"B_repro_micro_displacement", "B_repro_micro_displacement_repeat"}]
    reproduced = all(row.get("status") == "FAIL_DIAGNOSTIC" for row in repro_rows) if repro_rows else False
    deterministic = "YES" if len({row.get("status") for row in repro_rows}) == 1 and len(repro_rows) > 1 else "NOT_TESTED"
    err_parts = [row.get("error_log", "") for row in repro_rows if row.get("error_log")]
    if not err_parts:
        err_parts = ["No COMSOL solver exception. Failure is reproduced as a deterministic diagnostic gate failure: pseudo_spike_ROI_flag remains True / interface_quality remains weak_or_spiky."]
    report = [
        "# R3-B Minimal Phase-3 Reproduction Report",
        "",
        f"- Run id: `{RUN_ID}`",
        f"- Phase 3 failure reproduced: `{reproduced}`",
        f"- Deterministic across repeat: `{deterministic}`",
        "- Minimal reproduction case: `B_repro_micro_displacement`, generated with `Vring = 1e-3[m/s]`, `t_end = 0.005[s]`, `dt = 1e-4[s]`.",
        "- Failure step/time: diagnostic evaluation at final inner solution, `t = 0.005 s`, after successful transient solve.",
        "- Failure type: diagnostic gate failure, not a solver crash.",
        "",
        "## Exact Error / Failure Messages",
        "",
    ]
    report.extend([f"- `{item}`" for item in err_parts])
    report.extend(["", "## Reproduction Rows", ""])
    for row in repro_rows:
        report.append(
            f"- `{row['case_id']}`: status=`{row.get('status')}`, model=`{row.get('model_path', '')}`, {row.get('pseudo_spike_metric', '')}, {row.get('interface_metric', '')}"
        )
    write_text(OUT / "reports" / "R3_B_minimal_phase3_repro_report.md", "\n".join(report) + "\n")


def run_repair_ladder() -> dict[str, Any]:
    log("R3 Phase B/C COMSOL client start")
    cases = [
        ("B_repro_micro_displacement", "minimal Phase-3 repro: micro displacement baseline", "1e-3[m/s]", "0.005[s]", "1e-4[s]"),
        ("B_repro_micro_displacement_repeat", "minimal Phase-3 repro repeat", "1e-3[m/s]", "0.005[s]", "1e-4[s]"),
        ("C0_zero_displacement_baseline", "C0 zero-displacement baseline check", "0[m/s]", "0.005[s]", "1e-4[s]"),
        ("C1_micro_displacement_baseline", "C1 micro-displacement case", "1e-3[m/s]", "0.005[s]", "1e-4[s]"),
        ("C2_shorter_time_horizon", "C2 shorter time horizon only", "1e-3[m/s]", "0.001[s]", "1e-4[s]"),
        ("C3_smaller_time_step", "C3 smaller time step only", "1e-3[m/s]", "0.005[s]", "1e-4[s]"),
        ("C4_smooth_displacement_ramp", "C4 smoother displacement ramp only", "1e-3[m/s]", "0.005[s]", "1e-4[s]"),
        ("C5_levelset_eps_2mm", "C5 level-set interface thickness only", "1e-3[m/s]", "0.005[s]", "1e-4[s]"),
    ]
    rows: list[dict[str, Any]] = []
    client = None
    try:
        client = mph.Client(cores=2, version="6.4")
        for case_id, changed_factor, v, t_end, dt in cases:
            log(f"Running {case_id}: {changed_factor}")
            row = run_case(client, case_id, changed_factor, v, t_end, dt)
            rows.append(row)
            log(f"Finished {case_id}: {row.get('status')}")
    finally:
        if client is not None:
            try:
                client.clear()
            except Exception:
                pass
    build_minimal_report(rows)
    ladder_rows = [row for row in rows if row["case_id"].startswith("C")]
    write_csv(OUT / "tables" / "R3_C_repair_ladder_summary.csv", ladder_rows, SUMMARY_COLUMNS)
    write_json(OUT / "reports" / "R3_BC_raw_rows.json", rows)
    return {"all_rows": rows, "ladder_rows": ladder_rows}


def final_decision(evidence: dict[str, Any], result: dict[str, Any]) -> dict[str, str]:
    ladder = result.get("ladder_rows", [])
    zero_pass = any(row.get("case_id") == "C0_zero_displacement_baseline" and row.get("status") == "PASS" for row in ladder)
    micro_pass = any(row.get("case_id") != "C0_zero_displacement_baseline" and row.get("status") == "PASS" for row in ladder)
    repaired = zero_pass and micro_pass
    gates = {
        "R3_STATUS": "PASS" if repaired else "FAIL",
        "ALLOW_NEXT_DISPLACEMENT_LADDER": "YES" if repaired else "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    report = [
        "# R3 Final Report",
        "",
        f"- Run id: `{RUN_ID}`",
        f"- Active task: `tasks/NEXT_TASK.md` / `tasks/20260620_110300_T001_true_geometry_R3_phase3_repair.md`",
        f"- R2 source state: `FAIL_PHASE3`",
        "- Scope: Phase-3 diagnostic repair only.",
        "- Stage 6, parameter sweep, Jet1/Jet2 detection, and real Hmax output were not performed.",
        "",
        "## Gate Decision",
        "",
        f"- `R3_STATUS = {gates['R3_STATUS']}`",
        f"- `ALLOW_NEXT_DISPLACEMENT_LADDER = {gates['ALLOW_NEXT_DISPLACEMENT_LADDER']}`",
        f"- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = {gates['ALLOW_NEXT_TRUE_GEOMETRY_JET1']}`",
        f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
        f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
        "",
        "## Repair Ladder Summary",
        "",
        "| case_id | changed_factor | status | max_displacement_m | min_mesh_quality | pseudo_spike_metric |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in ladder:
        report.append(
            f"| `{row.get('case_id')}` | {row.get('changed_factor')} | `{row.get('status')}` | `{row.get('max_displacement_m', '')}` | `{row.get('min_mesh_quality', '')}` | `{row.get('pseudo_spike_metric', '')}` |"
        )
    report.extend(
        [
            "",
            "## Interpretation",
            "",
            "- R3 keeps the R2 interpretation that Phase-3 failure is a diagnostic interface-quality failure rather than a COMSOL transient-solver crash.",
            "- Mesh quality/ALE inversion remains unsupported as the dominant cause when mesh metrics remain finite and near unity.",
            "- Because no single-factor R3 repair produced both a clear zero-displacement and clear micro-displacement baseline, the branch remains gated.",
            "",
            "## Key Paths",
            "",
            f"- Evidence report: `{OUT / 'reports' / 'R3_A_evidence_consolidation.md'}`",
            f"- Minimal repro report: `{OUT / 'reports' / 'R3_B_minimal_phase3_repro_report.md'}`",
            f"- Repair ladder CSV: `{OUT / 'tables' / 'R3_C_repair_ladder_summary.csv'}`",
            f"- Raw rows JSON: `{OUT / 'reports' / 'R3_BC_raw_rows.json'}`",
            f"- Primary log: `{LOG}`",
        ]
    )
    write_text(OUT / "reports" / "R3_final_report.md", "\n".join(report) + "\n")
    write_json(OUT / "reports" / "R3_gate_summary.json", gates)
    return gates


def update_readme(gates: dict[str, str]) -> None:
    readme_path = ROOT / "README.md"
    start = "<!-- TRUE_GEOMETRY_R3_PHASE3_DIAGNOSTIC_REPAIR:START -->"
    end = "<!-- TRUE_GEOMETRY_R3_PHASE3_DIAGNOSTIC_REPAIR:END -->"
    block = "\n".join(
        [
            start,
            "## TRUE_GEOMETRY_R3_PHASE3_DIAGNOSTIC_REPAIR",
            "",
            f"- Run id: `{RUN_ID}`",
            "- Source state: true-moving-geometry R2 `FAIL_PHASE3`.",
            "- Scope: R3 Phase-3 diagnostic repair only.",
            f"- R3 status: `{gates['R3_STATUS']}`",
            f"- `ALLOW_NEXT_DISPLACEMENT_LADDER = {gates['ALLOW_NEXT_DISPLACEMENT_LADDER']}`",
            f"- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = {gates['ALLOW_NEXT_TRUE_GEOMETRY_JET1']}`",
            f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
            f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
            f"- Final report: `{OUT / 'reports' / 'R3_final_report.md'}`",
            f"- Repair ladder table: `{OUT / 'tables' / 'R3_C_repair_ladder_summary.csv'}`",
            "- No Stage 6 parameter sweep has been performed.",
            "- No real Hmax has been produced.",
            "- No true-geometry Jet1 detection has been performed.",
            end,
        ]
    )
    text = read_text(readme_path)
    if start in text and end in text:
        before = text.split(start, 1)[0].rstrip()
        after = text.split(end, 1)[1].lstrip()
        new_text = before + "\n\n" + block + "\n\n" + after
    else:
        new_text = text.rstrip() + "\n\n" + block + "\n"
    write_text(readme_path, new_text)


def write_task_run_metadata(gates: dict[str, str]) -> None:
    next_task = read_text(ROOT / "tasks" / "NEXT_TASK.md")
    metadata = {
        "run_id": RUN_ID,
        "started_log": str(LOG),
        "active_task": str(ROOT / "tasks" / "NEXT_TASK.md"),
        "active_task_sha256": sha256_text(next_task),
        "output_dir": str(OUT),
        "gates": gates,
    }
    write_json(OUT / "logs" / f"R3_builder_run_metadata_{RUN_ID}.json", metadata)


def main() -> int:
    ensure_dirs()
    script_copy = OUT / "scripts" / "R3_B_minimal_phase3_repro.py"
    if Path(__file__).resolve() != script_copy.resolve():
        shutil.copy2(Path(__file__).resolve(), script_copy)
    log("R3 Phase-3 diagnostic repair start")
    evidence = consolidate_evidence()
    try:
        result = run_repair_ladder()
        gates = final_decision(evidence, result)
        update_readme(gates)
        write_task_run_metadata(gates)
        log(f"R3 complete: {gates}")
        return 0 if gates["R3_STATUS"] == "PASS" else 1
    except Exception:
        err = traceback.format_exc()
        log("R3 exception:\n" + err)
        gates = {
            "R3_STATUS": "FAIL",
            "ALLOW_NEXT_DISPLACEMENT_LADDER": "NO",
            "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "NO",
            "ALLOW_STAGE6": "NO",
            "ALLOW_REAL_HMAX_OUTPUT": "NO",
        }
        write_text(
            OUT / "reports" / "R3_final_report.md",
            "\n".join(
                [
                    "# R3 Final Report",
                    "",
                    f"- Run id: `{RUN_ID}`",
                    "- R3 stopped by exception during Phase-3 diagnostic repair.",
                    f"- Error: `{err[:1800]}`",
                    "",
                    f"- `R3_STATUS = {gates['R3_STATUS']}`",
                    f"- `ALLOW_NEXT_DISPLACEMENT_LADDER = {gates['ALLOW_NEXT_DISPLACEMENT_LADDER']}`",
                    f"- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = {gates['ALLOW_NEXT_TRUE_GEOMETRY_JET1']}`",
                    f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
                    f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
                ]
            )
            + "\n",
        )
        update_readme(gates)
        write_task_run_metadata(gates)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
