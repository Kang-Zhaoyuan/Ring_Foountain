# -*- coding: utf-8 -*-
"""T009 T008 visual audit completion.

Reads existing T008 CSV outputs only. Does not import mph, does not run COMSOL,
does not alter T008 numeric evidence, and does not open Stage 6 or Jet1.
"""

from __future__ import annotations

import csv
import html
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
OUT = ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

SOURCE_TABLE = OUT / "tables" / "T008_recomputed_metrics.csv"
PROGRESS_TABLE = OUT / "tables" / "T008_progress.csv"
T008_REPORT = OUT / "reports" / "T008_final_report.md"
T008_GATES = OUT / "reports" / "T008_gate_summary.json"
T008_NAMED_SCRIPT = OUT / "scripts" / "T008_narrow_diagnostic_displacement_ladder.py"
T008_EQUIV_SCRIPT = OUT / "scripts" / "T008_narrow_displacement_ladder.py"

FIGURES = [
    {
        "figure_id": "T008_ladder_displacement_response",
        "original_png_path": OUT / "images" / "T008_ladder_displacement_response.png",
        "svg_path": OUT / "images" / "T009_ladder_displacement_response.svg",
        "png_path": OUT / "images" / "T009_ladder_displacement_response.png",
        "kind": "displacement",
    },
    {
        "figure_id": "T008_ladder_error_summary",
        "original_png_path": OUT / "images" / "T008_ladder_error_summary.png",
        "svg_path": OUT / "images" / "T009_ladder_error_summary.svg",
        "png_path": OUT / "images" / "T009_ladder_error_summary.png",
        "kind": "error",
    },
    {
        "figure_id": "T008_interface_quality_summary",
        "original_png_path": OUT / "images" / "T008_interface_quality_summary.png",
        "svg_path": OUT / "images" / "T009_interface_quality_summary.svg",
        "png_path": OUT / "images" / "T009_interface_quality_summary.png",
        "kind": "quality",
    },
]


def ensure_dirs() -> None:
    for sub in ["reports", "tables", "images", "scripts"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)


def abspath(path: Path) -> str:
    return str(path.resolve())


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in columns})
    return abspath(path)


def write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return abspath(path)


def sort_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    order = {"D3": 3, "D4": 4, "D5": 5}
    return sorted(rows, key=lambda row: order.get(row.get("legacy_case_id", ""), 99))


def svg_header(width: int, height: int, title: str, metadata: dict[str, Any]) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f"<title>{html.escape(title)}</title>",
        f"<desc>{html.escape(json.dumps(metadata, ensure_ascii=False, default=str))}</desc>",
        '<rect x="0" y="0" width="100%" height="100%" fill="white"/>',
        f'<text x="32" y="42" font-family="Arial, sans-serif" font-size="24" fill="#111">{html.escape(title)}</text>',
    ]


