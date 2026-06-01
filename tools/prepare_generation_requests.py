from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = ROOT / "assets" / "production" / "desktop_cat"
MANIFEST = PRODUCTION / "batch_manifest.json"
PROMPT_PACK = PRODUCTION / "prompt_pack.md"
CHARACTER_LOCK = PRODUCTION / "character_lock.md"


def section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    if not match:
        raise SystemExit(f"Missing section in prompt pack: {heading}")
    return match.group("body").strip()


def action_prompt(text: str, action: str) -> str:
    for line in text.splitlines():
        if line.startswith(f"`{action}`:"):
            return line.strip()
    raise SystemExit(f"Missing action prompt: {action}")


def prepare(batch_root: Path, actions: list[str]) -> Path:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    prompt_pack = PROMPT_PACK.read_text(encoding="utf-8")
    character_lock = CHARACTER_LOCK.read_text(encoding="utf-8").strip()
    identity = section(prompt_pack, "Character Identity")
    negative = section(prompt_pack, "Negative Prompt")

    out_dir = batch_root / "generation_requests"
    out_dir.mkdir(parents=True, exist_ok=True)
    for action in actions:
        if action not in manifest["actions"]:
            raise SystemExit(f"Unknown action: {action}")
        spec = manifest["actions"][action]
        text = "\n".join(
            [
                f"# Generation Request: {action}",
                "",
                "## Character Lock",
                "",
                character_lock,
                "",
                "## Character Identity",
                "",
                identity,
                "",
                "## Action Prompt",
                "",
                action_prompt(prompt_pack, action),
                "",
                "## Output Contract",
                "",
                f"- Frame Count: {spec['frames']}",
                f"- FPS Target: {spec['fps']}",
                "- Canvas: 512x512 RGBA transparent PNG",
                "- Full body visible unless the action intentionally curls or sleeps",
                "- Keep bow and bell visible and consistent",
                "- First and last frames must be idle-compatible for non-idle actions",
                "- No guide marks, background, text, watermark, or cutout damage",
                "",
                "## Negative Prompt",
                "",
                negative,
                "",
            ]
        )
        (out_dir / f"{action}.md").write_text(text, encoding="utf-8")
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-root", type=Path, required=True)
    parser.add_argument("--actions", required=True, help="Comma-separated action names.")
    args = parser.parse_args()

    actions = [item.strip() for item in args.actions.split(",") if item.strip()]
    out_dir = prepare(args.batch_root, actions)
    print(f"generation_requests_prepared path={out_dir}")


if __name__ == "__main__":
    main()
