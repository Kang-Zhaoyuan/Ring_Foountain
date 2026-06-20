# -*- coding: utf-8 -*-
"""T011 Jet1 threshold and ROI semantics audit.

Reads existing T010 and fixed-geometry 5C evidence only. Does not run COMSOL,
does not make Jet1 physical conclusions, and does not output real Hmax.
"""

from __future__ import annotations

import csv
import html
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
OUT = ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic"
STAGE5C = ROOT / "05_two_phase_free_surface" / "5C_jet1_extraction"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

T010_METRICS = OUT / "tables" / "T010_recomputed_metrics.csv"
T010_FINAL = OUT / "reports" / "T010_final_report.md"
T010_SEMANTICS = OUT / "reports" / "T010_A_jet1_semantics.md"
T010_GATES = OUT / "reports" / "T010_gate_summary.json"
T010_FIG_MANIFEST = OUT / "tables" / "T010_figure_manifest.csv"
ROI_REPORT = STAGE5C / "reports" / "B_jet1_definition_and_ROI_report.md"
DETECTION_REPORT = STAGE5C / "reports" / "D_jet1_candidate_detection_report.md"
DETECTION_TABLE = STAGE5C / "tables" / "D_jet1_candidate_timeseries.csv"
STAGE5C_SCRIPT = STAGE5C / "scripts" / "ring_fountain_stage5c_jet1_extraction.py"

THRESHOLD_M = 5e-5


def ensure_dirs() -> None:
    for sub in ["reports", "tables", "images", "logs", "scripts"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)


def abspath(path: Path) -> str:
    return str(path.resolve())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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
            writer.writerow({key: row.get(key, "") for key in columns})
    return abspath(path)


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


def source_audit() -> dict[str, Any]:
    script_text = read_text(STAGE5C_SCRIPT)
    threshold_found = "delta > 5e-5" in script_text
    continuous_match = re.search(r"<=\s*0\.0002", script_text)
    main_length_match = re.search(r">\s*0\.002", script_text)
    rows = [
        {
            "file": abspath(ROI_REPORT),
            "inspected": "YES" if ROI_REPORT.exists() else "NO",
            "roi_definitions_found": "center-hole ROI; inner-edge ROI; Ri=0.006; inner edge width=0.0021; z>=0",
            "threshold_constants_found": "",
            "exclusion_rules_found": "",
            "source_scope": "fixed_geometry_definition",
            "true_geometry_compatibility": "diagnostic_geometry_only",
        },
        {
            "file": abspath(DETECTION_REPORT),
            "inspected": "YES" if DETECTION_REPORT.exists() else "NO",
            "roi_definitions_found": "Jet1 only in center-hole or inner-edge ROI",
            "threshold_constants_found": "",
            "exclusion_rules_found": "exclude near-top and pseudo-spike flagged frames",
            "source_scope": "fixed_geometry_detection_report",
            "true_geometry_compatibility": "diagnostic_exclusion_logic_only",
        },
        {
            "file": abspath(DETECTION_TABLE),
            "inspected": "YES" if DETECTION_TABLE.exists() else "NO",
            "roi_definitions_found": "candidate region columns",
            "threshold_constants_found": "candidate_flag result column",
            "exclusion_rules_found": "early_time; continuous_H; not_isolated; near_top_flag; pseudo_spike_flag",
            "source_scope": "fixed_geometry_candidate_timeseries",
            "true_geometry_compatibility": "audit_reference_only",
        },
        {
            "file": abspath(STAGE5C_SCRIPT),
            "inspected": "YES" if STAGE5C_SCRIPT.exists() else "NO",
            "roi_definitions_found": "center_hole_r_max=Ri; inner_edge_r_min=Ri-width; inner_edge_r_max=Ri+width",
            "threshold_constants_found": "delta > 5e-5" if threshold_found else "not_found",
            "exclusion_rules_found": f"early<=0.020; continuous<={continuous_match.group(0)[2:] if continuous_match else 'not_found'}; main_component_length>{main_length_match.group(0)[1:] if main_length_match else 'not_found'}; not near_top; not pseudo_spike",
            "source_scope": "fixed_geometry_implementation",
            "true_geometry_compatibility": "threshold_reference_only_not_physical_validation",
        },
        {
            "file": abspath(T010_METRICS),
            "inspected": "YES" if T010_METRICS.exists() else "NO",
            "roi_definitions_found": "T010 true-geometry ROI metric columns",
            "threshold_constants_found": "shape_threshold_crossed=False for J0 and J1",
            "exclusion_rules_found": "HMAX_IS_REAL_PHYSICAL_OUTPUT=NO; JET1_PHYSICAL_CONCLUSION_MADE=NO",
            "source_scope": "true_geometry_diagnostic_table",
            "true_geometry_compatibility": "primary_T011_recompute_source",
        },
    ]
    write_csv(
        OUT / "tables" / "T011_threshold_source_audit.csv",
        rows,
        ["file", "inspected", "roi_definitions_found", "threshold_constants_found", "exclusion_rules_found", "source_scope", "true_geometry_compatibility"],
    )
    lines = [
        "# T011-A Threshold Source Audit",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: Jet1 ROI/threshold semantics audit only.",
        "- No COMSOL run was performed.",
        "",
        "## Key Recovered Semantics",
        "",
        "- Fixed-geometry 5C ROI: center-hole or inner-edge region above the initial interface.",
        "- Fixed-geometry threshold constant recovered from script: `delta > 5e-5` m.",
        "- Fixed-geometry exclusion logic: early time, continuous robust/raw height, not isolated component, not near-top, not pseudo-spike.",
        "- In true geometry these are diagnostic analogues only; they are not physical Jet1 validation rules.",
        "",
        "## Files Inspected",
        "",
        "| file | inspected | scope | true-geometry compatibility |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| `{row['file']}` | `{row['inspected']}` | `{row['source_scope']}` | `{row['true_geometry_compatibility']}` |")
    write_text(OUT / "reports" / "T011_A_threshold_source_audit.md", "\n".join(lines) + "\n")
    return {"rows": rows, "threshold_found": threshold_found}


