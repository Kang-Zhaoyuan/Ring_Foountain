# -*- coding: utf-8 -*-
"""Build the T002 R3 strict audit-completion package.

This script packages existing R3 evidence only. It does not run COMSOL, does
not advance physics stages, does not perform Jet1/Jet2 detection, and does not
produce real Hmax.
"""

from __future__ import annotations

import csv
import json
import math
import os
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
OUT = ROOT / "06_true_moving_geometry_R3_audit_completion_package"
R3_DIRS = [
    ROOT / "06_true_moving_geometry_R3_phase3_diagnostic_repair",
    ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation",
]
REQUIRED_INPUTS = [
    ROOT / "README.md",
    ROOT / "tasks" / "TASK_INDEX.md",
    ROOT / "reviews" / "20260620_120000_R002_run_trace.md",
    ROOT / "reviews" / "20260620_120000_R002_review_and_plan.md",
] + R3_DIRS
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dirs() -> None:
    for sub in ["reports", "tables", "images", "manifests", "scripts"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(path)


def abspath(path: Path) -> str:
    return str(path.resolve())


def write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return abspath(path)


def write_json(path: Path, payload: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return abspath(path)


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            out: dict[str, Any] = {}
            for key in columns:
                value = row.get(key, "")
                if isinstance(value, (dict, list, tuple, set)):
                    value = json.dumps(value, ensure_ascii=False, default=str)
                out[key] = value
            writer.writerow(out)
    return abspath(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def all_artifacts() -> list[Path]:
    found: list[Path] = []
    for base in R3_DIRS:
        if base.exists():
            for path in base.rglob("*"):
                if path.is_file():
                    found.append(path)
    return sorted(found, key=lambda p: rel(p).lower())


def source_phase(path: Path) -> str:
    text = rel(path)
    parts = text.split("\\")
    if len(parts) < 2:
        return parts[0] if parts else "unknown"
    if parts[0] == "06_true_moving_geometry_R3_phase3_diagnostic_repair":
        return "R3_phase3_diagnostic_repair"
    if parts[0] == "06_true_moving_geometry_R3_ring_contactline_isolation":
        if len(parts) >= 2 and parts[1][0:2].isdigit():
            return "R3_ring_contactline_" + parts[1]
        return "R3_ring_contactline_top"
    return parts[0]


def artifact_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".png":
        return "image_png"
    if ext in {".csv", ".tsv"}:
        return "table_" + ext[1:]
    if ext == ".json":
        return "data_json"
    if ext == ".md":
        return "report_markdown"
    if ext == ".log":
        return "log_text"
    if ext == ".py":
        return "script_python"
    if ext == ".java":
        return "export_java"
    if ext == ".mph":
        return "model_mph"
    return "artifact_" + (ext[1:] if ext else "no_ext")


def artifact_role(path: Path) -> str:
    parts = set(rel(path).lower().split("\\"))
    ext = path.suffix.lower()
    if "images" in parts or ext == ".png":
        return "visual evidence for reviewer audit"
    if "tables" in parts or ext in {".csv", ".tsv"}:
        return "numeric/tabular evidence for reviewer audit"
    if ext == ".json":
        return "structured summary or raw row evidence"
    if "reports" in parts or ext == ".md":
        return "narrative report / gate evidence"
    if "logs" in parts or ext == ".log":
        return "execution trace / negative evidence"
    if "models" in parts or ext == ".mph":
        return "COMSOL model artifact; not re-executed by T002"
    if "exports" in parts or ext == ".java":
        return "COMSOL Java export for construction audit"
    if "scripts" in parts or ext == ".py":
        return "reproducibility script"
    return "supporting artifact"


def file_mtime(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
    except OSError:
        return ""


def build_artifact_manifest(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        ext = path.suffix.lower()
        rows.append(
            {
                "artifact_path": abspath(path),
                "artifact_type": artifact_type(path),
                "source_phase": source_phase(path),
                "file_size_if_available": path.stat().st_size if path.exists() else "",
                "created_or_modified_if_available": file_mtime(path),
                "role": artifact_role(path),
                "requires_visual_audit": "YES" if ext == ".png" else "NO",
                "requires_numeric_audit": "YES" if ext in {".csv", ".tsv", ".json"} else "NO",
                "notes": "existing R3 evidence; original artifact not modified",
            }
        )
    return rows


def image_category(path: Path) -> str:
    name = path.name.lower()
    text = rel(path).lower()
    if "contact" in text or "wettedwall" in text:
        return "contactline_or_wettedwall_summary"
    if "spike_region" in name:
        return "spike_region_map"
    if "roughness" in name or "slope" in name:
        return "interface_metric_curve"
    if "geometry" in text:
        return "ring_geometry_control"
    if "consistency" in text or "drift" in name or "controls" in name or "stabilization" in name:
        return "R2_consistency_or_stabilization"
    if "key_metrics" in name:
        return "R2_key_metrics"
    return "R3_visual_evidence"


def expected_source_table_for_image(path: Path, table_paths: list[Path]) -> str:
    phase = source_phase(path)
    same_phase = [p for p in table_paths if source_phase(p) == phase and p.suffix.lower() in {".csv", ".tsv"}]
    if same_phase:
        return "; ".join(abspath(p) for p in same_phase[:3])
    parent_parts = set(path.parts)
    near = [p for p in table_paths if parent_parts.intersection(p.parts) and p.suffix.lower() in {".csv", ".tsv"}]
    return "; ".join(abspath(p) for p in near[:3])


def image_caption(path: Path) -> str:
    stem = path.stem.replace("_", " ")
    return f"{stem}; source phase {source_phase(path)}"


def build_image_index(image_paths: list[Path], table_paths: list[Path]) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    unreadable: list[str] = []
    for path in sorted(image_paths, key=lambda p: rel(p).lower()):
        width = ""
        height = ""
        readable = "NO"
        limitation = "not opened"
        try:
            with Image.open(path) as img:
                width, height = img.size
                img.verify()
            readable = "YES"
            limitation = "visual content not interpreted for physics validity; T002 only indexes and packages"
        except Exception as exc:
            unreadable.append(abspath(path))
            limitation = f"unreadable: {exc}"
        rows.append(
            {
                "image_path": abspath(path),
                "width_px": width,
                "height_px": height,
                "readable": readable,
                "visual_category": image_category(path),
                "expected_source_table": expected_source_table_for_image(path, table_paths),
                "caption": image_caption(path),
                "known_limitations": limitation,
            }
        )
    return rows, unreadable


def load_font(size: int) -> ImageFont.ImageFont:
    for candidate in ["arial.ttf", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/consola.ttf"]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:4]


def create_contact_sheet(image_rows: list[dict[str, Any]]) -> str:
    readable_paths = [Path(row["image_path"]) for row in image_rows if row["readable"] == "YES"]
    if not readable_paths:
        path = OUT / "images" / "R3_image_contact_sheet.png"
        Image.new("RGB", (1200, 300), "white").save(path)
        return abspath(path)

    thumb_w, thumb_h = 520, 300
    label_h = 110
    margin = 24
    cols = 2
    rows = math.ceil(len(readable_paths) / cols)
    sheet_w = cols * thumb_w + (cols + 1) * margin
    sheet_h = rows * (thumb_h + label_h) + (rows + 1) * margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)
    font = load_font(16)
    small = load_font(13)

    row_by_path = {row["image_path"]: row for row in image_rows}
    for idx, path in enumerate(readable_paths):
        r = idx // cols
        c = idx % cols
        x = margin + c * (thumb_w + margin)
        y = margin + r * (thumb_h + label_h + margin)
        draw.rectangle([x - 1, y - 1, x + thumb_w + 1, y + thumb_h + label_h + 1], outline=(180, 180, 180))
        with Image.open(path) as img:
            img = img.convert("RGB")
            img.thumbnail((thumb_w, thumb_h))
            ox = x + (thumb_w - img.width) // 2
            oy = y + (thumb_h - img.height) // 2
            sheet.paste(img, (ox, oy))
        row = row_by_path[abspath(path)]
        label = f"{idx + 1}. {path.name} | {source_phase(path)}"
        lines = wrap_text(draw, label, font, thumb_w - 10)
        ty = y + thumb_h + 6
        for line in lines:
            draw.text((x + 6, ty), line, fill=(0, 0, 0), font=font)
            ty += 19
        detail = f"{row['width_px']}x{row['height_px']} | {row['visual_category']}"
        detail_lines = wrap_text(draw, detail, small, thumb_w - 10)
        for line in detail_lines:
            draw.text((x + 6, ty), line, fill=(70, 70, 70), font=small)
            ty += 16

    out = OUT / "images" / "R3_image_contact_sheet.png"
    sheet.save(out)
    return abspath(out)


def parse_scalar(value: str) -> float | None:
    try:
        if value is None:
            return None
        text = str(value).strip()
        if text == "" or text.lower() in {"nan", "inf", "-inf"}:
            return None
        return float(text)
    except Exception:
        return None


def summarize_csv_table(path: Path, delimiter: str = ",") -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            rows = list(reader)
            columns = reader.fieldnames or []
    except Exception as exc:
        return {
            "row_count": "",
            "column_or_field_summary": f"unreadable: {exc}",
            "key_numeric_columns": "",
            "key_status_values": "",
            "obvious_anomalies": f"unreadable: {exc}",
        }
    numeric_cols: list[str] = []
    status_values: Counter[str] = Counter()
    anomalies: list[str] = []
    for col in columns:
        values = [row.get(col, "") for row in rows]
        nums = [parse_scalar(v) for v in values]
        finite_nums = [v for v in nums if v is not None and math.isfinite(v)]
        if values and len(finite_nums) >= max(1, len(values) // 2):
            numeric_cols.append(col)
    for col in columns:
        if any(token in col.lower() for token in ["status", "pass", "fail", "quality", "gate", "allow"]):
            for row in rows:
                value = str(row.get(col, "")).strip()
                if value:
                    status_values[f"{col}={value}"] += 1
    if len(rows) == 0:
        anomalies.append("zero rows")
    if not columns:
        anomalies.append("no header columns")
    return {
        "row_count": len(rows),
        "column_or_field_summary": "; ".join(columns[:40]),
        "key_numeric_columns": "; ".join(numeric_cols[:30]),
        "key_status_values": "; ".join(f"{k}({v})" for k, v in status_values.most_common(20)),
        "obvious_anomalies": "; ".join(anomalies) if anomalies else "none obvious from structural audit",
    }


def flatten_json_fields(obj: Any, prefix: str = "", limit: int = 80) -> list[str]:
    fields: list[str] = []
    if len(fields) >= limit:
        return fields
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            fields.append(path)
            if isinstance(value, (dict, list)) and len(fields) < limit:
                fields.extend(flatten_json_fields(value, path, limit - len(fields)))
    elif isinstance(obj, list):
        fields.append(f"{prefix}[]")
        if obj:
            fields.extend(flatten_json_fields(obj[0], f"{prefix}[]" if prefix else "[]", limit - len(fields)))
    return fields[:limit]


def summarize_json_table(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(read_text(path))
    except Exception as exc:
        return {
            "row_count": "",
            "column_or_field_summary": f"unreadable: {exc}",
            "key_numeric_columns": "",
            "key_status_values": "",
            "obvious_anomalies": f"unreadable: {exc}",
        }
    if isinstance(data, list):
        row_count = len(data)
    elif isinstance(data, dict):
        row_count = len(data)
    else:
        row_count = 1
    fields = flatten_json_fields(data)
    status_values: list[str] = []
    text = json.dumps(data, ensure_ascii=False, default=str)
    for token in ["PASS", "FAIL", "FAIL_DIAGNOSTIC", "NO", "YES", "weak_or_spiky"]:
        count = text.count(token)
        if count:
            status_values.append(f"{token}({count})")
    anomalies = []
    if row_count == 0:
        anomalies.append("empty JSON")
    return {
        "row_count": row_count,
        "column_or_field_summary": "; ".join(fields[:60]),
        "key_numeric_columns": "JSON numeric scan not expanded; see field summary",
        "key_status_values": "; ".join(status_values),
        "obvious_anomalies": "; ".join(anomalies) if anomalies else "none obvious from structural audit",
    }


def linked_images_for_table(path: Path, image_paths: list[Path]) -> str:
    phase = source_phase(path)
    same_phase = [p for p in image_paths if source_phase(p) == phase]
    return "; ".join(abspath(p) for p in same_phase[:8])


def build_table_index(table_paths: list[Path], image_paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(table_paths, key=lambda p: rel(p).lower()):
        ext = path.suffix.lower()
        if ext == ".csv":
            summary = summarize_csv_table(path, ",")
        elif ext == ".tsv":
            summary = summarize_csv_table(path, "\t")
        elif ext == ".json":
            summary = summarize_json_table(path)
        else:
            continue
        rows.append(
            {
                "table_path": abspath(path),
                "file_type": ext[1:],
                "row_count": summary["row_count"],
                "column_or_field_summary": summary["column_or_field_summary"],
                "key_numeric_columns": summary["key_numeric_columns"],
                "key_status_values": summary["key_status_values"],
                "obvious_anomalies": summary["obvious_anomalies"],
                "linked_images": linked_images_for_table(path, image_paths),
                "notes": "structural audit only; original table not modified",
            }
        )
    return rows


def create_summary_tables(manifest: list[dict[str, Any]], image_rows: list[dict[str, Any]], table_rows: list[dict[str, Any]]) -> None:
    by_type = Counter(row["artifact_type"] for row in manifest)
    write_csv(
        OUT / "tables" / "R3_artifact_type_summary.csv",
        [{"artifact_type": key, "count": value} for key, value in sorted(by_type.items())],
        ["artifact_type", "count"],
    )
    by_category = Counter(row["visual_category"] for row in image_rows)
    write_csv(
        OUT / "tables" / "R3_image_category_summary.csv",
        [{"visual_category": key, "count": value} for key, value in sorted(by_category.items())],
        ["visual_category", "count"],
    )
    status_counter: Counter[str] = Counter()
    for row in table_rows:
        for item in str(row.get("key_status_values", "")).split("; "):
            if item:
                status_counter[item] += 1
    write_csv(
        OUT / "tables" / "R3_table_status_token_summary.csv",
        [{"status_token": key, "table_count": value} for key, value in status_counter.most_common()],
        ["status_token", "table_count"],
    )


def report_artifact_manifest(manifest: list[dict[str, Any]], missing: list[str]) -> None:
    counts = Counter(row["artifact_type"] for row in manifest)
    lines = [
        "# R3 Artifact Manifest Report",
        "",
        f"- Run id: `{RUN_ID}`",
        f"- Artifact count: `{len(manifest)}`",
        f"- Source directories: `{'; '.join(abspath(p) for p in R3_DIRS)}`",
        "- Scope: existing R3 outputs only; no COMSOL run and no physics advancement.",
        "",
        "## Artifact Type Counts",
        "",
    ]
    lines.extend([f"- `{key}`: `{value}`" for key, value in sorted(counts.items())])
    if missing:
        lines.extend(["", "## Missing Expected Inputs", ""])
        lines.extend([f"- `{item}`" for item in missing])
    write_text(OUT / "reports" / "R3_artifact_manifest_report.md", "\n".join(lines) + "\n")


def report_image_support(image_rows: list[dict[str, Any]], unreadable: list[str], contact_sheet: str) -> None:
    lines = [
        "# R3 Image Audit Support",
        "",
        f"- Run id: `{RUN_ID}`",
        f"- PNG images indexed: `{len(image_rows)}`",
        f"- Readable PNG images: `{sum(1 for row in image_rows if row['readable'] == 'YES')}`",
        f"- Unreadable PNG images: `{len(unreadable)}`",
        f"- Contact sheet: `{contact_sheet}`",
        "",
        "## Notes",
        "",
        "- Original images were not altered or replaced.",
        "- Contact sheet is for reviewer navigation only and is not new physics evidence.",
    ]
    if unreadable:
        lines.extend(["", "## Unreadable Images", ""])
        lines.extend([f"- `{path}`" for path in unreadable])
    write_text(OUT / "reports" / "R3_image_audit_support.md", "\n".join(lines) + "\n")


def report_table_support(table_rows: list[dict[str, Any]]) -> None:
    anomalies = [row for row in table_rows if str(row.get("obvious_anomalies", "")) != "none obvious from structural audit"]
    lines = [
        "# R3 Table Audit Support",
        "",
        f"- Run id: `{RUN_ID}`",
        f"- CSV/TSV/JSON table-like artifacts indexed: `{len(table_rows)}`",
        f"- Structural anomaly rows: `{len(anomalies)}`",
        "- Original table-like artifacts were not modified.",
        "",
        "## Indexed Table Paths",
        "",
    ]
    lines.extend([f"- `{row['table_path']}`" for row in table_rows])
    if anomalies:
        lines.extend(["", "## Structural Anomalies", ""])
        for row in anomalies:
            lines.append(f"- `{row['table_path']}`: {row['obvious_anomalies']}")
    write_text(OUT / "reports" / "R3_table_audit_support.md", "\n".join(lines) + "\n")


def final_report(manifest: list[dict[str, Any]], image_rows: list[dict[str, Any]], table_rows: list[dict[str, Any]], unreadable: list[str], missing: list[str]) -> dict[str, str]:
    all_images_indexed = "YES" if not unreadable else "NO"
    all_tables_indexed = "YES" if table_rows else "NO"
    status = "PASS" if all_images_indexed == "YES" and all_tables_indexed == "YES" and not missing else "PARTIAL"
    gates = {
        "AUDIT_PACKAGE_STATUS": status,
        "ALL_IMAGES_INDEXED": all_images_indexed,
        "ALL_TABLES_INDEXED": all_tables_indexed,
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "NO",
    }
    lines = [
        "# R3 Audit Completion Final Report",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Task: `tasks/NEXT_TASK.md` / T002 R3 Output Strict Audit Completion Package.",
        "- Scope: audit packaging only; no COMSOL run, no Stage 6, no parameter sweep, no Jet1/Jet2 detection, no real Hmax.",
        "",
        "## Gate Values",
        "",
        f"- `AUDIT_PACKAGE_STATUS = {gates['AUDIT_PACKAGE_STATUS']}`",
        f"- `ALL_IMAGES_INDEXED = {gates['ALL_IMAGES_INDEXED']}`",
        f"- `ALL_TABLES_INDEXED = {gates['ALL_TABLES_INDEXED']}`",
        f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
        f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
        f"- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = {gates['ALLOW_NEXT_TRUE_GEOMETRY_JET1']}`",
        "",
        "## Counts",
        "",
        f"- Artifacts in manifest: `{len(manifest)}`",
        f"- PNG images indexed: `{len(image_rows)}`",
        f"- Table-like artifacts indexed: `{len(table_rows)}`",
        f"- Unreadable images: `{len(unreadable)}`",
        f"- Missing expected input paths: `{len(missing)}`",
        "",
        "## Key Outputs",
        "",
        f"- Manifest: `{OUT / 'manifests' / 'R3_artifact_manifest.csv'}`",
        f"- Image index: `{OUT / 'tables' / 'R3_image_audit_index.csv'}`",
        f"- Image contact sheet: `{OUT / 'images' / 'R3_image_contact_sheet.png'}`",
        f"- Table index: `{OUT / 'tables' / 'R3_table_audit_index.csv'}`",
        "",
        "## Next Recommended Task",
        "",
        "- Review Agent should perform strict review using this package. Stage advancement remains blocked unless a later task explicitly changes gates.",
    ]
    if unreadable:
        lines.extend(["", "## Unreadable Images", ""])
        lines.extend([f"- `{path}`" for path in unreadable])
    if missing:
        lines.extend(["", "## Missing Expected Inputs", ""])
        lines.extend([f"- `{path}`" for path in missing])
    write_text(OUT / "reports" / "R3_audit_completion_final_report.md", "\n".join(lines) + "\n")
    write_json(OUT / "reports" / "R3_audit_completion_gate_summary.json", gates)
    return gates


def update_readme(gates: dict[str, str], image_count: int, table_count: int) -> None:
    readme = ROOT / "README.md"
    start = "<!-- TRUE_GEOMETRY_R3_AUDIT_COMPLETION_PACKAGE:START -->"
    end = "<!-- TRUE_GEOMETRY_R3_AUDIT_COMPLETION_PACKAGE:END -->"
    block = "\n".join(
        [
            start,
            "## TRUE_GEOMETRY_R3_AUDIT_COMPLETION_PACKAGE",
            "",
            f"- Run id: `{RUN_ID}`",
            "- Scope: audit-completion packaging for existing R3 outputs only.",
            f"- Audit package status: `{gates['AUDIT_PACKAGE_STATUS']}`",
            f"- Images indexed: `{image_count}`",
            f"- Table-like artifacts indexed: `{table_count}`",
            f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
            f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
            f"- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = {gates['ALLOW_NEXT_TRUE_GEOMETRY_JET1']}`",
            f"- Final report: `{OUT / 'reports' / 'R3_audit_completion_final_report.md'}`",
            f"- Manifest: `{OUT / 'manifests' / 'R3_artifact_manifest.csv'}`",
            f"- Image contact sheet: `{OUT / 'images' / 'R3_image_contact_sheet.png'}`",
            "- No Stage 6 parameter sweep has been performed.",
            "- No real Hmax has been produced.",
            "- No true-geometry Jet1 detection has been performed.",
            end,
        ]
    )
    text = read_text(readme)
    if start in text and end in text:
        before = text.split(start, 1)[0].rstrip()
        after = text.split(end, 1)[1].lstrip()
        text = before + "\n\n" + block + "\n\n" + after
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    write_text(readme, text)


def main() -> int:
    ensure_dirs()
    script_copy = OUT / "scripts" / "R3_audit_completion_package.py"
    if Path(__file__).resolve() != script_copy.resolve():
        shutil.copy2(Path(__file__).resolve(), script_copy)

    missing = [abspath(path) for path in REQUIRED_INPUTS if not path.exists()]
    paths = all_artifacts()
    image_paths = [path for path in paths if path.suffix.lower() == ".png"]
    table_paths = [path for path in paths if path.suffix.lower() in {".csv", ".tsv", ".json"}]

    manifest = build_artifact_manifest(paths)
    write_csv(
        OUT / "manifests" / "R3_artifact_manifest.csv",
        manifest,
        ["artifact_path", "artifact_type", "source_phase", "file_size_if_available", "created_or_modified_if_available", "role", "requires_visual_audit", "requires_numeric_audit", "notes"],
    )
    report_artifact_manifest(manifest, missing)

    image_rows, unreadable = build_image_index(image_paths, table_paths)
    write_csv(
        OUT / "tables" / "R3_image_audit_index.csv",
        image_rows,
        ["image_path", "width_px", "height_px", "readable", "visual_category", "expected_source_table", "caption", "known_limitations"],
    )
    contact_sheet = create_contact_sheet(image_rows)
    report_image_support(image_rows, unreadable, contact_sheet)

    table_rows = build_table_index(table_paths, image_paths)
    write_csv(
        OUT / "tables" / "R3_table_audit_index.csv",
        table_rows,
        ["table_path", "file_type", "row_count", "column_or_field_summary", "key_numeric_columns", "key_status_values", "obvious_anomalies", "linked_images", "notes"],
    )
    report_table_support(table_rows)
    create_summary_tables(manifest, image_rows, table_rows)
    gates = final_report(manifest, image_rows, table_rows, unreadable, missing)
    update_readme(gates, len(image_rows), len(table_rows))
    return 0 if gates["AUDIT_PACKAGE_STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
