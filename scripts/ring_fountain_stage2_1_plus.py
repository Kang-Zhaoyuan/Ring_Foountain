# -*- coding: utf-8 -*-
"""Continue COMSOL Ring Fountain automation from stage 2.1.

This script is intentionally conservative.  It keeps the original V0 and the
previous stage outputs untouched, writes each new stage into its own directory,
and gates later stages on explicit review status.
"""

from __future__ import annotations

import csv
import json
import math
import os
import shutil
import struct
import traceback
import zipfile
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import numpy as np


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
INPUT_CHECKED = ROOT / "01_v0_checked" / "models" / "ring_fountain_v0_checked.mph"
OLD_SWEEP = ROOT / "02_param_sweep" / "tables" / "param_sweep_results.csv"
SCRIPTS = ROOT / "scripts"

STAGE21 = ROOT / "02_1_metric_calibration"
STAGE22 = ROOT / "02_2_clean_param_sweep"
STAGE23 = ROOT / "02_3_clean_sweep_review"
STAGE3 = ROOT / "03_relative_flow_model"
STAGE4 = ROOT / "04_moving_ring_model"
STAGE5 = ROOT / "05_two_phase_free_surface"

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = STAGE21 / "logs" / f"stage2_1_plus_{RUN_ID}.log"

BASE_PARAMS = {
    "Ro": "20[mm]",
    "Ri": "8[mm]",
    "Rtank": "100[mm]",
    "Zup": "120[mm]",
    "Zdown": "120[mm]",
    "U0": "0.02[m/s]",
    "rho_w": "1000[kg/m^3]",
    "mu_w": "1e-3[Pa*s]",
    "h_ring": "2[mm]",
}

PARAM_DESCRIPTIONS = {
    "Ro": "Outer radius of the ring.",
    "Ri": "Inner radius of the ring opening.",
    "Rtank": "Radius of the axisymmetric computational water domain.",
    "Zup": "Water-domain height above the ring center plane.",
    "Zdown": "Water-domain height below the ring center plane.",
    "U0": "Relative incoming velocity in the fixed-ring single-phase model.",
    "rho_w": "Water density.",
    "mu_w": "Water dynamic viscosity.",
    "h_ring": "Ring cross-section thickness in the simplified model.",
}

STAGE_DIRS = [STAGE21, STAGE22, STAGE23, STAGE3, STAGE4, STAGE5]


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def safe(label: str, fn: Callable[[], Any]) -> dict[str, Any]:
    try:
        value = fn()
        log(f"OK: {label}")
        return {"ok": True, "value": value}
    except Exception as exc:
        log(f"FAIL: {label}: {exc}")
        with LOG.open("a", encoding="utf-8") as handle:
            handle.write(traceback.format_exc() + "\n")
        return {"ok": False, "error": str(exc)}


