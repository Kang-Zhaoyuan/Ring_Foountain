# -*- coding: utf-8 -*-
"""Stage 5A static free-surface smoke test.

Attempts a minimal COMSOL Level Set + Laminar Flow model.  This is deliberately
kept separate from the Stage 4 moving-ring model and does not extract Hmax.
"""

from __future__ import annotations

import csv
import json
import shutil
import struct
import traceback
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any

import mph
import numpy as np

import ring_fountain_stage4_2a as s42a


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
STAGE5 = ROOT / "05_two_phase_free_surface"
MODEL_OUT = STAGE5 / "models" / "ring_fountain_v4_5A_static_interface.mph"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
MODEL_TS = STAGE5 / "models" / f"ring_fountain_v4_5A_static_interface_{RUN_ID}.mph"
LOG = STAGE5 / "logs" / f"stage5a_static_interface_{RUN_ID}.log"
SCRIPTS = ROOT / "scripts"


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def make_dirs() -> None:
    for sub in ["models", "reports", "images", "tables", "logs"]:
        (STAGE5 / sub).mkdir(parents=True, exist_ok=True)
    (STAGE5 / "images" / "frames").mkdir(parents=True, exist_ok=True)
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


def put(pixels: bytearray, width: int, height: int, x: int, y: int, color: tuple[int, int, int]) -> None:
    if 0 <= x < width and 0 <= y < height:
        i = (y * width + x) * 3
        pixels[i:i + 3] = bytes(color)


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


