# -*- coding: utf-8 -*-
"""5D Jet2 / later-stage Worthington-like detection.

This stage only detects possible later-stage axis-near free-surface jet
candidates from the fixed-geometry WettedWall equivalent falling-ring model.
It does not enter 5E or Stage 6, does not run a parameter sweep, and does not
report a real Hmax.
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

import numpy as np
import mph


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
STAGE5 = ROOT / "05_two_phase_free_surface"
C5 = STAGE5 / "5C_jet1_extraction"
D5 = STAGE5 / "5D_jet2_detection"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = D5 / "logs" / f"5D_jet2_detection_{RUN_ID}.log"

C5_FINAL = C5 / "reports" / "5C_jet1_extraction_final_report.md"
C5_D_REPORT = C5 / "reports" / "D_jet1_candidate_detection_report.md"
C5_E_REPORT = C5 / "reports" / "E_velocity_field_support_report.md"
C5_INTERFACE_TABLE = C5 / "tables" / "C_interface_sequence_diagnostics.csv"
C5_JET1_SUMMARY = C5 / "tables" / "D_jet1_candidate_summary.csv"
C5_VELOCITY_TABLE = C5 / "tables" / "E_velocity_support_metrics.csv"
C5_MODEL = C5 / "models" / "ring_fountain_v5C_jet1_extraction_best.mph"
C5_JAVA = C5 / "exports" / "ring_fountain_v5C_jet1_extraction_best.java"
C5_SUMMARY = C5 / "5C_jet1_extraction_summary.json"

SCRIPT_ARCHIVE = SCRIPTS / "ring_fountain_stage5d_jet2_detection.py"
LOCAL_SCRIPT_ARCHIVE = D5 / "scripts" / "ring_fountain_stage5d_jet2_detection.py"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ring_fountain_stage4_2a as s42a  # noqa: E402
import ring_fountain_stage5_cleanup_5b_5c as base  # noqa: E402
import ring_fountain_stage5b3_C4_seed_based_ring_smoke as c4help  # noqa: E402
import ring_fountain_stage5b4_R1_extended_stability_repair as r1help  # noqa: E402
import ring_fountain_stage5c_jet1_extraction as c5help  # noqa: E402


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def ensure_dirs() -> None:
    for sub in ["models", "exports", "reports", "tables", "images", "frames", "logs", "scripts"]:
        (D5 / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path)) if path.exists() else {}


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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            out: dict[str, Any] = {}
            for key in keys:
                value = row.get(key, "")
                if isinstance(value, (list, tuple, dict)):
                    value = json.dumps(value, ensure_ascii=False, default=str)
                out[key] = value
            writer.writerow(out)
    return str(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def archive_script() -> dict[str, str]:
    src = Path(__file__).resolve()
    shutil.copy2(src, SCRIPT_ARCHIVE)
    shutil.copy2(src, LOCAL_SCRIPT_ARCHIVE)
    root_ts = SCRIPT_ARCHIVE.with_name(f"{SCRIPT_ARCHIVE.stem}_{RUN_ID}{SCRIPT_ARCHIVE.suffix}")
    local_ts = LOCAL_SCRIPT_ARCHIVE.with_name(f"{LOCAL_SCRIPT_ARCHIVE.stem}_{RUN_ID}{LOCAL_SCRIPT_ARCHIVE.suffix}")
    shutil.copy2(src, root_ts)
    shutil.copy2(src, local_ts)
    return {
        "root_script": str(SCRIPT_ARCHIVE),
        "root_script_timestamp": str(root_ts),
        "local_script": str(LOCAL_SCRIPT_ARCHIVE),
        "local_script_timestamp": str(local_ts),
        "sha256": sha256(SCRIPT_ARCHIVE),
    }


def to_float(value: Any, default: float = math.nan) -> float:
    try:
        text = str(value).replace("[s]", "").replace("[m/s]", "").replace("[m]", "")
        return float(text)
    except Exception:
        return default


def read_times(model: Any) -> list[float]:
    return r1help.read_times(model)


def phase_data(model: Any, inner: int) -> dict[str, np.ndarray]:
    return r1help.phase_data(model, inner)


def param_float(model: Any, name: str, unit: str = "m", default: float = math.nan) -> float:
    try:
        return float(s42a.param_float(model, name, unit))
    except Exception:
        return default


def jet2_roi(model: Any) -> dict[str, float]:
    ri = param_float(model, "Ri", "m", 0.006)
    ro = param_float(model, "Ro", "m", 0.012)
    z0 = param_float(model, "z0", "m", 0.0)
    return {
        "Ri": ri,
        "Ro": ro,
        "z0": z0,
        "axis_r_min": 0.0,
        "axis_r_max": 0.25 * ri,
        "center_r_min": 0.0,
        "center_r_max": ri,
        "t_Jet1_window_end": 0.005,
    }


def interface_points(data: dict[str, np.ndarray]) -> list[tuple[float, float]]:
    return base.estimate_interface(data["r"], data["z"], data["phi"], threshold=0.5)


def points_roi(points: list[tuple[float, float]], roi: dict[str, float], region: str) -> list[tuple[float, float]]:
    z0 = roi["z0"]
    if region == "axis":
        return [(r, z) for r, z in points if roi["axis_r_min"] <= r <= roi["axis_r_max"] and z >= z0 - 1e-9]
    if region == "center":
        return [(r, z) for r, z in points if roi["center_r_min"] <= r <= roi["center_r_max"] and z >= z0 - 1e-9]
    return []


def robust_height(points: list[tuple[float, float]]) -> tuple[float, float, int, float, float]:
    comps = r1help.split_components(points)
    if not comps:
        return math.nan, math.nan, 0, 0.0, math.nan
    lengths = [r1help.component_length(comp) for comp in comps]
    idx = int(np.argmax(lengths))
    comp = comps[idx]
    zvals = [z for _, z in comp]
    h_max = max(zvals, default=math.nan)
    h_p95 = float(np.percentile(zvals, 95)) if zvals else math.nan
    h_min = min(zvals, default=math.nan)
    return h_max, h_p95, len(comps), max(lengths, default=0.0), h_min


def global_metrics(points: list[tuple[float, float]]) -> dict[str, Any]:
    metrics = r1help.robust_interface_metrics_from_points(points)
    return {
        "H_raw_global": metrics["H_max_raw"],
        "H_robust_main_interface": metrics["H_robust"],
        "number_of_interface_components": metrics["number_of_interface_components"],
        "main_component_length": metrics["largest_component_length"],
        "near_top_flag": metrics["near_top"],
    }


def render_roi_map(path: Path, roi: dict[str, float]) -> str:
    width, height = 980, 620
    pixels = bytearray([248, 248, 246] * width * height)
    rlim = (0.0, max(0.03, roi["Ro"] * 1.8))
    zlim = (-0.025, 0.04)
    tx, ty, _ = base.axis_map(width, height, rlim, zlim)
    base.line(pixels, width, height, tx(rlim[0]), ty(zlim[0]), tx(rlim[1]), ty(zlim[0]), (40, 40, 40))
    base.line(pixels, width, height, tx(rlim[0]), ty(zlim[0]), tx(rlim[0]), ty(zlim[1]), (40, 40, 40))
    z0 = roi["z0"]
    for r in np.linspace(roi["axis_r_min"], roi["axis_r_max"], 35):
        for z in np.linspace(z0, zlim[1], 100):
            base.circle(pixels, width, height, tx(float(r)), ty(float(z)), 1, (210, 225, 255))
    for r in np.linspace(roi["center_r_min"], roi["center_r_max"], 85):
        for z in np.linspace(z0, zlim[1], 100):
            base.circle(pixels, width, height, tx(float(r)), ty(float(z)), 1, (245, 225, 180))
    base.line(pixels, width, height, tx(0.0), ty(z0), tx(rlim[1]), ty(z0), (50, 50, 50))
    base.line(pixels, width, height, tx(roi["axis_r_max"]), ty(zlim[0]), tx(roi["axis_r_max"]), ty(zlim[1]), (10, 80, 180))
    base.line(pixels, width, height, tx(roi["center_r_max"]), ty(zlim[0]), tx(roi["center_r_max"]), ty(zlim[1]), (160, 100, 20))
    base.png_write(path, width, height, pixels)
    return str(path)


def render_height_plot(path: Path, rows: list[dict[str, Any]], key: str = "Jet2_candidate_height_m") -> str:
    plot_rows = []
    for row in rows:
        h = to_float(row.get(key))
        plot_rows.append({"time_s": to_float(row.get("time_s")), "H_m": h, "H_mm": h * 1000 if math.isfinite(h) else math.nan})
    base.render_curve(path, plot_rows)
    return str(path)


def render_selected_panel(path: Path, datasets: list[dict[str, np.ndarray]], value_key: str, cmap: str, vlim: tuple[float, float] | None = None) -> str:
    width, height = 980, 720
    pixels = bytearray([248, 248, 246] * width * height)
    if not datasets:
        base.png_write(path, width, height, pixels)
        return str(path)
    cols = min(2, len(datasets))
    panel_rows = int(math.ceil(len(datasets) / cols))
    rlim = (0.0, 0.025)
    zlim = (-0.012, 0.03)
    cmap_fn = base.cmap_blue_red if cmap == "phase" else base.cmap_viridis_like
    if vlim is None:
        vals = np.concatenate([d[value_key][np.isfinite(d[value_key])] for d in datasets if value_key in d and np.any(np.isfinite(d[value_key]))])
        lo, hi = (float(np.nanpercentile(vals, 2)), float(np.nanpercentile(vals, 98))) if vals.size else (0.0, 1.0)
    else:
        lo, hi = vlim
    for idx, data in enumerate(datasets):
        col, row = idx % cols, idx // cols
        x0 = 40 + col * (width // cols)
        x1 = (col + 1) * (width // cols) - 40
        y0 = 40 + row * (height // panel_rows)
        y1 = (row + 1) * (height // panel_rows) - 40

        def tx(r: float) -> int:
            return int(x0 + (r - rlim[0]) / max(1e-12, rlim[1] - rlim[0]) * (x1 - x0))

        def ty(z: float) -> int:
            return int(y1 - (z - zlim[0]) / max(1e-12, zlim[1] - zlim[0]) * (y1 - y0))

        mask = base.finite_mask(data["r"], data["z"], data[value_key])
        rr, zz, vv = data["r"][mask].reshape(-1), data["z"][mask].reshape(-1), data[value_key][mask].reshape(-1)
        step = max(1, len(rr) // 12000)
        for r, z, val in zip(rr[::step], zz[::step], vv[::step]):
            if rlim[0] <= r <= rlim[1] and zlim[0] <= z <= zlim[1]:
                t = (float(val) - lo) / max(1e-12, hi - lo)
                base.circle(pixels, width, height, tx(float(r)), ty(float(z)), 1, cmap_fn(t))
        pts = interface_points(data)
        for (a, b), (c, d) in zip(pts[:-1], pts[1:]):
            if rlim[0] <= a <= rlim[1] and rlim[0] <= c <= rlim[1]:
                base.line(pixels, width, height, tx(a), ty(b), tx(c), ty(d), (0, 0, 0))
        base.line(pixels, width, height, x0, y1, x1, y1, (60, 60, 60))
        base.line(pixels, width, height, x0, y0, x0, y1, (60, 60, 60))
    base.png_write(path, width, height, pixels)
    return str(path)


def stage_a_review() -> dict[str, Any]:
    log("A: reviewing 5C gates.")
    summary = read_json(C5_SUMMARY)
    inputs = [
        C5_FINAL,
        C5_D_REPORT,
        C5_E_REPORT,
        C5_INTERFACE_TABLE,
        C5_JET1_SUMMARY,
        C5_VELOCITY_TABLE,
        C5_MODEL,
        C5_JAVA,
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        SCRIPTS / "SCRIPT_MANIFEST.md",
    ]
    rows = [
        {"item": "5C", "value": summary.get("5C_status"), "status": "PASS" if summary.get("5C_status") == "PASS" else "FAIL"},
        {"item": "Jet1_detected", "value": summary.get("D", {}).get("detected"), "status": "PASS" if summary.get("D", {}).get("detected") == "NO" else "INFO"},
        {"item": "ALLOW_5D", "value": summary.get("ALLOW_5D"), "status": "PASS" if summary.get("ALLOW_5D") == "YES" else "FAIL"},
        {"item": "ALLOW_STAGE6", "value": summary.get("ALLOW_STAGE6"), "status": "PASS" if summary.get("ALLOW_STAGE6") == "NO" else "FAIL"},
        {"item": "this_run_allows", "value": "Jet2 detection", "status": "CONFIRMED"},
        {"item": "this_run_forbids", "value": "Stage 6 parameter sweep, real Hmax output", "status": "CONFIRMED"},
        *[{"item": f"input_exists:{p.name}", "value": str(p), "status": "PASS" if p.exists() else "FAIL"} for p in inputs],
    ]
    write_csv(D5 / "tables" / "A_5C_gate_review.csv", rows)
    write_text(D5 / "reports" / "A_5C_import_review.md", "\n".join([
        "# A 5C Import Review",
        "",
        f"Run ID: `{RUN_ID}`",
        "",
        f"- `5C = {summary.get('5C_status')}`",
        f"- `Jet1_detected = {summary.get('D', {}).get('detected')}`",
        f"- `ALLOW_5D = {summary.get('ALLOW_5D')}`",
        f"- `ALLOW_STAGE6 = {summary.get('ALLOW_STAGE6')}`",
        "- This run allows Jet2 detection.",
        "- This run forbids Stage 6 parameter sweep.",
        "- This run forbids real Hmax output.",
        f"- Best model: `{C5_MODEL}`",
        f"- Best Java: `{C5_JAVA}`",
    ]))
    status = "PASS" if summary.get("5C_status") == "PASS" and summary.get("ALLOW_5D") == "YES" and all(p.exists() for p in inputs[:8]) else "FAIL"
    return {"status": status, "summary": summary, "rows": rows}


def stage_b_roi(model: Any) -> dict[str, Any]:
    log("B: defining Jet2 ROI.")
    roi = jet2_roi(model)
    rows = [
        {"roi": "axis_near_region", "definition": "0 <= r <= 0.25*Ri and z >= z0", "r_min_m": roi["axis_r_min"], "r_max_m": roi["axis_r_max"], "z_min_m": roi["z0"]},
        {"roi": "center_region", "definition": "0 <= r <= Ri and z >= z0", "r_min_m": roi["center_r_min"], "r_max_m": roi["center_r_max"], "z_min_m": roi["z0"]},
        {"roi": "late_time_window", "definition": "t >= t_Jet1_window_end", "t_min_s": roi["t_Jet1_window_end"]},
    ]
    write_csv(D5 / "tables" / "B_jet2_ROI_definition.csv", rows)
    render_roi_map(D5 / "images" / "B_jet2_ROI_map.png", roi)
    write_text(D5 / "reports" / "B_jet2_definition_and_ROI_report.md", "\n".join([
        "# B Jet2 Definition and ROI Report",
        "",
        "- Jet2 is a later-stage axis-focused / Worthington-like candidate.",
        "- Jet2 is not Jet1.",
        "- Jet2 is not the early center-hole through-flow jet.",
        "- Jet2 is not a real final fountain Hmax.",
        "- Current model: fixed-geometry equivalent falling-ring with WettedWall wall velocity.",
        "",
        f"- `Ri = {roi['Ri']}` m.",
        f"- `axis_near_region: 0 <= r <= {roi['axis_r_max']}` m.",
        f"- `center_region: 0 <= r <= {roi['center_r_max']}` m.",
        f"- `z0 = {roi['z0']}` m.",
        f"- `t_Jet1_window_end = {roi['t_Jet1_window_end']}` s.",
        f"- ROI map: `{D5 / 'images' / 'B_jet2_ROI_map.png'}`",
    ]))
    return {"status": "PASS", "roi": roi}


def extract_jet2_rows(model: Any, roi: dict[str, float], prefix: str, render_frames: bool = True) -> list[dict[str, Any]]:
    times = read_times(model)
    rows: list[dict[str, Any]] = []
    for inner, t in enumerate(times, start=1):
        data = phase_data(model, inner)
        pts = interface_points(data)
        gm = global_metrics(pts)
        axis_pts = points_roi(pts, roi, "axis")
        center_pts = points_roi(pts, roi, "center")
        axis_raw, axis_h, axis_components, axis_len, axis_min = robust_height(axis_pts)
        center_raw, center_h, center_components, center_len, center_min = robust_height(center_pts)
        pseudo = bool(gm["number_of_interface_components"] > 1 and gm["H_raw_global"] - gm["H_robust_main_interface"] > 0.00015)
        rows.append({
            "time": t,
            "time_s": t,
            "H_axis_near": axis_h,
            "H_axis_near_raw": axis_raw,
            "H_axis_near_min": axis_min,
            "H_center_region": center_h,
            "H_center_region_raw": center_raw,
            "H_center_region_min": center_min,
            "H_robust_main_interface": gm["H_robust_main_interface"],
            "H_raw_global": gm["H_raw_global"],
            "axis_interface_points_count": len(axis_pts),
            "center_interface_points_count": len(center_pts),
            "number_of_interface_components": gm["number_of_interface_components"],
            "main_component_length": gm["main_component_length"],
            "axis_component_length": axis_len,
            "center_component_length": center_len,
            "pseudo_spike_flag": pseudo,
            "near_top_flag": gm["near_top_flag"],
            "late_time_flag": t >= roi["t_Jet1_window_end"],
            "cavity_or_rebound_proxy_m": center_h - center_min if math.isfinite(center_h) and math.isfinite(center_min) else math.nan,
            "H_m": center_h if math.isfinite(center_h) else gm["H_robust_main_interface"],
            "H_mm": (center_h if math.isfinite(center_h) else gm["H_robust_main_interface"]) * 1000 if math.isfinite(center_h if math.isfinite(center_h) else gm["H_robust_main_interface"]) else math.nan,
        })
        if render_frames:
            base.render_field(D5 / "frames" / f"{prefix}_frame_{inner:03d}.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True)
    return rows


def detect_jet2(rows: list[dict[str, Any]], roi: dict[str, float]) -> dict[str, Any]:
    late = [r for r in rows if r.get("late_time_flag")]
    if not late:
        return {"detected": "NO", "rows": [], "reason": "No late-time rows."}
    h0_axis = next((to_float(r["H_axis_near"]) for r in late if math.isfinite(to_float(r["H_axis_near"]))), math.nan)
    h0_center = next((to_float(r["H_center_region"]) for r in late if math.isfinite(to_float(r["H_center_region"]))), math.nan)
    out: list[dict[str, Any]] = []
    for r in rows:
        ha = to_float(r["H_axis_near"])
        hc = to_float(r["H_center_region"])
        da = ha - h0_axis if math.isfinite(ha) and math.isfinite(h0_axis) else math.nan
        dc = hc - h0_center if math.isfinite(hc) and math.isfinite(h0_center) else math.nan
        use_axis = math.isfinite(da) and (not math.isfinite(dc) or da >= dc)
        h = ha if use_axis else hc
        delta = da if use_axis else dc
        region = "axis_near_region" if use_axis else "center_region"
        continuous = abs(to_float(r["H_raw_global"]) - to_float(r["H_robust_main_interface"])) <= 0.00025
        not_isolated = not bool(r.get("pseudo_spike_flag")) and to_float(r.get("main_component_length")) > 0.002
        axial_focus = use_axis or to_float(r.get("axis_interface_points_count"), 0) > 0
        upward_trend = math.isfinite(delta) and delta > 5e-5
        candidate = bool(r.get("late_time_flag") and upward_trend and continuous and not_isolated and not r.get("near_top_flag") and axial_focus)
        out.append({
            "time_s": r["time_s"],
            "Jet2_candidate_height_m": h,
            "Jet2_candidate_delta_m": delta,
            "Jet2_candidate_region": region,
            "axis_interface_points_count": r["axis_interface_points_count"],
            "center_interface_points_count": r["center_interface_points_count"],
            "continuous_H": continuous,
            "not_isolated": not_isolated,
            "near_top_flag": r["near_top_flag"],
            "pseudo_spike_flag": r["pseudo_spike_flag"],
            "axial_focus_flag": axial_focus,
            "cavity_or_rebound_proxy_m": r["cavity_or_rebound_proxy_m"],
            "candidate_flag": candidate,
            "H_m": h,
            "H_mm": h * 1000 if math.isfinite(h) else math.nan,
        })
    valid = [r for r in out if r["candidate_flag"]]
    best = max(valid, key=lambda r: to_float(r["Jet2_candidate_delta_m"])) if valid else None
    return {
        "detected": "YES" if best else "NO",
        "rows": out,
        "best": best,
        "first_time": valid[0]["time_s"] if valid else "",
        "max_delta": to_float(best["Jet2_candidate_delta_m"]) if best else math.nan,
    }


def stage_c_existing(model: Any, roi: dict[str, float]) -> dict[str, Any]:
    log("C: screening existing 0.020 s window.")
    rows = extract_jet2_rows(model, roi, "C_existing_window_jet2", render_frames=True)
    detection = detect_jet2(rows, roi)
    write_csv(D5 / "tables" / "C_existing_window_jet2_timeseries.csv", rows)
    render_height_plot(D5 / "images" / "C_existing_window_jet2_H_vs_t.png", [
        {"time_s": r["time_s"], "Jet2_candidate_height_m": r["H_center_region"] if math.isfinite(to_float(r["H_center_region"])) else r["H_robust_main_interface"]}
        for r in rows
    ])
    write_text(D5 / "logs" / "C_existing_window_jet2_screening.log", json.dumps({"rows": len(rows), "Jet2_detected_existing_window": detection["detected"]}, ensure_ascii=False, indent=2, default=str))
    write_text(D5 / "reports" / "C_existing_window_jet2_screening_report.md", "\n".join([
        "# C Existing Window Jet2 Screening Report",
        "",
        f"- Time window: existing solution up to `{rows[-1]['time_s'] if rows else ''}` s.",
        f"- `Jet2_detected_existing_window = {detection['detected']}`.",
        "- Candidate criteria: late-time, axis/center ROI, continuous H(t), not isolated, not near top, axial upward trend.",
        "- This is not real Hmax.",
        f"- Timeseries: `{D5 / 'tables' / 'C_existing_window_jet2_timeseries.csv'}`",
        f"- H-vs-t image: `{D5 / 'images' / 'C_existing_window_jet2_H_vs_t.png'}`",
    ]))
    return {"status": "PASS" if rows else "FAIL", "rows": rows, "detection": detection}


def set_case_params(model: Any, t_end: str, dt: str) -> None:
    model.java.param().set("Vtarget", "1e-2[m/s]")
    model.java.param().set("t_end", t_end)
    model.java.param().set("dt", dt)
    try:
        model.java.param().set("t_ramp", "1e-3[s]")
    except Exception:
        pass
    model.java.study("std1").feature("time").set("tlist", "range(0,dt,t_end)")


def save_model_no_clobber(model: Any, canonical: Path) -> dict[str, str]:
    canonical.parent.mkdir(parents=True, exist_ok=True)
    timestamp = canonical.with_name(f"{canonical.stem}_{RUN_ID}{canonical.suffix}")
    model.save(path=str(timestamp), format="Comsol")
    result = {"timestamp_model": str(timestamp)}
    if canonical.exists():
        result["model"] = str(timestamp)
        result["canonical_note"] = f"canonical existed and was not overwritten: {canonical}"
    else:
        model.save(path=str(canonical), format="Comsol")
        result["model"] = str(canonical)
    return result


def save_java_no_clobber(model: Any, canonical: Path) -> dict[str, str]:
    canonical.parent.mkdir(parents=True, exist_ok=True)
    timestamp = canonical.with_name(f"{canonical.stem}_{RUN_ID}{canonical.suffix}")
    model.save(path=str(timestamp), format="Java")
    result = {"timestamp_java": str(timestamp)}
    if canonical.exists():
        result["java"] = str(timestamp)
        result["canonical_note"] = f"canonical existed and was not overwritten: {canonical}"
    else:
        model.save(path=str(canonical), format="Java")
        result["java"] = str(canonical)
    return result


def solve_extended_case(client: Any, roi: dict[str, float], case_id: str, t_end: str, dt: str) -> dict[str, Any]:
    model = None
    row: dict[str, Any] = {"case_id": case_id, "t_end": t_end, "dt": dt}
    try:
        model = client.load(str(C5_MODEL))
        set_case_params(model, t_end, dt)
        model.solve()
        rows = extract_jet2_rows(model, roi, f"D_extended_window_jet2_{case_id}", render_frames=True)
        detection = detect_jet2(rows, roi)
        model_paths = save_model_no_clobber(model, D5 / "models" / f"ring_fountain_v5D_{case_id}.mph")
        h0 = next((to_float(r["H_robust_main_interface"]) for r in rows if math.isfinite(to_float(r["H_robust_main_interface"]))), math.nan)
        hf = to_float(rows[-1]["H_robust_main_interface"]) if rows else math.nan
        row.update({
            "solve_status": "PASS",
            "failure_message": "",
            "H_robust_final_minus_H0": hf - h0 if math.isfinite(hf) and math.isfinite(h0) else math.nan,
            "interface_quality": "clear" if rows and not any(r["near_top_flag"] for r in rows) else "uncertain",
            "pseudo_spike_detected": any(r["pseudo_spike_flag"] for r in rows),
            "near_top_flag": any(r["near_top_flag"] for r in rows),
            "Jet2_detected": detection["detected"],
            "rows": rows,
            "detection": detection,
            **model_paths,
        })
    except Exception:
        err = traceback.format_exc()
        err_path = D5 / "logs" / f"{case_id}_error_{RUN_ID}.log"
        err_path.write_text(err, encoding="utf-8")
        row.update({
            "solve_status": "FAIL",
            "failure_message": str(err_path),
            "H_robust_final_minus_H0": math.nan,
            "interface_quality": "failed",
            "pseudo_spike_detected": True,
            "near_top_flag": False,
            "Jet2_detected": "NO",
            "rows": [],
            "detection": {"detected": "NO", "rows": []},
        })
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass
    return row


def stage_d_extended(client: Any, roi: dict[str, float], execute: bool) -> dict[str, Any]:
    if not execute:
        write_text(D5 / "reports" / "D_extended_window_jet2_detection_report.md", "# D Extended Window Jet2 Detection Report\n\nSkipped because Jet2 was detected in the existing window.\n")
        write_csv(D5 / "tables" / "D_extended_window_cases.csv", [{"case_id": "SKIPPED", "solve_status": "SKIPPED"}])
        return {"status": "SKIPPED", "executed": False, "rows": []}
    log("D: running optional extended-window detection.")
    cases = [("D_ext_030", "0.030[s]", "1e-4[s]"), ("D_ext_025", "0.025[s]", "1e-4[s]")]
    rows: list[dict[str, Any]] = []
    selected_detection: dict[str, Any] | None = None
    for case_id, t_end, dt in cases:
        row = solve_extended_case(client, roi, case_id, t_end, dt)
        rows.append(row)
        if row.get("solve_status") == "PASS":
            selected_detection = row.get("detection", {})
            if row.get("Jet2_detected") == "YES":
                break
            # A successful longer window is enough; do not continue to shorter retry.
            break
    flat_rows = [{k: v for k, v in row.items() if k not in {"rows", "detection"}} for row in rows]
    write_csv(D5 / "tables" / "D_extended_window_cases.csv", flat_rows)
    plot_rows = []
    for row in rows:
        for r in row.get("rows", []):
            plot_rows.append({"time_s": r["time_s"], "Jet2_candidate_height_m": r["H_center_region"] if math.isfinite(to_float(r["H_center_region"])) else r["H_robust_main_interface"]})
    if plot_rows:
        render_height_plot(D5 / "images" / "D_extended_window_jet2_H_vs_t.png", plot_rows)
    write_text(D5 / "logs" / "D_extended_window_jet2_detection.log", json.dumps(flat_rows, ensure_ascii=False, indent=2, default=str))
    write_text(D5 / "reports" / "D_extended_window_jet2_detection_report.md", "\n".join([
        "# D Extended Window Jet2 Detection Report",
        "",
        "- Executed only because the existing 0.020 s window did not contain a clear Jet2 candidate.",
        "- This is an optional later-time-window search, not a parameter sweep.",
        "",
        *[
            f"- {r.get('case_id')}: solve `{r.get('solve_status')}`, Jet2 `{r.get('Jet2_detected')}`, robust delta `{r.get('H_robust_final_minus_H0')}` m, failure `{r.get('failure_message', '')}`."
            for r in rows
        ],
    ]))
    return {"status": "PASS" if any(r.get("solve_status") == "PASS" for r in rows) else "FAIL", "executed": True, "rows": rows, "detection": selected_detection or {"detected": "NO", "rows": []}}


def pick_detection(summary: dict[str, Any]) -> dict[str, Any]:
    cdet = summary.get("C", {}).get("detection", {})
    if cdet.get("detected") == "YES":
        return cdet
    ddet = summary.get("D", {}).get("detection", {})
    if ddet:
        return ddet
    return cdet or {"detected": "NO", "rows": []}


def stage_e_support(model: Any, roi: dict[str, float], detection: dict[str, Any]) -> dict[str, Any]:
    log("E: exporting Jet2 velocity and pressure support frames.")
    times = read_times(model)
    best_time = to_float((detection.get("best") or {}).get("time_s"), math.nan)
    if math.isfinite(best_time) and times:
        best_idx = min(range(len(times)), key=lambda i: abs(times[i] - best_time)) + 1
        selected = sorted(set([max(1, best_idx - 10), max(1, best_idx - 3), best_idx, min(len(times), best_idx + 3)]))
    else:
        selected = sorted(set([1, max(1, len(times) // 3), max(1, 2 * len(times) // 3), len(times)]))
    metrics: list[dict[str, Any]] = []
    datasets: list[dict[str, np.ndarray]] = []
    for inner in selected:
        data = phase_data(model, inner)
        datasets.append(data)
        mask = base.finite_mask(data["r"], data["z"], data["w"], data["U"], data["p"])
        rr, zz = data["r"][mask].reshape(-1), data["z"][mask].reshape(-1)
        ww, uu, pp = data["w"][mask].reshape(-1), data["U"][mask].reshape(-1), data["p"][mask].reshape(-1)
        roi_mask = (zz >= roi["z0"]) & (rr <= roi["center_r_max"]) & (zz <= roi["z0"] + 0.03)
        axis_mask = (zz >= roi["z0"]) & (rr <= roi["axis_r_max"]) & (zz <= roi["z0"] + 0.03)
        roi_w = ww[roi_mask]
        axis_w = ww[axis_mask]
        pts = interface_points(data)
        axis_pts = points_roi(pts, roi, "axis")
        center_pts = points_roi(pts, roi, "center")
        metrics.append({
            "inner_solution": inner,
            "time_s": times[inner - 1] if inner - 1 < len(times) else math.nan,
            "center_samples": int(np.count_nonzero(roi_mask)),
            "axis_samples": int(np.count_nonzero(axis_mask)),
            "center_w_mean_m_per_s": float(np.nanmean(roi_w)) if roi_w.size else math.nan,
            "center_w_max_m_per_s": float(np.nanmax(roi_w)) if roi_w.size else math.nan,
            "axis_w_mean_m_per_s": float(np.nanmean(axis_w)) if axis_w.size else math.nan,
            "axis_w_max_m_per_s": float(np.nanmax(axis_w)) if axis_w.size else math.nan,
            "axis_upward_fraction": float(np.count_nonzero(axis_w > 0) / axis_w.size) if axis_w.size else math.nan,
            "center_U_max_m_per_s": float(np.nanmax(uu[roi_mask])) if np.count_nonzero(roi_mask) else math.nan,
            "center_pressure_max_Pa": float(np.nanmax(pp[roi_mask])) if np.count_nonzero(roi_mask) else math.nan,
            "axis_interface_points_count": len(axis_pts),
            "center_interface_points_count": len(center_pts),
        })
        for key, label in [("U", "U"), ("w", "w"), ("p", "p"), ("phi", "phils")]:
            cmap = "phase" if key == "phi" else "viridis"
            vlim = (0, 1) if key == "phi" else None
            base.render_field(D5 / "frames" / f"E_jet2_support_frame_{inner:03d}_{label}.png", data["r"], data["z"], data[key], vlim=vlim, cmap=cmap, phi=data["phi"], draw_interface=True)
    write_csv(D5 / "tables" / "E_jet2_support_metrics.csv", metrics)
    render_selected_panel(D5 / "images" / "E_jet2_velocity_magnitude_selected_frames.png", datasets, "U", "viridis")
    render_selected_panel(D5 / "images" / "E_jet2_axial_velocity_selected_frames.png", datasets, "w", "viridis")
    render_selected_panel(D5 / "images" / "E_jet2_pressure_selected_frames.png", datasets, "p", "viridis")
    upward = any(to_float(r.get("axis_w_max_m_per_s")) > 0 for r in metrics)
    focus = any(to_float(r.get("axis_interface_points_count"), 0) > 0 for r in metrics)
    rebound = any(to_float(r.get("center_w_mean_m_per_s")) > 0 for r in metrics)
    write_text(D5 / "reports" / "E_jet2_velocity_pressure_support_report.md", "\n".join([
        "# E Jet2 Velocity and Pressure Support Report",
        "",
        f"- Selected inner solution indices: `{selected}`.",
        f"- Jet2 candidate accompanied by upward axial velocity: `{upward}`.",
        f"- Axis-near interface evidence present: `{focus}`.",
        f"- Cavity contraction or interface rebound proxy present: `{rebound}`.",
        f"- Jet2 detected: `{detection.get('detected', 'NO')}`.",
        "- If Jet2 is not detected, reason: no continuous late-stage axis-near free-surface jet candidate.",
        f"- Metrics: `{D5 / 'tables' / 'E_jet2_support_metrics.csv'}`",
    ]))
    return {"status": "PASS" if metrics else "FAIL", "selected_inner": selected, "upward_velocity_support": upward, "axis_focus_support": focus, "rebound_proxy": rebound, "metrics": metrics}


def stage_f_artifact(model: Any) -> dict[str, Any]:
    log("F: saving 5D best artifact.")
    try:
        model.java.param().set("stage5d_note", "1")
        model.java.param().descr("stage5d_note", "5D Jet2 detection artifact marker; no physics change.")
    except Exception:
        pass
    model_paths = save_model_no_clobber(model, D5 / "models" / "ring_fountain_v5D_jet2_detection_best.mph")
    java_paths = save_java_no_clobber(model, D5 / "exports" / "ring_fountain_v5D_jet2_detection_best.java")
    write_csv(D5 / "tables" / "F_5D_best_artifact_manifest.csv", [
        {"artifact": "5D_best_model", **model_paths},
        {"artifact": "5D_best_java", **java_paths},
    ])
    write_text(D5 / "reports" / "F_5D_best_artifact_report.md", "\n".join([
        "# F 5D Best Artifact Report",
        "",
        "- This artifact archives the Jet2 detection postprocessing state.",
        "- The model remains fixed-geometry equivalent falling-ring.",
        f"- Model: `{model_paths.get('model')}`.",
        f"- Timestamp model: `{model_paths.get('timestamp_model')}`.",
        f"- Java: `{java_paths.get('java')}`.",
        f"- Timestamp Java: `{java_paths.get('timestamp_java')}`.",
    ]))
    return {"status": "PASS", "best_model": model_paths, "best_java": java_paths}


def final_gate(summary: dict[str, Any]) -> dict[str, str]:
    model_path = Path(str(summary.get("F", {}).get("best_model", {}).get("model", "")))
    java_path = Path(str(summary.get("F", {}).get("best_java", {}).get("java", "")))
    allow_5e = "YES" if (
        summary.get("B", {}).get("status") == "PASS"
        and summary.get("C", {}).get("status") == "PASS"
        and summary.get("E", {}).get("status") == "PASS"
        and model_path.exists()
        and java_path.exists()
    ) else "NO"
    return {"5D_status": "PASS" if allow_5e == "YES" else "FAIL", "ALLOW_5E": allow_5e, "ALLOW_STAGE6": "NO"}


def update_docs(summary: dict[str, Any]) -> None:
    log("Updating README, CHANGELOG, and SCRIPT_MANIFEST.")
    det = pick_detection(summary).get("detected", "NO")
    c4help.add_or_replace_section(ROOT / "README.md", "5D_JET2_DETECTION", [
        "## 5D Jet2 Detection",
        "",
        f"- Run ID: `{RUN_ID}`.",
        "- 5C: `PASS`.",
        f"- 5D: `{summary.get('5D_status', 'FAIL')}`.",
        f"- Jet2 detection completed; `Jet2_detected = {det}`.",
        "- No Stage 6 parameter sweep has been performed.",
        "- No real Hmax has been produced.",
        "- Jet2 candidate, if present, is not a true final fountain height.",
        "- The source model remains a fixed-geometry WettedWall moving-wall equivalent falling-ring model.",
        f"- `ALLOW_5E = {summary.get('ALLOW_5E', 'NO')}`.",
        f"- `ALLOW_STAGE6 = {summary.get('ALLOW_STAGE6', 'NO')}`.",
        f"- Final report: `{D5 / 'reports' / '5D_jet2_detection_final_report.md'}`.",
    ])
    c4help.add_or_replace_section(ROOT / "CHANGELOG.md", "5D_JET2_DETECTION", [
        "## 5D Jet2 Detection",
        "",
        f"- Run ID: `{RUN_ID}`.",
        f"- Status: `{summary.get('5D_status', 'FAIL')}`.",
        f"- Jet2 detected: `{det}`.",
        f"- Gate: `ALLOW_5E = {summary.get('ALLOW_5E', 'NO')}`, `ALLOW_STAGE6 = {summary.get('ALLOW_STAGE6', 'NO')}`.",
        "- Performed existing-window Jet2 screening and optional extended-window detection when needed.",
        "- Did not enter 5E or Stage 6; no parameter sweep or real Hmax output was performed.",
    ])
    c4help.add_or_replace_section(SCRIPTS / "SCRIPT_MANIFEST.md", "5D_JET2_DETECTION_SCRIPT", [
        "## 5D Script",
        "",
        f"| `ring_fountain_stage5d_jet2_detection.py` | 5D Jet2 / later-stage Worthington-like detection | `{RUN_ID}` | `{sha256(SCRIPT_ARCHIVE)}` |",
    ])


def write_final_report(summary: dict[str, Any]) -> None:
    det = pick_detection(summary)
    best = det.get("best") or {}
    e = summary.get("E", {})
    d_ext = summary.get("D", {})
    lines = [
        "# 5D Jet2 Detection Final Report",
        "",
        f"Run ID: `{RUN_ID}`",
        "",
        "## Required Answers",
        "",
        f"1. Imported 5C best successfully: `{summary.get('A', {}).get('status') == 'PASS'}`.",
        f"2. Defined Jet2 ROI successfully: `{summary.get('B', {}).get('status') == 'PASS'}`.",
        f"3. Completed existing 0.020 s Jet2 screening: `{summary.get('C', {}).get('status') == 'PASS'}`.",
        f"4. Extended-window detection executed: `{d_ext.get('executed', False)}`.",
        f"5. Extended-window solve successful: `{any(r.get('solve_status') == 'PASS' for r in d_ext.get('rows', []))}`.",
        f"6. Jet2 candidate detected: `{det.get('detected', 'NO')}`.",
        f"7. Jet2 candidate first time: `{det.get('first_time', '')}` s.",
        f"8. Jet2 candidate max robust height change: `{det.get('max_delta', '')}` m.",
        f"9. Jet2 candidate accompanied by upward axial velocity: `{e.get('upward_velocity_support', False)}`.",
        f"10. Cavity contraction or interface rebound indication: `{e.get('rebound_proxy', False)}`.",
        "11. Isolated pseudo-spike exclusion implemented: `YES`.",
        f"12. Generated `ring_fountain_v5D_jet2_detection_best.mph`: `{summary.get('F', {}).get('status') == 'PASS'}`.",
        f"13. Exported `ring_fountain_v5D_jet2_detection_best.java`: `{summary.get('F', {}).get('status') == 'PASS'}`.",
        f"14. Allow 5E: `{summary.get('ALLOW_5E', 'NO')}`.",
        f"15. Allow Stage 6: `{summary.get('ALLOW_STAGE6', 'NO')}`.",
        "",
        "## Gates",
        "",
        f"- `5D = {summary.get('5D_status', 'FAIL')}`",
        f"- `Jet2_detected = {det.get('detected', 'NO')}`",
        f"- `ALLOW_5E = {summary.get('ALLOW_5E', 'NO')}`",
        f"- `ALLOW_STAGE6 = {summary.get('ALLOW_STAGE6', 'NO')}`",
        "",
        "## Scope Notes",
        "",
        "- This run did not enter 5E or Stage 6.",
        "- No parameter sweep was performed.",
        "- No real Hmax was produced.",
        "- Any Jet2 candidate is not a true final fountain height.",
        "- This remains a fixed-geometry equivalent falling-ring model, not a true freely falling ring.",
        "",
        "## Key Paths",
        "",
        f"- Summary JSON: `{D5 / '5D_jet2_detection_summary.json'}`",
        f"- Best model: `{summary.get('F', {}).get('best_model', {}).get('model', '')}`",
        f"- Best Java: `{summary.get('F', {}).get('best_java', {}).get('java', '')}`",
        f"- Reports: `{D5 / 'reports'}`",
        f"- Tables: `{D5 / 'tables'}`",
        f"- Images: `{D5 / 'images'}`",
        f"- Frames: `{D5 / 'frames'}`",
        f"- Logs: `{D5 / 'logs'}`",
        f"- Script archive: `{SCRIPT_ARCHIVE}`",
        "",
        f"Stop reason: `{summary.get('stop_reason', '')}`",
    ]
    write_text(D5 / "reports" / "5D_jet2_detection_final_report.md", "\n".join(lines))


def main() -> int:
    ensure_dirs()
    script_info = archive_script()
    summary: dict[str, Any] = {
        "run_id": RUN_ID,
        "stage": "5D Jet2 / later-stage Worthington-like detection",
        "script": script_info,
        "ALLOW_5E": "NO",
        "ALLOW_STAGE6": "NO",
        "5D_status": "FAIL",
    }
    client = None
    model = None
    try:
        summary["A"] = stage_a_review()
        if summary["A"]["status"] != "PASS":
            summary["stop_reason"] = "5C import gate failed."
        else:
            client = mph.Client(cores=2, version="6.4")
            model = client.load(str(C5_MODEL))
            summary["B"] = stage_b_roi(model)
            summary["C"] = stage_c_existing(model, summary["B"]["roi"])
            existing_detected = summary["C"].get("detection", {}).get("detected") == "YES"
            summary["D"] = stage_d_extended(client, summary["B"]["roi"], execute=not existing_detected)
            summary["E"] = stage_e_support(model, summary["B"]["roi"], pick_detection(summary))
            summary["F"] = stage_f_artifact(model)
            summary["stop_reason"] = "5D completed; did not enter 5E or Stage 6."
        summary.update(final_gate(summary))
    except Exception:
        err = traceback.format_exc()
        err_path = D5 / "logs" / f"fatal_error_{RUN_ID}.log"
        err_path.write_text(err, encoding="utf-8")
        summary["stop_reason"] = str(err_path)
        summary.update({"ALLOW_5E": "NO", "ALLOW_STAGE6": "NO", "5D_status": "FAIL"})
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
    write_json(D5 / "5D_jet2_detection_summary.json", summary)
    write_final_report(summary)
    update_docs(summary)
    write_json(D5 / "5D_jet2_detection_summary.json", summary)
    log("5D completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
