from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class RigPreviewTests(unittest.TestCase):
    def test_nearest_exit_side_uses_horizontal_distance(self) -> None:
        from desktop_cat.rig_app import nearest_exit_side

        self.assertEqual("left", nearest_exit_side(100, 280, 1920))
        self.assertEqual("right", nearest_exit_side(1600, 280, 1920))
        self.assertEqual("right", nearest_exit_side(820, 280, 1920))

    def test_entry_geometry_starts_outside_and_stops_fully_visible(self) -> None:
        from desktop_cat.rig_app import entry_positions

        self.assertEqual((-280, 8), entry_positions("left", 1920))
        self.assertEqual((1920, 1632), entry_positions("right", 1920))

    def test_entry_y_is_clamped_to_current_screen(self) -> None:
        from desktop_cat.rig_app import clamped_window_y

        self.assertEqual(8, clamped_window_y(-100, 1080))
        self.assertEqual(400, clamped_window_y(400, 1080))
        self.assertEqual(832, clamped_window_y(5000, 1080))

    def test_place_initially_uses_saved_exit_side_for_entry(self) -> None:
        from desktop_cat import rig_app

        geometries: list[str] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.store = type(
            "Store",
            (),
            {
                "config": type(
                    "Config",
                    (),
                    {
                        "last_exit_side": "left",
                        "last_exit_y": 400,
                        "last_position": {"x": 100, "y": 100},
                    },
                )()
            },
        )()
        app.root = type(
            "Root",
            (),
            {
                "winfo_screenwidth": lambda _self: 1920,
                "winfo_screenheight": lambda _self: 1080,
                "geometry": lambda _self, value: geometries.append(value),
            },
        )()
        app.entering = False
        app.entry_side = None
        app.entry_target_x = None
        app.first_launch_pending = False

        app.place_initially()

        self.assertTrue(app.entering)
        self.assertEqual("left", app.entry_side)
        self.assertEqual(8, app.entry_target_x)
        self.assertEqual(["280x240+-280+400"], geometries)

    def test_place_initially_walks_in_from_right_on_first_launch(self) -> None:
        from desktop_cat import rig_app

        geometries: list[str] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.store = type(
            "Store",
            (),
            {
                "config": type(
                    "Config",
                    (),
                    {
                        "last_exit_side": None,
                        "last_exit_y": None,
                        "last_position": None,
                    },
                )()
            },
        )()
        app.root = type(
            "Root",
            (),
            {
                "winfo_screenwidth": lambda _self: 1920,
                "winfo_screenheight": lambda _self: 1080,
                "geometry": lambda _self, value: geometries.append(value),
            },
        )()
        app.entering = False
        app.entry_side = None
        app.entry_target_x = None
        app.first_launch_pending = True

        app.place_initially()

        self.assertTrue(app.entering)
        self.assertEqual("right", app.entry_side)
        self.assertEqual(1612, app.entry_target_x)
        self.assertEqual(-1, app.walk_direction)
        self.assertEqual("walk_left", app.action)
        self.assertEqual(["280x240+1920+784"], geometries)

    def test_place_initially_restores_saved_position_without_exit_state(self) -> None:
        from desktop_cat import rig_app

        geometries: list[str] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.store = type(
            "Store",
            (),
            {
                "config": type(
                    "Config",
                    (),
                    {
                        "last_exit_side": None,
                        "last_exit_y": None,
                        "last_position": {"x": 640, "y": 360},
                    },
                )()
            },
        )()
        app.root = type(
            "Root",
            (),
            {
                "winfo_screenwidth": lambda _self: 1920,
                "winfo_screenheight": lambda _self: 1080,
                "geometry": lambda _self, value: geometries.append(value),
            },
        )()
        app.entering = False
        app.entry_side = None
        app.entry_target_x = None
        app.first_launch_pending = False

        app.place_initially()

        self.assertFalse(app.entering)
        self.assertIsNone(app.entry_side)
        self.assertIsNone(app.entry_target_x)
        self.assertEqual(["280x240+640+360"], geometries)

    def test_begin_exit_chooses_nearest_edge_and_interrupts_current_action(self) -> None:
        from desktop_cat import rig_app

        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.root = type(
            "Root",
            (),
            {
                "winfo_x": lambda _self: 1500,
                "winfo_y": lambda _self: 300,
                "winfo_screenwidth": lambda _self: 1920,
            },
        )()
        app.bubble = type("Bubble", (), {"clear_all": lambda _self: None})()
        app.draw = lambda: None
        app.action = "sleep"
        app.action_token_counter = 2
        app.active_action_token = None
        app.exiting = False

        app.begin_exit()

        self.assertTrue(app.exiting)
        self.assertEqual("right", app.exit_side)
        self.assertEqual("walk", app.action)

    def test_exit_completion_persists_side_and_closes_immediately(self) -> None:
        from desktop_cat import rig_app

        saved: list[tuple[str, int]] = []
        destroyed: list[bool] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.exit_side = "left"
        app.store = type(
            "Store",
            (),
            {
                "update_exit_state": lambda _self, side, y: saved.append(
                    (side, y)
                )
            },
        )()
        app.root = type(
            "Root",
            (),
            {
                "winfo_y": lambda _self: 360,
                "destroy": lambda _self: destroyed.append(True),
            },
        )()
        app.bubble = type(
            "Bubble",
            (),
            {
                "window": type(
                    "Window",
                    (),
                    {"destroy": lambda _self: None},
                )()
            },
        )()

        app.finish_exit()

        self.assertEqual([("left", 360)], saved)
        self.assertEqual([True], destroyed)

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

    def test_non_idle_action_rejects_new_action_without_queueing(self) -> None:
        from desktop_cat import rig_app

        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.action = "happy"
        app.frame = 12
        app.resetting_position = False
        app.drag_start = None
        app.happy_start = (10, 10)
        app.draw = lambda: None

        started = app.set_action("wave", 2.2)

        self.assertFalse(started)
        self.assertEqual("happy", app.action)
        self.assertEqual(12, app.frame)
        self.assertFalse(hasattr(app, "pending_actions"))

    def test_finished_action_returns_to_natural_chain_without_old_requests(self) -> None:
        from desktop_cat import rig_app

        cleared: list[int] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.action = "happy"
        app.frame = 47
        app.action_until = 0.0
        app.happy_start = (10, 10)
        app.active_action_token = 7
        app.bubble = type(
            "Bubble",
            (),
            {"clear_owner": lambda _self, owner: cleared.append(owner)},
        )()

        app.finish_current_action(123.0)

        self.assertEqual([7], cleared)
        self.assertIsNone(app.active_action_token)
        self.assertEqual("idle", app.action)
        self.assertEqual(0, app.frame)
        self.assertGreater(app.action_until, 123.0)

    def test_forced_action_replacement_clears_previous_action_bubble(self) -> None:
        from desktop_cat import rig_app

        cleared: list[int] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.action = "happy"
        app.active_action_token = 4
        app.action_token_counter = 4
        app.happy_start = (10, 10)
        app.bubble = type(
            "Bubble",
            (),
            {"clear_owner": lambda _self, owner: cleared.append(owner)},
        )()
        app.draw = lambda: None

        started = app.set_action("drag", 1.0, force=True)

        self.assertTrue(started)
        self.assertEqual([4], cleared)
        self.assertEqual(5, app.active_action_token)
        self.assertEqual("drag", app.action)

    def test_new_action_starts_immediately_after_previous_action_finishes(self) -> None:
        from desktop_cat import rig_app

        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.action = "happy"
        app.frame = 47
        app.action_until = 0.0
        app.resetting_position = False
        app.drag_start = None
        app.happy_start = (10, 10)
        app.draw = lambda: None

        app.finish_current_action(123.0)
        started = app.set_action("wave", 2.2)

        self.assertTrue(started)
        self.assertEqual("wave", app.action)
        self.assertEqual(0, app.frame)

    def test_idle_mouse_press_waits_for_release_before_click_feedback(self) -> None:
        from desktop_cat import rig_app

        shown: list[object] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.action = "idle"
        app.resetting_position = False
        app.drag_start = None
        app.root = type(
            "Root",
            (),
            {"winfo_x": lambda _self: 10, "winfo_y": lambda _self: 20},
        )()
        app.draw = lambda: None
        app.say = shown.append

        event = type("Event", (), {"x_root": 100, "y_root": 120})()
        app.on_press(event)

        self.assertEqual("idle", app.action)
        self.assertEqual([], shown)

    def test_idle_mouse_release_without_drag_starts_clicked_and_shows_one_bubble(self) -> None:
        from desktop_cat import rig_app

        shown: list[object] = []

        class FakeRoot:
            def winfo_x(self) -> int:
                return 10

            def winfo_y(self) -> int:
                return 20

        class FakeStore:
            def update_position(self, _x: int, _y: int) -> None:
                pass

        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.action = "idle"
        app.resetting_position = False
        app.drag_start = (100, 120)
        app.window_start = (10, 20)
        app.press_action = "idle"
        app.drag_moved = False
        app.root = FakeRoot()
        app.store = FakeStore()
        app.draw = lambda: None
        app.say = shown.append

        app.on_release(None)

        self.assertEqual("clicked", app.action)
        self.assertEqual(1, len(shown))

    def test_action_speech_is_owned_by_the_active_action_token(self) -> None:
        from desktop_cat import rig_app

        shown: list[dict[str, object]] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.active_action_token = 21
        app.render_text = lambda text: text
        app.pet_anchor = lambda: (10, 20)
        app.bubble = type(
            "Bubble",
            (),
            {
                "show": lambda _self, _text, _x, _y, **kwargs: shown.append(
                    kwargs
                )
            },
        )()

        app.say("hello")

        self.assertEqual(21, shown[0]["owner"])

    def test_busy_mouse_press_drops_clicked_action_and_bubble(self) -> None:
        from desktop_cat import rig_app

        shown: list[object] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.action = "happy"
        app.frame = 5
        app.resetting_position = False
        app.drag_start = None
        app.root = type(
            "Root",
            (),
            {"winfo_x": lambda _self: 10, "winfo_y": lambda _self: 20},
        )()
        app.draw = lambda: None
        app.say = shown.append

        event = type("Event", (), {"x_root": 100, "y_root": 120})()
        app.on_press(event)

        self.assertEqual("happy", app.action)
        self.assertEqual([], shown)

    def test_drag_start_from_idle_has_no_click_action_or_bubble(self) -> None:
        from desktop_cat import rig_app

        cleared: list[int] = []
        shown: list[object] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.action = "idle"
        app.active_action_token = None
        app.action_token_counter = 8
        app.drag_start = (100, 120)
        app.window_start = (10, 20)
        app.drag_moved = False
        app.bubble = type(
            "Bubble",
            (),
            {
                "clear_owner": lambda _self, owner: cleared.append(owner),
                "move_to_pet": lambda *_args: None,
            },
        )()
        app.root = type("Root", (), {"geometry": lambda *_args: None})()
        app.draw = lambda: None
        app.say = shown.append

        event = type("Event", (), {"x_root": 110, "y_root": 130})()
        app.on_drag(event)

        self.assertEqual([], cleared)
        self.assertEqual([], shown)
        self.assertEqual(9, app.active_action_token)
        self.assertEqual("drag", app.action)

    def test_sleep_mouse_press_still_wakes_immediately(self) -> None:
        from desktop_cat import rig_app

        shown: list[object] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.action = "sleep"
        app.resetting_position = False
        app.drag_start = None
        app.root = type(
            "Root",
            (),
            {"winfo_x": lambda _self: 10, "winfo_y": lambda _self: 20},
        )()
        app.draw = lambda: None
        app.say = shown.append

        event = type("Event", (), {"x_root": 100, "y_root": 120})()
        app.on_press(event)

        self.assertEqual("wake", app.action)
        self.assertEqual(1, len(shown))

    def test_rejected_cute_action_does_not_show_bubble(self) -> None:
        from desktop_cat import rig_app

        shown: list[object] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.set_action = lambda *_args, **_kwargs: False
        app.say = shown.append

        app.cute()

        self.assertEqual([], shown)

    def test_rejected_happy_does_not_mutate_motion_state_or_show_bubble(self) -> None:
        from desktop_cat import rig_app

        shown: list[object] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.happy_direction = -1
        app.happy_start = (40, 50)
        app.action = "wave"
        app.resetting_position = False
        app.drag_start = None
        app.next_horizontal_direction = lambda *_args: 1
        app.root = type(
            "Root",
            (),
            {"winfo_x": lambda _self: 100, "winfo_y": lambda _self: 120},
        )()
        app.draw = lambda: None
        app.say = shown.append

        app.happy()

        self.assertEqual(-1, app.happy_direction)
        self.assertEqual((40, 50), app.happy_start)
        self.assertEqual([], shown)

    def test_rejected_walk_left_does_not_mutate_direction_or_show_bubble(self) -> None:
        from desktop_cat import rig_app

        shown: list[object] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.walk_direction = 1
        app.walk_can_reverse = True
        app.set_action = lambda *_args, **_kwargs: False
        app.say = shown.append

        app.walk_left()

        self.assertEqual(1, app.walk_direction)
        self.assertTrue(app.walk_can_reverse)
        self.assertEqual([], shown)

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
        app.draw = lambda: None

        app.on_release(None)

        self.assertEqual("clicked", app.action)
        self.assertEqual([(10, 20)], app.store.positions)


if __name__ == "__main__":
    unittest.main()
