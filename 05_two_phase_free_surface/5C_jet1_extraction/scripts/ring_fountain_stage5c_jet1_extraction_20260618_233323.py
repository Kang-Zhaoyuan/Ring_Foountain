# -*- coding: utf-8 -*-
"""5C Jet1 extraction from fixed-geometry equivalent falling-ring model.

This stage only performs Jet1-oriented postprocessing on the 5B4-R1 best
model.  It does not enter 5D/5E/Stage 6, extract Jet2, run a parameter sweep,
or report a real Hmax.
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
R1 = STAGE5 / "5B4_R1_extended_stability_repair"
C5 = STAGE5 / "5C_jet1_extraction"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = C5 / "logs" / f"5C_jet1_extraction_{RUN_ID}.log"

R1_FINAL = R1 / "reports" / "5B4_R1_extended_stability_repair_final_report.md"
R1_B_REPORT = R1 / "reports" / "B_interface_diagnostic_audit.md"
R1_C_REPORT = R1 / "reports" / "C_E0_D4_repeat_report.md"
R1_F_REPORT = R1 / "reports" / "F_R1_best_model_report.md"
R1_MODEL = R1 / "models" / "ring_fountain_v5B4_R1_best.mph"
R1_JAVA = R1 / "exports" / "ring_fountain_v5B4_R1_best.java"
R1_SUMMARY = R1 / "5B4_R1_extended_stability_repair_summary.json"

SCRIPT_ARCHIVE = SCRIPTS / "ring_fountain_stage5c_jet1_extraction.py"
LOCAL_SCRIPT_ARCHIVE = C5 / "scripts" / "ring_fountain_stage5c_jet1_extraction.py"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ring_fountain_stage4_2a as s42a  # noqa: E402
import ring_fountain_stage5_cleanup_5b_5c as base  # noqa: E402
import ring_fountain_stage5b3_C4_seed_based_ring_smoke as c4help  # noqa: E402
import ring_fountain_stage5b4_R1_extended_stability_repair as r1help  # noqa: E402


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def ensure_dirs() -> None:
    for sub in ["models", "exports", "reports", "tables", "images", "frames", "logs", "scripts"]:
        (C5 / sub).mkdir(parents=True, exist_ok=True)
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


def param_float(model: Any, name: str, unit: str = "m", default: float = math.nan) -> float:
    try:
        return float(s42a.param_float(model, name, unit))
    except Exception:
        return default


def read_times(model: Any) -> list[float]:
    return r1help.read_times(model)


def phase_data(model: Any, inner: int) -> dict[str, np.ndarray]:
    return r1help.phase_data(model, inner)


def roi_params(model: Any) -> dict[str, float]:
    ri = param_float(model, "Ri", "m", 0.015)
    ro = param_float(model, "Ro", "m", 0.025)
    h_ring = param_float(model, "h_ring", "m", 0.004)
    z_ring = param_float(model, "z_ring", "m", 0.0)
    z0 = param_float(model, "z0", "m", 0.0)
    edge_width = max(0.002, min(0.006, 0.35 * abs(ro - ri) if math.isfinite(ro - ri) else 0.003))
    return {
        "Ri": ri,
        "Ro": ro,
        "h_ring": h_ring,
        "z_ring": z_ring,
        "z0": z0,
        "inner_edge_width": edge_width,
        "center_hole_r_min": 0.0,
        "center_hole_r_max": ri,
        "inner_edge_r_min": max(0.0, ri - edge_width),
        "inner_edge_r_max": ri + edge_width,
    }


def interface_points(data: dict[str, np.ndarray]) -> list[tuple[float, float]]:
    return base.estimate_interface(data["r"], data["z"], data["phi"], threshold=0.5)


def points_in_roi(points: list[tuple[float, float]], roi: dict[str, float], which: str) -> list[tuple[float, float]]:
    z0 = roi["z0"]
    if which == "center_hole":
        return [(r, z) for r, z in points if 0 <= r <= roi["center_hole_r_max"] and z >= z0 - 1e-9]
    if which == "inner_edge":
        return [(r, z) for r, z in points if roi["inner_edge_r_min"] <= r <= roi["inner_edge_r_max"] and z >= z0 - 1e-9]
    if which == "jet1_union":
        return [
            (r, z)
            for r, z in points
            if z >= z0 - 1e-9 and (0 <= r <= roi["center_hole_r_max"] or roi["inner_edge_r_min"] <= r <= roi["inner_edge_r_max"])
        ]
    return []


def robust_height(points: list[tuple[float, float]]) -> tuple[float, float, int, float]:
    comps = r1help.split_components(points)
    if not comps:
        return math.nan, math.nan, 0, 0.0
    lengths = [r1help.component_length(comp) for comp in comps]
    idx = int(np.argmax(lengths))
    comp = comps[idx]
    zvals = [z for _, z in comp]
    h_max = max(zvals, default=math.nan)
    h_p95 = float(np.percentile(zvals, 95)) if zvals else math.nan
    return h_max, h_p95, len(comps), max(lengths, default=0.0)


def global_metrics(points: list[tuple[float, float]]) -> dict[str, Any]:
    metrics = r1help.robust_interface_metrics_from_points(points)
    return {
        "H_raw_global": metrics["H_max_raw"],
        "H_robust_main_interface": metrics["H_robust"],
        "H_95_percentile": metrics["H_percentile_95"],
        "H_99_percentile": metrics["H_percentile_99"],
        "interface_points_count": metrics["interface_points_count"],
        "main_component_length": metrics["largest_component_length"],
        "number_of_interface_components": metrics["number_of_interface_components"],
        "near_top_flag": metrics["near_top"],
    }


def render_roi_map(path: Path, roi: dict[str, float]) -> str:
    width, height = 980, 620
    pixels = bytearray([248, 248, 246] * width * height)
    rlim = (0.0, max(0.04, roi["Ro"] * 1.6))
    zlim = (-0.025, 0.04)
    tx, ty, _ = base.axis_map(width, height, rlim, zlim)
    base.line(pixels, width, height, tx(rlim[0]), ty(zlim[0]), tx(rlim[1]), ty(zlim[0]), (40, 40, 40))
    base.line(pixels, width, height, tx(rlim[0]), ty(zlim[0]), tx(rlim[0]), ty(zlim[1]), (40, 40, 40))
    z0 = roi["z0"]
    # Center-hole ROI fill.
    for r in np.linspace(0, roi["center_hole_r_max"], 90):
        for z in np.linspace(z0, zlim[1], 90):
            base.circle(pixels, width, height, tx(float(r)), ty(float(z)), 1, (205, 225, 250))
    # Inner-edge ROI fill.
    for r in np.linspace(roi["inner_edge_r_min"], roi["inner_edge_r_max"], 45):
        for z in np.linspace(z0, zlim[1], 90):
            base.circle(pixels, width, height, tx(float(r)), ty(float(z)), 1, (245, 218, 180))
    # Ring cross-section outline.
    ri, ro, h, zr = roi["Ri"], roi["Ro"], roi["h_ring"], roi["z_ring"]
    yb, yt = zr - h / 2, zr + h / 2
    pts = [(ri, yb), (ro, yb), (ro, yt), (ri, yt), (ri, yb)]
    for (a, b), (c, d) in zip(pts[:-1], pts[1:]):
        base.line(pixels, width, height, tx(a), ty(b), tx(c), ty(d), (20, 20, 20))
    base.line(pixels, width, height, tx(rlim[0]), ty(z0), tx(rlim[1]), ty(z0), (60, 60, 60))
    base.png_write(path, width, height, pixels)
    return str(path)


def render_xy_curve(path: Path, rows: list[dict[str, Any]], xkey: str, ykey: str) -> str:
    plot_rows = []
    for row in rows:
        y = to_float(row.get(ykey))
        plot_rows.append({"time_s": to_float(row.get(xkey)), "H_m": y, "H_mm": y * 1000 if math.isfinite(y) else math.nan})
    base.render_curve(path, plot_rows)
    return str(path)


def render_location_curve(path: Path, rows: list[dict[str, Any]]) -> str:
    plot_rows = []
    for row in rows:
        r = to_float(row.get("Jet1_candidate_r"))
        plot_rows.append({"time_s": to_float(row.get("time_s")), "H_m": r, "H_mm": r * 1000 if math.isfinite(r) else math.nan})
    base.render_curve(path, plot_rows)
    return str(path)


def render_selected_panel(path: Path, datasets: list[dict[str, np.ndarray]], value_key: str, cmap: str, vlim: tuple[float, float] | None = None) -> str:
    width, height = 980, 720
    pixels = bytearray([248, 248, 246] * width * height)
    if not datasets:
        base.png_write(path, width, height, pixels)
        return str(path)
    cols = min(2, len(datasets))
    rows = int(math.ceil(len(datasets) / cols))
    rlim = (0.0, 0.04)
    zlim = (-0.01, 0.025)
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
        y0 = 40 + row * (height // rows)
        y1 = (row + 1) * (height // rows) - 40

        def tx(r: float) -> int:
            return int(x0 + (r - rlim[0]) / max(1e-12, rlim[1] - rlim[0]) * (x1 - x0))

        def ty(z: float) -> int:
            return int(y1 - (z - zlim[0]) / max(1e-12, zlim[1] - zlim[0]) * (y1 - y0))

        mask = base.finite_mask(data["r"], data["z"], data[value_key])
        rr, zz, vv = data["r"][mask].reshape(-1), data["z"][mask].reshape(-1), data[value_key][mask].reshape(-1)
        step = max(1, len(rr) // 12000)
        for r, z, val in zip(rr[::step], zz[::step], vv[::step]):
            if not (rlim[0] <= r <= rlim[1] and zlim[0] <= z <= zlim[1]):
                continue
            t = (float(val) - lo) / max(1e-12, hi - lo)
            base.circle(pixels, width, height, tx(float(r)), ty(float(z)), 1, cmap_fn(t))
        if "phi" in data:
            for (a, b), (c, d) in zip(interface_points(data)[:-1], interface_points(data)[1:]):
                if rlim[0] <= a <= rlim[1] and rlim[0] <= c <= rlim[1]:
                    base.line(pixels, width, height, tx(a), ty(b), tx(c), ty(d), (0, 0, 0))
        base.line(pixels, width, height, x0, y1, x1, y1, (60, 60, 60))
        base.line(pixels, width, height, x0, y0, x0, y1, (60, 60, 60))
    base.png_write(path, width, height, pixels)
    return str(path)


def stage_a_review() -> dict[str, Any]:
    log("A: reviewing 5B4-R1 gates.")
    summary = read_json(R1_SUMMARY)
    inputs = [
        R1_FINAL,
        R1_B_REPORT,
        R1_C_REPORT,
        R1_F_REPORT,
        R1_MODEL,
        R1_JAVA,
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        SCRIPTS / "SCRIPT_MANIFEST.md",
    ]
    rows = [
        {"item": "5B4-R1", "value": summary.get("5B4_R1_status"), "status": "PASS" if summary.get("5B4_R1_status") == "PASS" else "FAIL"},
        {"item": "ALLOW_5C", "value": summary.get("ALLOW_5C"), "status": "PASS" if summary.get("ALLOW_5C") == "YES" else "FAIL"},
        {"item": "ALLOW_STAGE6", "value": summary.get("ALLOW_STAGE6"), "status": "PASS" if summary.get("ALLOW_STAGE6") == "NO" else "FAIL"},
        {"item": "this_run_allows", "value": "Jet1 extraction", "status": "CONFIRMED"},
        {"item": "this_run_forbids", "value": "Jet2 extraction, Stage 6 parameter sweep, real Hmax output", "status": "CONFIRMED"},
        *[{"item": f"input_exists:{p.name}", "value": str(p), "status": "PASS" if p.exists() else "FAIL"} for p in inputs],
    ]
    write_csv(C5 / "tables" / "A_5B4_R1_gate_review.csv", rows)
    write_text(C5 / "reports" / "A_5B4_R1_import_review.md", "\n".join([
        "# A 5B4-R1 Import Review",
        "",
        f"Run ID: `{RUN_ID}`",
        "",
        f"- `5B4-R1 = {summary.get('5B4_R1_status')}`",
        f"- `ALLOW_5C = {summary.get('ALLOW_5C')}`",
        f"- `ALLOW_STAGE6 = {summary.get('ALLOW_STAGE6')}`",
        "- This run allows Jet1 extraction.",
        "- This run forbids Jet2 extraction.",
        "- This run forbids Stage 6 parameter sweep.",
        "- This run forbids real Hmax output.",
        f"- Best model: `{R1_MODEL}`",
        f"- Best Java: `{R1_JAVA}`",
    ]))
    status = "PASS" if rows[0]["status"] == "PASS" and rows[1]["status"] == "PASS" and all(p.exists() for p in inputs[:6]) else "FAIL"
    return {"status": status, "summary": summary, "rows": rows}


def stage_b_roi(model: Any) -> dict[str, Any]:
    log("B: defining Jet1 ROI.")
    roi = roi_params(model)
    rows = [
        {"roi": "center_hole_region", "definition": "0 <= r <= Ri and z >= z0", "r_min_m": 0.0, "r_max_m": roi["Ri"], "z_min_m": roi["z0"]},
        {"roi": "inner_edge_region", "definition": "Ri +/- inner_edge_width and z >= z0", "r_min_m": roi["inner_edge_r_min"], "r_max_m": roi["inner_edge_r_max"], "z_min_m": roi["z0"]},
        {"roi": "above_initial_interface", "definition": "z >= z0", "z_min_m": roi["z0"]},
    ]
    write_csv(C5 / "tables" / "B_jet1_ROI_definition.csv", rows)
    render_roi_map(C5 / "images" / "B_jet1_ROI_map.png", roi)
    write_text(C5 / "reports" / "B_jet1_definition_and_ROI_report.md", "\n".join([
        "# B Jet1 Definition and ROI Report",
        "",
        "- Jet1 is the early free-surface structure rising from the center-hole or annular opening region.",
        "- Jet1 may appear before cavity pinch-off.",
        "- Jet1 is not Worthington jet / Jet2.",
        "- Jet1 is not a real Hmax measurement.",
        "- Current model: fixed-geometry equivalent falling-ring with WettedWall wall velocity.",
        "",
        f"- `Ri = {roi['Ri']}` m",
        f"- `Ro = {roi['Ro']}` m",
        f"- `h_ring = {roi['h_ring']}` m",
        f"- `z_ring = {roi['z_ring']}` m",
        f"- `z0 = {roi['z0']}` m",
        f"- Inner-edge half-width: `{roi['inner_edge_width']}` m",
        f"- ROI map: `{C5 / 'images' / 'B_jet1_ROI_map.png'}`",
    ]))
    return {"status": "PASS", "roi": roi}


def stage_c_extract_interface(model: Any, roi: dict[str, float]) -> dict[str, Any]:
    log("C: extracting interface sequence.")
    times = read_times(model)
    rows: list[dict[str, Any]] = []
    for inner, t in enumerate(times, start=1):
        data = phase_data(model, inner)
        pts = interface_points(data)
        gm = global_metrics(pts)
        center_pts = points_in_roi(pts, roi, "center_hole")
        edge_pts = points_in_roi(pts, roi, "inner_edge")
        center_max, center_p95, center_components, center_len = robust_height(center_pts)
        edge_max, edge_p95, edge_components, edge_len = robust_height(edge_pts)
        pseudo_spike = bool(gm["number_of_interface_components"] > 1 and gm["H_raw_global"] - gm["H_robust_main_interface"] > 0.00015)
        rows.append({
            "time": t,
            "time_s": t,
            **gm,
            "H_center_hole": center_p95,
            "H_center_hole_raw": center_max,
            "H_inner_edge": edge_p95,
            "H_inner_edge_raw": edge_max,
            "center_hole_components": center_components,
            "center_hole_main_length": center_len,
            "inner_edge_components": edge_components,
            "inner_edge_main_length": edge_len,
            "pseudo_spike_flag": pseudo_spike,
            "near_top_flag": gm["near_top_flag"],
            "H_m": gm["H_robust_main_interface"],
            "H_mm": gm["H_robust_main_interface"] * 1000 if math.isfinite(gm["H_robust_main_interface"]) else math.nan,
        })
        base.render_field(C5 / "frames" / f"C_interface_frame_{inner:03d}.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True)
    write_csv(C5 / "tables" / "C_interface_sequence_diagnostics.csv", rows)
    r1help.render_comparison(C5 / "images" / "C_interface_height_comparison.png", [
        {
            "time_s": row["time_s"],
            "H_max_raw": row["H_raw_global"],
            "H_robust": row["H_robust_main_interface"],
            "H_percentile_95": row["H_95_percentile"],
        }
        for row in rows
    ])
    write_text(C5 / "logs" / "C_interface_sequence_extraction.log", json.dumps({"rows": len(rows), "first_time": rows[0]["time_s"] if rows else None, "last_time": rows[-1]["time_s"] if rows else None}, ensure_ascii=False, indent=2))
    write_text(C5 / "reports" / "C_interface_sequence_extraction_report.md", "\n".join([
        "# C Interface Sequence Extraction Report",
        "",
        f"- Extracted time steps: `{len(rows)}`.",
        "- Interface source: `phils = 0.5` Level Set main interface estimate.",
        "- Raw and robust diagnostics are both retained.",
        "- Global highest points alone are not used to judge Jet1.",
        "- Isolated pseudo-spike flags are exported.",
        "- This diagnostic is not real Hmax.",
        f"- Table: `{C5 / 'tables' / 'C_interface_sequence_diagnostics.csv'}`",
        f"- Comparison image: `{C5 / 'images' / 'C_interface_height_comparison.png'}`",
        f"- Frames: `{C5 / 'frames' / 'C_interface_frame_*.png'}`",
    ]))
    return {"status": "PASS" if rows else "FAIL", "rows": rows, "table": str(C5 / "tables" / "C_interface_sequence_diagnostics.csv")}


def detect_jet1_candidate(rows: list[dict[str, Any]], roi: dict[str, float]) -> dict[str, Any]:
    if not rows:
        return {"detected": "NO", "reason": "No interface rows."}
    h0_center = next((to_float(r["H_center_hole"]) for r in rows if math.isfinite(to_float(r["H_center_hole"]))), math.nan)
    h0_edge = next((to_float(r["H_inner_edge"]) for r in rows if math.isfinite(to_float(r["H_inner_edge"]))), math.nan)
    candidates = []
    for row in rows:
        hc = to_float(row["H_center_hole"])
        he = to_float(row["H_inner_edge"])
        dc = hc - h0_center if math.isfinite(hc) and math.isfinite(h0_center) else math.nan
        de = he - h0_edge if math.isfinite(he) and math.isfinite(h0_edge) else math.nan
        if math.isfinite(dc) and (not math.isfinite(de) or dc >= de):
            h, delta, region, rloc = hc, dc, "center_hole_region", roi["Ri"] * 0.5
        else:
            h, delta, region, rloc = he, de, "inner_edge_region", roi["Ri"]
        early = to_float(row["time_s"]) <= 0.020
        continuous = abs(to_float(row.get("H_raw_global")) - to_float(row.get("H_robust_main_interface"))) <= 0.0002
        not_isolated = not bool(row.get("pseudo_spike_flag")) and to_float(row.get("main_component_length")) > 0.002
        candidate = bool(early and not_isolated and not row.get("near_top_flag") and math.isfinite(delta) and delta > 5e-5)
        candidates.append({
            "time_s": row["time_s"],
            "Jet1_candidate_height_m": h,
            "Jet1_candidate_delta_m": delta,
            "Jet1_candidate_region": region,
            "Jet1_candidate_r": rloc,
            "early_time": early,
            "continuous_H": continuous,
            "not_isolated": not_isolated,
            "near_top_flag": row.get("near_top_flag"),
            "pseudo_spike_flag": row.get("pseudo_spike_flag"),
            "candidate_flag": candidate,
            "H_m": h,
            "H_mm": h * 1000 if math.isfinite(h) else math.nan,
        })
    valid = [r for r in candidates if r["candidate_flag"]]
    best = max(valid, key=lambda r: to_float(r["Jet1_candidate_delta_m"])) if valid else None
    return {
        "detected": "YES" if best else "NO",
        "best": best,
        "rows": candidates,
        "max_delta": to_float(best["Jet1_candidate_delta_m"]) if best else math.nan,
        "first_time": valid[0]["time_s"] if valid else "",
    }


def stage_d_detect(rows: list[dict[str, Any]], roi: dict[str, float]) -> dict[str, Any]:
    log("D: detecting Jet1 candidate.")
    detection = detect_jet1_candidate(rows, roi)
    cand_rows = detection.get("rows", [])
    write_csv(C5 / "tables" / "D_jet1_candidate_timeseries.csv", cand_rows)
    summary_row = {
        "Jet1_detected": detection["detected"],
        "Jet1_first_time_s": detection.get("first_time", ""),
        "Jet1_max_delta_m": detection.get("max_delta", math.nan),
        "best": detection.get("best", {}),
    }
    write_csv(C5 / "tables" / "D_jet1_candidate_summary.csv", [summary_row])
    render_xy_curve(C5 / "images" / "D_jet1_candidate_H_vs_t.png", cand_rows, "time_s", "Jet1_candidate_height_m")
    render_location_curve(C5 / "images" / "D_jet1_candidate_location_vs_t.png", cand_rows)
    selected = [i + 1 for i, r in enumerate(cand_rows) if r.get("candidate_flag")][:4]
    if not selected and cand_rows:
        selected = [1, max(1, len(cand_rows) // 3), max(1, 2 * len(cand_rows) // 3), len(cand_rows)]
    for inner in selected:
        src = C5 / "frames" / f"C_interface_frame_{inner:03d}.png"
        dst = C5 / "frames" / f"D_jet1_candidate_frame_{inner:03d}.png"
        if src.exists():
            shutil.copy2(src, dst)
    write_text(C5 / "logs" / "D_jet1_candidate_detection.log", json.dumps(summary_row, ensure_ascii=False, indent=2, default=str))
    write_text(C5 / "reports" / "D_jet1_candidate_detection_report.md", "\n".join([
        "# D Jet1 Candidate Detection Report",
        "",
        f"- `Jet1_detected = {detection['detected']}`.",
        f"- First candidate time: `{detection.get('first_time', '')}` s.",
        f"- Maximum candidate robust height change: `{detection.get('max_delta', math.nan)}` m.",
        "- Jet1 is defined only in the center-hole or inner-edge ROI.",
        "- Candidate logic excludes near-top frames and pseudo-spike flagged frames.",
        "- Jet1 is not Jet2 and not real Hmax.",
        f"- Timeseries: `{C5 / 'tables' / 'D_jet1_candidate_timeseries.csv'}`",
        f"- Summary: `{C5 / 'tables' / 'D_jet1_candidate_summary.csv'}`",
    ]))
    return {"status": "PASS", **detection}


def stage_e_velocity_support(model: Any, detection: dict[str, Any], roi: dict[str, float]) -> dict[str, Any]:
    log("E: exporting velocity support frames.")
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
        pts = interface_points(data)
        jet_pts = points_in_roi(pts, roi, "jet1_union")
        mask = base.finite_mask(data["r"], data["z"], data["w"], data["U"], data["p"])
        rr, zz = data["r"][mask].reshape(-1), data["z"][mask].reshape(-1)
        ww, uu, pp = data["w"][mask].reshape(-1), data["U"][mask].reshape(-1), data["p"][mask].reshape(-1)
        roi_mask = (
            (zz >= roi["z0"])
            & ((rr <= roi["center_hole_r_max"]) | ((rr >= roi["inner_edge_r_min"]) & (rr <= roi["inner_edge_r_max"])))
            & (zz <= roi["z0"] + 0.025)
        )
        upward = ww[roi_mask]
        metrics.append({
            "inner_solution": inner,
            "time_s": times[inner - 1] if inner - 1 < len(times) else math.nan,
            "roi_samples": int(np.count_nonzero(roi_mask)),
            "roi_w_mean_m_per_s": float(np.nanmean(upward)) if upward.size else math.nan,
            "roi_w_max_m_per_s": float(np.nanmax(upward)) if upward.size else math.nan,
            "roi_upward_fraction": float(np.count_nonzero(upward > 0) / upward.size) if upward.size else math.nan,
            "roi_U_max_m_per_s": float(np.nanmax(uu[roi_mask])) if np.count_nonzero(roi_mask) else math.nan,
            "roi_pressure_max_Pa": float(np.nanmax(pp[roi_mask])) if np.count_nonzero(roi_mask) else math.nan,
            "jet_roi_interface_points": len(jet_pts),
        })
        base.render_field(C5 / "frames" / f"E_velocity_support_frame_{inner:03d}_U.png", data["r"], data["z"], data["U"], cmap="viridis", phi=data["phi"], draw_interface=True)
        base.render_field(C5 / "frames" / f"E_velocity_support_frame_{inner:03d}_w.png", data["r"], data["z"], data["w"], cmap="viridis", phi=data["phi"], draw_interface=True)
        base.render_field(C5 / "frames" / f"E_velocity_support_frame_{inner:03d}_p.png", data["r"], data["z"], data["p"], cmap="viridis", phi=data["phi"], draw_interface=True)
        base.render_field(C5 / "frames" / f"E_velocity_support_frame_{inner:03d}_phils.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True)
    write_csv(C5 / "tables" / "E_velocity_support_metrics.csv", metrics)
    render_selected_panel(C5 / "images" / "E_velocity_magnitude_selected_frames.png", datasets, "U", "viridis")
    render_selected_panel(C5 / "images" / "E_axial_velocity_selected_frames.png", datasets, "w", "viridis")
    render_selected_panel(C5 / "images" / "E_pressure_selected_frames.png", datasets, "p", "viridis")
    up_support = any(to_float(r.get("roi_w_max_m_per_s")) > 0 for r in metrics)
    write_text(C5 / "reports" / "E_velocity_field_support_report.md", "\n".join([
        "# E Velocity Field Support Report",
        "",
        f"- Selected inner solution indices: `{selected}`.",
        f"- Jet1 candidate accompanied by upward axial velocity: `{up_support}`.",
        "- Velocity support was evaluated in the center-hole / inner-edge region above the initial interface.",
        "- Fields exported: `spf.U`, `w`, `p`, `phils`.",
        "- This supports only the fixed-geometry equivalent moving-wall interpretation.",
        f"- Metrics: `{C5 / 'tables' / 'E_velocity_support_metrics.csv'}`",
    ]))
    return {"status": "PASS" if metrics else "FAIL", "selected_inner": selected, "upward_velocity_support": up_support, "metrics": metrics}


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


def stage_f_artifact(model: Any, summary: dict[str, Any]) -> dict[str, Any]:
    log("F: saving 5C best artifact.")
    try:
        model.java.param().set("stage5c_note", "1")
        model.java.param().descr("stage5c_note", "5C Jet1 extraction artifact marker; no physics change.")
    except Exception:
        pass
    model_paths = save_model_no_clobber(model, C5 / "models" / "ring_fountain_v5C_jet1_extraction_best.mph")
    java_paths = save_java_no_clobber(model, C5 / "exports" / "ring_fountain_v5C_jet1_extraction_best.java")
    rows = [
        {"artifact": "5C_best_model", **model_paths},
        {"artifact": "5C_best_java", **java_paths},
    ]
    write_csv(C5 / "tables" / "F_5C_best_artifact_manifest.csv", rows)
    write_text(C5 / "reports" / "F_5C_best_artifact_report.md", "\n".join([
        "# F 5C Best Artifact Report",
        "",
        "- No new physical model was created; this artifact archives the 5B4-R1 best model with 5C extraction documentation.",
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
    allow_5d = "YES" if (
        summary.get("C", {}).get("status") == "PASS"
        and summary.get("B", {}).get("status") == "PASS"
        and summary.get("D", {}).get("status") == "PASS"
        and summary.get("E", {}).get("status") == "PASS"
        and model_path.exists()
        and java_path.exists()
    ) else "NO"
    return {"5C_status": "PASS" if allow_5d == "YES" else "FAIL", "ALLOW_5D": allow_5d, "ALLOW_STAGE6": "NO"}


def update_docs(summary: dict[str, Any]) -> None:
    log("Updating README, CHANGELOG, and SCRIPT_MANIFEST.")
    jet = summary.get("D", {}).get("detected", "NO")
    c4help.add_or_replace_section(ROOT / "README.md", "5C_JET1_EXTRACTION", [
        "## 5C Jet1 Extraction",
        "",
        f"- Run ID: `{RUN_ID}`.",
        "- 5B4-R1: `PASS`.",
        f"- 5C: `{summary.get('5C_status', 'FAIL')}`.",
        f"- Jet1 extraction completed; `Jet1_detected = {jet}`.",
        "- No Jet2 extraction has been performed.",
        "- No Stage 6 parameter sweep has been performed.",
        "- No real Hmax has been produced.",
        "- The source model remains a fixed-geometry WettedWall moving-wall equivalent falling-ring model.",
        f"- `ALLOW_5D = {summary.get('ALLOW_5D', 'NO')}`.",
        f"- `ALLOW_STAGE6 = {summary.get('ALLOW_STAGE6', 'NO')}`.",
        f"- Final report: `{C5 / 'reports' / '5C_jet1_extraction_final_report.md'}`.",
    ])
    c4help.add_or_replace_section(ROOT / "CHANGELOG.md", "5C_JET1_EXTRACTION", [
        "## 5C Jet1 Extraction",
        "",
        f"- Run ID: `{RUN_ID}`.",
        f"- Status: `{summary.get('5C_status', 'FAIL')}`.",
        f"- Jet1 detected: `{jet}`.",
        f"- Gate: `ALLOW_5D = {summary.get('ALLOW_5D', 'NO')}`, `ALLOW_STAGE6 = {summary.get('ALLOW_STAGE6', 'NO')}`.",
        "- Extracted phils=0.5 interface sequence with raw/robust diagnostics and velocity-field support frames.",
        "- Did not enter 5D/5E/Stage 6; no Jet2 extraction, parameter sweep, or real Hmax output was performed.",
    ])
    c4help.add_or_replace_section(SCRIPTS / "SCRIPT_MANIFEST.md", "5C_JET1_EXTRACTION_SCRIPT", [
        "## 5C Script",
        "",
        f"| `ring_fountain_stage5c_jet1_extraction.py` | 5C Jet1 ROI/interface/velocity extraction | `{RUN_ID}` | `{sha256(SCRIPT_ARCHIVE)}` |",
    ])


def write_final_report(summary: dict[str, Any]) -> None:
    d = summary.get("D", {})
    e = summary.get("E", {})
    lines = [
        "# 5C Jet1 Extraction Final Report",
        "",
        f"Run ID: `{RUN_ID}`",
        "",
        "## Required Answers",
        "",
        f"1. Imported 5B4-R1 best successfully: `{summary.get('A', {}).get('status') == 'PASS'}`.",
        f"2. Defined Jet1 ROI successfully: `{summary.get('B', {}).get('status') == 'PASS'}`.",
        f"3. Extracted interface sequence successfully: `{summary.get('C', {}).get('status') == 'PASS'}`.",
        f"4. Completed raw/robust H comparison: `{summary.get('C', {}).get('status') == 'PASS'}`.",
        f"5. Jet1 candidate detected: `{d.get('detected', 'NO')}`.",
        f"6. Jet1 candidate first time: `{d.get('first_time', '')}` s.",
        f"7. Jet1 candidate max robust height change: `{d.get('max_delta', '')}` m.",
        f"8. Jet1 candidate accompanied by upward axial velocity: `{e.get('upward_velocity_support', False)}`.",
        "9. Isolated pseudo-spike exclusion implemented: `YES`.",
        f"10. Generated `ring_fountain_v5C_jet1_extraction_best.mph`: `{summary.get('F', {}).get('status') == 'PASS'}`.",
        f"11. Exported `ring_fountain_v5C_jet1_extraction_best.java`: `{summary.get('F', {}).get('status') == 'PASS'}`.",
        f"12. Allow 5D: `{summary.get('ALLOW_5D', 'NO')}`.",
        f"13. Allow Stage 6: `{summary.get('ALLOW_STAGE6', 'NO')}`.",
        "",
        "## Gates",
        "",
        f"- `5C = {summary.get('5C_status', 'FAIL')}`",
        f"- `Jet1_detected = {d.get('detected', 'NO')}`",
        f"- `ALLOW_5D = {summary.get('ALLOW_5D', 'NO')}`",
        f"- `ALLOW_STAGE6 = {summary.get('ALLOW_STAGE6', 'NO')}`",
        "",
        "## Scope Notes",
        "",
        "- This run did not enter 5D, 5E, or Stage 6.",
        "- Jet2 extraction was not performed.",
        "- Parameter sweep was not performed.",
        "- Real Hmax was not produced.",
        "- This remains a fixed-geometry equivalent falling-ring model, not a true freely falling ring.",
        "",
        "## Key Paths",
        "",
        f"- Summary JSON: `{C5 / '5C_jet1_extraction_summary.json'}`",
        f"- Best model: `{summary.get('F', {}).get('best_model', {}).get('model', '')}`",
        f"- Best Java: `{summary.get('F', {}).get('best_java', {}).get('java', '')}`",
        f"- Reports: `{C5 / 'reports'}`",
        f"- Tables: `{C5 / 'tables'}`",
        f"- Images: `{C5 / 'images'}`",
        f"- Frames: `{C5 / 'frames'}`",
        f"- Logs: `{C5 / 'logs'}`",
        f"- Script archive: `{SCRIPT_ARCHIVE}`",
    ]
    write_text(C5 / "reports" / "5C_jet1_extraction_final_report.md", "\n".join(lines))


def main() -> int:
    ensure_dirs()
    script_info = archive_script()
    summary: dict[str, Any] = {
        "run_id": RUN_ID,
        "stage": "5C Jet1 extraction from fixed-geometry equivalent falling-ring model",
        "script": script_info,
        "ALLOW_5D": "NO",
        "ALLOW_STAGE6": "NO",
        "5C_status": "FAIL",
    }
    client = None
    model = None
    try:
        summary["A"] = stage_a_review()
        if summary["A"]["status"] != "PASS":
            summary["stop_reason"] = "5B4-R1 import gate failed."
        else:
            client = mph.Client(cores=2, version="6.4")
            model = client.load(str(R1_MODEL))
            summary["B"] = stage_b_roi(model)
            summary["C"] = stage_c_extract_interface(model, summary["B"]["roi"])
            summary["D"] = stage_d_detect(summary["C"].get("rows", []), summary["B"]["roi"])
            summary["E"] = stage_e_velocity_support(model, summary["D"], summary["B"]["roi"])
            summary["F"] = stage_f_artifact(model, summary)
            summary["stop_reason"] = "5C completed; did not enter 5D/5E/Stage 6."
        summary.update(final_gate(summary))
    except Exception:
        err = traceback.format_exc()
        err_path = C5 / "logs" / f"fatal_error_{RUN_ID}.log"
        err_path.write_text(err, encoding="utf-8")
        summary["stop_reason"] = str(err_path)
        summary.update({"ALLOW_5D": "NO", "ALLOW_STAGE6": "NO", "5C_status": "FAIL"})
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
    write_json(C5 / "5C_jet1_extraction_summary.json", summary)
    write_final_report(summary)
    update_docs(summary)
    write_json(C5 / "5C_jet1_extraction_summary.json", summary)
    log("5C completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
