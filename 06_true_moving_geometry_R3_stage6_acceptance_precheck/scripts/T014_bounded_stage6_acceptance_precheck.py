from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "06_true_moving_geometry_R3_stage6_acceptance_precheck"
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


def exists(path: Path) -> str:
    return "YES" if path.exists() else "NO"


def group_exists(paths: list[Path]) -> str:
    if not paths:
        return "NO"
    count = sum(1 for path in paths if path.exists())
    if count == len(paths):
        return "YES"
    if count:
        return "PARTIAL"
    return "NO"


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


def write_svg(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="520" viewBox="0 0 1080 520">
  <rect width="1080" height="520" fill="#ffffff"/>
  <style>
    .title { font: 700 24px Arial, sans-serif; fill: #111827; }
    .label { font: 700 16px Arial, sans-serif; fill: #111827; }
    .small { font: 13px Arial, sans-serif; fill: #374151; }
    .pass { fill: #dcfce7; stroke: #22c55e; stroke-width: 1.5; rx: 8; }
    .partial { fill: #fef3c7; stroke: #f59e0b; stroke-width: 1.5; rx: 8; }
    .fail { fill: #fee2e2; stroke: #ef4444; stroke-width: 1.5; rx: 8; }
    .arrow { stroke: #6b7280; stroke-width: 2; marker-end: url(#arrow); }
  </style>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#6b7280"/>
    </marker>
  </defs>
  <text x="40" y="45" class="title">T014 Bounded No-Stage6 Acceptance Precheck</text>

  <rect x="50" y="90" width="220" height="88" class="partial"/>
  <text x="70" y="122" class="label">Ring motion</text>
  <text x="70" y="150" class="small">PARTIAL</text>

  <rect x="310" y="90" width="220" height="88" class="partial"/>
  <text x="330" y="122" class="label">Non-double-counting</text>
  <text x="330" y="150" class="small">PARTIAL</text>

  <rect x="570" y="90" width="220" height="88" class="fail"/>
  <text x="590" y="122" class="label">Contactline</text>
  <text x="590" y="150" class="small">FAIL</text>

  <rect x="830" y="90" width="220" height="88" class="partial"/>
  <text x="850" y="122" class="label">Interface extraction</text>
  <text x="850" y="150" class="small">PARTIAL</text>

  <rect x="195" y="270" width="260" height="96" class="fail"/>
  <text x="215" y="302" class="label">Real Hmax executable now</text>
  <text x="215" y="330" class="small">NO: sensitivity and physical</text>
  <text x="215" y="350" class="small">contactline validity missing</text>

  <rect x="625" y="270" width="260" height="96" class="fail"/>
  <text x="645" y="302" class="label">Bounded Stage6 candidate</text>
  <text x="645" y="330" class="small">NO: precheck did not pass</text>

  <line x1="270" y1="134" x2="310" y2="134" class="arrow"/>
  <line x1="530" y1="134" x2="570" y2="134" class="arrow"/>
  <line x1="790" y1="134" x2="830" y2="134" class="arrow"/>
  <line x1="540" y1="178" x2="325" y2="270" class="arrow"/>
  <line x1="540" y1="178" x2="755" y2="270" class="arrow"/>
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    for directory in [REPORTS, TABLES, IMAGES, SCRIPTS]:
        directory.mkdir(parents=True, exist_ok=True)

    inputs = {
        "r014_review": ROOT / "reviews/20260620_175000_R014_review_and_plan.md",
        "r014_trace": ROOT / "reviews/20260620_175000_R014_run_trace.md",
        "t013_task": ROOT / "tasks/20260620_173000_T013_true_geometry_model_semantics_repair.md",
        "t013_final": ROOT / "06_true_moving_geometry_R3_model_semantics_repair/reports/T013_final_report.md",
        "t013_criteria": ROOT / "06_true_moving_geometry_R3_model_semantics_repair/reports/T013_stage6_acceptance_criteria.md",
        "t013_matrix": ROOT / "06_true_moving_geometry_R3_model_semantics_repair/tables/T013_semantics_consistency_matrix.csv",
        "t013_inventory": ROOT / "06_true_moving_geometry_R3_model_semantics_repair/tables/T013_semantics_source_inventory.csv",
        "t012_final": ROOT / "06_true_moving_geometry_R3_stage6_decision_audit/reports/T012_final_report.md",
        "t012_ledger": ROOT / "06_true_moving_geometry_R3_stage6_decision_audit/tables/T012_stage6_evidence_ledger.csv",
        "t006_merged": ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute/tables/T006_merged_T004_T005_T006_metrics.csv",
        "t008_metrics": ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/tables/T008_recomputed_metrics.csv",
        "t011_table": ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T011_threshold_recompute.csv",
        "t008_d5_java": ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/models/T008_D5_20260620_161207.java",
        "t004_script": ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute/scripts/T004_raw_array_extraction_recompute.py",
        "t010_script": ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/scripts/T010_true_geometry_jet1_diagnostic.py",
        "interface_audit": ROOT / "06_true_moving_geometry_R2_interface_noise_isolation/01_extraction_algorithm_audit/reports/interface_extraction_algorithm_audit.md",
        "wettedwall_report": ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation/04_wettedwall_contactline_controls/reports/wettedwall_contactline_controls_report.md",
    }

    t006_rows = read_csv_rows(inputs["t006_merged"])
    t008_rows = read_csv_rows(inputs["t008_metrics"])
    t011_rows = read_csv_rows(inputs["t011_table"])

    t008_arrays = [Path(row.get("array_path", "")) for row in t008_rows if row.get("legacy_case_id") in {"D3", "D4", "D5"}]
    t008_logs = [ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/logs" / f"T008_{row.get('case_id')}_20260620_161207.log" for row in t008_rows if row.get("case_id")]
    t008_figures = [
        ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T008_ladder_displacement_response.png",
        ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T008_ladder_error_summary.png",
        ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/images/T008_interface_quality_summary.png",
    ]

    t006_arrays = [Path(row.get("array_path", "")) for row in t006_rows if row.get("array_path")]
    t006_logs = [ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute/logs" / f"T006_{row.get('case_id')}_20260620_153612.log" for row in t006_rows if row.get("source_task") == "T006"]
    t006_figures = [
        ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute/images/T006_interface_quality_summary.png",
        ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute/images/T006_extraction_status_summary.png",
        ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute/images/T006_baseline_discrimination_summary.png",
    ]

    t010_arrays = [
        ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/arrays/T010_J0_static_baseline_for_jet1_diagnostic_20260620_164644.npz",
        ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/arrays/T010_J1_true_geometry_jet1_diagnostic_20260620_164644.npz",
    ]
    t010_logs = [
        ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/logs/T010_J0_static_baseline_for_jet1_diagnostic_20260620_164644.log",
        ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/logs/T010_J1_true_geometry_jet1_diagnostic_20260620_164644.log",
    ]
    t010_figures = [
        ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/images/T010_diagnostic_shape_summary.svg",
        ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/images/T011_j0_j1_roi_delta_comparison.svg",
    ]

    candidates = [
        {
            "candidate_id": "T008_D5_best_existing_ALE_motion_candidate",
            "source_task": "T008",
            "source_model_or_table": str(ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/models/T008_D5_20260620_161207.mph"),
            "reason_selected": "largest existing validated diagnostic ALE displacement in D3/D4/D5 ladder",
            "available_arrays": group_exists(t008_arrays),
            "available_logs": group_exists(t008_logs),
            "available_figures": group_exists(t008_figures),
            "allowed_for_precheck": "YES_DIAGNOSTIC_ONLY",
            "notes": "motion evidence is diagnostic; not real Hmax",
        },
        {
            "candidate_id": "T006_control_baseline_set",
            "source_task": "T004/T005/T006",
            "source_model_or_table": str(inputs["t006_merged"]),
            "reason_selected": "best existing static/contactline/control table with repaired extraction",
            "available_arrays": group_exists(t006_arrays),
            "available_logs": group_exists(t006_logs),
            "available_figures": group_exists(t006_figures),
            "allowed_for_precheck": "YES_CONTROL_EVIDENCE_ONLY",
            "notes": "baseline credibility remains unknown in T006",
        },
        {
            "candidate_id": "T011_current_Jet1_negative_reference",
            "source_task": "T010/T011",
            "source_model_or_table": str(inputs["t011_table"]),
            "reason_selected": "required negative-control/reference for current Jet1 branch",
            "available_arrays": group_exists(t010_arrays),
            "available_logs": group_exists(t010_logs),
            "available_figures": group_exists(t010_figures),
            "allowed_for_precheck": "YES_NEGATIVE_REFERENCE_ONLY",
            "notes": "not positive Jet1 evidence and not allowed as current branch continuation",
        },
    ]
    candidate_path = TABLES / "T014_candidate_evidence_manifest.csv"
    write_csv(
        candidate_path,
        ["candidate_id", "source_task", "source_model_or_table", "reason_selected", "available_arrays", "available_logs", "available_figures", "allowed_for_precheck", "notes"],
        candidates,
    )

    matrix_rows = [
        {
            "criterion": "physical_ring_motion_validity",
            "current_answer": "PARTIAL",
            "required_for_stage6": "YES",
            "evidence_for": "T008 D3/D4/D5 measured displacements match expected ALE diagnostic displacements; Java export contains dx=[0,-Vring*t] on ring boundaries",
            "evidence_against": "validation is short diagnostic motion only; no physical-height or free-fall acceptance proof",
            "blocking_gap": "physical motion must be tied to a real-Hmax candidate with documented tolerance and controls",
            "precheck_result": "PARTIAL",
            "next_action": "keep candidate as diagnostic motion input only",
        },
        {
            "criterion": "ALE_vs_WettedWall_non_double_counting",
            "current_answer": "PARTIAL",
            "required_for_stage6": "YES",
            "evidence_for": "T013 defines ALE dx as geometry proof and WettedWall utr as wall-frame/contactline condition",
            "evidence_against": "existing evidence has both dx and utr but no executed non-double-counting acceptance check",
            "blocking_gap": "wall-frame convention must be verified for any future candidate model",
            "precheck_result": "PARTIAL",
            "next_action": "run metadata/script audit focused on dx/utr convention before candidate task",
        },
        {
            "criterion": "boundary_contactline_validity",
            "current_answer": "NO",
            "required_for_stage6": "YES",
            "evidence_for": "exports show NavierSlip, theta=pi/2, and utr=-Vring",
            "evidence_against": "R3 contactline report found no clear physical WettedWall cases",
            "blocking_gap": "contactline physical classification is not passed",
            "precheck_result": "FAIL",
            "next_action": "repair or classify contactline setting before any Stage6 candidate",
        },
        {
            "criterion": "contact_angle_slip_control_validity",
            "current_answer": "PARTIAL",
            "required_for_stage6": "YES",
            "evidence_for": "T006 W2/W3/W4/W7/W8 extraction and postprocess pass",
            "evidence_against": "T006 credible static and micro-motion baselines remain UNKNOWN",
            "blocking_gap": "controls are diagnostic and not yet physical-sensitivity acceptance evidence",
            "precheck_result": "PARTIAL",
            "next_action": "classify each contact-angle/slip case as physical control, numerical control, or excluded",
        },
        {
            "criterion": "connected_interface_extraction_validity",
            "current_answer": "PARTIAL",
            "required_for_stage6": "YES",
            "evidence_for": "R2/T004 extraction excludes known raw-global contamination and T004-T006 postprocess pass",
            "evidence_against": "extractor has not passed real-Hmax visual, mesh, and control-case acceptance",
            "blocking_gap": "connected-interface extraction remains diagnostic",
            "precheck_result": "PARTIAL",
            "next_action": "add real-Hmax extractor feasibility checks without outputting real Hmax",
        },
        {
            "criterion": "ROI_extraction_validity",
            "current_answer": "NO",
            "required_for_stage6": "YES_IF_ROI_USED",
            "evidence_for": "T010/T011 provide auditable diagnostic center-hole/inner-edge ROI",
            "evidence_against": "T011 says fixed-geometry ROI is a true-geometry diagnostic analogue only and current Jet1 evidence is negative",
            "blocking_gap": "no physical ROI/domain rule for Stage6 Hmax is passed",
            "precheck_result": "FAIL",
            "next_action": "do not use current Jet1 ROI branch for Stage6",
        },
        {
            "criterion": "real_Hmax_definition_executability",
            "current_answer": "NO",
            "required_for_stage6": "YES",
            "evidence_for": "arrays, z0 convention, time windows, and diagnostic extractor code exist",
            "evidence_against": "missing mesh/time-step sensitivity and physical contactline validity; no candidate passed T013 criteria",
            "blocking_gap": "real-Hmax definition cannot be executed as real output now",
            "precheck_result": "FAIL",
            "next_action": "keep all height-like values diagnostic until criteria pass",
        },
        {
            "criterion": "image_table_log_audit_completeness",
            "current_answer": "PARTIAL",
            "required_for_stage6": "YES",
            "evidence_for": "T006/T008/T010/T011 include arrays/tables/logs/figures for diagnostic evidence",
            "evidence_against": "no Stage6-candidate-specific manifest or mesh/time-step sensitivity audit exists",
            "blocking_gap": "audit package is not complete for a real-Hmax candidate",
            "precheck_result": "PARTIAL",
            "next_action": "future precheck must include candidate-specific manifest",
        },
        {
            "criterion": "minimum_control_case_completeness",
            "current_answer": "PARTIAL",
            "required_for_stage6": "YES",
            "evidence_for": "zero/micro displacement, static/contactline controls, and negative Jet1 reference exist",
            "evidence_against": "mesh/time-step sensitivity and physical contactline acceptance are missing",
            "blocking_gap": "minimum controls are incomplete",
            "precheck_result": "PARTIAL",
            "next_action": "complete control checklist before Stage6 candidate",
        },
        {
            "criterion": "Jet1_requirement_status",
            "current_answer": "CURRENT_JET1_BRANCH_ALLOWED=NO",
            "required_for_stage6": "Jet1 not categorically required, but any mechanism must be explicitly defined",
            "evidence_for": "T013 criteria allow non-Jet1 mechanism; T011 closes current Jet1 branch",
            "evidence_against": "no alternative non-Jet1 Stage6 mechanism is currently validated",
            "blocking_gap": "future candidate must define mechanism without reopening current Jet1 branch",
            "precheck_result": "PASS",
            "next_action": "keep current Jet1 branch closed",
        },
    ]
    matrix_path = TABLES / "T014_acceptance_precheck_matrix.csv"
    write_csv(
        matrix_path,
        ["criterion", "current_answer", "required_for_stage6", "evidence_for", "evidence_against", "blocking_gap", "precheck_result", "next_action"],
        matrix_rows,
    )

    feasibility_rows = [
        {
            "candidate_id": "T008_D5_best_existing_ALE_motion_candidate",
            "has_connected_interface_source": "YES",
            "has_z0_reference": "YES",
            "has_artifact_exclusion_rule": "PARTIAL",
            "has_roi_or_domain_rule": "PARTIAL",
            "has_time_window": "YES",
            "has_visual_audit_support": "YES",
            "has_mesh_or_timestep_sensitivity": "NO",
            "executable_as_real_hmax_now": "NO",
            "reason": "diagnostic arrays and figures exist, but contactline validity and mesh/time-step sensitivity are missing",
        },
        {
            "candidate_id": "T006_control_baseline_set",
            "has_connected_interface_source": "YES",
            "has_z0_reference": "YES",
            "has_artifact_exclusion_rule": "PARTIAL",
            "has_roi_or_domain_rule": "NO",
            "has_time_window": "YES",
            "has_visual_audit_support": "PARTIAL",
            "has_mesh_or_timestep_sensitivity": "NO",
            "executable_as_real_hmax_now": "NO",
            "reason": "controls are useful diagnostics, but baseline credibility remains unknown and no Hmax domain rule is passed",
        },
        {
            "candidate_id": "T011_current_Jet1_negative_reference",
            "has_connected_interface_source": "YES",
            "has_z0_reference": "YES",
            "has_artifact_exclusion_rule": "PARTIAL",
            "has_roi_or_domain_rule": "PARTIAL",
            "has_time_window": "YES",
            "has_visual_audit_support": "YES",
            "has_mesh_or_timestep_sensitivity": "NO",
            "executable_as_real_hmax_now": "NO",
            "reason": "current Jet1 ROI is diagnostic-only and negative; cannot be used as real-Hmax route",
        },
    ]
    feasibility_path = TABLES / "T014_nonreal_hmax_extractor_feasibility.csv"
    write_csv(
        feasibility_path,
        [
            "candidate_id",
            "has_connected_interface_source",
            "has_z0_reference",
            "has_artifact_exclusion_rule",
            "has_roi_or_domain_rule",
            "has_time_window",
            "has_visual_audit_support",
            "has_mesh_or_timestep_sensitivity",
            "executable_as_real_hmax_now",
            "reason",
        ],
        feasibility_rows,
    )

    svg_path = IMAGES / "T014_acceptance_precheck_decision_map.svg"
    write_svg(svg_path)

    gates = {
        "T014_STATUS": "PASS",
        "ACCEPTANCE_PRECHECK_COMPLETED": "YES",
        "PHYSICAL_RING_MOTION_VALIDITY": "PARTIAL",
        "ALE_WETTEDWALL_NON_DOUBLE_COUNTING": "PARTIAL",
        "BOUNDARY_CONTACTLINE_VALIDITY": "NO",
        "CONNECTED_INTERFACE_EXTRACTION_VALIDITY": "PARTIAL",
        "REAL_HMAX_EXECUTABLE_NOW": "NO",
        "MINIMUM_CONTROLS_COMPLETE": "PARTIAL",
        "CURRENT_JET1_BRANCH_ALLOWED": "NO",
        "ALLOW_STAGE6_NOW": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
        "ALLOW_BOUNDED_STAGE6_CANDIDATE_TASK": "NO",
        "RECOMMENDED_NEXT_TASK": "Run a bounded no-Stage6 contactline/control-completeness repair task: classify WettedWall/contactline physical validity, verify dx/utr non-double-counting, and add or identify mesh/time-step sensitivity evidence without outputting real Hmax.",
    }
    gate_path = REPORTS / "T014_gate_summary.json"
    gate_path.write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")

    missing = [str(path) for path in inputs.values() if not path.exists()]
    final_path = REPORTS / "T014_final_report.md"
    final_report = f"""# T014 Final Report

- Run id: `{run_id}`
- Scope: bounded no-Stage6 acceptance precheck against existing evidence.
- No COMSOL run, Stage 6, parameter sweep, current Jet1 continuation, Jet1 physical conclusion, or real Hmax output was performed.

## Gate Values

- `T014_STATUS = PASS`
- `ACCEPTANCE_PRECHECK_COMPLETED = YES`
- `PHYSICAL_RING_MOTION_VALIDITY = PARTIAL`
- `ALE_WETTEDWALL_NON_DOUBLE_COUNTING = PARTIAL`
- `BOUNDARY_CONTACTLINE_VALIDITY = NO`
- `CONNECTED_INTERFACE_EXTRACTION_VALIDITY = PARTIAL`
- `REAL_HMAX_EXECUTABLE_NOW = NO`
- `MINIMUM_CONTROLS_COMPLETE = PARTIAL`
- `CURRENT_JET1_BRANCH_ALLOWED = NO`
- `ALLOW_STAGE6_NOW = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_BOUNDED_STAGE6_CANDIDATE_TASK = NO`

## Precheck Decision

No existing true-geometry candidate evidence is currently close enough to justify a bounded Stage 6 candidate task. T008/T007 provide useful diagnostic ALE motion evidence, and T004-T006 provide repaired extraction/control evidence, but the acceptance precheck fails the decisive physical-contactline and real-Hmax executability criteria.

The current Jet1 branch remains closed. T011/T014 may be used only as negative-control/reference evidence, not as positive Jet1 evidence and not as a real-Hmax route.

## Outputs

- Candidate manifest: `{candidate_path}`
- Acceptance precheck matrix: `{matrix_path}`
- Non-real-Hmax extractor feasibility: `{feasibility_path}`
- Decision map: `{svg_path}`
- Gate summary: `{gate_path}`

## Input Coverage

Missing inputs: `{'; '.join(missing) if missing else 'none'}`

## Next Recommended Task

Run a bounded no-Stage6 contactline/control-completeness repair task: classify WettedWall/contactline physical validity, verify dx/utr non-double-counting, and add or identify mesh/time-step sensitivity evidence without outputting real Hmax.
"""
    final_path.write_text(final_report, encoding="utf-8")

    readme_body = f"""## TRUE_GEOMETRY_R3_STAGE6_ACCEPTANCE_PRECHECK

- Run id: `{run_id}`
- Scope: T014 bounded no-Stage6 acceptance precheck against existing true-geometry evidence.
- T014 status: `PASS`
- `ACCEPTANCE_PRECHECK_COMPLETED = YES`
- `PHYSICAL_RING_MOTION_VALIDITY = PARTIAL`
- `ALE_WETTEDWALL_NON_DOUBLE_COUNTING = PARTIAL`
- `BOUNDARY_CONTACTLINE_VALIDITY = NO`
- `CONNECTED_INTERFACE_EXTRACTION_VALIDITY = PARTIAL`
- `REAL_HMAX_EXECUTABLE_NOW = NO`
- `MINIMUM_CONTROLS_COMPLETE = PARTIAL`
- `CURRENT_JET1_BRANCH_ALLOWED = NO`
- `ALLOW_STAGE6_NOW = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_BOUNDED_STAGE6_CANDIDATE_TASK = NO`
- Final report: `{final_path}`
- Candidate manifest: `{candidate_path}`
- Acceptance precheck matrix: `{matrix_path}`
- Non-real-Hmax feasibility table: `{feasibility_path}`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- Current Jet1 branch remains closed.
"""
    update_bounded_section(
        ROOT / "README.md",
        "<!-- TRUE_GEOMETRY_R3_STAGE6_ACCEPTANCE_PRECHECK:START -->",
        "<!-- TRUE_GEOMETRY_R3_STAGE6_ACCEPTANCE_PRECHECK:END -->",
        readme_body,
    )


if __name__ == "__main__":
    main()
