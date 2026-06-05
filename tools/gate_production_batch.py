from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = ROOT / "assets" / "production" / "desktop_cat"
POSE_TRANSITION_ACTIONS = {"sleep_in", "wake"}
HIGH_EXCURSION_ACTIONS = {"happy", "return_home"}


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Missing required QA report: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def gate_batch(batch_id: str, actions: list[str], qa_dir: Path) -> dict:
    audit = load_json(qa_dir / "audit_report.json")
    metrics = load_json(qa_dir / "shape_metrics.json")
    compare = load_json(qa_dir / "compare_to_baseline.json")

    errors: list[str] = []
    if not audit.get("ok"):
        errors.extend(audit.get("errors", ["audit failed"]))
    if metrics.get("actions") != actions:
        errors.append(f"shape metrics action scope mismatch: {metrics.get('actions')} != {actions}")
    if compare.get("actions") != actions:
        errors.append(f"baseline compare action scope mismatch: {compare.get('actions')} != {actions}")
    missing_baseline_actions = [
        error.split(":", 1)[0]
        for error in compare.get("errors", [])
        if error.endswith(": baseline has no frames")
    ]
    compare_has_only_missing_baselines = (
        len(missing_baseline_actions) == len(compare.get("errors", []))
    )
    missing_baseline_frame_count = sum(
        metrics["action_summaries"].get(action, {}).get("frame_count", 0)
        for action in missing_baseline_actions
    )
    expected_compare_frame_count = metrics.get("frame_count", 0) - missing_baseline_frame_count
    if (
        compare.get("frame_count") != expected_compare_frame_count
        or not compare_has_only_missing_baselines
    ):
        errors.append("shape metrics and baseline compare frame counts differ")

    checks = {
        "min_edge_margin": 12,
        "transition_min_edge_margin": 0,
        "high_excursion_min_edge_margin": 8,
        "max_center_x_span": 24,
        "max_center_y_span": 24,
        "max_baseline_rms_for_seed": 0.0,
    }
    for action in actions:
        summary = metrics["action_summaries"].get(action)
        if not summary:
            errors.append(f"missing shape summary for {action}")
            continue
        if action in POSE_TRANSITION_ACTIONS:
            min_edge_margin = checks["transition_min_edge_margin"]
        elif action in HIGH_EXCURSION_ACTIONS:
            min_edge_margin = checks["high_excursion_min_edge_margin"]
        else:
            min_edge_margin = checks["min_edge_margin"]
        if summary["min_edge_margin"] < min_edge_margin:
            errors.append(f"{action}: edge margin {summary['min_edge_margin']} below {min_edge_margin}")
        if action not in POSE_TRANSITION_ACTIONS and action not in HIGH_EXCURSION_ACTIONS:
            if summary["center_x_span"] > checks["max_center_x_span"]:
                errors.append(f"{action}: center_x_span {summary['center_x_span']} above {checks['max_center_x_span']}")
            if summary["center_y_span"] > checks["max_center_y_span"]:
                errors.append(f"{action}: center_y_span {summary['center_y_span']} above {checks['max_center_y_span']}")

    if compare.get("average_rms", 0) < 0:
        errors.append("baseline compare average_rms is invalid")

    return {
        "batch": batch_id,
        "actions": actions,
        "ok": not errors,
        "checks": checks,
        "errors": errors,
        "qa_dir": str(qa_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--actions", required=True, help="Comma-separated action subset.")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    actions = [item.strip() for item in args.actions.split(",") if item.strip()]
    qa_dir = PRODUCTION / "qa" / args.batch
    report = gate_batch(args.batch, actions, qa_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["ok"]:
        for error in report["errors"]:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"production_batch_gate_ok batch={args.batch} actions={','.join(actions)}")


if __name__ == "__main__":
    main()