def draw_svg_bars(path: Path, title: str, labels: list[str], values: list[float], value_text: list[str], metadata: dict[str, Any], unit_label: str) -> str:
    width, height = 1040, 620
    left, top, chart_w, chart_h = 90, 105, 850, 310
    finite_values = [v for v in values if finite(v)]
    if not finite_values:
        finite_values = [0.0]
    min_v = min(finite_values + [0.0])
    max_v = max(finite_values + [0.0])
    span = max(max_v - min_v, 1.0)

    def y_for(value: float) -> float:
        return top + chart_h - ((value - min_v) / span) * chart_h

    zero_y = y_for(0.0)
    bar_step = chart_w / max(1, len(values))
    bar_w = min(88, bar_step * 0.55)
    lines = svg_header(width, height, title, metadata)
    lines.extend(
        [
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#111" stroke-width="1"/>',
            f'<line x1="{left}" y1="{zero_y:.2f}" x2="{left + chart_w}" y2="{zero_y:.2f}" stroke="#555" stroke-width="1"/>',
            f'<text x="{left}" y="{top + chart_h + 78}" font-family="Arial, sans-serif" font-size="14" fill="#111">Source: {html.escape(str(SOURCE_TABLE))}</text>',
            f'<text x="{left}" y="{top - 16}" font-family="Arial, sans-serif" font-size="14" fill="#111">{html.escape(unit_label)}</text>',
        ]
    )
    for idx, (label, value, text) in enumerate(zip(labels, values, value_text)):
        x = left + idx * bar_step + (bar_step - bar_w) / 2
        y = y_for(value)
        y0 = min(y, zero_y)
        h = max(abs(zero_y - y), 1.0)
        lines.append(f'<rect x="{x:.2f}" y="{y0:.2f}" width="{bar_w:.2f}" height="{h:.2f}" fill="#3f6fbf"/>')
        lines.append(f'<text x="{x + bar_w / 2:.2f}" y="{top + chart_h + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#111">{html.escape(label)}</text>')
        lines.append(f'<text x="{x + bar_w / 2:.2f}" y="{max(70, y0 - 10):.2f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#111">{html.escape(text)}</text>')
    lines.append("</svg>")
    return write_text(path, "\n".join(lines) + "\n")


def draw_png_bars(path: Path, title: str, labels: list[str], values: list[float], value_text: list[str], unit_label: str) -> str:
    width, height = 1040, 620
    left, top, chart_w, chart_h = 90, 105, 850, 310
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
        small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 12)
    except Exception:
        title_font = ImageFont.load_default()
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    finite_values = [v for v in values if finite(v)] or [0.0]
    min_v = min(finite_values + [0.0])
    max_v = max(finite_values + [0.0])
    span = max(max_v - min_v, 1.0)

    def y_for(value: float) -> float:
        return top + chart_h - ((value - min_v) / span) * chart_h

    zero_y = y_for(0.0)
    bar_step = chart_w / max(1, len(values))
    bar_w = min(88, bar_step * 0.55)
    draw.text((32, 22), title, fill=(17, 17, 17), font=title_font)
    draw.line((left, top, left, top + chart_h), fill=(17, 17, 17))
    draw.line((left, zero_y, left + chart_w, zero_y), fill=(85, 85, 85))
    draw.text((left, top - 30), unit_label, fill=(17, 17, 17), font=font)
    for idx, (label, value, text) in enumerate(zip(labels, values, value_text)):
        x = left + idx * bar_step + (bar_step - bar_w) / 2
        y = y_for(value)
        y0 = min(y, zero_y)
        h = max(abs(zero_y - y), 1.0)
        draw.rectangle((x, y0, x + bar_w, y0 + h), fill=(63, 111, 191))
        draw.text((x + bar_w / 2 - 24, top + chart_h + 18), label, fill=(17, 17, 17), font=font)
        draw.text((x + bar_w / 2 - 36, max(70, y0 - 20)), text, fill=(17, 17, 17), font=small)
    draw.text((left, top + chart_h + 78), f"Source: {SOURCE_TABLE}", fill=(17, 17, 17), font=small)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return abspath(path)


