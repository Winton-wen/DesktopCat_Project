from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class RigPreviewTests(unittest.TestCase):
    def test_desktop_cat_rig_loads_parts_and_renders_idle_and_blink(self) -> None:
        from desktop_cat.rig import RigAnimation, RigModel, RigRenderer

        rig_path = ROOT / "assets" / "rig_parts" / "desktop_cat" / "rig.json"
        model = RigModel.load(rig_path)

        required_parts = {
            "body",
            "head",
            "ear_left",
            "ear_right",
            "eye_left",
            "eye_right",
            "eyelid_left",
            "eyelid_right",
            "paw_front_left",
            "paw_front_right",
            "paw_wave_right",
            "paw_back_left",
            "paw_back_right",
            "tail_01",
            "tail_02",
            "tail_03",
            "bow_left",
            "bow_right",
            "bow_center",
            "bell",
        }
        self.assertTrue(required_parts.issubset(model.parts.keys()))

        renderer = RigRenderer(model)
        animation = RigAnimation(model)
        idle = renderer.render(animation.pose("idle", 0.25))
        blink = renderer.render(animation.pose("blink", 0.5))

        self.assertEqual((512, 512), idle.size)
        self.assertEqual((512, 512), blink.size)
        self.assertEqual("RGBA", idle.mode)
        self.assertEqual("RGBA", blink.mode)
        self.assertIsNotNone(idle.getbbox())
        self.assertIsNotNone(blink.getbbox())
        self.assertNotEqual(idle.tobytes(), blink.tobytes())

    def test_wave_pose_moves_front_paw_and_renders_differently_from_idle(self) -> None:
        from desktop_cat.rig import RigAnimation, RigModel, RigRenderer

        rig_path = ROOT / "assets" / "rig_parts" / "desktop_cat" / "rig.json"
        model = RigModel.load(rig_path)
        animation = RigAnimation(model)
        renderer = RigRenderer(model)

        idle_pose = animation.pose("idle", 0.5)
        wave_pose = animation.pose("wave", 0.5)

        self.assertEqual(0.0, idle_pose.parts["pose_wave"].opacity)
        self.assertGreater(wave_pose.parts["pose_wave"].opacity, 0.8)
        self.assertEqual(0.0, wave_pose.parts["paw_wave_right"].opacity)
        self.assertEqual(0.0, wave_pose.parts["paw_front_right"].opacity)
        self.assertNotEqual(
            renderer.render(idle_pose).tobytes(),
            renderer.render(wave_pose).tobytes(),
        )

    def test_idle_keeps_full_ear_silhouette_without_separate_ear_masks(self) -> None:
        from desktop_cat.rig import RigAnimation, RigModel

        rig_path = ROOT / "assets" / "rig_parts" / "desktop_cat" / "rig.json"
        model = RigModel.load(rig_path)
        pose = RigAnimation(model).pose("idle", 0.0)

        self.assertEqual(0.0, pose.parts["ear_left"].opacity)
        self.assertEqual(0.0, pose.parts["ear_right"].opacity)

        head = model.parts["head"]
        self.assertEqual("head.png", head.file.name)

    def test_expressive_actions_have_distinct_rig_poses(self) -> None:
        from desktop_cat.rig import RigAnimation, RigModel, RigRenderer

        rig_path = ROOT / "assets" / "rig_parts" / "desktop_cat" / "rig.json"
        model = RigModel.load(rig_path)
        animation = RigAnimation(model)
        renderer = RigRenderer(model)
        idle = renderer.render(animation.pose("idle", 0.5)).tobytes()

        for action in ["clicked", "happy", "sleep", "drag"]:
            with self.subTest(action=action):
                pose = animation.pose(action, 0.5)
                rendered = renderer.render(pose)
                self.assertEqual((512, 512), rendered.size)
                self.assertNotEqual(idle, rendered.tobytes())

        clicked = animation.pose("clicked", 0.45)
        self.assertGreater(clicked.parts["mouth_open"].opacity, 0.8)
        happy = animation.pose("happy", 0.45)
        self.assertGreater(happy.parts["paw_wave_right"].opacity, 0.6)
        sleep = animation.pose("sleep", 0.5)
        self.assertGreater(sleep.parts["pose_sleep"].opacity, 0.8)
        drag = animation.pose("drag", 0.5)
        self.assertGreater(drag.parts["pose_drag"].opacity, 0.8)

    def test_rig_preview_app_module_imports_without_replacing_sprite_app(self) -> None:
        import desktop_cat.rig_app as rig_app

        self.assertTrue(hasattr(rig_app, "RigDesktopCatApp"))
        self.assertTrue(hasattr(rig_app, "StableSpriteFrameSource"))
        self.assertEqual("sprites", rig_app.StableSpriteFrameSource.asset_folder)
        sprite_app_path = ROOT / "src" / "desktop_cat" / "sprite_app.py"
        self.assertIn("class DesktopCatApp", sprite_app_path.read_text(encoding="utf-8"))

    def test_non_idle_actions_queue_instead_of_interrupting_current_action(self) -> None:
        from desktop_cat import rig_app

        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.action = "happy"
        app.frame = 12
        app.pending_actions = []
        app.happy_start = (10, 10)
        app.draw = lambda: None

        started = app.set_action("wave", 2.2)

        self.assertFalse(started)
        self.assertEqual("happy", app.action)
        self.assertEqual(12, app.frame)
        self.assertEqual([("wave", 2.2)], app.pending_actions)

    def test_queued_action_starts_after_current_non_idle_action_finishes(self) -> None:
        from desktop_cat import rig_app

        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.action = "happy"
        app.frame = 47
        app.action_until = 0.0
        app.pending_actions = [("wave", 2.2)]
        app.happy_start = (10, 10)
        app.draw = lambda: None

        app.finish_current_action(123.0)

        self.assertEqual("wave", app.action)
        self.assertEqual(0, app.frame)
        self.assertEqual([], app.pending_actions)

    def test_non_drag_release_does_not_cut_short_click_animation(self) -> None:
        from desktop_cat import rig_app

        class FakeRoot:
            def winfo_x(self) -> int:
                return 10

            def winfo_y(self) -> int:
                return 20

        class FakeStore:
            def __init__(self) -> None:
                self.positions: list[tuple[int, int]] = []

            def update_position(self, x: int, y: int) -> None:
                self.positions.append((x, y))

        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.action = "clicked"
        app.drag_start = (10, 10)
        app.window_start = (20, 20)
        app.press_action = "idle"
        app.drag_moved = False
        app.root = FakeRoot()
        app.store = FakeStore()
        app.pending_actions = []
        app.draw = lambda: None

        app.on_release(None)

        self.assertEqual("clicked", app.action)
        self.assertEqual([(10, 20)], app.store.positions)


if __name__ == "__main__":
    unittest.main()
