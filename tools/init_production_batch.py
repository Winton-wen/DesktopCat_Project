from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "assets" / "production" / "desktop_cat" / "batches"
TEMPLATE = DEFAULT_OUTPUT / "next_candidate_template"
ACTIONS = ["idle", "blink", "wave", "clicked", "happy", "sleep", "drag"]


def init_batch(batch_id: str, output_root: Path) -> Path:
    if not batch_id or any(char in batch_id for char in "\\/:*?\"<>| "):
        raise SystemExit("Batch id must be a non-empty filesystem-safe name without spaces.")

    target = output_root / batch_id
    if target.exists():
        raise SystemExit(f"Batch already exists: {target}")

    target.mkdir(parents=True)
    raw = target / "raw"
    clean = target / "clean"
    qa = target / "qa"
    raw.mkdir()
    clean.mkdir()
    qa.mkdir()
    for action in ACTIONS:
        (clean / action).mkdir()

    for filename in ["README.md", "notes.md"]:
        source = TEMPLATE / filename
        if source.exists():
            text = source.read_text(encoding="utf-8").replace("next_candidate_template", batch_id)
        else:
            text = f"# {batch_id}\n"
        (target / filename).write_text(text, encoding="utf-8")

    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    target = init_batch(args.batch_id, args.output_root)
    print(f"production_batch_initialized path={target}")


if __name__ == "__main__":
    main()
