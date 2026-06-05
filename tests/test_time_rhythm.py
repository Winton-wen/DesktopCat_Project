from __future__ import annotations

import sys
import unittest
from datetime import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class TimeRhythmTests(unittest.TestCase):
    def test_pet_rhythm_for_time_matches_day_parts(self) -> None:
        from desktop_cat.rig_app import pet_rhythm_for_time

        self.assertEqual("morning", pet_rhythm_for_time(time(8, 30)))
        self.assertEqual("afternoon", pet_rhythm_for_time(time(15, 0)))
        self.assertEqual("evening", pet_rhythm_for_time(time(20, 30)))
        self.assertEqual("bedtime", pet_rhythm_for_time(time(23, 30)))
        self.assertEqual("late_night", pet_rhythm_for_time(time(2, 30)))

    def test_morning_idle_profile_allows_gentle_activity(self) -> None:
        from desktop_cat.rig_app import idle_action_choices

        actions, weights = idle_action_choices(low_distraction_mode=False, current_time=time(8, 30))
        self.assertEqual(len(actions), len(weights))
        self.assertIn("wave", actions)
        self.assertIn("happy", actions)
        self.assertIn("walk", actions)
        self.assertNotIn("sleep_in", actions)

    def test_evening_idle_profile_is_warm_but_not_roaming(self) -> None:
        from desktop_cat.rig_app import idle_action_choices

        actions, _weights = idle_action_choices(low_distraction_mode=False, current_time=time(20, 30))
        self.assertIn("happy", actions)
        self.assertIn("cute", actions)
        self.assertIn("sleep_in", actions)
        self.assertNotIn("walk", actions)

    def test_late_night_idle_profile_is_sleepy(self) -> None:
        from desktop_cat.rig_app import idle_action_choices

        actions, _weights = idle_action_choices(low_distraction_mode=False, current_time=time(2, 30))
        self.assertIn("sleep_in", actions)
        self.assertIn("blink", actions)
        self.assertNotIn("happy", actions)
        self.assertNotIn("cute", actions)
        self.assertNotIn("walk", actions)
        self.assertNotIn("wave", actions)

    def test_low_distraction_keeps_rhythm_calm(self) -> None:
        from desktop_cat.rig_app import idle_action_choices

        actions, _weights = idle_action_choices(low_distraction_mode=True, current_time=time(8, 30))
        self.assertNotIn("happy", actions)
        self.assertNotIn("cute", actions)
        self.assertNotIn("walk", actions)

    def test_candidate_launcher_has_rhythm_preview_time(self) -> None:
        launcher = (ROOT / "candidate_launcher.py").read_text(encoding="utf-8")

        self.assertIn("--test-rhythm-time", launcher)
        self.assertIn("test_rhythm_time=args.test_rhythm_time", launcher)


if __name__ == "__main__":
    unittest.main()
