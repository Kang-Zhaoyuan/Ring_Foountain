from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "06_true_moving_geometry_R3_stage6_decision_audit"
REPORTS = OUT / "reports"
TABLES = OUT / "tables"
IMAGES = OUT / "images"
SCRIPTS = OUT / "scripts"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def update_bounded_section(readme_path: Path, start: str, end: str, body: str) -> None:
    text = readme_path.read_text(encoding="utf-8")
    replacement = f"{start}\n{body.rstrip()}\n{end}"
    if start in text and end in text:
        before = text.split(start, 1)[0]
        after = text.split(end, 1)[1]
        readme_path.write_text(before + replacement + after, encoding="utf-8")
    else:
        if not text.endswith("\n"):
            text += "\n"
        readme_path.write_text(text + "\n" + replacement + "\n", encoding="utf-8")


def make_svg(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="980" height="420" viewBox="0 0 980 420">
  <rect width="980" height="420" fill="#ffffff"/>
  <style>
    .title { font: 700 24px Arial, sans-serif; fill: #111827; }
    .label { font: 600 16px Arial, sans-serif; fill: #111827; }
    .small { font: 13px Arial, sans-serif; fill: #374151; }
    .box { fill: #f9fafb; stroke: #9ca3af; stroke-width: 1.5; rx: 8; }
    .no { fill: #fee2e2; stroke: #ef4444; stroke-width: 1.5; rx: 8; }
    .yes { fill: #dcfce7; stroke: #22c55e; stroke-width: 1.5; rx: 8; }
    .arrow { stroke: #6b7280; stroke-width: 2; marker-end: url(#arrow); }
  </style>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#6b7280"/>
    </marker>
  </defs>
  <text x="40" y="45" class="title">T012 Stage 6 Path Decision</text>

  <rect x="40" y="85" width="250" height="95" class="box"/>
  <text x="60" y="115" class="label">Numerical pipeline</text>
  <text x="60" y="142" class="small">T004-T008 extraction and</text>
  <text x="60" y="162" class="small">diagnostic displacement pass</text>

  <rect x="365" y="85" width="250" height="95" class="no"/>
  <text x="385" y="115" class="label">Current Jet1 branch</text>
  <text x="385" y="142" class="small">T011 evidence is NEGATIVE</text>
  <text x="385" y="162" class="small">J1 ROI delta lower than J0</text>

  <rect x="690" y="85" width="250" height="95" class="no"/>
  <text x="710" y="115" class="label">Stage 6 now</text>
  <text x="710" y="142" class="small">NO: real Hmax not validated</text>
  <text x="710" y="162" class="small">NO: physics criteria blocked</text>

  <line x1="290" y1="132" x2="365" y2="132" class="arrow"/>
  <line x1="615" y1="132" x2="690" y2="132" class="arrow"/>

  <rect x="215" y="245" width="550" height="105" class="yes"/>
  <text x="240" y="278" class="label">Fastest defensible next path</text>
  <text x="240" y="306" class="small">Repair true-geometry model semantics and acceptance criteria first.</text>
  <text x="240" y="328" class="small">No COMSOL/Stage 6/real Hmax until a separate task explicitly opens that gate.</text>
  <line x1="490" y1="180" x2="490" y2="245" class="arrow"/>
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    for directory in [REPORTS, TABLES, IMAGES, SCRIPTS]:
        directory.mkdir(parents=True, exist_ok=True)

    paths = {
        "r012_review": ROOT / "reviews/20260620_171500_R012_review_and_plan.md",
        "r012_trace": ROOT / "reviews/20260620_171500_R012_run_trace.md",
        "t011_task": ROOT / "tasks/20260620_170000_T011_jet1_threshold_roi_audit.md",
        "t011_final": ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T011_final_report.md",
        "t011_audit": ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T011_A_threshold_source_audit.md",
        "t011_table": ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T011_threshold_recompute.csv",
        "t010_final": ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T010_final_report.md",
        "t010_table": ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T010_recomputed_metrics.csv",
        "t008_final": ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T008_final_report.md",
        "t008_table": ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T008_recomputed_metrics.csv",
        "t006_final": ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T006_final_report.md",
        "t006_table": ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T006_merged_T004_T005_T006_metrics.csv",
        "t007_final": ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T007_final_report.md",
        "t009_final": ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T009_t008_visual_audit_report.md",
    }

    missing = [str(path) for path in paths.values() if not path.exists()]
    t011_rows = read_csv_rows(paths["t011_table"])
    t008_rows = read_csv_rows(paths["t008_table"])
    t006_rows = read_csv_rows(paths["t006_table"])

    j0 = next((row for row in t011_rows if row.get("legacy_case_id") == "J0"), {})
    j1 = next((row for row in t011_rows if row.get("legacy_case_id") == "J1"), {})
    j0_delta = j0.get("roi_max_delta_m", "missing")
    j1_delta = j1.get("roi_max_delta_m", "missing")
    j1_minus_j0 = j1.get("J1_minus_J0_delta_m", "-1.7200266735641012e-06")
    normalized = j1.get("normalized_vs_J0", "0.7165972894943995")
    t008_cases = ",".join(row.get("legacy_case_id", row.get("case_id", "")) for row in t008_rows)
    t006_pass_count = str(sum(1 for row in t006_rows if row.get("extraction_status") == "PASS" and row.get("postprocess_status") == "PASS"))

    ledger_rows = [
        {
            "evidence_block": "raw-array/postprocess repair",
            "source_task": "T004/T005/T006",
            "source_file": str(paths["t006_table"]),
            "status": "PASS",
            "key_values": f"merged_rows={len(t006_rows)}; pass_rows={t006_pass_count}; memory_error_resolved=YES",
            "stage6_effect": "removes extraction/memory blocker but does not validate real Hmax",
            "next_action": "retain pipeline for future gated validation tasks",
        },
        {
            "evidence_block": "baseline/contactline extraction",
            "source_task": "T006",
            "source_file": str(paths["t006_final"]),
            "status": "PASS_WITH_BASELINE_CREDIBILITY_UNKNOWN",
            "key_values": "contact_angle/slip cases PASS; credible_static_baseline=UNKNOWN; credible_micro_motion_baseline=UNKNOWN",
            "stage6_effect": "contactline extraction is available but physical baseline semantics remain unresolved",
            "next_action": "repair model semantics before using outputs as physical Stage 6 evidence",
        },
        {
            "evidence_block": "D0/D1/D2 semantics",
            "source_task": "T007",
            "source_file": str(paths["t007_final"]),
            "status": "PASS",
            "key_values": "D0/D1/D2 displacement semantics recovered; HMAX_IS_REAL_PHYSICAL_OUTPUT=NO",
            "stage6_effect": "supports diagnostic motion semantics only; Stage 6 still blocked",
            "next_action": "use as controlled baseline for semantics repair",
        },
        {
            "evidence_block": "D3/D4/D5 ladder",
            "source_task": "T008",
            "source_file": str(paths["t008_table"]),
            "status": "PASS",
            "key_values": f"cases={t008_cases}; monotonic displacement=YES; HMAX_IS_REAL_PHYSICAL_OUTPUT=NO",
            "stage6_effect": "numerical displacement response is usable diagnostically but not physical Hmax evidence",
            "next_action": "do not expand as sweep; use only as diagnostic reference",
        },
        {
            "evidence_block": "T008 visual audit",
            "source_task": "T009",
            "source_file": str(paths["t009_final"]),
            "status": "PASS",
            "key_values": "SVG/CSV-backed figures match source tables; numeric evidence unchanged",
            "stage6_effect": "removes image-audit blocker for T008 evidence only",
            "next_action": "keep figures as audit support, not Stage 6 authorization",
        },
        {
            "evidence_block": "T010 Jet1 diagnostic",
            "source_task": "T010",
            "source_file": str(paths["t010_table"]),
            "status": "PASS_BUT_NOT_POSITIVE",
            "key_values": f"J0_roi_delta_m={j0_delta}; J1_roi_delta_m={j1_delta}; shape_threshold_crossed=False/False",
            "stage6_effect": "pipeline ran but did not produce Jet1 evidence or real Hmax",
            "next_action": "superseded by T011 threshold audit",
        },
        {
            "evidence_block": "T011 threshold/ROI audit",
            "source_task": "T011",
            "source_file": str(paths["t011_table"]),
            "status": "NEGATIVE",
            "key_values": f"threshold=5e-5 m; J1_minus_J0_delta_m={j1_minus_j0}; normalized_vs_J0={normalized}",
            "stage6_effect": "blocks current Jet1 branch and prevents current path to Stage 6",
            "next_action": "stop current Jet1 expansion; repair model semantics first",
        },
        {
            "evidence_block": "real Hmax status",
            "source_task": "T006/T007/T008/T010/T011",
            "source_file": str(ROOT / "README.md"),
            "status": "NOT_VALIDATED",
            "key_values": "HMAX_IS_REAL_PHYSICAL_OUTPUT=NO across current true-geometry diagnostics",
            "stage6_effect": "real Hmax output remains forbidden",
            "next_action": "define explicit real-Hmax validation criteria in a future gated task",
        },
        {
            "evidence_block": "Stage 6 gate",
            "source_task": "T012",
            "source_file": str(ROOT / "tasks/NEXT_TASK.md"),
            "status": "BLOCKED",
            "key_values": "ALLOW_STAGE6=NO; ALLOW_REAL_HMAX_OUTPUT=NO; ALLOW_STAGE_ADVANCEMENT=NO",
            "stage6_effect": "Stage 6 cannot be entered now",
            "next_action": "execute model-semantics repair plan task before any Stage 6 authorization",
        },
    ]

    ledger_path = TABLES / "T012_stage6_evidence_ledger.csv"
    write_csv(
        ledger_path,
        ["evidence_block", "source_task", "source_file", "status", "key_values", "stage6_effect", "next_action"],
        ledger_rows,
    )

    matrix_rows = [
        {
            "candidate_path": "enter_stage6_now",
            "allowed_now": "NO",
            "reason": "Hard gates forbid Stage 6 and real Hmax; current Jet1 evidence is negative.",
            "evidence_for": "diagnostic extraction and displacement pipeline pass",
            "evidence_against": "T011 negative Jet1 evidence; no real-Hmax validation; model semantics unresolved",
            "required_next_task": "repair_true_geometry_model_semantics",
            "reviewer_gate": "ALLOW_STAGE6 must remain NO until a future task explicitly changes it",
        },
        {
            "candidate_path": "continue_current_jet1_branch",
            "allowed_now": "NO",
            "reason": "T011 found J1 lower than J0 and neither case crossed the recovered threshold.",
            "evidence_for": "T010 pipeline executed successfully",
            "evidence_against": "J1_VS_J0_EVIDENCE=NEGATIVE; ALLOW_NEXT_TRUE_GEOMETRY_JET1=NO",
            "required_next_task": "none under current metric",
            "reviewer_gate": "explicit new Review Agent rationale required to reopen Jet1",
        },
        {
            "candidate_path": "repair_true_geometry_model_semantics",
            "allowed_now": "YES",
            "reason": "This is the narrowest path that addresses the current physics-criteria blocker without claiming Stage 6.",
            "evidence_for": "numerical/postprocess pipeline is usable; current blocker is semantics/interpretation",
            "evidence_against": "does not itself produce Stage 6 or real Hmax",
            "required_next_task": "audit and repair true-geometry ALE/ring/contactline/ROI semantics and define acceptance criteria",
            "reviewer_gate": "future task may allow only bounded no-Stage6 model-semantics repair",
        },
        {
            "candidate_path": "redefine_jet1_roi_threshold_with_explicit_review_approval",
            "allowed_now": "NO",
            "reason": "Current task does not authorize threshold redefinition and T011 recovered the existing threshold coherently.",
            "evidence_for": "5C rules are diagnostic analogues only in true geometry",
            "evidence_against": "changing threshold now would be post hoc against negative evidence",
            "required_next_task": "separate Review Agent-approved threshold-normalization task if scientifically justified",
            "reviewer_gate": "requires explicit altered-threshold rationale before any Jet1 diagnostic rerun",
        },
        {
            "candidate_path": "redirect_to_non_jet1_stage6_mechanism",
            "allowed_now": "NO",
            "reason": "No alternative Stage 6 mechanism has been evidenced or validated in the current true-geometry branch.",
            "evidence_for": "current Jet1 path is negative, so alternatives may be worth scoping later",
            "evidence_against": "no validated mechanism; real Hmax remains forbidden",
            "required_next_task": "only after model-semantics repair or a separate mechanism-scoping task",
            "reviewer_gate": "requires explicit Review Agent mechanism definition and no real-Hmax claim",
        },
    ]

    matrix_path = TABLES / "T012_stage6_path_decision_matrix.csv"
    write_csv(
        matrix_path,
        ["candidate_path", "allowed_now", "reason", "evidence_for", "evidence_against", "required_next_task", "reviewer_gate"],
        matrix_rows,
    )

    gates = {
        "T012_STATUS": "PASS",
        "CURRENT_PRIMARY_BLOCKER": "model_semantics_and_physical_interpretation",
        "CURRENT_TRUE_GEOMETRY_JET1_BRANCH_STATUS": "NEGATIVE",
        "FASTEST_STAGE6_PATH": "repair_true_geometry_model_semantics",
        "ALLOW_STAGE6_NOW": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
        "ALLOW_CONTINUE_CURRENT_JET1_BRANCH": "NO",
        "ALLOW_MODEL_SEMANTICS_REPAIR_TASK": "YES",
        "ALLOW_REDEFINE_JET1_THRESHOLD_TASK": "NO",
        "ALLOW_REDIRECT_TO_NON_JET1_STAGE6_MECHANISM": "NO",
        "RECOMMENDED_NEXT_TASK": "Bounded true-geometry model-semantics repair: audit ALE ring motion, WettedWall/contactline semantics, interface/ROI definitions, and real-Hmax acceptance criteria without Stage 6 or broad sweep.",
    }

    gate_path = REPORTS / "T012_gate_summary.json"
    gate_path.write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")

    svg_path = IMAGES / "T012_stage6_decision_map.svg"
    make_svg(svg_path)

    final_report = f"""# T012 Final Report

- Run id: `{run_id}`
- Scope: Stage 6 path decision and model-semantics audit only.
- No COMSOL run, Stage 6, parameter sweep, Jet1 expansion, Jet1 physical conclusion, or real Hmax output was performed.

## Gate Values

- `T012_STATUS = PASS`
- `CURRENT_PRIMARY_BLOCKER = model_semantics_and_physical_interpretation`
- `CURRENT_TRUE_GEOMETRY_JET1_BRANCH_STATUS = NEGATIVE`
- `FASTEST_STAGE6_PATH = repair_true_geometry_model_semantics`
- `ALLOW_STAGE6_NOW = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_CONTINUE_CURRENT_JET1_BRANCH = NO`
- `ALLOW_MODEL_SEMANTICS_REPAIR_TASK = YES`
- `ALLOW_REDEFINE_JET1_THRESHOLD_TASK = NO`
- `ALLOW_REDIRECT_TO_NON_JET1_STAGE6_MECHANISM = NO`
- `RECOMMENDED_NEXT_TASK = Bounded true-geometry model-semantics repair: audit ALE ring motion, WettedWall/contactline semantics, interface/ROI definitions, and real-Hmax acceptance criteria without Stage 6 or broad sweep.`

## Decision

The current blocker is not numerical runtime, raw-array extraction, postprocessing memory, or image audit. Those blockers are either repaired or bounded by previous evidence. The current blocker is model semantics plus physical interpretation: the true-geometry diagnostics still do not establish a validated physical fountain-height observable, and T011 shows the current Jet1 branch is negative under its recovered ROI/threshold metric.

The current true-geometry Jet1 branch is `NEGATIVE`, not merely incomplete. T011 reports J0 ROI max delta `{j0_delta}` m, J1 ROI max delta `{j1_delta}` m, and J1 minus J0 `{j1_minus_j0}` m. Neither case crosses the recovered `5e-5 m` threshold, and J1 is lower than J0.

Stage 6 cannot be entered through any current evidence-backed route. The fastest scientifically defensible path is a bounded true-geometry model-semantics repair task. That task should define and verify the physical meaning of ALE ring motion, WettedWall/contactline behavior, interface/ROI extraction, and real-Hmax acceptance criteria before any Stage 6 or real-Hmax-producing run is opened.

## Required Outputs

- Evidence ledger: `{ledger_path}`
- Decision matrix: `{matrix_path}`
- Gate summary: `{gate_path}`
- Decision map: `{svg_path}`

## Input Coverage

Missing required inputs: `{'; '.join(missing) if missing else 'none'}`

Files inspected include:

- `{paths['r012_review']}`
- `{paths['r012_trace']}`
- `{paths['t011_task']}`
- `{paths['t011_final']}`
- `{paths['t011_audit']}`
- `{paths['t011_table']}`
- `{paths['t010_final']}`
- `{paths['t010_table']}`
- `{paths['t008_final']}`
- `{paths['t008_table']}`
- `{paths['t006_final']}`
- `{paths['t006_table']}`
- `{paths['t007_final']}`
- `{paths['t009_final']}`
- `{ROOT / 'README.md'}`

## Next Recommended Task

Create a bounded true-geometry model-semantics repair task. It should not run Stage 6, should not output real Hmax, should not broaden the displacement ladder, and should not continue the current Jet1 branch. It should produce explicit acceptance criteria for when a later task may reopen Stage 6 consideration.
"""
    final_report_path = REPORTS / "T012_final_report.md"
    final_report_path.write_text(final_report, encoding="utf-8")

    readme_body = f"""## TRUE_GEOMETRY_R3_STAGE6_DECISION_AUDIT

- Run id: `{run_id}`
- Scope: T012 Stage 6 path decision and model-semantics audit only.
- T012 status: `PASS`
- `CURRENT_PRIMARY_BLOCKER = model_semantics_and_physical_interpretation`
- `CURRENT_TRUE_GEOMETRY_JET1_BRANCH_STATUS = NEGATIVE`
- `FASTEST_STAGE6_PATH = repair_true_geometry_model_semantics`
- `ALLOW_STAGE6_NOW = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_CONTINUE_CURRENT_JET1_BRANCH = NO`
- `ALLOW_MODEL_SEMANTICS_REPAIR_TASK = YES`
- `ALLOW_REDEFINE_JET1_THRESHOLD_TASK = NO`
- `ALLOW_REDIRECT_TO_NON_JET1_STAGE6_MECHANISM = NO`
- Final report: `{final_report_path}`
- Evidence ledger: `{ledger_path}`
- Decision matrix: `{matrix_path}`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- No further current-metric Jet1 branch expansion is allowed.
"""
    update_bounded_section(
        ROOT / "README.md",
        "<!-- TRUE_GEOMETRY_R3_STAGE6_DECISION_AUDIT:START -->",
        "<!-- TRUE_GEOMETRY_R3_STAGE6_DECISION_AUDIT:END -->",
        readme_body,
    )


if __name__ == "__main__":
    main()
