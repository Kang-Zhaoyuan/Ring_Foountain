# -*- coding: utf-8 -*-
"""Probe COMSOL physics type names for Stage 5A two-phase smoke test."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import mph


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
OUT = ROOT / "05_two_phase_free_surface" / "logs" / f"stage5a_physics_probe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"


CANDIDATES = [
    "TwoPhaseFlowLevelSet",
    "LaminarTwoPhaseFlowLevelSet",
    "TwoPhaseFlowLS",
    "LaminarTwoPhaseFlowLS",
    "TpfLevelSet",
    "LevelSet",
    "TwoPhaseFlowPhaseField",
    "LaminarTwoPhaseFlowPhaseField",
    "TwoPhaseFlowPF",
    "LaminarTwoPhaseFlowPF",
    "PhaseField",
    "LaminarFlow",
]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    client = mph.Client(cores=2, version="6.4")
    rows = []
    try:
        for ptype in CANDIDATES:
            model = client.create(f"probe_{ptype}")
            try:
                comp = model.java.component().create("comp1", True)
                comp.geom().create("geom1", 2)
                try:
                    phys = comp.physics().create("phys1", ptype, "geom1")
                    rows.append({"type": ptype, "status": "ok", "label": str(phys.label()), "created_type": str(phys.getType())})
                except Exception as exc:
                    rows.append({"type": ptype, "status": "failed", "error": str(exc)})
            finally:
                try:
                    client.remove(model)
                except Exception:
                    pass
    finally:
        client.clear()
    OUT.write_text(json.dumps({"rows": rows, "run_time": datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
