from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_production_batch import action_specs_for_batch, audit_frames, find_batch, load_manifest
from compare_production_batch import compare_batch
from export_production_batch_qa import export_batch_qa
from gate_production_batch import gate_batch
from measure_production_batch import measure_batch


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = ROOT / "assets" / "production" / "desktop_cat"


def run_full_qa(batch_id: str, actions: list[str]) -> dict:
    manifest = load_manifest()
    batch = find_batch(manifest, batch_id)
    source = ROOT / batch["source"]
    qa_dir = PRODUCTION / "qa" / batch_id
    qa_dir.mkdir(parents=True, exist_ok=True)

    export_batch_qa(batch_id, actions)

    action_specs = action_specs_for_batch(manifest, batch, actions)
    canvas_size = tuple(manifest["frame_standard"]["canvas_size"])
    audit_errors = audit_frames(source, action_specs, canvas_size)
    audit_report = {
        "batch": batch_id,
        "source": str(source),
        "ok": not audit_errors,
        "errors": audit_errors,
    }
    (qa_dir / "audit_report.json").write_text(json.dumps(audit_report, indent=2), encoding="utf-8")

    metrics_report = measure_batch(batch_id, actions)
    (qa_dir / "shape_metrics.json").write_text(json.dumps(metrics_report, indent=2), encoding="utf-8")

    compare_report = compare_batch(batch_id, actions, qa_dir / "compare_to_baseline.json")
    gate_report = gate_batch(batch_id, actions, qa_dir)
    (qa_dir / "gate_report.json").write_text(json.dumps(gate_report, indent=2), encoding="utf-8")

    report = {
        "batch": batch_id,
        "actions": actions,
        "ok": audit_report["ok"] and not compare_report["errors"] and gate_report["ok"],
        "qa_dir": str(qa_dir),
        "reports": {
            "contact_sheet": str(qa_dir / "contact_sheet.png"),
            "audit": str(qa_dir / "audit_report.json"),
            "shape_metrics": str(qa_dir / "shape_metrics.json"),
            "compare": str(qa_dir / "compare_to_baseline.json"),
            "gate": str(qa_dir / "gate_report.json"),
        },
    }
    (qa_dir / "full_qa_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--actions", required=True, help="Comma-separated action subset.")
    args = parser.parse_args()

    actions = [item.strip() for item in args.actions.split(",") if item.strip()]
    report = run_full_qa(args.batch, actions)
    if not report["ok"]:
        print(f"production_batch_full_qa_failed batch={args.batch} report={report['qa_dir']}")
        raise SystemExit(1)
    print(f"production_batch_full_qa_ok batch={args.batch} actions={','.join(actions)} qa={report['qa_dir']}")


if __name__ == "__main__":
    main()
