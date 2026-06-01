from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "assets" / "sprites"
OUT = ROOT / "assets" / "qa" / "sprite_contact_sheet.png"
ACTIONS = ["idle", "blink", "clicked", "happy", "wave", "sleep_in", "sleep", "wake", "walk", "walk_left", "drag"]


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    cell_w, cell_h = 180, 210
    cols = 4
    rows = (len(ACTIONS) + cols - 1) // cols
    sheet = Image.new("RGBA", (cell_w * cols, cell_h * rows), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    for index, action in enumerate(ACTIONS):
        frames = sorted((SPRITES / action).glob("*.png"))
        x0 = (index % cols) * cell_w
        y0 = (index // cols) * cell_h
        draw.text((x0 + 12, y0 + 12), action, fill=(80, 50, 50))
        if not frames:
            draw.text((x0 + 12, y0 + 96), "missing", fill=(160, 80, 80))
            continue
        image = Image.open(frames[0]).convert("RGBA")
        image.thumbnail((150, 150), Image.Resampling.LANCZOS)
        x = x0 + (cell_w - image.width) // 2
        y = y0 + 44
        sheet.alpha_composite(image, (x, y))

    sheet.save(OUT)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
