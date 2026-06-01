from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "concept" / "desktopcat_action_sheet_v1.png"
OUT = ROOT / "assets" / "action_refs"

ACTIONS = [
    "idle",
    "blink",
    "clicked",
    "happy",
    "wave",
    "sleep",
    "walk",
    "drag",
]


def main() -> int:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)

    OUT.mkdir(parents=True, exist_ok=True)
    image = Image.open(SOURCE).convert("RGBA")
    cell_w = image.width // 4
    cell_h = image.height // 2

    for index, action in enumerate(ACTIONS):
        col = index % 4
        row = index // 4
        box = (col * cell_w, row * cell_h, (col + 1) * cell_w, (row + 1) * cell_h)
        crop = image.crop(box)
        crop.save(OUT / f"{action}.png")

    print(f"Extracted {len(ACTIONS)} action references to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
