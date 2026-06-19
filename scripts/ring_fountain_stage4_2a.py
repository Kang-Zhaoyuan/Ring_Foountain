# -*- coding: utf-8 -*-
"""Stage 4.2A relative-velocity check for the COMSOL Ring Fountain model.

This script starts from the manually reviewed Stage 4.1 model, writes the
confirmed boundary selections into the model, then performs three conservative
fixed-geometry moving-wall comparison cases.  It does not proceed to Stage 5.
"""

from __future__ import annotations

import csv
import json
import math
import shutil
import struct
import traceback
import zipfile
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any

import jpype
import mph
import numpy as np


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
STAGE4 = ROOT / "04_moving_ring_model"
INPUT = STAGE4 / "models" / "ring_fountain_v3_boundary_review_package.mph"
NAMED = STAGE4 / "models" / "ring_fountain_v3_boundary_named.mph"
CHECK = STAGE4 / "relative_velocity_check"
SCRIPTS = ROOT / "scripts"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = STAGE4 / "logs" / f"stage4_2a_{RUN_ID}.log"

RING_IDS = [4, 5, 6, 7]
BOUNDARY_NAMES = {
    "sel_ring_wall_inner": [4],
    "sel_ring_wall_outer": [7],
    "sel_ring_wall_top": [6],
    "sel_ring_wall_bottom": [5],
    "sel_ring_wall_confirmed": RING_IDS,
}


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def make_dirs() -> None:
    for base in [STAGE4, CHECK]:
        for sub in ["models", "reports", "images", "tables", "logs", "frames"]:
            (base / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def jints(values: list[int]) -> Any:
    return jpype.JArray(jpype.JInt)(values)


def ensure_selection(model: Any, tag: str, ids: list[int], label: str) -> None:
    selections = model.java.component("comp1").selection()
    if tag in [str(x) for x in list(selections.tags())]:
        selections.remove(tag)
    selections.create(tag, "Explicit")
    node = selections.get(tag)
    node.label(label)
    node.geom("geom1", 1)
    node.set(jints(ids))


def selection_entities(model: Any, tag: str) -> list[int]:
    node = model.java.component("comp1").selection(tag)
    return [int(x) for x in list(node.entities(1))]


def feature_entities(model: Any, ftag: str) -> list[int]:
    feat = model.java.component("comp1").physics("spf").feature(ftag)
    return [int(x) for x in list(feat.selection().entities(1))]


def set_feature_entities(model: Any, ftag: str, ids: list[int]) -> None:
    feat = model.java.component("comp1").physics("spf").feature(ftag)
    feat.selection().set(jints(ids))


def getstr(feature: Any, key: str) -> str:
    try:
        return str(feature.getString(key))
    except Exception:
        return ""


def save_named_model(client: Any) -> dict[str, Any]:
    log(f"Loading review model for named selections: {INPUT}")
    model = client.load(INPUT)
    try:
        for tag, ids in BOUNDARY_NAMES.items():
            ensure_selection(model, tag, ids, tag)
        checks = {tag: selection_entities(model, tag) for tag in BOUNDARY_NAMES}
        ts = STAGE4 / "models" / f"ring_fountain_v3_boundary_named_{RUN_ID}.mph"
        model.save(NAMED)
        model.save(ts)
        log(f"Saved named selection model: {NAMED}")
        return {"model": str(NAMED), "timestamp_model": str(ts), "selections": checks}
    finally:
        try:
            client.remove(model)
        except Exception:
            pass


def set_time_list(model: Any, t_end_name: str) -> None:
    for stag in ["std1"]:
        try:
            study = model.java.study(stag)
            for ftag in [str(x) for x in list(study.feature().tags())]:
                feat = study.feature(ftag)
                if "time" in ftag.lower() or "time" in str(feat.getType()).lower():
                    feat.set("tlist", f"range(0,{t_end_name}/4,{t_end_name})")
                    return
        except Exception:
            pass


def configure_wall(model: Any, moving: bool, speed_expr: str) -> dict[str, Any]:
    spf = model.java.component("comp1").physics("spf")
    wall = spf.feature("wallbc1")
    existing = feature_entities(model, "wallbc1")
    if sorted(existing) != sorted(RING_IDS):
        raise RuntimeError(f"spf.wallbc1 selection {existing} does not match confirmed ring boundaries {RING_IDS}")
    wall.set("BoundaryCondition", "NoSlip")
    if moving:
        wall.set("SlidingWall", "1")
        wall.set("TranslationalVelocityOption", "Manual")
        wall.set("utr", ["0", "0", speed_expr])
    else:
        wall.set("SlidingWall", "0")
        wall.set("TranslationalVelocityOption", "ZeroFixedWall")
        wall.set("utr", ["0", "0", "0"])
    return {
        "feature": "spf/wallbc1",
        "BoundaryCondition": getstr(wall, "BoundaryCondition"),
        "SlidingWall": getstr(wall, "SlidingWall"),
        "TranslationalVelocityOption": getstr(wall, "TranslationalVelocityOption"),
        "selection": feature_entities(model, "wallbc1"),
        "selection_binding": "wallbc1 uses COMSOL's existing noneditable explicit selection; verified equal to sel_ring_wall_confirmed [4,5,6,7]",
        "utr_set": ["0", "0", speed_expr if moving else "0"],
    }


def configure_inlet_outlet(model: Any, inlet_ids: list[int], outlet_ids: list[int], u0_expr: str) -> dict[str, Any]:
    spf = model.java.component("comp1").physics("spf")
    inlet = spf.feature("inl1")
    outlet = spf.feature("out1")
    inlet.selection().set(jints(inlet_ids))
    outlet.selection().set(jints(outlet_ids))
    inlet.set("BoundaryCondition", "Velocity")
    inlet.set("ComponentWise", "NormalInflowVelocity")
    inlet.set("U0in", u0_expr)
    outlet.set("BoundaryCondition", "Pressure")
    outlet.set("p0", "0")
    return {
        "inlet_feature": "spf/inl1",
        "inlet_ids": feature_entities(model, "inl1"),
        "outlet_feature": "spf/out1",
        "outlet_ids": feature_entities(model, "out1"),
        "U0in": getstr(inlet, "U0in"),
        "inlet_boundary_direction": "boundary 2 bottom inlet is +z/upward; boundary 3 top inlet is -z/downward",
    }


def remove_stage3_scale_params_for_solve(model: Any) -> dict[str, Any]:
    """Remove Stage 3 postprocessing scale parameters that block equation compile."""
    removed: list[str] = []
    adjusted: list[str] = []
    param = model.java.param()
    for name in ["U_impact", "g_const", "H_drop"]:
        try:
            param.remove(name)
            removed.append(name)
        except Exception:
            try:
                if name == "U_impact":
                    model.parameter(name, "0[m/s]")
                    adjusted.append(name)
            except Exception:
                pass
    return {
        "removed": removed,
        "adjusted": adjusted,
        "reason": "Stage 3 scale-only parameters caused a duplicate global name with the Gravity feature during transient equation compilation.",
    }


def eval_array(model: Any, expr: str, unit: str | None = None, inner: Any = "last") -> np.ndarray:
    if unit:
        value = model.evaluate(expr, unit=unit, inner=inner)
    else:
        value = model.evaluate(expr, inner=inner)
    return np.asarray(value, dtype=float)


def finite_flat(a: np.ndarray) -> np.ndarray:
    arr = np.asarray(a, dtype=float).reshape(-1)
    return arr[np.isfinite(arr)]


def param_float(model: Any, expr: str, unit: str = "m") -> float:
    arr = finite_flat(model.evaluate(expr, unit=unit))
    if arr.size == 0:
        raise ValueError(expr)
    return float(np.nanmean(arr))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(row.get(key), ensure_ascii=False) if isinstance(row.get(key), (list, dict)) else row.get(key) for key in keys})


