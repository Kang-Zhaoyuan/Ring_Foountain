from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "06_true_moving_geometry_R3_model_semantics_repair"
REPORTS = OUT / "reports"
TABLES = OUT / "tables"
IMAGES = OUT / "images"
SCRIPTS = OUT / "scripts"


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def bool_text(value: bool) -> str:
    return "YES" if value else "NO"


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
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="520" viewBox="0 0 1040 520">
  <rect width="1040" height="520" fill="#ffffff"/>
  <style>
    .title { font: 700 24px Arial, sans-serif; fill: #111827; }
    .label { font: 700 16px Arial, sans-serif; fill: #111827; }
    .small { font: 13px Arial, sans-serif; fill: #374151; }
    .partial { fill: #fef3c7; stroke: #f59e0b; stroke-width: 1.5; rx: 8; }
    .no { fill: #fee2e2; stroke: #ef4444; stroke-width: 1.5; rx: 8; }
    .yes { fill: #dcfce7; stroke: #22c55e; stroke-width: 1.5; rx: 8; }
    .arrow { stroke: #6b7280; stroke-width: 2; marker-end: url(#arrow); }
  </style>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#6b7280"/>
    </marker>
  </defs>
  <text x="40" y="45" class="title">T013 Model Semantics Repair Status</text>

  <rect x="55" y="85" width="260" height="100" class="partial"/>
  <text x="75" y="118" class="label">ALE ring motion</text>
  <text x="75" y="146" class="small">PARTIAL: dx and measured motion</text>
  <text x="75" y="166" class="small">are diagnostic, not real Hmax proof</text>

  <rect x="390" y="85" width="260" height="100" class="partial"/>
  <text x="410" y="118" class="label">Contactline semantics</text>
  <text x="410" y="146" class="small">PARTIAL/UNKNOWN: settings exist,</text>
  <text x="410" y="166" class="small">physical acceptance not established</text>

  <rect x="725" y="85" width="260" height="100" class="partial"/>
  <text x="745" y="118" class="label">Interface/ROI extraction</text>
  <text x="745" y="146" class="small">PARTIAL: diagnostic extraction passes,</text>
  <text x="745" y="166" class="small">physical height validity not complete</text>

  <rect x="220" y="285" width="260" height="100" class="no"/>
  <text x="240" y="318" class="label">Real Hmax output</text>
  <text x="240" y="346" class="small">NO: definition and validation</text>
  <text x="240" y="366" class="small">criteria are not yet passed</text>

  <rect x="560" y="285" width="260" height="100" class="yes"/>
  <text x="580" y="318" class="label">Next allowed step</text>
  <text x="580" y="346" class="small">YES: bounded no-Stage6</text>
  <text x="580" y="366" class="small">acceptance precheck only</text>

  <line x1="315" y1="135" x2="390" y2="135" class="arrow"/>
  <line x1="650" y1="135" x2="725" y2="135" class="arrow"/>
  <line x1="520" y1="185" x2="390" y2="285" class="arrow"/>
  <line x1="520" y1="185" x2="650" y2="285" class="arrow"/>
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    for directory in [REPORTS, TABLES, IMAGES, SCRIPTS]:
        directory.mkdir(parents=True, exist_ok=True)

    sources = {
        "r013_review": ROOT / "reviews/20260620_173000_R013_review_and_plan.md",
        "r013_trace": ROOT / "reviews/20260620_173000_R013_run_trace.md",
        "t012_task": ROOT / "tasks/20260620_171500_T012_stage6_path_decision_audit.md",
        "t012_final": ROOT / "06_true_moving_geometry_R3_stage6_decision_audit/reports/T012_final_report.md",
        "t012_ledger": ROOT / "06_true_moving_geometry_R3_stage6_decision_audit/tables/T012_stage6_evidence_ledger.csv",
        "t012_matrix": ROOT / "06_true_moving_geometry_R3_stage6_decision_audit/tables/T012_stage6_path_decision_matrix.csv",
        "t011_final": ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T011_final_report.md",
        "t011_table": ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/tables/T011_threshold_recompute.csv",
        "t010_final": ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T010_final_report.md",
        "t008_final": ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T008_final_report.md",
        "t006_final": ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute/reports/T006_final_report.md",
        "campaign_final": ROOT / "06_true_moving_geometry_campaign/reports/true_moving_geometry_campaign_final_report.md",
        "ring_smoke": ROOT / "06_true_moving_geometry_campaign/03_true_moving_ring_smoke/reports/true_moving_ring_smoke_report.md",
        "stability_report": ROOT / "06_true_moving_geometry_campaign/04_true_moving_ring_stability/reports/true_moving_ring_stability_report.md",
        "true_vs_fixed_review": ROOT / "06_true_moving_geometry_campaign/05_physical_validity_review/true_vs_fixed_geometry_review.md",
        "t008_d5_java": ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/models/T008_D5_20260620_161207.java",
        "t007_semantics": ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T007_A_d0_d1_d2_semantics.md",
        "t008_semantics": ROOT / "06_true_moving_geometry_R3_diagnostic_displacement_regression/reports/T008_A_ladder_semantics.md",
        "interface_audit": ROOT / "06_true_moving_geometry_R2_interface_noise_isolation/01_extraction_algorithm_audit/reports/interface_extraction_algorithm_audit.md",
        "wettedwall_report": ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation/04_wettedwall_contactline_controls/reports/wettedwall_contactline_controls_report.md",
        "w0_java": ROOT / "06_true_moving_geometry_R3_ring_contactline_isolation/04_wettedwall_contactline_controls/exports/W0_current_wettedwall.java",
        "t004_script": ROOT / "06_true_moving_geometry_R3_raw_array_extraction_recompute/scripts/T004_raw_array_extraction_recompute.py",
        "t010_script": ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/scripts/T010_true_geometry_jet1_diagnostic.py",
        "t011_audit": ROOT / "06_true_moving_geometry_R3_true_geometry_jet1_diagnostic/reports/T011_A_threshold_source_audit.md",
        "readme": ROOT / "README.md",
    }

    t008_java = read_text(sources["t008_d5_java"])
    w0_java = read_text(sources["w0_java"])
    t004_script = read_text(sources["t004_script"])
    t010_script = read_text(sources["t010_script"])

    has_ale_dx = 'set("dx", new String[]{"0", "-Vring*t"})' in t008_java
    has_wettedwall_utr = 'set("utr", new String[]{"0", "-Vring", "0"})' in t008_java
    has_ring_selection = "feature(\"move_ring\").selection().set(4, 5, 6, 7)" in t008_java
    has_contact_angle = 'set("thetaw", "pi/2")' in t008_java or 'set("thetaw", "pi/2")' in w0_java
    has_navier_slip = "NavierSlip" in t008_java or "NavierSlip" in w0_java
    has_binned_extractor = "npz_binned_crossing_160" in t004_script
    has_roi_diagnostic_guard = "diagnostic_only" in t010_script and "real_hmax_excluded" in t010_script

    inventory_rows = [
        {
            "source_file": str(sources["campaign_final"]),
            "exists": bool_text(sources["campaign_final"].exists()),
            "source_type": "report",
            "semantics_area": "true_geometry_campaign",
            "key_claim_or_setting": "PASS_MINIMAL; ALLOW_STAGE6_PARAMETER_SWEEP=NO; ALLOW_REAL_HMAX_OUTPUT=NO",
            "relevance": "establishes branch transition but not real Hmax",
            "uncertainty": "minimal campaign only",
        },
        {
            "source_file": str(sources["ring_smoke"]),
            "exists": bool_text(sources["ring_smoke"].exists()),
            "source_type": "report",
            "semantics_area": "ALE_ring_motion",
            "key_claim_or_setting": "MovingMesh/PrescribedMeshDisplacement on ring boundaries; not fixed-geometry utr alone",
            "relevance": "supports intended true-geometry meaning",
            "uncertainty": "smoke proof only",
        },
        {
            "source_file": str(sources["true_vs_fixed_review"]),
            "exists": bool_text(sources["true_vs_fixed_review"].exists()),
            "source_type": "report",
            "semantics_area": "fixed_vs_true_geometry",
            "key_claim_or_setting": "WettedWall utr may remain for contact-line physics, not geometry-motion proof",
            "relevance": "separates ALE motion proof from wall velocity surrogate",
            "uncertainty": "does not validate Hmax",
        },
        {
            "source_file": str(sources["t008_d5_java"]),
            "exists": bool_text(sources["t008_d5_java"].exists()),
            "source_type": "java_export",
            "semantics_area": "ALE_moving_boundary",
            "key_claim_or_setting": f"ALE dx={bool_text(has_ale_dx)}; ring selection 4/5/6/7={bool_text(has_ring_selection)}; WettedWall utr={bool_text(has_wettedwall_utr)}",
            "relevance": "direct model export evidence for current diagnostic D5",
            "uncertainty": "export evidence is structural, not physical Hmax validation",
        },
        {
            "source_file": str(sources["w0_java"]),
            "exists": bool_text(sources["w0_java"].exists()),
            "source_type": "java_export",
            "semantics_area": "WettedWall_contactline",
            "key_claim_or_setting": f"NavierSlip={bool_text(has_navier_slip)}; contact_angle_pi_over_2={bool_text(has_contact_angle)}; utr_present={'YES' if 'utr' in w0_java else 'NO'}",
            "relevance": "documents contactline settings in current wetted-wall control branch",
            "uncertainty": "physical acceptance remains unresolved",
        },
        {
            "source_file": str(sources["wettedwall_report"]),
            "exists": bool_text(sources["wettedwall_report"].exists()),
            "source_type": "report",
            "semantics_area": "WettedWall_contactline",
            "key_claim_or_setting": "Clear physical WettedWall cases=[]; no-WettedWall diagnostic clear=False",
            "relevance": "negative/uncertain contactline semantics evidence",
            "uncertainty": "requires future bounded repair or acceptance criteria",
        },
        {
            "source_file": str(sources["t007_semantics"]),
            "exists": bool_text(sources["t007_semantics"].exists()),
            "source_type": "report",
            "semantics_area": "displacement_ladder",
            "key_claim_or_setting": "D0/D1/D2 semantics recovered; dx=[0,-Vring*t]; utr=[0,-Vring,0]",
            "relevance": "diagnostic motion semantics baseline",
            "uncertainty": "Hmax remains non-real",
        },
        {
            "source_file": str(sources["t008_semantics"]),
            "exists": bool_text(sources["t008_semantics"].exists()),
            "source_type": "report",
            "semantics_area": "displacement_ladder",
            "key_claim_or_setting": "D3/D4/D5 change only Vring; diagnostic-only; HMAX_IS_REAL_PHYSICAL_OUTPUT=NO",
            "relevance": "supports bounded displacement consistency",
            "uncertainty": "not a parameter sweep or physical Hmax result",
        },
        {
            "source_file": str(sources["interface_audit"]),
            "exists": bool_text(sources["interface_audit"].exists()),
            "source_type": "report",
            "semantics_area": "interface_extraction",
            "key_claim_or_setting": "H_raw_global is not trusted; M1 excludes contaminating crossings",
            "relevance": "prevents using raw global height as physical Hmax",
            "uncertainty": "M1 remains diagnostic until acceptance controls pass",
        },
        {
            "source_file": str(sources["t004_script"]),
            "exists": bool_text(sources["t004_script"].exists()),
            "source_type": "script",
            "semantics_area": "interface_extraction",
            "key_claim_or_setting": f"memory-safe binned crossing extractor={bool_text(has_binned_extractor)}",
            "relevance": "repaired extraction implementation",
            "uncertainty": "method is postprocessing diagnostic, not yet real-Hmax validation",
        },
        {
            "source_file": str(sources["t010_script"]),
            "exists": bool_text(sources["t010_script"].exists()),
            "source_type": "script",
            "semantics_area": "ROI_extraction",
            "key_claim_or_setting": f"ROI diagnostic guard={bool_text(has_roi_diagnostic_guard)}; fixed-geometry ROI reused as diagnostic analogue",
            "relevance": "Jet1/ROI semantics source",
            "uncertainty": "current Jet1 branch is negative under T011",
        },
        {
            "source_file": str(sources["t011_audit"]),
            "exists": bool_text(sources["t011_audit"].exists()),
            "source_type": "report",
            "semantics_area": "ROI_threshold",
            "key_claim_or_setting": "5C threshold delta > 5e-5 m; true-geometry compatibility is diagnostic only",
            "relevance": "blocks current Jet1 continuation",
            "uncertainty": "not a real-Hmax validation rule",
        },
        {
            "source_file": str(sources["readme"]),
            "exists": bool_text(sources["readme"].exists()),
            "source_type": "README",
            "semantics_area": "project_gates",
            "key_claim_or_setting": "current true-geometry R3 sections keep Stage 6 and real Hmax closed",
            "relevance": "repository-level gate summary",
            "uncertainty": "bounded sections summarize, not primary evidence",
        },
    ]

    inventory_path = TABLES / "T013_semantics_source_inventory.csv"
    write_csv(
        inventory_path,
        ["source_file", "exists", "source_type", "semantics_area", "key_claim_or_setting", "relevance", "uncertainty"],
        inventory_rows,
    )

    consistency_rows = [
        {
            "semantics_item": "ALE_ring_motion_semantics",
            "current_status": "PARTIAL",
            "evidence_for": "campaign reports and Java exports show PrescribedMeshDisplacement dx=[0,-Vring*t] on ring boundaries 4/5/6/7; D-ladder displacement verified",
            "evidence_against": "verified only over diagnostic short displacements; not validated against physical free-fall or real-Hmax criteria",
            "blocking_uncertainty": "whether diagnostic ALE motion is sufficient for future physical-height output",
            "repair_action": "define a precheck requiring boundary displacement audit, outer-wall fixed constraints, and no double-counting of geometry motion vs utr",
            "gate_effect": "does not open Stage 6 now",
        },
        {
            "semantics_item": "moving_boundary_vs_mesh_motion",
            "current_status": "PARTIAL",
            "evidence_for": "true_vs_fixed review separates ALE geometry proof from WettedWall utr; Java contains both dx and utr",
            "evidence_against": "combined ALE dx plus WettedWall utr needs explicit non-double-counting acceptance rule",
            "blocking_uncertainty": "whether utr is purely contactline velocity or duplicates wall translation in physics interpretation",
            "repair_action": "future precheck must document wall-frame convention and compare expected vs measured displacement for each candidate model",
            "gate_effect": "bounded precheck allowed; Stage 6 remains NO",
        },
        {
            "semantics_item": "wettedwall_contactline_semantics",
            "current_status": "UNKNOWN",
            "evidence_for": "WettedWall uses NavierSlip, theta=pi/2, and utr=-Vring in exports",
            "evidence_against": "R3 contactline report found no clear physical WettedWall cases",
            "blocking_uncertainty": "physical interpretability of contactline settings under true ALE motion",
            "repair_action": "define required contact-angle/slip/control-case acceptance before real-Hmax use",
            "gate_effect": "blocks real Hmax",
        },
        {
            "semantics_item": "contact_angle_slip_semantics",
            "current_status": "PARTIAL",
            "evidence_for": "T006 contact-angle/slip extraction and postprocess pass for W2/W3/W4/W7/W8",
            "evidence_against": "T006 still reports credible static and micro-motion baseline as UNKNOWN",
            "blocking_uncertainty": "whether parameter variations are physical sensitivity controls or only diagnostic stabilizers",
            "repair_action": "classify each contact-angle/slip case as physical control, numerical control, or excluded diagnostic",
            "gate_effect": "does not authorize parameter sweep",
        },
        {
            "semantics_item": "interface_extraction_physical_validity",
            "current_status": "PARTIAL",
            "evidence_for": "R2 M1 excludes boundary/ring-near contamination; T004-T006 memory-safe extraction passes",
            "evidence_against": "old H_raw_global is explicitly untrusted; M1/M4 remain diagnostic until physical controls pass",
            "blocking_uncertainty": "whether extracted connected interface corresponds to physical free-surface maximum under moving geometry",
            "repair_action": "define Hmax extractor acceptance with connected-interface, ROI, visual, mass, and mesh checks",
            "gate_effect": "keeps HMAX_IS_REAL_PHYSICAL_OUTPUT=NO",
        },
        {
            "semantics_item": "ROI_extraction_physical_validity",
            "current_status": "NO",
            "evidence_for": "T010/T011 document auditable center-hole and inner-edge ROI diagnostics",
            "evidence_against": "T011 says fixed-geometry 5C ROI is diagnostic analogue only and current Jet1 branch is negative",
            "blocking_uncertainty": "no current ROI rule validates physical Jet1 or Stage 6",
            "repair_action": "do not reuse current Jet1 ROI for Stage 6 unless Review Agent defines a new justified rule",
            "gate_effect": "CURRENT_JET1_BRANCH_ALLOWED=NO",
        },
        {
            "semantics_item": "real_Hmax_definition",
            "current_status": "PARTIAL",
            "evidence_for": "T013 defines a candidate acceptance definition in T013_stage6_acceptance_criteria.md",
            "evidence_against": "no case has passed those criteria; all current diagnostics label HMAX_IS_REAL_PHYSICAL_OUTPUT=NO",
            "blocking_uncertainty": "definition must be tested by a future bounded precheck before any output is real",
            "repair_action": "require documented z0 reference, connected-interface maximum, artifact exclusions, convergence and visual audits",
            "gate_effect": "ALLOW_REAL_HMAX_OUTPUT=NO",
        },
        {
            "semantics_item": "Stage6_minimum_acceptance_criteria",
            "current_status": "YES_CRITERIA_DEFINED",
            "evidence_for": "T013 acceptance report lists explicit YES/NO criteria for ring motion, contactline, extraction, Hmax, controls, and audits",
            "evidence_against": "criteria have not been executed as a future precheck",
            "blocking_uncertainty": "whether future candidate model can pass all criteria",
            "repair_action": "next task should execute a bounded no-Stage6 acceptance precheck against saved candidate models",
            "gate_effect": "ALLOW_BOUNDED_STAGE6_PRECHECK=YES; ALLOW_STAGE6_NOW=NO",
        },
    ]

    consistency_path = TABLES / "T013_semantics_consistency_matrix.csv"
    write_csv(
        consistency_path,
        ["semantics_item", "current_status", "evidence_for", "evidence_against", "blocking_uncertainty", "repair_action", "gate_effect"],
        consistency_rows,
    )

    acceptance_path = REPORTS / "T013_stage6_acceptance_criteria.md"
    acceptance_report = f"""# T013 Stage 6 Acceptance Criteria

- Run id: `{run_id}`
- Scope: acceptance criteria only. No COMSOL, Stage 6, real Hmax, parameter sweep, or Jet1 continuation was performed.

## Required YES/NO Criteria Before Any Future `ALLOW_STAGE6 = YES`

### 1. Physical Ring Motion Validity

- Required answer for future Stage 6: `YES`.
- Current T013 answer: `PARTIAL`.
- Must show ALE `PrescribedMeshDisplacement` on the confirmed ring boundaries and measured ring displacement matching the intended physical motion within a stated tolerance.
- Must document that WettedWall `utr` is a contactline/wall-frame condition, not double-counted geometry translation.

### 2. Boundary / Contactline Validity

- Required answer for future Stage 6: `YES`.
- Current T013 answer: `UNKNOWN`.
- Must classify WettedWall, contact angle, and slip settings as physically justified for the intended experiment, not only numerical stabilizers.
- Must include a static/control comparison showing the contactline setting does not introduce nonphysical free-surface artifacts.

### 3. Interface Extraction Validity

- Required answer for future Stage 6: `YES`.
- Current T013 answer: `PARTIAL`.
- Must use the main connected air-water interface, exclude outer-wall/top/bottom/ring-near contamination, and pass visual checks on representative frames.
- Must not use raw global crossings as physical height.

### 4. Real Hmax Validity

- Required answer for future Stage 6: `YES`.
- Current T013 answer: `NO`.
- Candidate real-Hmax definition: maximum vertical elevation of the validated connected air-water interface above the documented initial free-surface reference `z0`, inside a physically justified domain or ROI, after excluding boundary/mesh/contactline artifacts.
- Must include units, sign convention, time window, initial reference, extraction method, artifact exclusions, mesh/time-step sensitivity, and figure/table/log audit.

### 5. Image / Table / Log Audit Completeness

- Required answer for future Stage 6: `YES`.
- Current T013 answer: `CRITERIA_DEFINED`.
- Every future candidate must have a manifest of source models, scripts, logs, arrays/tables, and CSV-backed figures. Claims must trace to tables, not only images.

### 6. Minimum Control-Case Requirements

- Required answer for future Stage 6: `YES`.
- Current T013 answer: `CRITERIA_DEFINED`.
- Minimum controls: zero-motion baseline, micro-motion baseline, static/no-ring or ring-position controls, contactline/slip controls, mesh/time-step sensitivity, fixed-geometry negative-control context, and visual audit of interface continuity.

### 7. Is Jet1 Required For Stage 6?

- Required answer for future Stage 6: `NO, not categorically`.
- Current T013 answer: `CURRENT_JET1_BRANCH_ALLOWED = NO`.
- Stage 6 may later be entered through a non-Jet1 physical mechanism only if the mechanism has an explicit Review Agent definition and passes the same real-Hmax acceptance criteria. The current Jet1 ROI/threshold branch remains closed.

## Gate Result

- `ALLOW_STAGE6_NOW = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_BOUNDED_STAGE6_PRECHECK = YES`
"""
    acceptance_path.write_text(acceptance_report, encoding="utf-8")

    gate_summary = {
        "T013_STATUS": "PASS",
        "MODEL_SEMANTICS_REPAIRED": "PARTIAL",
        "ALE_RING_MOTION_SEMANTICS_VALID": "PARTIAL",
        "WETTEDWALL_CONTACTLINE_SEMANTICS_VALID": "UNKNOWN",
        "INTERFACE_EXTRACTION_PHYSICAL_VALIDITY": "PARTIAL",
        "REAL_HMAX_DEFINITION_READY": "PARTIAL",
        "STAGE6_ACCEPTANCE_CRITERIA_READY": "YES",
        "CURRENT_JET1_BRANCH_ALLOWED": "NO",
        "ALLOW_STAGE6_NOW": "NO",
        "ALLOW_REAL_HMAX_OUTPUT": "NO",
        "ALLOW_BOUNDED_STAGE6_PRECHECK": "YES",
        "RECOMMENDED_NEXT_TASK": "Run a bounded no-Stage6 acceptance precheck against existing true-geometry candidate evidence: verify ALE/wall-frame non-double-counting, contactline physical classification, connected-interface Hmax extractor criteria, and required control-case checklist without outputting real Hmax.",
    }
    gate_path = REPORTS / "T013_gate_summary.json"
    gate_path.write_text(json.dumps(gate_summary, indent=2) + "\n", encoding="utf-8")

    svg_path = IMAGES / "T013_model_semantics_gate_map.svg"
    write_svg(svg_path)

    missing = [str(path) for path in sources.values() if not path.exists()]
    final_path = REPORTS / "T013_final_report.md"
    final_report = f"""# T013 Final Report

- Run id: `{run_id}`
- Scope: true-geometry model-semantics repair package and Stage 6 acceptance criteria only.
- No COMSOL run, Stage 6, parameter sweep, current Jet1 continuation, Jet1 physical conclusion, or real Hmax output was performed.

## Gate Values

- `T013_STATUS = PASS`
- `MODEL_SEMANTICS_REPAIRED = PARTIAL`
- `ALE_RING_MOTION_SEMANTICS_VALID = PARTIAL`
- `WETTEDWALL_CONTACTLINE_SEMANTICS_VALID = UNKNOWN`
- `INTERFACE_EXTRACTION_PHYSICAL_VALIDITY = PARTIAL`
- `REAL_HMAX_DEFINITION_READY = PARTIAL`
- `STAGE6_ACCEPTANCE_CRITERIA_READY = YES`
- `CURRENT_JET1_BRANCH_ALLOWED = NO`
- `ALLOW_STAGE6_NOW = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_BOUNDED_STAGE6_PRECHECK = YES`

## Semantics Repair Result

The intended true-geometry ring motion meaning is: the ring boundary geometry is moved by ALE `PrescribedMeshDisplacement` with vertical displacement `-Vring*t` on confirmed ring boundaries `[4, 5, 6, 7]`. WettedWall `utr=[0,-Vring,0]` may remain as a wall-frame/contactline condition, but it is not sufficient proof of geometry motion by itself and must not be double-counted as an additional physical translation.

Current ALE and displacement semantics are consistent enough for diagnostic use, because campaign reports and D-ladder exports show ALE displacement and measured diagnostic displacement. They are not sufficient for Stage 6 or real Hmax because contactline semantics, physical interface-height validity, and real-Hmax acceptance controls have not passed.

WettedWall/contactline semantics remain the weakest area. The code exports contain NavierSlip, contact angle `pi/2`, and `utr=-Vring`, but the R3 contactline report did not find clear physical WettedWall cases. This keeps boundary/contactline validity at `UNKNOWN`.

Interface extraction is `PARTIAL`: repaired extraction avoids known raw-global contamination and passes diagnostic tables, but no output is yet a validated physical height. T013 defines what must be true for real Hmax, but does not produce real Hmax.

## Outputs

- Source inventory: `{inventory_path}`
- Semantics consistency matrix: `{consistency_path}`
- Stage 6 acceptance criteria: `{acceptance_path}`
- Gate summary: `{gate_path}`
- Gate map: `{svg_path}`

## Input Coverage

Missing inputs: `{'; '.join(missing) if missing else 'none'}`

## Next Recommended Task

Run a bounded no-Stage6 acceptance precheck against existing true-geometry candidate evidence: verify ALE/wall-frame non-double-counting, contactline physical classification, connected-interface Hmax extractor criteria, and required control-case checklist without outputting real Hmax.
"""
    final_path.write_text(final_report, encoding="utf-8")

    readme_body = f"""## TRUE_GEOMETRY_R3_MODEL_SEMANTICS_REPAIR

- Run id: `{run_id}`
- Scope: T013 true-geometry model-semantics repair and Stage 6 acceptance criteria only.
- T013 status: `PASS`
- `MODEL_SEMANTICS_REPAIRED = PARTIAL`
- `ALE_RING_MOTION_SEMANTICS_VALID = PARTIAL`
- `WETTEDWALL_CONTACTLINE_SEMANTICS_VALID = UNKNOWN`
- `INTERFACE_EXTRACTION_PHYSICAL_VALIDITY = PARTIAL`
- `REAL_HMAX_DEFINITION_READY = PARTIAL`
- `STAGE6_ACCEPTANCE_CRITERIA_READY = YES`
- `CURRENT_JET1_BRANCH_ALLOWED = NO`
- `ALLOW_STAGE6_NOW = NO`
- `ALLOW_REAL_HMAX_OUTPUT = NO`
- `ALLOW_BOUNDED_STAGE6_PRECHECK = YES`
- Final report: `{final_path}`
- Acceptance criteria: `{acceptance_path}`
- Source inventory: `{inventory_path}`
- Consistency matrix: `{consistency_path}`
- No Stage 6 parameter sweep has been performed.
- No real Hmax has been produced.
- Current Jet1 branch remains closed.
"""
    update_bounded_section(
        ROOT / "README.md",
        "<!-- TRUE_GEOMETRY_R3_MODEL_SEMANTICS_REPAIR:START -->",
        "<!-- TRUE_GEOMETRY_R3_MODEL_SEMANTICS_REPAIR:END -->",
        readme_body,
    )


if __name__ == "__main__":
    main()
