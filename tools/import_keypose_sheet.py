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


def alpha_components(image: Image.Image, min_pixels: int = 5000) -> list[tuple[int, tuple[int, int, int, int]]]:
    alpha = image.getchannel("A")
    width, height = image.size
    visited: set[tuple[int, int]] = set()
    components: list[tuple[int, tuple[int, int, int, int]]] = []

    for y in range(height):
        for x in range(width):
            point = (x, y)
            if point in visited or alpha.getpixel(point) <= ALPHA_THRESHOLD:
                continue
            stack = [point]
            visited.add(point)
            xs: list[int] = []
            ys: list[int] = []
            while stack:
                cx, cy = stack.pop()
                xs.append(cx)
                ys.append(cy)
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
            pixel_count = len(xs)
            if pixel_count >= min_pixels:
                components.append((pixel_count, (min(xs), min(ys), max(xs) + 1, max(ys) + 1)))
    return components


def clear_long_white_grid_lines(image: Image.Image) -> Image.Image:
    source = image.convert("RGBA")
    pixels = source.load()
    white_columns: set[int] = set()
    white_rows: set[int] = set()
    for x in range(source.width):
        white_count = 0
        for y in range(source.height):
            r, g, b, a = pixels[x, y]
            if a and r > 248 and g > 248 and b > 248:
                white_count += 1
        if white_count > source.height * 0.18:
            white_columns.add(x)
    for y in range(source.height):
        white_count = 0
        for x in range(source.width):
            r, g, b, a = pixels[x, y]
            if a and r > 248 and g > 248 and b > 248:
                white_count += 1
        if white_count > source.width * 0.18:
            white_rows.add(y)
    for x in white_columns:
        for nx in range(max(0, x - 1), min(source.width, x + 2)):
            for y in range(source.height):
                r, g, b, _a = pixels[nx, y]
                pixels[nx, y] = (r, g, b, 0)
    for y in white_rows:
        for ny in range(max(0, y - 1), min(source.height, y + 2)):
            for x in range(source.width):
                r, g, b, _a = pixels[x, ny]
                pixels[x, ny] = (r, g, b, 0)
    return source


def sort_components_by_rows(
    components: list[tuple[int, tuple[int, int, int, int]]],
    row_count: int,
) -> list[tuple[int, tuple[int, int, int, int]]]:
    if row_count <= 0:
        return sorted(components, key=lambda item: (item[1][1], item[1][0]))
    by_y = sorted(components, key=lambda item: ((item[1][1] + item[1][3]) / 2, item[1][0]))
    rows = [[] for _ in range(row_count)]
    for index, component in enumerate(by_y):
        row_index = min(row_count - 1, index * row_count // len(by_y))
        rows[row_index].append(component)
    ordered: list[tuple[int, tuple[int, int, int, int]]] = []
    for row in rows:
        ordered.extend(sorted(row, key=lambda item: item[1][0]))
    return ordered


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


def normalize_component(
    sheet: Image.Image,
    bbox: tuple[int, int, int, int],
    canvas_size: tuple[int, int],
    target_extent: int,
) -> Image.Image:
    crop = keep_largest_alpha_component(sheet.crop(bbox))
    clean_bbox = crop.getbbox()
    if clean_bbox is None:
        raise ValueError("empty keypose component")
    return normalize_pose(crop.crop(clean_bbox), canvas_size, target_extent)


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


def extract_keyposes_by_component(
    sheet_path: Path,
    out_dir: Path,
    rows: int,
    canvas_size: tuple[int, int],
    target_extent: int,
    limit: int | None,
) -> list[Path]:
    sheet = chroma_to_alpha(clear_long_white_grid_lines(Image.open(sheet_path)))
    components = sort_components_by_rows(alpha_components(sheet), rows)
    if limit is not None:
        components = components[:limit]
    if not components:
        raise ValueError(f"no keypose components found in {sheet_path}")
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for index, (_pixel_count, bbox) in enumerate(components):
        pose = normalize_component(sheet, bbox, canvas_size, target_extent)
        path = out_dir / f"{index:02d}.png"
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


def resample_sequence(keyposes: list[Path], frame_count: int, out_dir: Path, mirror: bool = False) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for frame_index in range(frame_count):
        phase = frame_index / max(1, frame_count - 1)
        key_index = round(phase * (len(keyposes) - 1))
        source = Image.open(keyposes[key_index]).convert("RGBA")
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
    parser.add_argument("--resample", action="store_true", help="Spread keyposes evenly across --frames instead of cycling.")
    parser.add_argument("--component-extract", action="store_true", help="Extract keyposes as alpha components from the full sheet.")
    parser.add_argument("--component-limit", type=int, help="Maximum component keyposes to keep.")
    args = parser.parse_args()

    keypose_dir = args.out_root / "keyposes"
    if args.component_extract:
        keyposes = extract_keyposes_by_component(
            args.sheet,
            keypose_dir,
            args.rows,
            args.canvas_size,
            args.target_extent,
            args.component_limit,
        )
    else:
        keyposes = split_keyposes(args.sheet, keypose_dir, args.columns, args.rows, args.canvas_size, args.target_extent)
    if args.action:
        frame_count = args.frames or len(keyposes)
        sequence_builder = resample_sequence if args.resample else copy_sequence
        sequence_builder(keyposes, frame_count, args.out_root / args.action)
        if args.mirror_action:
            sequence_builder(keyposes, frame_count, args.out_root / args.mirror_action, mirror=True)
    else:
        build_sequence(keyposes, list(range(0, 8)), 48, args.out_root / "happy")
        build_sequence(keyposes, [8, 9, 10, 11, 10, 9, 8], 44, args.out_root / "cute")
    report = {
        "sheet": str(args.sheet),
        "keypose_count": len(keyposes),
        "action": args.action,
        "frames": args.frames or len(keyposes),
        "mirror_action": args.mirror_action,
        "resample": args.resample,
        "component_extract": args.component_extract,
        "component_limit": args.component_limit,
        "target_extent": args.target_extent,
        "note": "Generated from real redrawn keyposes; still requires visual QA and may need hand or AI in-betweens.",
    }
    report_path = args.out_root / "keypose_import_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"keypose_sheet_import_ok keyposes={len(keyposes)} out={args.out_root}")


if __name__ == "__main__":
    main()
