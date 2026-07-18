#!/usr/bin/env python3
"""Derive trajectory and nondimensional constraints from video labels."""

import argparse
import csv
import math
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("observations", type=Path)
    parser.add_argument("model_parameters", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--fps", type=float, default=2000.0)
    parser.add_argument("--contact-frame", type=int, default=300)
    parser.add_argument("--gravity", type=float, default=9.81)
    return parser.parse_args()


def read_tsv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def model_values(path):
    return {row["parameter"]: row["value"] for row in read_tsv(path)}


def fmt(value):
    if isinstance(value, int):
        return str(value)
    return f"{value:.12g}"


def main():
    args = parse_args()
    observations = read_tsv(args.observations)
    model = model_values(args.model_parameters)

    preimpact = [
        row for row in observations
        if row["use"] == "impact_trajectory_fit"
    ]
    impact_speeds = []
    for row in preimpact:
        time = (int(row["frame"]) - args.contact_frame)/args.fps
        position = -float(row["value"])/1000.0
        speed = (position - 0.5*args.gravity*time*time)/time
        impact_speeds.append((int(row["frame"]), speed))
    impact_mean = sum(speed for _, speed in impact_speeds)/len(impact_speeds)

    postimpact = [
        row for row in observations
        if row["use"] == "post_impact_trajectory_fit"
    ]
    if len(postimpact) != 2:
        raise ValueError("exactly two post-impact trajectory labels required")
    t1, t2 = [
        (int(row["frame"]) - args.contact_frame)/args.fps
        for row in postimpact
    ]
    z1, z2 = [float(row["value"])/1000.0 for row in postimpact]
    determinant = 0.5*t1*t2*(t2 - t1)
    post_v0 = (0.5*z1*t2*t2 - 0.5*z2*t1*t1)/determinant
    post_accel = (t1*z2 - t2*z1)/determinant

    def exponential_integral(rate, time):
        return -math.expm1(-rate*time)/rate

    def inferred_terminal(rate, time, position):
        transient = exponential_integral(rate, time)
        return (position - transient*impact_mean)/(time - transient)

    def terminal_mismatch(rate):
        return inferred_terminal(rate, t1, z1) - inferred_terminal(rate, t2, z2)

    bracket = None
    previous_rate = 0.01
    previous_value = terminal_mismatch(previous_rate)
    for index in range(2, 20001):
        rate = 0.01*index
        value = terminal_mismatch(rate)
        if value*previous_value <= 0.0:
            bracket = (previous_rate, rate)
            break
        previous_rate, previous_value = rate, value
    if bracket is None:
        raise ValueError("could not bracket exponential trajectory fit")
    lower, upper = bracket
    for _ in range(100):
        middle = 0.5*(lower + upper)
        if terminal_mismatch(lower)*terminal_mismatch(middle) <= 0.0:
            upper = middle
        else:
            lower = middle
    decay_rate = 0.5*(lower + upper)
    terminal_speed = inferred_terminal(decay_rate, t1, z1)

    closure = next(row for row in observations if row["quantity"] == "cavity_closure")
    closure_time = (int(closure["frame"]) - args.contact_frame)/args.fps
    closure_depth_constant_accel = (
        post_v0*closure_time + 0.5*post_accel*closure_time**2
    )
    closure_transient = exponential_integral(decay_rate, closure_time)
    closure_depth = (
        closure_transient*impact_mean +
        (closure_time - closure_transient)*terminal_speed
    )

    Ri = float(model["Ri"])
    Ro = float(model["Ro"])
    thickness = float(model["ring_thickness"])
    mass = float(model["ring_mass"])
    volume = math.pi*(Ro*Ro - Ri*Ri)*thickness
    diameter = 2.0*Ro
    rho_water = 998.0
    mu_water = 1.0e-3
    sigma = float(model["surface_tension"])
    speed_spread = max(speed for _, speed in impact_speeds) - min(
        speed for _, speed in impact_speeds
    )

    rows = [
        ("source_capture_rate", args.fps, "fps", "user supplied original high_speed rate"),
        ("physical_frame_interval", 1000.0/args.fps, "ms", "one over source capture rate"),
        ("contact_frame", args.contact_frame, "frame", "user classification"),
    ]
    rows.extend(
        (f"impact_speed_from_frame_{frame}", speed, "m/s",
         f"ballistic back_extrapolation with g={fmt(args.gravity)}")
        for frame, speed in impact_speeds
    )
    rows.extend([
        ("impact_speed_mean", impact_mean, "m/s", "mean of independent labels"),
        ("impact_speed_spread", speed_spread, "m/s", "maximum minus minimum"),
        ("equivalent_vacuum_release_height", impact_mean**2/(2.0*args.gravity), "m",
         "mean impact speed squared over 2g"),
        ("equivalent_vacuum_contact_time", impact_mean/args.gravity, "s",
         "impact speed over g"),
        ("post_impact_constant_accel_v0", post_v0, "m/s",
         "two_point descriptive fit to frames 384 and 405"),
        ("post_impact_constant_accel", post_accel, "m/s2",
         "two_point descriptive fit not a force law"),
        ("closure_depth_constant_accel", closure_depth_constant_accel, "m",
         "descriptive quadratic fit evaluated at frame 492"),
        ("trajectory_decay_rate", decay_rate, "1/s",
         "continuous exponential velocity fit to frames 384 and 405"),
        ("trajectory_terminal_speed", terminal_speed, "m/s",
         "continuous exponential velocity fit to frames 384 and 405"),
        ("closure_depth_exponential", closure_depth, "m",
         "selected trajectory fit evaluated at frame 492"),
        ("ring_volume", volume, "m3",
         "pi times Ro squared minus Ri squared times thickness"),
        ("equivalent_density", mass/volume, "kg/m3",
         "measured mass over rectangular annulus volume"),
        ("Re_D", rho_water*impact_mean*diameter/mu_water, "-",
         "D=40.14 mm U=impact_speed_mean"),
        ("We_D", rho_water*impact_mean**2*diameter/sigma, "-",
         "D=40.14 mm U=impact_speed_mean"),
        ("Fr_D", impact_mean/math.sqrt(args.gravity*diameter), "-",
         "D=40.14 mm U=impact_speed_mean"),
        ("Bo_D", rho_water*args.gravity*diameter**2/sigma, "-", "D=40.14 mm"),
        ("Ca", mu_water*impact_mean/sigma, "-", "water properties at impact_speed_mean"),
        ("Oh_D", mu_water/math.sqrt(rho_water*sigma*diameter), "-", "D=40.14 mm"),
    ])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("quantity", "value", "unit", "derivation_or_note"))
        for quantity, value, unit, note in rows:
            writer.writerow((quantity, fmt(value), unit, note))


if __name__ == "__main__":
    main()
