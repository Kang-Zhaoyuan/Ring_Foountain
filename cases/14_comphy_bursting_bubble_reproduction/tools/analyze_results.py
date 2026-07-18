#!/usr/bin/env python3
"""Build frozen metric tables and figures from read-only dump audits."""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree

REPORT = Path(__file__).resolve().parents[1]
TABLES = REPORT / "tables"
FIGURES = REPORT / "figures"
CASES = {2808: (8, 0.01), 2809: (8, 0.01), 2820: (8, 0.02), 2810: (10, 0.01)}
RUNTIME_S = {2808: 55.65, 2809: 56.70, 2820: 55.93, 2810: 1139.61}
DISK_B = {2808: 48944504, 2809: 48944504, 2820: 47000895, 2810: 240234209}
MIN_DT = {2808: 1.2522e-5, 2809: 1.2522e-5, 2820: 1.2522e-5, 2810: 1.56525e-6}


def read_tsv(path: Path) -> list[dict[str, float]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    out = []
    for row in rows:
        out.append({k: float(v) for k, v in row.items()})
    return out


def load_case(case: int) -> list[dict[str, float]]:
    metrics = read_tsv(TABLES / f"case{case}_snapshot_metrics.tsv")
    base = read_tsv(TABLES / f"case{case}_base.tsv")
    assert len(metrics) == len(base)
    for m, b in zip(metrics, base):
        assert abs(m["time"] - b["time"]) < 1e-9
        m.update({k: v for k, v in b.items() if k not in {"case", "time"}})
    times = np.array([r["time"] for r in metrics])
    heights = np.array([r["z_center"] for r in metrics])
    edge_order = 2 if len(times) > 2 else 1
    speeds = np.gradient(heights, times, edge_order=edge_order)
    for row, speed in zip(metrics, speeds):
        row["tip_speed"] = float(speed)
    return metrics


DATA = {case: load_case(case) for case in CASES}


def event_time(rows: list[dict[str, float]]) -> float:
    for row in rows:
        threshold = max(0.02, 2.0 * row["delta_min"])
        if row["z_center"] > threshold and row["r_base"] > 2.0 * row["delta_min"]:
            return row["time"]
    return math.nan


def topology_time(rows: list[dict[str, float]]) -> float:
    return next((r["time"] for r in rows if r["n_liquid"] > 1), math.nan)


def at(rows: list[dict[str, float]], time: float) -> dict[str, float]:
    return min(rows, key=lambda r: abs(r["time"] - time))


def max_volume_drift(rows: list[dict[str, float]]) -> float:
    v0 = rows[0]["volume"]
    return max(abs(r["volume"] - v0) / v0 for r in rows)


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


jet_rows: list[dict[str, object]] = []
for case, rows in DATA.items():
    for r in rows:
        if r["time"] < 0.40:
            continue
        jet_rows.append({
            "case": case, "level": CASES[case][0], "Oh": CASES[case][1],
            "time": f'{r["time"]:.6f}', "H_main_center": f'{r["z_center"]:.9g}',
            "dHdt": f'{r["tip_speed"]:.9g}', "z_all": f'{r["z_all"]:.9g}',
            "z_main": f'{r["z_main"]:.9g}', "cavity_z_base": f'{r["z_base"]:.9g}',
            "r_j_outer_base": f'{r["r_base"]:.9g}', "liquid_components": int(r["n_liquid"]),
            "q_jet": "NA", "Q_j": "NA",
            "flux_note": "getJetFoot candidate did not match robust getBase outer base",
        })
write_tsv(TABLES / "jet_metrics.tsv", list(jet_rows[0]), jet_rows)

response_rows = []
for case in (2808, 2820):
    rows = DATA[case]
    response_rows.append({
        "case": case, "Oh": CASES[case][1], "jet_time": f"{event_time(rows):.6f}",
        "H_t0.60": f'{at(rows, .60)["z_center"]:.9g}',
        "H_t0.69": f'{at(rows, .69)["z_center"]:.9g}',
        "first_liquid_component_split": f"{topology_time(rows):.6f}" if not math.isnan(topology_time(rows)) else "NONE_BY_0.69",
        "max_KE_snapshot": f'{max(r["ke"] for r in rows):.9g}',
        "max_speed_snapshot": f'{max(r["umax"] for r in rows):.9g}',
        "interpretation": "higher Oh delays and damps the early jet; L8 functional response only",
    })
write_tsv(TABLES / "parameter_response.tsv", list(response_rows[0]), response_rows)

grid_rows = []
for case in (2808, 2810):
    rows = DATA[case]
    grid_rows.append({
        "case": case, "level": CASES[case][0], "status": "COMPLETED",
        "jet_time": f"{event_time(rows):.6f}", "H_t0.60": f'{at(rows,.60)["z_center"]:.9g}',
        "H_t0.69": f'{at(rows,.69)["z_center"]:.9g}',
        "r_base_t0.60": f'{at(rows,.60)["r_base"]:.9g}',
        "KE_t0.60": f'{at(rows,.60)["ke"]:.9g}',
        "max_rel_volume_drift": f"{max_volume_drift(rows):.9g}",
        "max_speed": f'{max(r["umax"] for r in rows):.9g}',
        "max_leaf_cells": int(max(r["leaves"] for r in rows)),
        "delta_min": f'{min(r["delta_min"] for r in rows):.9g}',
        "min_dt": f"{MIN_DT[case]:.9g}", "runtime_s": f"{RUNTIME_S[case]:.3f}",
        "case_bytes": DISK_B[case], "note": "two-level evidence; not a convergence claim",
    })
for case, level, runtime, size in ((2811, 11, 5157.1, 532_231_175), (2812, 12, 23337.1, 1_179_141_077)):
    grid_rows.append({
        "case": case, "level": level, "status": "NOT_RUN_RESOURCE_GATE", "jet_time": "NA",
        "H_t0.60": "NA", "H_t0.69": "NA", "r_base_t0.60": "NA", "KE_t0.60": "NA",
        "max_rel_volume_drift": "NA", "max_speed": "NA", "max_leaf_cells": "NA",
        "delta_min": "NA", "min_dt": "NA", "runtime_s": f"{runtime:.1f}",
        "case_bytes": size, "note": "estimate exceeds 60-minute single-run gate",
    })
write_tsv(TABLES / "grid_convergence.tsv", list(grid_rows[0]), grid_rows)

runtime_factor = math.sqrt(RUNTIME_S[2810] / RUNTIME_S[2808])
disk_factor = math.sqrt(DISK_B[2810] / DISK_B[2808])
resource_rows = [
    {"case": 2810, "level": 10, "horizon": 0.7, "basis": "measured", "runtime_s": RUNTIME_S[2810], "disk_bytes": DISK_B[2810], "decision": "COMPLETED"},
    {"case": 2811, "level": 11, "horizon": 0.7, "basis": f"L8-L10 per-level factor {runtime_factor:.3f}/{disk_factor:.3f}", "runtime_s": round(RUNTIME_S[2810]*runtime_factor,1), "disk_bytes": round(DISK_B[2810]*disk_factor), "decision": "PAUSE_GT_60_MIN"},
    {"case": 2812, "level": 12, "horizon": 0.7, "basis": "same scaling", "runtime_s": round(RUNTIME_S[2810]*runtime_factor**2,1), "disk_bytes": round(DISK_B[2810]*disk_factor**2), "decision": "NOT_STARTED"},
    {"case": 1000, "level": 12, "horizon": 1.5, "basis": "short-L12 estimate scaled linearly by horizon (optimistic)", "runtime_s": round(RUNTIME_S[2810]*runtime_factor**2*1.5/0.7,1), "disk_bytes": round(DISK_B[2810]*disk_factor**2*1.5/0.7), "decision": "NOT_STARTED_GT_60_MIN"},
]
write_tsv(TABLES / "resource_estimates.tsv", list(resource_rows[0]), resource_rows)


def facet_points(case: int, time: str) -> np.ndarray:
    path = FIGURES / f"interface_case{case}_t{time}.dat"
    points = []
    for line in path.read_text().splitlines():
        if line.strip():
            points.append(tuple(map(float, line.split())))
    return np.asarray(points)


distance_rows = []
for time in ("0.5000", "0.5800", "0.6400", "0.6900"):
    a, b = facet_points(2808, time), facet_points(2810, time)
    dab = cKDTree(b).query(a, k=1)[0].max()
    dba = cKDTree(a).query(b, k=1)[0].max()
    distance_rows.append({"time": time, "case_a": 2808, "case_b": 2810,
                          "symmetric_endpoint_Hausdorff": f"{max(dab,dba):.9g}",
                          "in_L10_Delta": f"{max(dab,dba)/0.009765625:.6g}"})
write_tsv(TABLES / "interface_distances.tsv", list(distance_rows[0]), distance_rows)

plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 180, "font.size": 9})

