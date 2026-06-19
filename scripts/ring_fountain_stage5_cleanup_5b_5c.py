# -*- coding: utf-8 -*-
"""Stage 5 cleanup, reduced free-surface forcing, and Hmax extraction.

This script intentionally treats Stage 5B as a reduced model chain.  It starts
from the already-passed Stage 5A smoke-test model and only advances through the
requested review gates when the previous stage passes.
"""

from __future__ import annotations

import csv
import json
import math
import os
import shutil
import struct
import traceback
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any

import jpype
import mph
import numpy as np

import ring_fountain_stage4_1_boundary_review as s41
import ring_fountain_stage4_2a as s42a


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
STAGE5 = ROOT / "05_two_phase_free_surface"
SCRIPTS = ROOT / "scripts"
MODEL_5A = STAGE5 / "models" / "ring_fountain_v4_5A_static_interface.mph"
MODEL_B1 = STAGE5 / "models" / "ring_fountain_v4_5B1_center_forcing.mph"
MODEL_B2 = STAGE5 / "models" / "ring_fountain_v4_5B2_fixed_ring_moving_wall_free_surface.mph"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = STAGE5 / "logs" / f"stage5_cleanup_5b_5c_{RUN_ID}.log"


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def make_dirs() -> None:
    for sub in ["models", "reports", "images", "tables", "logs"]:
        (STAGE5 / sub).mkdir(parents=True, exist_ok=True)
    for sub in ["5A_review", "5B1_center_forcing", "5B1_center_forcing/frames", "5B2_fixed_ring", "5B2_fixed_ring/frames", "5C_Hmax", "5C_Hmax/frames"]:
        (STAGE5 / "images" / sub).mkdir(parents=True, exist_ok=True)
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


