from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "assets" / "sprites"
OUT = ROOT / "assets" / "qa" / "gifs"

FPS = {
    "idle": 10,
    "blink": 7,
    "clicked": 14,
    "happy": 14,
    "wave": 14,
    "sleep_in": 10,
    "sleep": 8,
    "wake": 10,
    "walk": 14,
    "walk_left": 14,
    "drag": 5,
}


def make_gif(action: str) -> None:
    frames = sorted((SPRITES / action).glob("*.png"))
    if not frames:
        return

    images: list[Image.Image] = []
    for frame in frames:
        image = Image.open(frame).convert("RGBA")
        bbox = image.getbbox()
        if bbox:
            image = image.crop(bbox)
        image.thumbnail((180, 180), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (220, 220), (255, 255, 255, 0))
        canvas.alpha_composite(image, ((220 - image.width) // 2, 196 - image.height))
        images.append(canvas)

    duration = round(1000 / FPS.get(action, 10))
    images[0].save(
        OUT / f"{action}.gif",
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,
        disposal=2,
        transparency=0,
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for action in FPS:
        make_gif(action)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