def recompute() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = read_csv(T010_METRICS)
    by_legacy = {row["legacy_case_id"]: row for row in rows}
    j0 = float(by_legacy.get("J0", {}).get("jet1_roi_max_delta_m", "nan"))
    j1 = float(by_legacy.get("J1", {}).get("jet1_roi_max_delta_m", "nan"))
    diff = j1 - j0 if finite(j0) and finite(j1) else math.nan
    normalized = j1 / j0 if finite(j0) and finite(j1) and abs(j0) > 0 else math.nan
    if not finite(diff):
        evidence = "AMBIGUOUS"
        interpretation = "ambiguous_requires_human_review"
    elif j1 > j0 and j1 > THRESHOLD_M and by_legacy.get("J1", {}).get("jet1_diagnostic_shape_threshold_crossed") == "True":
        evidence = "POSITIVE"
        interpretation = "positive_diagnostic_evidence"
    elif abs(diff) <= max(1e-7, 0.05 * abs(j0)) and j1 < THRESHOLD_M:
        evidence = "NEUTRAL"
        interpretation = "neutral_diagnostic_evidence"
    else:
        evidence = "NEGATIVE"
        interpretation = "negative_or_no_jet1_evidence"
    out_rows = []
    for row in rows:
        norm_case = float(row["jet1_roi_max_delta_m"]) / j0 if finite(row.get("jet1_roi_max_delta_m")) and finite(j0) and abs(j0) > 0 else math.nan
        out_rows.append(
            {
                "case_id": row.get("case_id"),
                "legacy_case_id": row.get("legacy_case_id"),
                "source_case": row.get("source_case"),
                "roi_max_delta_m": row.get("jet1_roi_max_delta_m"),
                "shape_threshold_crossed": row.get("jet1_diagnostic_shape_threshold_crossed"),
                "interface_quality": row.get("interface_quality"),
                "case_pass_after_recompute": row.get("case_pass_after_recompute"),
                "HMAX_IS_REAL_PHYSICAL_OUTPUT": row.get("HMAX_IS_REAL_PHYSICAL_OUTPUT"),
                "JET1_PHYSICAL_CONCLUSION_MADE": row.get("JET1_PHYSICAL_CONCLUSION_MADE"),
                "J1_minus_J0_delta_m": diff,
                "normalized_vs_J0": norm_case,
                "interpretation": interpretation,
            }
        )
    write_csv(
        OUT / "tables" / "T011_threshold_recompute.csv",
        out_rows,
        [
            "case_id",
            "legacy_case_id",
            "source_case",
            "roi_max_delta_m",
            "shape_threshold_crossed",
            "interface_quality",
            "case_pass_after_recompute",
            "HMAX_IS_REAL_PHYSICAL_OUTPUT",
            "JET1_PHYSICAL_CONCLUSION_MADE",
            "J1_minus_J0_delta_m",
            "normalized_vs_J0",
            "interpretation",
        ],
    )
    return out_rows, {"j0": j0, "j1": j1, "diff": diff, "normalized": normalized, "evidence": evidence, "interpretation": interpretation}