def render_phase(path: Path, r: np.ndarray, z: np.ndarray, phi: np.ndarray, interface: float = 0.5) -> dict[str, Any]:
    width, height = 900, 760
    pixels = bytearray([248, 248, 246] * width * height)
    finite = np.isfinite(r) & np.isfinite(z) & np.isfinite(phi)
    if not np.any(finite):
        png_write(path, width, height, pixels)
        return {"ok": False, "file": str(path), "error": "no finite samples"}
    rr, zz, pp = r[finite], z[finite], phi[finite]
    rlo, rhi = 0.0, 0.1
    zlo, zhi = -0.12, 0.12
    margin = 55
    def tx(x: float) -> int:
        return int(margin + (x - rlo) / (rhi - rlo) * (width - 2 * margin))
    def ty(y: float) -> int:
        return int(height - margin - (y - zlo) / (zhi - zlo) * (height - 2 * margin))
    step = max(1, len(rr) // 25000)
    for x, y, val in zip(rr[::step], zz[::step], pp[::step]):
        t = max(0.0, min(1.0, float(val)))
        col = (int(220 - 130 * t), int(230 - 80 * t), int(245 - 10 * t))
        px, py = tx(float(x)), ty(float(y))
        for ox in range(-2, 3):
            for oy in range(-2, 3):
                put(pixels, width, height, px + ox, py + oy, col)
    # z=0 reference line.
    y0 = ty(0.0)
    for x in range(margin, width - margin):
        put(pixels, width, height, x, y0, (30, 30, 30))
    png_write(path, width, height, pixels)
    return {
        "ok": True,
        "file": str(path),
        "phi_min": float(np.nanmin(pp)),
        "phi_max": float(np.nanmax(pp)),
        "interface_reference": interface,
        "method": "Python rendering of COMSOL Level Set field samples; black line is z=0 reference",
    }


def try_set(feature: Any, key: str, value: Any) -> dict[str, Any]:
    try:
        feature.set(key, value)
        return {"key": key, "value": value, "status": "ok"}
    except Exception as exc:
        return {"key": key, "value": value, "status": "failed", "error": str(exc)}


def build_model(client: Any) -> tuple[Any, dict[str, Any]]:
    model = client.create("ring_fountain_5A_static_interface")
    java = model.java
    param = java.param()
    for name, value in {
        "Rtank": "100[mm]",
        "Hwater": "120[mm]",
        "Hair": "120[mm]",
        "rho_w": "1000[kg/m^3]",
        "mu_w": "1e-3[Pa*s]",
        "rho_air": "1.225[kg/m^3]",
        "mu_air": "1.8e-5[Pa*s]",
        "sigma_wa": "0.072[N/m]",
        "g_const_user": "9.81[m/s^2]",
        "t_end_5A": "0.02[s]",
        "eps_ls": "2[mm]",
    }.items():
        param.set(name, value)
    comp = java.component().create("comp1", True)
    geom = comp.geom().create("geom1", 2)
    axisym_status = "not_set"
    try:
        geom.axisymmetric(True)
        axisym_status = "geom.axisymmetric(True)"
    except Exception as exc:
        axisym_status = f"axisymmetric call failed: {exc}"
    rect = geom.feature().create("r1", "Rectangle")
    rect.set("size", ["Rtank", "Hwater+Hair"])
    rect.set("pos", ["0", "-Hwater"])
    geom.run()
    mesh = comp.mesh().create("mesh1")
    mesh.autoMeshSize(4)
    mesh.run()
    spf = comp.physics().create("spf", "LaminarFlow", "geom1")
    ls = comp.physics().create("ls", "LevelSet", "geom1")
    setup: dict[str, Any] = {"axisym_status": axisym_status, "level_set_attempts": [], "spf_attempts": []}
    fp = spf.feature("fp1")
    setup["spf_attempts"].append(try_set(fp, "rho_mat", "userdef"))
    setup["spf_attempts"].append(try_set(fp, "rho", "rho_air+(rho_w-rho_air)*phils"))
    setup["spf_attempts"].append(try_set(fp, "mu_mat", "userdef"))
    setup["spf_attempts"].append(try_set(fp, "mu", "mu_air+(mu_w-mu_air)*phils"))
    # Keep the velocity field quiescent where possible.
    try:
        spf.feature("init1").set("u", ["0", "0", "0"])
    except Exception as exc:
        setup["spf_attempts"].append({"init_velocity": "failed", "error": str(exc)})
    # Level Set initial interface. Property names differ by version; try the common ones and record all outcomes.
    init = ls.feature("init1")
    for key in ["phi", "Phi", "phils", "ls", "u"]:
        setup["level_set_attempts"].append(try_set(init, key, "flc2hs(-z,eps_ls)"))
    for key in ["epsilon", "eps", "interfaceThickness", "lsinit"]:
        setup["level_set_attempts"].append(try_set(ls, key, "eps_ls"))
    # Use all domains for both interfaces.
    try:
        spf.selection().all()
        ls.selection().all()
    except Exception:
        pass
    study = java.study().create("std1")
    study.create("time", "Transient")
    study.feature("time").set("tlist", "range(0,t_end_5A/4,t_end_5A)")
    return model, setup


def evaluate_outputs(model: Any) -> dict[str, Any]:
    outputs: dict[str, Any] = {}
    candidates = ["ls.phils", "phils", "ls.phi", "phi", "Phi", "ls.Phi"]
    chosen = None
    last_error = None
    for expr in candidates:
        try:
            arr = s42a.eval_array(model, expr, "", inner="last").reshape(-1)
            if np.any(np.isfinite(arr)):
                chosen = expr
                break
        except Exception as exc:
            last_error = exc
    if chosen is None:
        raise RuntimeError(f"Could not evaluate Level Set interface variable candidates {candidates}: {last_error}")
    r = s42a.eval_array(model, "r", "m", inner="last").reshape(-1)
    z = s42a.eval_array(model, "z", "m", inner="last").reshape(-1)
    phi = s42a.eval_array(model, chosen, "", inner="last").reshape(-1)
    outputs["chosen_interface_variable"] = chosen
    outputs["final_image"] = render_phase(STAGE5 / "images" / "5A_static_interface_final.png", r, z, phi)
    rows = []
    frames = []
    for inner in range(1, 6):
        try:
            ri = s42a.eval_array(model, "r", "m", inner=[inner]).reshape(-1)
            zi = s42a.eval_array(model, "z", "m", inner=[inner]).reshape(-1)
            phii = s42a.eval_array(model, chosen, "", inner=[inner]).reshape(-1)
            ti = s42a.finite_flat(model.evaluate("t", unit="s", inner=[inner]))
            water_below = phii[(zi < -0.01) & np.isfinite(phii)]
            air_above = phii[(zi > 0.01) & np.isfinite(phii)]
            rows.append({
                "inner_solution": inner,
                "time_s": float(ti[0]) if ti.size else None,
                "phi_mean_below_z_minus_1cm": float(np.nanmean(water_below)) if water_below.size else None,
                "phi_mean_above_z_plus_1cm": float(np.nanmean(air_above)) if air_above.size else None,
                "phi_min": float(np.nanmin(phii)),
                "phi_max": float(np.nanmax(phii)),
            })
            frame = STAGE5 / "images" / "frames" / f"5A_static_interface_frame_{inner:03d}.png"
            img = render_phase(frame, ri, zi, phii)
            frames.append({"inner_solution": inner, "time_s": float(ti[0]) if ti.size else None, "file": str(frame), "ok": img.get("ok")})
        except Exception as exc:
            frames.append({"inner_solution": inner, "error": str(exc)})
            break
    write_csv(STAGE5 / "tables" / "5A_static_interface_metrics.csv", rows)
    write_csv(STAGE5 / "tables" / "5A_static_interface_frame_index.csv", frames)
    outputs["metrics_csv"] = str(STAGE5 / "tables" / "5A_static_interface_metrics.csv")
    outputs["frame_index_csv"] = str(STAGE5 / "tables" / "5A_static_interface_frame_index.csv")
    outputs["frames"] = frames
    outputs["metrics"] = rows
    if rows:
        stable = max(abs((row.get("phi_mean_below_z_minus_1cm") or 0) - rows[0].get("phi_mean_below_z_minus_1cm", 0)) for row in rows) < 0.05
        stable = stable and max(abs((row.get("phi_mean_above_z_plus_1cm") or 0) - rows[0].get("phi_mean_above_z_plus_1cm", 0)) for row in rows) < 0.05
    else:
        stable = False
    outputs["interface_stability_smoke_pass"] = stable
    return outputs


def update_docs(status: str, outputs: dict[str, Any]) -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8", errors="ignore") if readme.exists() else "# COMSOL Ring Fountain Simulation\n"
    text += f"""

## Stage 5A Static Free-Surface Smoke Test

- Stage 5A status: `{status}`.
- Model: `{MODEL_OUT}`.
- This smoke test only checks whether a static air-water interface can be initialized and remain approximately stable for a short time.
- No ring motion is included in 5A.
- No `Hmax` is extracted.
"""
    readme.write_text(text, encoding="utf-8")
    changelog = ROOT / "CHANGELOG.md"
    ch = changelog.read_text(encoding="utf-8", errors="ignore") if changelog.exists() else "# Changelog\n"
    ch += f"""

## {datetime.now().isoformat(timespec='seconds')} - Stage 5A static interface smoke test

- Stage 5A status: `{status}`.
- Model: `{MODEL_OUT}`.
- Report: `{STAGE5 / 'reports' / '5A_static_interface_report.md'}`.
"""
    changelog.write_text(ch, encoding="utf-8")


def write_report(status: str, setup: dict[str, Any], outputs: dict[str, Any]) -> None:
    lines = [
        "# Stage 5A Static Interface Report",
        "",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"5A review status: `{status}`",
        "",
        "## Scope",
        "",
        "- Static free-surface smoke test only.",
        "- No moving ring.",
        "- No `Hmax` extraction.",
        "",
        "## Interface Attempt",
        "",
        "- Preferred combined physics type names were probed separately; standalone `LevelSet` and `LaminarFlow` were available.",
        "- This script attempted a minimal `LaminarFlow + LevelSet` model on a fixed 2D/axisymmetric rectangle.",
        f"- Setup details: `{json.dumps(setup, ensure_ascii=False)}`",
        "",
        "## Outputs",
        "",
        f"- Model: `{MODEL_OUT}`",
        f"- Timestamp model: `{MODEL_TS}`",
        f"- Interface variable: `{outputs.get('chosen_interface_variable')}`",
        f"- Final image: `{outputs.get('final_image', {}).get('file')}`",
        f"- Metrics CSV: `{outputs.get('metrics_csv')}`",
        f"- Frame index CSV: `{outputs.get('frame_index_csv')}`",
        "",
        "## Review",
        "",
        f"- Interface stability smoke pass: `{outputs.get('interface_stability_smoke_pass')}`",
        "- This is only a smoke test of static interface initialization, not a ring-fountain free-surface simulation.",
        "",
        "## Structured Data",
        "",
        "```json",
        json.dumps({"status": status, "setup": setup, "outputs": outputs}, ensure_ascii=False, indent=2, default=str),
        "```",
        "",
    ]
    (STAGE5 / "reports" / "5A_static_interface_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    make_dirs()
    shutil.copy2(Path(__file__), SCRIPTS / "ring_fountain_stage5a_static_interface.py")
    client = mph.Client(cores=2, version="6.4")
    status = "FAIL"
    setup: dict[str, Any] = {}
    outputs: dict[str, Any] = {}
    model = None
    try:
        model, setup = build_model(client)
        log("Solving Stage 5A static interface smoke model.")
        model.solve()
        model.save(MODEL_OUT)
        model.save(MODEL_TS)
        outputs = evaluate_outputs(model)
        status = "PASS" if outputs.get("interface_stability_smoke_pass") else "FAIL"
    except Exception as exc:
        outputs["error"] = str(exc)
        (STAGE5 / "logs" / f"stage5a_static_interface_error_{RUN_ID}.log").write_text(traceback.format_exc(), encoding="utf-8")
        try:
            if model is not None:
                model.save(MODEL_OUT)
                model.save(MODEL_TS)
        except Exception:
            pass
        status = "FAIL"
    finally:
        try:
            if model is not None:
                client.remove(model)
        except Exception:
            pass
        write_report(status, setup, outputs)
        update_docs(status, outputs)
        (STAGE5 / "stage5a_summary.json").write_text(json.dumps({"status": status, "model": str(MODEL_OUT), "timestamp_model": str(MODEL_TS), "setup": setup, "outputs": outputs, "report": str(STAGE5 / "reports" / "5A_static_interface_report.md")}, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        log(f"Stage 5A status: {status}")
        client.clear()


if __name__ == "__main__":
    main()
