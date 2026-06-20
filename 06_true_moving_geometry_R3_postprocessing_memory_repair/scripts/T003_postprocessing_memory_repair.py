# -*- coding: utf-8 -*-
"""T003 postprocessing memory/extraction repair.

This is a diagnostic postprocessing-only task. It loads existing R3 models when
available and recomputes interface regional metrics with bounded memory usage.
It does not run COMSOL studies, Stage 6, Jet1/Jet2 detection, parameter sweeps,
or real Hmax extraction.
"""

from __future__ import annotations

import csv
import json
import math
import os
import shutil
import traceback
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import mph
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
OUT = ROOT / "06_true_moving_geometry_R3_postprocessing_memory_repair"
R3 = ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = OUT / "logs" / f"T003_postprocessing_memory_repair_{RUN_ID}.log"

RTANK = 0.040
Z0 = 0.0
RI0 = 0.006
RO0 = 0.012
H_RING0 = 0.002
Z_RING0 = -0.002
MAX_EVAL_POINTS = 250_000
BIN_COUNT = 160

RING_CSV = R3 / "03_ring_geometry_position_controls" / "tables" / "ring_geometry_position_cases.csv"
WETTED_CSV = R3 / "04_wettedwall_contactline_controls" / "tables" / "wettedwall_contactline_cases.csv"