def png_write(path: Path, width: int, height: int, pixels: bytearray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw.extend(pixels[y * stride:(y + 1) * stride])
    def chunk(name: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b""))


def put(pixels: bytearray, width: int, height: int, x: int, y: int, color: tuple[int, int, int]) -> None:
    if 0 <= x < width and 0 <= y < height:
        i = (y * width + x) * 3
        pixels[i:i + 3] = bytes(color)


def line(pixels: bytearray, width: int, height: int, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int], thick: int = 1) -> None:
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        for ox in range(-thick, thick + 1):
            for oy in range(-thick, thick + 1):
                put(pixels, width, height, x0 + ox, y0 + oy, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def color_map(value: float, vmin: float, vmax: float) -> tuple[int, int, int]:
    if not math.isfinite(value):
        return (230, 230, 230)
    if vmax <= vmin:
        t = 0.5
    else:
        t = max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))
    if t < 0.5:
        q = t / 0.5
        return (int(40 + 40 * q), int(90 + 140 * q), int(190 - 40 * q))
    q = (t - 0.5) / 0.5
    return (int(80 + 170 * q), int(230 - 120 * q), int(150 - 110 * q))


def render_field(path: Path, title: str, r: np.ndarray, z: np.ndarray, value: np.ndarray, vector: tuple[np.ndarray, np.ndarray] | None = None) -> dict[str, Any]:
    width, height = 980, 760
    pixels = bytearray([248, 248, 246] * width * height)
    finite = np.isfinite(r) & np.isfinite(z) & np.isfinite(value)
    if not np.any(finite):
        png_write(path, width, height, pixels)
        return {"ok": False, "file": str(path), "error": "no finite field samples"}
    rr, zz, vv = r[finite], z[finite], value[finite]
    ri, ro = 0.008, 0.020
    zlo, zhi = -0.008, 0.008
    rlo, rhi = -0.001, 0.035
    margin = 60
    def tx(x: float) -> int:
        return int(margin + (x - rlo) / (rhi - rlo) * (width - 2 * margin))
    def ty(y: float) -> int:
        return int(height - margin - (y - zlo) / (zhi - zlo) * (height - 2 * margin))
    vmin, vmax = float(np.nanpercentile(vv, 2)), float(np.nanpercentile(vv, 98))
    step = max(1, len(rr) // 18000)
    for x, y, val in zip(rr[::step], zz[::step], vv[::step]):
        px, py = tx(float(x)), ty(float(y))
        col = color_map(float(val), vmin, vmax)
        for ox in range(-2, 3):
            for oy in range(-2, 3):
                put(pixels, width, height, px + ox, py + oy, col)
    # Ring outline.
    line(pixels, width, height, tx(ri), ty(-0.001), tx(ro), ty(-0.001), (20, 20, 20), 2)
    line(pixels, width, height, tx(ri), ty(0.001), tx(ro), ty(0.001), (20, 20, 20), 2)
    line(pixels, width, height, tx(ri), ty(-0.001), tx(ri), ty(0.001), (20, 20, 20), 2)
    line(pixels, width, height, tx(ro), ty(-0.001), tx(ro), ty(0.001), (20, 20, 20), 2)
    # Optional vector overlay, decimated.
    if vector is not None:
        u, w = vector
        fv = finite & np.isfinite(u) & np.isfinite(w)
        idxs = np.where(fv)[0]
        if idxs.size:
            for idx in idxs[::max(1, idxs.size // 120)]:
                x, y = float(r[idx]), float(z[idx])
                if not (rlo <= x <= rhi and zlo <= y <= zhi):
                    continue
                scale = 0.015
                x0, y0 = tx(x), ty(y)
                x1, y1 = tx(x + float(u[idx]) * scale), ty(y + float(w[idx]) * scale)
                line(pixels, width, height, x0, y0, x1, y1, (15, 15, 15), 1)
    png_write(path, width, height, pixels)
    return {"ok": True, "file": str(path), "title": title, "vmin": vmin, "vmax": vmax, "method": "Python rendering of COMSOL solved field samples near the ring"}


def center_mask(model: Any, r: np.ndarray, z: np.ndarray) -> np.ndarray:
    ri = param_float(model, "Ri", "m")
    h = param_float(model, "h_ring", "m")
    return np.isfinite(r) & np.isfinite(z) & (r >= 0) & (r <= ri) & (z >= 0) & (z <= 4 * h)


def collect_metrics_and_images(model: Any, case_id: str, img_dir: Path, table_dir: Path) -> dict[str, Any]:
    r = eval_array(model, "r", "m", inner="last").reshape(-1)
    z = eval_array(model, "z", "m", inner="last").reshape(-1)
    u = eval_array(model, "u", "m/s", inner="last").reshape(-1)
    w = eval_array(model, "w", "m/s", inner="last").reshape(-1)
    spfu = eval_array(model, "spf.U", "m/s", inner="last").reshape(-1)
    wrel = w + param_float(model, "V_ring_test", "m/s")
    mask = center_mask(model, r, z)
    w_center = w[mask & np.isfinite(w)]
    wrel_ring_mask = np.isfinite(wrel) & (r >= 0.006) & (r <= 0.022) & (z >= -0.004) & (z <= 0.004)
    summary = {
        "case": case_id,
        "w_center_above_final_mean_m_per_s": float(np.nanmean(w_center)) if w_center.size else None,
        "w_center_above_final_max_m_per_s": float(np.nanmax(w_center)) if w_center.size else None,
        "ring_near_abs_w_relative_mean_m_per_s": float(np.nanmean(np.abs(wrel[wrel_ring_mask]))) if np.any(wrel_ring_mask) else None,
        "ring_near_abs_w_relative_p95_m_per_s": float(np.nanpercentile(np.abs(wrel[wrel_ring_mask]), 95)) if np.any(wrel_ring_mask) else None,
    }
    images = [
        render_field(img_dir / f"{case_id}_velocity_magnitude_spfU.png", "spf.U", r, z, spfu),
        render_field(img_dir / f"{case_id}_axial_velocity_w.png", "w", r, z, w),
        render_field(img_dir / f"{case_id}_w_relative_to_ring.png", "w + V_ring_test", r, z, wrel),
        render_field(img_dir / f"{case_id}_ring_near_velocity_vectors.png", "velocity vectors", r, z, spfu, (u, w)),
        render_field(img_dir / f"{case_id}_ring_near_relative_velocity.png", "relative velocity", r, z, np.sqrt(u * u + wrel * wrel), (u, wrel)),
    ]
    rows: list[dict[str, Any]] = []
    for inner in range(1, 6):
        try:
            wi = eval_array(model, "w", "m/s", inner=[inner]).reshape(-1)
            ti = finite_flat(model.evaluate("t", unit="s", inner=[inner]))
            zi = eval_array(model, "z", "m", inner=[inner]).reshape(-1)
            ri = eval_array(model, "r", "m", inner=[inner]).reshape(-1)
            mi = center_mask(model, ri, zi)
            vals = wi[mi & np.isfinite(wi)]
            rows.append({
                "case": case_id,
                "inner_solution": inner,
                "time_s": float(ti[0]) if ti.size else None,
                "w_center_above_mean_m_per_s": float(np.nanmean(vals)) if vals.size else None,
                "sample_count": int(vals.size),
            })
        except Exception:
            break
    write_csv(table_dir / f"{case_id}_center_hole_w_t.csv", rows)
    return {"summary": summary, "images": images, "w_t_csv": str(table_dir / f"{case_id}_center_hole_w_t.csv")}


def solve_case(client: Any, case: dict[str, Any]) -> dict[str, Any]:
    model = client.load(NAMED)
    out_model = CHECK / "models" / f"{case['id']}.mph"
    out_ts = CHECK / "models" / f"{case['id']}_{RUN_ID}.mph"
    try:
        model.parameter("V_ring_test", "0.10[m/s]")
        model.parameter("t_end_check", "0.02[s]")
        if case.get("set_u0") is not None:
            model.parameter("U0", case["set_u0"])
        scale_param_cleanup = remove_stage3_scale_params_for_solve(model)
        set_time_list(model, "t_end_check")
        wall_info = configure_wall(model, case["moving_wall"], case["wall_speed"])
        flow_info = configure_inlet_outlet(model, case["inlet"], case["outlet"], case["u0_expr"])
        log(f"Solving {case['id']}: {case['label']}")
        model.solve()
        model.save(out_model)
        model.save(out_ts)
        outputs = collect_metrics_and_images(model, case["id"], CHECK / "images", CHECK / "tables")
        return {"case": case, "status": "PASS", "model": str(out_model), "timestamp_model": str(out_ts), "wall": wall_info, "flow": flow_info, "stage3_scale_param_cleanup": scale_param_cleanup, "outputs": outputs}
    except Exception as exc:
        err = traceback.format_exc()
        (CHECK / "logs" / f"{case['id']}_error_{RUN_ID}.log").write_text(err, encoding="utf-8")
        try:
            model.save(out_model)
        except Exception:
            pass
        return {"case": case, "status": "FAIL", "error": str(exc), "traceback": err, "model": str(out_model)}
    finally:
        try:
            client.remove(model)
        except Exception:
            pass


def append_docs(named: dict[str, Any], status: str, case_results: list[dict[str, Any]]) -> None:
    readme = ROOT / "README.md"
    changelog = ROOT / "CHANGELOG.md"
    block = f"""

## Stage 4 Boundary Confirmation And Moving-Wall Gate

- Manual boundary review result: `PASS`.
- Confirmed ring-wall boundaries: `[4, 5, 6, 7]`.
- Named selections written into the model:
  - `sel_ring_wall_inner = [4]`
  - `sel_ring_wall_outer = [7]`
  - `sel_ring_wall_top = [6]`
  - `sel_ring_wall_bottom = [5]`
  - `sel_ring_wall_confirmed = [4, 5, 6, 7]`
- Named boundary model: `{named.get('model')}`.
- Stage 4.2A relative-velocity check status: `{status}`.
- Moving wall method under test: Laminar Flow `spf.wallbc1`, `SlidingWall=1`, `TranslationalVelocityOption=Manual`, `utr=[0,0,-V_ring_test]`, selected only on `sel_ring_wall_confirmed`.
- Current limitation: this is a fixed-geometry wall-velocity approximation. It is still single-phase, has no free surface, uses an externally prescribed ring speed, and does not compute ring density, gravity, buoyancy, or fluid-structure coupling. It cannot output a true `Hmax`.
"""
    old = readme.read_text(encoding="utf-8", errors="ignore") if readme.exists() else "# COMSOL Ring Fountain Simulation\n"
    readme.write_text(old.rstrip() + "\n" + block.lstrip(), encoding="utf-8")
    ch = changelog.read_text(encoding="utf-8", errors="ignore") if changelog.exists() else "# Changelog\n"
    ch += f"""

## {datetime.now().isoformat(timespec='seconds')} - Stage 4 boundary naming and 4.2A check

- Boundary naming model: `{named.get('model')}`.
- Confirmed selections: `{json.dumps(named.get('selections'), ensure_ascii=False)}`.
- Stage 4.2A relative-velocity check: `{status}`.
- Case statuses: `{json.dumps({r['case']['id']: r['status'] for r in case_results}, ensure_ascii=False)}`.
- Formal Stage 4.2 and Stage 5A were not run by this script.
"""
    changelog.write_text(ch, encoding="utf-8")


def write_report(named: dict[str, Any], status: str, case_results: list[dict[str, Any]], review: dict[str, Any]) -> None:
    report = CHECK / "reports" / "relative_velocity_check_report.md"
    lines = [
        "# Stage 4.2A Relative Velocity Check Report",
        "",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"4.2A review status: `{status}`",
        "",
        "## Confirmed Named Selections",
        "",
        f"- Named model: `{named.get('model')}`",
        f"- Timestamp model: `{named.get('timestamp_model')}`",
        f"- Selections: `{json.dumps(named.get('selections'), ensure_ascii=False)}`",
        "",
        "## Direction Confirmation",
        "",
        "- In the current model, `spf.inl1` is on boundary 2, the bottom tank boundary `z=-Zdown`; positive normal inflow therefore points into the domain, i.e. `+z` / upward.",
        "- `spf.out1` is on boundary 3, the top tank boundary.",
        "- The axial/vertical velocity component is `w`; positive `w` is upward along `+z`.",
        "- Ring moving-wall test speed is set as `utr=[0,0,-V_ring_test]`, i.e. negative `z` / downward.",
        "",
        "## Moving Wall Property Names",
        "",
        "- Wall feature: `spf.wallbc1`.",
        "- Confirmed wall selection: `[4, 5, 6, 7]` only.",
        "- Properties used: `BoundaryCondition=NoSlip`, `SlidingWall=1`, `TranslationalVelocityOption=Manual`, `utr=[0,0,-V_ring_test]`.",
        "",
        "## Case Results",
        "",
    ]
    for result in case_results:
        lines += [
            f"### {result['case']['id']} - {result['case']['label']}",
            "",
            f"- Status: `{result['status']}`",
            f"- Model: `{result.get('model')}`",
        ]
        if result["status"] == "PASS":
            lines += [
                f"- Wall: `{json.dumps(result['wall'], ensure_ascii=False)}`",
                f"- Flow: `{json.dumps(result['flow'], ensure_ascii=False)}`",
                f"- Summary: `{json.dumps(result['outputs']['summary'], ensure_ascii=False)}`",
                f"- Center-hole `w(t)` CSV: `{result['outputs']['w_t_csv']}`",
                "- Images:",
            ]
            for img in result["outputs"]["images"]:
                lines.append(f"  - `{img.get('file')}` (`ok={img.get('ok')}`)")
        else:
            lines += [f"- Error: `{result.get('error')}`"]
        lines.append("")
    lines += [
        "## Review",
        "",
        f"- Case B ring-near mean `abs(w + V_ring_test)`: `{review.get('case_b_relative_mean')}` m/s",
        f"- Case C ring-near mean `abs(w + V_ring_test)`: `{review.get('case_c_relative_mean')}` m/s",
        f"- Relative disturbance ratio B/C: `{review.get('relative_ratio_b_over_c')}`",
        "- Limitation: the geometry and outer boundaries are fixed. The ring outline does not translate; only the no-slip wall velocity condition is changed.",
        "- Limitation: this is still a single-phase model with no free liquid surface; it cannot produce a true `Hmax`.",
        "",
        "## Structured Data",
        "",
        "```json",
        json.dumps({"status": status, "named": named, "review": review, "cases": case_results}, ensure_ascii=False, indent=2, default=str),
        "```",
        "",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    make_dirs()
    shutil.copy2(Path(__file__), SCRIPTS / "ring_fountain_stage4_2a.py")
    client = mph.Client(cores=2, version="6.4")
    try:
        named = save_named_model(client)
        cases = [
            {"id": "case_A_stationary_ring", "label": "stationary ring, original upward inflow", "moving_wall": False, "wall_speed": "0", "inlet": [2], "outlet": [3], "u0_expr": "U0", "set_u0": None},
            {"id": "case_B_same_downward", "label": "ring and water both downward at V_ring_test", "moving_wall": True, "wall_speed": "-V_ring_test", "inlet": [3], "outlet": [2], "u0_expr": "V_ring_test", "set_u0": "0.10[m/s]"},
            {"id": "case_C_opposite_relative", "label": "ring downward, water upward at V_ring_test", "moving_wall": True, "wall_speed": "-V_ring_test", "inlet": [2], "outlet": [3], "u0_expr": "V_ring_test", "set_u0": "0.10[m/s]"},
        ]
        results = [solve_case(client, case) for case in cases]
        all_pass = all(r["status"] == "PASS" for r in results)
        b = next((r for r in results if r["case"]["id"].startswith("case_B") and r["status"] == "PASS"), None)
        c = next((r for r in results if r["case"]["id"].startswith("case_C") and r["status"] == "PASS"), None)
        bmean = b["outputs"]["summary"]["ring_near_abs_w_relative_mean_m_per_s"] if b else None
        cmean = c["outputs"]["summary"]["ring_near_abs_w_relative_mean_m_per_s"] if c else None
        ratio = (bmean / cmean) if isinstance(bmean, (int, float)) and isinstance(cmean, (int, float)) and cmean else None
        relative_ok = ratio is not None and ratio < 0.5
        status = "PASS" if all_pass and relative_ok else "FAIL"
        review = {
            "all_cases_pass": all_pass,
            "case_b_relative_mean": bmean,
            "case_c_relative_mean": cmean,
            "relative_ratio_b_over_c": ratio,
            "case_b_disturbance_much_less_than_case_c": relative_ok,
        }
        write_report(named, status, results, review)
        append_docs(named, status, results)
        summary = {"stage": "4.2A", "status": status, "named": named, "review": review, "cases": results, "report": str(CHECK / "reports" / "relative_velocity_check_report.md")}
        (CHECK / "stage4_2a_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        log(f"Stage 4.2A status: {status}")
    finally:
        client.clear()


if __name__ == "__main__":
    main()
