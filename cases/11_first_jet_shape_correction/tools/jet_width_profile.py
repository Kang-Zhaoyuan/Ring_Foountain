#!/usr/bin/env python3
"""Measure the central above-surface jet width from Basilisk facets."""

import argparse
import csv
import math
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("summary_output", type=Path)
    parser.add_argument("profile_output", type=Path)
    parser.add_argument("--contact-time-s", type=float, required=True)
    parser.add_argument("--relative-ms", type=float, action="append", default=[])
    parser.add_argument(
        "--range-ms", type=float, nargs=3,
        metavar=("START", "END", "STEP")
    )
    parser.add_argument("--central-radius-mm", type=float, default=10.0)
    parser.add_argument("--z-step-mm", type=float, default=0.25)
    return parser.parse_args()


def read_snapshots(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def read_segments(path):
    segments = []
    previous = None
    with path.open() as stream:
        for line in stream:
            if not line.strip():
                previous = None
                continue
            if line.startswith("#"):
                continue
            point = tuple(map(float, line.split()[:2]))
            if previous is not None:
                segments.append((previous, point))
            previous = point
    if not segments:
        raise ValueError(f"no interface segments in {path}")
    return segments


def horizontal_crossings(segments, center, z_lab):
    x_query = z_lab - center
    radii = []
    for (x1, y1), (x2, y2) in segments:
        if x1 == x2:
            if abs(x_query - x1) < 1e-14:
                radii.extend((y1, y2))
        elif min(x1, x2) <= x_query <= max(x1, x2):
            fraction = (x_query - x1)/(x2 - x1)
            radii.append(y1 + fraction*(y2 - y1))
    return sorted(radius for radius in radii if radius >= 0.0)


def mean(values):
    return sum(values)/len(values) if values else math.nan


def fmt(value):
    return "nan" if not math.isfinite(value) else f"{value:.12g}"


def main():
    args = parse_args()
    run_directory = args.run_directory.resolve()
    snapshots = read_snapshots(run_directory/"snapshots.tsv")
    if not snapshots:
        raise ValueError("empty snapshots index")

    requested_times = list(args.relative_ms)
    if args.range_ms:
        start, end, step = args.range_ms
        if step <= 0.0 or end < start:
            raise ValueError("invalid --range-ms interval")
        count = int(math.floor((end - start)/step + 1e-9))
        requested_times.extend(start + index*step for index in range(count + 1))
    if not requested_times:
        raise ValueError("provide --relative-ms or --range-ms")

    selected = []
    for requested_ms in requested_times:
        target = args.contact_time_s + requested_ms/1000.0
        row = min(snapshots, key=lambda item: abs(float(item["time_s"]) - target))
        selected.append((requested_ms, row))

    summary_fields = (
        "requested_relative_ms", "sample_time_s", "sample_relative_ms", "file",
        "jet_top_mm", "base_radius_mm", "max_radius_mm",
        "max_to_base_ratio", "upper_mean_radius_mm", "lower_mean_radius_mm",
        "upper_to_lower_ratio", "layers_with_multiple_central_crossings",
        "max_central_crossings",
    )
    profile_fields = (
        "requested_relative_ms", "sample_relative_ms", "z_mm",
        "central_radius_mm", "central_crossings",
    )
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.profile_output.parent.mkdir(parents=True, exist_ok=True)
    with args.summary_output.open("w", newline="") as summary_stream, \
         args.profile_output.open("w", newline="") as profile_stream:
        summary_writer = csv.DictWriter(
            summary_stream, delimiter="\t", fieldnames=summary_fields,
            lineterminator="\n"
        )
        profile_writer = csv.DictWriter(
            profile_stream, delimiter="\t", fieldnames=profile_fields,
            lineterminator="\n"
        )
        summary_writer.writeheader()
        profile_writer.writeheader()

        for requested_ms, row in selected:
            sample_time = float(row["time_s"])
            sample_relative_ms = (sample_time - args.contact_time_s)*1000.0
            center = float(row["ring_center_lab_m"])
            segments = read_segments(run_directory/row["file"])
            central_limit = args.central_radius_mm/1000.0
            positive_points = [
                x + center
                for segment in segments
                for x, y in segment
                if x + center > 0.0 and y <= central_limit
            ]
            if not positive_points:
                raise ValueError(f"no central positive interface in {row['file']}")
            jet_top = max(positive_points)
            step = args.z_step_mm/1000.0
            layer_count = max(1, int(math.floor(jet_top/step)))
            profile = []
            for layer in range(layer_count + 1):
                z_lab = layer*step
                crossings = [
                    radius for radius in horizontal_crossings(segments, center, z_lab)
                    if radius <= central_limit
                ]
                if not crossings:
                    continue
                profile.append((z_lab, crossings[0], len(crossings)))
                profile_writer.writerow({
                    "requested_relative_ms": fmt(requested_ms),
                    "sample_relative_ms": fmt(sample_relative_ms),
                    "z_mm": fmt(z_lab*1000.0),
                    "central_radius_mm": fmt(crossings[0]*1000.0),
                    "central_crossings": len(crossings),
                })
            if not profile:
                raise ValueError(f"no central width profile in {row['file']}")

            base_radius = profile[0][1]
            max_radius = max(radius for _, radius, _ in profile)
            lower = [
                radius for z, radius, _ in profile
                if 0.10*jet_top <= z <= 0.35*jet_top
            ]
            upper = [
                radius for z, radius, _ in profile
                if 0.55*jet_top <= z <= 0.80*jet_top
            ]
            lower_mean = mean(lower)
            upper_mean = mean(upper)
            multi = sum(1 for _, _, count in profile if count > 1)
            max_crossings = max(count for _, _, count in profile)
            summary_writer.writerow({
                "requested_relative_ms": fmt(requested_ms),
                "sample_time_s": fmt(sample_time),
                "sample_relative_ms": fmt(sample_relative_ms),
                "file": row["file"],
                "jet_top_mm": fmt(jet_top*1000.0),
                "base_radius_mm": fmt(base_radius*1000.0),
                "max_radius_mm": fmt(max_radius*1000.0),
                "max_to_base_ratio": fmt(max_radius/base_radius),
                "upper_mean_radius_mm": fmt(upper_mean*1000.0),
                "lower_mean_radius_mm": fmt(lower_mean*1000.0),
                "upper_to_lower_ratio": fmt(upper_mean/lower_mean),
                "layers_with_multiple_central_crossings": multi,
                "max_central_crossings": max_crossings,
            })


if __name__ == "__main__":
    main()
