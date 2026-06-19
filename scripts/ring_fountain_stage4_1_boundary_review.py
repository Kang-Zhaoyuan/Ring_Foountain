# -*- coding: utf-8 -*-
"""Stage 4.1 boundary review package for the COMSOL Ring Fountain model.

This script intentionally stops before any moving-wall or wall-movement
physics is applied.  It only identifies the four candidate ring-wall
boundaries, creates a candidate named selection, and exports material for
manual review.
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


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
INPUT_MODEL = ROOT / "03_relative_flow_model" / "models" / "ring_fountain_v2_relative_flow.mph"
STAGE4 = ROOT / "04_moving_ring_model"
SCRIPTS = ROOT / "scripts"

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = STAGE4 / "logs" / f"stage4_1_boundary_review_{RUN_ID}.log"


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def make_dirs() -> None:
    for sub in ["models", "reports", "images", "tables", "logs"]:
        (STAGE4 / sub).mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)


def param_float(model: Any, expression: str, unit: str = "m") -> float:
    value = model.evaluate(expression, unit=unit)
    if hasattr(value, "flatten"):
        arr = value.flatten()
        return float(arr[0])
    return float(value)


def read_parameters(model: Any) -> dict[str, dict[str, Any]]:
    params = model.parameters()
    rows: dict[str, dict[str, Any]] = {}
    for name in ["Ri", "Ro", "h_ring", "Rtank", "Zup", "Zdown"]:
        rows[name] = {
            "expression": params.get(name),
            "value_m": param_float(model, name, "m"),
        }
    return rows


def numerical_values(model: Any, kind: str, boundary_id: int, expressions: list[str]) -> list[float]:
    nums = model.java.result().numerical()
    tag = nums.uniquetag("rfbnd")
    nums.create(tag, kind)
    node = nums.get(tag)
    jint_array = jpype.JArray(jpype.JInt)
    node.selection().geom("geom1", 1)
    node.selection().set(jint_array([boundary_id]))
    node.set("expr", expressions)
    try:
        values = []
        for arr in node.getReal():
            values.append(float(arr[0]) if len(arr) else math.nan)
        return values
    finally:
        nums.remove(tag)


def boundary_metrics(model: Any) -> list[dict[str, Any]]:
    n_boundaries = int(model.java.geom("geom1").getNBoundaries())
    rows: list[dict[str, Any]] = []
    for bid in range(1, n_boundaries + 1):
        length, int_r, int_z = numerical_values(model, "IntLine", bid, ["1", "r", "z"])
        r_max, z_max = numerical_values(model, "MaxLine", bid, ["r", "z"])
        r_min, z_min = numerical_values(model, "MinLine", bid, ["r", "z"])
        r_avg, z_avg = numerical_values(model, "AvLine", bid, ["r", "z"])
        rows.append({
            "boundary_id": bid,
            "length_m": length,
            "center_r_m": r_avg,
            "center_z_m": z_avg,
            "r_min_m": r_min,
            "r_max_m": r_max,
            "z_min_m": z_min,
            "z_max_m": z_max,
            "endpoint_1": [r_min, z_min],
            "endpoint_2": [r_max, z_max],
            "int_r": int_r,
            "int_z": int_z,
        })
    return rows


def classify_boundaries(rows: list[dict[str, Any]], params: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ri = params["Ri"]["value_m"]
    ro = params["Ro"]["value_m"]
    h = params["h_ring"]["value_m"]
    rtank = params["Rtank"]["value_m"]
    zup = params["Zup"]["value_m"]
    zdown = params["Zdown"]["value_m"]
    z_top = h / 2.0
    z_bottom = -h / 2.0
    horizontal_length = ro - ri
    vertical_length = h
    tol_pos = max(1e-7, h * 0.02, horizontal_length * 0.005)
    tol_len = max(1e-7, (2 * horizontal_length + 2 * h) * 0.01)

    def near(a: float, b: float, tol: float = tol_pos) -> bool:
        return abs(a - b) <= tol

    candidates: dict[str, dict[str, Any] | None] = {
        "inner_vertical_r_eq_Ri": None,
        "outer_vertical_r_eq_Ro": None,
        "top_horizontal_z_eq_plus_h_over_2": None,
        "bottom_horizontal_z_eq_minus_h_over_2": None,
    }

    scored: list[dict[str, Any]] = []
    for row in rows:
        bid = row["boundary_id"]
        r_min, r_max = row["r_min_m"], row["r_max_m"]
        z_min, z_max = row["z_min_m"], row["z_max_m"]
        length = row["length_m"]
        is_vertical = near(r_min, r_max) and abs(length - vertical_length) <= tol_len
        is_horizontal = near(z_min, z_max) and abs(length - horizontal_length) <= tol_len
        inside_tank = (
            r_min > tol_pos
            and r_max < rtank - tol_pos
            and z_min > -zdown + tol_pos
            and z_max < zup - tol_pos
        )
        row["inside_water_domain_not_outer_tank"] = inside_tank

        checks = {
            "inner_vertical_r_eq_Ri": is_vertical and inside_tank and near(r_min, ri) and near(r_max, ri) and near(z_min, z_bottom) and near(z_max, z_top),
            "outer_vertical_r_eq_Ro": is_vertical and inside_tank and near(r_min, ro) and near(r_max, ro) and near(z_min, z_bottom) and near(z_max, z_top),
            "top_horizontal_z_eq_plus_h_over_2": is_horizontal and inside_tank and near(z_min, z_top) and near(z_max, z_top) and near(r_min, ri) and near(r_max, ro),
            "bottom_horizontal_z_eq_minus_h_over_2": is_horizontal and inside_tank and near(z_min, z_bottom) and near(z_max, z_bottom) and near(r_min, ri) and near(r_max, ro),
        }
        for role, ok in checks.items():
            if ok:
                enriched = dict(row)
                enriched["candidate_role"] = role
                candidates[role] = enriched
                scored.append(enriched)

        row["candidate_match"] = ",".join(role for role, ok in checks.items() if ok)

    candidate_rows = [row for row in candidates.values() if row is not None]
    candidate_ids = sorted(int(row["boundary_id"]) for row in candidate_rows)
    total_length = sum(float(row["length_m"]) for row in candidate_rows)
    expected_length = 2 * (ro - ri) + 2 * h
    duplicate_free = len(candidate_ids) == len(set(candidate_ids))

    checks = {
        "candidate_count_is_4": len(candidate_rows) == 4 and duplicate_free,
        "total_length_close_to_theory": abs(total_length - expected_length) <= tol_len,
        "all_positions_match_theory": all(row is not None for row in candidates.values()),
        "all_candidates_are_internal_hole_boundaries": all(bool(row["inside_water_domain_not_outer_tank"]) for row in candidate_rows),
        "no_outer_tank_boundaries_selected": all(
            not (
                abs(row["r_min_m"]) <= tol_pos
                or abs(row["r_max_m"] - rtank) <= tol_pos
                or abs(row["z_min_m"] + zdown) <= tol_pos
                or abs(row["z_max_m"] - zup) <= tol_pos
            )
            for row in candidate_rows
        ),
    }

    return {
        "candidate_ids": candidate_ids,
        "roles": candidates,
        "checks": checks,
        "candidate_total_length_m": total_length,
        "theoretical_total_length_m": expected_length,
        "tolerance_position_m": tol_pos,
        "tolerance_length_m": tol_len,
    }


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
        text = json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else str(value)
        try:
            number = float(text)
            if math.isfinite(number) and text.strip() == text:
                return "", str(number)
        except Exception:
            pass
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        return ' t="inlineStr"', f"<is><t>{escaped}</t></is>"

    sheet_rows = []
    all_rows = [dict(zip(keys, keys))] + rows
    for r_index, row in enumerate(all_rows, start=1):
        cells = []
        for c_index, key in enumerate(keys):
            attrs, body = cell_xml(row.get(key, ""))
            cells.append(f'<c r="{col_name(c_index)}{r_index}"{attrs}>{body}</c>')
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
<sheets><sheet name="boundaries" sheetId="1" r:id="rId1"/></sheets></workbook>""")
        zf.writestr("xl/_rels/workbook.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>""")
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)


