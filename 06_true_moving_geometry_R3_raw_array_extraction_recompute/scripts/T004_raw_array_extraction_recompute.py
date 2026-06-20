# -*- coding: utf-8 -*-
"""T004 resumable raw-array extraction and postprocessing recompute.

This script extracts compact sampled arrays from existing saved R3 .mph models
and recomputes memory-safe interface metrics case by case. It never runs a
study, Stage 6, Jet1/Jet2 detection, parameter sweeps, or real Hmax.
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
T003 = ROOT / "06_true_moving_geometry_R3_postprocessing_memory_repair"
T003_SCRIPT_DIR = T003 / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
MAX_SAMPLE_POINTS = 250_000

sys.path.insert(0, str(T003_SCRIPT_DIR))
import T003_postprocessing_memory_repair as t3  # noqa: E402


PRIORITY = [
    ("G2_ring_deeper_submerged", ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation" / "03_ring_geometry_position_controls" / "models" / "G2_ring_deeper_submerged_20260620_022152.mph"),
    ("G3_ring_far_below_surface", ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation" / "03_ring_geometry_position_controls" / "models" / "G3_ring_far_below_surface_20260620_022152.mph"),
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


def write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return abspath(path)


def write_json(path: Path, payload: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return abspath(path)


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


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def append_csv(path: Path, row: dict[str, Any], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        if not exists:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in columns})


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


def sample_array_triplet(r: np.ndarray, z: np.ndarray, phi: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, int, str]:
    original = int(min(r.size, z.size, phi.size))
    if original <= MAX_SAMPLE_POINTS:
        return r, z, phi, original, original, "exact_full_arrays"
    stride = int(math.ceil(original / MAX_SAMPLE_POINTS))
    return r[::stride], z[::stride], phi[::stride], original, int(r[::stride].size), f"downsampled_stride_{stride}"


def latest_array_path(priority: int, case_id: str) -> Path | None:
    matches = sorted((OUT / "arrays").glob(f"{priority:02d}_{case_id}_*.npz"))
    return matches[-1] if matches else None


def region_name(r: float, z: float, ri: float, ro: float, z_ring0: float, h_ring: float) -> str:
    if 0 <= r <= ri:
        return "center_hole"
    if ri - 0.002 <= r <= ri + 0.002:
        return "inner_edge"
    if ro - 0.002 <= r <= ro + 0.002:
        return "outer_edge"
    if ro + 0.005 <= r <= t3.RTANK - 0.005:
        return "farfield"
    if r >= t3.RTANK - 0.002:
        return "outer_wall_exclusion_zone"
    if ri <= r <= ro and abs(z - (z_ring0 + h_ring / 2)) <= 0.002:
        return "ring_top"
    return "global"


def interface_points_from_arrays(r: np.ndarray, z: np.ndarray, phi: np.ndarray, bins: int = 160) -> tuple[list[tuple[float, float]], dict[str, Any]]:
    original = int(min(r.size, z.size, phi.size))
    if original == 0:
        return [], {"point_count_original": 0, "point_count_used": 0, "postprocess_method": "npz_binned_crossing_160"}
    mask = (
        np.isfinite(r)
        & np.isfinite(z)
        & np.isfinite(phi)
        & (r >= 0.0)
        & (r <= t3.RTANK - 0.002)
        & (z >= t3.Z0 - 0.003)
        & (z <= t3.Z0 + 0.003)
    )
    rr = r[mask]
    zz = z[mask]
    pp = phi[mask]
    points: list[tuple[float, float]] = []
    edges = np.linspace(0.0, t3.RTANK - 0.002, bins + 1)
    for left, right in zip(edges[:-1], edges[1:]):
        sel = (rr >= left) & (rr < right)
        if np.count_nonzero(sel) < 2:
            continue
        rs = rr[sel]
        zs = zz[sel]
        ps = pp[sel]
        order = np.argsort(zs)
        rs = rs[order]
        zs = zs[order]
        ps = ps[order]
        crossings = np.where((ps[:-1] - 0.5) * (ps[1:] - 0.5) <= 0)[0]
        if crossings.size == 0:
            continue
        idx = int(crossings[np.argmin(np.abs(zs[crossings] - t3.Z0))])
        p0, p1 = ps[idx], ps[idx + 1]
        z0, z1 = zs[idx], zs[idx + 1]
        if abs(p1 - p0) > 1e-12:
            zi = z0 + (0.5 - p0) * (z1 - z0) / (p1 - p0)
        else:
            zi = 0.5 * (z0 + z1)
        points.append((float(np.nanmean(rs[idx : idx + 2])), float(zi)))
    return points, {"point_count_original": original, "point_count_used": int(rr.size), "postprocess_method": "npz_binned_crossing_160"}


def point_metrics(points: list[tuple[float, float]]) -> dict[str, Any]:
    if not points:
        return {
            "interface_points_count": 0,
            "H_median": math.nan,
            "roughness_peak_to_peak": math.nan,
            "max_slope": math.nan,
            "number_of_components": 0,
        }
    pts = sorted(points)
    rr = np.asarray([p[0] for p in pts], dtype=float)
    zz = np.asarray([p[1] for p in pts], dtype=float)
    if rr.size >= 2:
        dr = np.diff(rr)
        slopes = np.diff(zz) / np.where(np.abs(dr) > 1e-12, dr, np.nan)
        max_slope = float(np.nanmax(np.abs(slopes))) if np.any(np.isfinite(slopes)) else math.nan
    else:
        max_slope = math.nan
    return {
        "interface_points_count": int(rr.size),
        "H_median": float(np.nanmedian(zz)),
        "roughness_peak_to_peak": float(np.nanmax(zz) - np.nanmin(zz)),
        "max_slope": max_slope,
        "number_of_components": t3.split_components(pts),
    }


def summary_from_arrays(case_id: str, inner: int, time_s: float, r: np.ndarray, z: np.ndarray, phi: np.ndarray, ri: float, ro: float, z_ring0: float, h_ring: float) -> dict[str, Any]:
    points, meta = interface_points_from_arrays(r, z, phi)
    by_region: dict[str, list[tuple[float, float]]] = {
        "center_hole": [],
        "inner_edge": [],
        "ring_top": [],
        "outer_edge": [],
        "farfield": [],
        "outer_wall_exclusion_zone": [],
    }
    for r0, z0 in points:
        by_region.setdefault(region_name(r0, z0, ri, ro, z_ring0, h_ring), []).append((r0, z0))
    global_m = point_metrics(points)
    inner_m = point_metrics(by_region.get("inner_edge", []))
    outer_m = point_metrics(by_region.get("outer_edge", []))
    far_m = point_metrics(by_region.get("farfield", []))
    global_p2p = float(global_m["roughness_peak_to_peak"])
    max_slope = float(global_m["max_slope"])
    inner_p2p = float(inner_m["roughness_peak_to_peak"])
    outer_p2p = float(outer_m["roughness_peak_to_peak"])
    flag = bool(
        (not finite(global_m["H_median"]))
        or global_m["interface_points_count"] < 20
        or (finite(global_p2p) and global_p2p > 0.002)
        or (finite(max_slope) and max_slope > 12.0)
        or (finite(inner_p2p) and inner_p2p > 0.0015)
        or (finite(outer_p2p) and outer_p2p > 0.0015)
    )
    candidates = [
        ("inner_edge", inner_p2p),
        ("outer_edge", outer_p2p),
        ("farfield", float(far_m["roughness_peak_to_peak"])),
        ("global", global_p2p),
    ]
    finite_candidates = [(name, value) for name, value in candidates if finite(value)]
    principal = max(finite_candidates, key=lambda item: item[1])[0] if finite_candidates else "unresolved"
    return {
        **meta,
        "case_id": case_id,
        "inner": inner,
        "time": time_s,
        "H_median": global_m["H_median"],
        "roughness_peak_to_peak": global_p2p,
        "max_slope": max_slope,
        "pseudo_spike_regional_flag": flag,
        "principal_spike_region": principal,
        "regional_roughness_inner_edge": inner_p2p,
        "regional_roughness_outer_edge": outer_p2p,
        "regional_roughness_farfield": float(far_m["roughness_peak_to_peak"]),
        "interface_points_count": global_m["interface_points_count"],
    }


def case_params(case_id: str) -> tuple[float, float, float, float]:
    if case_id == "G2_ring_deeper_submerged":
        return 0.006, 0.012, -0.003, 0.002
    if case_id == "G3_ring_far_below_surface":
        return 0.006, 0.012, -0.006, 0.002
    return 0.006, 0.012, -0.002, 0.002


def progress_columns() -> list[str]:
    return [
        "case_id",
        "priority",
        "model_path",
        "model_exists",
        "attempted",
        "extraction_status",
        "postprocess_status",
        "output_array_path",
        "notes",
    ]


def metric_columns() -> list[str]:
    return [
        "case_id",
        "priority",
        "model_path",
        "extraction_status",
        "postprocess_status",
        "array_path",
        "point_count_original_initial",
        "point_count_used_initial",
        "point_count_original_final",
        "point_count_used_final",
        "array_method_initial",
        "array_method_final",
        "postprocess_method",
        "H0_recomputed",
        "Hfinal_recomputed",
        "H_final_minus_H0_recomputed",
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


def build_manifest() -> list[dict[str, Any]]:
    progress = {row.get("case_id"): row for row in read_csv(OUT / "tables" / "T004_progress.csv")}
    rows = []
    for idx, (case_id, model_path) in enumerate(PRIORITY, start=1):
        prev = progress.get(case_id, {})
        rows.append(
            {
                "case_id": case_id,
                "priority": idx,
                "model_path": abspath(model_path),
                "model_exists": "YES" if model_path.exists() else "NO",
                "attempted": prev.get("attempted", "NO"),
                "extraction_status": prev.get("extraction_status", "NOT_ATTEMPTED"),
                "postprocess_status": prev.get("postprocess_status", "NOT_ATTEMPTED"),
                "output_array_path": prev.get("output_array_path", ""),
                "notes": prev.get("notes", ""),
            }
        )
    return rows


def extraction_plan() -> None:
    write_csv(OUT / "tables" / "T004_case_manifest.csv", build_manifest(), progress_columns())
    lines = [
        "# T004-A Extraction Plan",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: raw-array extraction and postprocessing recompute from existing saved `.mph` models only.",
        "- No studies are run; no Stage 6, parameter sweep, Jet1/Jet2 detection, or real Hmax output is performed.",
        "- The script processes one model at a time and appends progress immediately after each case.",
        f"- Default case budget: `{os.environ.get('T004_MAX_CASES', '2')}` priority cases.",
        "",
        "## Priority Order",
        "",
    ]
    for idx, (case_id, model_path) in enumerate(PRIORITY, start=1):
        lines.append(f"{idx}. `{case_id}` -> `{model_path}` exists=`{model_path.exists()}`")
    write_text(OUT / "reports" / "T004_A_extraction_plan.md", "\n".join(lines) + "\n")


def per_case_log(case_id: str, text: str) -> None:
    path = OUT / "logs" / f"T004_{case_id}_{RUN_ID}.log"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text + "\n")


def process_case(client: Any, priority: int, case_id: str, model_path: Path) -> dict[str, Any]:
    model = None
    array_path = latest_array_path(priority, case_id) or (OUT / "arrays" / f"{priority:02d}_{case_id}_{RUN_ID}.npz")
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
        return result
    try:
        if not array_path.exists():
            model = client.load(str(model_path))
            per_case_log(case_id, "model_loaded")
            t0 = t3.scalar_time(model, 1)
            tf = t3.scalar_time(model, 51)
            r0 = t3.eval_array(model, "r", "m", 1)
            z0 = t3.eval_array(model, "z", "m", 1)
            p0 = t3.eval_array(model, "phils", "", 1)
            rf = t3.eval_array(model, "r", "m", 51)
            zf = t3.eval_array(model, "z", "m", 51)
            pf = t3.eval_array(model, "phils", "", 51)
            per_case_log(case_id, "arrays_evaluated")
            r0s, z0s, p0s, n0, u0, m0 = sample_array_triplet(r0, z0, p0)
            rfs, zfs, pfs, nf, uf, mf = sample_array_triplet(rf, zf, pf)
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
        ri, ro, z_ring0, h_ring = case_params(case_id)
        s0 = summary_from_arrays(case_id, 1, t0, r0s, z0s, p0s, ri, ro, z_ring0, h_ring)
        sf = summary_from_arrays(case_id, 51, tf, rfs, zfs, pfs, ri, ro, z_ring0, h_ring)
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
    width, height = 1100, 560
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
        small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    draw.text((30, 20), title, fill=(0, 0, 0), font=font)
    x0, y0, w, h = 80, 100, 940, 330
    draw.line((x0, y0 + h, x0 + w, y0 + h), fill=(0, 0, 0))
    draw.line((x0, y0, x0, y0 + h), fill=(0, 0, 0))
    finite_values = [v for v in values if finite(v)]
    max_v = max(finite_values + [1.0])
    bar_w = max(35, int(w / max(1, len(values) * 2)))
    for idx, (label, value) in enumerate(zip(labels, values)):
        bx0 = x0 + 40 + idx * (bar_w + 60)
        bx1 = bx0 + bar_w
        if finite(value):
            by1 = y0 + h
            by0 = by1 - int(h * float(value) / max_v)
            draw.rectangle((bx0, by0, bx1, by1), fill=(67, 111, 191))
            draw.text((bx0 - 10, by0 - 22), f"{value:.3g}", fill=(0, 0, 0), font=small)
        draw.text((bx0 - 20, y0 + h + 18), label[:22], fill=(0, 0, 0), font=small)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return abspath(path)


def reviewer_figures(metrics: list[dict[str, str]]) -> None:
    status_counts = Counter(row.get("extraction_status", "") for row in metrics)
    render_bars(OUT / "images" / "T004_extraction_status_summary.png", list(status_counts.keys()), [float(v) for v in status_counts.values()], "T004 extraction status summary")
    quality_counts = Counter(row.get("interface_quality", "") for row in metrics)
    render_bars(OUT / "images" / "T004_interface_quality_summary.png", list(quality_counts.keys()), [float(v) for v in quality_counts.values()], "T004 interface quality summary")
    labels = [row.get("case_id", "") for row in metrics]
    rough = [float(row.get("regional_roughness", "nan")) * 1e6 if finite(row.get("regional_roughness")) else math.nan for row in metrics]
    render_bars(OUT / "images" / "T004_regional_roughness_summary.png", labels, rough, "T004 regional roughness summary (um)")


def final_report(metrics: list[dict[str, str]]) -> dict[str, str]:
    attempted = len(metrics)
    extraction_pass = sum(1 for row in metrics if row.get("extraction_status") == "PASS")
    post_pass = sum(1 for row in metrics if row.get("postprocess_status") == "PASS")
    total_priority = len(PRIORITY)
    raw_status = "YES" if extraction_pass == total_priority else "PARTIAL" if extraction_pass else "NO"
    mem_status = "YES" if post_pass == attempted and attempted > 0 else "PARTIAL" if post_pass else "NO"
    iq_status = "YES" if post_pass == attempted and attempted > 0 else "PARTIAL" if post_pass else "NO"
    static_baseline = "NO"
    micro_baseline = "UNKNOWN"
    t004_status = "PASS" if raw_status == "YES" and post_pass == total_priority else "PARTIAL" if attempted else "FAIL"
    gates = {
        "T004_STATUS": t004_status,
        "RAW_ARRAY_EXTRACTION_COMPLETED": raw_status,
        "POSTPROCESSING_MEMORY_ERROR_RESOLVED": mem_status,
        "INTERFACE_QUALITY_EXTRACTION_REPAIRED": iq_status,
        "CREDIBLE_STATIC_BASELINE_AFTER_RECOMPUTE": static_baseline,
        "CREDIBLE_MICRO_MOTION_BASELINE_AFTER_RECOMPUTE": micro_baseline,
        "ALLOW_NEXT_DISPLACEMENT_LADDER": "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    lines = [
        "# T004 Final Report",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: raw-array extraction and postprocessing recompute from saved models only.",
        "- No COMSOL study, Stage 6, parameter sweep, Jet1/Jet2 detection, or real Hmax output was performed.",
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
            f"- Attempted cases: `{attempted}`",
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
            "## Next Recommended Task",
            "",
            "- Continue resumable T004 extraction for remaining priority cases if Review Agent needs W10/W0/contact-angle/slip rows. Stage advancement remains blocked.",
        ]
    )
    write_text(OUT / "reports" / "T004_final_report.md", "\n".join(lines) + "\n")
    write_json(OUT / "reports" / "T004_gate_summary.json", gates)
    return gates


def latest_metrics_by_case(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for row in rows:
        case_id = row.get("case_id", "")
        if case_id:
            latest[case_id] = row
    ordered = []
    for case_id, _ in PRIORITY:
        if case_id in latest:
            ordered.append(latest[case_id])
    return ordered


def update_readme(gates: dict[str, str], attempted: int) -> None:
    readme = ROOT / "README.md"
    start = "<!-- TRUE_GEOMETRY_R3_RAW_ARRAY_EXTRACTION_RECOMPUTE:START -->"
    end = "<!-- TRUE_GEOMETRY_R3_RAW_ARRAY_EXTRACTION_RECOMPUTE:END -->"
    block = "\n".join(
        [
            start,
            "## TRUE_GEOMETRY_R3_RAW_ARRAY_EXTRACTION_RECOMPUTE",
            "",
            f"- Run id: `{RUN_ID}`",
            "- Scope: raw-array extraction plus postprocessing recompute from existing saved models.",
            f"- Attempted priority cases: `{attempted}`",
            f"- T004 status: `{gates['T004_STATUS']}`",
            f"- `RAW_ARRAY_EXTRACTION_COMPLETED = {gates['RAW_ARRAY_EXTRACTION_COMPLETED']}`",
            f"- `POSTPROCESSING_MEMORY_ERROR_RESOLVED = {gates['POSTPROCESSING_MEMORY_ERROR_RESOLVED']}`",
            f"- `INTERFACE_QUALITY_EXTRACTION_REPAIRED = {gates['INTERFACE_QUALITY_EXTRACTION_REPAIRED']}`",
            f"- `ALLOW_NEXT_DISPLACEMENT_LADDER = {gates['ALLOW_NEXT_DISPLACEMENT_LADDER']}`",
            f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
            f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
            f"- Final report: `{OUT / 'reports' / 'T004_final_report.md'}`",
            f"- Progress table: `{OUT / 'tables' / 'T004_progress.csv'}`",
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
    script_copy = OUT / "scripts" / "T004_raw_array_extraction_recompute.py"
    if Path(__file__).resolve() != script_copy.resolve():
        shutil.copy2(Path(__file__).resolve(), script_copy)
    extraction_plan()

    max_cases = int(os.environ.get("T004_MAX_CASES", "2"))
    existing_metrics = read_csv(OUT / "tables" / "T004_recomputed_metrics.csv")
    done = {row.get("case_id") for row in existing_metrics if row.get("extraction_status") == "PASS"}
    attempted_this_run = 0
    client = mph.Client(cores=2, version="6.4")
    try:
        for priority, (case_id, model_path) in enumerate(PRIORITY, start=1):
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
                "attempted": "YES",
                "extraction_status": result.get("extraction_status", ""),
                "postprocess_status": result.get("postprocess_status", ""),
                "output_array_path": result.get("array_path", ""),
                "notes": result.get("exception_message", ""),
            }
            append_csv(OUT / "tables" / "T004_progress.csv", progress, progress_columns())
            append_csv(OUT / "tables" / "T004_recomputed_metrics.csv", result, metric_columns())
            existing_metrics.append({key: str(result.get(key, "")) for key in metric_columns()})
            write_csv(OUT / "tables" / "T004_case_manifest.csv", build_manifest(), progress_columns())
    finally:
        try:
            client.clear()
        except Exception:
            pass

    metrics = latest_metrics_by_case(read_csv(OUT / "tables" / "T004_recomputed_metrics.csv"))
    reviewer_figures(metrics)
    gates = final_report(metrics)
    update_readme(gates, len(metrics))
    return 0 if gates["T004_STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
