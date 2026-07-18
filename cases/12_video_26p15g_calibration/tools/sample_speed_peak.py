#!/usr/bin/env python3
"""Locate saved-field speed peaks without treating cut cells as a jet."""

import argparse
import csv
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("output_tsv", type=Path)
    parser.add_argument("--contact-time-s", type=float, required=True)
    parser.add_argument("--start-s", type=float, default=0.0)
    parser.add_argument("--end-s", type=float, default=float("inf"))
    return parser.parse_args()


def classify(fraction, solid_fraction):
    if solid_fraction < 0.999:
        return "embedded_cut_cell"
    if 0.01 < fraction < 0.99:
        return "full_fluid_interface"
    return "full_liquid"


def main():
    args = parse_args()
    run_directory = args.run_directory.resolve()
    with (run_directory / "fields.tsv").open(newline="") as stream:
        fields = list(csv.DictReader(stream, delimiter="\t"))

    selected = [
        row for row in fields
        if args.start_s <= float(row["time_s"]) <= args.end_s
    ]
    if not selected:
        raise ValueError("no saved fields in requested interval")

    peaks = {key: None for key in (
        "all_mobile_water", "embedded_cut_cell",
        "full_fluid_interface", "full_liquid",
    )}
    for row in selected:
        time_s = float(row["time_s"])
        center = float(row["ring_center_lab_m"])
        with (run_directory / row["file"]).open() as stream:
            for line in stream:
                if not line.strip() or line.startswith("#"):
                    continue
                x, radius, speed, fraction, solid_fraction = map(
                    float, line.split()[:5]
                )
                if fraction <= 0.01 or solid_fraction <= 1e-6:
                    continue
                category = classify(fraction, solid_fraction)
                sample = {
                    "time_s": time_s,
                    "time_after_contact_ms": (
                        time_s - args.contact_time_s
                    ) * 1000.0,
                    "x_ring_m": x,
                    "radius_m": radius,
                    "z_lab_m": x + center,
                    "lab_speed_mps": speed,
                    "f": fraction,
                    "cs": solid_fraction,
                    "location_class": category,
                }
                for key in ("all_mobile_water", category):
                    if peaks[key] is None or speed > peaks[key]["lab_speed_mps"]:
                        peaks[key] = sample

    fieldnames = (
        "selection", "time_s", "time_after_contact_ms", "x_ring_m",
        "radius_m", "z_lab_m", "lab_speed_mps", "f", "cs",
        "location_class",
    )
    args.output_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_tsv.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream, delimiter="\t", fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        for selection, peak in peaks.items():
            if peak is None:
                continue
            writer.writerow({
                "selection": selection,
                **{
                    key: (f"{value:.12g}" if isinstance(value, float) else value)
                    for key, value in peak.items()
                },
            })


if __name__ == "__main__":
    main()
