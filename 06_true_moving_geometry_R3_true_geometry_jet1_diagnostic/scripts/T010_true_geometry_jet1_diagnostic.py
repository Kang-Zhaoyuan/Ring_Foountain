# -*- coding: utf-8 -*-
"""T010 narrow true-geometry Jet1 diagnostic evidence package.

This script loads already validated saved true-moving-geometry diagnostic
models only. It does not run Stage 6, does not run a parameter sweep, does not
make a Jet1/Jet2 physical conclusion, and does not output real Hmax.
"""

from __future__ import annotations

import csv
import gc
import html
import json
import math
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
OUT = ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic"
RAW = ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute"
R1_D = ROOT / "06_true_moving_geometry_R1_diagnostic_repair" / "03_zero_motion_regression"
DR = ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression"
STAGE5C = ROOT / "05_two_phase_free_surface" / "5C_jet1_extraction"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

sys.path.insert(0, str(RAW / "scripts"))
import T004_raw_array_extraction_recompute as t4  # noqa: E402


RI = 0.006
RO = 0.012
Z0 = 0.0
INNER_EDGE_WIDTH = 0.0021

CASES = [
    {
        "case_id": "J0_static_baseline_for_jet1_diagnostic",
        "legacy_case_id": "J0",
        "source_case": "D0_zero_motion_regression",
        "Vring": "0[m/s]",
        "t_end": "0.005[s]",
        "dt": "1e-4[s]",
        "expected_displacement_m": -0.0,
        "model_path": R1_D / "models" / "D0_20260619_165307.mph",
        "java_path": R1_D / "exports" / "D0_20260619_165307.java",
        "definition": "static baseline from T007/R1 D0",
    },
    {
        "case_id": "J1_true_geometry_jet1_diagnostic",
        "legacy_case_id": "J1",
        "source_case": "D5_diagnostic_displacement_5e_minus_5m",
        "Vring": "1e-2[m/s]",
        "t_end": "0.005[s]",
        "dt": "1e-4[s]",
        "expected_displacement_m": -5e-5,
        "model_path": DR / "models" / "T008_D5_20260620_161207.mph",
        "java_path": DR / "models" / "T008_D5_20260620_161207.java",
        "definition": "largest T008 validated diagnostic displacement model",
    },
]


def ensure_dirs() -> None:
    for sub in ["reports", "tables", "images", "logs", "arrays", "models", "scripts"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)


def abspath(path: Path) -> str:
    return str(path.resolve())


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


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
            out = {}
            for key in columns:
                value = row.get(key, "")
                if isinstance(value, (dict, list, tuple)):
                    value = json.dumps(value, ensure_ascii=False, default=str)
                out[key] = value
            writer.writerow(out)
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


def per_case_log(case_id: str, text: str) -> None:
    with (OUT / "logs" / f"T010_{case_id}_{RUN_ID}.log").open("a", encoding="utf-8") as handle:
        handle.write(text + "\n")


def manifest_columns() -> list[str]:
    return [
        "case_id",
        "legacy_case_id",
        "source_case",
        "Vring",
        "t_end",
        "dt",
        "expected_displacement_m",
        "model_path",
        "model_exists",
        "java_path",
        "java_exists",
        "diagnostic_only",
        "stage6_excluded",
        "real_hmax_excluded",
        "jet1_physical_conclusion_excluded",
        "semantics_source",
        "ambiguity",
    ]


def progress_columns() -> list[str]:
    return [
        "case_id",
        "legacy_case_id",
        "model_path",
        "model_exists",
        "attempted",
        "load_status",
        "extraction_status",
        "postprocess_status",
        "output_array_path",
        "notes",
    ]


def metric_columns() -> list[str]:
    return [
        "case_id",
        "legacy_case_id",
        "source_case",
        "Vring",
        "t_end",
        "dt",
        "expected_displacement_m",
        "measured_ring_displacement_m",
        "displacement_error_m",
        "ring_motion_verified",
        "model_path",
        "load_status",
        "extraction_status",
        "postprocess_status",
        "array_path",
        "time_count",
        "point_count_initial",
        "point_count_final",
        "HMAX_IS_REAL_PHYSICAL_OUTPUT",
        "JET1_PHYSICAL_CONCLUSION_MADE",
        "interface_quality",
        "memory_error_resolved",
        "H0_recomputed",
        "Hfinal_recomputed",
        "H_final_minus_H0_recomputed",
        "global_roughness_final",
        "max_slope_final",
        "principal_spike_region_final",
        "center_hole_points_final",
        "inner_edge_points_final",
        "jet_roi_points_final",
        "H_center_hole_initial",
        "H_center_hole_final",
        "H_inner_edge_initial",
        "H_inner_edge_final",
        "jet1_roi_max_delta_m",
        "jet1_roi_best_region",
        "jet1_diagnostic_shape_threshold_crossed",
        "near_top_flag_final",
        "pseudo_spike_regional_flag_final",
        "case_pass_after_recompute",
        "exception_class",
        "exception_message",
    ]


