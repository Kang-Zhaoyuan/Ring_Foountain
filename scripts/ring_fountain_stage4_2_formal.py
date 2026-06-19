# -*- coding: utf-8 -*-
"""Formal Stage 4.2 fixed-geometry moving-wall model."""

from __future__ import annotations

import csv
import json
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import mph
import numpy as np

import ring_fountain_stage4_2a as s42a


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
STAGE4 = ROOT / "04_moving_ring_model"
NAMED = STAGE4 / "models" / "ring_fountain_v3_boundary_named.mph"
OUT_MODEL = STAGE4 / "models" / "ring_fountain_v3_moving_ring.mph"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_TS = STAGE4 / "models" / f"ring_fountain_v3_moving_ring_{RUN_ID}.mph"
LOG = STAGE4 / "logs" / f"stage4_2_formal_{RUN_ID}.log"
SCRIPTS = ROOT / "scripts"


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def make_dirs() -> None:
    for sub in ["models", "reports", "images", "tables", "logs"]:
        (STAGE4 / sub).mkdir(parents=True, exist_ok=True)
    (STAGE4 / "images" / "frames").mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


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
            writer.writerow(row)


def safe_eval(model: Any, exprs: list[str], unit: str, inner: Any = "last") -> tuple[str, np.ndarray]:
    last_error = None
    for expr in exprs:
        try:
            arr = s42a.eval_array(model, expr, unit, inner=inner).reshape(-1)
            if np.any(np.isfinite(arr)):
                return expr, arr
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Could not evaluate {exprs}: {last_error}")


def export_final_images(model: Any) -> dict[str, Any]:
    img_dir = STAGE4 / "images"
    r = s42a.eval_array(model, "r", "m", inner="last").reshape(-1)
    z = s42a.eval_array(model, "z", "m", inner="last").reshape(-1)
    _, u = safe_eval(model, ["u", "spf.u"], "m/s")
    _, w = safe_eval(model, ["w", "spf.w"], "m/s")
    _, spfu = safe_eval(model, ["spf.U", "U"], "m/s")
    p_expr, pressure = safe_eval(model, ["p", "spf.p"], "Pa")
    images = {
        "velocity_magnitude": s42a.render_field(img_dir / "moving_ring_velocity_magnitude_spfU.png", "spf.U", r, z, spfu),
        "pressure": s42a.render_field(img_dir / "moving_ring_pressure.png", p_expr, r, z, pressure),
        "axial_velocity_w": s42a.render_field(img_dir / "moving_ring_axial_velocity_w.png", "w", r, z, w),
        "ring_near_velocity_vectors": s42a.render_field(img_dir / "moving_ring_ring_near_velocity_vectors.png", "velocity vectors", r, z, spfu, (u, w)),
    }
    return images


def export_w_t_and_frames(model: Any) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    frame_rows: list[dict[str, Any]] = []
    frame_dir = STAGE4 / "images" / "frames"
    for inner in range(1, 6):
        try:
            r = s42a.eval_array(model, "r", "m", inner=[inner]).reshape(-1)
            z = s42a.eval_array(model, "z", "m", inner=[inner]).reshape(-1)
            w = s42a.eval_array(model, "w", "m/s", inner=[inner]).reshape(-1)
            u = s42a.eval_array(model, "u", "m/s", inner=[inner]).reshape(-1)
            spfu = s42a.eval_array(model, "spf.U", "m/s", inner=[inner]).reshape(-1)
            t = s42a.finite_flat(model.evaluate("t", unit="s", inner=[inner]))
            mask = s42a.center_mask(model, r, z)
            vals = w[mask & np.isfinite(w)]
            time_s = float(t[0]) if t.size else None
            rows.append({
                "inner_solution": inner,
                "time_s": time_s,
                "w_center_above_mean_m_per_s": float(np.nanmean(vals)) if vals.size else None,
                "w_center_above_max_m_per_s": float(np.nanmax(vals)) if vals.size else None,
                "sample_count": int(vals.size),
            })
            frame = frame_dir / f"moving_ring_velocity_frame_{inner:03d}.png"
            img = s42a.render_field(frame, f"spf.U t={time_s}", r, z, spfu, (u, w))
            frame_rows.append({"inner_solution": inner, "time_s": time_s, "file": str(frame), "ok": img.get("ok")})
        except Exception as exc:
            frame_rows.append({"inner_solution": inner, "error": str(exc)})
            break
    csv_path = STAGE4 / "tables" / "moving_ring_center_hole_w_t.csv"
    frame_csv = STAGE4 / "tables" / "moving_ring_frame_index.csv"
    write_csv(csv_path, rows)
    write_csv(frame_csv, frame_rows)
    return {"w_t_csv": str(csv_path), "frame_index_csv": str(frame_csv), "frames": frame_rows}