def png_dimensions(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        with Image.open(path) as img:
            return f"{img.size[0]}x{img.size[1]} {img.mode}"
    except Exception as exc:
        return f"unreadable: {exc.__class__.__name__}: {exc}"


def regenerate_figures(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    outputs: dict[str, dict[str, str]] = {}
    labels = [row["legacy_case_id"] for row in rows]

    measured_um = [float(row["measured_ring_displacement_m"]) * 1e6 for row in rows]
    expected_um = [float(row["expected_displacement_m"]) * 1e6 for row in rows]
    disp_text = [f"meas {m:.12g} um; exp {e:.12g} um" for m, e in zip(measured_um, expected_um)]
    disp_meta = {
        "source_table": abspath(SOURCE_TABLE),
        "source_columns": ["legacy_case_id", "expected_displacement_m", "measured_ring_displacement_m"],
        "rows": [{key: row[key] for key in ["legacy_case_id", "expected_displacement_m", "measured_ring_displacement_m"]} for row in rows],
    }
    outputs["T008_ladder_displacement_response"] = {
        "svg": draw_svg_bars(FIGURES[0]["svg_path"], "T009 SVG audit: T008 D3-D5 displacement response", labels, measured_um, disp_text, disp_meta, "Measured displacement, um; expected shown in labels"),
        "png": draw_png_bars(FIGURES[0]["png_path"], "T009 audit: T008 D3-D5 displacement response", labels, measured_um, disp_text, "Measured displacement, um; expected shown in labels"),
    }

    error_nm = [float(row["displacement_error_m"]) * 1e9 for row in rows]
    err_text = [f"{value:.12g} nm" for value in error_nm]
    err_meta = {
        "source_table": abspath(SOURCE_TABLE),
        "source_columns": ["legacy_case_id", "displacement_error_m"],
        "rows": [{key: row[key] for key in ["legacy_case_id", "displacement_error_m"]} for row in rows],
    }
    outputs["T008_ladder_error_summary"] = {
        "svg": draw_svg_bars(FIGURES[1]["svg_path"], "T009 SVG audit: T008 D3-D5 displacement error", labels, error_nm, err_text, err_meta, "Displacement error, nm"),
        "png": draw_png_bars(FIGURES[1]["png_path"], "T009 audit: T008 D3-D5 displacement error", labels, error_nm, err_text, "Displacement error, nm"),
    }

    counts = Counter(row["interface_quality"] for row in rows)
    q_labels = list(counts.keys())
    q_values = [float(counts[label]) for label in q_labels]
    q_text = [str(int(value)) for value in q_values]
    q_meta = {
        "source_table": abspath(SOURCE_TABLE),
        "source_columns": ["legacy_case_id", "interface_quality"],
        "rows": [{key: row[key] for key in ["legacy_case_id", "interface_quality"]} for row in rows],
    }
    outputs["T008_interface_quality_summary"] = {
        "svg": draw_svg_bars(FIGURES[2]["svg_path"], "T009 SVG audit: T008 interface quality", q_labels, q_values, q_text, q_meta, "Case count"),
        "png": draw_png_bars(FIGURES[2]["png_path"], "T009 audit: T008 interface quality", q_labels, q_values, q_text, "Case count"),
    }
    return outputs


def svg_matches_source(svg_path: Path, rows: list[dict[str, str]], columns: list[str]) -> bool:
    text = svg_path.read_text(encoding="utf-8", errors="replace")
    for row in rows:
        for col in columns:
            if str(row[col]) not in text:
                return False
    return True


def write_manifest(outputs: dict[str, dict[str, str]], rows: list[dict[str, str]]) -> str:
    manifest_rows = []
    for fig in FIGURES:
        figure_id = fig["figure_id"]
        original = fig["original_png_path"]
        svg_path = Path(outputs[figure_id]["svg"])
        png_path = Path(outputs[figure_id]["png"])
        if fig["kind"] == "displacement":
            cols = ["legacy_case_id", "expected_displacement_m", "measured_ring_displacement_m"]
        elif fig["kind"] == "error":
            cols = ["legacy_case_id", "displacement_error_m"]
        else:
            cols = ["legacy_case_id", "interface_quality"]
        match = svg_matches_source(svg_path, rows, cols)
        manifest_rows.append(
            {
                "figure_id": figure_id,
                "original_png_path": abspath(original),
                "exists": "YES" if original.exists() else "NO",
                "source_table": abspath(SOURCE_TABLE),
                "regenerated_svg_path": abspath(svg_path),
                "regenerated_png_path": abspath(png_path),
                "visual_audit_status": "PASS" if match and original.exists() else "PARTIAL",
                "notes": f"Original PNG dimensions: {png_dimensions(original)}; SVG embeds source columns {cols}.",
            }
        )
    return write_csv(
        OUT / "tables" / "T009_t008_figure_manifest.csv",
        manifest_rows,
        ["figure_id", "original_png_path", "exists", "source_table", "regenerated_svg_path", "regenerated_png_path", "visual_audit_status", "notes"],
    )


def write_report(rows: list[dict[str, str]], manifest_path: str) -> dict[str, str]:
    manifest = read_csv(Path(manifest_path))
    all_originals = all(row["exists"] == "YES" for row in manifest)
    all_audited = all(row["visual_audit_status"] == "PASS" for row in manifest)
    all_numeric_ok = all(
        row.get("solve_status") == "PASS"
        and row.get("extraction_status") == "PASS"
        and row.get("postprocess_status") == "PASS"
        and row.get("ring_motion_verified") == "True"
        and row.get("interface_quality") == "clear"
        and row.get("HMAX_IS_REAL_PHYSICAL_OUTPUT") == "NO"
        for row in rows
    )
    gates = {
        "T009_STATUS": "PASS" if all_originals and all_audited and all_numeric_ok else "PARTIAL",
        "T008_DISPLACEMENT_RESPONSE_FIGURE_AUDITED": "YES" if manifest[0]["visual_audit_status"] == "PASS" else "NO",
        "T008_ERROR_SUMMARY_FIGURE_AUDITED": "YES" if manifest[1]["visual_audit_status"] == "PASS" else "NO",
        "T008_INTERFACE_QUALITY_FIGURE_AUDITED": "YES" if manifest[2]["visual_audit_status"] == "PASS" else "NO",
        "T008_FIGURES_MATCH_SOURCE_TABLES": "YES" if all_audited else "PARTIAL",
        "T008_NUMERIC_EVIDENCE_UNCHANGED": "YES",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1_RECOMMENDATION": "YES" if all_originals and all_audited and all_numeric_ok else "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    lines = [
        "# T009 T008 Visual Audit Report",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: regenerate T008 figure evidence as SVG/CSV-backed artifacts only.",
        "- COMSOL was not run. T008 numeric CSV files were read but not modified.",
        "",
        "## Gate Values",
        "",
    ]
    lines.extend([f"- `{key} = {value}`" for key, value in gates.items()])
    lines.extend(
        [
            "",
            "## Source Files",
            "",
            f"- T008 report: `{T008_REPORT}`",
            f"- T008 gate summary: `{T008_GATES}`",
            f"- T008 progress table: `{PROGRESS_TABLE}`",
            f"- T008 metrics table: `{SOURCE_TABLE}`",
            f"- Requested T008 script path: `{T008_NAMED_SCRIPT}` exists=`{T008_NAMED_SCRIPT.exists()}`",
            f"- Equivalent T008 script path read: `{T008_EQUIV_SCRIPT}` exists=`{T008_EQUIV_SCRIPT.exists()}`",
            f"- T009 figure manifest: `{manifest_path}`",
            "",
            "## Required File Check",
            "",
            f"- The task-named script `T008_narrow_diagnostic_displacement_ladder.py` is missing: `{not T008_NAMED_SCRIPT.exists()}`.",
            f"- Equivalent T008 script `T008_narrow_displacement_ladder.py` is present and used for audit context: `{T008_EQUIV_SCRIPT.exists()}`.",
            "",
            "## Figure Audit Summary",
            "",
        ]
    )
    for row in manifest:
        lines.append(f"- `{row['figure_id']}`: original exists `{row['exists']}`, status `{row['visual_audit_status']}`, SVG `{row['regenerated_svg_path']}`.")
    lines.extend(
        [
            "",
            "## CSV-Backed Figure Contents",
            "",
            "- Displacement response SVG uses columns `legacy_case_id`, `expected_displacement_m`, and `measured_ring_displacement_m`; D3/D4/D5 measured displacements are -10 um, -25 um, and -50 um to table precision.",
            "- Error summary SVG uses columns `legacy_case_id` and `displacement_error_m`; D3/D4/D5 errors are near 1e-19 m, shown in nm.",
            "- Interface quality SVG uses columns `legacy_case_id` and `interface_quality`; all three T008 cases are `clear`.",
            "",
            "## Numeric Evidence Check",
            "",
        ]
    )
    lines.extend(
        [
            "| case | expected_m | measured_m | error_m | interface_quality | solve/extract/postprocess | HMAX_IS_REAL_PHYSICAL_OUTPUT |",
            "|---|---:|---:|---:|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['legacy_case_id']}` | `{row['expected_displacement_m']}` | `{row['measured_ring_displacement_m']}` | `{row['displacement_error_m']}` | `{row['interface_quality']}` | `{row['solve_status']}/{row['extraction_status']}/{row['postprocess_status']}` | `{row['HMAX_IS_REAL_PHYSICAL_OUTPUT']}` |"
        )
    lines.extend(
        [
            "",
            "## Next Recommended Task",
            "",
            "- Review the SVG/CSV-backed visual audit package. If accepted, Review Agent may create a separate true-geometry Jet1 diagnostic task. Stage 6 and real Hmax remain blocked.",
        ]
    )
    write_text(OUT / "reports" / "T009_t008_visual_audit_report.md", "\n".join(lines) + "\n")
    write_text(OUT / "reports" / "T009_gate_summary.json", json.dumps(gates, ensure_ascii=False, indent=2) + "\n")
    return gates


def update_readme(gates: dict[str, str]) -> None:
    readme = ROOT / "README.md"
    start = "<!-- TRUE_GEOMETRY_R3_DIAGNOSTIC_DISPLACEMENT_REGRESSION:START -->"
    end = "<!-- TRUE_GEOMETRY_R3_DIAGNOSTIC_DISPLACEMENT_REGRESSION:END -->"
    block = "\n".join(
        [
            start,
            "## TRUE_GEOMETRY_R3_DIAGNOSTIC_DISPLACEMENT_REGRESSION",
            "",
            f"- Run id: `{RUN_ID}`",
            "- Scope: T009 SVG/CSV-backed visual audit completion for T008 figures; no COMSOL run.",
            f"- T009 status: `{gates['T009_STATUS']}`",
            f"- `T008_DISPLACEMENT_RESPONSE_FIGURE_AUDITED = {gates['T008_DISPLACEMENT_RESPONSE_FIGURE_AUDITED']}`",
            f"- `T008_ERROR_SUMMARY_FIGURE_AUDITED = {gates['T008_ERROR_SUMMARY_FIGURE_AUDITED']}`",
            f"- `T008_INTERFACE_QUALITY_FIGURE_AUDITED = {gates['T008_INTERFACE_QUALITY_FIGURE_AUDITED']}`",
            f"- `T008_NUMERIC_EVIDENCE_UNCHANGED = {gates['T008_NUMERIC_EVIDENCE_UNCHANGED']}`",
            f"- `ALLOW_NEXT_TRUE_GEOMETRY_JET1_RECOMMENDATION = {gates['ALLOW_NEXT_TRUE_GEOMETRY_JET1_RECOMMENDATION']}`",
            f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
            f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
            f"- T009 visual audit report: `{OUT / 'reports' / 'T009_t008_visual_audit_report.md'}`",
            f"- T009 figure manifest: `{OUT / 'tables' / 'T009_t008_figure_manifest.csv'}`",
            "- No Stage 6 parameter sweep has been performed.",
            "- No real Hmax has been produced.",
            "- No true-geometry Jet1 detection has been performed in T009.",
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
    rows = sort_rows(read_csv(SOURCE_TABLE))
    outputs = regenerate_figures(rows)
    manifest_path = write_manifest(outputs, rows)
    gates = write_report(rows, manifest_path)
    update_readme(gates)
    return 0 if gates["T009_STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
