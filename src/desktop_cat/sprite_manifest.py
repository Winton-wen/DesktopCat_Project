from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SpriteAction:
    name: str
    frame_count: int
    fps: int
    description: str


ACTIONS = [
    SpriteAction("idle", 16, 10, "stable front sitting with subtle breathing"),
    SpriteAction("blink", 10, 7, "calm front sitting blink"),
    SpriteAction("clicked", 9, 14, "surprised cute pop, ears perk"),
    SpriteAction("happy", 48, 24, "high-fps happy jump, hover, and settle"),
    SpriteAction("wave", 17, 14, "one front paw raised and waving"),
    SpriteAction("cute", 44, 24, "high-fps cute blink and tiny bounce"),
    SpriteAction("sleep_in", 96, 24, "settle down into sleep"),
    SpriteAction("sleep", 11, 8, "curled or lying down, eyes closed, breathing"),
    SpriteAction("wake", 96, 24, "wake up and return to sitting"),
    SpriteAction("walk", 16, 14, "short alternating steps, body sway, bell follows"),
    SpriteAction("walk_left", 16, 14, "mirrored short alternating steps for moving left"),
    SpriteAction("drag", 8, 5, "front paws lifted, soft hanging body, puzzled face"),
]


def action_dirs(root: Path) -> dict[str, Path]:
    return {action.name: root / action.name for action in ACTIONS}