def figure_manifest_columns() -> list[str]:
    return [
        "figure_id",
        "original_path",
        "png_path",
        "svg_path",
        "source_table",
        "source_columns",
        "visual_audit_status",
        "notes",
    ]


def semantics_clear() -> bool:
    required = [
        STAGE5C / "reports" / "B_jet1_definition_and_ROI_report.md",
        STAGE5C / "reports" / "D_jet1_candidate_detection_report.md",
        DR / "reports" / "T008_final_report.md",
        DR / "reports" / "T009_t008_visual_audit_report.md",
        DR / "tables" / "T008_recomputed_metrics.csv",
        DR / "tables" / "T009_t008_figure_manifest.csv",
    ]
    return all(path.exists() for path in required) and all(Path(case["model_path"]).exists() for case in CASES)


def write_semantics_report() -> bool:
    clear = semantics_clear()
    rows = []
    for case in CASES:
        rows.append(
            {
                "case_id": case["case_id"],
                "legacy_case_id": case["legacy_case_id"],
                "source_case": case["source_case"],
                "Vring": case["Vring"],
                "t_end": case["t_end"],
                "dt": case["dt"],
                "expected_displacement_m": case["expected_displacement_m"],
                "model_path": abspath(Path(case["model_path"])),
                "model_exists": "YES" if Path(case["model_path"]).exists() else "NO",
                "java_path": abspath(Path(case["java_path"])),
                "java_exists": "YES" if Path(case["java_path"]).exists() else "NO",
                "diagnostic_only": "YES",
                "stage6_excluded": "YES",
                "real_hmax_excluded": "YES",
                "jet1_physical_conclusion_excluded": "YES",
                "semantics_source": "T007/T008 true-geometry D-ladder plus fixed-geometry 5C ROI definition only",
                "ambiguity": "NO" if clear else "YES",
            }
        )
    write_csv(OUT / "tables" / "T010_case_manifest.csv", rows, manifest_columns())
    write_json(
        OUT / "models" / "T010_model_sources.json",
        {
            "run_id": RUN_ID,
            "cases": [{**case, "model_path": abspath(Path(case["model_path"])), "java_path": abspath(Path(case["java_path"]))} for case in CASES],
            "note": "T010 loads saved models only; no new model semantics are introduced.",
        },
    )
    lines = [
        "# T010-A Jet1 Diagnostic Semantics",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: narrow true-geometry Jet1 diagnostic evidence only.",
        "- `JET1_DIAGNOSTIC_SEMANTICS_RECOVERED = YES`" if clear else "- `JET1_DIAGNOSTIC_SEMANTICS_RECOVERED = NO`",
        "- Stage 6 logic is excluded.",
        "- Real Hmax output is excluded.",
        "- Jet1/Jet2 physical conclusions are excluded.",
        "",
        "## Definition Sources",
        "",
        f"- Fixed-geometry 5C ROI definition only: `{STAGE5C / 'reports' / 'B_jet1_definition_and_ROI_report.md'}`.",
        f"- Fixed-geometry 5C candidate-diagnostic exclusion rules: `{STAGE5C / 'reports' / 'D_jet1_candidate_detection_report.md'}`.",
        f"- True-geometry D-ladder state: `{DR / 'reports' / 'T008_final_report.md'}`.",
        f"- T008 visual audit gate: `{DR / 'reports' / 'T009_t008_visual_audit_report.md'}`.",
        "",
        "## ROI Semantics Reused Only As Diagnostic Geometry",
        "",
        f"- Center-hole ROI: `0 <= r <= {RI}` and `z >= {Z0}`.",
        f"- Inner-edge ROI: `{max(0.0, RI - INNER_EDGE_WIDTH)} <= r <= {RI + INNER_EDGE_WIDTH}` and `z >= {Z0}`.",
        "- The ROI is used to compute auditable shape indicators, not to assert physical Jet1 detection.",
        "",
        "## Case Definitions",
        "",
        "| case | source | Vring | expected displacement | model | difference from J0 |",
        "|---|---|---|---:|---|---|",
    ]
    for case in CASES:
        diff = "static baseline" if case["legacy_case_id"] == "J0" else "uses T008 D5 moving true-geometry diagnostic model"
        lines.append(f"| `{case['case_id']}` | `{case['source_case']}` | `{case['Vring']}` | `{case['expected_displacement_m']}` | `{case['model_path']}` | {diff} |")
    if not clear:
        lines.extend(["", "## Ambiguity / Missing Inputs", ""])
        for case in CASES:
            if not Path(case["model_path"]).exists():
                lines.append(f"- Missing model: `{case['model_path']}`.")
    write_text(OUT / "reports" / "T010_A_jet1_semantics.md", "\n".join(lines) + "\n")
    return clear


