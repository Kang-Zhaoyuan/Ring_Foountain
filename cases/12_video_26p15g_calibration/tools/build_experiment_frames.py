#!/usr/bin/env python3
"""Extract and annotate the laboratory-video reference frames."""

import argparse
import csv
import hashlib
import math
import shutil
import subprocess
from pathlib import Path


EXPECTED_VIDEO_SHA256 = (
    "c5982c4ee7c2332d9798de1cc61a57400bb9acb694d9bfbb5473dba189ab8c07"
)
CONTACT_FRAME = 300
CAPTURE_FPS = 2000.0
GRAVITY = 9.81
IMPACT_SPEED = 1.3455503811482585
TERMINAL_SPEED = 0.7204147743288176
DECAY_RATE = 76.91121418549537


FRAME_SPECS = (
    (103, "approach", "trajectory_fit", "Ring airborne; manual lower-face height is 85.161 mm."),
    (155, "approach", "trajectory_fit", "Ring airborne; manual lower-face height is 71.613 mm."),
    (
        280, "approach", "geometry_limit",
        "Near impact; about 5 deg of depth-direction tilt has developed.",
    ),
    (300, "contact", "time_origin", "First water contact; this frame defines physical time zero."),
    (
        335, "early_entry", "morphology_holdout",
        "Shallow crown splash and the initial open air cavity.",
    ),
    (
        360, "early_entry", "morphology_holdout",
        "A thin central rise is visible inside the expanding crown.",
    ),
    (384, "first_jet", "trajectory_fit", "Open cavity and crown; manual ring depth is 38.064 mm."),
    (
        405, "first_jet", "morphology_target",
        "Thin, slightly left-curved first jet with a surrounding crown.",
    ),
    (
        430, "first_jet", "morphology_holdout",
        "The thin first jet persists while the cavity remains open.",
    ),
    (
        455, "cavity_taper", "morphology_holdout",
        "The first jet persists as the air cavity narrows.",
    ),
    (
        492, "cavity_closure", "topology_target",
        "Cavity closure with an hourglass air shape; first jet persists.",
    ),
    (
        520, "post_closure", "morphology_holdout",
        "Ring is separated from the cavity; the surrounding surface relaxes.",
    ),
    (
        550, "later_jet", "morphology_holdout",
        "A later central rise begins on a nearly flat surrounding surface.",
    ),
    (
        587, "later_jet", "chronology_target",
        "Prominent later central jet; a clear representative frame.",
    ),
    (
        620, "later_jet", "morphology_holdout",
        "The later jet remains tall and narrow above the submerged ring.",
    ),
)


MANUAL_POSITION_MM = {
    103: -85.16129,
    155: -71.6129,
    384: 38.064,
    405: 45.80645,
}


SHEETS = (
    ("01_approach_and_contact.jpg", (103, 155, 280, 300), "2x2"),
    ("02_early_entry_and_first_jet.jpg", (335, 360, 384, 405, 430, 455), "3x2"),
    ("03_closure_and_later_jet.jpg", (492, 520, 550, 587, 620), "3x2"),
)


