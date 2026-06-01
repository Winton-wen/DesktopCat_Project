from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "assets" / "sprites"
QA = ROOT / "assets" / "qa" / "stable"


def make_sheet() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    actions = ["idle", "blink", "wave", "clicked", "happy", "sleep", "drag"]
    thumb = 128
    label_h = 24
    columns = 8
    all_frames = {action: sorted((SPRITES / action).glob("*.png")) for action in actions}
    rows = sum((len(paths) + columns - 1) // columns for paths in all_frames.values())
    sheet = Image.new("RGB", (columns * thumb, rows * (thumb + label_h)), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    row = 0
    for action, paths in all_frames.items():
        frames = [Image.open(path).convert("RGBA") for path in paths]
        for index, frame in enumerate(frames):
            col = index % columns
            if index and col == 0:
                row += 1
            x = col * thumb
            y = row * (thumb + label_h)
            preview = frame.resize((thumb, thumb), Image.Resampling.LANCZOS)
            sheet.paste(Image.new("RGB", preview.size, (255, 255, 255)), (x, y + label_h))
            sheet.paste(preview, (x, y + label_h), preview)
            draw.text((x + 4, y + 4), f"{action} {index:02d}", fill=(30, 30, 30))
        if frames:
            frames[0].save(
                QA / f"{action}.gif",
                save_all=True,
                append_images=frames[1:],
                duration=100,
                loop=0,
                disposal=2,
            )
        row += 1
    sheet.save(QA / "stable_sprite_contact_sheet.png")


if __name__ == "__main__":
    make_sheet()
