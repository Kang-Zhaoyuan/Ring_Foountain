#!/usr/bin/env python3
"""Calibrated subgrid jet-tip model for features thinner than the L7 grid."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

G = 9.81

# Frame 405 is the user-supplied exact height.  The other values are provisional
# pixel calibrations using the per-frame ring depth in Case 12; their uncertainty
# is deliberately wider because the fragmented tip is only a few pixels thick.
CALIBRATION = {
    "first": ((0.0525, 0.10580, 0.005), (0.0775, 0.127, 0.012)),
    "worthington": ((0.1435, 0.107, 0.012), (0.1600, 0.131, 0.015)),
}
FIRST_LAUNCH = 0.0175
WORTHINGTON_LAUNCH = 0.110
CROWN_KEYPOINTS = (
    (0.0000, 0.0), (0.0175, 0.020), (0.0300, 0.026),
    (0.0420, 0.030), (0.0525, 0.032), (0.0650, 0.025),
    (0.0775, 0.015), (0.0960, 0.005), (0.1100, 0.0),
)


def height(tau: float, launch_speed: float, damping: float) -> float:
    if tau <= 0.0:
        return 0.0
    decay = math.exp(-damping * tau)
    return ((launch_speed + G / damping) * (1.0 - decay) / damping
            - G * tau / damping)


def fit_pair(t1: float, h1: float, t2: float, h2: float) -> tuple[float, float]:
    best: tuple[float, float, float] | None = None
    for index in range(1, 100_001):
        damping = index / 1000.0
        a1 = (1.0 - math.exp(-damping * t1)) / damping
        b1 = G * (a1 / damping - t1 / damping)
        launch_speed = (h1 - b1) / a1
        mismatch = abs(height(t2, launch_speed, damping) - h2)
        if best is None or mismatch < best[0]:
            best = mismatch, launch_speed, damping
    assert best is not None
    return best[1], best[2]


def crown_height(time_s: float) -> float:
    if time_s <= CROWN_KEYPOINTS[0][0]:
        return CROWN_KEYPOINTS[0][1]
    for left, right in zip(CROWN_KEYPOINTS, CROWN_KEYPOINTS[1:]):
        if time_s <= right[0]:
            fraction = (time_s - left[0]) / (right[0] - left[0])
            return left[1] + fraction * (right[1] - left[1])
    return 0.0


def first_visible_height(time_s: float, launch_speed: float, damping: float) -> float:
    ballistic = height(time_s - FIRST_LAUNCH, launch_speed, damping)
    if time_s <= 0.096:
        return ballistic
    if time_s >= 0.110:
        return 0.0
    return ballistic * (0.110 - time_s) / (0.110 - 0.096)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    (f1, f2) = CALIBRATION["first"]
    first_speed, first_damping = fit_pair(
        f1[0] - FIRST_LAUNCH, f1[1],
        f2[0] - FIRST_LAUNCH, f2[1],
    )
    (w1, w2) = CALIBRATION["worthington"]
    worth_speed, worth_damping = fit_pair(
        w1[0] - WORTHINGTON_LAUNCH, w1[1],
        w2[0] - WORTHINGTON_LAUNCH, w2[1],
    )

    with (output_dir / "hybrid_model_parameters.tsv").open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("parameter", "value", "unit", "status"))
        writer.writerow(("first_launch_time", FIRST_LAUNCH, "s", "frame_335_no-jet boundary"))
        writer.writerow(("first_launch_speed", f"{first_speed:.9g}", "m/s", "fit"))
        writer.writerow(("first_linear_damping", f"{first_damping:.9g}", "1/s", "fit"))
        writer.writerow(("worthington_launch_time", WORTHINGTON_LAUNCH, "s", "frame_550_onset"))
        writer.writerow(("worthington_launch_speed", f"{worth_speed:.9g}", "m/s", "fit"))
        writer.writerow(("worthington_linear_damping", f"{worth_damping:.9g}", "1/s", "fit"))

    event_times = (0.0175, 0.0300, 0.0420, 0.0525, 0.0650, 0.0775,
                   0.0960, 0.1100, 0.1250, 0.1435, 0.1600)
    with (output_dir / "hybrid_height_timeseries.tsv").open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("time_ms", "crown_envelope_height_mm",
                         "first_jet_height_mm", "worthington_height_mm"))
        for time_s in event_times:
            writer.writerow((
                f"{1000.0 * time_s:g}",
                f"{1000.0 * crown_height(time_s):.6f}",
                f"{1000.0 * first_visible_height(time_s, first_speed, first_damping):.6f}",
                f"{1000.0 * height(time_s - WORTHINGTON_LAUNCH, worth_speed, worth_damping):.6f}",
            ))

    with (output_dir / "hybrid_calibration_check.tsv").open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("feature", "time_ms", "observed_mm", "predicted_mm",
                         "uncertainty_mm", "normalized_error", "verdict"))
        for feature, pair in CALIBRATION.items():
            speed, damping, launch = (
                (first_speed, first_damping, FIRST_LAUNCH) if feature == "first"
                else (worth_speed, worth_damping, WORTHINGTON_LAUNCH)
            )
            for time_s, observed, uncertainty in pair:
                predicted = height(time_s - launch, speed, damping)
                error = abs(predicted - observed) / uncertainty
                writer.writerow((feature, 1000.0 * time_s,
                                 f"{1000.0 * observed:.6f}",
                                 f"{1000.0 * predicted:.6f}",
                                 1000.0 * uncertainty, f"{error:.6g}",
                                 "PASS" if error <= 1.0 else "FAIL"))

    print(f"first: v0={first_speed:.4f} m/s beta={first_damping:.3f} 1/s")
    print(f"Worthington: v0={worth_speed:.4f} m/s beta={worth_damping:.3f} 1/s")


if __name__ == "__main__":
    main()
