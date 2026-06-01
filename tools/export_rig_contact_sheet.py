from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "assets" / "qa" / "rig"


def load_frames(action: str) -> list[Image.Image]:
    frames_dir = QA / action
    return [Image.open(path).convert("RGBA") for path in sorted(frames_dir.glob("*.png"))]


def make_sheet() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    actions = ["idle", "blink", "wave", "clicked", "happy", "sleep", "drag"]
    thumb = 128
    label_h = 24
    columns = 8
    rows = sum((len(load_frames(action)) + columns - 1) // columns for action in actions)
    sheet = Image.new("RGBA", (columns * thumb, rows * (thumb + label_h)), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    row = 0
    for action in actions:
        frames = load_frames(action)
        for index, frame in enumerate(frames):
            col = index % columns
            if index and col == 0:
                row += 1
            x = col * thumb
            y = row * (thumb + label_h)
            preview = frame.resize((thumb, thumb), Image.Resampling.LANCZOS)
            sheet.alpha_composite(preview, (x, y + label_h))
            draw.text((x + 4, y + 4), f"{action} {index:02d}", fill=(30, 30, 30, 255))
        row += 1
    sheet = sheet.convert("RGB")
    sheet.save(QA / "rig_all_actions_contact_sheet.png")
    sheet.save(QA / "rig_idle_blink_wave_contact_sheet.png")
    sheet.save(QA / "rig_idle_blink_contact_sheet.png")

    for action in actions:
        frames = load_frames(action)
        frames[0].save(
            QA / f"{action}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
            disposal=2,
        )


if __name__ == "__main__":
    make_sheet()