fig, axes = plt.subplots(2, 2, figsize=(9, 7), constrained_layout=True)
for ax, time in zip(axes.flat, ("0.5000", "0.5800", "0.6400", "0.6900")):
    for case, color in ((2808, "tab:blue"), (2810, "tab:orange")):
        p = facet_points(case, time)
        ax.plot(p[:, 0], p[:, 1], ".", ms=0.7, color=color, label=f"L{CASES[case][0]}")
        ax.plot(p[:, 0], -p[:, 1], ".", ms=0.7, color=color)
    ax.set(title=f"t={time}", xlabel="z/R", ylabel="r/R")
    ax.set_xlim(-2.1, 4.1); ax.set_ylim(-1.3, 1.3); ax.legend()
fig.savefig(FIGURES / "common_time_interfaces.png"); plt.close(fig)

def plot_series(field: str, ylabel: str, filename: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    for case, style in ((2808, "-"), (2820, "--"), (2810, "-")):
        rows = DATA[case]
        ax.plot([r["time"] for r in rows], [r[field] for r in rows], style,
                label=f"case {case}, L{CASES[case][0]}, Oh={CASES[case][1]:g}")
    ax.axhline(0, color="0.5", lw=.7); ax.set(xlabel="t/t_cap", ylabel=ylabel)
    ax.legend(); fig.tight_layout(); fig.savefig(FIGURES / filename); plt.close(fig)

plot_series("z_center", "main connected center-tip H/R", "jet_height_vs_time.png")
plot_series("tip_speed", "dH/dt", "jet_speed_vs_time.png")

fig, ax = plt.subplots(figsize=(7, 4))
for case in (2808, 2820, 2810):
    rows = DATA[case]
    ax.plot([r["time"] for r in rows], [r["z_base"] for r in rows], label=f"cavity/base {case}")
    ax.axvline(event_time(rows), lw=.8, ls="--")
ax.axhline(0, color="black", lw=.7); ax.set(xlabel="t/t_cap", ylabel="outer cavity/base z/R")
ax.legend(ncol=2, fontsize=7); fig.tight_layout(); fig.savefig(FIGURES / "cavity_and_jet_events.png"); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4))
for case in (2808, 2820, 2810):
    rows = DATA[case]; v0 = rows[0]["volume"]
    ax.plot([r["time"] for r in rows], [(r["volume"]-v0)/v0 for r in rows], label=str(case))
ax.set(xlabel="t/t_cap", ylabel="relative liquid-volume drift"); ax.legend()
fig.tight_layout(); fig.savefig(FIGURES / "volume_conservation.png"); plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 4))
levels = [8, 10, 11, 12]
minutes = [RUNTIME_S[2808]/60, RUNTIME_S[2810]/60,
           resource_rows[1]["runtime_s"]/60, resource_rows[2]["runtime_s"]/60]
bars = ax.bar([str(x) for x in levels], minutes, color=["tab:blue", "tab:blue", "tab:gray", "tab:gray"])
bars[2].set_hatch("//"); bars[3].set_hatch("//")
ax.axhline(60, color="tab:red", ls="--", label="60-minute gate")
ax.set(xlabel="MAXlevel", ylabel="runtime (minutes, hatched=estimate)", yscale="log")
ax.legend(); fig.tight_layout(); fig.savefig(FIGURES / "grid_cost.png"); plt.close(fig)