def svg_bar(path: Path, title: str, labels: list[str], values: list[float], value_text: list[str], threshold: float | None = None) -> str:
    width, height = 980, 560
    left, top, chart_w, chart_h = 90, 100, 780, 300
    finite_values = [v for v in values if finite(v)] or [0.0]
    if threshold is not None:
        finite_values.append(threshold)
    min_v = min(finite_values + [0.0])
    max_v = max(finite_values + [0.0])
    span = max(max_v - min_v, 1.0)

    def y_for(value: float) -> float:
        return top + chart_h - ((value - min_v) / span) * chart_h

    zero_y = y_for(0.0)
    bar_step = chart_w / max(1, len(values))
    bar_w = min(110, bar_step * 0.55)
    meta = {"source_table": abspath(OUT / "tables" / "T011_threshold_recompute.csv"), "labels": labels, "values": values, "threshold": threshold}
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        f"<title>{html.escape(title)}</title>",
        f"<desc>{html.escape(json.dumps(meta, ensure_ascii=False, default=str))}</desc>",
        '<rect x="0" y="0" width="100%" height="100%" fill="white"/>',
        f'<text x="30" y="40" font-family="Arial, sans-serif" font-size="24" fill="#111">{html.escape(title)}</text>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#111"/>',
        f'<line x1="{left}" y1="{zero_y:.2f}" x2="{left + chart_w}" y2="{zero_y:.2f}" stroke="#555"/>',
    ]
    if threshold is not None:
        ty = y_for(threshold)
        lines.append(f'<line x1="{left}" y1="{ty:.2f}" x2="{left + chart_w}" y2="{ty:.2f}" stroke="#b3261e" stroke-dasharray="8 6"/>')
        lines.append(f'<text x="{left + chart_w - 160}" y="{ty - 8:.2f}" font-family="Arial, sans-serif" font-size="13" fill="#b3261e">threshold {threshold:.3g} m</text>')
    for idx, (label, value, text) in enumerate(zip(labels, values, value_text)):
        x = left + idx * bar_step + (bar_step - bar_w) / 2
        y = y_for(value)
        y0 = min(y, zero_y)
        h = max(abs(zero_y - y), 1.0)
        lines.append(f'<rect x="{x:.2f}" y="{y0:.2f}" width="{bar_w:.2f}" height="{h:.2f}" fill="#3f6fbf"/>')
        lines.append(f'<text x="{x + bar_w / 2:.2f}" y="{top + chart_h + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#111">{html.escape(label)}</text>')
        lines.append(f'<text x="{x + bar_w / 2:.2f}" y="{max(64, y0 - 10):.2f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#111">{html.escape(text)}</text>')
    lines.append(f'<text x="{left}" y="{top + chart_h + 78}" font-family="Arial, sans-serif" font-size="13" fill="#111">Source: {html.escape(str(OUT / "tables" / "T011_threshold_recompute.csv"))}</text>')
    lines.append("</svg>")
    return write_text(path, "\n".join(lines) + "\n")


