from __future__ import annotations

import argparse
import math
import shutil
from pathlib import Path

from PIL import Image


CANVAS = 512
SPECS = {
    "happy": 48,
    "cute": 44,
}


def ease_in_out(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def source_crop(source: Image.Image) -> Image.Image:
    bbox = source.getbbox()
    if bbox is None:
        raise SystemExit("Source image is empty")
    return source.crop(bbox)


def transform_frame(crop: Image.Image, y_offset: int, scale_x: float = 1.0, scale_y: float = 1.0, rotation: float = 0.0) -> Image.Image:
    width = max(1, round(crop.width * scale_x))
    height = max(1, round(crop.height * scale_y))
    image = crop.resize((width, height), Image.Resampling.LANCZOS)
    if rotation:
        image = image.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=True)
    frame = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    x = (CANVAS - image.width) // 2
    base_bottom = 494
    y = base_bottom - image.height + y_offset
    frame.alpha_composite(image, (x, y))
    return frame


def happy_values(index: int, count: int) -> tuple[int, float, float, float]:
    t = index / (count - 1)
    if t < 0.16:
        p = ease_in_out(t / 0.16)
        y = round(8 * p)
        sx = 1.0 + 0.018 * p
        sy = 1.0 - 0.018 * p
    elif t < 0.54:
        p = ease_in_out((t - 0.16) / 0.38)
        y = round(8 - 46 * p)
        sx = 1.018 - 0.028 * p
        sy = 0.982 + 0.045 * p
    elif t < 0.76:
        p = ease_in_out((t - 0.54) / 0.22)
        y = round(-38 + 38 * p)
        sx = 0.99 + 0.02 * p
        sy = 1.027 - 0.032 * p
    else:
        p = (t - 0.76) / 0.24
        y = round(math.sin(p * math.pi * 2.0) * 5 * (1.0 - p))
        sx = 1.0 + math.sin(p * math.pi * 2.0) * 0.008 * (1.0 - p)
        sy = 1.0 - math.sin(p * math.pi * 2.0) * 0.008 * (1.0 - p)
    rotation = math.sin(t * math.pi * 2.0) * 0.7
    return y, sx, sy, rotation


def cute_values(index: int, count: int) -> tuple[int, float, float, float]:
    t = index / (count - 1)
    bounce = math.sin(t * math.pi * 4.0)
    y = round(-8 * max(0.0, bounce) + 3 * min(0.0, bounce))
    scale = 1.0 + 0.014 * max(0.0, bounce)
    rotation = math.sin(t * math.pi * 2.0) * 2.4
    return y, scale, scale, rotation


def backup_existing(folder: Path) -> None:
    if not folder.exists() or not any(folder.glob("*.png")):
        return
    backup = folder.parent / f"{folder.name}_before_synth"
    if backup.exists():
        return
    shutil.copytree(folder, backup)


def write_action(source: Image.Image, action: str, target_root: Path) -> None:
    count = SPECS[action]
    crop = source_crop(source)
    out_dir = target_root / action
    backup_existing(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for index in range(count):
        values = happy_values(index, count) if action == "happy" else cute_values(index, count)
        frame = transform_frame(crop, *values)
        frame.save(out_dir / f"{index:02d}.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--actions", required=True, help="Comma-separated actions: happy,cute")
    args = parser.parse_args()

    source = Image.open(args.source).convert("RGBA")
    actions = [item.strip() for item in args.actions.split(",") if item.strip()]
    for action in actions:
        if action not in SPECS:
            raise SystemExit(f"Unsupported synthetic action: {action}")
        write_action(source, action, args.target_root)
    print(f"synthetic_motion_actions_ok target={args.target_root} actions={','.join(actions)}")


if __name__ == "__main__":
    main()
