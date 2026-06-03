from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageSequence


def parse_canvas_size(value: str) -> tuple[int, int]:
    if "x" not in value.lower():
        raise argparse.ArgumentTypeError("Canvas size must use WIDTHxHEIGHT, for example 512x512")
    width, height = value.lower().split("x", 1)
    return int(width), int(height)


def png_frames(source: Path) -> list[Path]:
    return sorted(source.glob("*.png"))


def validate_source_frames(source: Path, expected_count: int, canvas_size: tuple[int, int]) -> list[Path]:
    frames = png_frames(source)
    if len(frames) != expected_count:
        raise SystemExit(f"{source}: expected {expected_count} png frames, found {len(frames)}")
    for frame in frames:
        with Image.open(frame) as loaded:
            image = loaded.convert("RGBA")
            if image.size != canvas_size:
                raise SystemExit(f"{frame}: expected canvas {canvas_size}, found {image.size}")
            if image.getbbox() is None:
                raise SystemExit(f"{frame}: frame is empty")
    return frames


def copy_normalized_frames(frames: list[Path], target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for index, frame in enumerate(frames):
        shutil.copy2(frame, target / f"{index:02d}.png")


def save_normalized_frames(frames: list[Image.Image], target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for index, frame in enumerate(frames):
        frame.convert("RGBA").save(target / f"{index:02d}.png")


def validate_gif_frames(source_gif: Path, expected_count: int, canvas_size: tuple[int, int]) -> list[Image.Image]:
    if not source_gif.exists():
        raise SystemExit(f"GIF source does not exist: {source_gif}")
    frames: list[Image.Image] = []
    with Image.open(source_gif) as loaded:
        for frame in ImageSequence.Iterator(loaded):
            image = frame.convert("RGBA")
            if image.size != canvas_size:
                raise SystemExit(f"{source_gif}: expected canvas {canvas_size}, found {image.size}")
            if image.getbbox() is None:
                raise SystemExit(f"{source_gif}: GIF frame {len(frames)} is empty")
            frames.append(image.copy())
    if len(frames) != expected_count:
        raise SystemExit(f"{source_gif}: expected {expected_count} gif frames, found {len(frames)}")
    return frames


def backup_existing_action(target: Path, backup_root: Path, action: str) -> Path | None:
    existing = png_frames(target) if target.exists() else []
    if not existing:
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / f"{action}_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for frame in existing:
        shutil.copy2(frame, backup_dir / frame.name)
    return backup_dir


def replace_action_frames(batch_root: Path, action: str, source: Path, expected_count: int, canvas_size: tuple[int, int]) -> dict:
    frames = validate_source_frames(source, expected_count, canvas_size)
    target = batch_root / "clean" / action
    existing = png_frames(target) if target.exists() else []
    if existing and len(existing) != expected_count:
        raise SystemExit(f"{target}: expected 0 or {expected_count} existing png frames, found {len(existing)}")
    backup = backup_existing_action(target, batch_root / "qa" / "import_backups", action)

    target.mkdir(parents=True, exist_ok=True)
    copy_normalized_frames(frames, target)

    report = {
        "action": action,
        "source": str(source),
        "source_type": "png_directory",
        "target": str(target),
        "imported_count": len(frames),
        "canvas_size": list(canvas_size),
        "backup": str(backup) if backup else None,
    }
    report_path = batch_root / "qa" / f"import_report_{action}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def replace_action_from_gif(
    batch_root: Path,
    action: str,
    source_gif: Path,
    expected_count: int,
    canvas_size: tuple[int, int],
) -> dict:
    frames = validate_gif_frames(source_gif, expected_count, canvas_size)
    target = batch_root / "clean" / action
    existing = png_frames(target) if target.exists() else []
    if existing and len(existing) != expected_count:
        raise SystemExit(f"{target}: expected 0 or {expected_count} existing png frames, found {len(existing)}")
    backup = backup_existing_action(target, batch_root / "qa" / "import_backups", action)

    target.mkdir(parents=True, exist_ok=True)
    save_normalized_frames(frames, target)

    report = {
        "action": action,
        "source": str(source_gif),
        "source_type": "gif",
        "target": str(target),
        "imported_count": len(frames),
        "canvas_size": list(canvas_size),
        "backup": str(backup) if backup else None,
        "note": "GIF was imported as normalized PNG frames for the production sprite pipeline.",
    }
    report_path = batch_root / "qa" / f"import_report_{action}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-root", type=Path, required=True)
    parser.add_argument("--action", required=True)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--source", type=Path, help="Directory containing transparent PNG frames.")
    source_group.add_argument("--source-gif", type=Path, help="Animated GIF to split into normalized PNG frames.")
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--canvas-size", type=parse_canvas_size, required=True)
    args = parser.parse_args()

    if args.source_gif:
        report = replace_action_from_gif(
            batch_root=args.batch_root,
            action=args.action,
            source_gif=args.source_gif,
            expected_count=args.expected_count,
            canvas_size=args.canvas_size,
        )
    else:
        report = replace_action_frames(
            batch_root=args.batch_root,
            action=args.action,
            source=args.source,
            expected_count=args.expected_count,
            canvas_size=args.canvas_size,
        )
    print(
        "production_action_import_ok "
        f"action={report['action']} frames={report['imported_count']} target={report['target']}"
    )


if __name__ == "__main__":
    main()
