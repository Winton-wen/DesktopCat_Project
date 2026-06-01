from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "src"))

from desktop_cat.rig import RigAnimation, RigModel, RigRenderer


def export_frames(action: str, frames: int, out_dir: Path) -> list[Image.Image]:
    model = RigModel.load(ROOT / "assets" / "rig_parts" / "desktop_cat" / "rig.json")
    animation = RigAnimation(model)
    renderer = RigRenderer(model)
    out_dir.mkdir(parents=True, exist_ok=True)
    rendered = []
    for index in range(frames):
        phase = index / frames
        frame = renderer.render(animation.pose(action, phase))
        frame.save(out_dir / f"{index:02d}.png")
        rendered.append(frame)
    return rendered


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["idle", "blink", "wave", "clicked", "happy", "sleep", "drag"], required=True)
    parser.add_argument("--frames", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    export_frames(args.action, args.frames, args.output)


if __name__ == "__main__":
    main()
