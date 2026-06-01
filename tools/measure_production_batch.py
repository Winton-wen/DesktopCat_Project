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


def measure_frame(path: Path) -> dict:
    image = Image.open(path).convert("RGBA")
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return {
            "path": str(path),
            "bbox": None,
            "alpha_pixels": 0,
            "alpha_coverage": 0.0,
            "center": None,
            "edge_margin": 0,
        }
    left, top, right, bottom = bbox
    alpha_pixels = sum(1 for value in alpha.getdata() if value > 0)
    edge_margin = min(left, top, image.width - right, image.height - bottom)
    return {
        "path": str(path),
        "bbox": [left, top, right, bottom],
        "alpha_pixels": alpha_pixels,
        "alpha_coverage": round(alpha_pixels / (image.width * image.height), 6),
        "center": [round((left + right) / 2, 2), round((top + bottom) / 2, 2)],
        "edge_margin": edge_margin,
    }


def summarize_action(frames: list[dict]) -> dict:
    non_empty = [frame for frame in frames if frame["bbox"] is not None]
    if not non_empty:
        return {
            "frame_count": len(frames),
            "min_edge_margin": 0,
            "alpha_coverage_min": 0.0,
            "alpha_coverage_max": 0.0,
            "center_x_span": 0.0,
            "center_y_span": 0.0,
        }
    centers_x = [frame["center"][0] for frame in non_empty]
    centers_y = [frame["center"][1] for frame in non_empty]
    coverages = [frame["alpha_coverage"] for frame in non_empty]
    return {
        "frame_count": len(frames),
        "min_edge_margin": min(frame["edge_margin"] for frame in non_empty),
        "alpha_coverage_min": min(coverages),
        "alpha_coverage_max": max(coverages),
        "center_x_span": round(max(centers_x) - min(centers_x), 2),
        "center_y_span": round(max(centers_y) - min(centers_y), 2),
    }


def measure_batch(batch_id: str, actions: list[str]) -> dict:
    manifest = load_manifest()
    batch = find_batch(manifest, batch_id)
    source = ROOT / batch["source"]
    frames_by_action: dict[str, list[dict]] = {}
    summaries: dict[str, dict] = {}
    for action in actions:
        frame_metrics = [measure_frame(path) for path in sorted((source / action).glob("*.png"))]
        frames_by_action[action] = frame_metrics
        summaries[action] = summarize_action(frame_metrics)
    return {
        "batch": batch_id,
        "source": str(source),
        "actions": actions,
        "frame_count": sum(len(frames) for frames in frames_by_action.values()),
        "action_summaries": summaries,
        "frames": frames_by_action,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--actions", required=True, help="Comma-separated action subset.")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    actions = [item.strip() for item in args.actions.split(",") if item.strip()]
    report = measure_batch(args.batch, actions)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        "production_batch_measure_ok "
        f"batch={report['batch']} frames={report['frame_count']} report={args.report}"
    )


if __name__ == "__main__":
    main()