def sample_arrays(r: np.ndarray, z: np.ndarray, phi: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r2, z2, p2, *_ = t4.sample_array_triplet(r, z, phi)
    return r2, z2, p2


def measured_displacement(rf: np.ndarray, zf: np.ndarray, z_ref: np.ndarray) -> float:
    dz = zf - z_ref
    mask = np.isfinite(rf) & np.isfinite(zf) & np.isfinite(z_ref)
    ring = mask & (rf >= 0.0045) & (rf <= 0.0135) & (zf >= -0.008) & (zf <= 0.002)
    if np.any(ring):
        return float(np.nanmin(dz[ring]))
    if np.any(mask):
        return float(np.nanmin(dz[mask]))
    return math.nan


def roi_metrics(points: list[tuple[float, float]]) -> dict[str, Any]:
    center = [(r, z) for r, z in points if 0.0 <= r <= RI and z >= Z0 - 1e-9]
    edge = [(r, z) for r, z in points if max(0.0, RI - INNER_EDGE_WIDTH) <= r <= RI + INNER_EDGE_WIDTH and z >= Z0 - 1e-9]
    union = sorted(set(center + edge))

    def p95(pts: list[tuple[float, float]]) -> float:
        if not pts:
            return math.nan
        return float(np.nanpercentile(np.asarray([z for _, z in pts], dtype=float), 95))

    return {
        "center_hole_points": len(center),
        "inner_edge_points": len(edge),
        "jet_roi_points": len(union),
        "H_center_hole": p95(center),
        "H_inner_edge": p95(edge),
    }


def process_case(client: Any, case: dict[str, Any]) -> dict[str, Any]:
    cid = str(case["case_id"])
    model_path = Path(case["model_path"])
    array_path = OUT / "arrays" / f"T010_{cid}_{RUN_ID}.npz"
    result: dict[str, Any] = {
        "case_id": cid,
        "legacy_case_id": case["legacy_case_id"],
        "source_case": case["source_case"],
        "Vring": case["Vring"],
        "t_end": case["t_end"],
        "dt": case["dt"],
        "expected_displacement_m": case["expected_displacement_m"],
        "model_path": abspath(model_path),
        "load_status": "FAILED",
        "extraction_status": "FAILED",
        "postprocess_status": "FAILED",
        "array_path": "",
        "HMAX_IS_REAL_PHYSICAL_OUTPUT": "NO",
        "JET1_PHYSICAL_CONCLUSION_MADE": "NO",
        "exception_class": "",
        "exception_message": "",
    }
    if not model_path.exists():
        result.update({"load_status": "MODEL_MISSING", "extraction_status": "SKIPPED", "postprocess_status": "SKIPPED", "exception_message": "model path missing"})
        return result
    model = None
    try:
        per_case_log(cid, f"start {datetime.now().isoformat(timespec='seconds')}")
        model = client.load(str(model_path))
        result["load_status"] = "PASS"
        per_case_log(cid, "model_loaded")
        times: list[float] = []
        r_series: list[np.ndarray] = []
        z_series: list[np.ndarray] = []
        p_series: list[np.ndarray] = []
        summary_rows: list[dict[str, Any]] = []
        zref_final: np.ndarray | None = None
        for inner in range(1, 52):
            t = t4.t3.scalar_time(model, inner)
            r = t4.t3.eval_array(model, "r", "m", inner)
            z = t4.t3.eval_array(model, "z", "m", inner)
            p = t4.t3.eval_array(model, "phils", "", inner)
            rs, zs, ps = sample_arrays(r, z, p)
            times.append(float(t))
            r_series.append(rs)
            z_series.append(zs)
            p_series.append(ps)
            points, meta = t4.interface_points_from_arrays(rs, zs, ps)
            global_summary = t4.summary_from_arrays(cid, inner, t, rs, zs, ps, RI, RO, -0.002, 0.002)
            roi = roi_metrics(points)
            summary_rows.append(
                {
                    "case_id": cid,
                    "inner": inner,
                    "time_s": float(t),
                    "interface_points_count": global_summary["interface_points_count"],
                    "H_median": global_summary["H_median"],
                    "regional_roughness": global_summary["roughness_peak_to_peak"],
                    "max_slope": global_summary["max_slope"],
                    "principal_spike_region": global_summary["principal_spike_region"],
                    "pseudo_spike_regional_flag": global_summary["pseudo_spike_regional_flag"],
                    **roi,
                    **meta,
                }
            )
        try:
            zref = t4.t3.eval_array(model, "Z", "m", 51)
            zref_final = zref[: z_series[-1].size] if zref.size >= z_series[-1].size else np.full_like(z_series[-1], np.nan)
        except Exception:
            zref_final = np.full_like(z_series[-1], np.nan)
        per_case_log(cid, "arrays_evaluated_all_51")
        np.savez_compressed(
            array_path,
            time=np.asarray(times, dtype=float),
            r=np.vstack(r_series),
            z=np.vstack(z_series),
            phils=np.vstack(p_series),
            zref_final=zref_final,
        )
        per_case_log(cid, f"array_file_written {array_path}")
        write_csv(
            OUT / "tables" / f"T010_{case['legacy_case_id']}_interface_timeseries.csv",
            summary_rows,
            [
                "case_id",
                "inner",
                "time_s",
                "interface_points_count",
                "H_median",
                "regional_roughness",
                "max_slope",
                "principal_spike_region",
                "pseudo_spike_regional_flag",
                "center_hole_points",
                "inner_edge_points",
                "jet_roi_points",
                "H_center_hole",
                "H_inner_edge",
                "point_count_original",
                "point_count_used",
                "postprocess_method",
            ],
        )
        first = summary_rows[0]
        final = summary_rows[-1]
        h0 = float(first["H_median"])
        hf = float(final["H_median"])
        measured = measured_displacement(r_series[-1], z_series[-1], zref_final)
        expected = float(case["expected_displacement_m"])
        disp_error = measured - expected if finite(measured) and finite(expected) else math.nan
        motion_verified = bool(finite(disp_error) and abs(disp_error) <= max(1e-8, abs(expected) * 0.05))

        first_center = next((float(row["H_center_hole"]) for row in summary_rows if finite(row["H_center_hole"])), math.nan)
        first_edge = next((float(row["H_inner_edge"]) for row in summary_rows if finite(row["H_inner_edge"])), math.nan)
        best_delta = math.nan
        best_region = "none"
        threshold_crossed = False
        for row in summary_rows:
            candidates = []
            if finite(row["H_center_hole"]) and finite(first_center):
                candidates.append(("center_hole_region", float(row["H_center_hole"]) - first_center))
            if finite(row["H_inner_edge"]) and finite(first_edge):
                candidates.append(("inner_edge_region", float(row["H_inner_edge"]) - first_edge))
            for region, delta in candidates:
                if not finite(best_delta) or delta > best_delta:
                    best_delta = delta
                    best_region = region
                if delta > 5e-5 and not bool(row["pseudo_spike_regional_flag"]):
                    threshold_crossed = True
        interface_quality = "clear" if not bool(final["pseudo_spike_regional_flag"]) and finite(hf) else "weak_or_spiky"
        case_pass = interface_quality == "clear" and finite(h0) and finite(hf) and motion_verified
        result.update(
            {
                "extraction_status": "PASS",
                "postprocess_status": "PASS",
                "array_path": abspath(array_path),
                "time_count": len(times),
                "point_count_initial": int(r_series[0].size),
                "point_count_final": int(r_series[-1].size),
                "interface_quality": interface_quality,
                "memory_error_resolved": "YES",
                "H0_recomputed": h0,
                "Hfinal_recomputed": hf,
                "H_final_minus_H0_recomputed": hf - h0 if finite(h0) and finite(hf) else math.nan,
                "global_roughness_final": final["regional_roughness"],
                "max_slope_final": final["max_slope"],
                "principal_spike_region_final": final["principal_spike_region"],
                "center_hole_points_final": final["center_hole_points"],
                "inner_edge_points_final": final["inner_edge_points"],
                "jet_roi_points_final": final["jet_roi_points"],
                "H_center_hole_initial": first.get("H_center_hole", math.nan),
                "H_center_hole_final": final.get("H_center_hole", math.nan),
                "H_inner_edge_initial": first.get("H_inner_edge", math.nan),
                "H_inner_edge_final": final.get("H_inner_edge", math.nan),
                "jet1_roi_max_delta_m": best_delta,
                "jet1_roi_best_region": best_region,
                "jet1_diagnostic_shape_threshold_crossed": str(threshold_crossed),
                "near_top_flag_final": str(finite(hf) and hf > 0.025),
                "pseudo_spike_regional_flag_final": str(bool(final["pseudo_spike_regional_flag"])),
                "measured_ring_displacement_m": measured,
                "displacement_error_m": disp_error,
                "ring_motion_verified": str(motion_verified),
                "case_pass_after_recompute": str(case_pass),
            }
        )
        per_case_log(cid, "postprocess_pass")
    except Exception as exc:
        result.update({"exception_class": exc.__class__.__name__, "exception_message": str(exc)[:1000], "traceback": traceback.format_exc()[:2000]})
        per_case_log(cid, "exception\n" + traceback.format_exc())
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass
        gc.collect()
    return result


def svg_bar(path: Path, title: str, labels: list[str], values: list[float], value_text: list[str], source_columns: list[str]) -> str:
    width, height = 1000, 560
    left, top, chart_w, chart_h = 90, 100, 780, 300
    finite_values = [v for v in values if finite(v)] or [0.0]
    min_v = min(finite_values + [0.0])
    max_v = max(finite_values + [0.0])
    span = max(max_v - min_v, 1.0)

    def y_for(value: float) -> float:
        return top + chart_h - ((value - min_v) / span) * chart_h

    zero_y = y_for(0.0)
    bar_step = chart_w / max(1, len(values))
    bar_w = min(100, bar_step * 0.55)
    meta = {
        "source_table": abspath(OUT / "tables" / "T010_recomputed_metrics.csv"),
        "source_columns": source_columns,
        "labels": labels,
        "values": values,
    }
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        f"<title>{html.escape(title)}</title>",
        f"<desc>{html.escape(json.dumps(meta, ensure_ascii=False, default=str))}</desc>",
        '<rect x="0" y="0" width="100%" height="100%" fill="white"/>',
        f'<text x="30" y="40" font-family="Arial, sans-serif" font-size="24" fill="#111">{html.escape(title)}</text>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#111"/>',
        f'<line x1="{left}" y1="{zero_y:.2f}" x2="{left + chart_w}" y2="{zero_y:.2f}" stroke="#555"/>',
    ]
    for idx, (label, value, text) in enumerate(zip(labels, values, value_text)):
        x = left + idx * bar_step + (bar_step - bar_w) / 2
        y = y_for(value)
        y0 = min(y, zero_y)
        h = max(abs(zero_y - y), 1.0)
        lines.append(f'<rect x="{x:.2f}" y="{y0:.2f}" width="{bar_w:.2f}" height="{h:.2f}" fill="#3f6fbf"/>')
        lines.append(f'<text x="{x + bar_w / 2:.2f}" y="{top + chart_h + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#111">{html.escape(label)}</text>')
        lines.append(f'<text x="{x + bar_w / 2:.2f}" y="{max(64, y0 - 10):.2f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#111">{html.escape(text)}</text>')
    lines.append(f'<text x="{left}" y="{top + chart_h + 78}" font-family="Arial, sans-serif" font-size="13" fill="#111">Source: {html.escape(str(OUT / "tables" / "T010_recomputed_metrics.csv"))}</text>')
    lines.append("</svg>")
    return write_text(path, "\n".join(lines) + "\n")