def make_dirs() -> None:
    for base in STAGE_DIRS:
        for sub in ["models", "reports", "images", "tables", "logs"]:
            (base / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def clean_value(value: Any) -> Any:
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def eval_array(model: Any, expression: str, unit: str | None = None) -> np.ndarray:
    if unit:
        value = model.evaluate(expression, unit=unit)
    else:
        value = model.evaluate(expression)
    arr = np.asarray(value, dtype=float)
    return arr[np.isfinite(arr)]


def eval_scalar_max(model: Any, expression: str, unit: str | None = None) -> float:
    arr = eval_array(model, expression, unit)
    if arr.size == 0:
        raise ValueError(f"no finite values for {expression}")
    return float(np.nanmax(arr))


def eval_scalar_mean(model: Any, expression: str, unit: str | None = None) -> float:
    arr = eval_array(model, expression, unit)
    if arr.size == 0:
        raise ValueError(f"no finite values for {expression}")
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
            writer.writerow({
                key: json.dumps(row.get(key), ensure_ascii=False) if isinstance(row.get(key), (list, dict)) else row.get(key)
                for key in keys
            })


def col_name(index: int) -> str:
    name = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        name = chr(65 + rem) + name
    return name


def write_xlsx(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)

    def cell_xml(value: Any) -> tuple[str, str]:
        if value is None:
            return "", ""
        text = str(value)
        try:
            number = float(text)
            if math.isfinite(number) and text.strip() == text:
                return "", str(number)
        except Exception:
            pass
        escaped = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        return ' t="inlineStr"', f"<is><t>{escaped}</t></is>"

    sheet_rows = []
    all_rows = [dict(zip(keys, keys))] + rows
    for r_index, row in enumerate(all_rows, start=1):
        cells = []
        for c_index, key in enumerate(keys):
            attrs, body = cell_xml(row.get(key, ""))
            ref = f"{col_name(c_index)}{r_index}"
            cells.append(f'<c r="{ref}"{attrs}>{body}</c>')
        sheet_rows.append(f'<row r="{r_index}">{"".join(cells)}</row>')
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>'
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>""")
        zf.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>""")
        zf.writestr("xl/workbook.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>""")
        zf.writestr("xl/_rels/workbook.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>""")
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def png_write(path: Path, width: int, height: int, pixels: bytearray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw.extend(pixels[y * stride:(y + 1) * stride])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    payload = b"\x89PNG\r\n\x1a\n"
    payload += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    payload += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    payload += chunk(b"IEND", b"")
    path.write_bytes(payload)


def draw_line(pixels: bytearray, width: int, height: int, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        if 0 <= x < width and 0 <= y < height:
            i = (y * width + x) * 3
            pixels[i:i + 3] = bytes(color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def draw_rect(pixels: bytearray, width: int, height: int, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for y in [y0, y1]:
            if 0 <= x < width and 0 <= y < height:
                i = (y * width + x) * 3
                pixels[i:i + 3] = bytes(color)
    for y in range(min(y0, y1), max(y0, y1) + 1):
        for x in [x0, x1]:
            if 0 <= x < width and 0 <= y < height:
                i = (y * width + x) * 3
                pixels[i:i + 3] = bytes(color)


def make_line_chart(path: Path, title: str, rows: list[dict[str, Any]], x_key: str, y_key: str) -> bool:
    points = []
    for row in rows:
        try:
            x = float(row[x_key])
            y = float(row[y_key])
            if math.isfinite(x) and math.isfinite(y):
                points.append((x, y))
        except Exception:
            pass
    if len(points) < 2:
        return False
    width, height = 900, 560
    pixels = bytearray([255, 255, 255] * width * height)
    margin_l, margin_r, margin_t, margin_b = 90, 40, 50, 80
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmax == xmin:
        xmax += 1.0
    if ymax == ymin:
        ymax += 1.0
    ymin -= 0.06 * abs(ymax - ymin)
    ymax += 0.06 * abs(ymax - ymin)

    def tx(x: float) -> int:
        return int(margin_l + (x - xmin) / (xmax - xmin) * (width - margin_l - margin_r))

    def ty(y: float) -> int:
        return int(height - margin_b - (y - ymin) / (ymax - ymin) * (height - margin_t - margin_b))

    axis = (35, 35, 35)
    grid = (220, 220, 220)
    blue = (24, 96, 160)
    draw_line(pixels, width, height, margin_l, height - margin_b, width - margin_r, height - margin_b, axis)
    draw_line(pixels, width, height, margin_l, margin_t, margin_l, height - margin_b, axis)
    for i in range(6):
        y = margin_t + i * (height - margin_t - margin_b) // 5
        draw_line(pixels, width, height, margin_l, y, width - margin_r, y, grid)
    last = None
    for x, y in sorted(points):
        px, py = tx(x), ty(y)
        if last:
            draw_line(pixels, width, height, last[0], last[1], px, py, blue)
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                if dx * dx + dy * dy <= 16 and 0 <= px + dx < width and 0 <= py + dy < height:
                    i = ((py + dy) * width + px + dx) * 3
                    pixels[i:i + 3] = bytes((180, 40, 40))
        last = (px, py)
    png_write(path, width, height, pixels)
    return True


def make_schematic(path: Path) -> None:
    width, height = 900, 620
    pixels = bytearray([250, 250, 248] * width * height)
    black = (40, 40, 40)
    blue = (40, 120, 180)
    red = (190, 55, 45)
    green = (35, 150, 95)
    orange = (220, 145, 45)
    tank = (110, 60, 790, 560)
    draw_rect(pixels, width, height, *tank, black)
    # axis
    draw_line(pixels, width, height, 110, 60, 110, 560, blue)
    # ring cross-section: r = Ri..Ro, z = +/- h/2
    ring = (175, 302, 246, 318)
    draw_rect(pixels, width, height, *ring, red)
    # ring-near box
    draw_rect(pixels, width, height, 145, 270, 285, 350, orange)
    # center above
    draw_rect(pixels, width, height, 112, 235, 175, 300, green)
    # hole-above horizontal line
    draw_line(pixels, width, height, 112, 255, 175, 255, green)
    # center vertical line
    draw_line(pixels, width, height, 112, 230, 112, 300, blue)
    png_write(path, width, height, pixels)


def export_plot(model: Any, plot_name: str, output: Path) -> dict[str, Any]:
    try:
        plot_node = model / "plots" / plot_name
        plot_tag = plot_node.tag()
        plot_type = plot_node.type() or ""
        export_types = ["Image3D", "Image2D"] if "3D" in plot_type or "3D" in plot_name else ["Image2D", "Image3D"]
        last_error = None
        for export_type in export_types:
            tag = None
            try:
                exports = model.java.result().export()
                tag = exports.uniquetag(f"rfimg_{plot_tag}")
                exports.create(tag, export_type)
                export = exports.get(tag)
                export.set("plotgroup", plot_tag)
                for key in ["pngfilename", "filename"]:
                    try:
                        export.set(key, str(output))
                    except Exception:
                        pass
                export.run()
                return {"ok": True, "plot": plot_name, "file": str(output), "export_type": export_type}
            except Exception as exc:
                last_error = exc
                try:
                    if tag:
                        model.java.result().export().remove(tag)
                except Exception:
                    pass
        return {"ok": False, "plot": plot_name, "file": str(output), "error": str(last_error)}
    except Exception as exc:
        return {"ok": False, "plot": plot_name, "file": str(output), "error": str(exc)}


def create_vertical_velocity_plot(model: Any, expression: str, output: Path) -> dict[str, Any]:
    tag = None
    try:
        result = model.java.result()
        tag = result.uniquetag("pg_vz")
        result.create(tag, "PlotGroup2D")
        pg = result.get(tag)
        pg.label(f"Vertical velocity metric plot {RUN_ID} {output.stem}")
        surf = pg.feature().create("surf1", "Surface")
        surf.set("expr", expression)
        surf.set("descr", "Calibrated vertical/axial velocity")
        pg.run()
        exports = result.export()
        etag = exports.uniquetag("rfimg_vz")
        exports.create(etag, "Image2D")
        exp = exports.get(etag)
        exp.set("plotgroup", tag)
        for key in ["pngfilename", "filename"]:
            try:
                exp.set(key, str(output))
            except Exception:
                pass
        exp.run()
        return {"ok": True, "plot": "Vertical velocity metric plot", "file": str(output)}
    except Exception as exc:
        return {"ok": False, "plot": "Vertical velocity metric plot", "file": str(output), "error": str(exc)}


def ensure_coupling_ops(model: Any) -> list[dict[str, Any]]:
    ops = [
        ("rfmax_all", "Maximum", "Full fluid-domain maximum operator, all domains."),
        ("rfavg_all", "Average", "Full fluid-domain average operator, all domains."),
        ("rfint_all", "Integration", "Full fluid-domain integration operator, all domains."),
    ]
    rows = []
    comp = model.java.component("comp1")
    cpl = comp.cpl()
    for tag, op_type, label in ops:
        try:
            try:
                cpl.remove(tag)
            except Exception:
                pass
            cpl.create(tag, op_type)
            node = cpl.get(tag)
            node.label(label)
            try:
                node.selection().geom("geom1", 2)
            except Exception:
                pass
            node.selection().all()
            rows.append({"tag": tag, "type": op_type, "status": "ok", "selection": "all domains"})
        except Exception as exc:
            rows.append({"tag": tag, "type": op_type, "status": "failed", "error": str(exc)})
    return rows


def set_parameter_descriptions(model: Any) -> list[dict[str, str]]:
    rows = []
    params = model.parameters()
    for name, desc in PARAM_DESCRIPTIONS.items():
        if name not in params:
            rows.append({"parameter": name, "status": "missing"})
            continue
        try:
            model.description(name, desc)
            rows.append({"parameter": name, "status": "ok", "description": desc})
        except Exception as exc:
            rows.append({"parameter": name, "status": f"failed: {exc}"})
    return rows


def variable_probe(model: Any) -> dict[str, Any]:
    candidates = {
        "velocity_magnitude": [("spf.U", "m/s"), ("U", "m/s")],
        "pressure": [("p", "Pa"), ("spf.p", "Pa")],
        "radial_velocity": [("u", "m/s"), ("spf.u", "m/s")],
        "axial_velocity": [("w", "m/s"), ("spf.w", "m/s"), ("v", "m/s"), ("spf.v", "m/s")],
        "radial_coordinate": [("r", "m"), ("x", "m")],
        "axial_coordinate": [("z", "m"), ("y", "m")],
    }
    details: dict[str, list[dict[str, Any]]] = {}
    chosen: dict[str, str] = {}
    for role, exprs in candidates.items():
        details[role] = []
        for expr, unit in exprs:
            row = {"expression": expr, "unit": unit}
            try:
                arr = eval_array(model, expr, unit)
                if arr.size == 0:
                    raise ValueError("no finite values")
                row.update({
                    "status": "ok",
                    "min": float(np.nanmin(arr)),
                    "max": float(np.nanmax(arr)),
                    "max_abs": float(np.nanmax(np.abs(arr))),
                    "sample_count": int(arr.size),
                })
            except Exception as exc:
                row.update({"status": "failed", "error": str(exc)})
            details[role].append(row)

        ok_rows = [row for row in details[role] if row.get("status") == "ok"]
        if not ok_rows:
            continue
        if role == "axial_velocity":
            chosen[role] = max(ok_rows, key=lambda row: row.get("max_abs", 0.0))["expression"]
        else:
            chosen[role] = ok_rows[0]["expression"]

    return {"chosen": chosen, "details": details}


def param_float(model: Any, expression: str, unit: str = "m") -> float:
    return eval_scalar_mean(model, expression, unit)


def metric_conditions(model: Any, coords: dict[str, str]) -> dict[str, Any]:
    r = coords["radial"]
    z = coords["axial"]
    Ri = param_float(model, "Ri", "m")
    Ro = param_float(model, "Ro", "m")
    h = param_float(model, "h_ring", "m")
    return {
        "values_m": {"Ri": Ri, "Ro": Ro, "h_ring": h, "Ri_over_Ro": Ri / Ro if Ro else None},
        "full_domain": "domain 1, current single-phase fluid domain",
        "ring_near": f"{r} in [{Ri - 2*h:.6g}, {Ro + 2*h:.6g}] m and {z} in [{-4*h:.6g}, {4*h:.6g}] m",
        "center_above": f"{r} in [0, {Ri:.6g}] m and {z} in [0, {4*h:.6g}] m",
        "axis_near": f"{r} <= {0.15*Ri:.6g} m",
        "hole_above_line": f"{z} = {h:.6g} m, {r} in [0, {Ri:.6g}] m",
        "center_vertical_line": f"{r} = 0 m, {z} in [0, {4*h:.6g}] m",
    }


def field_mask_metrics(model: Any, variables: dict[str, str], coords: dict[str, str]) -> dict[str, dict[str, Any]]:
    r_arr = np.asarray(model.evaluate(coords["radial"], unit="m"), dtype=float)
    z_arr = np.asarray(model.evaluate(coords["axial"], unit="m"), dtype=float)
    Ri = param_float(model, "Ri", "m")
    Ro = param_float(model, "Ro", "m")
    h = param_float(model, "h_ring", "m")
    finite = np.isfinite(r_arr) & np.isfinite(z_arr)
    ring_mask = finite & (r_arr >= Ri - 2 * h) & (r_arr <= Ro + 2 * h) & (z_arr >= -4 * h) & (z_arr <= 4 * h)
    center_mask = finite & (r_arr >= 0) & (r_arr <= Ri) & (z_arr >= 0) & (z_arr <= 4 * h)
    rows: dict[str, dict[str, Any]] = {}

    def masked_stat(metric: str, expr: str, unit: str, mask: np.ndarray, stat: str) -> None:
        try:
            values = np.asarray(model.evaluate(expr, unit=unit), dtype=float)
            data = values[mask & np.isfinite(values)]
            if data.size == 0:
                raise ValueError("mask contains no finite samples")
            if stat == "max":
                value = float(np.nanmax(data))
            elif stat == "mean":
                value = float(np.nanmean(data))
            else:
                raise ValueError(stat)
            rows[metric] = {
                "metric": metric,
                "expression": expr,
                "unit": unit,
                "value": value,
                "status": "ok",
                "method": "coordinate-masked field sampling over solved COMSOL data",
                "sample_count": int(data.size),
            }
        except Exception as exc:
            rows[metric] = {"metric": metric, "expression": expr, "unit": unit, "status": "failed", "error": str(exc)}

    masked_stat("p_max_ring_near", variables["pressure"], "Pa", ring_mask, "max")
    masked_stat("vz_max_center_above", variables["axial_velocity"], "m/s", center_mask, "max")
    masked_stat("vz_avg_hole_above", variables["axial_velocity"], "m/s", center_mask, "mean")
    rows["Q_axisym_hole_above"] = {
        "metric": "Q_axisym_hole_above",
        "status": "NA",
        "value": "NA",
        "method": "not used",
        "notes": "A reliable axisymmetric line integration requires a cut-line dataset or boundary-normal flux definition; not implemented for stage 2.1.",
    }
    return rows


def operator_metric(model: Any, metric: str, expression: str, unit: str, fallback_expression: str | None = None) -> dict[str, Any]:
    try:
        value = eval_scalar_max(model, expression, unit)
        return {"metric": metric, "expression": expression, "unit": unit, "value": value, "status": "ok", "method": "COMSOL coupling operator over full domain"}
    except Exception as exc:
        if fallback_expression is None:
            return {"metric": metric, "expression": expression, "unit": unit, "status": "failed", "error": str(exc), "method": "COMSOL coupling operator over full domain"}
        try:
            value = eval_scalar_max(model, fallback_expression, unit)
            return {
                "metric": metric,
                "expression": fallback_expression,
                "unit": unit,
                "value": value,
                "status": "ok",
                "method": "calibrated full-domain field sampling fallback",
                "operator_expression": expression,
                "operator_error": str(exc),
            }
        except Exception as fallback_exc:
            return {
                "metric": metric,
                "expression": expression,
                "fallback_expression": fallback_expression,
                "unit": unit,
                "status": "failed",
                "error": str(exc),
                "fallback_error": str(fallback_exc),
                "method": "COMSOL coupling operator with calibrated field fallback",
            }


def evaluate_calibrated_metrics(model: Any, variables: dict[str, str], coords: dict[str, str]) -> dict[str, Any]:
    rows: dict[str, dict[str, Any]] = {}
    rows["u_mag_max"] = operator_metric(
        model,
        "u_mag_max",
        f"rfmax_all({variables['velocity_magnitude']})",
        "m/s",
        variables["velocity_magnitude"],
    )
    rows["p_max_global"] = operator_metric(
        model,
        "p_max_global",
        f"rfmax_all({variables['pressure']})",
        "Pa",
        variables["pressure"],
    )
    rows.update(field_mask_metrics(model, variables, coords))
    return rows


def param_snapshot(model: Any) -> dict[str, Any]:
    params = model.parameters()
    row: dict[str, Any] = {}
    for key in ["Ro", "Ri", "h_ring", "U0", "Rtank", "Zup", "Zdown", "rho_w", "mu_w"]:
        row[key] = params.get(key)
    try:
        row["Ri_over_Ro"] = param_float(model, "Ri", "m") / param_float(model, "Ro", "m")
    except Exception:
        row["Ri_over_Ro"] = "NA"
    return row


def flatten_metric_row(model: Any, metrics: dict[str, dict[str, Any]]) -> dict[str, Any]:
    row = param_snapshot(model)
    for key in ["u_mag_max", "p_max_global", "p_max_ring_near", "vz_max_center_above", "vz_avg_hole_above", "Q_axisym_hole_above"]:
        item = metrics.get(key, {})
        row[key] = item.get("value", "NA") if item.get("status") in ["ok", "NA"] else "failed"
    return row


def write_report(path: Path, title: str, sections: list[str], data: Any | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", f"Run time: {datetime.now().isoformat(timespec='seconds')}", ""]
    lines.extend(sections)
    if data is not None:
        lines.extend(["", "## Structured Data", "", "```json", json.dumps(data, ensure_ascii=False, indent=2, default=str), "```"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_changelog(entry: str) -> None:
    changelog = ROOT / "CHANGELOG.md"
    with changelog.open("a", encoding="utf-8") as handle:
        handle.write("\n" + entry.rstrip() + "\n")


def update_readme(stage_status: dict[str, str]) -> None:
    readme = ROOT / "README.md"
    previous = readme.read_text(encoding="utf-8", errors="replace") if readme.exists() else "# COMSOL Ring Fountain Simulation\n"
    marker = "\n## Stage 2.1+ Continuation Status\n"
    preserved = previous.split(marker)[0].rstrip()
    lines = [
        preserved,
        marker.strip(),
        "",
        f"- Stage 2.1 metric calibration: `{stage_status.get('2.1', 'not_run')}`.",
        f"- Stage 2.2 clean one-dimensional sweep: `{stage_status.get('2.2', 'not_run')}`.",
        f"- Stage 2.3 clean sweep review: `{stage_status.get('2.3', 'not_run')}`.",
        f"- Stage 3 relative-flow model: `{stage_status.get('3', 'not_run')}`.",
        f"- Stage 4 moving-ring model: `{stage_status.get('4', 'not_run')}`.",
        f"- Stage 5 two-phase free-surface model: `{stage_status.get('5', 'not_run')}`.",
        "",
        "The old `02_param_sweep` results are retained as a preliminary automation test and are not used for final physical interpretation.",
        "The current single-phase stages still cannot output a true two-phase free-surface fountain height `Hmax`.",
        "",
        "New automation script: `D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\scripts\\ring_fountain_stage2_1_plus.py`.",
    ]
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")


def stage21_metric_calibration(client: Any) -> tuple[str, dict[str, Any], Path | None]:
    data: dict[str, Any] = {"stage": "2.1"}
    if not INPUT_CHECKED.exists():
        raise FileNotFoundError(INPUT_CHECKED)
    model = client.load(str(INPUT_CHECKED))
    out_model = STAGE21 / "models" / "ring_fountain_v0_metric_calibrated.mph"
    out_ts = STAGE21 / "models" / f"ring_fountain_v0_metric_calibrated_{RUN_ID}.mph"
    try:
        data["parameter_descriptions"] = set_parameter_descriptions(model)
        data["coupling_operators"] = ensure_coupling_ops(model)
        probe = variable_probe(model)
        data["variable_probe"] = probe
        chosen = probe["chosen"]
        required = ["velocity_magnitude", "pressure", "radial_coordinate", "axial_coordinate", "axial_velocity"]
        missing = [key for key in required if key not in chosen]
        coords = {"radial": chosen.get("radial_coordinate"), "axial": chosen.get("axial_coordinate")}
        variables = {
            "velocity_magnitude": chosen.get("velocity_magnitude"),
            "pressure": chosen.get("pressure"),
            "axial_velocity": chosen.get("axial_velocity"),
        }
        if missing:
            data["review"] = {"status": "FAIL", "missing": missing}
        else:
            data["coordinate_meaning"] = {
                "radial_coordinate": coords["radial"],
                "axial_coordinate": coords["axial"],
                "axisymmetric_interpretation": "2D axisymmetric r-z model; horizontal coordinate is radius, vertical coordinate is axial z.",
            }
            data["metric_regions"] = metric_conditions(model, coords)
            metrics = evaluate_calibrated_metrics(model, variables, coords)
            data["metrics"] = metrics
            table_row = flatten_metric_row(model, metrics)
            table_path = STAGE21 / "tables" / "metric_calibration_baseline.csv"
            write_csv(table_path, [table_row])
            write_xlsx(STAGE21 / "tables" / "metric_calibration_baseline.xlsx", [table_row])
            data["tables"] = [str(table_path), str(STAGE21 / "tables" / "metric_calibration_baseline.xlsx")]
            exports = [
                export_plot(model, "Velocity (spf)", STAGE21 / "images" / "metric_velocity_magnitude.png"),
                export_plot(model, "Pressure (spf)", STAGE21 / "images" / "metric_pressure.png"),
                create_vertical_velocity_plot(model, variables["axial_velocity"], STAGE21 / "images" / "metric_vertical_velocity.png"),
            ]
            make_schematic(STAGE21 / "images" / "metric_regions_schematic.png")
            exports.append({"ok": True, "plot": "metric regions schematic", "file": str(STAGE21 / "images" / "metric_regions_schematic.png")})
            data["images"] = exports
            model.save(out_model)
            model.save(out_ts)
            data["models"] = [str(out_model), str(out_ts)]

            pass_items = [
                Path(out_model).exists(),
                all(probe["chosen"].get(k) for k in ["velocity_magnitude", "pressure", "axial_velocity"]),
                metrics.get("u_mag_max", {}).get("status") == "ok",
                metrics.get("p_max_ring_near", {}).get("status") == "ok",
                metrics.get("vz_max_center_above", {}).get("status") == "ok",
            ]
            data["review"] = {"status": "PASS" if all(pass_items) else "PARTIAL_PASS", "checks": pass_items}
        status = data["review"]["status"]
        sections = [
            "## Review",
            "",
            f"Stage 2.1 review status: `{status}`.",
            "",
            "## Variable Confirmation",
            "",
            f"- Velocity magnitude: `{data.get('variable_probe', {}).get('chosen', {}).get('velocity_magnitude', 'NA')}`.",
            f"- Pressure: `{data.get('variable_probe', {}).get('chosen', {}).get('pressure', 'NA')}`.",
            f"- Vertical/axial velocity: `{data.get('variable_probe', {}).get('chosen', {}).get('axial_velocity', 'NA')}`.",
            "- Previous `v = 0` issue is resolved by selecting the nonzero axisymmetric axial component; in this model `w` is the meaningful vertical/axial velocity when available.",
            "",
            "## Metric Definitions",
            "",
            "- `u_mag_max`: COMSOL full-domain maximum of velocity magnitude.",
            "- `p_max_global`: COMSOL full-domain maximum pressure.",
            "- `p_max_ring_near`: coordinate-masked maximum pressure in a ring-near box, without boundary-ID guessing.",
            "- `vz_max_center_above`: coordinate-masked maximum axial velocity above the center hole.",
            "- `vz_avg_hole_above`: coordinate-masked average axial velocity above the center hole.",
            "- `Q_axisym_hole_above`: `NA`; a reliable 2*pi*r weighted line integration was not implemented in this stage.",
            "",
            "## Next Gate",
            "",
            "Proceed to stage 2.2 only if this review is `PASS`.",
        ]
        write_report(STAGE21 / "reports" / "metric_calibration_report.md", "Stage 2.1 Metric Calibration Report", sections, data)
        return status, data, out_model if status == "PASS" else None
    finally:
        try:
            client.remove(model)
        except Exception:
            pass


def reset_base_params(model: Any) -> None:
    for name, value in BASE_PARAMS.items():
        model.parameter(name, value)


def stage22_clean_sweep(client: Any, input_model: Path, calibration_data: dict[str, Any]) -> tuple[str, dict[str, Any], Path | None]:
    data: dict[str, Any] = {"stage": "2.2"}
    model = client.load(str(input_model))
    out_model = STAGE22 / "models" / "ring_fountain_v1_clean_param_sweep.mph"
    out_ts = STAGE22 / "models" / f"ring_fountain_v1_clean_param_sweep_{RUN_ID}.mph"
    rows: list[dict[str, Any]] = []
    try:
        probe = variable_probe(model)
        chosen = probe["chosen"]
        coords = {"radial": chosen["radial_coordinate"], "axial": chosen["axial_coordinate"]}
        variables = {
            "velocity_magnitude": chosen["velocity_magnitude"],
            "pressure": chosen["pressure"],
            "axial_velocity": chosen["axial_velocity"],
        }
        sweep_cases = [
            ("U0_sweep", "U0_001", "U0", "0.01[m/s]", 0.01),
            ("U0_sweep", "U0_002", "U0", "0.02[m/s]", 0.02),
            ("U0_sweep", "U0_005", "U0", "0.05[m/s]", 0.05),
            ("U0_sweep", "U0_010", "U0", "0.10[m/s]", 0.10),
            ("h_ring_sweep", "h_001", "h_ring", "1[mm]", 1.0),
            ("h_ring_sweep", "h_002", "h_ring", "2[mm]", 2.0),
            ("h_ring_sweep", "h_004", "h_ring", "4[mm]", 4.0),
            ("Ri_Ro_sweep", "ri_006", "Ri", "6[mm]", 0.3),
            ("Ri_Ro_sweep", "ri_008", "Ri", "8[mm]", 0.4),
            ("Ri_Ro_sweep", "ri_010", "Ri", "10[mm]", 0.5),
            ("Ri_Ro_sweep", "ri_012", "Ri", "12[mm]", 0.6),
        ]
        for group, case_id, parameter, value, numeric_value in sweep_cases:
            row: dict[str, Any] = {"sweep_group": group, "case_id": case_id, "parameter_changed": parameter, "parameter_value": value}
            try:
                reset_base_params(model)
                model.parameter(parameter, value)
                row["control_reset"] = "base parameters reset before case"
                row["notes"] = ""
                log(f"Stage 2.2 solve {case_id}: {parameter}={value}")
                try:
                    model.solve()
                    row["solve_status"] = "ok"
                except Exception as exc:
                    row["solve_status"] = "failed"
                    row["notes"] = str(exc)
                metrics = evaluate_calibrated_metrics(model, variables, coords)
                row.update(param_snapshot(model))
                for key in ["u_mag_max", "p_max_global", "p_max_ring_near", "vz_max_center_above", "vz_avg_hole_above", "Q_axisym_hole_above"]:
                    item = metrics.get(key, {})
                    row[key] = item.get("value", "NA") if item.get("status") in ["ok", "NA"] else "failed"
                if group == "U0_sweep":
                    row["x_value"] = numeric_value
                elif group == "h_ring_sweep":
                    row["x_value"] = numeric_value
                elif group == "Ri_Ro_sweep":
                    row["x_value"] = numeric_value
                rows.append(row)
            except Exception as exc:
                row["solve_status"] = "failed"
                row["notes"] = str(exc)
                rows.append(row)

        csv_path = STAGE22 / "tables" / "clean_param_sweep_results.csv"
        xlsx_path = STAGE22 / "tables" / "clean_param_sweep_results.xlsx"
        write_csv(csv_path, rows)
        write_xlsx(xlsx_path, rows)
        data["tables"] = [str(csv_path), str(xlsx_path)]

        image_specs = [
            ("U0_sweep", "U0_vs_vz_max_center_above.png", "U0 vs vz_max_center_above", "vz_max_center_above"),
            ("U0_sweep", "U0_vs_p_max_ring_near.png", "U0 vs p_max_ring_near", "p_max_ring_near"),
            ("h_ring_sweep", "h_ring_vs_vz_max_center_above.png", "h_ring vs vz_max_center_above", "vz_max_center_above"),
            ("h_ring_sweep", "h_ring_vs_p_max_ring_near.png", "h_ring vs p_max_ring_near", "p_max_ring_near"),
            ("Ri_Ro_sweep", "Ri_over_Ro_vs_vz_max_center_above.png", "Ri/Ro vs vz_max_center_above", "vz_max_center_above"),
            ("Ri_Ro_sweep", "Ri_over_Ro_vs_p_max_ring_near.png", "Ri/Ro vs p_max_ring_near", "p_max_ring_near"),
        ]
        images = []
        for group, filename, title, y_key in image_specs:
            subset = [row for row in rows if row.get("sweep_group") == group]
            path = STAGE22 / "images" / filename
            ok = make_line_chart(path, title, subset, "x_value", y_key)
            images.append({"file": str(path), "ok": ok, "group": group, "metric": y_key})
        data["images"] = images
        model.save(out_model)
        model.save(out_ts)
        data["models"] = [str(out_model), str(out_ts)]
        data["rows"] = rows

        all_solved = all(row.get("solve_status") == "ok" for row in rows) and len(rows) == 11
        metrics_ok = all(str(row.get("vz_max_center_above")) not in ["failed", "NA", ""] and str(row.get("p_max_ring_near")) not in ["failed", "NA", ""] for row in rows)
        images_ok = all(item["ok"] for item in images)
        status = "PASS" if all_solved and metrics_ok and images_ok else "PARTIAL_PASS"
        data["review"] = {"status": status, "all_solved": all_solved, "metrics_ok": metrics_ok, "images_ok": images_ok}
        sections = [
            "## Review",
            "",
            f"Stage 2.2 review status: `{status}`.",
            "",
            "This clean sweep differs from the previous preliminary sweep because every case resets the full baseline parameter set before changing exactly one parameter.",
            "",
            "The results are still single-phase fixed-ring intermediate indicators. They cannot output a true free-surface fountain height `Hmax`.",
        ]
        write_report(STAGE22 / "reports" / "clean_param_sweep_report.md", "Stage 2.2 Clean Parameter Sweep Report", sections, data)
        return status, data, out_model if status == "PASS" else None
    finally:
        try:
            client.remove(model)
        except Exception:
            pass


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def stage23_review(clean_data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    clean_rows = read_csv_rows(STAGE22 / "tables" / "clean_param_sweep_results.csv")
    old_rows = read_csv_rows(OLD_SWEEP)
    data = {
        "stage": "2.3",
        "clean_rows": len(clean_rows),
        "old_rows": len(old_rows),
        "old_preliminary_label": "preliminary automation test; not used for final physical interpretation",
        "clean_sweep_source": str(STAGE22 / "tables" / "clean_param_sweep_results.csv"),
    }
    rows_ok = len(clean_rows) == 11 and all(row.get("solve_status") == "ok" for row in clean_rows)
    data["review"] = {"status": "PASS" if rows_ok else "PARTIAL_PASS", "clean_rows_ok": rows_ok}
    status = data["review"]["status"]
    sections = [
        "## Review",
        "",
        f"Stage 2.3 review status: `{status}`.",
        "",
        "## Preliminary Sweep Downgrade",
        "",
        "The old `02_param_sweep/tables/param_sweep_results.csv` is retained but explicitly downgraded to a preliminary automation test. It is not used for final physical interpretation.",
        "",
        "Main issues in the old sweep:",
        "",
        "- Control variables were not reset from a common baseline before every case.",
        "- Metric extraction used ambiguous Python field-array maxima before variable direction was calibrated.",
        "- The vertical velocity direction was not yet confirmed; the zero `v` result was misleading.",
        "",
        "## Current Single-Phase Assumptions",
        "",
        "The trusted clean result remains a 2D axisymmetric, single-phase, fixed-ring Laminar Flow model. It is useful for comparing velocity and pressure concentration trends, but it cannot directly produce a real free-surface `Hmax`.",
        "",
        "Proceed to stage 3 only if this review is `PASS`.",
    ]
    write_report(STAGE23 / "reports" / "param_sweep_clean_review.md", "Stage 2.3 Clean Sweep Review", sections, data)
    summary = [
        "# 阶段 2.3 中文摘要",
        "",
        f"Review 结果：`{status}`。",
        "",
        "旧的 `02_param_sweep` 结果已降级标注为 preliminary automation test，不作为正式物理解释。",
        "新的 clean sweep 每个算例都从同一组基准参数恢复，只改变一个控制变量，因此当前更可信。",
        "当前模型仍是单相、固定圆环、轴对称层流模型，不能直接给出真实两相自由液面的 `Hmax`。",
    ]
    (STAGE23 / "reports" / "param_sweep_clean_summary_cn.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    return status, data


def stage3_relative_flow(client: Any, input_model: Path) -> tuple[str, dict[str, Any], Path | None]:
    model = client.load(str(input_model))
    out_model = STAGE3 / "models" / "ring_fountain_v2_relative_flow.mph"
    out_ts = STAGE3 / "models" / f"ring_fountain_v2_relative_flow_{RUN_ID}.mph"
    data: dict[str, Any] = {"stage": "3"}
    try:
        for name, value in {
            "H_drop": "50[mm]",
            "g_const": "9.81[m/s^2]",
            "U_impact": "sqrt(2*g_const*H_drop)",
        }.items():
            model.parameter(name, value)
        probe = variable_probe(model)
        chosen = probe["chosen"]
        coords = {"radial": chosen["radial_coordinate"], "axial": chosen["axial_coordinate"]}
        variables = {
            "velocity_magnitude": chosen["velocity_magnitude"],
            "pressure": chosen["pressure"],
            "axial_velocity": chosen["axial_velocity"],
        }
        metrics = evaluate_calibrated_metrics(model, variables, coords)
        vz = metrics["vz_max_center_above"]["value"] if metrics["vz_max_center_above"]["status"] == "ok" else None
        g = eval_scalar_mean(model, "g_const", "m/s^2")
        try:
            H_drop_value = eval_scalar_mean(model, "H_drop", "m")
        except Exception:
            H_drop_value = 0.05
        U_impact = math.sqrt(2 * g * H_drop_value)
        H_kin_proxy = float(vz) ** 2 / (2 * g) if vz is not None else "NA"
        row = {
            "H_drop": "50[mm]",
            "U0": model.parameters().get("U0"),
            "U_impact_m_per_s": U_impact,
            "vz_max_center_above_m_per_s": vz,
            "H_kin_proxy_m": H_kin_proxy,
            "model_type": "single-phase fixed-ring relative-flow proxy",
            "notes": "H_kin_proxy is not true two-phase free-surface Hmax.",
        }
        write_csv(STAGE3 / "tables" / "H_kin_proxy_estimate.csv", [row])
        write_xlsx(STAGE3 / "tables" / "H_kin_proxy_estimate.xlsx", [row])
        images = [
            export_plot(model, "Velocity (spf)", STAGE3 / "images" / "relative_velocity.png"),
            export_plot(model, "Pressure (spf)", STAGE3 / "images" / "relative_pressure.png"),
            create_vertical_velocity_plot(model, variables["axial_velocity"], STAGE3 / "images" / "relative_vertical_velocity.png"),
        ]
        model.save(out_model)
        model.save(out_ts)
        data.update({"models": [str(out_model), str(out_ts)], "metrics": metrics, "H_kin_proxy": row, "images": images})
        images_ok = all(item.get("ok") for item in images)
        status = "PASS" if out_model.exists() and vz is not None and images_ok else "PARTIAL_PASS"
        data["review"] = {"status": status, "images_ok": images_ok}
        sections = [
            "## Review",
            "",
            f"Stage 3 review status: `{status}`.",
            "",
            "This model is not a laboratory-frame falling ring. It is a fixed-ring reference-frame relative-flow approximation.",
            "`U0` remains an independent relative incoming velocity parameter. `U_impact = sqrt(2*g_const*H_drop)` is added only as a scale comparison.",
            "`H_kin_proxy = vz_max_center_above^2/(2*g_const)` is a kinetic-height proxy, not the true two-phase free-surface `Hmax`.",
        ]
        write_report(STAGE3 / "reports" / "relative_flow_model_report.md", "Stage 3 Relative Flow Model Report", sections, data)
        return status, data, out_model if status == "PASS" else None
    finally:
        try:
            client.remove(model)
        except Exception:
            pass


def stage4_attempt(client: Any, input_model: Path) -> tuple[str, dict[str, Any]]:
    model = client.load(str(input_model))
    out_model = STAGE4 / "models" / "ring_fountain_v3_moving_ring.mph"
    out_ts = STAGE4 / "models" / f"ring_fountain_v3_moving_ring_{RUN_ID}.mph"
    data: dict[str, Any] = {"stage": "4"}
    try:
        model.parameter("V_ring", "0.10[m/s]")
        model.parameter("t_end_move", "0.02[s]")
        # Stop before modifying Wall/ALE features.  The ring boundary selection
        # needs GUI/API confirmation before it can be used as a moving wall.
        model.save(out_model)
        model.save(out_ts)
        data["models"] = [str(out_model), str(out_ts)]
        data["review"] = {
            "status": "FAIL",
            "reason": "Automation did not safely confirm the ring moving-wall boundary selection or wall movement property names; physics was not altered.",
            "no_stage5": True,
        }
        sections = [
            "## Review",
            "",
            "Stage 4 review status: `FAIL`.",
            "",
            "A stage-4 copy was saved with conservative motion parameters `V_ring` and `t_end_move`, but no moving-wall or ALE physics was applied.",
            "Reason: the automation could not safely confirm the ring boundary selection and COMSOL wall-movement property names without risking an incorrect physical model.",
            "Because stage 4 is `FAIL`, stage 5 two-phase free-surface modeling is not attempted in this run.",
        ]
        write_report(STAGE4 / "reports" / "moving_ring_model_report.md", "Stage 4 Moving Ring Model Report", sections, data)
        return "FAIL", data
    finally:
        try:
            client.remove(model)
        except Exception:
            pass


def final_status_report(statuses: dict[str, str], records: dict[str, Any]) -> None:
    append_changelog(
        f"""## {datetime.now().isoformat(timespec='seconds')} - Stage 2.1+ continuation

- Stage 2.1 metric calibration: {statuses.get('2.1')}.
- Stage 2.2 clean parameter sweep: {statuses.get('2.2')}.
- Stage 2.3 clean sweep review: {statuses.get('2.3')}.
- Stage 3 relative-flow model: {statuses.get('3')}.
- Stage 4 moving-ring model: {statuses.get('4')}.
- Stage 5 two-phase free-surface model: {statuses.get('5', 'not_run')}.
- Old `02_param_sweep` results are retained as preliminary automation tests and not used for final physical interpretation.
"""
    )
    update_readme(statuses)
    (ROOT / "stage2_1_plus_run_summary.json").write_text(json.dumps({"statuses": statuses, "records": records}, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def main() -> None:
    os.environ["JAVA_HOME"] = r"D:\COMSOL64\Multiphysics\java\win64\jre"
    make_dirs()
    shutil.copy2(Path(__file__), SCRIPTS / "ring_fountain_stage2_1_plus.py")
    log("Starting Ring Fountain stage 2.1+ automation")

    import mph

    client = mph.Client(cores=2, version="6.4")
    log(f"COMSOL client started: version={client.version}, cores={client.cores}, standalone={client.standalone}")
    statuses: dict[str, str] = {}
    records: dict[str, Any] = {}
    try:
        status21, data21, model21 = stage21_metric_calibration(client)
        statuses["2.1"] = status21
        records["2.1"] = data21
        if status21 != "PASS" or model21 is None:
            statuses.update({"2.2": "not_run", "2.3": "not_run", "3": "not_run", "4": "not_run", "5": "not_run"})
            final_status_report(statuses, records)
            return

        status22, data22, model22 = stage22_clean_sweep(client, model21, data21)
        statuses["2.2"] = status22
        records["2.2"] = data22
        if status22 != "PASS" or model22 is None:
            statuses.update({"2.3": "not_run", "3": "not_run", "4": "not_run", "5": "not_run"})
            final_status_report(statuses, records)
            return

        status23, data23 = stage23_review(data22)
        statuses["2.3"] = status23
        records["2.3"] = data23
        if status23 != "PASS":
            statuses.update({"3": "not_run", "4": "not_run", "5": "not_run"})
            final_status_report(statuses, records)
            return

        status3, data3, model3 = stage3_relative_flow(client, model21)
        statuses["3"] = status3
        records["3"] = data3
        if status3 != "PASS" or model3 is None:
            statuses.update({"4": "not_run", "5": "not_run"})
            final_status_report(statuses, records)
            return

        status4, data4 = stage4_attempt(client, model3)
        statuses["4"] = status4
        records["4"] = data4
        statuses["5"] = "not_run"
        records["5"] = {"status": "not_run", "reason": "Stage 4 did not pass."}
        final_status_report(statuses, records)
    finally:
        try:
            client.clear()
        except Exception:
            pass
        log("Finished Ring Fountain stage 2.1+ automation")


if __name__ == "__main__":
    main()
