# -*- coding: utf-8 -*-
"""T007 diagnostic D0/D1/D2 displacement regression.

Loads existing R1 D0/D1/D2 saved models and applies the repaired T004 bounded
raw-array extraction/postprocessing path. No COMSOL studies are run, no Stage 6
is entered, and no real Hmax is reported.
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
OUT = ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression"
RAW = ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute"
R1_D = ROOT / "06_true_moving_geometry_R1_diagnostic_repair" / "03_zero_motion_regression"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

sys.path.insert(0, str(RAW / "scripts"))
import T004_raw_array_extraction_recompute as t4  # noqa: E402


CASES = [
    {
        "case_id": "D0_zero_motion_regression",
        "legacy_case_id": "D0",
        "Vring": "0[m/s]",
        "Vring_m_per_s": 0.0,
        "t_end": "0.005[s]",
        "dt": "1e-4[s]",
        "expected_displacement_m": -0.0,
        "model_path": R1_D / "models" / "D0_20260619_165307.mph",
        "java_path": R1_D / "exports" / "D0_20260619_165307.java",
    },
    {
        "case_id": "D1_micro_motion_regression",
        "legacy_case_id": "D1",
        "Vring": "1e-4[m/s]",
        "Vring_m_per_s": 1e-4,
        "t_end": "0.005[s]",
        "dt": "1e-4[s]",
        "expected_displacement_m": -5e-7,
        "model_path": R1_D / "models" / "D1_20260619_165307.mph",
        "java_path": R1_D / "exports" / "D1_20260619_165307.java",
    },
    {
        "case_id": "D2_micro_motion_regression",
        "legacy_case_id": "D2",
        "Vring": "1e-3[m/s]",
        "Vring_m_per_s": 1e-3,
        "t_end": "0.005[s]",
        "dt": "1e-4[s]",
        "expected_displacement_m": -5e-6,
        "model_path": R1_D / "models" / "D2_20260619_165307.mph",
        "java_path": R1_D / "exports" / "D2_20260619_165307.java",
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
            writer.writerow({key: json.dumps(row.get(key), ensure_ascii=False, default=str) if isinstance(row.get(key), (list, tuple, dict)) else row.get(key, "") for key in columns})
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


def progress_columns() -> list[str]:
    return [
        "case_id",
        "legacy_case_id",
        "model_path",
        "model_exists",
        "attempted",
        "extraction_status",
        "postprocess_status",
        "output_array_path",
        "notes",
    ]


def manifest_columns() -> list[str]:
    return [
        "case_id",
        "legacy_case_id",
        "Vring",
        "t_end",
        "dt",
        "expected_displacement_m",
        "model_path",
        "model_exists",
        "java_path",
        "java_exists",
        "semantics_source",
        "semantics_exact_match_r1",
        "ambiguity",
    ]


def per_case_log(case_id: str, text: str) -> None:
    with (OUT / "logs" / f"T007_{case_id}_{RUN_ID}.log").open("a", encoding="utf-8") as handle:
        handle.write(text + "\n")


def semantics_recovered() -> bool:
    for case in CASES:
        if not Path(case["model_path"]).exists() or not Path(case["java_path"]).exists():
            return False
        java_text = Path(case["java_path"]).read_text(encoding="utf-8", errors="replace")
        required = [
            f'model.param().set("Vring", "{case["Vring"]}")',
            'model.param().set("t_end", "0.005[s]")',
            'model.param().set("dt", "1e-4[s]")',
            'set("dx", new String[]{"0", "-Vring*t"})',
            'set("utr", new String[]{"0", "-Vring", "0"})',
        ]
        if not all(item in java_text for item in required):
            return False
    return True


def write_semantics_report() -> None:
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
                "model_path": abspath(Path(case["model_path"])),
                "model_exists": "YES" if Path(case["model_path"]).exists() else "NO",
                "java_path": abspath(Path(case["java_path"])),
                "java_exists": "YES" if Path(case["java_path"]).exists() else "NO",
                "semantics_source": "R1 D_zero_and_micro_motion_cases.csv plus D0/D1/D2 Java exports",
                "semantics_exact_match_r1": "YES" if semantics_recovered() else "NO",
                "ambiguity": "NO" if semantics_recovered() else "YES",
            }
        )
    write_csv(OUT / "tables" / "T007_case_manifest.csv", rows, manifest_columns())
    lines = [
        "# T007-A D0/D1/D2 Semantics",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Historical report: `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/reports/D_zero_and_micro_motion_regression_report.md`.",
        "- Historical table: `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/tables/D_zero_and_micro_motion_cases.csv`.",
        "- Java exports inspected: `D0_20260619_165307.java`, `D1_20260619_165307.java`, `D2_20260619_165307.java`.",
        f"- `D0_D1_D2_SEMANTICS_RECOVERED = {'YES' if semantics_recovered() else 'NO'}`",
        "- Baseline candidate used for interpretation: repaired R3 raw-array baseline/control package from T004/T005/T006, especially merged table `T006_merged_T004_T005_T006_metrics.csv`.",
        "- No ambiguity remains." if semantics_recovered() else "- Ambiguity remains; no D-case run should proceed.",
        "",
        "## Recovered Definitions",
        "",
        "| case_id | legacy_id | Vring | t_end | dt | ALE displacement | WettedWall velocity | expected displacement |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for case in CASES:
        lines.append(f"| `{case['case_id']}` | `{case['legacy_case_id']}` | `{case['Vring']}` | `{case['t_end']}` | `{case['dt']}` | `dx=[0,-Vring*t]` | `utr=[0,-Vring,0]` | `{case['expected_displacement_m']}` |")
    write_text(OUT / "reports" / "T007_A_d0_d1_d2_semantics.md", "\n".join(lines) + "\n")


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


def process_case(client: Any, case: dict[str, Any]) -> dict[str, Any]:
    cid = str(case["case_id"])
    model_path = Path(case["model_path"])
    array_path = OUT / "arrays" / f"T007_{cid}_{RUN_ID}.npz"
    result = {
        "case_id": cid,
        "legacy_case_id": case["legacy_case_id"],
        "Vring": case["Vring"],
        "t_end": case["t_end"],
        "dt": case["dt"],
        "expected_displacement_m": case["expected_displacement_m"],
        "model_path": abspath(model_path),
        "extraction_status": "FAILED",
        "postprocess_status": "FAILED",
        "array_path": "",
        "HMAX_IS_REAL_PHYSICAL_OUTPUT": "NO",
        "exception_class": "",
        "exception_message": "",
    }
    model = None
    per_case_log(cid, f"start {datetime.now().isoformat(timespec='seconds')}")
    if not model_path.exists():
        result.update({"extraction_status": "MODEL_MISSING", "postprocess_status": "SKIPPED", "exception_message": "model path missing"})
        per_case_log(cid, "model_missing")
        return result
    try:
        model = client.load(str(model_path))
        per_case_log(cid, "model_loaded")
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
        try:
            client.remove(model)
        except Exception:
            pass
        model = None
        gc.collect()

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
        per_case_log(cid, "exception\n" + traceback.format_exc())
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
    max_abs = max([abs(v) for v in finite_values] + [1.0])
    zero_y = y0 + h // 2 if any(v < 0 for v in finite_values) else y0 + h
    draw.line((x0, zero_y, x0 + w, zero_y), fill=(80, 80, 80))
    bar_w = max(40, int(w / max(1, len(values) * 2)))
    for idx, (label, value) in enumerate(zip(labels, values)):
        bx0 = x0 + 60 + idx * (bar_w + 90)
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
    if row.get("extraction_status") or row.get("postprocess_status"):
        return "FAIL"
    return "UNKNOWN"


def reviewer_figures(rows: list[dict[str, str]]) -> None:
    status_counts = Counter(row.get("case_pass_after_recompute", "") for row in rows)
    render_bars(OUT / "images" / "T007_d0_d1_d2_status_summary.png", list(status_counts.keys()), [float(v) for v in status_counts.values()], "T007 D0/D1/D2 pass status")
    labels = [row.get("legacy_case_id", "") for row in rows]
    disp_um = [float(row.get("measured_ring_displacement_m", "nan")) * 1e6 if finite(row.get("measured_ring_displacement_m")) else math.nan for row in rows]
    render_bars(OUT / "images" / "T007_displacement_response_summary.png", labels, disp_um, "T007 measured ring displacement (um)")
    quality_counts = Counter(row.get("interface_quality", "") for row in rows)
    render_bars(OUT / "images" / "T007_interface_quality_summary.png", list(quality_counts.keys()), [float(v) for v in quality_counts.values()], "T007 interface quality summary")


def final_report(rows: list[dict[str, str]]) -> dict[str, str]:
    latest = {row.get("legacy_case_id"): row for row in rows}
    extraction_pass = sum(1 for row in rows if row.get("extraction_status") == "PASS")
    post_pass = sum(1 for row in rows if row.get("postprocess_status") == "PASS")
    d0 = status_for_case(latest.get("D0"))
    d1 = status_for_case(latest.get("D1"))
    d2 = status_for_case(latest.get("D2"))
    all_pass = d0 == d1 == d2 == "PASS"
    gates = {
        "T007_STATUS": "PASS" if all_pass else "PARTIAL" if rows else "FAIL",
        "D0_STATUS": d0,
        "D1_STATUS": d1,
        "D2_STATUS": d2,
        "D0_D1_D2_SEMANTICS_RECOVERED": "YES" if semantics_recovered() else "NO",
        "RAW_ARRAY_EXTRACTION_COMPLETED": "YES" if extraction_pass == 3 else "PARTIAL" if extraction_pass else "NO",
        "POSTPROCESSING_MEMORY_ERROR_RESOLVED": "YES" if post_pass == len(rows) and rows else "PARTIAL" if post_pass else "NO",
        "INTERFACE_QUALITY_EXTRACTION_REPAIRED": "YES" if all(row.get("interface_quality") == "clear" for row in rows) and rows else "NO",
        "HMAX_IS_REAL_PHYSICAL_OUTPUT": "NO",
        "ALLOW_NEXT_DISPLACEMENT_LADDER": "YES" if all_pass else "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    lines = [
        "# T007 Final Report",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: diagnostic D0/D1/D2 displacement regression using repaired raw-array/postprocessing only.",
        "- No COMSOL study, Stage 6, broad parameter sweep, Jet1/Jet2 detection, or real Hmax output was performed.",
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
            "| case_id | Vring | expected_displacement_m | measured_ring_displacement_m | interface_quality | status | array_path |",
            "|---|---|---:|---:|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(f"| `{row.get('case_id')}` | `{row.get('Vring')}` | `{row.get('expected_displacement_m')}` | `{row.get('measured_ring_displacement_m')}` | `{row.get('interface_quality')}` | `{status_for_case(row)}` | `{row.get('array_path')}` |")
    lines.extend(
        [
            "",
            "## Semantics Source",
            "",
            "- `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/tables/D_zero_and_micro_motion_cases.csv`",
            "- `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/exports/D0_20260619_165307.java`",
            "- `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/exports/D1_20260619_165307.java`",
            "- `06_true_moving_geometry_R1_diagnostic_repair/03_zero_motion_regression/exports/D2_20260619_165307.java`",
            "",
            "## Next Recommended Task",
            "",
            "- Review T007 diagnostics. If accepted, the next task may be a narrow diagnostic displacement ladder; Stage 6, Jet1, and real Hmax remain blocked.",
        ]
    )
    write_text(OUT / "reports" / "T007_final_report.md", "\n".join(lines) + "\n")
    write_json(OUT / "reports" / "T007_gate_summary.json", gates)
    return gates


def write_human_required_package(reason: str) -> dict[str, str]:
    gates = {
        "T007_STATUS": "HUMAN_REQUIRED",
        "D0_STATUS": "NOT_ATTEMPTED",
        "D1_STATUS": "NOT_ATTEMPTED",
        "D2_STATUS": "NOT_ATTEMPTED",
        "D0_D1_D2_SEMANTICS_RECOVERED": "NO",
        "RAW_ARRAY_EXTRACTION_COMPLETED": "NO",
        "POSTPROCESSING_MEMORY_ERROR_RESOLVED": "NO",
        "INTERFACE_QUALITY_EXTRACTION_REPAIRED": "NO",
        "HMAX_IS_REAL_PHYSICAL_OUTPUT": "NO",
        "ALLOW_NEXT_DISPLACEMENT_LADDER": "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    write_text(OUT / "reports" / "T007_final_report.md", "# T007 Final Report\n\n" + "\n".join([f"- `{k} = {v}`" for k, v in gates.items()]) + f"\n\nReason: {reason}\n")
    write_json(OUT / "reports" / "T007_gate_summary.json", gates)
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
            "- Scope: diagnostic D0/D1/D2 regression with repaired raw-array/postprocessing.",
            f"- T007 status: `{gates['T007_STATUS']}`",
            f"- `D0_STATUS = {gates['D0_STATUS']}`",
            f"- `D1_STATUS = {gates['D1_STATUS']}`",
            f"- `D2_STATUS = {gates['D2_STATUS']}`",
            f"- `HMAX_IS_REAL_PHYSICAL_OUTPUT = {gates['HMAX_IS_REAL_PHYSICAL_OUTPUT']}`",
            f"- `ALLOW_NEXT_DISPLACEMENT_LADDER = {gates['ALLOW_NEXT_DISPLACEMENT_LADDER']}`",
            f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
            f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
            f"- Final report: `{OUT / 'reports' / 'T007_final_report.md'}`",
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
        "active_task_archive": "tasks/20260620_154500_T007_diagnostic_d0_d1_d2_displacement_regression.md",
        "executed": "YES",
        "pushed": "PENDING",
        "commit_sha": "",
        "notes": "T007 executed or stopped after semantics recovery; commit SHA filled after push.",
    }
    append_csv(ROOT / "tasks" / "BUILDER_POLLING_LOG.csv", row, ["round_start_time", "active_task", "active_task_archive", "executed", "pushed", "commit_sha", "notes"])


def main() -> int:
    ensure_dirs()
    script_copy = OUT / "scripts" / "T007_d0_d1_d2_displacement_regression.py"
    if Path(__file__).resolve() != script_copy.resolve():
        shutil.copy2(Path(__file__).resolve(), script_copy)
    write_semantics_report()
    if not semantics_recovered():
        gates = write_human_required_package("D0/D1/D2 Java/table semantics could not be exactly recovered.")
        update_readme(gates)
        update_polling_log()
        return 1

    client = mph.Client(cores=2, version="6.4")
    try:
        for case in CASES:
            result = process_case(client, case)
            append_csv(OUT / "tables" / "T007_progress.csv", {
                "case_id": result.get("case_id"),
                "legacy_case_id": result.get("legacy_case_id"),
                "model_path": result.get("model_path"),
                "model_exists": "YES" if Path(str(case["model_path"])).exists() else "NO",
                "attempted": "YES",
                "extraction_status": result.get("extraction_status"),
                "postprocess_status": result.get("postprocess_status"),
                "output_array_path": result.get("array_path"),
                "notes": result.get("exception_message"),
            }, progress_columns())
            append_csv(OUT / "tables" / "T007_recomputed_metrics.csv", result, metric_columns())
    finally:
        try:
            client.clear()
        except Exception:
            pass
    rows = read_csv(OUT / "tables" / "T007_recomputed_metrics.csv")
    reviewer_figures(rows)
    gates = final_report(rows)
    update_readme(gates)
    update_polling_log()
    return 0 if gates["T007_STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