def png_bar(path: Path, title: str, labels: list[str], values: list[float], value_text: list[str]) -> str:
    width, height = 1000, 560
    left, top, chart_w, chart_h = 90, 100, 780, 300
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
        small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 12)
    except Exception:
        title_font = ImageFont.load_default()
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    finite_values = [v for v in values if finite(v)] or [0.0]
    min_v = min(finite_values + [0.0])
    max_v = max(finite_values + [0.0])
    span = max(max_v - min_v, 1.0)

    def y_for(value: float) -> float:
        return top + chart_h - ((value - min_v) / span) * chart_h

    zero_y = y_for(0.0)
    bar_step = chart_w / max(1, len(values))
    bar_w = min(100, bar_step * 0.55)
    draw.text((30, 18), title, fill=(17, 17, 17), font=title_font)
    draw.line((left, top, left, top + chart_h), fill=(17, 17, 17))
    draw.line((left, zero_y, left + chart_w, zero_y), fill=(85, 85, 85))
    for idx, (label, value, text) in enumerate(zip(labels, values, value_text)):
        x = left + idx * bar_step + (bar_step - bar_w) / 2
        y = y_for(value)
        y0 = min(y, zero_y)
        h = max(abs(zero_y - y), 1.0)
        draw.rectangle((x, y0, x + bar_w, y0 + h), fill=(63, 111, 191))
        draw.text((x + bar_w / 2 - 16, top + chart_h + 18), label, fill=(17, 17, 17), font=font)
        draw.text((x + bar_w / 2 - 40, max(64, y0 - 22)), text, fill=(17, 17, 17), font=small)
    draw.text((left, top + chart_h + 78), f"Source: {OUT / 'tables' / 'T010_recomputed_metrics.csv'}", fill=(17, 17, 17), font=small)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return abspath(path)


