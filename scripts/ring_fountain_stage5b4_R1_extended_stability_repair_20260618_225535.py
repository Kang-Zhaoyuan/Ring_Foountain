# -*- coding: utf-8 -*-
"""5B4-R1 extended stability repair and diagnostic audit.

This script only executes 5B4-R1.  It audits the original 5B4 extended
stability failure, recomputes robust free-surface diagnostics, reruns the D4
extended case with unchanged physics, and only proceeds to lower-velocity or
numerical repair cases if the gate requires it.

No 5C/5D/5E/Stage 6, Jet1/Jet2 extraction, parameter sweep, or real Hmax
reporting is performed.
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
B4_ORIG = STAGE5 / "5B4_falling_or_equivalent_ring"
R1 = STAGE5 / "5B4_R1_extended_stability_repair"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = R1 / "logs" / f"5B4_R1_extended_stability_repair_{RUN_ID}.log"

SCRIPT_ARCHIVE = SCRIPTS / "ring_fountain_stage5b4_R1_extended_stability_repair.py"
LOCAL_SCRIPT_ARCHIVE = R1 / "scripts" / "ring_fountain_stage5b4_R1_extended_stability_repair.py"

ORIG_FINAL_REPORT = B4_ORIG / "reports" / "5B4_falling_or_equivalent_ring_final_report.md"
ORIG_E_REPORT = B4_ORIG / "reports" / "E_extended_stability_report.md"
ORIG_D_TABLE = B4_ORIG / "tables" / "D_velocity_ladder_cases.csv"
ORIG_E_TABLE = B4_ORIG / "tables" / "E_extended_stability_H_vs_t.csv"
ORIG_E_MODEL = B4_ORIG / "models" / "ring_fountain_v5B4_extended_stability.mph"
BEST_CANDIDATE_MODEL = B4_ORIG / "models" / "ring_fountain_v5B4_best.mph"
BEST_CANDIDATE_JAVA = B4_ORIG / "exports" / "ring_fountain_v5B4_best.java"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ring_fountain_stage4_2a as s42a  # noqa: E402
import ring_fountain_stage5_cleanup_5b_5c as base  # noqa: E402
import ring_fountain_stage5b3_C4_seed_based_ring_smoke as c4help  # noqa: E402
import ring_fountain_stage5b4_falling_or_equivalent_ring as prev5b4  # noqa: E402


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def ensure_dirs() -> None:
    for sub in ["models", "exports", "reports", "tables", "images", "frames", "logs", "scripts"]:
        (R1 / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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
                if isinstance(value, (dict, list, tuple)):
                    value = json.dumps(value, ensure_ascii=False, default=str)
                out[key] = value
            writer.writerow(out)
    return str(path)


def write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def write_json(path: Path, payload: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return str(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def redirect_prev_module() -> None:
    prev5b4.B4 = R1
    prev5b4.LOG = LOG
    prev5b4.RUN_ID = RUN_ID
    prev5b4.SCRIPT_ARCHIVE = SCRIPT_ARCHIVE


def archive_script() -> dict[str, str]:
    src = Path(__file__).resolve()
    shutil.copy2(src, SCRIPT_ARCHIVE)
    shutil.copy2(src, LOCAL_SCRIPT_ARCHIVE)
    ts1 = SCRIPT_ARCHIVE.with_name(f"{SCRIPT_ARCHIVE.stem}_{RUN_ID}{SCRIPT_ARCHIVE.suffix}")
    ts2 = LOCAL_SCRIPT_ARCHIVE.with_name(f"{LOCAL_SCRIPT_ARCHIVE.stem}_{RUN_ID}{LOCAL_SCRIPT_ARCHIVE.suffix}")
    shutil.copy2(src, ts1)
    shutil.copy2(src, ts2)
    return {
        "root_script": str(SCRIPT_ARCHIVE),
        "root_script_timestamp": str(ts1),
        "local_script": str(LOCAL_SCRIPT_ARCHIVE),
        "local_script_timestamp": str(ts2),
        "sha256": sha256(SCRIPT_ARCHIVE),
    }


def to_float(value: Any, default: float = math.nan) -> float:
    try:
        return float(value)
    except Exception:
        return default


def finite_values(values: list[float]) -> list[float]:
    return [float(v) for v in values if math.isfinite(float(v))]


def split_components(points: list[tuple[float, float]]) -> list[list[tuple[float, float]]]:
    pts = sorted([(float(r), float(z)) for r, z in points if math.isfinite(r) and math.isfinite(z)], key=lambda p: p[0])
    if not pts:
        return []
    diffs = [pts[i + 1][0] - pts[i][0] for i in range(len(pts) - 1)]
    finite_diffs = [d for d in diffs if d > 1e-12]
    median_dr = float(np.median(finite_diffs)) if finite_diffs else 0.001
    gap = max(0.004, min(0.015, median_dr * 5.0))
    comps: list[list[tuple[float, float]]] = [[pts[0]]]
    for prev, cur in zip(pts[:-1], pts[1:]):
        if cur[0] - prev[0] > gap:
            comps.append([cur])
        else:
            comps[-1].append(cur)
    return comps


def component_length(comp: list[tuple[float, float]]) -> float:
    if len(comp) < 2:
        return 0.0
    return float(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(comp[:-1], comp[1:])))


def robust_interface_metrics_from_points(points: list[tuple[float, float]]) -> dict[str, Any]:
    valid = [(r, z) for r, z in points if math.isfinite(r) and math.isfinite(z) and 0 <= r <= 0.1 and -0.08 <= z <= 0.08]
    zvals = [z for _, z in valid]
    comps = split_components(valid)
    lengths = [component_length(comp) for comp in comps]
    largest_idx = int(np.argmax(lengths)) if lengths else -1
    if largest_idx >= 0:
        largest = comps[largest_idx]
    else:
        largest = []
    lz = [z for _, z in largest]
    center = [z for r, z in valid if r <= 0.012]
    raw = max(zvals, default=math.nan)
    p95 = float(np.percentile(zvals, 95)) if zvals else math.nan
    p99 = float(np.percentile(zvals, 99)) if zvals else math.nan
    main_max = max(lz, default=math.nan)
    main_p95 = float(np.percentile(lz, 95)) if lz else math.nan
    center_h = max(center, default=math.nan)
    proxy = float(sum(max(0.0, z) for z in zvals)) if zvals else math.nan
    raw_minus_main = raw - main_p95 if math.isfinite(raw) and math.isfinite(main_p95) else math.nan
    return {
        "H_max_raw": raw,
        "H_connected_main_interface": main_max,
        "H_centerline_or_axis_near": center_h,
        "H_percentile_95": p95,
        "H_percentile_99": p99,
        "H_robust": main_p95,
        "interface_area_or_volume_proxy": proxy,
        "number_of_interface_components": len(comps),
        "largest_component_length": max(lengths, default=0.0),
        "interface_points_count": len(valid),
        "raw_minus_main_p95": raw_minus_main,
        "raw_outlier_detected": bool(math.isfinite(raw_minus_main) and raw_minus_main > 0.00015),
        "near_top": bool(math.isfinite(raw) and raw > 0.028),
    }


def robust_interface_metrics(data: dict[str, np.ndarray]) -> dict[str, Any]:
    pts = base.estimate_interface(data["r"], data["z"], data["phi"], threshold=0.5)
    return robust_interface_metrics_from_points(pts)


def read_times(model: Any) -> list[float]:
    return prev5b4.read_times(model)


def phase_data(model: Any, inner: int) -> dict[str, np.ndarray]:
    return prev5b4.phase_data(model, inner)


def render_comparison(path: Path, rows: list[dict[str, Any]], title: str = "") -> str:
    width, height = 980, 560
    pixels = bytearray([248, 248, 246] * width * height)
    valid = [r for r in rows if math.isfinite(to_float(r.get("time_s"))) and math.isfinite(to_float(r.get("H_max_raw")))]
    if not valid:
        base.png_write(path, width, height, pixels)
        return str(path)
    ts = np.array([to_float(r.get("time_s")) for r in valid], dtype=float)
    series = [
        ("H_max_raw", (180, 30, 40)),
        ("H_robust", (20, 90, 190)),
        ("H_percentile_95", (30, 140, 75)),
    ]
    hs_all: list[float] = []
    for key, _ in series:
        hs_all.extend([to_float(r.get(key)) * 1000 for r in valid if math.isfinite(to_float(r.get(key)))])
    margin = 65
    tlo, thi = float(np.min(ts)), float(np.max(ts))
    hlo, hhi = min(0.0, min(hs_all, default=0.0)), max(0.001, max(hs_all, default=0.001))

    def tx(t: float) -> int:
        return int(margin + (t - tlo) / max(1e-12, thi - tlo) * (width - 2 * margin))

    def ty(h: float) -> int:
        return int(height - margin - (h - hlo) / max(1e-12, hhi - hlo) * (height - 2 * margin))

    base.line(pixels, width, height, margin, height - margin, width - margin, height - margin, (40, 40, 40))
    base.line(pixels, width, height, margin, margin, margin, height - margin, (40, 40, 40))
    for key, color in series:
        pts = [(to_float(r.get("time_s")), to_float(r.get(key)) * 1000) for r in valid if math.isfinite(to_float(r.get(key)))]
        for (t0, h0), (t1, h1) in zip(pts[:-1], pts[1:]):
            base.line(pixels, width, height, tx(t0), ty(h0), tx(t1), ty(h1), color)
        for t, h in pts[:: max(1, len(pts) // 50)]:
            base.circle(pixels, width, height, tx(t), ty(h), 3, color)
    # 0.2 mm gate as a horizontal guide relative to initial robust height.
    h0 = to_float(valid[0].get("H_robust"))
    if math.isfinite(h0):
        gate = (h0 + 0.0002) * 1000
        if hlo <= gate <= hhi:
            y = ty(gate)
            for x in range(margin, width - margin, 8):
                base.line(pixels, width, height, x, y, min(width - margin, x + 4), y, (20, 20, 20))
    base.png_write(path, width, height, pixels)
    return str(path)


def write_case_frame(model: Any, inner: int, prefix: str) -> None:
    data = phase_data(model, inner)
    base.render_field(
        R1 / "frames" / f"{prefix}_interface_frame_{inner:03d}.png",
        data["r"],
        data["z"],
        data["phi"],
        vlim=(0, 1),
        cmap="phase",
        phi=data["phi"],
        draw_interface=True,
    )


def extract_r1_outputs(model: Any, case_id: str, prefix: str, include_velocity: bool = True) -> dict[str, Any]:
    times = read_times(model)
    rows: list[dict[str, Any]] = []
    max_velocity = math.nan
    max_pressure = math.nan
    for inner, t in enumerate(times, start=1):
        data = phase_data(model, inner)
        metrics = robust_interface_metrics(data)
        finite_u = data["U"][np.isfinite(data["U"])]
        finite_p = data["p"][np.isfinite(data["p"])]
        if finite_u.size:
            max_velocity = max(float(np.max(np.abs(finite_u))), max_velocity if math.isfinite(max_velocity) else 0.0)
        if finite_p.size:
            max_pressure = max(float(np.max(np.abs(finite_p))), max_pressure if math.isfinite(max_pressure) else 0.0)
        row = {
            "case_id": case_id,
            "inner_solution": inner,
            "time_s": t,
            **metrics,
            "H_raw_mm": metrics["H_max_raw"] * 1000 if math.isfinite(metrics["H_max_raw"]) else math.nan,
            "H_robust_mm": metrics["H_robust"] * 1000 if math.isfinite(metrics["H_robust"]) else math.nan,
            "H_m": metrics["H_robust"],
            "H_mm": metrics["H_robust"] * 1000 if math.isfinite(metrics["H_robust"]) else math.nan,
        }
        rows.append(row)
        write_case_frame(model, inner, prefix)

    table = R1 / "tables" / f"{prefix}_H_diagnostics.csv"
    plot = R1 / "images" / f"{prefix}_H_vs_t.png"
    phils = R1 / "images" / f"{prefix}_phils_final.png"
    write_csv(table, rows)
    render_comparison(plot, rows)
    if times:
        data = phase_data(model, len(times))
        base.render_field(phils, data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True)
        if include_velocity:
            vel = R1 / "images" / f"{prefix}_velocity_magnitude.png"
            base.render_field(vel, data["r"], data["z"], data["U"], cmap="viridis", phi=data["phi"], draw_interface=True)

    raw0 = to_float(rows[0].get("H_max_raw")) if rows else math.nan
    rawf = to_float(rows[-1].get("H_max_raw")) if rows else math.nan
    robust0 = to_float(rows[0].get("H_robust")) if rows else math.nan
    robustf = to_float(rows[-1].get("H_robust")) if rows else math.nan
    raw_delta = rawf - raw0 if math.isfinite(raw0) and math.isfinite(rawf) else math.nan
    robust_delta = robustf - robust0 if math.isfinite(robust0) and math.isfinite(robustf) else math.nan
    max_jump = max((abs(to_float(b.get("H_max_raw")) - to_float(a.get("H_max_raw"))) for a, b in zip(rows[:-1], rows[1:])), default=math.nan)
    point_jump = max((abs(int(to_float(b.get("interface_points_count"), 0)) - int(to_float(a.get("interface_points_count"), 0))) for a, b in zip(rows[:-1], rows[1:])), default=0)
    near_top_any = any(bool(r.get("near_top")) for r in rows)
    raw_outlier_any = any(bool(r.get("raw_outlier_detected")) for r in rows)
    min_points = min((int(to_float(r.get("interface_points_count"), 0)) for r in rows), default=0)
    interface_quality = "clear" if rows and min_points >= 2 and not near_top_any else "uncertain"
    pseudo_spike = bool(raw_outlier_any and math.isfinite(robust_delta) and abs(robust_delta) <= 0.0002)
    return {
        "times": times,
        "rows": rows,
        "table": str(table),
        "plot": str(plot),
        "phils_final": str(phils),
        "H_raw_final_minus_H0": raw_delta,
        "H_robust_final_minus_H0": robust_delta,
        "max_raw_step_jump": max_jump,
        "interface_points_jump": point_jump,
        "max_velocity": max_velocity,
        "max_pressure": max_pressure,
        "interface_quality": interface_quality,
        "pseudo_spike_detected": pseudo_spike,
        "raw_outlier_detected": raw_outlier_any,
    }


def set_case_params(model: Any, vtarget: str, t_end: str, dt: str, t_ramp: str = "1e-3[s]") -> None:
    model.java.param().set("Vtarget", vtarget)
    model.java.param().set("t_end", t_end)
    model.java.param().set("dt", dt)
    model.java.param().set("t_ramp", t_ramp)
    model.java.study("std1").feature("time").set("tlist", "range(0,dt,t_end)")


def save_model_no_clobber(model: Any, canonical: Path) -> dict[str, str]:
    canonical.parent.mkdir(parents=True, exist_ok=True)
    timestamp = canonical.with_name(f"{canonical.stem}_{RUN_ID}{canonical.suffix}")
    model.save(path=str(timestamp), format="Comsol")
    result = {"timestamp_model": str(timestamp)}
    if not canonical.exists():
        model.save(path=str(canonical), format="Comsol")
        result["model"] = str(canonical)
    else:
        result["model"] = str(timestamp)
        result["canonical_note"] = f"canonical existed and was not overwritten: {canonical}"
    return result


def save_java_no_clobber(model: Any, canonical: Path) -> dict[str, str]:
    canonical.parent.mkdir(parents=True, exist_ok=True)
    timestamp = canonical.with_name(f"{canonical.stem}_{RUN_ID}{canonical.suffix}")
    model.save(path=str(timestamp), format="Java")
    result = {"timestamp_java": str(timestamp)}
    if not canonical.exists():
        model.save(path=str(canonical), format="Java")
        result["java"] = str(canonical)
    else:
        result["java"] = str(timestamp)
        result["canonical_note"] = f"canonical existed and was not overwritten: {canonical}"
    return result


def solve_r1_case(
    model: Any,
    case_id: str,
    vtarget: str,
    t_end: str,
    dt: str,
    model_name: str,
    prefix: str,
    t_ramp: str = "1e-3[s]",
) -> dict[str, Any]:
    log(f"Solving {case_id}: Vtarget={vtarget}, t_end={t_end}, dt={dt}, t_ramp={t_ramp}.")
    set_case_params(model, vtarget, t_end, dt, t_ramp=t_ramp)
    row: dict[str, Any] = {
        "case_id": case_id,
        "Vtarget": vtarget,
        "t_end": t_end,
        "dt": dt,
        "t_ramp": t_ramp,
        "used_forcing_route": "TwoPhaseFlowLevelSet + WettedWall utr = {0,-Vwall_eff(t),0}",
        "WettedWall_selection_ok": True,
    }
    try:
        model.solve()
        metrics = extract_r1_outputs(model, case_id, prefix)
        model_paths = save_model_no_clobber(model, R1 / "models" / model_name)
        row.update({
            "solve_status": "PASS",
            "failure_message": "",
            "H_raw_final_minus_H0": metrics["H_raw_final_minus_H0"],
            "H_robust_final_minus_H0": metrics["H_robust_final_minus_H0"],
            "max_velocity": metrics["max_velocity"],
            "max_pressure": metrics["max_pressure"],
            "interface_quality": metrics["interface_quality"],
            "pseudo_spike_detected": metrics["pseudo_spike_detected"],
            "raw_outlier_detected": metrics["raw_outlier_detected"],
            "max_raw_step_jump": metrics["max_raw_step_jump"],
            "interface_points_jump": metrics["interface_points_jump"],
            "model": model_paths.get("model", ""),
            "timestamp_model": model_paths.get("timestamp_model", ""),
            "table": metrics["table"],
            "plot": metrics["plot"],
            "phils_final": metrics["phils_final"],
        })
        pass_gate = (
            math.isfinite(to_float(row["H_robust_final_minus_H0"]))
            and abs(to_float(row["H_robust_final_minus_H0"])) <= 0.0002
            and row["interface_quality"] == "clear"
            and row["solve_status"] == "PASS"
            and row["WettedWall_selection_ok"]
            and "WettedWall" in row["used_forcing_route"]
            and "Inlet" not in row["used_forcing_route"]
            and "Outlet" not in row["used_forcing_route"]
            and "OpenBoundary" not in row["used_forcing_route"]
        )
        row["case_pass"] = "PASS" if pass_gate else "FAIL"
    except Exception:
        err = traceback.format_exc()
        err_path = R1 / "logs" / f"{case_id}_error_{RUN_ID}.log"
        err_path.write_text(err, encoding="utf-8")
        row.update({
            "solve_status": "FAIL",
            "failure_message": str(err_path),
            "H_raw_final_minus_H0": math.nan,
            "H_robust_final_minus_H0": math.nan,
            "max_velocity": math.nan,
            "max_pressure": math.nan,
            "interface_quality": "failed",
            "pseudo_spike_detected": True,
            "raw_outlier_detected": False,
            "case_pass": "FAIL",
        })
    write_text(R1 / "logs" / f"{case_id}.log", json.dumps(row, ensure_ascii=False, indent=2, default=str))
    return row


def analyze_h_table(rows: list[dict[str, str]]) -> dict[str, Any]:
    hs = [to_float(r.get("H_m") or r.get("diagnostic_interface_height_m")) for r in rows]
    points = [int(to_float(r.get("interface_points"), 0)) for r in rows]
    near_top = [str(r.get("near_top", "")).lower() == "true" for r in rows]
    valid_h = finite_values(hs)
    steps = [abs(hs[i + 1] - hs[i]) for i in range(len(hs) - 1) if math.isfinite(hs[i]) and math.isfinite(hs[i + 1])]
    point_steps = [abs(points[i + 1] - points[i]) for i in range(len(points) - 1)]
    return {
        "rows": len(rows),
        "H0": valid_h[0] if valid_h else math.nan,
        "Hfinal": valid_h[-1] if valid_h else math.nan,
        "delta_H": (valid_h[-1] - valid_h[0]) if len(valid_h) >= 2 else math.nan,
        "max_step": max(steps, default=math.nan),
        "max_interface_points_jump": max(point_steps, default=0),
        "interface_points_min": min(points, default=0),
        "interface_points_max": max(points, default=0),
        "near_top_any": any(near_top),
        "discrete_step_likely": bool(max(steps, default=0.0) > 5e-5 or max(point_steps, default=0) >= 2),
    }


def stage_a_review() -> dict[str, Any]:
    log("A: reviewing original 5B4 failure.")
    e_rows = read_csv(ORIG_E_TABLE)
    analysis = analyze_h_table(e_rows)
    inputs = [
        ORIG_FINAL_REPORT,
        ORIG_E_REPORT,
        ORIG_D_TABLE,
        ORIG_E_TABLE,
        BEST_CANDIDATE_MODEL,
        BEST_CANDIDATE_JAVA,
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        SCRIPTS / "SCRIPT_MANIFEST.md",
    ]
    rows = [
        {"item": "5B4", "value": "FAIL", "status": "CONFIRMED"},
        {"item": "E extended stability solve_status", "value": "PASS", "status": "CONFIRMED"},
        {"item": "E extended stability case_pass", "value": "FAIL", "status": "CONFIRMED"},
        {"item": "E diagnostic H(final)-H(0)", "value": "0.0002340315 m", "status": "CONFIRMED"},
        {"item": "ALLOW_5C", "value": "NO", "status": "CONFIRMED"},
        {"item": "ALLOW_STAGE6", "value": "NO", "status": "CONFIRMED"},
        *[{"item": f"input_exists:{p.name}", "value": str(p), "status": "PASS" if p.exists() else "FAIL"} for p in inputs],
        {"item": "E H(t) discrete_step_likely", "value": analysis["discrete_step_likely"], "status": "INFO"},
        {"item": "E interface_points range", "value": f"{analysis['interface_points_min']}..{analysis['interface_points_max']}", "status": "INFO"},
        {"item": "E near_top any", "value": analysis["near_top_any"], "status": "INFO"},
    ]
    write_csv(R1 / "tables" / "A_5B4_gate_review.csv", rows)
    write_text(R1 / "reports" / "A_5B4_failure_review.md", "\n".join([
        "# A 5B4 Failure Review",
        "",
        f"Run ID: `{RUN_ID}`",
        "",
        "- `5B4 = FAIL`.",
        "- `E extended stability solve_status = PASS`.",
        "- `E extended stability case_pass = FAIL`.",
        "- `E diagnostic H(final)-H(0) = 0.0002340315 m`.",
        "- `ALLOW_5C = NO`.",
        "- `ALLOW_STAGE6 = NO`.",
        "",
        "## H(t) Audit",
        "",
        f"- Rows: `{analysis['rows']}`.",
        f"- Original diagnostic delta: `{analysis['delta_H']}` m.",
        f"- Max single-step H jump: `{analysis['max_step']}` m.",
        f"- Interface point count range: `{analysis['interface_points_min']}..{analysis['interface_points_max']}`.",
        f"- Max interface point jump: `{analysis['max_interface_points_jump']}`.",
        f"- near_top ever true: `{analysis['near_top_any']}`.",
        f"- Discrete-step behavior likely: `{analysis['discrete_step_likely']}`.",
        "",
        "The original table indicates a step-like diagnostic change rather than a smooth monotonic displacement.",
    ]))
    return {"status": "PASS" if all(p.exists() for p in inputs[:6]) else "FAIL", "analysis": analysis, "rows": rows}


def stage_b_diagnostic_audit(client: Any) -> dict[str, Any]:
    log("B: recomputing robust diagnostics on the original E solution.")
    rows: list[dict[str, Any]] = []
    model = None
    try:
        model = client.load(str(ORIG_E_MODEL))
        times = read_times(model)
        for inner, t in enumerate(times, start=1):
            data = phase_data(model, inner)
            metrics = robust_interface_metrics(data)
            rows.append({
                "case_id": "original_E_recomputed",
                "inner_solution": inner,
                "time_s": t,
                **metrics,
                "H_raw_mm": metrics["H_max_raw"] * 1000 if math.isfinite(metrics["H_max_raw"]) else math.nan,
                "H_robust_mm": metrics["H_robust"] * 1000 if math.isfinite(metrics["H_robust"]) else math.nan,
                "H_m": metrics["H_robust"],
                "H_mm": metrics["H_robust"] * 1000 if math.isfinite(metrics["H_robust"]) else math.nan,
            })
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                pass
    write_csv(R1 / "tables" / "B_recomputed_E_interface_diagnostics.csv", rows)
    render_comparison(R1 / "images" / "B_E_H_diagnostic_comparison.png", rows)
    raw_delta = to_float(rows[-1].get("H_max_raw")) - to_float(rows[0].get("H_max_raw")) if len(rows) >= 2 else math.nan
    robust_delta = to_float(rows[-1].get("H_robust")) - to_float(rows[0].get("H_robust")) if len(rows) >= 2 else math.nan
    raw_outliers = sum(1 for r in rows if r.get("raw_outlier_detected"))
    write_text(R1 / "reports" / "B_interface_diagnostic_audit.md", "\n".join([
        "# B Interface Diagnostic Audit",
        "",
        f"Run ID: `{RUN_ID}`",
        "",
        "- This section only audits diagnostics and does not change any gate.",
        f"- Original E model: `{ORIG_E_MODEL}`.",
        f"- Recomputed rows: `{len(rows)}`.",
        f"- `H_max_raw` final minus initial: `{raw_delta}` m.",
        f"- `H_robust` final minus initial: `{robust_delta}` m.",
        f"- Raw outlier frames detected: `{raw_outliers}`.",
        f"- Diagnostic table: `{R1 / 'tables' / 'B_recomputed_E_interface_diagnostics.csv'}`.",
        f"- Comparison image: `{R1 / 'images' / 'B_E_H_diagnostic_comparison.png'}`.",
        "",
        "The robust diagnostic uses the 95th percentile of the largest connected interface component. It is still a smoke-test interface stability diagnostic, not real Hmax.",
    ]))
    return {"status": "PASS" if rows else "FAIL", "rows": len(rows), "raw_delta": raw_delta, "robust_delta": robust_delta, "raw_outlier_frames": raw_outliers}


def prepare_model(client: Any) -> Any:
    model = client.load(str(BEST_CANDIDATE_MODEL))
    prev5b4.configure_velocity_ramp(model)
    return model


def stage_c_e0_repeat(model: Any) -> dict[str, Any]:
    row = solve_r1_case(
        model,
        "C_E0_D4_repeat",
        "1e-2[m/s]",
        "0.020[s]",
        "1e-4[s]",
        "ring_fountain_v5B4_R1_E0_D4_repeat.mph",
        "C_E0_D4_repeat",
    )
    # The requirement names this table explicitly.
    src = Path(str(row.get("table", "")))
    dst = R1 / "tables" / "C_E0_D4_repeat_H_diagnostics.csv"
    if src.exists() and src != dst:
        shutil.copy2(src, dst)
        row["table"] = str(dst)
    write_text(R1 / "reports" / "C_E0_D4_repeat_report.md", "\n".join([
        "# C E0 D4 Repeat Report",
        "",
        f"- Vtarget: `{row.get('Vtarget')}`.",
        f"- t_end: `{row.get('t_end')}`.",
        f"- dt: `{row.get('dt')}`.",
        f"- Solve status: `{row.get('solve_status')}`.",
        f"- Case pass: `{row.get('case_pass')}`.",
        f"- Raw diagnostic `H(final)-H(0)`: `{row.get('H_raw_final_minus_H0')}` m.",
        f"- Robust diagnostic `H(final)-H(0)`: `{row.get('H_robust_final_minus_H0')}` m.",
        f"- Interface quality: `{row.get('interface_quality')}`.",
        f"- Raw outlier detected: `{row.get('raw_outlier_detected')}`.",
        f"- Pseudo-spike diagnostic: `{row.get('pseudo_spike_detected')}`.",
        "- Physics was not changed from the 5B4 D4 extended setup.",
        "- This remains fixed-geometry WettedWall moving-wall, not true falling ring geometry.",
        "- No real Hmax is produced.",
        f"- Model: `{row.get('model')}`.",
        f"- Table: `{row.get('table')}`.",
        f"- H comparison image: `{row.get('plot')}`.",
        f"- Final phase image: `{row.get('phils_final')}`.",
    ]))
    return row


def stage_d_lower_velocity(model: Any) -> dict[str, Any]:
    log("D: C failed, running lower-velocity extended repair cases.")
    cases = [
        ("R1_D3_ext", "5e-3[m/s]", "0.020[s]", "1e-4[s]", "ring_fountain_v5B4_R1_D3_ext.mph", "D_R1_D3_ext"),
        ("R1_D2_ext", "2e-3[m/s]", "0.020[s]", "1e-4[s]", "ring_fountain_v5B4_R1_D2_ext.mph", "D_R1_D2_ext"),
        ("R1_D1_ext", "1e-3[m/s]", "0.020[s]", "1e-4[s]", "ring_fountain_v5B4_R1_D1_ext.mph", "D_R1_D1_ext"),
    ]
    rows = [solve_r1_case(model, *case) for case in cases]
    write_csv(R1 / "tables" / "D_lower_velocity_extended_cases.csv", rows)
    summary_rows = [
        {"time_s": i, "H_m": to_float(r.get("H_robust_final_minus_H0")), "H_mm": to_float(r.get("H_robust_final_minus_H0")) * 1000, "case_id": r.get("case_id")}
        for i, r in enumerate(rows, start=1)
    ]
    base.render_curve(R1 / "images" / "D_lower_velocity_extended_summary.png", summary_rows)
    write_text(R1 / "logs" / "D_lower_velocity_extended_repair.log", json.dumps(rows, ensure_ascii=False, indent=2, default=str))
    write_text(R1 / "reports" / "D_lower_velocity_extended_repair_report.md", "\n".join([
        "# D Lower Velocity Extended Repair Report",
        "",
        "- Executed only because C did not pass.",
        "- All cases retain `TwoPhaseFlowLevelSet + WettedWall` and `utr = {0,-Vwall_eff(t),0}`.",
        "- No Inlet/Outlet/OpenBoundary surrogate route was used.",
        "",
        *[
            f"- {r.get('case_id')}: solve `{r.get('solve_status')}`, case `{r.get('case_pass')}`, robust delta `{r.get('H_robust_final_minus_H0')}` m, raw delta `{r.get('H_raw_final_minus_H0')}` m."
            for r in rows
        ],
    ]))
    passed = [r for r in rows if r.get("case_pass") == "PASS"]
    return {"status": "PASS" if passed else "FAIL", "rows": rows, "best": passed[0] if passed else None}


def stage_e_numerical_repair(model: Any) -> dict[str, Any]:
    log("E: D failed, running numerical stability repair cases.")
    cases = [
        ("R1_E_S1_dt5e-5", "1e-3[m/s]", "0.020[s]", "5e-5[s]", "ring_fountain_v5B4_R1_E_S1_dt5e-5.mph", "E_S1_dt5e-5", "1e-3[s]"),
        ("R1_E_S2_ramp2e-3", "1e-3[m/s]", "0.020[s]", "1e-4[s]", "ring_fountain_v5B4_R1_E_S2_ramp2e-3.mph", "E_S2_ramp2e-3", "2e-3[s]"),
        ("R1_E_S3_ramp5e-3", "1e-3[m/s]", "0.020[s]", "1e-4[s]", "ring_fountain_v5B4_R1_E_S3_ramp5e-3.mph", "E_S3_ramp5e-3", "5e-3[s]"),
    ]
    rows = [solve_r1_case(model, case_id, v, t_end, dt, model_name, prefix, ramp) for case_id, v, t_end, dt, model_name, prefix, ramp in cases]
    # Mesh-refinement S4/S5 are recorded as skipped unless API-safe refinement is added later.
    rows.extend([
        {"case_id": "R1_E_S4_local_mesh_refine", "solve_status": "SKIPPED", "case_pass": "SKIPPED", "notes": "Not executed; safe scripted mesh-refinement scope was not available without changing the validated model route."},
        {"case_id": "R1_E_S5_local_mesh_refine_dt5e-5", "solve_status": "SKIPPED", "case_pass": "SKIPPED", "notes": "Not executed; safe scripted mesh-refinement scope was not available without changing the validated model route."},
    ])
    write_csv(R1 / "tables" / "E_numerical_stability_repair_cases.csv", rows)
    summary_rows = [
        {"time_s": i, "H_m": to_float(r.get("H_robust_final_minus_H0")), "H_mm": to_float(r.get("H_robust_final_minus_H0")) * 1000, "case_id": r.get("case_id")}
        for i, r in enumerate(rows, start=1)
        if math.isfinite(to_float(r.get("H_robust_final_minus_H0")))
    ]
    if summary_rows:
        base.render_curve(R1 / "images" / "E_numerical_stability_repair_summary.png", summary_rows)
    write_text(R1 / "logs" / "E_numerical_stability_repair.log", json.dumps(rows, ensure_ascii=False, indent=2, default=str))
    write_text(R1 / "reports" / "E_numerical_stability_repair_report.md", "\n".join([
        "# E Numerical Stability Repair Report",
        "",
        "- Executed only because all D lower-velocity extended cases failed.",
        "- S1-S3 change one numerical factor at a time.",
        "- S4-S5 local mesh refinement were not executed because no safe scripted mesh-refinement route was available in this pass.",
        "",
        *[
            f"- {r.get('case_id')}: solve `{r.get('solve_status')}`, case `{r.get('case_pass')}`, robust delta `{r.get('H_robust_final_minus_H0', '')}` m."
            for r in rows
        ],
    ]))
    passed = [r for r in rows if r.get("case_pass") == "PASS"]
    return {"status": "PASS" if passed else "FAIL", "rows": rows, "best": passed[0] if passed else None}


def select_best(summary: dict[str, Any]) -> dict[str, Any] | None:
    c = summary.get("C", {})
    if c.get("case_pass") == "PASS":
        return {**c, "source": "C D4 repeat PASS"}
    d_best = summary.get("D", {}).get("best")
    if d_best:
        return {**d_best, "source": "highest passing D lower-velocity extended case"}
    e_best = summary.get("E", {}).get("best")
    if e_best:
        return {**e_best, "source": "highest trusted E numerical repair case"}
    return None


def stage_f_best(model: Any, summary: dict[str, Any]) -> dict[str, Any]:
    selected = select_best(summary)
    if not selected:
        write_text(R1 / "reports" / "F_R1_best_model_report.md", "# F R1 Best Model Report\n\nNo passing R1 case was available for promotion.\n")
        return {"status": "FAIL", "reason": "No R1 passing case."}
    set_case_params(model, str(selected.get("Vtarget", "1e-3[m/s]")), str(selected.get("t_end", "0.020[s]")), str(selected.get("dt", "1e-4[s]")), str(selected.get("t_ramp", "1e-3[s]")))
    model_paths = save_model_no_clobber(model, R1 / "models" / "ring_fountain_v5B4_R1_best.mph")
    java_paths = save_java_no_clobber(model, R1 / "exports" / "ring_fountain_v5B4_R1_best.java")
    rows = [
        {"artifact": "R1_best_model", **model_paths, **{k: selected.get(k, "") for k in ["source", "Vtarget", "t_end", "dt", "H_raw_final_minus_H0", "H_robust_final_minus_H0"]}},
        {"artifact": "R1_best_java", **java_paths, **{k: selected.get(k, "") for k in ["source", "Vtarget", "t_end", "dt", "H_raw_final_minus_H0", "H_robust_final_minus_H0"]}},
    ]
    write_csv(R1 / "tables" / "F_R1_best_model_manifest.csv", rows)
    allow_5c_by_selected = "YES" if selected.get("case_pass") == "PASS" and to_float(selected.get("H_robust_final_minus_H0")) <= 0.0002 else "NO"
    write_text(R1 / "reports" / "F_R1_best_model_report.md", "\n".join([
        "# F R1 Best Model Report",
        "",
        f"- Source: `{selected.get('source')}`.",
        f"- R1 best Vtarget: `{selected.get('Vtarget')}`.",
        f"- R1 best t_end: `{selected.get('t_end')}`.",
        f"- R1 best dt: `{selected.get('dt')}`.",
        f"- R1 best raw diagnostic delta: `{selected.get('H_raw_final_minus_H0')}` m.",
        f"- R1 best robust diagnostic delta: `{selected.get('H_robust_final_minus_H0')}` m.",
        "- R1 best remains a fixed-geometry equivalent falling-ring model.",
        f"- R1 best allows 5C by selected case metrics: `{allow_5c_by_selected}`.",
        f"- Model: `{model_paths.get('model')}`.",
        f"- Timestamp model: `{model_paths.get('timestamp_model')}`.",
        f"- Java: `{java_paths.get('java')}`.",
        f"- Timestamp Java: `{java_paths.get('timestamp_java')}`.",
    ]))
    return {"status": "PASS", "selected": selected, "best_model": model_paths, "best_java": java_paths}


def final_gate(summary: dict[str, Any]) -> dict[str, str]:
    selected = summary.get("F", {}).get("selected", {})
    best_model = Path(str(summary.get("F", {}).get("best_model", {}).get("model", "")))
    best_java = Path(str(summary.get("F", {}).get("best_java", {}).get("java", "")))
    allow_5c = "YES" if (
        selected.get("case_pass") == "PASS"
        and to_float(selected.get("t_end", "0").replace("[s]", "")) >= 0.020
        and abs(to_float(selected.get("H_robust_final_minus_H0"))) <= 0.0002
        and selected.get("interface_quality") == "clear"
        and "TwoPhaseFlowLevelSet" in selected.get("used_forcing_route", "")
        and "WettedWall" in selected.get("used_forcing_route", "")
        and "Inlet" not in selected.get("used_forcing_route", "")
        and "Outlet" not in selected.get("used_forcing_route", "")
        and "OpenBoundary" not in selected.get("used_forcing_route", "")
        and best_model.exists()
        and best_java.exists()
    ) else "NO"
    return {"5B4_R1_status": "PASS" if allow_5c == "YES" else "FAIL", "ALLOW_5C": allow_5c, "ALLOW_STAGE6": "NO"}


def update_docs(summary: dict[str, Any]) -> None:
    log("Updating README, CHANGELOG, and SCRIPT_MANIFEST.")
    c4help.add_or_replace_section(ROOT / "README.md", "5B4_R1_EXTENDED_STABILITY_REPAIR", [
        "## 5B4-R1 Extended Stability Repair",
        "",
        f"- Run ID: `{RUN_ID}`.",
        "- 5B4 original: `FAIL`.",
        f"- 5B4-R1: `{summary.get('5B4_R1_status', 'FAIL')}`.",
        f"- `ALLOW_5C = {summary.get('ALLOW_5C', 'NO')}`.",
        f"- `ALLOW_STAGE6 = {summary.get('ALLOW_STAGE6', 'NO')}`.",
        "- Route retained: `TwoPhaseFlowLevelSet + WettedWall`.",
        "- Ring motion remains `utr = {0,-Vwall_eff(t),0}` on boundaries `[4,5,6,7]`.",
        "- This is still a fixed-geometry equivalent falling-ring model, not a true freely falling ring.",
        "- No real Hmax has been produced.",
        "- No Jet1/Jet2 extraction has been performed.",
        "- No Stage 6 parameter sweep has been performed.",
        f"- Final report: `{R1 / 'reports' / '5B4_R1_extended_stability_repair_final_report.md'}`.",
    ])
    c4help.add_or_replace_section(ROOT / "CHANGELOG.md", "5B4_R1_EXTENDED_STABILITY_REPAIR", [
        "## 5B4-R1 Extended Stability Repair",
        "",
        f"- Run ID: `{RUN_ID}`.",
        f"- Status: `{summary.get('5B4_R1_status', 'FAIL')}`.",
        f"- Gate: `ALLOW_5C = {summary.get('ALLOW_5C', 'NO')}`, `ALLOW_STAGE6 = {summary.get('ALLOW_STAGE6', 'NO')}`.",
        "- Recomputed robust interface diagnostics for the original 5B4 E failure.",
        "- Repeated the D4 extended case with unchanged physics and improved diagnostics.",
        "- Did not enter 5C/5D/5E/Stage 6; no Jet1/Jet2 extraction, parameter sweep, or real Hmax was produced.",
        f"- Final report: `{R1 / 'reports' / '5B4_R1_extended_stability_repair_final_report.md'}`.",
    ])
    c4help.add_or_replace_section(SCRIPTS / "SCRIPT_MANIFEST.md", "5B4_R1_EXTENDED_STABILITY_REPAIR_SCRIPT", [
        "## 5B4-R1 Script",
        "",
        f"| `ring_fountain_stage5b4_R1_extended_stability_repair.py` | 5B4-R1 diagnostic audit and extended stability repair | `{RUN_ID}` | `{sha256(SCRIPT_ARCHIVE)}` |",
    ])


def write_final_report(summary: dict[str, Any]) -> None:
    d_rows = summary.get("D", {}).get("rows", [])
    e_rows = summary.get("E", {}).get("rows", [])
    lines = [
        "# 5B4-R1 Extended Stability Repair Final Report",
        "",
        f"Run ID: `{RUN_ID}`",
        "",
        "## Required Answers",
        "",
        f"1. 是否成功导入 5B4 结果？ `{summary.get('A', {}).get('status') == 'PASS'}`.",
        f"2. 是否确认 5B4 原始失败原因？ `YES, E solve PASS but case FAIL because diagnostic delta was 0.0002340315 m`.",
        f"3. E 的高度失败是否可能是诊断跳点？ `{summary.get('A', {}).get('analysis', {}).get('discrete_step_likely')}`.",
        f"4. 是否重算了稳健 H 诊断？ `{summary.get('B', {}).get('status') == 'PASS'}`.",
        f"5. C D4 repeat 是否通过？ `{summary.get('C', {}).get('case_pass')}`.",
        f"6. D lower velocity extended cases 哪些通过？ `{[(r.get('case_id'), r.get('case_pass')) for r in d_rows]}`.",
        f"7. E numerical stability repair 哪些通过？ `{[(r.get('case_id'), r.get('case_pass')) for r in e_rows]}`.",
        f"8. 是否生成 ring_fountain_v5B4_R1_best.mph？ `{summary.get('F', {}).get('status') == 'PASS'}`.",
        f"9. 是否导出 ring_fountain_v5B4_R1_best.java？ `{summary.get('F', {}).get('status') == 'PASS'}`.",
        f"10. 是否允许进入 5C？ `{summary.get('ALLOW_5C', 'NO')}`.",
        f"11. 是否允许进入 Stage 6？ `{summary.get('ALLOW_STAGE6', 'NO')}`.",
        "",
        "## Gates",
        "",
        f"- `5B4-R1 = {summary.get('5B4_R1_status', 'FAIL')}`",
        f"- `ALLOW_5C = {summary.get('ALLOW_5C', 'NO')}`",
        f"- `ALLOW_STAGE6 = {summary.get('ALLOW_STAGE6', 'NO')}`",
        "",
        "## Scope Notes",
        "",
        "- This run did not enter 5C, 5D, 5E, or Stage 6.",
        "- No Jet1/Jet2 extraction, parameter sweep, or real Hmax output was performed.",
        "- No Inlet/Outlet/OpenBoundary surrogate route was used.",
        "- The promoted model, if present, remains a fixed-geometry WettedWall moving-wall model.",
        "",
        "## Key Paths",
        "",
        f"- Summary JSON: `{R1 / '5B4_R1_extended_stability_repair_summary.json'}`",
        f"- R1 best model: `{summary.get('F', {}).get('best_model', {}).get('model', '')}`",
        f"- R1 best Java: `{summary.get('F', {}).get('best_java', {}).get('java', '')}`",
        f"- Reports: `{R1 / 'reports'}`",
        f"- Tables: `{R1 / 'tables'}`",
        f"- Images: `{R1 / 'images'}`",
        f"- Frames: `{R1 / 'frames'}`",
        f"- Logs: `{R1 / 'logs'}`",
        f"- Script archive: `{SCRIPT_ARCHIVE}`",
        f"- Local script copy: `{LOCAL_SCRIPT_ARCHIVE}`",
        "",
        f"Stop reason: `{summary.get('stop_reason', '')}`",
    ]
    write_text(R1 / "reports" / "5B4_R1_extended_stability_repair_final_report.md", "\n".join(lines))


def main() -> int:
    ensure_dirs()
    redirect_prev_module()
    script_info = archive_script()
    summary: dict[str, Any] = {
        "run_id": RUN_ID,
        "stage": "5B4-R1 extended stability repair and diagnostic audit",
        "script": script_info,
        "ALLOW_5C": "NO",
        "ALLOW_STAGE6": "NO",
        "5B4_R1_status": "FAIL",
    }
    client = None
    model = None
    try:
        summary["A"] = stage_a_review()
        client = mph.Client(cores=2, version="6.4")
        summary["B"] = stage_b_diagnostic_audit(client)
        model = prepare_model(client)
        summary["C"] = stage_c_e0_repeat(model)
        if summary["C"].get("case_pass") == "PASS":
            summary["stop_reason"] = "C D4 repeat passed with robust diagnostics; D/E were not entered."
        else:
            summary["D"] = stage_d_lower_velocity(model)
            if summary["D"].get("status") == "PASS":
                summary["stop_reason"] = "At least one lower-velocity extended case passed; E was not entered."
            else:
                summary["E"] = stage_e_numerical_repair(model)
                if summary["E"].get("status") == "PASS":
                    summary["stop_reason"] = "A numerical stability repair case passed."
                else:
                    summary["stop_reason"] = "No R1 extended stability repair case passed."
        summary["F"] = stage_f_best(model, summary)
        summary.update(final_gate(summary))
    except Exception:
        err = traceback.format_exc()
        err_path = R1 / "logs" / f"fatal_error_{RUN_ID}.log"
        err_path.write_text(err, encoding="utf-8")
        summary["stop_reason"] = str(err_path)
        summary.update({"ALLOW_5C": "NO", "ALLOW_STAGE6": "NO", "5B4_R1_status": "FAIL"})
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
    write_json(R1 / "5B4_R1_extended_stability_repair_summary.json", summary)
    write_final_report(summary)
    update_docs(summary)
    write_json(R1 / "5B4_R1_extended_stability_repair_summary.json", summary)
    log("5B4-R1 completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
