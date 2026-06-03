from __future__ import annotations

import inspect
import sys
import types
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

STABLE_FRAME_COUNTS = {
    "idle": 16,
    "blink": 10,
    "clicked": 9,
    "happy": 48,
    "wave": 17,
    "cute": 44,
    "sleep_in": 11,
    "sleep": 11,
    "wake": 11,
    "walk": 14,
    "walk_left": 14,
    "drag": 8,
}


class StableSpriteRouteTests(unittest.TestCase):
    def test_core_stable_sprite_assets_are_complete_transparent_and_512_square(self) -> None:
        from desktop_cat.sprite_manifest import ACTIONS

        sprite_root = ROOT / "assets" / "sprites"
        expected = {action.name: STABLE_FRAME_COUNTS[action.name] for action in ACTIONS}
        for action, frame_count in expected.items():
            with self.subTest(action=action):
                frames = sorted((sprite_root / action).glob("*.png"))
                self.assertEqual(frame_count, len(frames))
                for path in frames:
                    image = Image.open(path).convert("RGBA")
                    self.assertEqual((512, 512), image.size)
                    self.assertEqual((0, 0, 0, 0), image.getpixel((0, 0)))
                    self.assertEqual((0, 0, 0, 0), image.getpixel((511, 0)))
                    self.assertEqual((0, 0, 0, 0), image.getpixel((0, 511)))
                    self.assertEqual((0, 0, 0, 0), image.getpixel((511, 511)))
                    self.assertIsNotNone(image.getbbox())

    def test_stable_preview_uses_full_sprite_frames_not_cutout_rig_renderer(self) -> None:
        from desktop_cat import rig_app

        self.assertTrue(hasattr(rig_app, "StableDesktopCatApp"))
        source = inspect.getsource(rig_app.StableSpriteFrameSource)
        self.assertIn('asset_folder = "sprites"', source)
        self.assertNotIn("RigRenderer", source)
        self.assertNotIn("RigModel", source)
        self.assertNotIn("rig_parts", source)

    def test_stable_build_and_run_scripts_exist(self) -> None:
        self.assertTrue((ROOT / "stable_launcher.py").exists())
        self.assertTrue((ROOT / "run_stable_dev.ps1").exists())
        self.assertTrue((ROOT / "build_stable.ps1").exists())

    def test_candidate_build_script_is_separate_from_stable_build(self) -> None:
        script_path = ROOT / "build_candidate.ps1"
        self.assertTrue(script_path.exists())
        script = script_path.read_text(encoding="utf-8")
        self.assertIn("DesktopCatCandidatePreview", script)
        self.assertIn("candidate_launcher.py", script)
        self.assertIn("--add-data", script)
        self.assertIn("idle,blink,wave,clicked,happy,sleep_in,sleep,wake,walk,walk_left,cute,drag", script)
        self.assertNotIn("DesktopCatStablePreview", script)

    def test_candidate_preview_uses_production_batch_clean_frames(self) -> None:
        from desktop_cat import rig_app

        self.assertTrue(hasattr(rig_app, "ProductionBatchFrameSource"))
        self.assertTrue(hasattr(rig_app, "CandidateDesktopCatApp"))
        source = inspect.getsource(rig_app.ProductionBatchFrameSource)
        self.assertIn("assets", source)
        self.assertIn("production", source)
        self.assertIn("batches", source)
        self.assertIn("clean", source)
        self.assertTrue((ROOT / "candidate_launcher.py").exists())
        self.assertTrue((ROOT / "run_candidate_dev.ps1").exists())

    def test_candidate_launcher_defaults_to_latest_motion_quality_batch(self) -> None:
        launcher = (ROOT / "candidate_launcher.py").read_text(encoding="utf-8")
        self.assertIn("20260527_motion_quality_v1", launcher)
        self.assertIn("CandidateDesktopCatApp", launcher)
        self.assertIn("--smoke-ms", launcher)

    def test_candidate_app_builds_frame_source_after_tk_root_exists(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.CandidateDesktopCatApp)
        self.assertIn("frame_source_factory", inspect.getsource(rig_app.RigDesktopCatApp))
        self.assertIn("ProductionBatchFrameSource(batch_id)", source)

    def test_sleep_interaction_uses_sleep_in_sleep_and_wake_sequence(self) -> None:
        from desktop_cat import rig_app

        app_source = inspect.getsource(rig_app.RigDesktopCatApp)
        self.assertIn('"sleep_in"', app_source)
        self.assertIn('"wake"', app_source)
        self.assertIn('self.set_action("wake"', app_source)
        release_source = inspect.getsource(rig_app.RigDesktopCatApp.on_release)
        self.assertIn('press_action in {"sleep", "sleep_in"}', release_source)
        self.assertIn('self.action == "wake"', release_source)
        self.assertIn("return", release_source)

    def test_walk_action_moves_desktop_window_instead_of_only_playing_in_place(self) -> None:
        from desktop_cat import rig_app

        app_source = inspect.getsource(rig_app.RigDesktopCatApp)
        self.assertIn("walk_direction", app_source)
        self.assertIn("advance_walk", app_source)
        self.assertIn("self.root.geometry", inspect.getsource(rig_app.RigDesktopCatApp.advance_walk))

    def test_happy_action_has_left_and_right_motion_variants(self) -> None:
        from desktop_cat import rig_app

        app_source = inspect.getsource(rig_app.RigDesktopCatApp)
        self.assertIn('"happy_right"', app_source)
        self.assertIn("happy_action_for_direction", app_source)
        self.assertIn("advance_happy", app_source)
        self.assertIn("self.root.geometry", inspect.getsource(rig_app.RigDesktopCatApp.advance_happy))
        self.assertEqual("happy", rig_app.RigDesktopCatApp.happy_action_for_direction(None, -1))
        self.assertEqual("happy_right", rig_app.RigDesktopCatApp.happy_action_for_direction(None, 1))

    def test_walk_menu_has_explicit_left_and_right_commands(self) -> None:
        from desktop_cat import rig_app

        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)
        self.assertIn("向左散步", menu_source)
        self.assertIn("向右散步", menu_source)
        self.assertIn("walk_left", inspect.getsource(rig_app.RigDesktopCatApp))
        self.assertIn("walk_right", inspect.getsource(rig_app.RigDesktopCatApp))

    def test_walk_step_does_not_snap_from_outside_safe_bounds(self) -> None:
        from desktop_cat.rig_app import bounded_walk_direction, next_walk_x

        self.assertEqual(496, next_walk_x(current_x=500, direction=-1, min_x=8, max_x=400, step=4))
        self.assertEqual(500, next_walk_x(current_x=500, direction=1, min_x=8, max_x=400, step=4))
        self.assertEqual(12, next_walk_x(current_x=8, direction=1, min_x=8, max_x=400, step=4))
        self.assertEqual(8, next_walk_x(current_x=8, direction=-1, min_x=8, max_x=400, step=4))
        self.assertEqual(-1, bounded_walk_direction(current_x=500, preferred=1, min_x=8, max_x=400))
        self.assertEqual(1, bounded_walk_direction(current_x=0, preferred=-1, min_x=8, max_x=400))

    def test_cute_action_is_available_from_context_menu(self) -> None:
        from desktop_cat import rig_app

        app_source = inspect.getsource(rig_app.RigDesktopCatApp)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)
        self.assertIn('"cute"', app_source)
        self.assertIn("卖萌一下", menu_source)
        self.assertIn("self.set_action(\"cute\"", app_source)

    def test_candidate_speech_bubble_sits_close_to_pet_head(self) -> None:
        from desktop_cat import rig_app

        _x, y = rig_app.speech_bubble_geometry(
            screen_w=1024,
            pet_center_x=500,
            pet_top_y=300,
            bubble_w=160,
            bubble_h=50,
        )
        self.assertEqual(300 - 50 + rig_app.SPEECH_BUBBLE_PET_OVERLAP_PX, y)

    def test_sprite_speech_bubble_sits_close_to_pet_head(self) -> None:
        sys.modules.setdefault("pystray", types.ModuleType("pystray"))
        from desktop_cat import sprite_app

        _x, y = sprite_app.speech_bubble_geometry(
            screen_w=1024,
            pet_center_x=500,
            pet_top_y=300,
            bubble_w=160,
            bubble_h=70,
        )
        self.assertEqual(300 - 70 + sprite_app.SPEECH_BUBBLE_PET_OVERLAP_PX, y)


if __name__ == "__main__":
    unittest.main()
