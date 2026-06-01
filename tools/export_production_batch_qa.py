from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = ROOT / "assets" / "production" / "desktop_cat"
MANIFEST = PRODUCTION / "batch_manifest.json"


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def find_batch(manifest: dict, batch_id: str) -> dict:
    for batch in manifest["batches"]:
        if batch["id"] == batch_id:
            return batch
    raise SystemExit(f"Unknown production batch: {batch_id}")


def load_action_frames(source: Path, action: str) -> list[Image.Image]:
    paths = sorted((source / action).glob("*.png"))
    return [Image.open(path).convert("RGBA") for path in paths]


def export_batch_qa(batch_id: str, action_subset: list[str] | None = None) -> Path:
    manifest = load_manifest()
    batch = find_batch(manifest, batch_id)
    source = ROOT / batch["source"]
    qa_dir = PRODUCTION / "qa" / batch_id
    qa_dir.mkdir(parents=True, exist_ok=True)

    actions = action_subset or list(manifest["actions"].keys())
    frames_by_action = {action: load_action_frames(source, action) for action in actions}
    thumb = 128
    label_h = 24
    columns = 8
    rows = sum((len(frames) + columns - 1) // columns for frames in frames_by_action.values())
    sheet = Image.new("RGB", (columns * thumb, rows * (thumb + label_h)), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    row = 0
    for action, frames in frames_by_action.items():
        for index, frame in enumerate(frames):
            col = index % columns
            if index and col == 0:
                row += 1
            x = col * thumb
            y = row * (thumb + label_h)
            preview = frame.resize((thumb, thumb), Image.Resampling.LANCZOS)
            sheet.paste(preview, (x, y + label_h), preview)
            draw.text((x + 4, y + 4), f"{action} {index:02d}", fill=(30, 30, 30))
        if frames:
            frames[0].save(
                qa_dir / f"{action}.gif",
                save_all=True,
                append_images=frames[1:],
                duration=round(1000 / int(manifest["actions"][action]["fps"])),
                loop=0,
                disposal=2,
            )
        row += 1

    sheet.save(qa_dir / "contact_sheet.png")
    return qa_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--actions", help="Optional comma-separated action subset.")
    args = parser.parse_args()
    actions = [item.strip() for item in args.actions.split(",") if item.strip()] if args.actions else None
    qa_dir = export_batch_qa(args.batch, actions)
    print(f"production_batch_qa_export_ok batch={args.batch} qa={qa_dir}")


if __name__ == "__main__":
    main()