def append_docs(status: str, outputs: dict[str, Any]) -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8", errors="ignore") if readme.exists() else "# COMSOL Ring Fountain Simulation\n"
    text += f"""

## Stage 4 Moving Ring Model

- Stage 4 status: `{status}`.
- Formal moving-wall model: `{OUT_MODEL}`.
- Moving wall acts on the confirmed ring boundaries `[4, 5, 6, 7]`, verified equal to `sel_ring_wall_confirmed`.
- COMSOL wall feature/property path: `spf.wallbc1`, `BoundaryCondition=NoSlip`, `SlidingWall=1`, `TranslationalVelocityOption=Manual`, `utr=[0,0,-V_ring]`.
- Direction: negative `z`; `u_r=0`, `u_z=-V_ring`.
- This is fixed geometry plus moving wall velocity. The ring outline does not translate in the video/frames.
- Current limits: single-phase; no free surface; ring speed is externally prescribed; no ring density, gravity, buoyancy, or fluid-structure coupling; no true `Hmax`.
"""
    readme.write_text(text, encoding="utf-8")
    changelog = ROOT / "CHANGELOG.md"
    ch = changelog.read_text(encoding="utf-8", errors="ignore") if changelog.exists() else "# Changelog\n"
    ch += f"""

## {datetime.now().isoformat(timespec='seconds')} - Formal Stage 4 moving-wall model

- Stage 4.2 status: `{status}`.
- Model: `{OUT_MODEL}`.
- Timestamp model: `{OUT_TS}`.
- Center-hole `w(t)`: `{outputs.get('times', {}).get('w_t_csv')}`.
- Frame index: `{outputs.get('times', {}).get('frame_index_csv')}`.
"""
    changelog.write_text(ch, encoding="utf-8")


def write_report(status: str, outputs: dict[str, Any], wall_info: dict[str, Any], flow_info: dict[str, Any], cleanup: dict[str, Any]) -> None:
    report = STAGE4 / "reports" / "moving_ring_model_report.md"
    lines = [
        "# Stage 4 Moving Ring Model Report",
        "",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"Stage 4.2 review status: `{status}`",
        "",
        "## Boundary And Wall Setting",
        "",
        "- Manually confirmed ring boundaries: `[4, 5, 6, 7]`.",
        "- Final named selection: `sel_ring_wall_confirmed`.",
        f"- Wall feature / property name: `{wall_info}`",
        f"- Flow inlet/outlet setting: `{flow_info}`",
        "- Moving direction: negative `z`.",
        "- `V_ring = 0.10[m/s]`.",
        "- `t_end_move = 0.02[s]`.",
        "- `u_r = 0`, `u_z = -V_ring` via `utr=[0,0,-V_ring]`.",
        "",
        "## Fixed-Geometry Limitation",
        "",
        "- Moving Wall changes the wall velocity boundary condition, not the ring geometry position.",
        "- If the frame sequence shows the ring outline staying fixed, that is expected.",
        "- Current model is still single-phase, has no free liquid surface, and cannot output true `Hmax`.",
        "",
        "## Outputs",
        "",
        f"- Model: `{OUT_MODEL}`",
        f"- Timestamp model: `{OUT_TS}`",
        f"- Center-hole `w(t)`: `{outputs.get('times', {}).get('w_t_csv')}`",
        f"- Frame index: `{outputs.get('times', {}).get('frame_index_csv')}`",
        "- Images:",
    ]
    for key, item in outputs.get("images", {}).items():
        lines.append(f"  - {key}: `{item.get('file')}` (`ok={item.get('ok')}`)")
    lines += [
        "- Frames:",
    ]
    for item in outputs.get("times", {}).get("frames", []):
        if item.get("file"):
            lines.append(f"  - `{item.get('file')}` (`ok={item.get('ok')}`)")
    lines += [
        "",
        "## Solve Review",
        "",
        f"- Solve success: `{status == 'PASS'}`",
        f"- Stage 3 scale-parameter cleanup before solve: `{cleanup}`",
        f"- Current model can be used as Stage 5 input: `{status == 'PASS'}` for single-phase fixed-geometry moving-wall context only.",
        "",
        "## Structured Data",
        "",
        "```json",
        json.dumps({"status": status, "wall": wall_info, "flow": flow_info, "cleanup": cleanup, "outputs": outputs}, ensure_ascii=False, indent=2, default=str),
        "```",
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    make_dirs()
    shutil.copy2(Path(__file__), SCRIPTS / "ring_fountain_stage4_2_formal.py")
    client = mph.Client(cores=2, version="6.4")
    status = "FAIL"
    outputs: dict[str, Any] = {}
    wall_info: dict[str, Any] = {}
    flow_info: dict[str, Any] = {}
    cleanup: dict[str, Any] = {}
    try:
        model = client.load(NAMED)
        try:
            model.parameter("V_ring", "0.10[m/s]")
            model.parameter("t_end_move", "0.02[s]")
            cleanup = s42a.remove_stage3_scale_params_for_solve(model)
            s42a.set_time_list(model, "t_end_move")
            wall_info = s42a.configure_wall(model, True, "-V_ring")
            flow_info = s42a.configure_inlet_outlet(model, [2], [3], "U0")
            log("Solving formal Stage 4.2 moving-wall model.")
            model.solve()
            model.save(OUT_MODEL)
            model.save(OUT_TS)
            outputs["images"] = export_final_images(model)
            outputs["times"] = export_w_t_and_frames(model)
            status = "PASS" if all(v.get("ok") for v in outputs["images"].values()) and outputs["times"]["frames"] else "PARTIAL_PASS"
        finally:
            try:
                client.remove(model)
            except Exception:
                pass
    except Exception as exc:
        (STAGE4 / "logs" / f"stage4_2_formal_error_{RUN_ID}.log").write_text(traceback.format_exc(), encoding="utf-8")
        outputs["error"] = str(exc)
        status = "FAIL"
    finally:
        write_report(status, outputs, wall_info, flow_info, cleanup)
        append_docs(status, outputs)
        (STAGE4 / "stage4_2_formal_summary.json").write_text(json.dumps({"status": status, "model": str(OUT_MODEL), "timestamp_model": str(OUT_TS), "outputs": outputs, "wall": wall_info, "flow": flow_info, "cleanup": cleanup}, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        log(f"Formal Stage 4.2 status: {status}")
        client.clear()


if __name__ == "__main__":
    main()