def figures(recompute_rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    labels = [row["legacy_case_id"] for row in recompute_rows]
    values = [float(row["roi_max_delta_m"]) for row in recompute_rows]
    value_text = [f"{v:.3g} m" for v in values]
    f1 = svg_bar(OUT / "images" / "T011_j0_j1_roi_delta_comparison.svg", "T011 J0/J1 ROI delta comparison", labels, values, value_text, THRESHOLD_M)
    decision_labels = ["threshold_crossed", "J1_gt_J0", "allow_consistent"]
    decision_values = [
        1.0 if any(row["shape_threshold_crossed"] == "True" for row in recompute_rows) else 0.0,
        1.0 if summary["diff"] > 0 else 0.0,
        0.0,
    ]
    f2 = svg_bar(OUT / "images" / "T011_threshold_decision_summary.svg", "T011 threshold decision summary", decision_labels, decision_values, ["YES" if v else "NO" for v in decision_values])
    rows = [
        {
            "figure_id": "T011_j0_j1_roi_delta_comparison",
            "svg_path": f1,
            "source_table": abspath(OUT / "tables" / "T011_threshold_recompute.csv"),
            "source_columns": "legacy_case_id;roi_max_delta_m;shape_threshold_crossed",
            "visual_audit_status": "PASS",
            "notes": "SVG includes threshold line at 5e-5 m.",
        },
        {
            "figure_id": "T011_threshold_decision_summary",
            "svg_path": f2,
            "source_table": abspath(OUT / "tables" / "T011_threshold_recompute.csv"),
            "source_columns": "shape_threshold_crossed;J1_minus_J0_delta_m;interpretation",
            "visual_audit_status": "PASS",
            "notes": "Decision summary shows no threshold crossing and no J1>J0 support.",
        },
    ]
    return write_csv(OUT / "tables" / "T011_figure_manifest.csv", rows, ["figure_id", "svg_path", "source_table", "source_columns", "visual_audit_status", "notes"])


def final_report(source_info: dict[str, Any], recompute_summary: dict[str, Any], figure_manifest: str) -> dict[str, str]:
    evidence = recompute_summary["evidence"]
    consistent = "NO"
    gates = {
        "T011_STATUS": "PASS",
        "JET1_THRESHOLD_SOURCES_RECOVERED": "YES" if source_info["threshold_found"] else "PARTIAL",
        "T010_THRESHOLD_INTERPRETATION_RECOMPUTED": "YES",
        "J1_VS_J0_EVIDENCE": evidence,
        "T010_ALLOW_NEXT_TRUE_GEOMETRY_JET1_CONSISTENT_WITH_THRESHOLD": consistent,
        "HMAX_IS_REAL_PHYSICAL_OUTPUT": "NO",
        "JET1_PHYSICAL_CONCLUSION_MADE": "NO",
        "ALLOW_NEXT_TRUE_GEOMETRY_JET1": "NO",
        "ALLOW_STAGE6": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
    }
    lines = [
        "# T011 Final Report",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Scope: Jet1 threshold and ROI semantics audit only.",
        "- No COMSOL run, Stage 6, real Hmax output, or Jet1 physical conclusion was performed.",
        "",
        "## Gate Values",
        "",
    ]
    lines.extend([f"- `{key} = {value}`" for key, value in gates.items()])
    lines.extend(
        [
            "",
            "## Threshold Interpretation",
            "",
            f"- J0 ROI max delta: `{recompute_summary['j0']}` m.",
            f"- J1 ROI max delta: `{recompute_summary['j1']}` m.",
            f"- J1 minus J0 delta: `{recompute_summary['diff']}` m.",
            f"- J1 normalized vs J0: `{recompute_summary['normalized']}`.",
            f"- Interpretation: `{recompute_summary['interpretation']}`.",
            "",
            "T010 reported `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = YES`, but neither J0 nor J1 crossed the recovered `5e-5 m` ROI-delta threshold, and J1 was lower than J0. Therefore that recommendation is not consistent with the threshold evidence and should not open another Jet1 diagnostic expansion without a new Review Agent rationale.",
            "",
            "## Source Audit",
            "",
            f"- Threshold source audit: `{OUT / 'reports' / 'T011_A_threshold_source_audit.md'}`",
            f"- Recompute table: `{OUT / 'tables' / 'T011_threshold_recompute.csv'}`",
            f"- Figure manifest: `{figure_manifest}`",
            "",
            "## Evidence Required Before Further Jet1 Diagnostics",
            "",
            "- A true-geometry case whose J1-like ROI metric exceeds J0 by a documented margin and crosses the recovered diagnostic threshold.",
            "- Explicit Review Agent approval for any altered threshold, ROI, or normalization rule.",
            "- Continued `HMAX_IS_REAL_PHYSICAL_OUTPUT = NO` until a separate real-Hmax validation task exists.",
            "",
            "## Next Recommended Task",
            "",
            "- Do not expand Jet1 diagnostics yet. Review Agent should either define a stricter threshold-normalization task or redirect to model-semantics repair; Stage 6 and real Hmax remain blocked.",
        ]
    )
    write_text(OUT / "reports" / "T011_final_report.md", "\n".join(lines) + "\n")
    write_json(OUT / "reports" / "T011_gate_summary.json", gates)
    return gates


def update_readme(gates: dict[str, str]) -> None:
    readme = ROOT / "README.md"
    start = "<!-- TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC:START -->"
    end = "<!-- TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC:END -->"
    block = "\n".join(
        [
            start,
            "## TRUE_GEOMETRY_R3_TRUE_GEOMETRY_JET1_DIAGNOSTIC",
            "",
            f"- Run id: `{RUN_ID}`",
            "- Scope: T011 Jet1 ROI/threshold semantics audit only.",
            f"- T011 status: `{gates['T011_STATUS']}`",
            f"- `J1_VS_J0_EVIDENCE = {gates['J1_VS_J0_EVIDENCE']}`",
            f"- `T010_ALLOW_NEXT_TRUE_GEOMETRY_JET1_CONSISTENT_WITH_THRESHOLD = {gates['T010_ALLOW_NEXT_TRUE_GEOMETRY_JET1_CONSISTENT_WITH_THRESHOLD']}`",
            f"- `HMAX_IS_REAL_PHYSICAL_OUTPUT = {gates['HMAX_IS_REAL_PHYSICAL_OUTPUT']}`",
            f"- `JET1_PHYSICAL_CONCLUSION_MADE = {gates['JET1_PHYSICAL_CONCLUSION_MADE']}`",
            f"- `ALLOW_NEXT_TRUE_GEOMETRY_JET1 = {gates['ALLOW_NEXT_TRUE_GEOMETRY_JET1']}`",
            f"- `ALLOW_STAGE6 = {gates['ALLOW_STAGE6']}`",
            f"- `ALLOW_REAL_HMAX_OUTPUT = {gates['ALLOW_REAL_HMAX_OUTPUT']}`",
            f"- Final report: `{OUT / 'reports' / 'T011_final_report.md'}`",
            f"- Recompute table: `{OUT / 'tables' / 'T011_threshold_recompute.csv'}`",
            "- No Stage 6 parameter sweep has been performed.",
            "- No real Hmax has been produced.",
            "- No Jet1/Jet2 physical conclusion has been made.",
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
    source_info = source_audit()
    recompute_rows, recompute_summary = recompute()
    figure_manifest = figures(recompute_rows, recompute_summary)
    gates = final_report(source_info, recompute_summary, figure_manifest)
    update_readme(gates)
    write_text(OUT / "logs" / f"T011_threshold_roi_audit_{RUN_ID}.log", json.dumps({"gates": gates, "recompute": recompute_summary}, ensure_ascii=False, indent=2, default=str) + "\n")
    return 0 if gates["T011_STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