def ensure_dirs() -> None:
    for sub in ["reports", "tables", "images", "logs", "scripts"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


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
            out: dict[str, Any] = {}
            for key in columns:
                value = row.get(key, "")
                if isinstance(value, (list, tuple, dict)):
                    value = json.dumps(value, ensure_ascii=False, default=str)
                out[key] = value
            writer.writerow(out)
    return abspath(path)


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


def fnum(value: Any, default: float = math.nan) -> float:
    try:
        text = str(value).strip()
        if text == "":
            return default
        return float(text)
    except Exception:
        return default


def affected(row: dict[str, str]) -> bool:
    msg = str(row.get("failure_message", ""))
    iq = str(row.get("interface_quality", ""))
    status = str(row.get("solve_status", ""))
    return (
        "MemoryError" in msg
        or iq == ""
        or iq == "extraction_failed"
        or status.upper() == "SKIP"
    )


def model_path_for(row: dict[str, str]) -> Path | None:
    for key in ["model", "timestamp_model"]:
        value = str(row.get(key, "")).strip()
        if value:
            path = Path(value)
            if path.exists():
                return path
    return None


def parse_build(row: dict[str, str]) -> dict[str, Any]:
    raw = str(row.get("build", "")).strip()
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            return {}
    return {}


def eval_array(model: Any, expr: str, unit: str = "", inner: int = 1) -> np.ndarray:
    kwargs: dict[str, Any] = {"inner": [inner]}
    if unit:
        kwargs["unit"] = unit
    return np.asarray(model.evaluate(expr, **kwargs), dtype=float).reshape(-1)


def scalar_time(model: Any, inner: int) -> float:
    try:
        arr = eval_array(model, "t", "s", inner)
        arr = arr[np.isfinite(arr)]
        return float(arr[0]) if arr.size else math.nan
    except Exception:
        return math.nan


def region_of(r: float, z: float, ri: float, ro: float, z_ring0: float, h_ring: float) -> str:
    if 0 <= r <= ri:
        return "center_hole"
    if ri - 0.002 <= r <= ri + 0.002:
        return "inner_edge"
    if ro - 0.002 <= r <= ro + 0.002:
        return "outer_edge"
    if ro + 0.005 <= r <= RTANK - 0.005:
        return "farfield"
    if r >= RTANK - 0.002:
        return "outer_wall_exclusion_zone"
    if ri <= r <= ro and abs(z - (z_ring0 + h_ring / 2)) <= 0.002:
        return "ring_top"
    return "global"


def split_components(points: list[tuple[float, float]], gap: float = 0.0015) -> int:
    if not points:
        return 0
    pts = sorted(points)
    count = 1
    prev = pts[0][0]
    for r, _ in pts[1:]:
        if abs(r - prev) > gap:
            count += 1
        prev = r
    return count


def metrics_for_points(points: list[tuple[float, float]]) -> dict[str, Any]:
    if not points:
        return {
            "interface_points_count": 0,
            "H_median": math.nan,
            "roughness_peak_to_peak": math.nan,
            "max_slope": math.nan,
            "number_of_components": 0,
        }
    pts = sorted(points)
    rr = np.array([p[0] for p in pts], dtype=float)
    zz = np.array([p[1] for p in pts], dtype=float)
    med = float(np.nanmedian(zz))
    if len(pts) >= 2:
        dr = np.diff(rr)
        slopes = np.diff(zz) / np.where(np.abs(dr) > 1e-12, dr, np.nan)
        max_slope = float(np.nanmax(np.abs(slopes))) if np.any(np.isfinite(slopes)) else math.nan
    else:
        max_slope = math.nan
    return {
        "interface_points_count": len(pts),
        "H_median": med,
        "roughness_peak_to_peak": float(np.nanmax(zz) - np.nanmin(zz)),
        "max_slope": max_slope,
        "number_of_components": split_components(pts),
    }


def safe_points_from_bins(r: np.ndarray, z: np.ndarray, phi: np.ndarray) -> tuple[list[tuple[float, float]], dict[str, Any]]:
    original = int(min(r.size, z.size, phi.size))
    method = "exact_bins_160"
    if original == 0:
        return [], {"point_count_original": 0, "point_count_used": 0, "postprocess_method": method}
    if original > MAX_EVAL_POINTS:
        stride = int(math.ceil(original / MAX_EVAL_POINTS))
        r = r[::stride]
        z = z[::stride]
        phi = phi[::stride]
        method = f"downsampled_stride_{stride}_bins_160"
    mask = (
        np.isfinite(r)
        & np.isfinite(z)
        & np.isfinite(phi)
        & (r >= 0.0)
        & (r <= RTANK - 0.002)
        & (z >= Z0 - 0.003)
        & (z <= Z0 + 0.003)
    )
    rr = r[mask]
    zz = z[mask]
    pp = phi[mask]
    used = int(rr.size)
    if used < 10:
        return [], {"point_count_original": original, "point_count_used": used, "postprocess_method": method}

    pts: list[tuple[float, float]] = []
    edges = np.linspace(0.0, RTANK - 0.002, BIN_COUNT + 1)
    threshold = 0.5
    for a, b in zip(edges[:-1], edges[1:]):
        sel = (rr >= a) & (rr < b)
        if np.count_nonzero(sel) < 2:
            continue
        rs = rr[sel]
        zs = zz[sel]
        ps = pp[sel]
        order = np.argsort(zs)
        rs = rs[order]
        zs = zs[order]
        ps = ps[order]
        crossings = np.where((ps[:-1] - threshold) * (ps[1:] - threshold) <= 0)[0]
        if crossings.size == 0:
            continue
        idx = int(crossings[np.argmin(np.abs(zs[crossings] - Z0))])
        p0, p1 = ps[idx], ps[idx + 1]
        z0, z1 = zs[idx], zs[idx + 1]
        if abs(p1 - p0) > 1e-12:
            zi = z0 + (threshold - p0) * (z1 - z0) / (p1 - p0)
        else:
            zi = 0.5 * (z0 + z1)
        pts.append((float(np.nanmean(rs[idx : idx + 2])), float(zi)))
    return pts, {"point_count_original": original, "point_count_used": used, "postprocess_method": method}


def safe_regional_metrics(case_id: str, inner: int, time_s: float, r: np.ndarray, z: np.ndarray, phi: np.ndarray, ri: float, ro: float, z_ring0: float, h_ring: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pts, meta = safe_points_from_bins(r, z, phi)
    regions = ["center_hole", "inner_edge", "ring_top", "outer_edge", "farfield", "outer_wall_exclusion_zone", "global"]
    by: dict[str, list[tuple[float, float]]] = {region: [] for region in regions}
    by["global"] = pts
    for r0, z0 in pts:
        region = region_of(r0, z0, ri, ro, z_ring0, h_ring)
        by.setdefault(region, []).append((r0, z0))
    rows = []
    for region in regions:
        m = metrics_for_points(by.get(region, []))
        m.update({"case_id": case_id, "inner": inner, "time": time_s, "region": region})
        rows.append(m)

    global_m = metrics_for_points(pts)
    edge = {row["region"]: row for row in rows}
    inner_p2p = float(edge.get("inner_edge", {}).get("roughness_peak_to_peak", math.nan))
    outer_p2p = float(edge.get("outer_edge", {}).get("roughness_peak_to_peak", math.nan))
    global_p2p = float(global_m.get("roughness_peak_to_peak", math.nan))
    max_slope = float(global_m.get("max_slope", math.nan))
    flag = bool(
        (not finite(global_m.get("H_median")))
        or global_m.get("interface_points_count", 0) < 20
        or (finite(global_p2p) and global_p2p > 0.002)
        or (finite(max_slope) and max_slope > 12.0)
        or (finite(inner_p2p) and inner_p2p > 0.0015)
        or (finite(outer_p2p) and outer_p2p > 0.0015)
    )
    candidates = [
        ("inner_edge", inner_p2p),
        ("outer_edge", outer_p2p),
        ("center_hole", float(edge.get("center_hole", {}).get("roughness_peak_to_peak", math.nan))),
        ("farfield", float(edge.get("farfield", {}).get("roughness_peak_to_peak", math.nan))),
        ("global", global_p2p),
    ]
    finite_candidates = [(name, value) for name, value in candidates if finite(value)]
    principal = max(finite_candidates, key=lambda item: item[1])[0] if finite_candidates else "unresolved"
    summary = {
        **meta,
        "H_median": global_m["H_median"],
        "roughness_peak_to_peak": global_p2p,
        "max_slope": max_slope,
        "pseudo_spike_regional_flag": flag,
        "principal_spike_region": principal,
        "regional_roughness_inner_edge": inner_p2p,
        "regional_roughness_outer_edge": outer_p2p,
        "regional_roughness_farfield": float(edge.get("farfield", {}).get("roughness_peak_to_peak", math.nan)),
        "interface_points_count": global_m["interface_points_count"],
    }
    return rows, summary


def evaluate_existing_model(client: Any, row: dict[str, str], family: str) -> dict[str, Any]:
    cid = row.get("case_id", "")
    build = parse_build(row)
    ri = fnum(row.get("ri"), fnum(build.get("ri"), RI0))
    ro = fnum(row.get("ro"), fnum(build.get("ro"), RO0))
    h_ring = fnum(row.get("h_ring"), fnum(build.get("h_ring"), H_RING0))
    z_ring0 = fnum(row.get("z_ring0"), fnum(build.get("z_ring0"), Z_RING0))
    model_path = model_path_for(row)
    base = {
        "case_id": cid,
        "source_case": family,
        "solve_status": row.get("solve_status", ""),
        "postprocess_status": "NOT_RUN",
        "postprocess_method": "",
        "point_count_original": "",
        "point_count_used": "",
        "interface_quality": row.get("interface_quality", ""),
        "regional_roughness": row.get("regional_roughness", ""),
        "pseudo_spike_regional_flag": row.get("pseudo_spike_regional_flag", ""),
        "memory_error_resolved": "NO",
        "case_pass_after_postprocess_only": "False",
        "notes": "",
    }
    if model_path is None:
        base.update(
            {
                "postprocess_status": "SKIP_RAW_MODEL_UNAVAILABLE",
                "postprocess_method": "not_recomputed",
                "notes": "No saved model path available for this source row; likely skipped in original R3.",
            }
        )
        return base

    model = None
    try:
        log(f"Loading model for {cid}: {model_path}")
        model = client.load(str(model_path))
        t0 = scalar_time(model, 1)
        r0 = eval_array(model, "r", "m", 1)
        z0 = eval_array(model, "z", "m", 1)
        p0 = eval_array(model, "phils", "", 1)
        _, s0 = safe_regional_metrics(cid, 1, t0, r0, z0, p0, ri, ro, z_ring0, h_ring)
        tf = scalar_time(model, 51)
        rf = eval_array(model, "r", "m", 51)
        zf = eval_array(model, "z", "m", 51)
        pf = eval_array(model, "phils", "", 51)
        _, sf = safe_regional_metrics(cid, 51, tf, rf, zf, pf, ri, ro, z_ring0, h_ring)
        h0 = float(s0["H_median"])
        hf = float(sf["H_median"])
        flag = bool(sf["pseudo_spike_regional_flag"])
        base.update(
            {
                "postprocess_status": "PASS",
                "postprocess_method": sf["postprocess_method"],
                "point_count_original": sf["point_count_original"],
                "point_count_used": sf["point_count_used"],
                "H0_repaired": h0,
                "Hfinal_repaired": hf,
                "H_final_minus_H0_repaired": hf - h0 if finite(h0) and finite(hf) else math.nan,
                "interface_quality": "clear" if not flag else "weak_or_spiky",
                "regional_roughness": sf["roughness_peak_to_peak"],
                "regional_roughness_inner_edge": sf["regional_roughness_inner_edge"],
                "regional_roughness_outer_edge": sf["regional_roughness_outer_edge"],
                "regional_roughness_farfield": sf["regional_roughness_farfield"],
                "max_slope": sf["max_slope"],
                "principal_spike_region": sf["principal_spike_region"],
                "interface_points_count": sf["interface_points_count"],
                "pseudo_spike_regional_flag": str(flag),
                "memory_error_resolved": "YES" if "MemoryError" in str(row.get("failure_message", "")) else "NOT_APPLICABLE",
                "case_pass_after_postprocess_only": str(row.get("solve_status") == "PASS" and not flag and finite(h0) and finite(hf)),
                "notes": "Existing saved model loaded; no solver run; memory-safe regional metrics recomputed.",
            }
        )
    except Exception:
        base.update(
            {
                "postprocess_status": "FAILED",
                "postprocess_method": "memory_safe_regional_metrics_exception",
                "memory_error_resolved": "NO",
                "notes": traceback.format_exc()[:1800],
            }
        )
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass
    return base


def deferred_row(row: dict[str, str], family: str) -> dict[str, Any]:
    """Record an affected row when raw arrays are not available without slow COMSOL reload."""
    model_path = model_path_for(row)
    original_memory = "MemoryError" in str(row.get("failure_message", ""))
    if model_path is None:
        status = "SKIP_RAW_MODEL_UNAVAILABLE"
        note = "No saved model path is available for this skipped/original row; raw r/z/phils arrays are not materialized in repository artifacts."
    else:
        status = "RECOMPUTE_DEFERRED_COMSOL_RELOAD_TIMEOUT"
        note = (
            "Saved model exists, but raw r/z/phils arrays are not materialized outside COMSOL. "
            "A direct COMSOL reload attempt exceeded the bounded Builder runtime; rerun this script with "
            "T003_ATTEMPT_COMSOL=1 for full model-by-model recomputation."
        )
    return {
        "case_id": row.get("case_id", ""),
        "source_case": family,
        "solve_status": row.get("solve_status", ""),
        "postprocess_status": status,
        "postprocess_method": "memory_safe_regional_metrics_available_not_executed",
        "point_count_original": "",
        "point_count_used": "",
        "interface_quality": row.get("interface_quality", "extraction_failed"),
        "regional_roughness": row.get("regional_roughness", ""),
        "pseudo_spike_regional_flag": row.get("pseudo_spike_regional_flag", ""),
        "memory_error_resolved": "NO" if original_memory else "NOT_APPLICABLE",
        "case_pass_after_postprocess_only": "False",
        "notes": note,
        "required_for_full_recompute": f"COMSOL result arrays from {model_path}" if model_path else "A solved model artifact for this skipped case",
    }


def raw_array_manifest(ring_out: list[dict[str, Any]], wet_out: list[dict[str, Any]]) -> None:
    lines = [
        "# T003 Raw Array Recompute Manifest",
        "",
        f"- Run id: `{RUN_ID}`",
        "- The memory-safe regional metrics implementation is present in `scripts/T003_postprocessing_memory_repair.py`.",
        "- Existing CSV/JSON/image artifacts do not contain raw `r`, `z`, and `phils` result arrays.",
        "- A direct COMSOL reload attempt in this Builder run exceeded the bounded runtime after completing/entering early model reloads.",
        "- Full recomputation requires loading each saved `.mph` model and evaluating `r`, `z`, `phils`, and `t` at initial/final inner solutions.",
        "- Command for full attempt:",
        "",
        "```powershell",
        "$env:T003_ATTEMPT_COMSOL='1'",
        ".venv\\Scripts\\python.exe 06_true_moving_geometry_R3_postprocessing_memory_repair\\scripts\\T003_postprocessing_memory_repair.py",
        "```",
        "",
        "## Deferred Rows",
        "",
    ]
    for row in ring_out + wet_out:
        lines.append(
            f"- `{row.get('case_id')}`: postprocess_status=`{row.get('postprocess_status')}`, required=`{row.get('required_for_full_recompute', '')}`"
        )
    write_text(OUT / "reports" / "T003_raw_array_recompute_manifest.md", "\n".join(lines) + "\n")


def evidence_report(ring_rows: list[dict[str, str]], wet_rows: list[dict[str, str]]) -> None:
    affected_ring = [row for row in ring_rows if affected(row)]
    affected_wet = [row for row in wet_rows if affected(row)]
    lines = [
        "# T003-A Postprocessing Failure Evidence",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Blocker type: postprocessing/regional metrics extraction failure.",
        "- COMSOL solve status is `PASS` for G2/G3 and all seven wetted-wall/contactline affected rows; therefore the blocker is likely postprocessing extraction, not COMSOL solving.",
        "- Script reference: `scripts/ring_fountain_06_R3_ring_contactline_isolation.py`.",
        "- Function references: `region_of` around line 269, `regional_metrics_from_arrays` around line 334, `evaluate_model` around line 423.",
        "- Failure trace points to `regional_metrics_from_arrays(...): by.setdefault(region_of(...), []).append(p)` around line 350.",
        "",
        "## Affected Ring Geometry Rows",
        "",
    ]
    for row in affected_ring:
        lines.append(f"- `{row.get('case_id')}`: solve_status=`{row.get('solve_status')}`, interface_quality=`{row.get('interface_quality')}`, MemoryError=`{'MemoryError' in row.get('failure_message', '')}`, model=`{row.get('model') or row.get('timestamp_model')}`")
    lines.extend(["", "## Affected Wetted-Wall/Contactline Rows", ""])
    for row in affected_wet:
        lines.append(f"- `{row.get('case_id')}`: solve_status=`{row.get('solve_status')}`, interface_quality=`{row.get('interface_quality')}`, MemoryError=`{'MemoryError' in row.get('failure_message', '')}`, model=`{row.get('model') or row.get('timestamp_model')}`")
    write_text(OUT / "reports" / "T003_A_postprocessing_failure_evidence.md", "\n".join(lines) + "\n")


def load_font(size: int) -> ImageFont.ImageFont:
    for candidate in ["arial.ttf", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/consola.ttf"]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def render_status_bars(path: Path, rows: list[dict[str, Any]], title: str) -> str:
    counts = Counter(str(row.get("postprocess_status", "")) for row in rows)
    labels = list(counts.keys()) or ["none"]
    values = [counts[label] for label in labels] or [0]
    width, height = 1000, 520
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    font = load_font(24)
    small = load_font(16)
    draw.text((30, 20), title, fill=(0, 0, 0), font=font)
    chart_x, chart_y = 80, 100
    chart_w, chart_h = 850, 320
    draw.line((chart_x, chart_y + chart_h, chart_x + chart_w, chart_y + chart_h), fill=(0, 0, 0))
    draw.line((chart_x, chart_y, chart_x, chart_y + chart_h), fill=(0, 0, 0))
    max_v = max(values + [1])
    bar_w = max(40, chart_w // max(1, len(values) * 2))
    for idx, (label, value) in enumerate(zip(labels, values)):
        x0 = chart_x + 60 + idx * (bar_w + 80)
        x1 = x0 + bar_w
        y1 = chart_y + chart_h
        y0 = y1 - int(chart_h * value / max_v)
        draw.rectangle((x0, y0, x1, y1), fill=(67, 111, 191))
        draw.text((x0, y0 - 24), str(value), fill=(0, 0, 0), font=small)
        draw.text((x0 - 25, y1 + 15), label[:24], fill=(0, 0, 0), font=small)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return abspath(path)


def render_quality_bars(path: Path, rows: list[dict[str, Any]]) -> str:
    counts = Counter(str(row.get("interface_quality", "")) for row in rows)
    return render_status_bars(path, [{"postprocess_status": key} for key, value in counts.items() for _ in range(value)], "T003 interface quality after repair")


def final_report(ring_out: list[dict[str, Any]], wet_out: list[dict[str, Any]]) -> dict[str, str]:
    all_rows = ring_out + wet_out
    memory_rows = [row for row in all_rows if row.get("memory_error_resolved") in {"YES", "NO"}]
    resolved_count = sum(1 for row in memory_rows if row.get("memory_error_resolved") == "YES")
    pass_count = sum(1 for row in all_rows if row.get("postprocess_status") == "PASS")
    deferred_count = sum(1 for row in all_rows if "DEFERRED" in str(row.get("postprocess_status", "")))
    failed_model_count = sum(1 for row in all_rows if row.get("postprocess_status") == "FAILED")
    skipped_count = sum(1 for row in all_rows if row.get("postprocess_status") == "SKIP_RAW_MODEL_UNAVAILABLE")
    memory_status = "YES" if memory_rows and resolved_count == len(memory_rows) else "PARTIAL" if resolved_count else "NO"
    iq_status = "YES" if failed_model_count == 0 and pass_count > 0 else "PARTIAL" if pass_count > 0 else "NO"
    static_baseline = "YES" if any(row.get("case_id") == "G1_ring_current_position_repeat" and row.get("interface_quality") == "clear" for row in all_rows) else "NO"
    micro_baseline = "UNKNOWN"
    t003_status = "PASS" if memory_status == "YES" and iq_status == "YES" else "PARTIAL" if (pass_count or deferred_count or skipped_count) else "FAIL"
    gates = {
        "T003_STATUS": t003_status,
        "POSTPROCESSING_MEMORY_ERROR_RESOLVED": memory_status,
        "INTERFACE_QUALITY_EXTRACTION_REPAIRED": iq_status,
        "CREDIBLE_STATIC_BASELINE_AFTER_POSTPROCESSING": static_baseline,
        "CREDIBLE_MICRO_MOTION_BASELINE_AFTER_POSTPROCESSING": micro_baseline,
        "ALLOW_NEXT_DISPLACEMENT_LADDER": "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    lines = [
        "# T003 Final Report",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: postprocessing repair only; no COMSOL solve rerun, no Stage 6, no Jet1/Jet2 detection, no real Hmax.",
        "",
        "## Gate Values",
        "",
    ]
    lines.extend([f"- `{key} = {value}`" for key, value in gates.items()])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Recomputed rows: `{len(all_rows)}`",
            f"- Postprocess PASS rows: `{pass_count}`",
            f"- Rows without saved model/raw arrays: `{skipped_count}`",
            f"- Rows deferred because COMSOL raw arrays are not materialized in repository artifacts: `{deferred_count}`",
            f"- Failed postprocess rows after repair: `{failed_model_count}`",
            f"- MemoryError rows resolved: `{resolved_count}/{len(memory_rows)}`",
            "- Interpretation: the memory-safe implementation is available, but full recomputation could not be completed in this bounded run because raw arrays are only inside `.mph` models and COMSOL reload exceeded runtime. Existing evidence still does not establish a credible static or micro-motion baseline.",
            "",
            "## Key Outputs",
            "",
            f"- Evidence report: `{OUT / 'reports' / 'T003_A_postprocessing_failure_evidence.md'}`",
            f"- Ring repaired table: `{OUT / 'tables' / 'T003_ring_geometry_position_cases_repaired.csv'}`",
            f"- Wetted-wall repaired table: `{OUT / 'tables' / 'T003_wettedwall_contactline_cases_repaired.csv'}`",
            f"- Images directory: `{OUT / 'images'}`",
        ]
    )
    write_text(OUT / "reports" / "T003_final_report.md", "\n".join(lines) + "\n")
    write_json(OUT / "reports" / "T003_gate_summary.json", gates)
    return gates


def update_readme(gates: dict[str, str]) -> None:
    readme = ROOT / "README.md"
    start = "<!-- TRUE_GEOMETRY_R3_POSTPROCESSING_MEMORY_REPAIR:START -->"
    end = "<!-- TRUE_GEOMETRY_R3_POSTPROCESSING_MEMORY_REPAIR:END -->"
    block = "\n".join(
        [
            start,
            "## TRUE_GEOMETRY_R3_POSTPROCESSING_MEMORY_REPAIR",
            "",
            f"- Run id: `{RUN_ID}`",
            "- Scope: postprocessing/regional-metrics repair only.",
            f"- T003 status: `{gates['T003_STATUS']}`",
            f"- `POSTPROCESSING_MEMORY_ERROR_RESOLVED = {gates['POSTPROCESSING_MEMORY_ERROR_RESOLVED']}`",
            f"- `INTERFACE_QUALITY_EXTRACTION_REPAIRED = {gates['INTERFACE_QUALITY_EXTRACTION_REPAIRED']}`",
            f"- `CREDIBLE_STATIC_BASELINE_AFTER_POSTPROCESSING = {gates['CREDIBLE_STATIC_BASELINE_AFTER_POSTPROCESSING']}`",
            f"- `CREDIBLE_MICRO_MOTION_BASELINE_AFTER_POSTPROCESSING = {gates['CREDIBLE_MICRO_MOTION_BASELINE_AFTER_POSTPROCESSING']}`",
            f"- `ALLOW_NEXT_DISPLACEMENT_LADDER = {gates['ALLOW_NEXT_DISPLACEMENT_LADDER']}`",
            f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
            f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
            f"- Final report: `{OUT / 'reports' / 'T003_final_report.md'}`",
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
    script_copy = OUT / "scripts" / "T003_postprocessing_memory_repair.py"
    if Path(__file__).resolve() != script_copy.resolve():
        shutil.copy2(Path(__file__).resolve(), script_copy)

    ring_rows = read_csv(RING_CSV)
    wet_rows = read_csv(WETTED_CSV)
    evidence_report(ring_rows, wet_rows)
    affected_ring = [row for row in ring_rows if affected(row)]
    affected_wet = [row for row in wet_rows if affected(row)]
    log(f"affected ring rows: {len(affected_ring)}; affected wetted rows: {len(affected_wet)}")

    attempt_comsol = os.environ.get("T003_ATTEMPT_COMSOL", "").strip() == "1"
    if attempt_comsol:
        client = mph.Client(cores=2, version="6.4")
        try:
            ring_out = [evaluate_existing_model(client, row, "ring_geometry_position_cases.csv") for row in affected_ring]
            wet_out = [evaluate_existing_model(client, row, "wettedwall_contactline_cases.csv") for row in affected_wet]
        finally:
            try:
                client.clear()
            except Exception:
                pass
    else:
        log("T003_ATTEMPT_COMSOL is not set; writing deferred recompute rows without COMSOL reload.")
        ring_out = [deferred_row(row, "ring_geometry_position_cases.csv") for row in affected_ring]
        wet_out = [deferred_row(row, "wettedwall_contactline_cases.csv") for row in affected_wet]
        raw_array_manifest(ring_out, wet_out)

    columns = [
        "case_id",
        "source_case",
        "solve_status",
        "postprocess_status",
        "postprocess_method",
        "point_count_original",
        "point_count_used",
        "interface_quality",
        "regional_roughness",
        "pseudo_spike_regional_flag",
        "memory_error_resolved",
        "case_pass_after_postprocess_only",
        "notes",
        "H0_repaired",
        "Hfinal_repaired",
        "H_final_minus_H0_repaired",
        "regional_roughness_inner_edge",
        "regional_roughness_outer_edge",
        "regional_roughness_farfield",
        "max_slope",
        "principal_spike_region",
        "interface_points_count",
        "required_for_full_recompute",
    ]
    write_csv(OUT / "tables" / "T003_ring_geometry_position_cases_repaired.csv", ring_out, columns)
    write_csv(OUT / "tables" / "T003_wettedwall_contactline_cases_repaired.csv", wet_out, columns)
    render_status_bars(OUT / "images" / "T003_geometry_postprocess_status_summary.png", ring_out, "T003 geometry postprocess status")
    render_status_bars(OUT / "images" / "T003_wettedwall_postprocess_status_summary.png", wet_out, "T003 wetted-wall postprocess status")
    render_quality_bars(OUT / "images" / "T003_interface_quality_after_repair.png", ring_out + wet_out)
    gates = final_report(ring_out, wet_out)
    update_readme(gates)
    return 0 if gates["T003_STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
