#!/usr/bin/env python3
"""Compare ring lower-face trajectory diagnostics with video labels."""

import argparse
import csv
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("motion_tsv", type=Path)
    parser.add_argument("observations_tsv", type=Path)
    parser.add_argument("output_tsv", type=Path)
    parser.add_argument("--drop-clearance-m", type=float, required=True)
    parser.add_argument("--contact-time-s", type=float, required=True)
    return parser.parse_args()


def read_tsv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def fmt(value):
    return f"{value:.12g}"


def main():
    args = parse_args()
    motion = read_tsv(args.motion_tsv)
    observations = [
        row for row in read_tsv(args.observations_tsv)
        if row["quantity"] in (
            "lower_face_height_above_water",
            "lower_face_depth_below_water",
        ) and row["use"] != "not_fitted"
    ]
    fields = (
        "frame", "requested_relative_ms", "observed_down_mm",
        "sample_time_s", "sample_relative_ms", "simulated_down_mm",
        "position_error_mm", "simulated_speed_down_mps",
        "simulated_accel_down_mps2",
    )
    args.output_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_tsv.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream, delimiter="\t", fieldnames=fields, lineterminator="\n"
        )
        writer.writeheader()
        for observation in observations:
            relative_ms = float(observation["physical_time_after_contact_ms"])
            target_time = args.contact_time_s + relative_ms/1000.0
            sample = min(motion, key=lambda row: abs(float(row["t_s"]) - target_time))
            observed = float(observation["value"])
            if observation["quantity"] == "lower_face_height_above_water":
                observed = -observed
            simulated = (
                float(sample["drop_m"]) - args.drop_clearance_m
            )*1000.0
            sample_time = float(sample["t_s"])
            writer.writerow({
                "frame": observation["frame"],
                "requested_relative_ms": fmt(relative_ms),
                "observed_down_mm": fmt(observed),
                "sample_time_s": fmt(sample_time),
                "sample_relative_ms": fmt(
                    (sample_time - args.contact_time_s)*1000.0
                ),
                "simulated_down_mm": fmt(simulated),
                "position_error_mm": fmt(simulated - observed),
                "simulated_speed_down_mps": sample["speed_down_mps"],
                "simulated_accel_down_mps2": sample["accel_down_mps2"],
            })


if __name__ == "__main__":
    main()