def png_write(path: Path, width: int, height: int, pixels: bytearray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw.extend(pixels[y * stride:(y + 1) * stride])

    def chunk(name: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        + chunk(b"IEND", b"")
    )


def put(pixels: bytearray, width: int, height: int, x: int, y: int, color: tuple[int, int, int]) -> None:
    if 0 <= x < width and 0 <= y < height:
        i = (y * width + x) * 3
        pixels[i:i + 3] = bytes(color)


def line(pixels: bytearray, width: int, height: int, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        put(pixels, width, height, x, y, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def circle(pixels: bytearray, width: int, height: int, cx: int, cy: int, radius: int, color: tuple[int, int, int]) -> None:
    rr = radius * radius
    for yy in range(cy - radius, cy + radius + 1):
        for xx in range(cx - radius, cx + radius + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= rr:
                put(pixels, width, height, xx, yy, color)


def cmap_blue_red(t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, float(t)))
    # phils=0 is air and is shown light blue; phils=1 is water and is deep blue.
    return (int(210 - 175 * t), int(235 - 170 * t), int(250 - 55 * t))


def cmap_viridis_like(t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, float(t)))
    stops = [(35, 45, 120), (40, 125, 180), (50, 170, 120), (230, 210, 70)]
    p = t * (len(stops) - 1)
    i = min(len(stops) - 2, int(p))
    a = p - i
    return tuple(int(stops[i][j] * (1 - a) + stops[i + 1][j] * a) for j in range(3))


def cmap_gray(t: float) -> tuple[int, int, int]:
    v = int(245 - 210 * max(0.0, min(1.0, float(t))))
    return (v, v, v)


def axis_map(width: int, height: int, rlim: tuple[float, float], zlim: tuple[float, float]) -> tuple[Any, Any, int]:
    margin = 58
    def tx(x: float) -> int:
        return int(margin + (x - rlim[0]) / (rlim[1] - rlim[0]) * (width - 2 * margin - 52))
    def ty(y: float) -> int:
        return int(height - margin - (y - zlim[0]) / (zlim[1] - zlim[0]) * (height - 2 * margin))
    return tx, ty, margin


def finite_mask(*arrays: np.ndarray) -> np.ndarray:
    mask = np.ones_like(np.asarray(arrays[0]).reshape(-1), dtype=bool)
    for arr in arrays:
        mask &= np.isfinite(np.asarray(arr).reshape(-1))
    return mask


def estimate_interface(r: np.ndarray, z: np.ndarray, phi: np.ndarray, threshold: float = 0.5, bins: int = 180) -> list[tuple[float, float]]:
    mask = finite_mask(r, z, phi)
    rr, zz, pp = r[mask].reshape(-1), z[mask].reshape(-1), phi[mask].reshape(-1)
    if rr.size < 10:
        return []
    near = (np.abs(pp - threshold) <= 0.08) & (np.abs(zz) <= 0.06)
    rr, zz, pp = rr[near], zz[near], pp[near]
    if rr.size < 3:
        return []
    rmin, rmax = float(np.nanmin(rr)), float(np.nanmax(rr))
    edges = np.linspace(rmin, rmax, bins + 1)
    pts: list[tuple[float, float]] = []
    for i in range(bins):
        sel = (rr >= edges[i]) & (rr < edges[i + 1])
        if np.count_nonzero(sel) < 1:
            continue
        rs, zs, ps = rr[sel], zz[sel], pp[sel]
        weight = 1.0 / np.maximum(np.abs(ps - threshold), 1e-4)
        zi = float(np.sum(zs * weight) / np.sum(weight))
        pts.append((float(np.nanmean(rs)), zi))
    return pts


def render_field(
    path: Path,
    r: np.ndarray,
    z: np.ndarray,
    values: np.ndarray,
    *,
    rlim: tuple[float, float] = (0.0, 0.1),
    zlim: tuple[float, float] = (-0.12, 0.12),
    vlim: tuple[float, float] | None = None,
    cmap: str = "phase",
    phi: np.ndarray | None = None,
    draw_interface: bool = False,
    draw_z0: bool = True,
    scatter_only: bool = False,
) -> dict[str, Any]:
    width, height = 980, 780
    pixels = bytearray([248, 248, 246] * width * height)
    mask = finite_mask(r, z, values)
    rr, zz, vv = r[mask].reshape(-1), z[mask].reshape(-1), values[mask].reshape(-1)
    if vv.size == 0:
        png_write(path, width, height, pixels)
        return {"ok": False, "file": str(path), "error": "no finite samples"}
    if vlim is None:
        lo, hi = float(np.nanpercentile(vv, 2)), float(np.nanpercentile(vv, 98))
        if abs(hi - lo) < 1e-12:
            lo, hi = float(np.nanmin(vv)), float(np.nanmax(vv) + 1e-12)
    else:
        lo, hi = vlim
    tx, ty, margin = axis_map(width, height, rlim, zlim)
    step = max(1, len(rr) // (22000 if scatter_only else 45000))
    radius = 1 if scatter_only else 2
    cmap_fn = cmap_blue_red if cmap == "phase" else cmap_gray if cmap == "gray" else cmap_viridis_like
    for x, y, val in zip(rr[::step], zz[::step], vv[::step]):
        if not (rlim[0] <= x <= rlim[1] and zlim[0] <= y <= zlim[1]):
            continue
        t = (float(val) - lo) / (hi - lo) if hi > lo else 0.5
        circle(pixels, width, height, tx(float(x)), ty(float(y)), radius, cmap_fn(t))
    # axes and z=0 reference.
    line(pixels, width, height, tx(rlim[0]), ty(zlim[0]), tx(rlim[1]), ty(zlim[0]), (60, 60, 60))
    line(pixels, width, height, tx(rlim[0]), ty(zlim[0]), tx(rlim[0]), ty(zlim[1]), (60, 60, 60))
    if draw_z0 and zlim[0] <= 0 <= zlim[1]:
        y0 = ty(0.0)
        for xpix in range(tx(rlim[0]), tx(rlim[1])):
            put(pixels, width, height, xpix, y0, (20, 20, 20))
    if draw_interface and phi is not None:
        pts = estimate_interface(r, z, phi)
        for (a, b), (c, d) in zip(pts[:-1], pts[1:]):
            if rlim[0] <= a <= rlim[1] and rlim[0] <= c <= rlim[1]:
                line(pixels, width, height, tx(a), ty(b), tx(c), ty(d), (0, 0, 0))
    # colorbar.
    bx0, bx1 = width - 42, width - 24
    by0, by1 = margin, height - margin
    for yy in range(by0, by1):
        t = 1.0 - (yy - by0) / max(1, (by1 - by0 - 1))
        col = cmap_fn(t)
        for xx in range(bx0, bx1):
            put(pixels, width, height, xx, yy, col)
    for yy in [by0, (by0 + by1) // 2, by1 - 1]:
        line(pixels, width, height, bx0 - 5, yy, bx1 + 5, yy, (20, 20, 20))
    png_write(path, width, height, pixels)
    return {"ok": True, "file": str(path), "vmin_render": lo, "vmax_render": hi, "samples": int(vv.size), "colorbar": "right-side gradient bar"}


def render_vector(path: Path, r: np.ndarray, z: np.ndarray, ur: np.ndarray, wz: np.ndarray, phi: np.ndarray | None = None) -> dict[str, Any]:
    width, height = 980, 780
    pixels = bytearray([248, 248, 246] * width * height)
    rlim, zlim = (0.0, 0.05), (-0.06, 0.04)
    tx, ty, _ = axis_map(width, height, rlim, zlim)
    mask = finite_mask(r, z, ur, wz)
    rr, zz, uu, ww = r[mask].reshape(-1), z[mask].reshape(-1), ur[mask].reshape(-1), wz[mask].reshape(-1)
    mag = np.sqrt(uu * uu + ww * ww)
    vmax = float(np.nanpercentile(mag, 98)) if mag.size else 1.0
    if vmax <= 0:
        vmax = 1.0
    step = max(1, len(rr) // 900)
    for x, y, u, w, m in zip(rr[::step], zz[::step], uu[::step], ww[::step], mag[::step]):
        if not (rlim[0] <= x <= rlim[1] and zlim[0] <= y <= zlim[1]):
            continue
        x0, y0 = tx(float(x)), ty(float(y))
        scale = 0.012 / vmax
        x1, y1 = tx(float(x + u * scale)), ty(float(y + w * scale))
        col = cmap_viridis_like(float(m / vmax))
        line(pixels, width, height, x0, y0, x1, y1, col)
        circle(pixels, width, height, x1, y1, 2, col)
    if phi is not None:
        pts = estimate_interface(r, z, phi)
        for (a, b), (c, d) in zip(pts[:-1], pts[1:]):
            line(pixels, width, height, tx(a), ty(b), tx(c), ty(d), (0, 0, 0))
    if zlim[0] <= 0 <= zlim[1]:
        y0 = ty(0.0)
        for xpix in range(tx(rlim[0]), tx(rlim[1])):
            put(pixels, width, height, xpix, y0, (20, 20, 20))
    png_write(path, width, height, pixels)
    return {"ok": True, "file": str(path), "vmax_reference": vmax}


def read_times(model: Any, count_limit: int = 999) -> list[float]:
    times: list[float] = []
    for inner in range(1, count_limit + 1):
        try:
            t = s42a.finite_flat(model.evaluate("t", unit="s", inner=[inner]))
            if t.size == 0:
                break
            times.append(float(t[0]))
        except Exception:
            break
    return times


def eval_field_set(model: Any, inner: int) -> dict[str, np.ndarray]:
    data: dict[str, np.ndarray] = {}
    for expr, key, unit in [
        ("r", "r", "m"),
        ("z", "z", "m"),
        ("phils", "phi", ""),
        ("rho_air+(rho_w-rho_air)*phils", "rho", "kg/m^3"),
        ("mu_air+(mu_w-mu_air)*phils", "mu", "Pa*s"),
        ("u", "u", "m/s"),
        ("w", "w", "m/s"),
        ("spf.U", "U", "m/s"),
        ("p", "p", "Pa"),
    ]:
        try:
            data[key] = s42a.eval_array(model, expr, unit, inner=[inner]).reshape(-1)
        except Exception:
            data[key] = np.full_like(data.get("r", np.array([math.nan])), math.nan, dtype=float)
    return data


def cleanup_docs() -> dict[str, Any]:
    readme = ROOT / "README.md"
    changelog = ROOT / "CHANGELOG.md"
    readme_text = """# COMSOL Ring Fountain Simulation

Project goal: build staged COMSOL numerical models for the IYPT 2026 Ring Fountain problem.

## Current Trusted Stage Status

- Stage 0 audit: completed.
- Stage 1 checked copy: completed.
- Stage 2 parameter sweep and calibrated continuation: completed.
- Stage 3 relative-flow model: `PASS`.
- Stage 4 fixed-geometry moving-wall ring model: `PASS`.
- Stage 5A static air-water interface smoke test: `PASS`.
- Stage 5B/5C: in progress after the 5A cleanup gate.

## Key Models

- V0 GUI baseline: `D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\ring_fountain_v0_single_phase\\ring_fountain_v0_single_phase.mph`.
- Stage 3 relative-flow model: `D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\03_relative_flow_model\\models\\ring_fountain_v2_relative_flow.mph`.
- Stage 4 moving-wall model: `D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\models\\ring_fountain_v3_moving_ring.mph`.
- Stage 5A static interface model: `D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\models\\ring_fountain_v4_5A_static_interface.mph`.

## Stage 4 Boundary Confirmation

- Manual review result: `PASS`.
- Confirmed ring-wall boundaries: `[4, 5, 6, 7]`.
- Named selections written into the Stage 4 model:
  - `sel_ring_wall_inner = [4]`
  - `sel_ring_wall_outer = [7]`
  - `sel_ring_wall_top = [6]`
  - `sel_ring_wall_bottom = [5]`
  - `sel_ring_wall_confirmed = [4, 5, 6, 7]`
- Moving-wall feature/property path: `spf.wallbc1`, `BoundaryCondition=NoSlip`, `SlidingWall=1`, `TranslationalVelocityOption=Manual`, `utr=[0,0,-V_ring]`.
- Stage 4 is a fixed-geometry moving-wall velocity model. The ring outline does not physically translate.

## Stage 5A Static Interface Smoke Test

- Stage 5A status: `PASS`.
- Purpose: verify that an air-water `phils` interface can be initialized with water below `z=0` and air above `z=0`, then remain approximately stable for a short time.
- 5A is not a ring-fountain model.
- 5A does not include ring motion.
- 5A does not extract `Hmax`.
- The available COMSOL API exposed standalone `LaminarFlow` and `LevelSet`; the combined `Laminar Two-Phase Flow, Level Set` multiphysics type was not available through the tested type names. Therefore 5A uses a minimal manual coupling: `LaminarFlow + LevelSet` with `rho=rho_air+(rho_w-rho_air)*phils` and `mu=mu_air+(mu_w-mu_air)*phils`.

## Known Limitations

- Stage 4 is single-phase and cannot output a true free-surface fountain height.
- Stage 5A is only a static free-surface smoke test.
- Stage 5B reduced models must be labelled approximate/reduced unless a fully coupled validated ring-fall model is later built.
- Current ring velocity is an imposed parameter, not the result of density, gravity, buoyancy, or fluid-structure interaction.
- No official `Hmax` should be reported unless Stage 5C quality checks pass.
"""
    readme.write_text(readme_text, encoding="utf-8")
    changelog_text = """# Changelog

This file keeps the useful stage history while removing repeated intermediate retry blocks from the working README.

## 2026-06-17 - Stages 0-3

- V0 audit, checked copy, parameter sweep, calibrated sweep continuation, and Stage 3 relative-flow model were generated.
- Stage 3 relative-flow model reached `PASS`.
- Earlier preliminary `02_param_sweep` outputs are retained as automation tests, not final physical interpretation.

## 2026-06-17 - Stage 4

- Manual ring-boundary review: `PASS`.
- Confirmed ring boundaries: `[4, 5, 6, 7]`.
- Named selections were written into `ring_fountain_v3_boundary_named.mph`.
- Stage 4.2A relative-velocity check: `PASS`.
- Formal fixed-geometry moving-wall ring model: `PASS`.
- Formal Stage 4 model: `D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\04_moving_ring_model\\models\\ring_fountain_v3_moving_ring.mph`.

## 2026-06-17 - Stage 5A

- Static air-water interface smoke test: `PASS`.
- 5A model: `D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\models\\ring_fountain_v4_5A_static_interface.mph`.
- 5A uses minimal manual `LaminarFlow + LevelSet` coupling because the combined Laminar Two-Phase Flow Level Set physics type was not available through the tested API names.
- 5A is not a fountain model and does not extract `Hmax`.
"""
    changelog.write_text(changelog_text, encoding="utf-8")
    return {"README.md": str(readme), "CHANGELOG.md": str(changelog)}


def stage5a_cleanup(client: Any) -> dict[str, Any]:
    log("Stage 5A cleanup started.")
    docs = cleanup_docs()
    model = client.load(MODEL_5A)
    outputs: dict[str, Any] = {"docs": docs, "images": [], "tables": []}
    try:
        times = read_times(model)
        if not times:
            raise RuntimeError("No time steps available in Stage 5A model.")
        last = len(times)
        data = eval_field_set(model, last)
        review_dir = STAGE5 / "images" / "5A_review"
        outputs["images"].append(render_field(review_dir / "5A_phils_cloud_with_colorbar.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True))
        outputs["images"].append(render_field(review_dir / "5A_phils_0p5_interface_line.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="gray", phi=data["phi"], draw_interface=True))
        outputs["images"].append(render_field(review_dir / "5A_phils_sample_scatter.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True, scatter_only=True))
        outputs["images"].append(render_field(review_dir / "5A_density_rho.png", data["r"], data["z"], data["rho"], cmap="viridis", phi=data["phi"], draw_interface=True))
        outputs["images"].append(render_field(review_dir / "5A_viscosity_mu.png", data["r"], data["z"], data["mu"], cmap="gray", phi=data["phi"], draw_interface=True))
        frame_rows: list[dict[str, Any]] = []
        for idx, t in enumerate(times[:5], start=1):
            frame_data = eval_field_set(model, idx)
            path = review_dir / f"5A_interface_overlay_frame_{idx:03d}.png"
            img = render_field(path, frame_data["r"], frame_data["z"], frame_data["phi"], vlim=(0, 1), cmap="phase", phi=frame_data["phi"], draw_interface=True)
            frame_rows.append({"frame": idx, "time_s": t, "file": str(path), "ok": img.get("ok")})
            outputs["images"].append(img)
        write_csv(STAGE5 / "tables" / "5A_review_frame_index.csv", frame_rows)
        outputs["tables"].append(str(STAGE5 / "tables" / "5A_review_frame_index.csv"))
        metrics = json.loads((STAGE5 / "stage5a_summary.json").read_text(encoding="utf-8"))["outputs"]["metrics"]
        water_ok = metrics[-1]["phi_mean_below_z_minus_1cm"] > 0.95
        air_ok = metrics[-1]["phi_mean_above_z_plus_1cm"] < 0.05
        stable_ok = bool(json.loads((STAGE5 / "stage5a_summary.json").read_text(encoding="utf-8"))["outputs"]["interface_stability_smoke_pass"])
        status = "PASS" if water_ok and air_ok and stable_ok and all(i.get("ok") for i in outputs["images"]) else "FAIL"
        report = STAGE5 / "reports" / "5A_visual_review_package.md"
        report.write_text(
            "\n".join([
                "# Stage 5A Visual Review Package",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                f"5A-cleanup review status: `{status}`",
                "",
                "## Meaning Of The Visuals",
                "",
                "- Deep blue points in the `phils` plots represent water-rich samples (`phils` close to 1).",
                "- Light blue/near-white points represent air-rich samples (`phils` close to 0).",
                "- The black horizontal reference line is `z=0`, the intended initial still-water level.",
                "- The black interface curve is extracted from `phils=0.5` and used as the free-surface threshold.",
                "- The `phils_sample_scatter` figure is a sampled point cloud, not a mesh plot.",
                "",
                "## Checks",
                "",
                f"- Water phase in `z<0`: `{water_ok}`.",
                f"- Air phase in `z>0`: `{air_ok}`.",
                f"- Interface short-time stability: `{stable_ok}`.",
                "- 5A is suitable as a reduced-model starting point for 5B, but it is not itself a fountain model.",
                "",
                "## Coupling Note",
                "",
                "- Current 5A is a minimal manual coupling: standalone `LaminarFlow + LevelSet`.",
                "- The combined `Laminar Two-Phase Flow, Level Set` multiphysics type could not be created through the tested COMSOL API type names in the previous probe.",
                "- The manual coupling sets mixture properties using `phils`: `rho_air+(rho_w-rho_air)*phils` and `mu_air+(mu_w-mu_air)*phils`.",
                "",
                "## Outputs",
                "",
                *[f"- `{item.get('file')}`" for item in outputs["images"]],
            ]),
            encoding="utf-8",
        )
        outputs["report"] = str(report)
        outputs["status"] = status
        return outputs
    finally:
        try:
            client.remove(model)
        except Exception:
            pass


def set_tlist(model: Any, expr: str) -> None:
    study = model.java.study("std1")
    for tag in [str(x) for x in list(study.feature().tags())]:
        feat = study.feature(tag)
        if "time" in tag.lower() or "time" in str(feat.getType()).lower():
            feat.set("tlist", expr)


def setup_b1(model: Any) -> dict[str, Any]:
    param = model.java.param()
    for k, v in {
        "A_force": "0.10[m/s]",
        "r_force": "8[mm]",
        "z_force": "-10[mm]",
        "sigma_r": "5[mm]",
        "sigma_z": "5[mm]",
        "t_force": "0.01[s]",
        "t_end_5B": "0.08[s]",
    }.items():
        param.set(k, v)
    force_shape = "exp(-((r-r_force)/sigma_r)^2-((z-z_force)/sigma_z)^2)"
    time_gate = "flc2hs(t_force-t,t_force/10)"
    spf = model.java.component("comp1").physics("spf")
    if "vf_center" in [str(x) for x in list(spf.feature().tags())]:
        spf.feature().remove("vf_center")
    vf = spf.feature().create("vf_center", "VolumeForce", 2)
    vf.set("F_src", "userdef")
    vf.set("F", ["0", "0", f"rho_w*A_force/t_force*({force_shape})*({time_gate})*phils"])
    try:
        spf.feature("init1").set("u", ["0", "0", f"A_force*({force_shape})"])
    except Exception:
        pass
    ls = model.java.component("comp1").physics("ls")
    lsm = ls.feature("lsm1")
    lsm.set("u_src", "userdef")
    lsm.set("u", ["u", "0", "w"])
    set_tlist(model, "range(0,t_end_5B/16,t_end_5B)")
    return {
        "mode": "hydrodynamic_volume_force",
        "forcing_type": "localized upward VolumeForce in LaminarFlow; LevelSet advected by solved flow field [u,0,w]",
        "volume_force_feature": "spf/vf_center",
        "F": ["0", "0", f"rho_w*A_force/t_force*({force_shape})*({time_gate})*phils"],
        "level_set_velocity": "ls/lsm1 u_src=userdef, u=[u,0,w]",
    }


def setup_b1_kinematic(model: Any) -> dict[str, Any]:
    param = model.java.param()
    for k, v in {
        "A_force": "0.10[m/s]",
        "r_force": "8[mm]",
        "z_force": "-10[mm]",
        "sigma_r": "5[mm]",
        "sigma_z": "5[mm]",
        "t_force": "0.01[s]",
        "t_end_5B": "0.08[s]",
    }.items():
        param.set(k, v)
    spf = model.java.component("comp1").physics("spf")
    if "vf_center" in [str(x) for x in list(spf.feature().tags())]:
        spf.feature().remove("vf_center")
    try:
        spf.feature("init1").set("u", ["0", "0", "0"])
    except Exception:
        pass
    # This fallback is deliberately reduced: it imposes a local upward Level Set
    # advection velocity near the axis and above the subsurface forcing center.
    # It is used only if the hydrodynamic VolumeForce version cannot initialize.
    force_expr = "A_force*exp(-(r/r_force)^2)*flc2hs(z-z_force,sigma_z)*flc2hs(t_force-t,t_force/10)"
    comp = model.java.component("comp1")
    try:
        if "var_b1" in [str(x) for x in list(comp.variable().tags())]:
            comp.variable().remove("var_b1")
        var = comp.variable().create("var_b1")
        var.set("w_force_kin", force_expr)
    except Exception:
        pass
    ls = comp.physics("ls")
    lsm = ls.feature("lsm1")
    lsm.set("u_src", "userdef")
    lsm.set("u", ["0", "0", force_expr])
    set_tlist(model, "range(0,t_end_5B/16,t_end_5B)")
    return {
        "mode": "kinematic_level_set_velocity",
        "forcing_type": "localized upward Level Set advection velocity; reduced kinematic forcing",
        "w_force_kin": force_expr,
        "level_set_velocity": f"ls/lsm1 u_src=userdef, u=[0,0,{force_expr}]",
        "note": "Used after the hydrodynamic VolumeForce attempt failed to find consistent initial values.",
    }


def extract_h_vs_t(model: Any, model_id: str, out_dir: Path, threshold: float = 0.5) -> dict[str, Any]:
    times = read_times(model)
    rows: list[dict[str, Any]] = []
    frames: list[dict[str, Any]] = []
    for inner, t in enumerate(times, start=1):
        data = eval_field_set(model, inner)
        pts = estimate_interface(data["r"], data["z"], data["phi"], threshold)
        valid = [(r, z) for r, z in pts if r < 0.095 and z < 0.11]
        max_z = max((z for _, z in valid), default=math.nan)
        h = max_z - 0.0 if math.isfinite(max_z) else math.nan
        near_top = bool(math.isfinite(max_z) and max_z > 0.105)
        rows.append({
            "model_id": model_id,
            "inner_solution": inner,
            "time_s": t,
            "interface_threshold": threshold,
            "interface_points": len(valid),
            "max_interface_z_m": max_z,
            "H_m": h,
            "H_mm": h * 1000 if math.isfinite(h) else math.nan,
            "near_domain_top": near_top,
        })
        frame = out_dir / "frames" / f"{model_id}_interface_frame_{inner:03d}.png"
        img = render_field(frame, data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True)
        frames.append({"inner_solution": inner, "time_s": t, "file": str(frame), "ok": img.get("ok")})
    csv_path = STAGE5 / "tables" / f"{model_id}_H_vs_t.csv"
    frame_index = STAGE5 / "tables" / f"{model_id}_frame_index.csv"
    write_csv(csv_path, rows)
    write_csv(frame_index, frames)
    valid_h = [row for row in rows if math.isfinite(float(row["H_m"]))]
    hmax_row = max(valid_h, key=lambda row: float(row["H_m"])) if valid_h else None
    plot_path = out_dir / f"{model_id}_H_vs_t.png"
    render_curve(plot_path, rows)
    return {"times": times, "rows": rows, "csv": str(csv_path), "frame_index": str(frame_index), "frames": frames, "H_vs_t_png": str(plot_path), "hmax_row": hmax_row}


def render_curve(path: Path, rows: list[dict[str, Any]]) -> None:
    width, height = 900, 520
    pixels = bytearray([248, 248, 246] * width * height)
    ts = np.array([float(r["time_s"]) for r in rows if math.isfinite(float(r["H_m"]))])
    hs = np.array([float(r["H_mm"]) for r in rows if math.isfinite(float(r["H_m"]))])
    if ts.size == 0:
        png_write(path, width, height, pixels)
        return
    margin = 60
    tlo, thi = float(np.min(ts)), float(np.max(ts))
    hlo, hhi = min(0.0, float(np.min(hs))), max(1e-6, float(np.max(hs)))
    def tx(t: float) -> int:
        return int(margin + (t - tlo) / max(1e-12, thi - tlo) * (width - 2 * margin))
    def ty(h: float) -> int:
        return int(height - margin - (h - hlo) / max(1e-12, hhi - hlo) * (height - 2 * margin))
    line(pixels, width, height, margin, height - margin, width - margin, height - margin, (40, 40, 40))
    line(pixels, width, height, margin, margin, margin, height - margin, (40, 40, 40))
    for (t0, h0), (t1, h1) in zip(zip(ts[:-1], hs[:-1]), zip(ts[1:], hs[1:])):
        line(pixels, width, height, tx(float(t0)), ty(float(h0)), tx(float(t1)), ty(float(h1)), (20, 90, 190))
    for t, h in zip(ts, hs):
        circle(pixels, width, height, tx(float(t)), ty(float(h)), 4, (180, 30, 40))
    png_write(path, width, height, pixels)


def stage_b1(client: Any) -> dict[str, Any]:
    log("Stage 5B1 center forcing started.")
    model = client.load(MODEL_5A)
    model_ts = STAGE5 / "models" / f"ring_fountain_v4_5B1_center_forcing_{RUN_ID}.mph"
    summary: dict[str, Any] = {"status": "FAIL"}
    try:
        setup = setup_b1(model)
        try:
            model.solve()
        except Exception as hyd_exc:
            log(f"B1 hydrodynamic VolumeForce attempt failed; trying kinematic Level Set forcing. Error: {hyd_exc}")
            try:
                client.remove(model)
            except Exception:
                pass
            model = client.load(MODEL_5A)
            setup = setup_b1_kinematic(model)
            model.solve()
        model.save(MODEL_B1)
        model.save(model_ts)
        out_dir = STAGE5 / "images" / "5B1_center_forcing"
        hdata = extract_h_vs_t(model, "5B1_center_forcing", out_dir)
        last_inner = len(hdata["times"])
        data = eval_field_set(model, last_inner)
        velocity_inner = min(3, last_inner) if setup.get("mode") == "kinematic_level_set_velocity" else last_inner
        velocity_data = eval_field_set(model, velocity_inner)
        if setup.get("mode") == "kinematic_level_set_velocity":
            w_force = s42a.eval_array(model, setup["w_force_kin"], "m/s", inner=[velocity_inner]).reshape(-1)
            u_force = np.zeros_like(w_force)
            velocity_mag = np.abs(w_force)
            axial_for_plot = w_force
            vector_u, vector_w = u_force, w_force
            velocity_note = f"Velocity plots use the imposed kinematic Level Set velocity field `w_force_kin` at inner solution {velocity_inner}, not solved `spf.w`."
        else:
            velocity_mag = velocity_data["U"]
            axial_for_plot = velocity_data["w"]
            vector_u, vector_w = velocity_data["u"], velocity_data["w"]
            velocity_note = "Velocity plots use solved Laminar Flow variables."
        images = [
            render_field(out_dir / "5B1_phils_final.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True),
            render_field(out_dir / "5B1_velocity_magnitude.png", velocity_data["r"], velocity_data["z"], velocity_mag, cmap="viridis", phi=velocity_data["phi"], draw_interface=True),
            render_field(out_dir / "5B1_axial_velocity_w.png", velocity_data["r"], velocity_data["z"], axial_for_plot, cmap="viridis", phi=velocity_data["phi"], draw_interface=True),
            render_vector(out_dir / "5B1_local_velocity_vectors.png", velocity_data["r"], velocity_data["z"], vector_u, vector_w, velocity_data["phi"]),
        ]
        hrows = hdata["rows"]
        hmax = hdata["hmax_row"]
        h0 = float(hrows[0]["H_m"]) if hrows and math.isfinite(float(hrows[0]["H_m"])) else 0.0
        h_peak = float(hmax["H_m"]) if hmax else math.nan
        upstroke = math.isfinite(h_peak) and h_peak - h0 > 2e-5
        no_top = hmax is not None and not bool(hmax["near_domain_top"])
        identifiable = all(row["interface_points"] > 20 for row in hrows)
        status = "PASS" if upstroke and no_top and identifiable and all(i.get("ok") for i in images) else "FAIL"
        report = STAGE5 / "reports" / "5B1_center_forcing_report.md"
        report.write_text(
            "\n".join([
                "# Stage 5B1 Center Forcing Report",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                f"B1 review status: `{status}`",
                "",
                "## Model Type",
                "",
                "- Reduced center-forcing free-surface model.",
                "- This is not a complete true falling-ring model.",
                "- Forcing is local and controlled, intended to validate interface tracking and H(t) extraction.",
                "",
                "## Forcing Method",
                "",
                f"- `{json.dumps(setup, ensure_ascii=False)}`",
                f"- {velocity_note}",
                "",
                "## Review",
                "",
                f"- Interface identifiable: `{identifiable}`.",
                f"- Observable upstroke: `{upstroke}`.",
                f"- Did not touch domain top: `{no_top}`.",
                f"- Preliminary H peak: `{h_peak} m`.",
                "",
                "## Outputs",
                "",
                f"- Model: `{MODEL_B1}`",
                f"- Timestamp model: `{model_ts}`",
                f"- H(t) CSV: `{hdata['csv']}`",
                f"- H(t) plot: `{hdata['H_vs_t_png']}`",
                *[f"- `{i.get('file')}`" for i in images],
            ]),
            encoding="utf-8",
        )
        summary.update({"status": status, "model": str(MODEL_B1), "timestamp_model": str(model_ts), "report": str(report), "setup": setup, "hdata": hdata, "images": images, "review": {"upstroke": upstroke, "no_top": no_top, "identifiable": identifiable}})
        return summary
    except Exception as exc:
        err = STAGE5 / "logs" / f"5B1_error_{RUN_ID}.log"
        err.write_text(traceback.format_exc(), encoding="utf-8")
        summary.update({"status": "FAIL", "error": str(exc), "error_log": str(err)})
        return summary
    finally:
        try:
            client.remove(model)
        except Exception:
            pass


def create_b2_model(client: Any) -> tuple[Any, dict[str, Any]]:
    model = client.create("ring_fountain_5B2_fixed_ring")
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
        "Ri": "8[mm]",
        "Ro": "20[mm]",
        "h_ring": "2[mm]",
        "z_ring_center": "-20[mm]",
        "V_ring_5B": "0.10[m/s]",
        "t_end_5B": "0.08[s]",
        "eps_ls": "2[mm]",
    }.items():
        param.set(name, value)
    comp = java.component().create("comp1", True)
    geom = comp.geom().create("geom1", 2)
    try:
        geom.axisymmetric(True)
    except Exception:
        pass
    tank = geom.feature().create("tank", "Rectangle")
    tank.set("size", ["Rtank", "Hwater+Hair"])
    tank.set("pos", ["0", "-Hwater"])
    ring = geom.feature().create("ring", "Rectangle")
    ring.set("size", ["Ro-Ri", "h_ring"])
    ring.set("pos", ["Ri", "z_ring_center-h_ring/2"])
    diff = geom.feature().create("dif1", "Difference")
    diff.selection("input").set(["tank"])
    diff.selection("input2").set(["ring"])
    geom.run()
    mesh = comp.mesh().create("mesh1")
    mesh.autoMeshSize(4)
    mesh.run()
    spf = comp.physics().create("spf", "LaminarFlow", "geom1")
    ls = comp.physics().create("ls", "LevelSet", "geom1")
    fp = spf.feature("fp1")
    fp.set("rho_mat", "userdef")
    fp.set("rho", "rho_air+(rho_w-rho_air)*phils")
    fp.set("mu_mat", "userdef")
    fp.set("mu", "mu_air+(mu_w-mu_air)*phils")
    try:
        spf.feature("init1").set("u", ["0", "0", "0"])
    except Exception:
        pass
    ls.feature("init1").set("phils", "flc2hs(-z,eps_ls)")
    ls.feature("lsm1").set("u_src", "userdef")
    ls.feature("lsm1").set("u", ["u", "0", "w"])
    study = java.study().create("std1")
    study.create("time", "Transient")
    study.feature("time").set("tlist", "range(0,t_end_5B/16,t_end_5B)")
    return model, {"geometry": "rectangle tank minus fixed rectangular ring hole", "coupling": "manual LaminarFlow + LevelSet with phils mixture properties"}


def jints(values: list[int]) -> Any:
    return jpype.JArray(jpype.JInt)(values)


def ensure_b2_selections(model: Any) -> dict[str, Any]:
    rows = s41.boundary_metrics(model)
    ri = s42a.param_float(model, "Ri", "m")
    ro = s42a.param_float(model, "Ro", "m")
    h = s42a.param_float(model, "h_ring", "m")
    zc = s42a.param_float(model, "z_ring_center", "m")
    tol = 5e-5
    roles: dict[str, int] = {}
    for row in rows:
        bid = int(row["boundary_id"])
        rmin, rmax, zmin, zmax = row["r_min_m"], row["r_max_m"], row["z_min_m"], row["z_max_m"]
        length = row["length_m"]
        if abs(rmin - ri) < tol and abs(rmax - ri) < tol and abs(length - h) < tol:
            roles["sel_5B_ring_wall_inner"] = bid
        if abs(rmin - ro) < tol and abs(rmax - ro) < tol and abs(length - h) < tol:
            roles["sel_5B_ring_wall_outer"] = bid
        if abs(zmin - (zc + h / 2)) < tol and abs(zmax - (zc + h / 2)) < tol and abs(length - (ro - ri)) < tol:
            roles["sel_5B_ring_wall_top"] = bid
        if abs(zmin - (zc - h / 2)) < tol and abs(zmax - (zc - h / 2)) < tol and abs(length - (ro - ri)) < tol:
            roles["sel_5B_ring_wall_bottom"] = bid
    if len(roles) != 4:
        return {"ok": False, "roles": roles, "rows": rows, "error": "Could not uniquely identify four ring boundaries."}
    selections = model.java.component("comp1").selection()
    for tag, bid in roles.items():
        if tag in [str(x) for x in list(selections.tags())]:
            selections.remove(tag)
        selections.create(tag, "Explicit")
        node = selections.get(tag)
        node.label(tag)
        node.geom("geom1", 1)
        node.set(jints([bid]))
    confirmed = sorted(roles.values())
    tag = "sel_5B_ring_wall_confirmed"
    if tag in [str(x) for x in list(selections.tags())]:
        selections.remove(tag)
    selections.create(tag, "Explicit")
    node = selections.get(tag)
    node.label(tag)
    node.geom("geom1", 1)
    node.set(jints(confirmed))
    return {"ok": True, "roles": roles, "confirmed": confirmed, "rows": rows}


def setup_b2_wall(model: Any, ids: list[int]) -> dict[str, Any]:
    spf = model.java.component("comp1").physics("spf")
    wall = spf.feature("wallbc1")
    # Default wall feature is used; selection is restricted to confirmed ring only for the moving wall.
    wall.selection().set(jints(ids))
    wall.set("BoundaryCondition", "NoSlip")
    wall.set("SlidingWall", "1")
    wall.set("TranslationalVelocityOption", "Manual")
    wall.set("utr", ["0", "0", "-V_ring_5B"])
    return {"feature": "spf/wallbc1", "selection": ids, "utr": ["0", "0", "-V_ring_5B"], "direction": "negative z"}


def stage_b2(client: Any) -> dict[str, Any]:
    log("Stage 5B2 fixed ring moving-wall model started.")
    summary: dict[str, Any] = {"status": "FAIL"}
    model = None
    model_ts = STAGE5 / "models" / f"ring_fountain_v4_5B2_fixed_ring_moving_wall_free_surface_{RUN_ID}.mph"
    try:
        model, setup = create_b2_model(client)
        sel = ensure_b2_selections(model)
        if not sel.get("ok"):
            raise RuntimeError(sel.get("error"))
        wall = setup_b2_wall(model, sel["confirmed"])
        model.solve()
        model.save(MODEL_B2)
        model.save(model_ts)
        out_dir = STAGE5 / "images" / "5B2_fixed_ring"
        hdata = extract_h_vs_t(model, "5B2_fixed_ring", out_dir)
        data = eval_field_set(model, len(hdata["times"]))
        images = [
            render_field(out_dir / "5B2_phils_final.png", data["r"], data["z"], data["phi"], vlim=(0, 1), cmap="phase", phi=data["phi"], draw_interface=True),
            render_field(out_dir / "5B2_velocity_magnitude.png", data["r"], data["z"], data["U"], cmap="viridis", phi=data["phi"], draw_interface=True),
            render_field(out_dir / "5B2_pressure.png", data["r"], data["z"], data["p"], cmap="viridis", phi=data["phi"], draw_interface=True),
            render_vector(out_dir / "5B2_local_velocity_vectors.png", data["r"], data["z"], data["u"], data["w"], data["phi"]),
        ]
        hmax = hdata["hmax_row"]
        h0 = float(hdata["rows"][0]["H_m"]) if hdata["rows"] else 0.0
        h_peak = float(hmax["H_m"]) if hmax else math.nan
        upstroke = math.isfinite(h_peak) and h_peak - h0 > 2e-5
        no_top = hmax is not None and not bool(hmax["near_domain_top"])
        identifiable = all(row["interface_points"] > 20 for row in hdata["rows"])
        status = "PASS" if upstroke and no_top and identifiable and all(i.get("ok") for i in images) else "FAIL"
        report = STAGE5 / "reports" / "5B2_fixed_ring_moving_wall_report.md"
        report.write_text(
            "\n".join([
                "# Stage 5B2 Fixed Ring Moving Wall Report",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                f"B2 review status: `{status}`",
                "",
                "## Model Type",
                "",
                "- Reduced fixed-ring geometry + moving-wall velocity + free-surface model.",
                "- The ring geometry is fixed; the moving wall imposes velocity and does not translate the ring.",
                "",
                "## Ring Boundary Selections",
                "",
                f"- `{json.dumps(sel.get('roles'), ensure_ascii=False)}`",
                f"- Confirmed B2 ring boundaries: `{sel.get('confirmed')}`",
                "",
                "## Moving Wall",
                "",
                f"- `{json.dumps(wall, ensure_ascii=False)}`",
                "",
                "## Review",
                "",
                f"- Interface identifiable: `{identifiable}`.",
                f"- Observable upstroke: `{upstroke}`.",
                f"- Did not touch domain top: `{no_top}`.",
                "",
                "## Outputs",
                "",
                f"- Model: `{MODEL_B2}`",
                f"- Timestamp model: `{model_ts}`",
                f"- H(t) CSV: `{hdata['csv']}`",
                *[f"- `{i.get('file')}`" for i in images],
            ]),
            encoding="utf-8",
        )
        summary.update({"status": status, "model": str(MODEL_B2), "timestamp_model": str(model_ts), "report": str(report), "setup": setup, "selections": sel, "wall": wall, "hdata": hdata, "images": images})
        return summary
    except Exception as exc:
        err = STAGE5 / "logs" / f"5B2_error_{RUN_ID}.log"
        err.write_text(traceback.format_exc(), encoding="utf-8")
        report = STAGE5 / "reports" / "5B2_fixed_ring_moving_wall_report.md"
        report.write_text(
            "\n".join([
                "# Stage 5B2 Fixed Ring Moving Wall Report",
                "",
                f"Run time: {datetime.now().isoformat(timespec='seconds')}",
                "",
                "B2 review status: `FAIL`",
                "",
                "## Stop Reason",
                "",
                f"- `{exc}`",
                "",
                "## Consequence",
                "",
                "- B2 was not used for Hmax extraction.",
                "- Because B1 passed, Stage 5C may proceed using the B1 approximate reduced center-forcing model.",
                "",
                "## Error Log",
                "",
                f"- `{err}`",
            ]),
            encoding="utf-8",
        )
        summary.update({"status": "FAIL", "error": str(exc), "error_log": str(err), "report": str(report)})
        return summary
    finally:
        try:
            if model is not None:
                client.remove(model)
        except Exception:
            pass


def stage_5c(source: dict[str, Any], model_type: str) -> dict[str, Any]:
    log("Stage 5C Hmax extraction started.")
    hdata = source["hdata"]
    hmax_row = hdata.get("hmax_row")
    out_dir = STAGE5 / "images" / "5C_Hmax"
    model_used = source.get("model")
    approximate = model_type.startswith("B1")
    forcing_type = source.get("setup", {}).get("forcing_type") if approximate else "fixed ring moving wall"
    summary_csv = STAGE5 / "tables" / "Hmax_summary.csv"
    h_vs_t_csv = STAGE5 / "tables" / "H_vs_t.csv"
    rows = hdata["rows"]
    write_csv(h_vs_t_csv, rows)
    quality_status = "invalid"
    if hmax_row is not None:
        enough_pts = min(row["interface_points"] for row in rows) > 20
        not_top = not bool(hmax_row["near_domain_top"])
        h_finite = math.isfinite(float(hmax_row["H_m"]))
        quality_status = "valid" if enough_pts and not_top and h_finite else "invalid"
    summary_row = {
        "model_used": model_used,
        "model_type": "approximate reduced center-forcing model" if approximate else "reduced fixed-geometry moving-wall free-surface model",
        "forcing_type": forcing_type or ("center Gaussian reduced forcing" if approximate else "fixed ring moving wall"),
        "V_used": "" if approximate else "0.10[m/s]",
        "A_force": "0.10[m/s]" if approximate else "",
        "Ri": "" if approximate else "8[mm]",
        "Ro": "" if approximate else "20[mm]",
        "h_ring": "" if approximate else "2[mm]",
        "z_ring_center": "" if approximate else "-20[mm]",
        "interface_variable": "phils",
        "interface_threshold": 0.5,
        "Hmax": float(hmax_row["H_m"]) if hmax_row else math.nan,
        "Hmax_mm": float(hmax_row["H_mm"]) if hmax_row else math.nan,
        "t_at_Hmax": float(hmax_row["time_s"]) if hmax_row else math.nan,
        "domain_top": "0.12[m]",
        "quality_status": quality_status,
        "notes": "approximate/reduced model; Hmax is not a fully validated physical ring-fountain height" if approximate else "reduced fixed-geometry moving-wall free-surface model",
    }
    write_csv(summary_csv, [summary_row])
    curve_copy = out_dir / "H_vs_t.png"
    render_curve(curve_copy, rows)
    status = "PASS" if quality_status == "valid" else "FAIL"
    report = STAGE5 / "reports" / "Hmax_extraction_report.md"
    report.write_text(
        "\n".join([
            "# Stage 5C Hmax Extraction Report",
            "",
            f"Run time: {datetime.now().isoformat(timespec='seconds')}",
            "",
            f"5C review status: `{status}`",
            "",
            "## Definition",
            "",
            "- Initial free surface: `z0=0`.",
            "- Interface threshold: `phils=0.5`.",
            "- `H(t)=max_z(interface at time t)-z0`.",
            "- `Hmax=max_t H(t)`.",
            "",
            "## Result",
            "",
            f"- Model used: `{model_used}`.",
            f"- Model type: `{summary_row['model_type']}`.",
            f"- Hmax: `{summary_row['Hmax']} m` = `{summary_row['Hmax_mm']} mm`.",
            f"- t_at_Hmax: `{summary_row['t_at_Hmax']} s`.",
            f"- Approximate: `{approximate}`.",
            f"- Quality status: `{quality_status}`.",
            "",
            "## Outputs",
            "",
            f"- H_vs_t.csv: `{h_vs_t_csv}`",
            f"- Hmax_summary.csv: `{summary_csv}`",
            f"- H_vs_t.png: `{curve_copy}`",
            f"- Source frame index: `{hdata['frame_index']}`",
        ]),
        encoding="utf-8",
    )
    return {"status": status, "model_used": model_used, "model_type": summary_row["model_type"], "approximate": approximate, "Hmax_m": summary_row["Hmax"], "Hmax_mm": summary_row["Hmax_mm"], "t_at_Hmax_s": summary_row["t_at_Hmax"], "quality_status": quality_status, "H_vs_t_csv": str(h_vs_t_csv), "summary_csv": str(summary_csv), "plot": str(curve_copy), "report": str(report)}


def append_final_docs(summary: dict[str, Any]) -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text += "\n\n## Stage 5B/5C Current Result\n\n"
    text += f"- 5A-cleanup: `{summary.get('5A_cleanup', {}).get('status')}`.\n"
    text += f"- 5B1 reduced center forcing: `{summary.get('B1', {}).get('status')}`.\n"
    text += f"- 5B2 fixed ring moving wall: `{summary.get('B2', {}).get('status', 'not_run')}`.\n"
    text += f"- 5C Hmax extraction: `{summary.get('5C', {}).get('status', 'not_run')}`.\n"
    if summary.get("5C"):
        text += f"- Hmax result is approximate: `{summary['5C'].get('approximate')}`.\n"
    readme.write_text(text, encoding="utf-8")
    changelog = ROOT / "CHANGELOG.md"
    ch = changelog.read_text(encoding="utf-8")
    ch += f"\n\n## {datetime.now().isoformat(timespec='seconds')} - Stage 5 cleanup, 5B, and 5C\n\n"
    ch += f"- 5A-cleanup: `{summary.get('5A_cleanup', {}).get('status')}`.\n"
    ch += f"- B1: `{summary.get('B1', {}).get('status')}`.\n"
    ch += f"- B2: `{summary.get('B2', {}).get('status', 'not_run')}`.\n"
    ch += f"- 5C: `{summary.get('5C', {}).get('status', 'not_run')}`.\n"
    changelog.write_text(ch, encoding="utf-8")


def main() -> None:
    os.environ["JAVA_HOME"] = r"D:\COMSOL64\Multiphysics\java\win64\jre"
    make_dirs()
    shutil.copy2(Path(__file__), SCRIPTS / "ring_fountain_stage5_cleanup_5b_5c.py")
    summary: dict[str, Any] = {"run_id": RUN_ID}
    client = mph.Client(cores=2, version="6.4")
    try:
        cleanup = stage5a_cleanup(client)
        summary["5A_cleanup"] = cleanup
        if cleanup.get("status") != "PASS":
            summary["stop_reason"] = "5A-cleanup review did not PASS."
            return
        b1 = stage_b1(client)
        summary["B1"] = b1
        if b1.get("status") != "PASS":
            summary["stop_reason"] = "B1 review did not PASS; B2 and 5C not run."
            return
        b2 = stage_b2(client)
        summary["B2"] = b2
        source = b2 if b2.get("status") == "PASS" else b1
        model_type = "B2" if b2.get("status") == "PASS" else "B1"
        summary["5C"] = stage_5c(source, model_type)
    finally:
        append_final_docs(summary)
        (STAGE5 / "stage5_cleanup_5b_5c_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        try:
            client.clear()
        except Exception:
            pass
        log(f"Stage 5 chain summary written: {STAGE5 / 'stage5_cleanup_5b_5c_summary.json'}")


if __name__ == "__main__":
    main()
