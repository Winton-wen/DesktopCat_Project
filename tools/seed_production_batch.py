from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "assets" / "sprites"


def seed(batch_root: Path, actions: list[str], force: bool) -> dict:
    copied: dict[str, int] = {}
    for action in actions:
        source_dir = BASELINE / action
        target_dir = batch_root / "clean" / action
        if not source_dir.exists():
            raise SystemExit(f"Missing baseline action folder: {source_dir}")
        target_dir.mkdir(parents=True, exist_ok=True)
        existing = list(target_dir.glob("*.png"))
        if existing and not force:
            raise SystemExit(f"Refusing to overwrite existing frames in {target_dir}; pass --force to replace.")
        if force:
            for frame in existing:
                frame.unlink()
        count = 0
        for frame in sorted(source_dir.glob("*.png")):
            shutil.copy2(frame, target_dir / frame.name)
            count += 1
        copied[action] = count

    report = {
        "source": str(BASELINE),
        "target": str(batch_root / "clean"),
        "actions": copied,
        "purpose": "Seed candidate batch with protected stable baseline frames for comparison and controlled replacement.",
    }
    (batch_root / "seed_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-root", type=Path, required=True)
    parser.add_argument("--actions", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    actions = [item.strip() for item in args.actions.split(",") if item.strip()]
    report = seed(args.batch_root, actions, args.force)
    print(f"production_batch_seeded target={report['target']} actions={','.join(actions)}")


if __name__ == "__main__":
    main()
