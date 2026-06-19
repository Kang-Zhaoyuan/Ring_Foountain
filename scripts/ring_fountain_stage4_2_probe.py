# -*- coding: utf-8 -*-
"""Read-only probe for Stage 4.2 COMSOL wall-feature properties."""

from __future__ import annotations

import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import mph


ROOT = Path(r"D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain")
MODEL = ROOT / "04_moving_ring_model" / "models" / "ring_fountain_v3_boundary_review_package.mph"
OUT = ROOT / "04_moving_ring_model" / "logs" / f"stage4_2_property_probe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"


def tags(node: Any) -> list[str]:
    try:
        return [str(x) for x in list(node.tags())]
    except Exception:
        return []


def props(node: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    try:
        names = tags(node.properties())
    except Exception:
        names = []
    for name in names:
        try:
            data[name] = str(node.getString(name))
        except Exception:
            try:
                data[name] = [str(x) for x in list(node.getStringArray(name))]
            except Exception:
                try:
                    data[name] = str(node.get(name))
                except Exception as exc:
                    data[name] = f"<unreadable: {exc}>"
    return data


def sel_entities(feature: Any) -> Any:
    try:
        return [int(x) for x in list(feature.selection().entities(1))]
    except Exception as exc:
        return f"<no entities: {exc}>"


def explicit_entities(selection: Any) -> Any:
    for call in (
        lambda: selection.entities(1),
        lambda: selection.entities(),
        lambda: selection.selection().entities(1),
    ):
        try:
            return [int(x) for x in list(call())]
        except Exception:
            pass
    return "<no explicit entities readable>"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    client = mph.Client(cores=2, version="6.4")
    payload: dict[str, Any] = {
        "model": str(MODEL),
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "components": {},
    }
    try:
        model = client.load(MODEL)
        java = model.java
        for ctag in tags(java.component()):
            comp = java.component(ctag)
            comp_data: dict[str, Any] = {"selections": {}, "physics": {}}
            try:
                for stag in tags(comp.selection()):
                    snode = comp.selection(stag)
                    comp_data["selections"][stag] = {
                        "label": str(snode.label()),
                        "dimension": str(snode.get("entitydim")) if "entitydim" in tags(snode.properties()) else "",
                        "entities_1d": explicit_entities(snode),
                        "properties": props(snode),
                    }
            except Exception as exc:
                comp_data["selections_error"] = traceback.format_exc()
            try:
                for ptag in tags(comp.physics()):
                    phys = comp.physics(ptag)
                    pdata: dict[str, Any] = {
                        "label": str(phys.label()),
                        "type": str(phys.getType()),
                        "properties": props(phys),
                        "features": {},
                    }
                    for ftag in tags(phys.feature()):
                        feat = phys.feature(ftag)
                        fdata: dict[str, Any] = {
                            "label": str(feat.label()),
                            "type": str(feat.getType()),
                            "selection_entities_1d": sel_entities(feat),
                            "properties": props(feat),
                        }
                        try:
                            fdata["allowed_property_tags"] = tags(feat.properties())
                        except Exception:
                            pass
                        pdata["features"][ftag] = fdata
                    comp_data["physics"][ptag] = pdata
            except Exception:
                comp_data["physics_error"] = traceback.format_exc()
            payload["components"][ctag] = comp_data
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    finally:
        try:
            client.remove(model)
        except Exception:
            pass
        client.clear()


if __name__ == "__main__":
    main()
