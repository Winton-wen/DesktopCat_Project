from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = ROOT / "assets" / "production" / "desktop_cat"


class ProductionPipelineTests(unittest.TestCase):
    def test_production_workspace_has_required_contract_files(self) -> None:
        required = [
            PRODUCTION / "README.md",
            PRODUCTION / "character_lock.md",
            PRODUCTION / "prompt_pack.md",
            PRODUCTION / "batch_manifest.json",
            PRODUCTION / "source_refs",
            PRODUCTION / "pose_sheets",
            PRODUCTION / "clean_frames",
            PRODUCTION / "rejected",
            PRODUCTION / "qa",
            PRODUCTION / "batches" / "stable_v2_baseline",
        ]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), str(path))

    def test_batch_manifest_tracks_stable_baseline_and_acceptance_rules(self) -> None:
        manifest = json.loads((PRODUCTION / "batch_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("desktop_cat", manifest["character_id"])
        self.assertEqual("stable_v2_baseline", manifest["protected_baseline"])
        self.assertIn("no_identity_drift", manifest["acceptance_gates"])
        self.assertIn("idle_compatible_first_last_frames", manifest["acceptance_gates"])
        self.assertIn("stable_v2_baseline", {batch["id"] for batch in manifest["batches"]})
        for action in ["sleep_in", "wake", "walk", "walk_left"]:
            self.assertIn(action, manifest["actions"])
        self.assertEqual(48, manifest["actions"]["happy"]["frames"])
        self.assertEqual(44, manifest["actions"]["cute"]["frames"])
        self.assertEqual(99, manifest["actions"]["sleep_in"]["frames"])
        self.assertEqual(96, manifest["actions"]["wake"]["frames"])
        self.assertEqual(16, manifest["actions"]["walk"]["frames"])
        self.assertEqual(16, manifest["actions"]["walk_left"]["frames"])
        self.assertEqual(24, manifest["actions"]["happy"]["fps"])
        self.assertEqual(24, manifest["actions"]["cute"]["fps"])

    def test_prompt_pack_has_action_prompt_for_every_manifest_action(self) -> None:
        manifest = json.loads((PRODUCTION / "batch_manifest.json").read_text(encoding="utf-8"))
        prompt_pack = (PRODUCTION / "prompt_pack.md").read_text(encoding="utf-8")
        for action in manifest["actions"]:
            with self.subTest(action=action):
                self.assertIn(f"`{action}`:", prompt_pack)

    def test_synth_motion_tool_generates_high_fps_happy_and_cute_frames(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "clean"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "synthesize_motion_action.py"),
                    "--source",
                    str(ROOT / "assets" / "sprites" / "idle" / "00.png"),
                    "--target-root",
                    str(target),
                    "--actions",
                    "happy,cute",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("synthetic_motion_actions_ok", result.stdout)
            self.assertEqual(48, len(list((target / "happy").glob("*.png"))))
            self.assertEqual(44, len(list((target / "cute").glob("*.png"))))
            first = Image.open(target / "happy" / "00.png").convert("RGBA")
            apex = Image.open(target / "happy" / "20.png").convert("RGBA")
            self.assertEqual((512, 512), first.size)
            self.assertLess(apex.getbbox()[1], first.getbbox()[1])

    def test_keypose_sheet_importer_splits_real_pose_sheet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sheet = Path(tmp) / "sheet.png"
            image = Image.new("RGBA", (400, 300), (0, 255, 0, 255))
            for row in range(3):
                for col in range(4):
                    x0 = col * 100 + 30
                    y0 = row * 100 + 20
                    x1 = x0 + 36 + col
                    y1 = y0 + 52 + row
                    color = (240, 150 + row * 20, 90 + col * 20, 255)
                    for y in range(y0, y1):
                        for x in range(x0, x1):
                            image.putpixel((x, y), color)
            image.save(sheet)
            out_root = Path(tmp) / "out"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "import_keypose_sheet.py"),
                    "--sheet",
                    str(sheet),
                    "--out-root",
                    str(out_root),
                    "--canvas-size",
                    "512x512",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("keypose_sheet_import_ok", result.stdout)
            self.assertEqual(12, len(list((out_root / "keyposes").glob("*.png"))))
            self.assertEqual(48, len(list((out_root / "happy").glob("*.png"))))
            self.assertEqual(44, len(list((out_root / "cute").glob("*.png"))))
            first = Image.open(out_root / "keyposes" / "00.png").convert("RGBA")
            self.assertEqual((512, 512), first.size)
            self.assertEqual(0, first.getpixel((0, 0))[3])

    def test_audit_tool_accepts_stable_baseline_batch(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "audit_production_batch.py"),
                "--batch",
                "stable_v2_baseline",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("production_batch_audit_ok", result.stdout)

    def test_audit_tool_can_write_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "audit.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "audit_production_batch.py"),
                    "--batch",
                    "stable_v2_baseline",
                    "--report",
                    str(report),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual("stable_v2_baseline", data["batch"])
            self.assertTrue(data["ok"])
            self.assertEqual([], data["errors"])

    def test_audit_tool_accepts_scoped_seeded_candidate_actions(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "audit_production_batch.py"),
                "--batch",
                "20260526_batch1_idle_blink_wave",
                "--actions",
                "idle,blink,wave",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("production_batch_audit_ok", result.stdout)
        self.assertNotIn("clicked", result.stdout + result.stderr)

    def test_batch_initializer_can_create_candidate_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "20260526_test_candidate"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "init_production_batch.py"),
                    "--batch-id",
                    target.name,
                    "--output-root",
                    str(Path(tmp)),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            for relative in [
                "README.md",
                "notes.md",
                "raw",
                "clean/idle",
                "clean/blink",
                "clean/wave",
                "clean/clicked",
                "clean/happy",
                "clean/sleep",
                "clean/drag",
                "qa",
            ]:
                self.assertTrue((target / relative).exists(), relative)

    def test_production_qa_exporter_generates_batch_contact_sheet_and_gifs(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "export_production_batch_qa.py"),
                "--batch",
                "stable_v2_baseline",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("production_batch_qa_export_ok", result.stdout)
        qa_dir = PRODUCTION / "qa" / "stable_v2_baseline"
        self.assertTrue((qa_dir / "contact_sheet.png").exists())
        for action in ["idle", "blink", "wave", "clicked", "happy", "sleep", "drag"]:
            self.assertTrue((qa_dir / f"{action}.gif").exists(), action)

    def test_production_qa_exporter_supports_scoped_actions(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "export_production_batch_qa.py"),
                "--batch",
                "stable_v2_baseline",
                "--actions",
                "idle,blink,wave",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        qa_dir = PRODUCTION / "qa" / "stable_v2_baseline"
        self.assertTrue((qa_dir / "contact_sheet.png").exists())

    def test_promote_tool_requires_audited_non_baseline_batch_and_dry_run(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "promote_production_batch.py"),
                "--batch",
                "stable_v2_baseline",
                "--dry-run",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("protected baseline", result.stderr + result.stdout)

    def test_promote_tool_can_dry_run_valid_candidate_batch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            candidate = tmp_root / "candidate"
            shutil.copytree(ROOT / "assets" / "sprites", candidate)
            manifest_path = tmp_root / "manifest.json"
            manifest = json.loads((PRODUCTION / "batch_manifest.json").read_text(encoding="utf-8"))
            manifest["protected_baseline"] = "stable_v2_baseline"
            manifest["batches"].append(
                {
                    "id": "candidate",
                    "status": "candidate",
                    "source": str(candidate),
                    "qa_contact_sheet": "assets/qa/stable/stable_sprite_contact_sheet.png",
                    "action_overrides": {
                        "sleep_in": {"frames": 11},
                        "wake": {"frames": 11},
                        "walk": {"frames": 14},
                        "walk_left": {"frames": 14},
                    },
                    "notes": "test candidate",
                }
            )
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "promote_production_batch.py"),
                    "--batch",
                    "candidate",
                    "--manifest",
                    str(manifest_path),
                    "--dry-run",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("production_batch_promote_dry_run_ok", result.stdout)

    def test_generation_request_tool_writes_action_prompt_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            batch_root = Path(tmp) / "batch"
            batch_root.mkdir()
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "prepare_generation_requests.py"),
                    "--batch-root",
                    str(batch_root),
                    "--actions",
                    "idle,blink,wave",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("generation_requests_prepared", result.stdout)
            for action in ["idle", "blink", "wave"]:
                path = batch_root / "generation_requests" / f"{action}.md"
                self.assertTrue(path.exists(), action)
                text = path.read_text(encoding="utf-8")
                self.assertIn("Character Identity", text)
                self.assertIn("Negative Prompt", text)
                self.assertIn("Frame Count", text)
                self.assertIn("idle-compatible", text)

    def test_seed_tool_copies_selected_baseline_actions_into_candidate_clean_frames(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            batch_root = Path(tmp) / "batch"
            for action in ["idle", "blink", "wave"]:
                (batch_root / "clean" / action).mkdir(parents=True)
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "seed_production_batch.py"),
                    "--batch-root",
                    str(batch_root),
                    "--actions",
                    "idle,blink,wave",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("production_batch_seeded", result.stdout)
            expected_counts = {"idle": 16, "blink": 10, "wave": 17}
            for action, expected_count in expected_counts.items():
                frames = sorted((batch_root / "clean" / action).glob("*.png"))
                self.assertEqual(expected_count, len(frames), action)
            self.assertTrue((batch_root / "seed_report.json").exists())

    def test_compare_tool_writes_baseline_difference_report_for_scoped_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "compare.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "compare_production_batch.py"),
                    "--batch",
                    "20260526_batch1_idle_blink_wave",
                    "--actions",
                    "idle,blink,wave",
                    "--report",
                    str(report),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("production_batch_compare_ok", result.stdout)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual("20260526_batch1_idle_blink_wave", data["batch"])
            self.assertEqual("stable_v2_baseline", data["baseline"])
            self.assertEqual(["idle", "blink", "wave"], data["actions"])
            self.assertEqual(43, data["frame_count"])
            self.assertEqual(0.0, data["average_rms"])

    def test_measure_tool_writes_shape_metrics_for_scoped_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "metrics.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "measure_production_batch.py"),
                    "--batch",
                    "20260526_batch1_idle_blink_wave",
                    "--actions",
                    "idle,blink,wave",
                    "--report",
                    str(report),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("production_batch_measure_ok", result.stdout)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual("20260526_batch1_idle_blink_wave", data["batch"])
            self.assertEqual(["idle", "blink", "wave"], data["actions"])
            self.assertEqual(43, data["frame_count"])
            self.assertIn("idle", data["action_summaries"])
            self.assertGreater(data["action_summaries"]["idle"]["min_edge_margin"], 0)

    def test_import_tool_replaces_candidate_action_with_backup_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            batch_root = tmp_root / "batch"
            source = tmp_root / "new_idle"
            shutil.copytree(ROOT / "assets" / "sprites" / "idle", batch_root / "clean" / "idle")
            shutil.copytree(ROOT / "assets" / "sprites" / "idle", source)
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "import_production_action.py"),
                    "--batch-root",
                    str(batch_root),
                    "--action",
                    "idle",
                    "--source",
                    str(source),
                    "--expected-count",
                    "16",
                    "--canvas-size",
                    "512x512",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("production_action_import_ok", result.stdout)
            self.assertEqual(16, len(list((batch_root / "clean" / "idle").glob("*.png"))))
            backups = list((batch_root / "qa" / "import_backups").glob("idle_*"))
            self.assertEqual(1, len(backups))
            self.assertEqual(16, len(list(backups[0].glob("*.png"))))
            report = json.loads((batch_root / "qa" / "import_report_idle.json").read_text(encoding="utf-8"))
            self.assertEqual("idle", report["action"])
            self.assertEqual(16, report["imported_count"])
            self.assertTrue(report["backup"])

    def test_import_tool_rejects_wrong_frame_count_before_replacing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            batch_root = tmp_root / "batch"
            source = tmp_root / "bad_idle"
            shutil.copytree(ROOT / "assets" / "sprites" / "idle", batch_root / "clean" / "idle")
            source.mkdir()
            shutil.copy2(ROOT / "assets" / "sprites" / "idle" / "00.png", source / "00.png")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "import_production_action.py"),
                    "--batch-root",
                    str(batch_root),
                    "--action",
                    "idle",
                    "--source",
                    str(source),
                    "--expected-count",
                    "16",
                    "--canvas-size",
                    "512x512",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("expected 16 png frames", result.stdout + result.stderr)
            self.assertEqual(16, len(list((batch_root / "clean" / "idle").glob("*.png"))))

    def test_gate_tool_accepts_current_seeded_candidate_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "gate.json"
            actions = "idle,blink,wave,clicked,happy,sleep_in,sleep,wake,walk,walk_left,cute,drag"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "gate_production_batch.py"),
                    "--batch",
                    "20260526_batch1_idle_blink_wave",
                    "--actions",
                    actions,
                    "--report",
                    str(report),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("production_batch_gate_ok", result.stdout)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertTrue(data["ok"])
            self.assertEqual([], data["errors"])
            self.assertIn("min_edge_margin", data["checks"])

    def test_gate_tool_accepts_full_candidate_action_scope_with_pose_transitions(self) -> None:
        report = PRODUCTION / "qa" / "20260526_batch1_idle_blink_wave" / "gate_report.json"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "gate_production_batch.py"),
                "--batch",
                "20260526_batch1_idle_blink_wave",
                "--actions",
                "idle,blink,wave,clicked,happy,sleep_in,sleep,wake,walk,walk_left,cute,drag",
                "--report",
                str(report),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("production_batch_gate_ok", result.stdout)

    def test_full_qa_runner_refreshes_all_scoped_candidate_reports(self) -> None:
        actions = "idle,blink,wave,clicked,happy,sleep_in,sleep,wake,walk,walk_left,cute,drag"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "run_production_batch_qa.py"),
                "--batch",
                "20260526_batch1_idle_blink_wave",
                "--actions",
                actions,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("production_batch_full_qa_ok", result.stdout)
        qa_dir = PRODUCTION / "qa" / "20260526_batch1_idle_blink_wave"
        for filename in [
            "contact_sheet.png",
            "idle.gif",
            "blink.gif",
            "wave.gif",
            "audit_report.json",
            "shape_metrics.json",
            "compare_to_baseline.json",
            "compare_to_baseline.png",
            "gate_report.json",
            "full_qa_report.json",
        ]:
            self.assertTrue((qa_dir / filename).exists(), filename)
        data = json.loads((qa_dir / "full_qa_report.json").read_text(encoding="utf-8"))
        self.assertTrue(data["ok"])
        self.assertEqual(actions.split(","), data["actions"])

    def test_candidate_runtime_batch_has_all_interactive_action_frames(self) -> None:
        manifest = json.loads((PRODUCTION / "batch_manifest.json").read_text(encoding="utf-8"))
        batch = next(batch for batch in manifest["batches"] if batch["id"] == "20260527_motion_quality_v1")
        source = ROOT / batch["source"]
        for action, spec in manifest["actions"].items():
            with self.subTest(action=action):
                frames = sorted((source / action).glob("*.png"))
                self.assertEqual(int(spec["frames"]), len(frames))


if __name__ == "__main__":
    unittest.main()
