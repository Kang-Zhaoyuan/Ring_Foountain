# -*- coding: utf-8 -*-
"""T006 finish remaining contact-angle/slip raw-array extraction.

Continuation-only task: load saved .mph models for W2/W3/W4/W7/W8, export
compact arrays, and recompute bounded postprocessing metrics. No studies,
Stage 6, Jet1/Jet2 detection, parameter sweeps, or real Hmax output.
"""

from __future__ import annotations

import csv
import json
import math
import os
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import mph


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
OUT = ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute"
SCRIPT_DIR = OUT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

sys.path.insert(0, str(SCRIPT_DIR))
import T005_continue_raw_array_extraction as t5  # noqa: E402


T006_PRIORITY = [
    ("W2_contact_angle_60deg", ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation" / "04_wettedwall_contactline_controls" / "models" / "W2_contact_angle_60deg.mph"),
    ("W3_contact_angle_120deg", ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation" / "04_wettedwall_contactline_controls" / "models" / "W3_contact_angle_120deg.mph"),
    ("W4_contact_angle_150deg", ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation" / "04_wettedwall_contactline_controls" / "models" / "W4_contact_angle_150deg.mph"),
    ("W7_user_defined_slip_0p1mm", ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation" / "04_wettedwall_contactline_controls" / "models" / "W7_user_defined_slip_0p1mm.mph"),
    ("W8_user_defined_slip_0p5mm", ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation" / "04_wettedwall_contactline_controls" / "models" / "W8_user_defined_slip_0p5mm.mph"),
]


def ensure_dirs() -> None:
    for sub in ["reports", "tables", "images", "logs", "arrays", "scripts"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)


def abspath(path: Path) -> str:
    return str(path.resolve())


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(row.get(key), ensure_ascii=False, default=str) if isinstance(row.get(key), (dict, list, tuple)) else row.get(key, "") for key in columns})
    return abspath(path)


def append_csv(path: Path, row: dict[str, Any], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        if not exists:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in columns})


def write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return abspath(path)


def write_json(path: Path, payload: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return abspath(path)


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


def latest_rows_by_case(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    latest = {}
    for row in rows:
        case_id = row.get("case_id", "")
        if case_id:
            latest[case_id] = row
    return latest


def progress_columns() -> list[str]:
    return [
        "case_id",
        "priority",
        "model_path",
        "model_exists",
        "previous_t005_status",
        "attempted_t006",
        "extraction_status",
        "postprocess_status",
        "output_array_path",
        "notes",
    ]


def metric_columns() -> list[str]:
    return t5.metric_columns()


def previous_t005_status_by_case() -> dict[str, str]:
    status = {}
    for row in read_csv(OUT / "tables" / "T005_case_manifest.csv"):
        status[row.get("case_id", "")] = f"{row.get('extraction_status', '')}/{row.get('postprocess_status', '')}"
    for row in read_csv(OUT / "tables" / "T005_recomputed_metrics.csv"):
        status[row.get("case_id", "")] = f"{row.get('extraction_status', '')}/{row.get('postprocess_status', '')}"
    return status


def latest_t006_array_path(priority: int, case_id: str) -> Path:
    matches = sorted((OUT / "arrays").glob(f"T006_{priority:02d}_{case_id}_*.npz"))
    return matches[-1] if matches else OUT / "arrays" / f"T006_{priority:02d}_{case_id}_{RUN_ID}.npz"


def per_case_log(case_id: str, text: str) -> None:
    path = OUT / "logs" / f"T006_{case_id}_{RUN_ID}.log"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text + "\n")


def patch_t005_runtime() -> None:
    t5.latest_t005_array_path = latest_t006_array_path
    t5.per_case_log = per_case_log


def build_manifest() -> list[dict[str, Any]]:
    previous = previous_t005_status_by_case()
    progress = latest_rows_by_case(read_csv(OUT / "tables" / "T006_progress.csv"))
    rows = []
    for idx, (case_id, model_path) in enumerate(T006_PRIORITY, start=1):
        prev = progress.get(case_id, {})
        rows.append(
            {
                "case_id": case_id,
                "priority": idx,
                "model_path": abspath(model_path),
                "model_exists": "YES" if model_path.exists() else "NO",
                "previous_t005_status": previous.get(case_id, "NOT_ATTEMPTED/NOT_ATTEMPTED"),
                "attempted_t006": prev.get("attempted_t006", "NO"),
                "extraction_status": prev.get("extraction_status", "NOT_ATTEMPTED"),
                "postprocess_status": prev.get("postprocess_status", "NOT_ATTEMPTED"),
                "output_array_path": prev.get("output_array_path", ""),
                "notes": prev.get("notes", ""),
            }
        )
    return rows


def remaining_case_plan() -> None:
    write_csv(OUT / "tables" / "T006_case_manifest.csv", build_manifest(), progress_columns())
    lines = [
        "# T006-A Remaining Case Plan",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: finish W2/W3/W4/W7/W8 raw-array extraction/recompute only.",
        "- No COMSOL study, Stage 6, parameter sweep, Jet1/Jet2 detection, or real Hmax output is performed.",
        "- New artifacts use `T006_*` filenames and do not overwrite T004/T005 arrays/logs/tables.",
        f"- Default case budget: `{os.environ.get('T006_MAX_CASES', '5')}` remaining cases.",
        "",
        "## Remaining Contact-Angle/Slip Priority Order",
        "",
    ]
    previous = previous_t005_status_by_case()
    for idx, (case_id, model_path) in enumerate(T006_PRIORITY, start=1):
        lines.append(f"{idx}. `{case_id}` -> `{model_path}` exists=`{model_path.exists()}` previous_t005=`{previous.get(case_id, 'NOT_ATTEMPTED/NOT_ATTEMPTED')}`")
    write_text(OUT / "reports" / "T006_A_remaining_case_plan.md", "\n".join(lines) + "\n")


def render_figures(metrics: list[dict[str, str]], merged: list[dict[str, Any]]) -> None:
    status_counts = Counter(row.get("extraction_status", "") for row in metrics)
    t5.render_bars(OUT / "images" / "T006_extraction_status_summary.png", list(status_counts.keys()), [float(v) for v in status_counts.values()], "T006 extraction status summary")
    quality_counts = Counter(row.get("interface_quality", "") for row in metrics)
    t5.render_bars(OUT / "images" / "T006_interface_quality_summary.png", list(quality_counts.keys()), [float(v) for v in quality_counts.values()], "T006 interface quality summary")
    labels = [str(row.get("case_id", "")) for row in merged]
    values = [float(row.get("regional_roughness", "nan")) * 1e6 if finite(row.get("regional_roughness")) else math.nan for row in merged]
    t5.render_bars(OUT / "images" / "T006_baseline_discrimination_summary.png", labels, values, "T006 merged baseline-discrimination roughness (um)")


def status_for_case(rows: dict[str, dict[str, str]], case_id: str) -> str:
    row = rows.get(case_id)
    if not row:
        return "NOT_ATTEMPTED"
    if row.get("postprocess_status") == "PASS" and row.get("case_pass_after_recompute") == "True":
        return "PASS"
    if row.get("extraction_status") or row.get("postprocess_status"):
        return "FAIL"
    return "UNKNOWN"


def merged_metrics(t006_metrics: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in read_csv(OUT / "tables" / "T005_merged_T004_T005_metrics.csv"):
        rows.append(dict(row))
    t006_latest = latest_rows_by_case(t006_metrics)
    for case_id, _ in T006_PRIORITY:
        if case_id in t006_latest:
            row = dict(t006_latest[case_id])
            row["source_task"] = "T006"
            rows.append(row)
    write_csv(OUT / "tables" / "T006_merged_T004_T005_T006_metrics.csv", rows, ["source_task"] + metric_columns())
    return rows


def final_report(metrics: list[dict[str, str]], merged: list[dict[str, Any]]) -> dict[str, str]:
    latest = latest_rows_by_case(metrics)
    attempted = len(metrics)
    extraction_pass = sum(1 for row in metrics if row.get("extraction_status") == "PASS")
    post_pass = sum(1 for row in metrics if row.get("postprocess_status") == "PASS")
    raw_status = "YES" if extraction_pass == len(T006_PRIORITY) else "PARTIAL" if extraction_pass else "NO"
    mem_status = "YES" if post_pass == attempted and attempted > 0 else "PARTIAL" if post_pass else "NO"
    iq_status = "YES" if post_pass == attempted and attempted > 0 else "PARTIAL" if post_pass else "NO"
    t006_status = "PASS" if raw_status == "YES" and post_pass == len(T006_PRIORITY) else "PARTIAL" if attempted else "FAIL"
    gates = {
        "T006_STATUS": t006_status,
        "RAW_ARRAY_EXTRACTION_COMPLETED_REMAINING_CASES": raw_status,
        "POSTPROCESSING_MEMORY_ERROR_RESOLVED_REMAINING_CASES": mem_status,
        "INTERFACE_QUALITY_EXTRACTION_REPAIRED_REMAINING_CASES": iq_status,
        "W2_CONTACT_ANGLE_60_STATUS": status_for_case(latest, "W2_contact_angle_60deg"),
        "W3_CONTACT_ANGLE_120_STATUS": status_for_case(latest, "W3_contact_angle_120deg"),
        "W4_CONTACT_ANGLE_150_STATUS": status_for_case(latest, "W4_contact_angle_150deg"),
        "W7_SLIP_0P1MM_STATUS": status_for_case(latest, "W7_user_defined_slip_0p1mm"),
        "W8_SLIP_0P5MM_STATUS": status_for_case(latest, "W8_user_defined_slip_0p5mm"),
        "CREDIBLE_STATIC_BASELINE_AFTER_T006": "UNKNOWN" if extraction_pass == len(T006_PRIORITY) else "NO",
        "CREDIBLE_MICRO_MOTION_BASELINE_AFTER_T006": "UNKNOWN",
        "ALLOW_NEXT_DISPLACEMENT_LADDER": "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    lines = [
        "# T006 Final Report",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: finish remaining contact-angle/slip raw-array extraction and postprocessing recompute.",
        "- No COMSOL study, Stage 6, parameter sweep, Jet1/Jet2 detection, or real Hmax output was performed.",
        "",
        "## Gate Values",
        "",
    ]
    lines.extend([f"- `{key} = {value}`" for key, value in gates.items()])
    lines.extend(
        [
            "",
            "## T006 Case Results",
            "",
            f"- Attempted T006 cases: `{attempted}`",
            f"- Extraction PASS cases: `{extraction_pass}`",
            f"- Postprocess PASS cases: `{post_pass}`",
            "",
            "| case_id | extraction_status | postprocess_status | interface_quality | memory_error_resolved | array_path |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in metrics:
        lines.append(f"| `{row.get('case_id')}` | `{row.get('extraction_status')}` | `{row.get('postprocess_status')}` | `{row.get('interface_quality', '')}` | `{row.get('memory_error_resolved', '')}` | `{row.get('array_path', '')}` |")
    lines.extend(
        [
            "",
            "## Merged Evidence",
            "",
            f"- Merged T004/T005/T006 metrics table: `{OUT / 'tables' / 'T006_merged_T004_T005_T006_metrics.csv'}`",
            f"- Merged rows available: `{len(merged)}`",
            "",
            "## Next Recommended Task",
            "",
            "- Review the completed raw-array extraction/recompute package and decide whether a diagnostic displacement ladder is justified. Stage 6, Jet1, and real Hmax remain blocked.",
        ]
    )
    write_text(OUT / "reports" / "T006_final_report.md", "\n".join(lines) + "\n")
    write_json(OUT / "reports" / "T006_gate_summary.json", gates)
    return gates


def update_readme(gates: dict[str, str], attempted: int) -> None:
    readme = ROOT / "README.md"
    start = "<!-- TRUE_GEOMETRY_R3_RAW_ARRAY_EXTRACTION_RECOMPUTE:START -->"
    end = "<!-- TRUE_GEOMETRY_R3_RAW_ARRAY_EXTRACTION_RECOMPUTE:END -->"
    block = "\n".join(
        [
            start,
            "## TRUE_GEOMETRY_R3_RAW_ARRAY_EXTRACTION_RECOMPUTE",
            "",
            f"- Latest run id: `{RUN_ID}`",
            "- Scope: raw-array extraction plus postprocessing recompute from existing saved models.",
            "- T004 completed G2/G3; T005 completed W10/W0; T006 targets W2/W3/W4/W7/W8.",
            f"- T006 attempted remaining cases: `{attempted}`",
            f"- T006 status: `{gates['T006_STATUS']}`",
            f"- `RAW_ARRAY_EXTRACTION_COMPLETED_REMAINING_CASES = {gates['RAW_ARRAY_EXTRACTION_COMPLETED_REMAINING_CASES']}`",
            f"- `POSTPROCESSING_MEMORY_ERROR_RESOLVED_REMAINING_CASES = {gates['POSTPROCESSING_MEMORY_ERROR_RESOLVED_REMAINING_CASES']}`",
            f"- `INTERFACE_QUALITY_EXTRACTION_REPAIRED_REMAINING_CASES = {gates['INTERFACE_QUALITY_EXTRACTION_REPAIRED_REMAINING_CASES']}`",
            f"- `ALLOW_NEXT_DISPLACEMENT_LADDER = {gates['ALLOW_NEXT_DISPLACEMENT_LADDER']}`",
            f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
            f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
            f"- T006 final report: `{OUT / 'reports' / 'T006_final_report.md'}`",
            f"- T006 merged metrics: `{OUT / 'tables' / 'T006_merged_T004_T005_T006_metrics.csv'}`",
            "- No Stage 6 parameter sweep has been performed.",
            "- No real Hmax has been produced.",
            "- No true-geometry Jet1 detection has been performed.",
            end,
        ]
    )
    text = readme.read_text(encoding="utf-8", errors="replace")
    if start in text and end in text:
        before = text.split(start, 1)[0].rstrip()
        after = text.split(end, 1)[1].lstrip()
        text = before + "\n\n" + block + "\n\n" + after
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    write_text(readme, text)


def update_polling_log() -> None:
    row = {
        "round_start_time": f"{RUN_ID[:4]}-{RUN_ID[4:6]}-{RUN_ID[6:8]}T{RUN_ID[9:11]}:{RUN_ID[11:13]}:{RUN_ID[13:15]}+08:00",
        "active_task": "tasks/NEXT_TASK.md",
        "active_task_archive": "tasks/20260620_153000_T006_finish_remaining_contact_angle_slip_extraction.md",
        "executed": "YES",
        "pushed": "PENDING",
        "commit_sha": "",
        "notes": "T006 executed for remaining contact-angle/slip cases; commit SHA filled after push.",
    }
    append_csv(ROOT / "tasks" / "BUILDER_POLLING_LOG.csv", row, ["round_start_time", "active_task", "active_task_archive", "executed", "pushed", "commit_sha", "notes"])


def main() -> int:
    ensure_dirs()
    script_copy = OUT / "scripts" / "T006_finish_remaining_extraction.py"
    if Path(__file__).resolve() != script_copy.resolve():
        shutil.copy2(Path(__file__).resolve(), script_copy)
    patch_t005_runtime()
    remaining_case_plan()

    max_cases = int(os.environ.get("T006_MAX_CASES", "5"))
    existing = read_csv(OUT / "tables" / "T006_recomputed_metrics.csv")
    done = {row.get("case_id") for row in existing if row.get("extraction_status") == "PASS"}
    attempted_this_run = 0
    client = mph.Client(cores=2, version="6.4")
    try:
        for priority, (case_id, model_path) in enumerate(T006_PRIORITY, start=1):
            if case_id in done:
                continue
            if attempted_this_run >= max_cases:
                break
            result = t5.process_case(client, priority, case_id, model_path)
            attempted_this_run += 1
            progress = {
                "case_id": case_id,
                "priority": priority,
                "model_path": abspath(model_path),
                "model_exists": "YES" if model_path.exists() else "NO",
                "previous_t005_status": previous_t005_status_by_case().get(case_id, ""),
                "attempted_t006": "YES",
                "extraction_status": result.get("extraction_status", ""),
                "postprocess_status": result.get("postprocess_status", ""),
                "output_array_path": result.get("array_path", ""),
                "notes": result.get("exception_message", ""),
            }
            append_csv(OUT / "tables" / "T006_progress.csv", progress, progress_columns())
            append_csv(OUT / "tables" / "T006_recomputed_metrics.csv", result, metric_columns())
            write_csv(OUT / "tables" / "T006_case_manifest.csv", build_manifest(), progress_columns())
    finally:
        try:
            client.clear()
        except Exception:
            pass

    latest = latest_rows_by_case(read_csv(OUT / "tables" / "T006_recomputed_metrics.csv"))
    metrics = [latest[case_id] for case_id, _ in T006_PRIORITY if case_id in latest]
    merged = merged_metrics(metrics)
    render_figures(metrics, merged)
    gates = final_report(metrics, merged)
    update_readme(gates, len(metrics))
    update_polling_log()
    return 0 if gates["T006_STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
