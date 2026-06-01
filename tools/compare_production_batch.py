from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat


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


def frame_paths(source: Path, action: str) -> list[Path]:
    return sorted((source / action).glob("*.png"))


def rms_difference(candidate_path: Path, baseline_path: Path) -> float:
    candidate = Image.open(candidate_path).convert("RGBA")
    baseline = Image.open(baseline_path).convert("RGBA")
    if candidate.size != baseline.size:
        raise ValueError(f"Size mismatch: {candidate_path} {candidate.size} != {baseline_path} {baseline.size}")
    diff = ImageChops.difference(candidate, baseline)
    stat = ImageStat.Stat(diff)
    return math.sqrt(sum(value * value for value in stat.rms) / len(stat.rms))


def save_compare_sheet(rows: list[dict], sheet_path: Path) -> None:
    thumb = 120
    label_h = 22
    columns = 3
    sheet = Image.new("RGB", (columns * thumb, max(1, len(rows)) * (thumb + label_h)), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    for row_index, row in enumerate(rows):
        y = row_index * (thumb + label_h)
        candidate = Image.open(row["candidate_path"]).convert("RGBA").resize((thumb, thumb), Image.Resampling.LANCZOS)
        baseline = Image.open(row["baseline_path"]).convert("RGBA").resize((thumb, thumb), Image.Resampling.LANCZOS)
        diff = ImageChops.difference(candidate, baseline)
        diff = ImageChops.multiply(diff, Image.new("RGBA", diff.size, (6, 6, 6, 255)))
        for column, (label, image) in enumerate(
            [
                ("candidate", candidate),
                ("baseline", baseline),
                (f"diff {row['rms']:.2f}", diff),
            ]
        ):
            x = column * thumb
            draw.text((x + 4, y + 4), f"{row['action']} {row['index']:02d} {label}", fill=(25, 25, 25))
            sheet.paste(image, (x, y + label_h), image if image.mode == "RGBA" else None)
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(sheet_path)


def compare_batch(batch_id: str, actions: list[str], report_path: Path) -> dict:
    manifest = load_manifest()
    baseline_id = manifest["protected_baseline"]
    batch = find_batch(manifest, batch_id)
    baseline = find_batch(manifest, baseline_id)
    source = ROOT / batch["source"]
    baseline_source = ROOT / baseline["source"]

    rows: list[dict] = []
    errors: list[str] = []
    for action in actions:
        candidate_frames = frame_paths(source, action)
        baseline_frames = frame_paths(baseline_source, action)
        if len(candidate_frames) != len(baseline_frames):
            errors.append(f"{action}: candidate has {len(candidate_frames)} frames, baseline has {len(baseline_frames)}")
            continue
        for index, (candidate_path, baseline_path) in enumerate(zip(candidate_frames, baseline_frames)):
            try:
                rms = rms_difference(candidate_path, baseline_path)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            rows.append(
                {
                    "action": action,
                    "index": index,
                    "candidate_path": str(candidate_path),
                    "baseline_path": str(baseline_path),
                    "rms": round(rms, 4),
                }
            )

    rms_values = [row["rms"] for row in rows]
    sheet_path = report_path.with_name("compare_to_baseline.png")
    if rows:
        save_compare_sheet(rows, sheet_path)
    report = {
        "batch": batch_id,
        "baseline": baseline_id,
        "actions": actions,
        "frame_count": len(rows),
        "average_rms": round(sum(rms_values) / len(rms_values), 4) if rms_values else 0.0,
        "max_rms": max(rms_values) if rms_values else 0.0,
        "compare_sheet": str(sheet_path),
        "errors": errors,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--actions", required=True, help="Comma-separated action subset.")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    actions = [item.strip() for item in args.actions.split(",") if item.strip()]
    report = compare_batch(args.batch, actions, args.report)
    if report["errors"]:
        for error in report["errors"]:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(
        "production_batch_compare_ok "
        f"batch={report['batch']} baseline={report['baseline']} "
        f"frames={report['frame_count']} average_rms={report['average_rms']}"
    )


if __name__ == "__main__":
    main()
