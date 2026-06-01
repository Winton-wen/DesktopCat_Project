from __future__ import annotations

from pathlib import Path
from statistics import median

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "assets" / "sprites"
FRAME_SIZE = (512, 512)


def bbox_size(path: Path) -> tuple[int, int]:
    image = Image.open(path).convert("RGBA")
    bbox = image.getbbox()
    if not bbox:
        return 0, 0
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def median_bbox(action: str) -> tuple[int, int]:
    sizes = [bbox_size(path) for path in sorted((SPRITES / action).glob("*.png"))]
    widths = [w for w, h in sizes if w and h]
    heights = [h for w, h in sizes if w and h]
    return round(median(widths)), round(median(heights))


def normalize_action_to_idle(action: str) -> None:
    target_w, target_h = median_bbox("idle")
    for path in sorted((SPRITES / action).glob("*.png")):
        image = Image.open(path).convert("RGBA")
        bbox = image.getbbox()
        if not bbox:
            continue
        crop = image.crop(bbox)
        crop = crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
        frame = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
        x = (FRAME_SIZE[0] - target_w) // 2
        y = FRAME_SIZE[1] - target_h - 18
        frame.alpha_composite(crop, (x, y))
        frame.save(path)


def rewrite_frames(action: str, frames: list[Image.Image]) -> None:
    out = SPRITES / action
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()
    for index, frame in enumerate(frames):
        frame.save(out / f"{index:02d}.png")


def rebuild_idle_from_stable_pose() -> None:
    source = Image.open(SPRITES / "blink" / "00.png").convert("RGBA")
    bbox = source.getbbox()
    if not bbox:
        return

    crop = source.crop(bbox)
    offsets = [0, 0, -1, -1, -2, -2, -1, -1, 0, 0, 1, 1, 0, 0, -1, 0]
    frames: list[Image.Image] = []
    for index, dy in enumerate(offsets):
        frame = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
        x = (FRAME_SIZE[0] - crop.width) // 2
        y = FRAME_SIZE[1] - crop.height - 18 + dy
        frame.alpha_composite(crop, (x, y))
        frames.append(frame)
    rewrite_frames("idle", frames)


def rebuild_happy_from_source() -> None:
    out = SPRITES / "happy"
    frames = [Image.open(path).convert("RGBA") for path in sorted(out.glob("*.png"))]
    if len(frames) < 7:
        return

    sequence = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1, 0, 0, 0]
    rewrite_frames("happy", [frames[index].copy() for index in sequence])


def transformed_pose(source: Image.Image, scale_x: float, scale_y: float, dy: int) -> Image.Image:
    bbox = source.getbbox()
    if not bbox:
        return source.copy()
    crop = source.crop(bbox)
    new_size = (max(1, round(crop.width * scale_x)), max(1, round(crop.height * scale_y)))
    crop = crop.resize(new_size, Image.Resampling.LANCZOS)
    frame = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
    x = (FRAME_SIZE[0] - crop.width) // 2
    y = FRAME_SIZE[1] - crop.height - 18 + dy
    frame.alpha_composite(crop, (x, y))
    return frame


def rebuild_sleep_transitions() -> None:
    idle = Image.open(SPRITES / "idle" / "00.png").convert("RGBA")
    sleep_frames = [Image.open(path).convert("RGBA") for path in sorted((SPRITES / "sleep").glob("*.png"))]
    if not sleep_frames:
        return

    sleep_start = sleep_frames[0]
    sleep_in = [
        idle,
        transformed_pose(idle, 1.0, 0.98, 3),
        transformed_pose(idle, 1.02, 0.95, 7),
        transformed_pose(idle, 1.04, 0.92, 12),
        transformed_pose(idle, 1.06, 0.88, 18),
        sleep_start,
    ]
    sleep_in.extend(frame.copy() for frame in sleep_frames[:5])
    rewrite_frames("sleep_in", sleep_in)
    rewrite_frames("wake", [frame.copy() for frame in reversed(sleep_in)])


def rebuild_drag_from_stable_pose() -> None:
    source = Image.open(SPRITES / "drag" / "00.png").convert("RGBA")
    bbox = source.getbbox()
    if not bbox:
        return

    crop = source.crop(bbox)
    offsets = [0, 2, 3, 2, 0, -1, 0, 1]
    frames: list[Image.Image] = []
    for index, dy in enumerate(offsets):
        frame = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
        x = (FRAME_SIZE[0] - crop.width) // 2
        y = FRAME_SIZE[1] - crop.height - 18 + dy
        frame.alpha_composite(crop, (x, y))
        frames.append(frame)
    rewrite_frames("drag", frames)


def remove_walk_outliers() -> None:
    out = SPRITES / "walk"
    frames = sorted(out.glob("*.png"))
    if not frames:
        return

    sizes = [(path, bbox_size(path)) for path in frames]
    median_w = median([width for _path, (width, height) in sizes if width and height])
    median_h = median([height for _path, (width, height) in sizes if width and height])
    kept = [
        path
        for path, (width, height) in sizes
        if width <= median_w * 1.25 and height >= median_h - 8
    ]
    if len(kept) < 8:
        return

    images = [Image.open(path).convert("RGBA") for path in kept]
    rewrite_frames("walk", images)


def rebuild_walk_left_from_walk() -> None:
    source = SPRITES / "walk"
    out = SPRITES / "walk_left"
    out.mkdir(parents=True, exist_ok=True)

    for old in out.glob("*.png"):
        old.unlink()

    for path in sorted(source.glob("*.png")):
        image = Image.open(path).convert("RGBA")
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        image.save(out / path.name)


def main() -> int:
    for action in ["blink", "clicked", "happy", "wave"]:
        normalize_action_to_idle(action)
    rebuild_idle_from_stable_pose()
    rebuild_happy_from_source()
    rebuild_sleep_transitions()
    rebuild_drag_from_stable_pose()
    remove_walk_outliers()
    rebuild_walk_left_from_walk()
    print("stabilized idle, happy, sleep transitions, one-shot actions, drag, walk, and walk_left")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
