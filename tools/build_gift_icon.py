from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "assets"
    / "production"
    / "desktop_cat"
    / "batches"
    / "20260527_motion_quality_v1"
    / "clean"
    / "idle"
    / "00.png"
)
PREVIEW = ROOT / "assets" / "gift" / "desktopcat_icon_head_preview.png"
ICON = ROOT / "assets" / "gift" / "desktopcat.ico"
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)

# Canonical 512 px frame: head, bow, bell, and a small amount of chest.
CROP_BOX = (122, 166, 378, 422)


def retain_center_component(alpha: Image.Image, seed: tuple[int, int]) -> Image.Image:
    width, height = alpha.size
    pixels = alpha.load()
    kept = Image.new("L", alpha.size, 0)
    kept_pixels = kept.load()
    queue = deque([seed])
    visited = {seed}

    while queue:
        x, y = queue.popleft()
        if pixels[x, y] == 0:
            continue
        kept_pixels[x, y] = pixels[x, y]
        for next_x, next_y in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            point = (next_x, next_y)
            if (
                0 <= next_x < width
                and 0 <= next_y < height
                and point not in visited
            ):
                visited.add(point)
                queue.append(point)
    return kept


def build_head_icon(source_path: Path = SOURCE) -> Image.Image:
    with Image.open(source_path) as source:
        crop = source.convert("RGBA").crop(CROP_BOX)

    # The production pose has a raised tail behind the right side of the head.
    # Remove that disconnected silhouette while retaining the right ear and bow.
    mask = crop.getchannel("A")
    draw = ImageDraw.Draw(mask)
    draw.polygon(
        [
            (204, 118),
            (256, 118),
            (256, 256),
            (188, 256),
            (198, 210),
            (198, 146),
        ],
        fill=0,
    )
    draw.polygon(
        [
            (0, 218),
            (82, 218),
            (102, 238),
            (154, 238),
            (174, 218),
            (256, 218),
            (256, 256),
            (0, 256),
        ],
        fill=0,
    )
    mask = retain_center_component(mask, (128, 100))
    crop.putalpha(mask)

    content_box = crop.getchannel("A").getbbox()
    if content_box is None:
        raise ValueError(f"No visible cat pixels found in {source_path}")
    content = crop.crop(content_box)
    content.thumbnail((464, 464), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    x = (canvas.width - content.width) // 2
    y = (canvas.height - content.height) // 2
    canvas.alpha_composite(content, (x, y))
    return canvas


def main() -> None:
    preview = build_head_icon()
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    preview.save(PREVIEW)
    preview.save(ICON, format="ICO", sizes=[(size, size) for size in ICON_SIZES])
    print(f"preview={PREVIEW}")
    print(f"icon={ICON}")


if __name__ == "__main__":
    main()
