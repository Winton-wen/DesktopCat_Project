from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
STRIPS = ROOT / "assets" / "generated_strips"
STRIPS_V2 = ROOT / "assets" / "generated_strips_v2"
SPRITES = ROOT / "assets" / "sprites"
FRAME_SIZE = 512
TARGET_HEIGHT = 430
TARGET_WIDTH = 430
EDGE_CONTRACT_PX = 1
ALPHA_THRESHOLD = 36
CELL_OVERLAP = 42

ACTIONS = {
    "idle": (STRIPS_V2, "idle_strip_source.png", 16),
    "blink": (STRIPS_V2, "blink_strip_source.png", 10),
    "clicked": (STRIPS_V2, "clicked_strip_source.png", 9),
    "happy": (STRIPS_V2, "happy_strip_source.png", 12),
    "wave": (STRIPS_V2, "wave_strip_source.png", 17),
    "sleep": (STRIPS_V2, "sleep_strip_source.png", 11),
    "walk": (STRIPS_V2, "walk_strip_source.png", 15),
    "drag": ("drag_strip_source.png", 4),
}


def remove_green(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    pixels = image.load()
    width, height = image.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            green_dominates = g > 105 and g > r * 1.22 and g > b * 1.22
            vivid_green = g > 145 and r < 120 and b < 120
            if green_dominates or vivid_green:
                pixels[x, y] = (r, g, b, 0)
            elif g > r * 1.08 and g > b * 1.08 and g > 90:
                # Suppress green spill near antialiased fur edges without erasing the pixel.
                pixels[x, y] = (r, min(g, max(r, b) + 8), b, a)

    return image


def keep_largest_alpha_component(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    alpha = image.getchannel("A")
    width, height = image.size
    alpha_pixels = alpha.load()
    visited = bytearray(width * height)
    components: list[list[tuple[int, int]]] = []

    for y in range(height):
        for x in range(width):
            offset = y * width + x
            if visited[offset] or alpha_pixels[x, y] < 16:
                continue

            stack = [(x, y)]
            visited[offset] = 1
            component: list[tuple[int, int]] = []

            while stack:
                cx, cy = stack.pop()
                component.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if nx < 0 or ny < 0 or nx >= width or ny >= height:
                        continue
                    noffset = ny * width + nx
                    if visited[noffset] or alpha_pixels[nx, ny] < 16:
                        continue
                    visited[noffset] = 1
                    stack.append((nx, ny))

            components.append(component)

    if not components:
        return image

    largest = max(components, key=len)
    pixels = image.load()
    for component in components:
        if component is largest:
            continue
        for x, y in component:
            r, g, b, _ = pixels[x, y]
            pixels[x, y] = (r, g, b, 0)

    return image


def alpha_components(image: Image.Image) -> list[tuple[int, int, int, int, int]]:
    alpha = image.convert("RGBA").getchannel("A")
    width, height = alpha.size
    alpha_pixels = alpha.load()
    visited = bytearray(width * height)
    components: list[tuple[int, int, int, int, int]] = []

    for y in range(height):
        for x in range(width):
            offset = y * width + x
            if visited[offset] or alpha_pixels[x, y] < 16:
                continue

            stack = [(x, y)]
            visited[offset] = 1
            min_x = max_x = x
            min_y = max_y = y
            area = 0

            while stack:
                cx, cy = stack.pop()
                area += 1
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)

                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if nx < 0 or ny < 0 or nx >= width or ny >= height:
                        continue
                    noffset = ny * width + nx
                    if visited[noffset] or alpha_pixels[nx, ny] < 16:
                        continue
                    visited[noffset] = 1
                    stack.append((nx, ny))

            components.append((min_x, min_y, max_x + 1, max_y + 1, area))

    return components


def v2_cells_from_components(source: Image.Image, count: int) -> list[Image.Image]:
    keyed = remove_green(source)
    source_area = source.width * source.height
    components = [
        bbox
        for bbox in alpha_components(keyed)
        if bbox[4] > source_area * 0.002 and (bbox[2] - bbox[0]) > 24 and (bbox[3] - bbox[1]) > 24
    ]
    if len(components) < count:
        return []

    selected = sorted(components, key=lambda bbox: (bbox[0] + bbox[2]) / 2)[:count]
    cells = []
    margin = 12
    for left, top, right, bottom, _area in selected:
        cells.append(keyed.crop((max(0, left - margin), max(0, top - margin), min(source.width, right + margin), min(source.height, bottom + margin))))
    return cells


def fit_cell_to_frame(cell: Image.Image) -> Image.Image:
    cell = keep_largest_alpha_component(remove_green(cell))
    alpha = cell.getchannel("A")
    for _ in range(EDGE_CONTRACT_PX):
        alpha = alpha.filter(ImageFilter.MinFilter(3))
    alpha = alpha.point(lambda value: 255 if value >= ALPHA_THRESHOLD else 0)
    cell.putalpha(alpha)
    bbox = cell.getbbox()
    if bbox:
        cell = cell.crop(bbox)

    scale = min(TARGET_WIDTH / cell.width, TARGET_HEIGHT / cell.height)
    cell = cell.resize((max(1, round(cell.width * scale)), max(1, round(cell.height * scale))), Image.Resampling.LANCZOS)
    frame = Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), (0, 0, 0, 0))
    x = (FRAME_SIZE - cell.width) // 2
    y = FRAME_SIZE - cell.height - 18
    frame.alpha_composite(cell, (x, y))
    return frame


def source_info(value: tuple) -> tuple[Path, str, int]:
    if len(value) == 2:
        filename, count = value
        return STRIPS, filename, count
    source_dir, filename, count = value
    return source_dir, filename, count


def split_strip(action: str, info: tuple) -> None:
    source_dir, filename, count = source_info(info)
    source = Image.open(source_dir / filename).convert("RGBA")
    overlap = 0 if source_dir == STRIPS_V2 else CELL_OVERLAP
    cells = v2_cells_from_components(source, count) if source_dir == STRIPS_V2 else []
    out_dir = SPRITES / action
    out_dir.mkdir(parents=True, exist_ok=True)

    for old in out_dir.glob("*.png"):
        old.unlink()

    for index in range(count):
        if cells:
            cell = cells[index]
        else:
            left = round(index * source.width / count)
            right = round((index + 1) * source.width / count)
            cell = source.crop((max(0, left - overlap), 0, min(source.width, right + overlap), source.height))
        frame = fit_cell_to_frame(cell)
        frame.save(out_dir / f"{index:02d}.png")


def main() -> int:
    missing = [name for name, info in ACTIONS.items() if not (source_info(info)[0] / source_info(info)[1]).exists()]
    if missing:
        raise FileNotFoundError(f"Missing generated strips for: {', '.join(missing)}")

    for action, info in ACTIONS.items():
        _source_dir, _filename, count = source_info(info)
        split_strip(action, info)
        print(f"{action}: {count} frames")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
