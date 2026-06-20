# -*- coding: utf-8 -*-
"""T005 continuation of R3 raw-array extraction.

This is a continuation of T004 for the remaining wetted-wall/contactline
priority cases. It loads existing saved .mph models, exports compact arrays,
and recomputes the same bounded interface metrics. It never runs a study,
Stage 6, Jet1/Jet2 detection, parameter sweeps, or real Hmax output.
"""

from __future__ import annotations

import csv
import gc
import json
import math
import os
import shutil
import sys
import traceback
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import mph
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
OUT = ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute"
SCRIPT_DIR = OUT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

sys.path.insert(0, str(SCRIPT_DIR))
import T004_raw_array_extraction_recompute as t4  # noqa: E402


REMAINING_PRIORITY = [
    ("W10_plain_wall_no_wettedwall_diagnostic", ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation" / "04_wettedwall_contactline_controls" / "models" / "W10_plain_wall_no_wettedwall_diagnostic.mph"),
    ("W0_current_wettedwall", ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation" / "04_wettedwall_contactline_controls" / "models" / "W0_current_wettedwall.mph"),
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


def t005_progress_columns() -> list[str]:
    return [
        "case_id",
        "priority",
        "model_path",
        "model_exists",
        "previous_t004_status",
        "attempted_t005",
        "extraction_status",
        "postprocess_status",
        "output_array_path",
        "notes",
    ]


def metric_columns() -> list[str]:
    return t4.metric_columns()


def previous_t004_status_by_case() -> dict[str, str]:
    status = {}
    for row in read_csv(OUT / "tables" / "T004_case_manifest.csv"):
        status[row.get("case_id", "")] = f"{row.get('extraction_status', '')}/{row.get('postprocess_status', '')}"
    return status


def latest_rows_by_case(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    latest = {}
    for row in rows:
        case_id = row.get("case_id", "")
        if case_id:
            latest[case_id] = row
    return latest


def latest_t005_array_path(priority: int, case_id: str) -> Path | None:
    matches = sorted((OUT / "arrays").glob(f"T005_{priority:02d}_{case_id}_*.npz"))
    return matches[-1] if matches else None


def per_case_log(case_id: str, text: str) -> None:
    path = OUT / "logs" / f"T005_{case_id}_{RUN_ID}.log"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text + "\n")


def build_manifest() -> list[dict[str, Any]]:
    previous = previous_t004_status_by_case()
    progress = latest_rows_by_case(read_csv(OUT / "tables" / "T005_progress.csv"))
    rows = []
    for idx, (case_id, model_path) in enumerate(REMAINING_PRIORITY, start=1):
        prev = progress.get(case_id, {})
        rows.append(
            {
                "case_id": case_id,
                "priority": idx,
                "model_path": abspath(model_path),
                "model_exists": "YES" if model_path.exists() else "NO",
                "previous_t004_status": previous.get(case_id, "NOT_IN_T004_MANIFEST"),
                "attempted_t005": prev.get("attempted_t005", "NO"),
                "extraction_status": prev.get("extraction_status", "NOT_ATTEMPTED"),
                "postprocess_status": prev.get("postprocess_status", "NOT_ATTEMPTED"),
                "output_array_path": prev.get("output_array_path", ""),
                "notes": prev.get("notes", ""),
            }
        )
    return rows


def continuation_plan() -> None:
    write_csv(OUT / "tables" / "T005_case_manifest.csv", build_manifest(), t005_progress_columns())
    lines = [
        "# T005-A Continuation Plan",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: continue T004 raw-array extraction/recompute for remaining priority cases only.",
        "- No COMSOL study, Stage 6, parameter sweep, Jet1/Jet2 detection, or real Hmax output is performed.",
        "- New artifacts use `T005_*` filenames and do not overwrite T004 arrays/logs/tables.",
        f"- Default case budget: `{os.environ.get('T005_MAX_CASES', '2')}` remaining priority cases.",
        "",
        "## Remaining Priority Order",
        "",
    ]
    for idx, (case_id, model_path) in enumerate(REMAINING_PRIORITY, start=1):
        lines.append(f"{idx}. `{case_id}` -> `{model_path}` exists=`{model_path.exists()}` previous_t004=`{previous_t004_status_by_case().get(case_id, '')}`")
    write_text(OUT / "reports" / "T005_A_continuation_plan.md", "\n".join(lines) + "\n")


def process_case(client: Any, priority: int, case_id: str, model_path: Path) -> dict[str, Any]:
    model = None
    array_path = latest_t005_array_path(priority, case_id) or (OUT / "arrays" / f"T005_{priority:02d}_{case_id}_{RUN_ID}.npz")
    per_case_log(case_id, f"start {datetime.now().isoformat(timespec='seconds')}")
    result: dict[str, Any] = {
        "case_id": case_id,
        "priority": priority,
        "model_path": abspath(model_path),
        "extraction_status": "FAILED",
        "postprocess_status": "FAILED",
        "array_path": "",
        "exception_class": "",
        "exception_message": "",
    }
    if not model_path.exists():
        result.update({"extraction_status": "MODEL_MISSING", "postprocess_status": "SKIPPED", "exception_message": "model path missing"})
        per_case_log(case_id, "model_missing")
        return result
    try:
        if not array_path.exists():
            model = client.load(str(model_path))
            per_case_log(case_id, "model_loaded")
            t0 = t4.t3.scalar_time(model, 1)
            tf = t4.t3.scalar_time(model, 51)
            r0 = t4.t3.eval_array(model, "r", "m", 1)
            z0 = t4.t3.eval_array(model, "z", "m", 1)
            p0 = t4.t3.eval_array(model, "phils", "", 1)
            rf = t4.t3.eval_array(model, "r", "m", 51)
            zf = t4.t3.eval_array(model, "z", "m", 51)
            pf = t4.t3.eval_array(model, "phils", "", 51)
            per_case_log(case_id, "arrays_evaluated")
            r0s, z0s, p0s, n0, u0, m0 = t4.sample_array_triplet(r0, z0, p0)
            rfs, zfs, pfs, nf, uf, mf = t4.sample_array_triplet(rf, zf, pf)
            np.savez_compressed(array_path, r0=r0s, z0=z0s, phils0=p0s, rf=rfs, zf=zfs, philsf=pfs, t0=np.array([t0]), tf=np.array([tf]))
            per_case_log(case_id, f"array_file_written {array_path}")
            try:
                client.remove(model)
            except Exception:
                pass
            model = None
            gc.collect()
        else:
            per_case_log(case_id, f"using_existing_array_file {array_path}")

        with np.load(array_path) as data:
            r0s = np.asarray(data["r0"], dtype=float)
            z0s = np.asarray(data["z0"], dtype=float)
            p0s = np.asarray(data["phils0"], dtype=float)
            rfs = np.asarray(data["rf"], dtype=float)
            zfs = np.asarray(data["zf"], dtype=float)
            pfs = np.asarray(data["philsf"], dtype=float)
            t0 = float(data["t0"][0])
            tf = float(data["tf"][0])
        n0, u0, m0 = int(r0s.size), int(r0s.size), "npz_existing_arrays"
        nf, uf, mf = int(rfs.size), int(rfs.size), "npz_existing_arrays"
        ri, ro, z_ring0, h_ring = t4.case_params(case_id)
        s0 = t4.summary_from_arrays(case_id, 1, t0, r0s, z0s, p0s, ri, ro, z_ring0, h_ring)
        sf = t4.summary_from_arrays(case_id, 51, tf, rfs, zfs, pfs, ri, ro, z_ring0, h_ring)
        h0 = float(s0["H_median"])
        hf = float(sf["H_median"])
        flag = bool(sf["pseudo_spike_regional_flag"])
        result.update(
            {
                "extraction_status": "PASS",
                "postprocess_status": "PASS",
                "array_path": abspath(array_path),
                "point_count_original_initial": n0,
                "point_count_used_initial": u0,
                "point_count_original_final": nf,
                "point_count_used_final": uf,
                "array_method_initial": m0,
                "array_method_final": mf,
                "postprocess_method": sf["postprocess_method"],
                "H0_recomputed": h0,
                "Hfinal_recomputed": hf,
                "H_final_minus_H0_recomputed": hf - h0 if finite(h0) and finite(hf) else math.nan,
                "interface_quality": "clear" if not flag else "weak_or_spiky",
                "regional_roughness": sf["roughness_peak_to_peak"],
                "regional_roughness_inner_edge": sf["regional_roughness_inner_edge"],
                "regional_roughness_outer_edge": sf["regional_roughness_outer_edge"],
                "regional_roughness_farfield": sf["regional_roughness_farfield"],
                "max_slope": sf["max_slope"],
                "principal_spike_region": sf["principal_spike_region"],
                "interface_points_count": sf["interface_points_count"],
                "pseudo_spike_regional_flag": str(flag),
                "memory_error_resolved": "YES",
                "case_pass_after_recompute": str(not flag and finite(h0) and finite(hf)),
            }
        )
        per_case_log(case_id, "postprocess_pass")
    except Exception as exc:
        result.update(
            {
                "exception_class": exc.__class__.__name__,
                "exception_message": str(exc)[:1000],
                "traceback": traceback.format_exc()[:2000],
            }
        )
        per_case_log(case_id, "exception\n" + traceback.format_exc())
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass
    return result


def render_bars(path: Path, labels: list[str], values: list[float], title: str) -> str:
    width, height = 1200, 580
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
        small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    draw.text((30, 20), title, fill=(0, 0, 0), font=font)
    x0, y0, w, h = 80, 105, 1020, 330
    draw.line((x0, y0 + h, x0 + w, y0 + h), fill=(0, 0, 0))
    draw.line((x0, y0, x0, y0 + h), fill=(0, 0, 0))
    finite_values = [v for v in values if finite(v)]
    max_v = max(finite_values + [1.0])
    bar_w = max(35, int(w / max(1, len(values) * 2)))
    for idx, (label, value) in enumerate(zip(labels, values)):
        bx0 = x0 + 40 + idx * (bar_w + 70)
        bx1 = bx0 + bar_w
        if finite(value):
            by1 = y0 + h
            by0 = by1 - int(h * float(value) / max_v)
            draw.rectangle((bx0, by0, bx1, by1), fill=(67, 111, 191))
            draw.text((bx0 - 12, by0 - 22), f"{value:.3g}", fill=(0, 0, 0), font=small)
        draw.text((bx0 - 24, y0 + h + 18), label[:24], fill=(0, 0, 0), font=small)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return abspath(path)


def reviewer_figures(metrics: list[dict[str, str]], merged: list[dict[str, Any]]) -> None:
    status_counts = Counter(row.get("extraction_status", "") for row in metrics)
    render_bars(OUT / "images" / "T005_extraction_status_summary.png", list(status_counts.keys()), [float(v) for v in status_counts.values()], "T005 extraction status summary")
    quality_counts = Counter(row.get("interface_quality", "") for row in metrics)
    render_bars(OUT / "images" / "T005_interface_quality_summary.png", list(quality_counts.keys()), [float(v) for v in quality_counts.values()], "T005 interface quality summary")
    baseline_cases = [row for row in merged if row.get("case_id") in {"G2_ring_deeper_submerged", "G3_ring_far_below_surface", "W10_plain_wall_no_wettedwall_diagnostic", "W0_current_wettedwall"}]
    labels = [str(row.get("case_id", "")) for row in baseline_cases]
    values = [float(row.get("regional_roughness", "nan")) * 1e6 if finite(row.get("regional_roughness")) else math.nan for row in baseline_cases]
    render_bars(OUT / "images" / "T005_baseline_discrimination_summary.png", labels, values, "T005 baseline-discrimination roughness (um)")


def status_for_case(rows: dict[str, dict[str, str]], case_id: str) -> str:
    row = rows.get(case_id)
    if not row:
        return "NOT_ATTEMPTED"
    if row.get("postprocess_status") == "PASS" and row.get("case_pass_after_recompute") == "True":
        return "PASS"
    if row.get("extraction_status") or row.get("postprocess_status"):
        return "FAIL"
    return "UNKNOWN"


def merged_metrics(t005_metrics: list[dict[str, str]]) -> list[dict[str, Any]]:
    t004_latest = latest_rows_by_case(read_csv(OUT / "tables" / "T004_recomputed_metrics.csv"))
    t005_latest = latest_rows_by_case(t005_metrics)
    rows: list[dict[str, Any]] = []
    for case_id in ["G2_ring_deeper_submerged", "G3_ring_far_below_surface"]:
        if case_id in t004_latest:
            row = dict(t004_latest[case_id])
            row["source_task"] = "T004"
            rows.append(row)
    for case_id, _ in REMAINING_PRIORITY:
        if case_id in t005_latest:
            row = dict(t005_latest[case_id])
            row["source_task"] = "T005"
            rows.append(row)
    columns = ["source_task"] + metric_columns()
    write_csv(OUT / "tables" / "T005_merged_T004_T005_metrics.csv", rows, columns)
    return rows


def final_report(metrics: list[dict[str, str]], merged: list[dict[str, Any]]) -> dict[str, str]:
    latest = latest_rows_by_case(metrics)
    attempted = len(metrics)
    extraction_pass = sum(1 for row in metrics if row.get("extraction_status") == "PASS")
    post_pass = sum(1 for row in metrics if row.get("postprocess_status") == "PASS")
    raw_status = "YES" if extraction_pass == len(REMAINING_PRIORITY) else "PARTIAL" if extraction_pass else "NO"
    mem_status = "YES" if post_pass == attempted and attempted > 0 else "PARTIAL" if post_pass else "NO"
    iq_status = "YES" if post_pass == attempted and attempted > 0 else "PARTIAL" if post_pass else "NO"
    w10_status = status_for_case(latest, "W10_plain_wall_no_wettedwall_diagnostic")
    w0_status = status_for_case(latest, "W0_current_wettedwall")
    t005_status = "PASS" if raw_status == "YES" and post_pass == len(REMAINING_PRIORITY) else "PARTIAL" if attempted else "FAIL"
    gates = {
        "T005_STATUS": t005_status,
        "RAW_ARRAY_EXTRACTION_COMPLETED_REMAINING_CASES": raw_status,
        "POSTPROCESSING_MEMORY_ERROR_RESOLVED_REMAINING_CASES": mem_status,
        "INTERFACE_QUALITY_EXTRACTION_REPAIRED_REMAINING_CASES": iq_status,
        "W10_PLAIN_WALL_BASELINE_STATUS": w10_status,
        "W0_CURRENT_WETTEDWALL_STATUS": w0_status,
        "CREDIBLE_STATIC_BASELINE_AFTER_T005": "UNKNOWN" if w10_status == "PASS" and w0_status == "PASS" else "NO",
        "CREDIBLE_MICRO_MOTION_BASELINE_AFTER_T005": "UNKNOWN",
        "ALLOW_NEXT_DISPLACEMENT_LADDER": "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    lines = [
        "# T005 Final Report",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: continuation of T004 raw-array extraction and postprocessing recompute for remaining cases.",
        "- No COMSOL study, Stage 6, parameter sweep, Jet1/Jet2 detection, or real Hmax output was performed.",
        "",
        "## Gate Values",
        "",
    ]
    lines.extend([f"- `{key} = {value}`" for key, value in gates.items()])
    lines.extend(
        [
            "",
            "## T005 Case Results",
            "",
            f"- Attempted T005 cases: `{attempted}`",
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
            f"- Merged T004/T005 metrics table: `{OUT / 'tables' / 'T005_merged_T004_T005_metrics.csv'}`",
            f"- Merged rows available: `{len(merged)}`",
            "",
            "## Next Recommended Task",
            "",
            "- Continue T005 extraction for the remaining contact-angle/slip cases if Review Agent needs all seven remaining rows before gate review. Stage advancement remains blocked.",
        ]
    )
    write_text(OUT / "reports" / "T005_final_report.md", "\n".join(lines) + "\n")
    write_json(OUT / "reports" / "T005_gate_summary.json", gates)
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
            "- T004 completed G2/G3 only; T005 continues remaining wetted-wall/contactline cases.",
            f"- T005 attempted remaining cases: `{attempted}`",
            f"- T005 status: `{gates['T005_STATUS']}`",
            f"- `RAW_ARRAY_EXTRACTION_COMPLETED_REMAINING_CASES = {gates['RAW_ARRAY_EXTRACTION_COMPLETED_REMAINING_CASES']}`",
            f"- `POSTPROCESSING_MEMORY_ERROR_RESOLVED_REMAINING_CASES = {gates['POSTPROCESSING_MEMORY_ERROR_RESOLVED_REMAINING_CASES']}`",
            f"- `INTERFACE_QUALITY_EXTRACTION_REPAIRED_REMAINING_CASES = {gates['INTERFACE_QUALITY_EXTRACTION_REPAIRED_REMAINING_CASES']}`",
            f"- `W10_PLAIN_WALL_BASELINE_STATUS = {gates['W10_PLAIN_WALL_BASELINE_STATUS']}`",
            f"- `W0_CURRENT_WETTEDWALL_STATUS = {gates['W0_CURRENT_WETTEDWALL_STATUS']}`",
            f"- `ALLOW_NEXT_DISPLACEMENT_LADDER = {gates['ALLOW_NEXT_DISPLACEMENT_LADDER']}`",
            f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
            f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
            f"- T005 final report: `{OUT / 'reports' / 'T005_final_report.md'}`",
            f"- T005 merged metrics: `{OUT / 'tables' / 'T005_merged_T004_T005_metrics.csv'}`",
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


def update_polling_log(commit_sha: str = "") -> None:
    log_path = ROOT / "tasks" / "BUILDER_POLLING_LOG.csv"
    row = {
        "round_start_time": f"{RUN_ID[:4]}-{RUN_ID[4:6]}-{RUN_ID[6:8]}T{RUN_ID[9:11]}:{RUN_ID[11:13]}:{RUN_ID[13:15]}+08:00",
        "active_task": "tasks/NEXT_TASK.md",
        "active_task_archive": "tasks/20260620_150000_T005_continue_raw_array_extraction_remaining_cases.md",
        "executed": "YES",
        "pushed": "PENDING",
        "commit_sha": commit_sha,
        "notes": "T005 executed for remaining priority cases under bounded runtime; commit SHA filled by git history after push.",
    }
    columns = ["round_start_time", "active_task", "active_task_archive", "executed", "pushed", "commit_sha", "notes"]
    append_csv(log_path, row, columns)


def main() -> int:
    ensure_dirs()
    script_copy = OUT / "scripts" / "T005_continue_raw_array_extraction.py"
    if Path(__file__).resolve() != script_copy.resolve():
        shutil.copy2(Path(__file__).resolve(), script_copy)
    continuation_plan()

    max_cases = int(os.environ.get("T005_MAX_CASES", "2"))
    existing = read_csv(OUT / "tables" / "T005_recomputed_metrics.csv")
    done = {row.get("case_id") for row in existing if row.get("extraction_status") == "PASS"}
    attempted_this_run = 0
    client = mph.Client(cores=2, version="6.4")
    try:
        for priority, (case_id, model_path) in enumerate(REMAINING_PRIORITY, start=1):
            if case_id in done:
                continue
            if attempted_this_run >= max_cases:
                break
            result = process_case(client, priority, case_id, model_path)
            attempted_this_run += 1
            progress = {
                "case_id": case_id,
                "priority": priority,
                "model_path": abspath(model_path),
                "model_exists": "YES" if model_path.exists() else "NO",
                "previous_t004_status": previous_t004_status_by_case().get(case_id, ""),
                "attempted_t005": "YES",
                "extraction_status": result.get("extraction_status", ""),
                "postprocess_status": result.get("postprocess_status", ""),
                "output_array_path": result.get("array_path", ""),
                "notes": result.get("exception_message", ""),
            }
            append_csv(OUT / "tables" / "T005_progress.csv", progress, t005_progress_columns())
            append_csv(OUT / "tables" / "T005_recomputed_metrics.csv", result, metric_columns())
            write_csv(OUT / "tables" / "T005_case_manifest.csv", build_manifest(), t005_progress_columns())
    finally:
        try:
            client.clear()
        except Exception:
            pass

    latest_metrics = [latest_rows_by_case(read_csv(OUT / "tables" / "T005_recomputed_metrics.csv"))[case_id] for case_id, _ in REMAINING_PRIORITY if case_id in latest_rows_by_case(read_csv(OUT / "tables" / "T005_recomputed_metrics.csv"))]
    merged = merged_metrics(latest_metrics)
    reviewer_figures(latest_metrics, merged)
    gates = final_report(latest_metrics, merged)
    update_readme(gates, len(latest_metrics))
    update_polling_log()
    return 0 if gates["T005_STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
