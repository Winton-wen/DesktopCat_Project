from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_SOURCE = ROOT / "\u53c2\u8003\u56fe" / "1.png"
PREVIEW = ROOT / "assets" / "gift" / "desktopcat_icon_head_preview.png"
SIZE_PREVIEW = ROOT / "assets" / "gift" / "desktopcat_icon_size_preview.png"
ICON = ROOT / "assets" / "gift" / "desktopcat.ico"
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)

# Tight square around the complete seated cat while retaining a small white
# margin around the ears, paws, and tail.
REFERENCE_CROP_BOX = (55, 45, 1199, 1189)


def build_full_cat_icon(source_path: Path = REFERENCE_SOURCE) -> Image.Image:
    with Image.open(source_path) as source:
        reference = source.convert("RGB")
        crop = reference.crop(REFERENCE_CROP_BOX)
        resized = crop.resize((512, 512), Image.Resampling.LANCZOS)
    return resized.convert("RGBA")


def build_size_preview(icon: Image.Image) -> Image.Image:
    canvas = Image.new("RGB", (640, 340), (244, 246, 250))
    draw = ImageDraw.Draw(canvas)
    x_positions = (84, 224, 364, 504, 624)
    sizes = (16, 24, 32, 48, 64)

    for x, size in zip(x_positions, sizes):
        scaled = icon.resize((size, size), Image.Resampling.LANCZOS).convert("RGB")
        canvas.paste(scaled, (x - size // 2, 72 - size // 2))
        draw.text((x - 18, 190), f"{size}px", fill=(32, 35, 42))

    return canvas


def main() -> None:
    preview = build_full_cat_icon()
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    preview.save(PREVIEW)
    build_size_preview(preview).save(SIZE_PREVIEW)
    preview.save(ICON, format="ICO", sizes=[(size, size) for size in ICON_SIZES])
    print(f"reference={REFERENCE_SOURCE}")
    print(f"preview={PREVIEW}")
    print(f"size_preview={SIZE_PREVIEW}")
    print(f"icon={ICON}")


if __name__ == "__main__":
    main()
