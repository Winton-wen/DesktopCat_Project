from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from audit_production_batch import action_specs_for_batch, audit_frames


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "assets" / "production" / "desktop_cat" / "batch_manifest.json"
SPRITES = ROOT / "assets" / "sprites"


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_batch(manifest: dict, batch_id: str) -> dict:
    for batch in manifest["batches"]:
        if batch["id"] == batch_id:
            return batch
    raise SystemExit(f"Unknown production batch: {batch_id}")


def resolve_source(source_text: str) -> Path:
    source = Path(source_text)
    if source.is_absolute():
        return source
    return ROOT / source


def promote(batch_id: str, manifest_path: Path, dry_run: bool) -> None:
    manifest = load_manifest(manifest_path)
    if batch_id == manifest["protected_baseline"]:
        raise SystemExit("Refusing to promote protected baseline batch.")

    batch = find_batch(manifest, batch_id)
    if batch.get("status") not in {"candidate", "accepted"}:
        raise SystemExit(f"Batch status must be candidate or accepted, got {batch.get('status')!r}.")

    source = resolve_source(batch["source"])
    canvas_size = tuple(manifest["frame_standard"]["canvas_size"])
    errors = audit_frames(source, action_specs_for_batch(manifest, batch), canvas_size)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    if dry_run:
        print(f"production_batch_promote_dry_run_ok batch={batch_id} source={source}")
        return

    for action in action_specs_for_batch(manifest, batch):
        target_dir = SPRITES / action
        target_dir.mkdir(parents=True, exist_ok=True)
        for old_frame in target_dir.glob("*.png"):
            old_frame.unlink()
        for frame in sorted((source / action).glob("*.png")):
            shutil.copy2(frame, target_dir / frame.name)
    print(f"production_batch_promote_apply_ok batch={batch_id} target={SPRITES}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.apply == args.dry_run:
        raise SystemExit("Choose exactly one: --dry-run or --apply.")
    promote(args.batch, args.manifest, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
