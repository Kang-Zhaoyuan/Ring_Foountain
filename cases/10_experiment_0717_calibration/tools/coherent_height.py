#!/usr/bin/env python3
"""Measure sampled water height with and without detached droplets."""

import argparse
import csv
from collections import deque
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("output_tsv", type=Path)
    parser.add_argument("--contact-time-s", type=float, required=True)
    parser.add_argument("--f-threshold", type=float, default=0.5)
    parser.add_argument("--cs-threshold", type=float, default=0.5)
    parser.add_argument("--central-radius-m", type=float, default=0.01)
    parser.add_argument("--connectivity", choices=(4, 8), type=int, default=4)
    parser.add_argument("--start-s", type=float, default=0.0)
    parser.add_argument("--end-s", type=float, default=float("inf"))
    return parser.parse_args()


def read_index(path):
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    required = {"time_s", "file", "ring_center_lab_m"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"invalid fields index: {path}")
    return rows


def read_grid(path):
    coordinates = []
    with path.open() as stream:
        for line in stream:
            if not line.strip() or line.startswith("#"):
                continue
            values = line.split()
            coordinates.append((float(values[0]), float(values[1])))

    if not coordinates:
        raise ValueError(f"empty sampled field: {path}")
    first_x = coordinates[0][0]
    ny = next(
        (index for index, (x, _) in enumerate(coordinates) if x != first_x),
        len(coordinates),
    )
    if len(coordinates) % ny:
        raise ValueError(f"non-rectangular sampled field: {path}")
    nx = len(coordinates) // ny
    xs = [coordinates[i * ny][0] for i in range(nx)]
    ys = [coordinates[j][1] for j in range(ny)]
    for i in range(nx):
        for j in range(ny):
            if coordinates[i * ny + j] != (xs[i], ys[j]):
                raise ValueError(f"non-tensor sampled grid: {path}")
    return nx, ny, xs, ys


def read_water_mask(path, count, f_threshold, cs_threshold):
    water = bytearray(count)
    index = 0
    with path.open() as stream:
        for line in stream:
            if not line.strip() or line.startswith("#"):
                continue
            values = line.split()
            if len(values) < 5:
                raise ValueError(f"invalid sampled row in {path}")
            if float(values[3]) >= f_threshold and float(values[4]) >= cs_threshold:
                water[index] = 1
            index += 1
    if index != count:
        raise ValueError(f"grid size changed in {path}: {index} != {count}")
    return water


def main_component(water, nx, ny, connectivity):
    visited = bytearray(len(water))
    queue = deque()

    # The lowest axial sample is always inside the main pool for these moving
    # ring-frame runs, so it provides an unambiguous main-water seed.
    for j in range(ny):
        if water[j]:
            visited[j] = 1
            queue.append(j)
    if not queue:
        raise ValueError("no water seed on the lowest axial sample")

    diagonals = ((-1, -1), (-1, 1), (1, -1), (1, 1)) if connectivity == 8 else ()
    offsets = ((-1, 0), (1, 0), (0, -1), (0, 1)) + diagonals
    while queue:
        current = queue.popleft()
        i, j = divmod(current, ny)
        for di, dj in offsets:
            ni, nj = i + di, j + dj
            if 0 <= ni < nx and 0 <= nj < ny:
                neighbor = ni * ny + nj
                if water[neighbor] and not visited[neighbor]:
                    visited[neighbor] = 1
                    queue.append(neighbor)
    return visited


def format_number(value):
    return "nan" if value is None else f"{value:.12g}"


def main():
    args = parse_args()
    run_directory = args.run_directory.resolve()
    rows = read_index(run_directory / "fields.tsv")
    selected = [
        row for row in rows
        if args.start_s <= float(row["time_s"]) <= args.end_s
    ]
    if not selected:
        raise ValueError("no indexed fields in the requested time interval")

    first_path = run_directory / selected[0]["file"]
    nx, ny, xs, ys = read_grid(first_path)
    count = nx * ny
    args.output_tsv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = (
        "time_s", "time_after_contact_ms", "ring_center_lab_m",
        "all_water_top_m", "coherent_top_m", "coherent_top_radius_m",
        "central_coherent_top_m", "detached_water_top_m",
        "water_samples", "coherent_samples", "detached_samples",
    )
    with args.output_tsv.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream, delimiter="\t", fieldnames=fieldnames, lineterminator="\n"
        )
        writer.writeheader()
        for number, row in enumerate(selected, start=1):
            time_s = float(row["time_s"])
            center = float(row["ring_center_lab_m"])
            field_path = run_directory / row["file"]
            water = read_water_mask(
                field_path, count, args.f_threshold, args.cs_threshold
            )
            coherent = main_component(water, nx, ny, args.connectivity)

            all_top = coherent_top = coherent_radius = central_top = None
            detached_top = None
            water_count = coherent_count = 0
            for index, is_water in enumerate(water):
                if not is_water:
                    continue
                water_count += 1
                i, j = divmod(index, ny)
                z = xs[i] + center
                if all_top is None or z > all_top:
                    all_top = z
                if coherent[index]:
                    coherent_count += 1
                    if coherent_top is None or z > coherent_top:
                        coherent_top = z
                        coherent_radius = ys[j]
                    if ys[j] <= args.central_radius_m and (
                        central_top is None or z > central_top
                    ):
                        central_top = z
                elif detached_top is None or z > detached_top:
                    detached_top = z

            output = {
                "time_s": f"{time_s:.12g}",
                "time_after_contact_ms": f"{(time_s - args.contact_time_s)*1000:.9g}",
                "ring_center_lab_m": f"{center:.12g}",
                "all_water_top_m": format_number(all_top),
                "coherent_top_m": format_number(coherent_top),
                "coherent_top_radius_m": format_number(coherent_radius),
                "central_coherent_top_m": format_number(central_top),
                "detached_water_top_m": format_number(detached_top),
                "water_samples": water_count,
                "coherent_samples": coherent_count,
                "detached_samples": water_count - coherent_count,
            }
            writer.writerow(output)
            print(f"[{number}/{len(selected)}] {field_path.name}", flush=True)


if __name__ == "__main__":
    main()