CALLOUT_SPECS = (
    {
        "filename": "01_ring_and_waterline_frame_0280.jpg",
        "frame": 280,
        "title": "Ring approaching the waterline",
        "note": "Identifies the metal ring and the undisturbed waterline before contact.",
        "crop": "650x300+180+330",
        "resize": "1300x600",
        "labels": (
            ("+40+45", "METAL RING"),
            ("+760+520", "UNDISTURBED WATERLINE"),
        ),
        "draw": (
            "ellipse 540,380 130,42 0,360 "
            "line 235,85 425,335 line 425,335 405,315 line 425,335 395,343 "
            "line 1120,505 1120,450"
        ),
    },
    {
        "filename": "02_first_contact_frame_0300.jpg",
        "frame": 300,
        "title": "First water contact",
        "note": "Identifies the ring at the contact-frame time origin and the waterline.",
        "crop": "650x300+180+350",
        "resize": "1300x600",
        "labels": (
            ("+40+45", "METAL RING AT FIRST CONTACT"),
            ("+820+520", "UNDISTURBED WATERLINE"),
        ),
        "draw": (
            "ellipse 540,400 145,45 0,360 "
            "line 300,85 430,350 line 430,350 425,310 line 430,350 395,325 "
            "line 1120,505 1120,450"
        ),
    },
    {
        "filename": "03_first_jet_and_open_cavity_frame_0405.jpg",
        "frame": 405,
        "title": "First jet, crown, and open cavity",
        "note": "Labels the thin first jet, crown splash, open air cavity, and submerged ring.",
        "crop": "650x650+150+180",
        "resize": "1300x1300",
        "labels": (
            ("+850+90", "FIRST JET"),
            ("+850+600", "CROWN SPLASH"),
            ("+40+850", "AIR CAVITY"),
            ("+850+1120", "METAL RING"),
        ),
        "draw": (
            "line 880,135 640,340 line 640,340 660,305 line 640,340 680,335 "
            "line 880,645 810,680 line 810,680 835,650 line 810,680 850,690 "
            "line 260,895 430,850 line 430,850 395,840 line 430,850 405,875 "
            "line 880,1165 735,1030 line 735,1030 748,1070 line 735,1030 775,1038"
        ),
    },
    {
        "filename": "04_hourglass_closure_frame_0492.jpg",
        "frame": 492,
        "title": "Hourglass cavity at closure",
        "note": "Labels the first-jet remnant, hourglass air cavity, cavity neck, and ring.",
        "crop": "650x650+150+250",
        "resize": "1300x1300",
        "labels": (
            ("+820+80", "FIRST JET REMNANT"),
            ("+40+700", "HOURGLASS AIR CAVITY"),
            ("+850+820", "CAVITY NECK"),
            ("+850+1120", "METAL RING"),
        ),
        "draw": (
            "line 850,125 650,250 line 650,250 675,220 line 650,250 690,255 "
            "line 370,745 500,700 line 500,700 465,690 line 500,700 480,730 "
            "line 880,865 650,800 line 650,800 680,780 line 650,800 680,820 "
            "line 880,1165 730,980 line 730,980 738,1020 line 730,980 770,990"
        ),
    },
    {
        "filename": "05_later_jet_frame_0587.jpg",
        "frame": 587,
        "title": "Later central jet",
        "note": "Labels the later jet, mostly flat surrounding surface, and submerged ring.",
        "crop": "650x650+150+250",
        "resize": "1300x1300",
        "labels": (
            ("+850+100", "LATER JET"),
            ("+40+650", "MOSTLY FLAT SURFACE"),
            ("+750+1160", "SUBMERGED METAL RING"),
        ),
        "draw": (
            "line 880,145 650,310 line 650,310 670,275 line 650,310 690,305 "
            "line 340,695 450,620 line 450,620 410,625 line 450,620 430,655 "
            "line 780,1205 700,1040 line 700,1040 695,1080 line 700,1040 735,1060"
        ),
    },
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("output_directory", type=Path)
    return parser.parse_args()


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def trajectory(frame):
    time_s = (frame - CONTACT_FRAME) / CAPTURE_FPS
    if time_s <= 0.0:
        position_m = IMPACT_SPEED * time_s + 0.5 * GRAVITY * time_s**2
        speed_mps = IMPACT_SPEED + GRAVITY * time_s
        speed_basis = "ballistic estimate from fitted impact speed"
    else:
        transient = -math.expm1(-DECAY_RATE * time_s) / DECAY_RATE
        position_m = TERMINAL_SPEED * time_s + (
            IMPACT_SPEED - TERMINAL_SPEED
        ) * transient
        speed_mps = TERMINAL_SPEED + (
            IMPACT_SPEED - TERMINAL_SPEED
        ) * math.exp(-DECAY_RATE * time_s)
        speed_basis = "post-contact exponential trajectory fit"
    return time_s, position_m * 1000.0, speed_mps, speed_basis


def position_label(position_mm, basis):
    if abs(position_mm) < 5e-7:
        return "Ring lower face: at undisturbed water level (contact definition)"
    direction = "depth below" if position_mm > 0.0 else "height above"
    return f"Ring lower-face {direction} water: {abs(position_mm):.3f} mm ({basis})"


def run(command):
    subprocess.run(command, check=True)


def main():
    args = parse_args()
    video = args.video.resolve()
    output = args.output_directory.resolve()
    if not video.is_file():
        raise FileNotFoundError(video)
    for command in ("ffmpeg", "magick"):
        if shutil.which(command) is None:
            raise RuntimeError(f"required command is unavailable: {command}")

    video_hash = sha256(video)
    if video_hash != EXPECTED_VIDEO_SHA256:
        raise ValueError(
            f"video SHA256 mismatch: {video_hash} != {EXPECTED_VIDEO_SHA256}"
        )

    raw_directory = output / "raw"
    annotated_directory = output / "annotated"
    callout_directory = output / "callouts"
    sheet_directory = output / "sheets"
    for directory in (
        raw_directory, annotated_directory, callout_directory, sheet_directory
    ):
        directory.mkdir(parents=True, exist_ok=True)

    rows = []
    annotated_paths = {}
    for frame, phase, use, observation in FRAME_SPECS:
        raw_path = raw_directory / f"frame_{frame:04d}.png"
        annotated_path = annotated_directory / f"frame_{frame:04d}_annotated.jpg"
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(video), "-vf", f"select=eq(n\\,{frame})",
            "-frames:v", "1", str(raw_path),
        ])

        time_s, fitted_position, speed, speed_basis = trajectory(frame)
        if frame in MANUAL_POSITION_MM:
            position = MANUAL_POSITION_MM[frame]
            position_basis = "manual pixel measurement"
        elif frame == CONTACT_FRAME:
            position = 0.0
            position_basis = "contact-frame definition"
        else:
            position = fitted_position
            position_basis = "trajectory model"

        caption = (
            f"FRAME {frame:04d}  |  t = {time_s * 1000.0:+.1f} ms from contact  |  "
            f"ring U_down = {speed:.3f} m/s\n"
            f"Speed basis: {speed_basis}; this is not a direct per-frame measurement.\n"
            f"{observation}\n"
            f"{position_label(position, position_basis)}"
        )
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
            "time_after_contact_ms": f"{time_s * 1000.0:.6g}",
            "phase": phase,
            "use": use,
            "observation": observation,
            "ring_lower_face_down_mm": f"{position:.12g}",
            "position_basis": position_basis,
            "ring_speed_down_mps": f"{speed:.12g}",
            "speed_basis": speed_basis,
            "raw_file": raw_path.relative_to(output).as_posix(),
            "raw_sha256": sha256(raw_path),
            "annotated_file": annotated_path.relative_to(output).as_posix(),
            "annotated_sha256": sha256(annotated_path),
        })

    with (output / "frame_index.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream, delimiter="\t", fieldnames=rows[0].keys(), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)

    for filename, frames, tile in SHEETS:
        run([
            "magick", "montage",
            *(str(annotated_paths[frame]) for frame in frames),
            "-tile", tile, "-geometry", "620x+18+18", "-background", "#e8edf1",
            "-strip", "-quality", "92", str(sheet_directory / filename),
        ])

    callout_rows = []
    callout_paths = []
    for spec in CALLOUT_SPECS:
        raw_path = raw_directory / f"frame_{spec['frame']:04d}.png"
        callout_path = callout_directory / spec["filename"]
        command = [
            "magick", str(raw_path), "-crop", spec["crop"], "+repage",
            "-resize", spec["resize"], "-font", "DejaVu-Sans-Bold",
            "-pointsize", "32", "-fill", "#ffe066",
            "-undercolor", "#101820cc", "-gravity", "northwest",
        ]
        for offset, label in spec["labels"]:
            command.extend(("-annotate", offset, label))
        command.extend((
            "-undercolor", "none", "-fill", "none", "-stroke", "#ffe066",
            "-strokewidth", "5", "-draw", spec["draw"], "-strip", "-quality",
            "94", str(callout_path),
        ))
        run(command)
        callout_paths.append(callout_path)
        callout_rows.append({
            "file": callout_path.relative_to(output).as_posix(),
            "frame": spec["frame"],
            "title": spec["title"],
            "note": spec["note"],
            "source_raw_file": raw_path.relative_to(output).as_posix(),
            "sha256": sha256(callout_path),
        })

    with (output / "callout_index.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream, delimiter="\t", fieldnames=callout_rows[0].keys(),
            lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(callout_rows)

    run([
        "magick", "montage", *(str(path) for path in callout_paths),
        "-tile", "3x2", "-geometry", "620x+18+18", "-background", "#e8edf1",
        "-strip", "-quality", "92", str(sheet_directory / "04_object_callouts.jpg"),
    ])

    print(f"video_sha256\t{video_hash}")
    print(f"frames\t{len(rows)}")
    print(f"callouts\t{len(callout_rows)}")
    print(f"output\t{output}")


if __name__ == "__main__":
    main()
