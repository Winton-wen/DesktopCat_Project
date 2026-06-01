from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = ROOT / "assets" / "production" / "desktop_cat"
MANIFEST = PRODUCTION / "batch_manifest.json"


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def find_batch(manifest: dict, batch_id: str) -> dict:
    for batch in manifest["batches"]:
        if batch["id"] == batch_id:
            return batch
    raise SystemExit(f"Unknown production batch: {batch_id}")


def audit_frames(source: Path, actions: dict, canvas_size: tuple[int, int]) -> list[str]:
    errors: list[str] = []
    for action, spec in actions.items():
        folder = source / action
        frames = sorted(folder.glob("*.png"))
        expected_count = int(spec["frames"])
        if len(frames) != expected_count:
            errors.append(f"{action}: expected {expected_count} png frames, found {len(frames)}")
            continue
        for frame_path in frames:
            image = Image.open(frame_path).convert("RGBA")
            if image.size != canvas_size:
                errors.append(f"{frame_path}: expected {canvas_size}, found {image.size}")
            for point in [(0, 0), (image.width - 1, 0), (0, image.height - 1), (image.width - 1, image.height - 1)]:
                if image.getpixel(point) != (0, 0, 0, 0):
                    errors.append(f"{frame_path}: corner {point} is not transparent")
                    break
            if image.getbbox() is None:
                errors.append(f"{frame_path}: image is empty")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--actions", help="Optional comma-separated action subset.")
    args = parser.parse_args()

    manifest = load_manifest()
    batch = find_batch(manifest, args.batch)
    source = ROOT / batch["source"]
    canvas_size = tuple(manifest["frame_standard"]["canvas_size"])
    action_specs = manifest["actions"]
    if args.actions:
        requested = [item.strip() for item in args.actions.split(",") if item.strip()]
        action_specs = {action: manifest["actions"][action] for action in requested}
    errors = audit_frames(source, action_specs, canvas_size)
    qa_path = ROOT / batch["qa_contact_sheet"]
    if not qa_path.exists():
        errors.append(f"Missing QA contact sheet: {qa_path}")

    report = {
        "batch": args.batch,
        "source": str(source),
        "ok": not errors,
        "errors": errors,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    print(f"production_batch_audit_ok batch={args.batch} source={source}")


if __name__ == "__main__":
    main()
