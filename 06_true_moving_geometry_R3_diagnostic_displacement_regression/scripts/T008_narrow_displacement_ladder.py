# -*- coding: utf-8 -*-
"""T008 narrow diagnostic displacement ladder.

Builds D3/D4/D5 by reusing the validated R1/T007 D-ladder semantics:
ALE dx = [0, -Vring*t], WettedWall utr = [0, -Vring, 0],
t_end = 0.005[s], dt = 1e-4[s]. This script is diagnostic only.
It does not run Stage 6, does not detect Jet1/Jet2, and does not output
real physical Hmax.
"""

from __future__ import annotations

import csv
import gc
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
OUT = ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression"
RAW = ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute"
R1_D = ROOT / "06_true_moving_geometry_R1_diagnostic_repair" / "03_zero_motion_regression"
TEMPLATE_MODEL = R1_D / "models" / "D2_20260619_165307.mph"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

sys.path.insert(0, str(RAW / "scripts"))
import T004_raw_array_extraction_recompute as t4  # noqa: E402


CASES = [
    {
        "case_id": "D3_diagnostic_displacement_1e_minus_5m",
        "legacy_case_id": "D3",
        "Vring": "2e-3[m/s]",
        "Vring_m_per_s": 2e-3,
        "t_end": "0.005[s]",
        "dt": "1e-4[s]",
        "expected_displacement_m": -1e-5,
    },
    {
        "case_id": "D4_diagnostic_displacement_2p5e_minus_5m",
        "legacy_case_id": "D4",
        "Vring": "5e-3[m/s]",
        "Vring_m_per_s": 5e-3,
        "t_end": "0.005[s]",
        "dt": "1e-4[s]",
        "expected_displacement_m": -2.5e-5,
    },
    {
        "case_id": "D5_diagnostic_displacement_5e_minus_5m",
        "legacy_case_id": "D5",
        "Vring": "1e-2[m/s]",
        "Vring_m_per_s": 1e-2,
        "t_end": "0.005[s]",
        "dt": "1e-4[s]",
        "expected_displacement_m": -5e-5,
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
    with (OUT / "logs" / f"T008_{case_id}_{RUN_ID}.log").open("a", encoding="utf-8") as handle:
        handle.write(text + "\n")


def manifest_columns() -> list[str]:
    return [
        "case_id",
        "legacy_case_id",
        "Vring",
        "t_end",
        "dt",
        "expected_displacement_m",
        "template_model_path",
        "template_model_exists",
        "model_path",
        "java_path",
        "diagnostic_only",
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
        "solve_status",
        "extraction_status",
        "postprocess_status",
        "output_array_path",
        "notes",
    ]


def metric_columns() -> list[str]:
    return [
        "case_id",
        "legacy_case_id",
        "Vring",
        "t_end",
        "dt",
        "expected_displacement_m",
        "measured_ring_displacement_m",
        "displacement_error_m",
        "ring_motion_verified",
        "model_path",
        "java_path",
        "solve_status",
        "extraction_status",
        "postprocess_status",
        "array_path",
        "point_count_initial",
        "point_count_final",
        "postprocess_method",
        "H0_recomputed",
        "Hfinal_recomputed",
        "H_final_minus_H0_recomputed",
        "HMAX_IS_REAL_PHYSICAL_OUTPUT",
        "interface_quality",
        "regional_roughness",
        "regional_roughness_inner_edge",
        "regional_roughness_outer_edge",
        "regional_roughness_farfield",
        "max_slope",
        "principal_spike_region",
        "interface_points_count",
        "pseudo_spike_regional_flag",
        "memory_error_resolved",
        "case_pass_after_recompute",
        "exception_class",
        "exception_message",
    ]


def model_path_for(case: dict[str, Any]) -> Path:
    return OUT / "models" / f"T008_{case['legacy_case_id']}_{RUN_ID}.mph"


def java_path_for(case: dict[str, Any]) -> Path:
    return OUT / "models" / f"T008_{case['legacy_case_id']}_{RUN_ID}.java"


def write_semantics_report() -> bool:
    clear = TEMPLATE_MODEL.exists()
    rows = []
    for case in CASES:
        rows.append(
            {
                "case_id": case["case_id"],
                "legacy_case_id": case["legacy_case_id"],
                "Vring": case["Vring"],
                "t_end": case["t_end"],
                "dt": case["dt"],
                "expected_displacement_m": case["expected_displacement_m"],
                "template_model_path": abspath(TEMPLATE_MODEL),
                "template_model_exists": "YES" if TEMPLATE_MODEL.exists() else "NO",
                "model_path": abspath(model_path_for(case)),
                "java_path": abspath(java_path_for(case)),
                "diagnostic_only": "YES",
                "semantics_source": "T007 D0/D1/D2 semantics plus R1 D2 model template",
                "ambiguity": "NO" if clear else "YES",
            }
        )
    write_csv(OUT / "tables" / "T008_case_manifest.csv", rows, manifest_columns())
    lines = [
        "# T008-A Ladder Semantics",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Source semantics: `06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T007_A_d0_d1_d2_semantics.md`.",
        "- Anchor metrics: `06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T007_recomputed_metrics.csv`.",
        f"- Template model for new cases: `{TEMPLATE_MODEL}`.",
        f"- `D_LADDER_SEMANTICS_CLEAR = {'YES' if clear else 'NO'}`",
        "- New cases remain diagnostic-only and keep `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO`.",
        "- No Stage 6, Jet1/Jet2 detection, broad parameter sweep, or real Hmax output is allowed.",
        "",
        "## Reused Anchor Semantics",
        "",
        "- D0/D1/D2 use `dx=[0,-Vring*t]`, `utr=[0,-Vring,0]`, `t_end=0.005[s]`, `dt=1e-4[s]`.",
        "- T008 applies the same equations to D3/D4/D5 and changes only `Vring` relative to the D2 template.",
        "",
        "## New Diagnostic Cases",
        "",
        "| case_id | legacy_id | Vring | t_end | dt | expected displacement | diagnostic-only |",
        "|---|---|---|---|---|---:|---|",
    ]
    for case in CASES:
        lines.append(
            f"| `{case['case_id']}` | `{case['legacy_case_id']}` | `{case['Vring']}` | `{case['t_end']}` | `{case['dt']}` | `{case['expected_displacement_m']}` | YES |"
        )
    if not clear:
        lines.extend(["", "## Blocking Ambiguity", "", f"- Template model is missing: `{TEMPLATE_MODEL}`."])
    write_text(OUT / "reports" / "T008_A_ladder_semantics.md", "\n".join(lines) + "\n")
    return clear


def save_model_and_java(model: Any, model_path: Path, java_path: Path) -> None:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(path=str(model_path), format="Comsol")
    model.save(path=str(java_path), format="Java")


def build_and_solve_case(client: Any, case: dict[str, Any]) -> tuple[Any | None, Path, Path, dict[str, Any]]:
    cid = str(case["case_id"])
    model_path = model_path_for(case)
    java_path = java_path_for(case)
    result = {
        "model_path": abspath(model_path),
        "java_path": abspath(java_path),
        "solve_status": "FAILED",
        "exception_class": "",
        "exception_message": "",
    }
    model = None
    try:
        per_case_log(cid, f"load_template {TEMPLATE_MODEL}")
        model = client.load(str(TEMPLATE_MODEL))
        j = model.java
        j.param().set("Vring", str(case["Vring"]))
        j.param().set("t_end", str(case["t_end"]))
        j.param().set("dt", str(case["dt"]))
        try:
            j.study("std1").feature("time").set("tlist", "range(0,dt,t_end)")
        except Exception as exc:
            per_case_log(cid, f"tlist_set_warning {exc.__class__.__name__}: {exc}")
        per_case_log(cid, "solve_start")
        model.solve()
        per_case_log(cid, "solve_pass")
        save_model_and_java(model, model_path, java_path)
        per_case_log(cid, f"model_saved {model_path}")
        result["solve_status"] = "PASS"
    except Exception as exc:
        result.update({"exception_class": exc.__class__.__name__, "exception_message": str(exc)[:1000], "traceback": traceback.format_exc()[:2000]})
        per_case_log(cid, "solve_exception\n" + traceback.format_exc())
        if model is not None:
            try:
                failed_model = OUT / "models" / f"T008_{case['legacy_case_id']}_{RUN_ID}_failed.mph"
                failed_java = OUT / "models" / f"T008_{case['legacy_case_id']}_{RUN_ID}_failed.java"
                save_model_and_java(model, failed_model, failed_java)
                result["model_path"] = abspath(failed_model)
                result["java_path"] = abspath(failed_java)
            except Exception as save_exc:
                per_case_log(cid, f"failed_model_save_exception {save_exc.__class__.__name__}: {save_exc}")
    return model, model_path, java_path, result


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


def extract_and_postprocess(model: Any, case: dict[str, Any], model_path: Path, java_path: Path, solve_result: dict[str, Any]) -> dict[str, Any]:
    cid = str(case["case_id"])
    array_path = OUT / "arrays" / f"T008_{cid}_{RUN_ID}.npz"
    result = {
        "case_id": cid,
        "legacy_case_id": case["legacy_case_id"],
        "Vring": case["Vring"],
        "t_end": case["t_end"],
        "dt": case["dt"],
        "expected_displacement_m": case["expected_displacement_m"],
        "model_path": solve_result.get("model_path", abspath(model_path)),
        "java_path": solve_result.get("java_path", abspath(java_path)),
        "solve_status": solve_result.get("solve_status", "FAILED"),
        "extraction_status": "FAILED",
        "postprocess_status": "FAILED",
        "array_path": "",
        "HMAX_IS_REAL_PHYSICAL_OUTPUT": "NO",
        "exception_class": solve_result.get("exception_class", ""),
        "exception_message": solve_result.get("exception_message", ""),
    }
    if solve_result.get("solve_status") != "PASS":
        result["postprocess_status"] = "SKIPPED"
        return result
    try:
        t0 = t4.t3.scalar_time(model, 1)
        tf = t4.t3.scalar_time(model, 51)
        r0 = t4.t3.eval_array(model, "r", "m", 1)
        z0 = t4.t3.eval_array(model, "z", "m", 1)
        p0 = t4.t3.eval_array(model, "phils", "", 1)
        rf = t4.t3.eval_array(model, "r", "m", 51)
        zf = t4.t3.eval_array(model, "z", "m", 51)
        pf = t4.t3.eval_array(model, "phils", "", 51)
        try:
            zref = t4.t3.eval_array(model, "Z", "m", 51)
        except Exception:
            zref = np.full_like(zf, np.nan)
        per_case_log(cid, "arrays_evaluated")
        r0s, z0s, p0s = sample_arrays(r0, z0, p0)
        rfs, zfs, pfs = sample_arrays(rf, zf, pf)
        zrefs = zref[: rfs.size] if zref.size >= rfs.size else np.full_like(rfs, np.nan)
        np.savez_compressed(array_path, r0=r0s, z0=z0s, phils0=p0s, rf=rfs, zf=zfs, philsf=pfs, zref_final=zrefs, t0=np.array([t0]), tf=np.array([tf]))
        per_case_log(cid, f"array_file_written {array_path}")

        ri, ro, z_ring0, h_ring = t4.case_params(cid)
        s0 = t4.summary_from_arrays(cid, 1, t0, r0s, z0s, p0s, ri, ro, z_ring0, h_ring)
        sf = t4.summary_from_arrays(cid, 51, tf, rfs, zfs, pfs, ri, ro, z_ring0, h_ring)
        h0 = float(s0["H_median"])
        hf = float(sf["H_median"])
        flag = bool(sf["pseudo_spike_regional_flag"])
        measured = measured_displacement(rfs, zfs, zrefs)
        expected = float(case["expected_displacement_m"])
        disp_error = measured - expected if finite(measured) and finite(expected) else math.nan
        motion_verified = bool(finite(disp_error) and abs(disp_error) <= max(1e-8, abs(expected) * 0.05))
        result.update(
            {
                "extraction_status": "PASS",
                "postprocess_status": "PASS",
                "array_path": abspath(array_path),
                "point_count_initial": int(r0s.size),
                "point_count_final": int(rfs.size),
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
                "measured_ring_displacement_m": measured,
                "displacement_error_m": disp_error,
                "ring_motion_verified": str(motion_verified),
                "case_pass_after_recompute": str((not flag) and finite(h0) and finite(hf) and motion_verified),
            }
        )
        per_case_log(cid, "postprocess_pass")
    except Exception as exc:
        result.update({"exception_class": exc.__class__.__name__, "exception_message": str(exc)[:1000], "traceback": traceback.format_exc()[:2000]})
        per_case_log(cid, "extract_exception\n" + traceback.format_exc())
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
    max_abs = max([abs(v) for v in finite_values] + [1.0])
    zero_y = y0 + h // 2 if any(v < 0 for v in finite_values) else y0 + h
    draw.line((x0, zero_y, x0 + w, zero_y), fill=(80, 80, 80))
    bar_w = max(40, int(w / max(1, len(values) * 2)))
    for idx, (label, value) in enumerate(zip(labels, values)):
        bx0 = x0 + 45 + idx * (bar_w + 80)
        bx1 = bx0 + bar_w
        if finite(value):
            scale_h = h // 2 if any(v < 0 for v in finite_values) else h
            by = zero_y - int(scale_h * float(value) / max_abs)
            draw.rectangle((bx0, min(by, zero_y), bx1, max(by, zero_y)), fill=(67, 111, 191))
            draw.text((bx0 - 12, min(by, zero_y) - 22), f"{value:.3g}", fill=(0, 0, 0), font=small)
        draw.text((bx0 - 20, y0 + h + 18), label[:24], fill=(0, 0, 0), font=small)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return abspath(path)


def status_for_case(row: dict[str, str] | None) -> str:
    if not row:
        return "NOT_ATTEMPTED"
    if row.get("case_pass_after_recompute") == "True":
        return "PASS"
    if row.get("solve_status") or row.get("extraction_status") or row.get("postprocess_status"):
        return "FAIL"
    return "UNKNOWN"


def reviewer_figures(merged_rows: list[dict[str, str]], t008_rows: list[dict[str, str]]) -> list[str]:
    paths = []
    labels = [row.get("legacy_case_id", "") for row in merged_rows]
    disp_um = [float(row.get("measured_ring_displacement_m", "nan")) * 1e6 if finite(row.get("measured_ring_displacement_m")) else math.nan for row in merged_rows]
    paths.append(render_bars(OUT / "images" / "T008_ladder_displacement_response.png", labels, disp_um, "T008 diagnostic ladder measured displacement (um)"))
    err_nm = [float(row.get("displacement_error_m", "nan")) * 1e9 if finite(row.get("displacement_error_m")) else math.nan for row in t008_rows]
    paths.append(render_bars(OUT / "images" / "T008_ladder_error_summary.png", [row.get("legacy_case_id", "") for row in t008_rows], err_nm, "T008 displacement error (nm)"))
    quality_counts = Counter(row.get("interface_quality", "") for row in t008_rows)
    paths.append(render_bars(OUT / "images" / "T008_interface_quality_summary.png", list(quality_counts.keys()), [float(v) for v in quality_counts.values()], "T008 interface quality summary"))
    return paths


def merge_t007_t008(t008_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    t007_rows = read_csv(OUT / "tables" / "T007_recomputed_metrics.csv")
    merged = t007_rows + t008_rows
    write_csv(OUT / "tables" / "T008_merged_T007_T008_metrics.csv", merged, metric_columns())
    return merged


def monotonic_or_explained(merged_rows: list[dict[str, str]]) -> tuple[str, str]:
    rows = [row for row in merged_rows if finite(row.get("expected_displacement_m")) and finite(row.get("measured_ring_displacement_m"))]
    rows.sort(key=lambda row: float(row["expected_displacement_m"]), reverse=True)
    expected = [float(row["expected_displacement_m"]) for row in rows]
    measured = [float(row["measured_ring_displacement_m"]) for row in rows]
    ok = all(measured[i] >= measured[i + 1] - 1e-10 for i in range(len(measured) - 1))
    if ok:
        return "YES", "Measured displacement becomes more negative monotonically with expected diagnostic displacement."
    return "NO", f"Non-monotonic measured sequence for expected={expected}, measured={measured}."


def final_report(t008_rows: list[dict[str, str]], merged_rows: list[dict[str, str]], semantics_clear: bool, image_paths: list[str]) -> dict[str, str]:
    latest = {row.get("legacy_case_id"): row for row in t008_rows}
    d3 = status_for_case(latest.get("D3"))
    d4 = status_for_case(latest.get("D4"))
    d5 = status_for_case(latest.get("D5"))
    extraction_pass = sum(1 for row in t008_rows if row.get("extraction_status") == "PASS")
    post_pass = sum(1 for row in t008_rows if row.get("postprocess_status") == "PASS")
    all_pass = d3 == d4 == d5 == "PASS"
    monotonic_status, monotonic_note = monotonic_or_explained(merged_rows)
    gates = {
        "T008_STATUS": "PASS" if all_pass and monotonic_status == "YES" else "PARTIAL" if t008_rows else "FAIL",
        "D3_STATUS": d3,
        "D4_STATUS": d4,
        "D5_STATUS": d5,
        "D_LADDER_SEMANTICS_CLEAR": "YES" if semantics_clear else "NO",
        "RAW_ARRAY_EXTRACTION_COMPLETED": "YES" if extraction_pass == 3 else "PARTIAL" if extraction_pass else "NO",
        "POSTPROCESSING_MEMORY_ERROR_RESOLVED": "YES" if post_pass == len(t008_rows) and t008_rows else "PARTIAL" if post_pass else "NO",
        "INTERFACE_QUALITY_EXTRACTION_REPAIRED": "YES" if all(row.get("interface_quality") == "clear" for row in t008_rows) and t008_rows else "NO",
        "DISPLACEMENT_RESPONSE_MONOTONIC_OR_EXPLAINED": monotonic_status,
        "HMAX_IS_REAL_PHYSICAL_OUTPUT": "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "YES" if all_pass and monotonic_status == "YES" else "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    lines = [
        "# T008 Final Report",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: narrow diagnostic displacement ladder D3/D4/D5 only.",
        "- No Stage 6, broad parameter sweep, Jet1/Jet2 detection, or real physical Hmax output was performed.",
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
            "| case_id | Vring | expected_displacement_m | measured_ring_displacement_m | displacement_error_m | interface_quality | status | array_path |",
            "|---|---|---:|---:|---:|---|---|---|",
        ]
    )
    for row in t008_rows:
        lines.append(
            f"| `{row.get('case_id')}` | `{row.get('Vring')}` | `{row.get('expected_displacement_m')}` | `{row.get('measured_ring_displacement_m')}` | `{row.get('displacement_error_m')}` | `{row.get('interface_quality')}` | `{status_for_case(row)}` | `{row.get('array_path')}` |"
        )
    lines.extend(
        [
            "",
            "## Displacement Monotonicity",
            "",
            f"- `{monotonic_note}`",
            "",
            "## Figures",
            "",
        ]
    )
    if image_paths:
        lines.extend([f"- `{path}`" for path in image_paths])
    else:
        lines.append("- Images were not generated because no diagnostic metrics existed.")
    lines.extend(
        [
            "",
            "## Semantics Source",
            "",
            "- `06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T007_A_d0_d1_d2_semantics.md`",
            "- `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/models/D2_20260619_165307.mph`",
            "- New D3/D4/D5 cases changed only `Vring` relative to the D2 template.",
            "",
            "## Next Recommended Task",
            "",
            "- Review T008 diagnostic ladder. If accepted, Review Agent may decide whether a true-geometry Jet1 diagnostic task is justified; Stage 6 and real Hmax remain blocked.",
        ]
    )
    write_text(OUT / "reports" / "T008_final_report.md", "\n".join(lines) + "\n")
    write_json(OUT / "reports" / "T008_gate_summary.json", gates)
    return gates


def write_human_required(reason: str) -> dict[str, str]:
    gates = {
        "T008_STATUS": "HUMAN_REQUIRED",
        "D3_STATUS": "NOT_ATTEMPTED",
        "D4_STATUS": "NOT_ATTEMPTED",
        "D5_STATUS": "NOT_ATTEMPTED",
        "D_LADDER_SEMANTICS_CLEAR": "NO",
        "RAW_ARRAY_EXTRACTION_COMPLETED": "NO",
        "POSTPROCESSING_MEMORY_ERROR_RESOLVED": "NO",
        "INTERFACE_QUALITY_EXTRACTION_REPAIRED": "NO",
        "DISPLACEMENT_RESPONSE_MONOTONIC_OR_EXPLAINED": "NO",
        "HMAX_IS_REAL_PHYSICAL_OUTPUT": "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    write_text(OUT / "reports" / "T008_final_report.md", "# T008 Final Report\n\n" + "\n".join([f"- `{k} = {v}`" for k, v in gates.items()]) + f"\n\nReason: {reason}\n")
    write_json(OUT / "reports" / "T008_gate_summary.json", gates)
    return gates


def update_readme(gates: dict[str, str]) -> None:
    readme = ROOT / "README.md"
    start = "<!-- TRUE_GEOMETRY_R3_DIAGNOSTIC_DISPLACEMENT_REGRESSION:START -->"
    end = "<!-- TRUE_GEOMETRY_R3_DIAGNOSTIC_DISPLACEMENT_REGRESSION:END -->"
    block = "\n".join(
        [
            start,
            "## TRUE_GEOMETRY_R3_DIAGNOSTIC_DISPLACEMENT_REGRESSION",
            "",
            f"- Run id: `{RUN_ID}`",
            "- Scope: T007 D0/D1/D2 plus T008 narrow diagnostic D3/D4/D5 displacement ladder.",
            f"- T008 status: `{gates['T008_STATUS']}`",
            f"- `D3_STATUS = {gates['D3_STATUS']}`",
            f"- `D4_STATUS = {gates['D4_STATUS']}`",
            f"- `D5_STATUS = {gates['D5_STATUS']}`",
            f"- `D_LADDER_SEMANTICS_CLEAR = {gates['D_LADDER_SEMANTICS_CLEAR']}`",
            f"- `HMAX_IS_REAL_PHYSICAL_OUTPUT = {gates['HMAX_IS_REAL_PHYSICAL_OUTPUT']}`",
            f"- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = {gates['ALLOW_NEXT_TRUE_GEOMETRY_JET1']}`",
            f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
            f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
            f"- T008 final report: `{OUT / 'reports' / 'T008_final_report.md'}`",
            f"- T008 merged metrics: `{OUT / 'tables' / 'T008_merged_T007_T008_metrics.csv'}`",
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


def main() -> int:
    ensure_dirs()
    script_copy = OUT / "scripts" / "T008_narrow_displacement_ladder.py"
    if Path(__file__).resolve() != script_copy.resolve():
        shutil.copy2(Path(__file__).resolve(), script_copy)
    semantics_clear = write_semantics_report()
    if not semantics_clear:
        gates = write_human_required(f"Template model missing: {TEMPLATE_MODEL}")
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
            cid = str(case["case_id"])
            per_case_log(cid, f"start {datetime.now().isoformat(timespec='seconds')}")
            model = None
            try:
                model, model_path, java_path, solve_result = build_and_solve_case(client, case)
                row = extract_and_postprocess(model, case, model_path, java_path, solve_result) if model is not None else {
                    "case_id": cid,
                    "legacy_case_id": case["legacy_case_id"],
                    "Vring": case["Vring"],
                    "t_end": case["t_end"],
                    "dt": case["dt"],
                    "expected_displacement_m": case["expected_displacement_m"],
                    "model_path": solve_result.get("model_path", ""),
                    "java_path": solve_result.get("java_path", ""),
                    "solve_status": solve_result.get("solve_status", "FAILED"),
                    "extraction_status": "SKIPPED",
                    "postprocess_status": "SKIPPED",
                    "HMAX_IS_REAL_PHYSICAL_OUTPUT": "NO",
                    "exception_class": solve_result.get("exception_class", ""),
                    "exception_message": solve_result.get("exception_message", ""),
                }
            finally:
                if model is not None:
                    try:
                        client.remove(model)
                    except Exception:
                        pass
                gc.collect()
            append_csv(OUT / "tables" / "T008_progress.csv", {
                "case_id": row.get("case_id"),
                "legacy_case_id": row.get("legacy_case_id"),
                "model_path": row.get("model_path"),
                "model_exists": "YES" if row.get("model_path") and Path(str(row.get("model_path"))).exists() else "NO",
                "attempted": "YES",
                "solve_status": row.get("solve_status"),
                "extraction_status": row.get("extraction_status"),
                "postprocess_status": row.get("postprocess_status"),
                "output_array_path": row.get("array_path"),
                "notes": row.get("exception_message"),
            }, progress_columns())
            append_csv(OUT / "tables" / "T008_recomputed_metrics.csv", row, metric_columns())
            rows.append(row)
    finally:
        try:
            client.clear()
        except Exception:
            pass

    t008_rows = read_csv(OUT / "tables" / "T008_recomputed_metrics.csv")
    merged_rows = merge_t007_t008(t008_rows)
    image_paths = reviewer_figures(merged_rows, t008_rows) if t008_rows else []
    gates = final_report(t008_rows, merged_rows, semantics_clear, image_paths)
    update_readme(gates)
    return 0 if gates["T008_STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
