#!/usr/bin/env python3
"""Build the Case 12 visual atlas for workbook row 7 (group 2, repeat 1)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import shutil
import subprocess
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET


VIDEO_SHA256 = "dcc451a854ee9ea6ac8ae4636aacec753863bd2868254f73148a5844795b80f2"
WORKBOOK_SHA256 = "770ee400b2bf4650ed9b87b13af2ea8c013da7b72659feeb230cb92ffbf20136"
CAPTURE_FPS = 2000.0
CONTACT_FRAME = 275
# WGS-84 normal gravity at Shenzhen latitude 22.54 deg, near sea level.
GRAVITY = 9.78792

APPROACH = ((90, 77.92), (201, 43.53), (242, 20.18))
CROWN = (374, 34.38)
FIRST_JET = (
    (354, 78.86), (380, 107.57), (406, 133.43),
    (415, 140.694), (428, 151.74), (447, 179.17),
)
SECOND_JET = (
    (540, 81.83), (565, 73.5), (584, 87.38),
    (598, 106.94), (638, 128.71), (663, 142.27),
)
FIRST_PEAK_FRAME = 824
SECOND_PEAK_FRAME = 837
SELECTED_FRAMES = tuple(sorted({
    *(frame for frame, _ in APPROACH), CONTACT_FRAME, CROWN[0],
    *(frame for frame, _ in FIRST_JET),
    *(frame for frame, _ in SECOND_JET),
    FIRST_PEAK_FRAME, SECOND_PEAK_FRAME,
}))

SHEETS = (
    ("01_approach_contact_crown.jpg", (90, 201, 242, 275, 354, 374), "3x2"),
    ("02_first_jet_six_points.jpg", tuple(f for f, _ in FIRST_JET), "3x2"),
    ("03_second_jet_six_points.jpg", tuple(f for f, _ in SECOND_JET), "3x2"),
    ("04_key_events_and_fitted_peaks.jpg", (275, 374, 447, 663, 824, 837), "3x2"),
)

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("output_directory", type=Path)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def workbook_cells(path: Path) -> dict[str, str]:
    """Read the first XLSX sheet with the Python standard library only."""
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", NS):
                shared.append("".join(t.text or "" for t in item.iterfind(".//m:t", NS)))

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in relationships}
        sheet = workbook.find("m:sheets", NS)[0]
        relationship_id = sheet.attrib[f"{{{NS['r']}}}id"]
        target = targets[relationship_id]
        sheet_path = str(PurePosixPath("xl") / target) if not target.startswith("/") else target[1:]
        root = ET.fromstring(archive.read(str(PurePosixPath(sheet_path))))

        cells: dict[str, str] = {}
        for cell in root.findall(".//m:sheetData/m:row/m:c", NS):
            reference = cell.attrib["r"]
            cell_type = cell.attrib.get("t")
            value = cell.find("m:v", NS)
            if cell_type == "inlineStr":
                text = "".join(t.text or "" for t in cell.iterfind(".//m:t", NS))
            elif value is None:
                continue
            elif cell_type == "s":
                text = shared[int(value.text)]
            else:
                text = value.text or ""
            cells[reference] = text
        return cells


def as_float(cells: dict[str, str], reference: str) -> float:
    return float(cells[reference])


def validate_row7(cells: dict[str, str]) -> None:
    expected = {
        "C7": 5.05, "D7": 20.07, "E7": 2.86, "F7": 26.15,
        "G7": 90, "H7": 77.92, "I7": 201, "J7": 43.53,
        "K7": 242, "L7": 20.18, "M7": 275, "N7": 34.38, "O7": 374,
        "P7": 354, "Q7": 78.86, "R7": 406, "S7": 133.43,
        "T7": 447, "U7": 179.17, "V7": 415, "W7": 140.694,
        "X7": 380, "Y7": 107.57, "Z7": 428, "AA7": 151.74,
        "AD7": 540, "AE7": 81.83, "AF7": 584, "AH7": 638,
        "AI7": 128.71, "AJ7": 598, "AK7": 106.94, "AL7": 663,
        "AM7": 142.27, "AN7": 565, "AO7": 73.5,
    }
    for reference, wanted in expected.items():
        actual = as_float(cells, reference)
        if not math.isclose(actual, wanted, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError(f"unexpected row-7 value {reference}={actual!r}, expected {wanted!r}")
    if cells.get("AG7") != "87.38cm":
        raise ValueError(f"unexpected AG7={cells.get('AG7')!r}; expected the owner-corrected source typo")


def solve_two_by_two(matrix: list[list[float]], rhs: list[float]) -> tuple[float, float]:
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    return (
        (rhs[0] * matrix[1][1] - matrix[0][1] * rhs[1]) / determinant,
        (matrix[0][0] * rhs[1] - rhs[0] * matrix[1][0]) / determinant,
    )


def approach_fits():
    times = [(frame - CONTACT_FRAME) / CAPTURE_FPS for frame, _ in APPROACH]
    positions = [-height / 1000.0 for _, height in APPROACH]
    design = [(time, 0.5 * time * time) for time in times]
    matrix = [[sum(row[i] * row[j] for row in design) for j in range(2)] for i in range(2)]
    rhs = [sum(row[i] * value for row, value in zip(design, positions)) for i in range(2)]
    impact_speed, acceleration = solve_two_by_two(matrix, rhs)
    predictions = [impact_speed * time + 0.5 * acceleration * time * time for time in times]
    free_rmse_mm = 1000.0 * math.sqrt(sum((a - b) ** 2 for a, b in zip(predictions, positions)) / len(times))

    gravity_speed = sum(
        time * (position - 0.5 * GRAVITY * time * time)
        for time, position in zip(times, positions)
    ) / sum(time * time for time in times)
    gravity_predictions = [gravity_speed * time + 0.5 * GRAVITY * time * time for time in times]
    gravity_rmse_mm = 1000.0 * math.sqrt(
        sum((a - b) ** 2 for a, b in zip(gravity_predictions, positions)) / len(times)
    )
    return impact_speed, acceleration, free_rmse_mm, gravity_speed, gravity_rmse_mm


def ballistic_jet_fit(points: tuple[tuple[int, float], ...]):
    times = [(frame - CONTACT_FRAME) / CAPTURE_FPS for frame, _ in points]
    adjusted = [height + 500.0 * GRAVITY * time * time for time, (_, height) in zip(times, points)]
    mean_time = sum(times) / len(times)
    mean_adjusted = sum(adjusted) / len(adjusted)
    speed_mm_s = sum(
        (time - mean_time) * (value - mean_adjusted)
        for time, value in zip(times, adjusted)
    ) / sum((time - mean_time) ** 2 for time in times)
    intercept_mm = mean_adjusted - speed_mm_s * mean_time
    predictions = [
        intercept_mm + speed_mm_s * time - 500.0 * GRAVITY * time * time
        for time in times
    ]
    rmse_mm = math.sqrt(
        sum((prediction - height) ** 2 for prediction, (_, height) in zip(predictions, points))
        / len(points)
    )
    peak_time = speed_mm_s / (1000.0 * GRAVITY)
    peak_frame = CONTACT_FRAME + peak_time * CAPTURE_FPS
    peak_height = intercept_mm + speed_mm_s * peak_time - 500.0 * GRAVITY * peak_time * peak_time
    return peak_frame, peak_height, rmse_mm, speed_mm_s


def annotation(frame: int, first_fit, second_fit) -> tuple[str, str, str]:
    time_ms = 1000.0 * (frame - CONTACT_FRAME) / CAPTURE_FPS
    approach = dict(APPROACH)
    first = dict(FIRST_JET)
    second = dict(SECOND_JET)
    if frame in approach:
        role = "RING APPROACH MEASUREMENT"
        measurement = f"Ring lower-face height above water: {approach[frame]:.3f} mm"
        note = "Workbook row 7; used in contact-speed fits."
    elif frame == CONTACT_FRAME:
        role = "FIRST WATER CONTACT"
        measurement = "Ring lower face at the waterline; physical time origin."
        note = "Workbook row 7, cell M7."
    elif frame == CROWN[0]:
        role = "CROWN-SPLASH MAXIMUM"
        measurement = f"Tracked crown height: {CROWN[1]:.3f} mm"
        note = "Workbook row 7, cells N7:O7."
    elif frame in first:
        role = "FIRST-JET TRACK POINT"
        measurement = f"Tracked liquid centroid height: {first[frame]:.3f} mm"
        note = "One of six workbook points; not necessarily the true maximum."
    elif frame in second:
        role = "SECOND-JET TRACK POINT"
        measurement = f"Tracked liquid centroid height: {second[frame]:.3f} mm"
        note = "Owner correction: AG7 is 87.38 mm." if frame == 584 else "One of six workbook points; not necessarily the true maximum."
    elif frame == FIRST_PEAK_FRAME:
        role = "FIRST-JET BALLISTIC-FIT PEAK FRAME"
        measurement = f"Model: {first_fit[1]:.1f} mm at frame {first_fit[0]:.1f}"
        note = "Extrapolated with acceleration fixed to -g; not a direct measurement."
    elif frame == SECOND_PEAK_FRAME:
        role = "SECOND-JET BALLISTIC-FIT PEAK FRAME"
        measurement = f"Model: {second_fit[1]:.1f} mm at frame {second_fit[0]:.1f}"
        note = "Extrapolated with acceleration fixed to -g; not a direct measurement."
    else:
        raise KeyError(frame)
    caption = f"FRAME {frame:04d} | t = {time_ms:+.1f} ms from contact\n{role}\n{measurement}\n{note}"
    return role, measurement, caption


def main():
    args = parse_args()
    video = args.video.resolve()
    workbook = args.workbook.resolve()
    output = args.output_directory.resolve()
    for path in (video, workbook):
        if not path.is_file():
            raise FileNotFoundError(path)
    for command in ("ffmpeg", "magick"):
        if shutil.which(command) is None:
            raise RuntimeError(f"required command is unavailable: {command}")
    if sha256(video) != VIDEO_SHA256:
        raise ValueError("video SHA256 mismatch")
    if sha256(workbook) != WORKBOOK_SHA256:
        raise ValueError("workbook SHA256 mismatch")
    cells = workbook_cells(workbook)
    validate_row7(cells)

    approach = approach_fits()
    first_fit = ballistic_jet_fit(FIRST_JET)
    second_fit = ballistic_jet_fit(SECOND_JET)
    raw_directory = output / "raw"
    annotated_directory = output / "annotated"
    sheet_directory = output / "sheets"
    for directory in (raw_directory, annotated_directory, sheet_directory):
        directory.mkdir(parents=True, exist_ok=True)

    rows = []
    annotated_paths: dict[int, Path] = {}
    for frame in SELECTED_FRAMES:
        raw_path = raw_directory / f"frame_{frame:04d}.png"
        annotated_path = annotated_directory / f"frame_{frame:04d}_annotated.jpg"
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
            "-vf", f"select=eq(n\\,{frame})", "-frames:v", "1", str(raw_path),
        ])
        role, measurement, caption = annotation(frame, first_fit, second_fit)
        run([
            "magick", str(raw_path),
            "(", "-size", "1280x235", "xc:#101820", "-fill", "white",
            "-font", "DejaVu-Sans", "-pointsize", "24", "-gravity", "northwest",
            "-annotate", "+30+25", caption, ")", "-append", "-strip",
            "-quality", "94", str(annotated_path),
        ])
        annotated_paths[frame] = annotated_path
        rows.append({
            "frame": frame,
            "time_after_contact_ms": f"{1000.0 * (frame - CONTACT_FRAME) / CAPTURE_FPS:.6g}",
            "role": role,
            "measurement_or_model": measurement,
            "raw_file": raw_path.relative_to(output).as_posix(),
            "raw_sha256": sha256(raw_path),
            "annotated_file": annotated_path.relative_to(output).as_posix(),
            "annotated_sha256": sha256(annotated_path),
        })
    with (output / "frame_index.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, delimiter="\t", fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    for filename, frames, tile in SHEETS:
        run([
            "magick", "montage", *(str(annotated_paths[frame]) for frame in frames),
            "-tile", tile, "-geometry", "620x+18+18", "-background", "#e8edf1",
            "-strip", "-quality", "92", str(sheet_directory / filename),
        ])

    observation_rows = []
    for frame, height in APPROACH:
        observation_rows.append(("approach", frame, height, "mm", "ring lower-face height above water", "workbook"))
    observation_rows.append(("contact", CONTACT_FRAME, 0.0, "mm", "first contact", "workbook"))
    observation_rows.append(("crown", CROWN[0], CROWN[1], "mm", "maximum tracked crown height", "workbook"))
    for frame, height in FIRST_JET:
        observation_rows.append(("first_jet", frame, height, "mm", "tracked liquid centroid height", "workbook"))
    for frame, height in SECOND_JET:
        basis = "owner-corrected AG7 unit: 87.38 mm" if frame == 584 else "workbook"
        observation_rows.append(("second_jet", frame, height, "mm", "tracked liquid centroid height", basis))
    with (output / "row7_observations.tsv").open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("phase", "frame", "time_after_contact_ms", "value", "unit", "quantity", "basis"))
        for phase, frame, value, unit, quantity, basis in observation_rows:
            writer.writerow((phase, frame, f"{1000.0 * (frame-CONTACT_FRAME)/CAPTURE_FPS:.6g}", f"{value:.12g}", unit, quantity, basis))

    calculation_rows = (
        ("approach_contact_constrained_free_acceleration", "impact_speed", approach[0], "m/s", "three approach points; contact position fixed to zero"),
        ("approach_contact_constrained_free_acceleration", "effective_acceleration", approach[1], "m/s2", "fitted rather than assumed"),
        ("approach_contact_constrained_free_acceleration", "position_rmse", approach[2], "mm", "three approach points"),
        ("approach_contact_constrained_shenzhen_gravity", "gravity", GRAVITY, "m/s2", "WGS-84 normal gravity at latitude 22.54 deg near sea level"),
        ("approach_contact_constrained_shenzhen_gravity", "impact_speed", approach[3], "m/s", "acceleration fixed to Shenzhen normal gravity"),
        ("approach_contact_constrained_shenzhen_gravity", "position_rmse", approach[4], "mm", "three approach points"),
        ("approach_contact_constrained_shenzhen_gravity", "equivalent_vacuum_release_height", 1000.0 * approach[3] ** 2 / (2.0 * GRAVITY), "mm", "derived scale, not supplied release height"),
        ("first_jet_ballistic_extrapolation", "peak_frame", first_fit[0], "frame", "six centroid points; vertical acceleration fixed to -g"),
        ("first_jet_ballistic_extrapolation", "peak_height", first_fit[1], "mm", "model extrapolation beyond the six measured points"),
        ("first_jet_ballistic_extrapolation", "height_rmse", first_fit[2], "mm", "six centroid points"),
        ("second_jet_ballistic_extrapolation", "peak_frame", second_fit[0], "frame", "six centroid points; owner confirms AG7 is 87.38 mm"),
        ("second_jet_ballistic_extrapolation", "peak_height", second_fit[1], "mm", "model extrapolation beyond the six measured points"),
        ("second_jet_ballistic_extrapolation", "height_rmse", second_fit[2], "mm", "six centroid points"),
    )
    with (output / "row7_calculations.tsv").open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("model", "quantity", "value", "unit", "note"))
        for model, quantity, value, unit, note in calculation_rows:
            writer.writerow((model, quantity, f"{value:.12g}", unit, note))

    with (output / "source_lock.tsv").open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("source", "sha256", "tracked", "note"))
        writer.writerow((video, VIDEO_SHA256, "no", "read-only owner-supplied 1584-frame MP4"))
        writer.writerow((workbook, WORKBOOK_SHA256, "no", "read-only owner-supplied XLSX; row 7 transcribed"))

    print(f"frames={len(SELECTED_FRAMES)} contact_speed_free={approach[0]:.9f} m/s")
    print(f"first_peak={first_fit[1]:.6f} mm@{first_fit[0]:.6f} second_peak={second_fit[1]:.6f} mm@{second_fit[0]:.6f}")


if __name__ == "__main__":
    main()
