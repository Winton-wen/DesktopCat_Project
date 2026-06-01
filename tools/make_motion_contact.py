from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "assets" / "sprites"
OUT = ROOT / "assets" / "qa" / "motion_contact_sheet.png"
ACTIONS = ["idle", "blink", "clicked", "happy", "wave", "sleep_in", "sleep", "wake", "walk", "walk_left", "drag"]


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    thumb = 128
    label_h = 28
    gap = 14

    rows: list[tuple[str, list[Path]]] = []
    max_count = 0
    for action in ACTIONS:
        frames = sorted((SPRITES / action).glob("*.png"))
        rows.append((action, frames))
        max_count = max(max_count, len(frames))

    width = gap + max_count * (thumb + gap)
    height = len(rows) * (thumb + label_h + gap) + gap
    sheet = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    for row_index, (action, frames) in enumerate(rows):
        y0 = gap + row_index * (thumb + label_h + gap)
        draw.text((gap, y0), action, fill=(70, 45, 45))
        for index, frame_path in enumerate(frames):
            image = Image.open(frame_path).convert("RGBA")
            image.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)
            x = gap + index * (thumb + gap) + (thumb - image.width) // 2
            y = y0 + label_h + (thumb - image.height) // 2
            sheet.alpha_composite(image, (x, y))

    sheet.save(OUT)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
