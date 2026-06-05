from __future__ import annotations

import inspect
import os
import sys
import tempfile
import unittest
from datetime import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class LowDistractionModeTests(unittest.TestCase):
    def test_config_store_round_trips_low_distraction_mode(self) -> None:
        from desktop_cat.config import ConfigStore

        with tempfile.TemporaryDirectory() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()
                store.config.low_distraction_mode = True
                store.save()

                self.assertTrue(ConfigStore().config.low_distraction_mode)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_low_distraction_idle_actions_are_calm(self) -> None:
        from desktop_cat.rig_app import idle_action_choices

        actions, weights = idle_action_choices(low_distraction_mode=True)
        self.assertEqual(len(actions), len(weights))
        self.assertIn("blink", actions)
        self.assertIn("sleep_in", actions)
        self.assertNotIn("happy", actions)
        self.assertNotIn("cute", actions)
        self.assertNotIn("walk", actions)

    def test_normal_idle_actions_keep_playful_variants(self) -> None:
        from desktop_cat.rig_app import idle_action_choices

        actions, _weights = idle_action_choices(low_distraction_mode=False, current_time=time(15, 0))
        self.assertIn("happy", actions)
        self.assertIn("cute", actions)
        self.assertIn("walk", actions)

    def test_candidate_launcher_has_low_distraction_preview_flag(self) -> None:
        launcher = (ROOT / "candidate_launcher.py").read_text(encoding="utf-8")

        self.assertIn("--low-distraction", launcher)
        self.assertIn("low_distraction_mode=args.low_distraction", launcher)

    def test_rig_app_has_menu_toggle_for_low_distraction_mode(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)
        self.assertIn("low_distraction_mode", source)
        self.assertIn("toggle_low_distraction_mode", source)
        self.assertIn("low_distraction_menu_label", menu_source)

    def test_low_distraction_menu_label_has_enter_and_exit_states(self) -> None:
        from desktop_cat.rig_app import low_distraction_menu_label

        self.assertEqual("进入低打扰模式", low_distraction_menu_label(False))
        self.assertEqual("退出低打扰模式", low_distraction_menu_label(True))


if __name__ == "__main__":
    unittest.main()
