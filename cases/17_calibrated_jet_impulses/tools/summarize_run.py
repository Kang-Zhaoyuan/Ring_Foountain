#!/usr/bin/env python3
"""Summarize Case 17 native PLIC heights at the Case 12 event times."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


TARGETS_MS = (17.5, 30.0, 42.0, 52.5, 65.0, 77.5, 96.0,
              110.0, 125.0, 143.5, 160.0)
FIRST_JET_TARGET_MM = 105.80
FIRST_JET_RELATIVE_TOLERANCE = 0.15


def read_parameter_table(path: Path) -> dict[str, float]:
    values: dict[str, float] = {}
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            try:
                values[row["parameter"]] = float(row["value"])
            except (KeyError, ValueError):
                continue
    return values


def prescribed_depth(t: float, p: dict[str, float]) -> float:
    impact = p["impact_speed"]
    terminal = p["terminal_speed"]
    decay = p["trajectory_decay_rate"]
    return terminal * t + (impact - terminal) * (1.0 - math.exp(-decay * t)) / decay


def interface_tops(path: Path, center_radius: float) -> tuple[float, float]:
    center = -math.inf
    outer = -math.inf
    with path.open() as stream:
        for line in stream:
            fields = line.split()
            if len(fields) != 2:
                continue
            axial, radial = map(float, fields)
            if radial <= center_radius:
                center = max(center, axial)
            else:
                outer = max(outer, axial)
    return center, outer


def nearest_interface(run_dir: Path, target_s: float) -> tuple[Path, float]:
    candidates: list[tuple[float, Path]] = []
    for path in run_dir.glob("interface-*.dat"):
        try:
            time_s = float(path.stem.split("-", 1)[1])
        except (IndexError, ValueError):
            continue
        candidates.append((abs(time_s - target_s), path))
    if not candidates:
        raise FileNotFoundError(f"no interface files in {run_dir}")
    error, selected = min(candidates)
    time_s = float(selected.stem.split("-", 1)[1])
    return selected, time_s


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    base = read_parameter_table(run_dir / "effective_parameters.tsv")
    closure = read_parameter_table(run_dir / "case17_effective_parameters.tsv")
    level = int(base["level"])
    delta = 0.120 / (1 << level)
    center_radius = base["Ri"] + delta

    rows: list[dict[str, str]] = []
    for target_ms in TARGETS_MS:
        target_s = target_ms / 1000.0
        interface, sampled_s = nearest_interface(run_dir, target_s)
        center_x, outer_x = interface_tops(interface, center_radius)
        surface_x = -base["thickness"] / 2.0 + prescribed_depth(sampled_s, {
            "impact_speed": base["impact_speed"],
            "terminal_speed": base["terminal_speed"],
            "trajectory_decay_rate": base["trajectory_decay_rate"],
        })
        center_mm = 1000.0 * (center_x - surface_x)
        outer_mm = 1000.0 * (outer_x - surface_x)
        if target_ms == 52.5:
            error_mm = center_mm - FIRST_JET_TARGET_MM
            within = abs(error_mm) <= FIRST_JET_RELATIVE_TOLERANCE * FIRST_JET_TARGET_MM
            verdict = "PASS" if within else "FAIL"
        else:
            error_mm = math.nan
            verdict = "MORPHOLOGY_REVIEW"
        rows.append({
            "target_time_ms": f"{target_ms:g}",
            "sampled_time_ms": f"{1000.0 * sampled_s:.6f}",
            "center_material_plic_height_mm": f"{center_mm:.6f}",
            "outer_material_plic_height_mm": f"{outer_mm:.6f}",
            "experiment_first_jet_target_mm": (
                f"{FIRST_JET_TARGET_MM:.2f}" if target_ms == 52.5 else "NA"
            ),
            "first_jet_error_mm": f"{error_mm:.6f}" if math.isfinite(error_mm) else "NA",
            "verdict": verdict,
            "interface_file": interface.name,
        })

    output = args.output or run_dir / "case17_event_summary.tsv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=rows[0].keys(), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)

    first = next(row for row in rows if row["target_time_ms"] == "52.5")
    print(
        f"Cd={closure.get('early_discharge_fraction', math.nan):g} "
        f"H52.5={first['center_material_plic_height_mm']} mm "
        f"target={FIRST_JET_TARGET_MM:.2f} mm verdict={first['verdict']}"
    )


if __name__ == "__main__":
    main()
