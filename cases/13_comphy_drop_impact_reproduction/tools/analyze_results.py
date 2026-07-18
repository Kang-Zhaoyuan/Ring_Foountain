#!/usr/bin/env python3
"""Aggregate the independent Drop-Impact reproduction evidence."""

from __future__ import annotations

import csv
import argparse
import math
import os
import re
from pathlib import Path

CASE_DIR = Path(__file__).resolve().parents[1]
UPSTREAM = Path()
REPORT = CASE_DIR
TABLES = REPORT / "tables"
FIGURES = REPORT / "figures"

CASES = {
    1808: (8, "smoke_l8_a.log"),
    1810: (10, "grid_l10.log"),
    1811: (11, "grid_l11.log"),
    1812: (12, "grid_l12.log"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def read_solver_log(case: int) -> list[tuple[int, float, float, float]]:
    rows = []
    path = UPSTREAM / "simulationCases" / str(case) / "results" / "log"
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        iteration, dt, time, ke = line.split()
        rows.append((int(iteration), float(dt), float(time), float(ke)))
    return rows


def parse_elapsed(value: str) -> float:
    pieces = [float(piece) for piece in value.strip().split(":")]
    if len(pieces) == 2:
        return 60.0 * pieces[0] + pieces[1]
    if len(pieces) == 3:
        return 3600.0 * pieces[0] + 60.0 * pieces[1] + pieces[2]
    raise ValueError(value)


def directory_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def runtime_record(log_name: str) -> dict[str, float]:
    text = (REPORT / "logs" / log_name).read_text(errors="replace")
    summary = re.search(
        r"# Quadtree, (\d+) steps, ([0-9.eE+-]+) CPU, "
        r"([0-9.eE+-]+) real, ([0-9.eE+-]+) points.step/s, (\d+) var",
        text,
    )
    elapsed = re.search(r"Elapsed \(wall clock\) time .*: ([0-9:.]+)", text)
    rss = re.search(r"Maximum resident set size \(kbytes\): (\d+)", text)
    if not summary or not elapsed or not rss:
        raise RuntimeError(f"cannot parse timing log {log_name}")
    return {
        "steps": int(summary.group(1)),
        "solver_cpu_s": float(summary.group(2)),
        "solver_real_s": float(summary.group(3)),
        "points_step_s": float(summary.group(4)),
        "variables": int(summary.group(5)),
        "total_wall_s": parse_elapsed(elapsed.group(1)),
        "max_rss_kib_including_compile": int(rss.group(1)),
    }


def nearest_ke(rows: list[tuple[int, float, float, float]], target: float) -> float:
    return min(rows, key=lambda row: abs(row[2] - target))[3]


def summarize_case(case: int, level: int, timing_log: str) -> dict[str, float | int]:
    metrics = read_tsv(TABLES / f"case_{case}_snapshot_metrics.tsv")
    footprint = read_tsv(TABLES / f"case_{case}_footprint.tsv")
    solver = read_solver_log(case)
    runtime = runtime_record(timing_log)

    volumes = np.array([float(row["volume_axi"]) for row in metrics])
    speeds = np.array([float(row["max_speed"]) for row in metrics])
    cells = np.array([int(row["leaf_cells"]) for row in metrics])
    deltas = np.array([float(row["min_delta"]) for row in metrics])
    fp_time = np.array([float(row["time"]) for row in footprint])
    fp_radius = np.array([float(row["footprint_radius_xcut_0.05"]) for row in footprint])
    fp_index = int(np.argmax(fp_radius))
    initial_volume = float(volumes[0])
    volume_drift = np.abs(volumes - initial_volume) / initial_volume
    case_dir = UPSTREAM / "simulationCases" / str(case)

    result: dict[str, float | int] = {
        "case": case,
        "max_level": level,
        "snapshots": len(metrics),
        "log_rows": len(solver),
        "steps": runtime["steps"],
        "simulation_time_last_snapshot": float(metrics[-1]["time"]),
        "min_dt": min(row[1] for row in solver),
        "initial_volume": initial_volume,
        "final_volume": float(volumes[-1]),
        "max_relative_volume_drift": float(np.max(volume_drift)),
        "final_kinetic_energy": solver[-1][3],
        "max_logged_kinetic_energy": max(row[3] for row in solver),
        "ke_t0.1": nearest_ke(solver, 0.1),
        "ke_t0.2": nearest_ke(solver, 0.2),
        "ke_t0.3": nearest_ke(solver, 0.3),
        "max_snapshot_speed": float(np.max(speeds)),
        "max_footprint_radius": float(fp_radius[fp_index]),
        "time_of_max_footprint": float(fp_time[fp_index]),
        "max_leaf_cells": int(np.max(cells)),
        "final_leaf_cells": int(cells[-1]),
        "minimum_cell_width": float(np.min(deltas)),
        "invalid_snapshot_values": max(int(row["invalid"]) for row in metrics),
        "solver_real_s": runtime["solver_real_s"],
        "total_wall_s": runtime["total_wall_s"],
        "max_rss_kib_including_compile": runtime["max_rss_kib_including_compile"],
        "case_bytes": directory_bytes(case_dir),
    }
    return result


def write_grid_table(summaries: list[dict[str, float | int]]) -> None:
    path = TABLES / "grid_convergence.tsv"
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, delimiter="\t", fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)


def relative_change(a: float, b: float) -> float:
    return abs(b - a) / abs(a) if a else math.inf


def write_engineering_changes(summaries: list[dict[str, float | int]]) -> None:
    by_level = {int(row["max_level"]): row for row in summaries}
    coarse, fine = by_level[11], by_level[12]
    metrics = (
        "final_volume",
        "max_relative_volume_drift",
        "final_kinetic_energy",
        "ke_t0.1",
        "ke_t0.2",
        "ke_t0.3",
        "max_footprint_radius",
        "time_of_max_footprint",
    )
    path = TABLES / "l11_l12_engineering_changes.tsv"
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(("metric", "l11", "l12", "raw_difference_l12_minus_l11",
                         "absolute_relative_change", "under_5_percent"))
        for name in metrics:
            a, b = float(coarse[name]), float(fine[name])
            change = relative_change(a, b)
            writer.writerow((name, f"{a:.17g}", f"{b:.17g}", f"{b-a:.17g}",
                             f"{change:.17g}", "PASS" if change < 0.05 else "FAIL"))


def load_interface(path: Path) -> np.ndarray:
    rows = []
    for line in path.read_text().splitlines():
        values = line.split()
        if len(values) == 2:
            rows.append((float(values[0]), float(values[1])))
    return np.array(rows)


def directed_hausdorff(a: np.ndarray, b: np.ndarray, chunk: int = 256) -> float:
    maximum = 0.0
    for start in range(0, len(a), chunk):
        delta = a[start:start + chunk, None, :] - b[None, :, :]
        nearest = np.sqrt(np.min(np.sum(delta * delta, axis=2), axis=1))
        maximum = max(maximum, float(np.max(nearest)))
    return maximum


def interface_comparison() -> None:
    with (TABLES / "interface_comparison.tsv").open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(("time", "l11_to_l12", "l12_to_l11", "symmetric_hausdorff_R"))
        for time in ("0.1000", "0.2000", "0.3000"):
            l11 = load_interface(TABLES / f"interface_case1811_t{time}.dat")
            l12 = load_interface(TABLES / f"interface_case1812_t{time}.dat")
            d1 = directed_hausdorff(l11, l12)
            d2 = directed_hausdorff(l12, l11)
            writer.writerow((float(time), d1, d2, max(d1, d2)))


def make_figures() -> None:
    colors = {8: "#777777", 10: "#1f77b4", 11: "#ff7f0e", 12: "#2ca02c"}

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for case, (level, _) in CASES.items():
        rows = read_tsv(TABLES / f"case_{case}_footprint.tsv")
        ax.plot([float(row["time"]) for row in rows],
                [float(row["footprint_radius_xcut_0.05"]) for row in rows],
                label=f"L{level}", color=colors[level])
    ax.set(xlabel=r"simulation time $tU/R$", ylabel=r"footprint radius $r/R$")
    ax.grid(alpha=0.25); ax.legend(); fig.tight_layout()
    fig.savefig(FIGURES / "grid_footprint_comparison.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for case, (level, _) in CASES.items():
        rows = read_tsv(TABLES / f"case_{case}_snapshot_metrics.tsv")
        times = [float(row["time"]) for row in rows]
        volumes = np.array([float(row["volume_axi"]) for row in rows])
        ax.plot(times, 100.0 * (volumes - volumes[0]) / volumes[0],
                label=f"L{level}", color=colors[level])
    ax.set(xlabel=r"simulation time $tU/R$", ylabel="liquid-volume change (%)")
    ax.grid(alpha=0.25); ax.legend(); fig.tight_layout()
    fig.savefig(FIGURES / "grid_volume_conservation.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for case, (level, _) in CASES.items():
        rows = read_solver_log(case)
        ax.plot([row[2] for row in rows], [row[3] for row in rows],
                label=f"L{level}", color=colors[level])
    ax.set(xlabel=r"simulation time $tU/R$", ylabel="logged kinetic energy")
    ax.grid(alpha=0.25); ax.legend(); fig.tight_layout()
    fig.savefig(FIGURES / "grid_kinetic_energy.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), sharex=True, sharey=True)
    for ax, time in zip(axes, ("0.1000", "0.2000", "0.3000")):
        for case, level in ((1810, 10), (1811, 11), (1812, 12)):
            points = load_interface(TABLES / f"interface_case{case}_t{time}.dat")
            ax.plot(points[:, 1], points[:, 0], ".", ms=0.7,
                    color=colors[level], label=f"L{level}")
            ax.plot(-points[:, 1], points[:, 0], ".", ms=0.7, color=colors[level])
        ax.set_title(f"t={float(time):.1f}")
        ax.set_aspect("equal"); ax.grid(alpha=0.2); ax.set_xlabel(r"radial $r/R$")
    axes[0].set_ylabel(r"axial $x/R$")
    axes[-1].legend(markerscale=5)
    fig.tight_layout()
    fig.savefig(FIGURES / "grid_interface_common_times.png", dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate the tracked Drop-Impact audit tables and figures."
    )
    parser.add_argument(
        "--reproduction-root",
        required=True,
        type=Path,
        help="Independent reproduction root containing upstream/.",
    )
    args = parser.parse_args()

    global np, plt
    import numpy as np
    import matplotlib.pyplot as plt

    global UPSTREAM
    UPSTREAM = args.reproduction_root.resolve() / "upstream"
    if not (UPSTREAM / "simulationCases").is_dir():
        parser.error(f"missing independent simulationCases directory: {UPSTREAM}")

    summaries = [summarize_case(case, level, log) for case, (level, log) in CASES.items()]
    write_grid_table(summaries)
    write_engineering_changes(summaries)
    interface_comparison()
    make_figures()


if __name__ == "__main__":
    main()
