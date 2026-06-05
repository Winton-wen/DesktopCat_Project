from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class CandidateFeatureQaScriptTests(unittest.TestCase):
    def script_path(self) -> Path:
        return ROOT / "tools" / "run_candidate_feature_qa.py"

    def script_source(self) -> str:
        return self.script_path().read_text(encoding="utf-8")

    def test_script_exists_and_is_parseable(self) -> None:
        source = self.script_source()

        ast.parse(source)

    def test_script_defaults_to_current_candidate_batch(self) -> None:
        source = self.script_source()

        self.assertIn("20260527_motion_quality_v1", source)

    def test_script_runs_backend_qa_commands(self) -> None:
        source = self.script_source()

        self.assertIn("test_stable_sprite_route.py", source)
        self.assertIn("test_gift_config_experience.py", source)
        self.assertIn("run_production_batch_qa.py", source)
        self.assertIn("return_home", source)

    def test_script_has_visual_tour_steps_for_frontend_features(self) -> None:
        source = self.script_source()

        for marker in [
            "show_first_launch_message",
            "show_companion_message",
            "check_time_reminder",
            "toggle_low_distraction_mode",
            "reset_position",
            "happy",
            "cute",
            "wave",
            "walk_left",
            "walk_right",
            "sleep",
        ]:
            self.assertIn(marker, source)
        self.assertIn("root.geometry(f\"+24+{y}\")", source)

    def test_script_supports_smoke_and_report_options(self) -> None:
        source = self.script_source()

        self.assertIn("--smoke", source)
        self.assertIn("--report-dir", source)
        self.assertIn("candidate_feature_qa_", source)


if __name__ == "__main__":
    unittest.main()