FONT = {
    "0": ["111", "101", "101", "101", "111"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"],
    "B": ["110", "101", "110", "101", "110"],
    "R": ["110", "101", "110", "101", "101"],
    "i": ["1", "0", "1", "1", "1"],
    "o": ["000", "111", "101", "101", "111"],
    "z": ["111", "001", "010", "100", "111"],
    "+": ["000", "010", "111", "010", "000"],
    "-": ["000", "000", "111", "000", "000"],
    "=": ["000", "111", "000", "111", "000"],
    ".": ["0", "0", "0", "0", "1"],
    "m": ["00000", "11010", "10101", "10101", "10101"],
    " ": ["0", "0", "0", "0", "0"],
}


def png_write(path: Path, width: int, height: int, pixels: bytearray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw.extend(pixels[y * stride:(y + 1) * stride])
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    path.write_bytes(png)


def draw_line(pixels: bytearray, width: int, height: int, p1: tuple[int, int], p2: tuple[int, int], color: tuple[int, int, int], thickness: int = 2) -> None:
    x1, y1 = p1
    x2, y2 = p2
    dx = abs(x2 - x1)
    dy = -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx + dy
    x, y = x1, y1
    while True:
        for ox in range(-thickness, thickness + 1):
            for oy in range(-thickness, thickness + 1):
                xx, yy = x + ox, y + oy
                if 0 <= xx < width and 0 <= yy < height:
                    i = (yy * width + xx) * 3
                    pixels[i:i + 3] = bytes(color)
        if x == x2 and y == y2:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def draw_text(pixels: bytearray, width: int, height: int, x: int, y: int, text: str, color: tuple[int, int, int], scale: int = 3) -> None:
    cursor = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    for sy in range(scale):
                        for sx in range(scale):
                            xx = cursor + gx * scale + sx
                            yy = y + gy * scale + sy
                            if 0 <= xx < width and 0 <= yy < height:
                                i = (yy * width + xx) * 3
                                pixels[i:i + 3] = bytes(color)
        cursor += (len(glyph[0]) + 1) * scale


def draw_boundary_image(path: Path, rows: list[dict[str, Any]], candidate_ids: list[int], title: str, zoom: tuple[float, float, float, float], highlight_only: bool = False) -> None:
    width, height = 1200, 900
    bg = (248, 248, 244)
    pixels = bytearray(bg * (width * height))
    margin = 90
    r_min, r_max, z_min, z_max = zoom
    span_r = r_max - r_min
    span_z = z_max - z_min

    def tr(r: float, z: float) -> tuple[int, int]:
        x = margin + int((r - r_min) / span_r * (width - 2 * margin))
        y = height - margin - int((z - z_min) / span_z * (height - 2 * margin))
        return x, y

    draw_text(pixels, width, height, 32, 28, title, (45, 45, 45), 3)
    for row in rows:
        bid = int(row["boundary_id"])
        p1 = tr(float(row["r_min_m"]), float(row["z_min_m"]))
        p2 = tr(float(row["r_max_m"]), float(row["z_max_m"]))
        is_candidate = bid in candidate_ids
        if highlight_only and not is_candidate:
            color = (190, 190, 185)
            thickness = 1
        else:
            color = (210, 50, 45) if is_candidate else (60, 85, 120)
            thickness = 4 if is_candidate else 2
        draw_line(pixels, width, height, p1, p2, color, thickness)
        if not highlight_only or is_candidate:
            cx = (p1[0] + p2[0]) // 2
            cy = (p1[1] + p2[1]) // 2
            label = f"B{bid}"
            draw_text(pixels, width, height, cx + 8, cy - 10, label, (10, 10, 10), 4 if is_candidate else 3)

    png_write(path, width, height, pixels)


def create_candidate_selection(model: Any, candidate_ids: list[int]) -> str:
    selections = model.java.component("comp1").selection()
    tag = "sel_ring_wall_candidate"
    if tag in list(selections.tags()):
        selections.remove(tag)
    selections.create(tag, "Explicit")
    node = selections.get(tag)
    node.label("Ring wall candidate boundaries for manual review")
    node.geom("geom1", 1)
    jint_array = jpype.JArray(jpype.JInt)
    node.set(jint_array(candidate_ids))
    return tag


def write_report(path: Path, params: dict[str, dict[str, Any]], rows: list[dict[str, Any]], classification: dict[str, Any], outputs: dict[str, Any]) -> None:
    candidate_ids = classification["candidate_ids"]
    roles = classification["roles"]
    checks = classification["checks"]
    lines: list[str] = [
        "# Stage 4.1 Ring Boundary Manual Review Package",
        "",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This package only identifies candidate ring-wall boundaries and creates `sel_ring_wall_candidate` for manual review. No moving-wall, wall-movement, ALE, or time-dependent motion setting has been applied.",
        "",
        "## 候选圆环边界编号：",
        "",
        f"`{candidate_ids}`",
        "",
        "Role mapping:",
    ]
    for role, row in roles.items():
        if row is None:
            lines.append(f"- `{role}`: NOT FOUND")
        else:
            lines.append(f"- `{role}`: boundary `{row['boundary_id']}`")

    lines += [
        "",
        "## 候选边界坐标：",
        "",
        "| role | boundary | center (r,z) m | endpoint/range 1 m | endpoint/range 2 m |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for role, row in roles.items():
        if row is not None:
            lines.append(
                f"| `{role}` | {row['boundary_id']} | "
                f"({row['center_r_m']:.9g}, {row['center_z_m']:.9g}) | "
                f"({row['r_min_m']:.9g}, {row['z_min_m']:.9g}) | "
                f"({row['r_max_m']:.9g}, {row['z_max_m']:.9g}) |"
            )

    lines += [
        "",
        "## 候选边界长度：",
        "",
        "| role | boundary | length m | length mm |",
        "| --- | ---: | ---: | ---: |",
    ]
    for role, row in roles.items():
        if row is not None:
            lines.append(f"| `{role}` | {row['boundary_id']} | {row['length_m']:.9g} | {row['length_m'] * 1000:.6g} |")

    ri = params["Ri"]["value_m"]
    ro = params["Ro"]["value_m"]
    h = params["h_ring"]["value_m"]
    lines += [
        "",
        "## 理论圆环边界位置：",
        "",
        f"- `Ri = {ri:.9g} m`",
        f"- `Ro = {ro:.9g} m`",
        f"- `h_ring = {h:.9g} m`",
        f"- Inner side: `r = Ri = {ri:.9g} m`, `z in [{-h/2:.9g}, {h/2:.9g}] m`",
        f"- Outer side: `r = Ro = {ro:.9g} m`, `z in [{-h/2:.9g}, {h/2:.9g}] m`",
        f"- Top side: `z = +h_ring/2 = {h/2:.9g} m`, `r in [{ri:.9g}, {ro:.9g}] m`",
        f"- Bottom side: `z = -h_ring/2 = {-h/2:.9g} m`, `r in [{ri:.9g}, {ro:.9g}] m`",
        f"- Theoretical 2D perimeter: `{classification['theoretical_total_length_m']:.9g} m`",
        f"- Candidate summed length: `{classification['candidate_total_length_m']:.9g} m`",
        "",
        "## 几何一致性检查：",
        "",
    ]
    for key, value in checks.items():
        lines.append(f"- `{key}`: `{value}`")

    lines += [
        "",
        "## 全部 boundary 导出：",
        "",
        "| boundary | center (r,z) m | endpoint/range 1 m | endpoint/range 2 m | length m | candidate match | internal hole? |",
        "| ---: | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['boundary_id']} | ({row['center_r_m']:.9g}, {row['center_z_m']:.9g}) | "
            f"({row['r_min_m']:.9g}, {row['z_min_m']:.9g}) | "
            f"({row['r_max_m']:.9g}, {row['z_max_m']:.9g}) | {row['length_m']:.9g} | "
            f"`{row.get('candidate_match', '')}` | `{row.get('inside_water_domain_not_outer_tank', False)}` |"
        )

    lines += [
        "",
        "## 输出文件：",
        "",
        f"- Boundary table CSV: `{outputs['boundary_csv']}`",
        f"- Boundary table XLSX: `{outputs['boundary_xlsx']}`",
        f"- Review model with `sel_ring_wall_candidate`: `{outputs['model']}`",
        f"- Timestamp model: `{outputs['timestamp_model']}`",
        f"- Full boundary ID image: `{outputs['full_image']}`",
        f"- Ring-local boundary ID image: `{outputs['local_image']}`",
        f"- Candidate-highlight image: `{outputs['highlight_image']}`",
        "",
        "## 需要用户确认的问题：",
        "",
        "请人工确认：这些边界是否确实是圆环表面？",
        "",
        "如果确认，请回复：",
        "",
        f"`人工确认通过，圆环边界为：{candidate_ids}，可以继续阶段 4.2。`",
        "",
        "如果不确认，请指出错误边界编号或上传截图。",
        "",
        "## Structured Data",
        "",
        "```json",
        json.dumps({
            "stage": "4.1",
            "status": "AWAITING_MANUAL_CONFIRMATION",
            "candidate_ids": candidate_ids,
            "checks": checks,
            "outputs": outputs,
        }, ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    make_dirs()
    log("Stage 4.1 boundary review package started.")
    shutil.copy2(Path(__file__), SCRIPTS / "ring_fountain_stage4_1_boundary_review.py")

    client = mph.Client(cores=2, version="6.4")
    try:
        if not INPUT_MODEL.exists():
            raise FileNotFoundError(str(INPUT_MODEL))
        log(f"Loading model: {INPUT_MODEL}")
        model = client.load(INPUT_MODEL)

        params = read_parameters(model)
        log(f"Parameters: {json.dumps(params, ensure_ascii=False)}")

        rows = boundary_metrics(model)
        classification = classify_boundaries(rows, params)
        candidate_ids = classification["candidate_ids"]
        log(f"Candidate boundary IDs: {candidate_ids}")

        csv_path = STAGE4 / "tables" / "ring_boundary_all_boundaries.csv"
        xlsx_path = STAGE4 / "tables" / "ring_boundary_all_boundaries.xlsx"
        write_csv(csv_path, rows)
        write_xlsx(xlsx_path, rows)

        selection_tag = create_candidate_selection(model, candidate_ids)
        log(f"Created named selection: {selection_tag}")

        full_image = STAGE4 / "images" / "ring_boundary_full_model_ids.png"
        local_image = STAGE4 / "images" / "ring_boundary_local_ids.png"
        highlight_image = STAGE4 / "images" / "ring_boundary_candidate_highlight.png"
        rtank = params["Rtank"]["value_m"]
        zup = params["Zup"]["value_m"]
        zdown = params["Zdown"]["value_m"]
        ri = params["Ri"]["value_m"]
        ro = params["Ro"]["value_m"]
        h = params["h_ring"]["value_m"]
        draw_boundary_image(full_image, rows, candidate_ids, "Full model boundary IDs", (-0.005, rtank * 1.05, -zdown * 1.05, zup * 1.05), False)
        draw_boundary_image(local_image, rows, candidate_ids, "Ring-local boundary IDs", (ri - 0.006, ro + 0.006, -h * 4.0, h * 4.0), False)
        draw_boundary_image(highlight_image, rows, candidate_ids, "sel_ring_wall_candidate", (ri - 0.006, ro + 0.006, -h * 4.0, h * 4.0), True)

        out_model = STAGE4 / "models" / "ring_fountain_v3_boundary_review_package.mph"
        out_ts = STAGE4 / "models" / f"ring_fountain_v3_boundary_review_package_{RUN_ID}.mph"
        model.save(out_model)
        model.save(out_ts)

        outputs = {
            "boundary_csv": str(csv_path),
            "boundary_xlsx": str(xlsx_path),
            "model": str(out_model),
            "timestamp_model": str(out_ts),
            "full_image": str(full_image),
            "local_image": str(local_image),
            "highlight_image": str(highlight_image),
            "report": str(STAGE4 / "reports" / "ring_boundary_manual_review_package.md"),
            "log": str(LOG),
        }
        write_report(STAGE4 / "reports" / "ring_boundary_manual_review_package.md", params, rows, classification, outputs)

        summary = {
            "stage": "4.1",
            "status": "AWAITING_MANUAL_CONFIRMATION",
            "run_id": RUN_ID,
            "input_model": str(INPUT_MODEL),
            "candidate_ids": candidate_ids,
            "classification": classification,
            "parameters": params,
            "outputs": outputs,
            "note": "No moving-wall, wall-movement, ALE, or time-dependent motion setting has been applied.",
        }
        (STAGE4 / "stage4_1_boundary_review_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        log("Stage 4.1 completed; awaiting manual confirmation.")
    except Exception as exc:
        log(f"Stage 4.1 failed: {exc}")
        with LOG.open("a", encoding="utf-8") as handle:
            handle.write(traceback.format_exc() + "\n")
        raise
    finally:
        client.clear()


if __name__ == "__main__":
    main()