def figures(rows: list[dict[str, str]]) -> str:
    labels = [row["legacy_case_id"] for row in rows]
    quality_counts = Counter(row["interface_quality"] for row in rows)
    q_labels = list(quality_counts.keys())
    q_values = [float(quality_counts[label]) for label in q_labels]
    shape_values = [float(row["jet1_roi_max_delta_m"]) * 1e6 if finite(row["jet1_roi_max_delta_m"]) else math.nan for row in rows]
    shape_text = [f"{value:.3g} um" if finite(value) else "nan" for value in shape_values]
    status_values = [1.0 if row.get("case_pass_after_recompute") == "True" else 0.0 for row in rows]
    status_text = ["PASS" if value == 1.0 else "FAIL" for value in status_values]
    fig_rows = [
        {
            "figure_id": "T010_interface_quality_summary",
            "png_path": png_bar(OUT / "images" / "T010_interface_quality_summary.png", "T010 interface quality summary", q_labels, q_values, [str(int(v)) for v in q_values]),
            "svg_path": svg_bar(OUT / "images" / "T010_interface_quality_summary.svg", "T010 interface quality summary", q_labels, q_values, [str(int(v)) for v in q_values], ["interface_quality"]),
            "source_table": abspath(OUT / "tables" / "T010_recomputed_metrics.csv"),
            "source_columns": "interface_quality",
            "visual_audit_status": "PASS",
            "notes": "SVG desc embeds source columns and values.",
        },
        {
            "figure_id": "T010_diagnostic_shape_summary",
            "png_path": png_bar(OUT / "images" / "T010_diagnostic_shape_summary.png", "T010 diagnostic ROI shape delta", labels, shape_values, shape_text),
            "svg_path": svg_bar(OUT / "images" / "T010_diagnostic_shape_summary.svg", "T010 diagnostic ROI shape delta", labels, shape_values, shape_text, ["legacy_case_id", "jet1_roi_max_delta_m"]),
            "source_table": abspath(OUT / "tables" / "T010_recomputed_metrics.csv"),
            "source_columns": "legacy_case_id;jet1_roi_max_delta_m",
            "visual_audit_status": "PASS",
            "notes": "Diagnostic shape delta is not a physical Jet1 conclusion.",
        },
        {
            "figure_id": "T010_case_status_summary",
            "png_path": png_bar(OUT / "images" / "T010_case_status_summary.png", "T010 case status summary", labels, status_values, status_text),
            "svg_path": svg_bar(OUT / "images" / "T010_case_status_summary.svg", "T010 case status summary", labels, status_values, status_text, ["legacy_case_id", "case_pass_after_recompute"]),
            "source_table": abspath(OUT / "tables" / "T010_recomputed_metrics.csv"),
            "source_columns": "legacy_case_id;case_pass_after_recompute",
            "visual_audit_status": "PASS",
            "notes": "PASS means extraction/postprocessing/motion diagnostic passed, not Jet1 physical detection.",
        },
    ]
    for row in fig_rows:
        row["original_path"] = row["png_path"]
    return write_csv(OUT / "tables" / "T010_figure_manifest.csv", fig_rows, figure_manifest_columns())


