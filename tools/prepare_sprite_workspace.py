from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "assets" / "sprites"
ACTION_REFS = ROOT / "assets" / "action_refs"
QA = ROOT / "assets" / "qa"

V1_ACTIONS = [
    "idle",
    "blink",
    "clicked",
    "happy",
    "wave",
    "sleep",
    "walk",
    "drag",
]


def touch_keep(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / ".gitkeep").write_text("", encoding="utf-8")


def main() -> int:
    for path in [SPRITES, ACTION_REFS, QA]:
        touch_keep(path)
    for action in V1_ACTIONS:
        touch_keep(SPRITES / action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
