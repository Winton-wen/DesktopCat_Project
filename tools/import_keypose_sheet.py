from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


ALPHA_THRESHOLD = 16


def parse_canvas_size(value: str) -> tuple[int, int]:
    if "x" not in value.lower():
        raise argparse.ArgumentTypeError("Canvas size must use WIDTHxHEIGHT")
    width, height = value.lower().split("x", 1)
    return int(width), int(height)


def chroma_to_alpha(image: Image.Image, key: tuple[int, int, int] = (0, 255, 0)) -> Image.Image:
    source = image.convert("RGBA")
    pixels = source.load()
    for y in range(source.height):
        for x in range(source.width):
            r, g, b, a = pixels[x, y]
            green_bias = g - max(r, b)
            dist = abs(r - key[0]) + abs(g - key[1]) + abs(b - key[2])
            if green_bias > 45 and dist < 230:
                alpha = 0
            elif green_bias > 25 and g > 120:
                alpha = max(0, min(a, int((45 - green_bias) * 6)))
            else:
                alpha = a
            pixels[x, y] = (r, g, b, alpha)
    return source


def keep_largest_alpha_component(image: Image.Image) -> Image.Image:
    source = image.convert("RGBA")
    alpha = source.getchannel("A")
    width, height = source.size
    visited: set[tuple[int, int]] = set()
    largest: set[tuple[int, int]] = set()

    for y in range(height):
        for x in range(width):
            point = (x, y)
            if point in visited or alpha.getpixel(point) <= ALPHA_THRESHOLD:
                continue
            stack = [point]
            component: set[tuple[int, int]] = set()
            visited.add(point)
            while stack:
                cx, cy = stack.pop()
                component.add((cx, cy))
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    neighbor = (nx, ny)
                    if (
                        nx < 0
                        or ny < 0
                        or nx >= width
                        or ny >= height
                        or neighbor in visited
                        or alpha.getpixel(neighbor) <= ALPHA_THRESHOLD
                    ):
                        continue
                    visited.add(neighbor)
                    stack.append(neighbor)
            if len(component) > len(largest):
                largest = component

    if not largest:
        return source
    pixels = source.load()
    for y in range(height):
        for x in range(width):
            if (x, y) not in largest:
                r, g, b, _ = pixels[x, y]
                pixels[x, y] = (r, g, b, 0)
    return source


def normalize_pose(cell: Image.Image, canvas_size: tuple[int, int], target_extent: int = 300) -> Image.Image:
    transparent = keep_largest_alpha_component(chroma_to_alpha(cell))
    bbox = transparent.getbbox()
    if bbox is None:
        raise ValueError("empty keypose cell")
    crop = transparent.crop(bbox)
    scale = target_extent / max(crop.width, crop.height)
    resized = crop.resize(
        (max(1, round(crop.width * scale)), max(1, round(crop.height * scale))),
        Image.Resampling.LANCZOS,
    )
    frame = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    x = (canvas_size[0] - resized.width) // 2
    y = canvas_size[1] - resized.height - 24
    frame.alpha_composite(resized, (x, y))
    return frame


def split_keyposes(
    sheet_path: Path,
    out_dir: Path,
    columns: int,
    rows: int,
    canvas_size: tuple[int, int],
    target_extent: int,
) -> list[Path]:
    sheet = Image.open(sheet_path).convert("RGBA")
    cell_w = sheet.width / columns
    cell_h = sheet.height / rows
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for row in range(rows):
        for col in range(columns):
            left = round(col * cell_w)
            top = round(row * cell_h)
            right = round((col + 1) * cell_w)
            bottom = round((row + 1) * cell_h)
            pose = normalize_pose(sheet.crop((left, top, right, bottom)), canvas_size, target_extent)
            path = out_dir / f"{row * columns + col:02d}.png"
            pose.save(path)
            written.append(path)
    return written


def build_sequence(keyposes: list[Path], key_indices: list[int], frame_count: int, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    keys = [Image.open(keyposes[index]).convert("RGBA") for index in key_indices]
    for frame_index in range(frame_count):
        phase = frame_index / max(1, frame_count - 1)
        key_float = phase * (len(keys) - 1)
        image = keys[round(key_float)]
        image.save(out_dir / f"{frame_index:02d}.png")


def copy_sequence(keyposes: list[Path], frame_count: int, out_dir: Path, mirror: bool = False) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for frame_index in range(frame_count):
        source = Image.open(keyposes[frame_index % len(keyposes)]).convert("RGBA")
        if mirror:
            source = source.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        source.save(out_dir / f"{frame_index:02d}.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--rows", type=int, default=3)
    parser.add_argument("--canvas-size", type=parse_canvas_size, default=(512, 512))
    parser.add_argument("--target-extent", type=int, default=300)
    parser.add_argument("--action", help="Optional action name to export directly from the sheet.")
    parser.add_argument("--frames", type=int, help="Frame count for --action export. Defaults to all keyposes.")
    parser.add_argument("--mirror-action", help="Optional second action exported as horizontally mirrored frames.")
    args = parser.parse_args()

    keypose_dir = args.out_root / "keyposes"
    keyposes = split_keyposes(args.sheet, keypose_dir, args.columns, args.rows, args.canvas_size, args.target_extent)
    if args.action:
        frame_count = args.frames or len(keyposes)
        copy_sequence(keyposes, frame_count, args.out_root / args.action)
        if args.mirror_action:
            copy_sequence(keyposes, frame_count, args.out_root / args.mirror_action, mirror=True)
    else:
        build_sequence(keyposes, list(range(0, 8)), 48, args.out_root / "happy")
        build_sequence(keyposes, [8, 9, 10, 11, 10, 9, 8], 44, args.out_root / "cute")
    report = {
        "sheet": str(args.sheet),
        "keypose_count": len(keyposes),
        "action": args.action,
        "frames": args.frames or len(keyposes),
        "mirror_action": args.mirror_action,
        "target_extent": args.target_extent,
        "note": "Generated from real redrawn keyposes; still requires visual QA and may need hand or AI in-betweens.",
    }
    report_path = args.out_root / "keypose_import_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"keypose_sheet_import_ok keyposes={len(keyposes)} out={args.out_root}")


if __name__ == "__main__":
    main()