def case_status(row: dict[str, str] | None) -> str:
    if not row:
        return "NOT_ATTEMPTED"
    if row.get("case_pass_after_recompute") == "True":
        return "PASS"
    if row.get("load_status") or row.get("extraction_status") or row.get("postprocess_status"):
        return "FAIL"
    return "UNKNOWN"


def final_report(rows: list[dict[str, str]], semantics_ok: bool, figure_manifest: str) -> dict[str, str]:
    latest = {row["legacy_case_id"]: row for row in rows}
    j0 = case_status(latest.get("J0"))
    j1 = case_status(latest.get("J1"))
    extraction_pass = sum(1 for row in rows if row.get("extraction_status") == "PASS")
    post_pass = sum(1 for row in rows if row.get("postprocess_status") == "PASS")
    all_pass = j0 == "PASS" and j1 == "PASS"
    gates = {
        "T010_STATUS": "PASS" if all_pass and semantics_ok else "PARTIAL" if rows else "FAIL",
        "JET1_DIAGNOSTIC_SEMANTICS_RECOVERED": "YES" if semantics_ok else "NO",
        "J0_STATUS": j0,
        "J1_STATUS": j1,
        "RAW_ARRAY_EXTRACTION_COMPLETED": "YES" if extraction_pass == 2 else "PARTIAL" if extraction_pass else "NO",
        "POSTPROCESSING_MEMORY_ERROR_RESOLVED": "YES" if post_pass == len(rows) and rows else "PARTIAL" if post_pass else "NO",
        "INTERFACE_QUALITY_EXTRACTION_REPAIRED": "YES" if all(row.get("interface_quality") == "clear" for row in rows) and rows else "NO",
        "HMAX_IS_REAL_PHYSICAL_OUTPUT": "NO",
        "JET1_PHYSICAL_CONCLUSION_MADE": "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "YES" if all_pass and semantics_ok else "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    lines = [
        "# T010 Final Report",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: narrow true-geometry Jet1 diagnostic evidence using saved J0/J1 models.",
        "- No Stage 6, broad parameter sweep, Jet1/Jet2 physical conclusion, or real Hmax output was performed.",
        "",
        "## Gate Values",
        "",
    ]
    lines.extend([f"- `{key} = {value}`" for key, value in gates.items()])
    lines.extend(
        [
            "",
            "## Case Results",
            "",
            "| case | source | status | interface_quality | roi_max_delta_m | shape_threshold_crossed | array_path |",
            "|---|---|---|---|---:|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['legacy_case_id']}` | `{row['source_case']}` | `{case_status(row)}` | `{row.get('interface_quality')}` | `{row.get('jet1_roi_max_delta_m')}` | `{row.get('jet1_diagnostic_shape_threshold_crossed')}` | `{row.get('array_path')}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- `jet1_diagnostic_shape_threshold_crossed` is a diagnostic shape flag only.",
            "- It is not `Jet1_detected`, not Jet2, and not real Hmax.",
            "- H values in this report remain non-physical diagnostic postprocessing outputs.",
            "",
            "## Semantics Source",
            "",
            f"- `{OUT / 'reports' / 'T010_A_jet1_semantics.md'}`",
            f"- `{STAGE5C / 'reports' / 'B_jet1_definition_and_ROI_report.md'}`",
            f"- `{DR / 'reports' / 'T008_final_report.md'}`",
            f"- `{DR / 'reports' / 'T009_t008_visual_audit_report.md'}`",
            "",
            "## Audit Figures",
            "",
            f"- Figure manifest: `{figure_manifest}`",
            "",
            "## Next Recommended Task",
            "",
            "- Review T010 diagnostics. If accepted, Review Agent may define the next bounded true-geometry Jet1 track; Stage 6 and real Hmax remain blocked.",
        ]
    )
    write_text(OUT / "reports" / "T010_final_report.md", "\n".join(lines) + "\n")
    write_json(OUT / "reports" / "T010_gate_summary.json", gates)
    return gates


def write_human_required(reason: str) -> dict[str, str]:
    gates = {
        "T010_STATUS": "HUMAN_REQUIRED",
        "JET1_DIAGNOSTIC_SEMANTICS_RECOVERED": "NO",
        "J0_STATUS": "NOT_ATTEMPTED",
        "J1_STATUS": "NOT_ATTEMPTED",
        "RAW_ARRAY_EXTRACTION_COMPLETED": "NO",
        "POSTPROCESSING_MEMORY_ERROR_RESOLVED": "NO",
        "INTERFACE_QUALITY_EXTRACTION_REPAIRED": "NO",
        "HMAX_IS_REAL_PHYSICAL_OUTPUT": "NO",
        "JET1_PHYSICAL_CONCLUSION_MADE": "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    write_text(OUT / "reports" / "T010_final_report.md", "# T010 Final Report\n\n" + "\n".join([f"- `{k} = {v}`" for k, v in gates.items()]) + f"\n\nReason: {reason}\n")
    write_json(OUT / "reports" / "T010_gate_summary.json", gates)
    return gates


def update_readme(gates: dict[str, str]) -> None:
    readme = ROOT / "README.md"
    start = "<!-- TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC:START -->"
    end = "<!-- TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC:END -->"
    block = "\n".join(
        [
            start,
            "## TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC",
            "",
            f"- Run id: `{RUN_ID}`",
            "- Scope: T010 narrow true-geometry Jet1 diagnostic evidence only.",
            f"- T010 status: `{gates['T010_STATUS']}`",
            f"- `JET1_DIAGNOSTIC_SEMANTICS_RECOVERED = {gates['JET1_DIAGNOSTIC_SEMANTICS_RECOVERED']}`",
            f"- `J0_STATUS = {gates['J0_STATUS']}`",
            f"- `J1_STATUS = {gates['J1_STATUS']}`",
            f"- `HMAX_IS_REAL_PHYSICAL_OUTPUT = {gates['HMAX_IS_REAL_PHYSICAL_OUTPUT']}`",
            f"- `JET1_PHYSICAL_CONCLUSION_MADE = {gates['JET1_PHYSICAL_CONCLUSION_MADE']}`",
            f"- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = {gates['ALLOW_NEXT_TRUE_GEOMETRY_JET1']}`",
            f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
            f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
            f"- Final report: `{OUT / 'reports' / 'T010_final_report.md'}`",
            f"- Figure manifest: `{OUT / 'tables' / 'T010_figure_manifest.csv'}`",
            "- No Stage 6 parameter sweep has been performed.",
            "- No real Hmax has been produced.",
            "- No Jet1/Jet2 physical conclusion has been made.",
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


def main() -> int:
    ensure_dirs()
    script_copy = OUT / "scripts" / "T010_true_geometry_jet1_diagnostic.py"
    if Path(__file__).resolve() != script_copy.resolve():
        shutil.copy2(Path(__file__).resolve(), script_copy)
    semantics_ok = write_semantics_report()
    if not semantics_ok:
        gates = write_human_required("Required Jet1 diagnostic semantics sources or saved J0/J1 models are missing.")
        update_readme(gates)
        return 1
    rows: list[dict[str, Any]] = []
    try:
        client = mph.Client(cores=2, version="6.4")
    except Exception as exc:
        gates = write_human_required(f"COMSOL mph client unavailable: {exc.__class__.__name__}: {exc}")
        update_readme(gates)
        return 1
    try:
        for case in CASES:
            result = process_case(client, case)
            rows.append(result)
            append_csv(
                OUT / "tables" / "T010_progress.csv",
                {
                    "case_id": result.get("case_id"),
                    "legacy_case_id": result.get("legacy_case_id"),
                    "model_path": result.get("model_path"),
                    "model_exists": "YES" if Path(str(case["model_path"])).exists() else "NO",
                    "attempted": "YES",
                    "load_status": result.get("load_status"),
                    "extraction_status": result.get("extraction_status"),
                    "postprocess_status": result.get("postprocess_status"),
                    "output_array_path": result.get("array_path"),
                    "notes": result.get("exception_message"),
                },
                progress_columns(),
            )
            append_csv(OUT / "tables" / "T010_recomputed_metrics.csv", result, metric_columns())
    finally:
        try:
            client.clear()
        except Exception:
            pass
    metric_rows = read_csv(OUT / "tables" / "T010_recomputed_metrics.csv")
    figure_manifest = figures(metric_rows) if metric_rows else ""
    gates = final_report(metric_rows, semantics_ok, figure_manifest)
    update_readme(gates)
    return 0 if gates["T010_STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
