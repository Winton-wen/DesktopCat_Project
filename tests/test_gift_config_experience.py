from __future__ import annotations

import inspect
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class GiftConfigExperienceTests(unittest.TestCase):
    def with_config_dir(self):
        return tempfile.TemporaryDirectory()

    def test_default_config_includes_partner_facing_fields(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()
                raw = json.loads(store.path.read_text(encoding="utf-8"))

                self.assertEqual("奶糖猫", store.config.pet_name)
                self.assertEqual("宝贝", store.config.partner_nickname)
                self.assertFalse(store.config.low_distraction_mode)
                self.assertFalse(store.config.first_launch_completed)
                self.assertEqual("assets/companion_messages/partner_default.json", store.config.companion_message_pack)
                self.assertIn("partner_nickname", raw)
                self.assertIn("companion_message_pack", raw)
                self.assertIn("first_launch_completed", raw)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_malformed_field_types_fall_back_to_safe_defaults(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                path = Path(temp_dir) / "config.json"
                path.write_text(
                    json.dumps(
                        {
                            "pet_name": {"bad": "type"},
                            "partner_nickname": [],
                            "low_distraction_mode": "false",
                            "first_launch_completed": "true",
                            "companion_message_pack": 42,
                            "last_position": {"x": True, "y": 20},
                        }
                    ),
                    encoding="utf-8",
                )

                config = ConfigStore().config

                self.assertEqual("奶糖猫", config.pet_name)
                self.assertEqual("宝贝", config.partner_nickname)
                self.assertFalse(config.low_distraction_mode)
                self.assertFalse(config.first_launch_completed)
                self.assertEqual("assets/companion_messages/partner_default.json", config.companion_message_pack)
                self.assertIsNone(config.last_position)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_first_launch_completion_round_trips(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()

                store.mark_first_launch_completed()

                self.assertTrue(ConfigStore().config.first_launch_completed)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_first_launch_completion_ignores_unwritable_config_file(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()
                store.path = Path(temp_dir)

                store.mark_first_launch_completed()

                self.assertTrue(store.config.first_launch_completed)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_companion_message_pack_path_falls_back_when_missing(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()
                store.config.companion_message_pack = "missing/messages.json"

                resolved = store.companion_message_pack_path()

                self.assertEqual(ROOT / "assets" / "companion_messages" / "partner_default.json", resolved)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_open_companion_message_pack_creates_editable_user_copy(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()

                path = store.open_companion_message_pack_file()

                self.assertEqual(Path(temp_dir) / "companion_messages" / "partner_custom.json", path)
                self.assertTrue(path.exists())
                self.assertEqual("companion_messages/partner_custom.json", ConfigStore().config.companion_message_pack)
                raw = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("messages", raw)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_open_config_file_creates_readme_for_non_developers(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()

                store.open_file()

                readme = Path(temp_dir) / "README.txt"
                self.assertTrue(readme.exists())
                text = readme.read_text(encoding="utf-8")
                self.assertIn("config.json", text)
                self.assertIn("pet_name", text)
                self.assertIn("partner_nickname", text)
                self.assertIn("low_distraction_mode", text)
                self.assertIn("companion_message_pack", text)
                self.assertIn("partner_custom.json", text)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_default_partner_facing_text_is_readable_chinese(self) -> None:
        from desktop_cat.config import PARTNER_NICKNAME, PET_NAME, README_TEXT
        from desktop_cat.rig_app import TEXT, low_distraction_menu_label
        from desktop_cat.time_reminders import DINNER_REMINDER, LUNCH_REMINDER

        readable_text = "\n".join(
            [
                PET_NAME,
                PARTNER_NICKNAME,
                README_TEXT,
                *TEXT.values(),
                low_distraction_menu_label(False),
                low_distraction_menu_label(True),
                LUNCH_REMINDER.message,
                DINNER_REMINDER.message,
            ]
        )

        self.assertIn("奶糖猫", readable_text)
        self.assertIn("宝贝", readable_text)
        self.assertIn("进入低打扰模式", readable_text)
        self.assertIn("小猪猪要乖乖按时吃午饭哟", readable_text)
        self.assertNotIn("鑷", readable_text)
        self.assertNotIn("闄", readable_text)
        self.assertNotIn("�", readable_text)

    def test_open_companion_message_pack_creates_readme(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()

                store.open_companion_message_pack_file()

                self.assertTrue((Path(temp_dir) / "README.txt").exists())
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_rig_falls_back_to_default_pack_when_custom_pack_is_malformed(self) -> None:
        from desktop_cat import rig_app
        from desktop_cat.companion_messages import load_default_companion_pack
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()
                custom_path = Path(temp_dir) / "companion_messages" / "partner_custom.json"
                custom_path.parent.mkdir(parents=True, exist_ok=True)
                custom_path.write_text("{not valid json", encoding="utf-8")
                store.config.companion_message_pack = "companion_messages/partner_custom.json"
                app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
                app.store = store

                pack = app.load_configured_companion_pack()

                self.assertEqual(
                    [message.id for message in load_default_companion_pack().messages],
                    [message.id for message in pack.messages],
                )
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_rig_falls_back_to_default_pack_when_custom_pack_has_no_valid_messages(self) -> None:
        from desktop_cat import rig_app
        from desktop_cat.companion_messages import load_default_companion_pack
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()
                custom_path = Path(temp_dir) / "companion_messages" / "partner_custom.json"
                custom_path.parent.mkdir(parents=True, exist_ok=True)
                custom_path.write_text('{"messages": [{"id": "broken"}]}', encoding="utf-8")
                store.config.companion_message_pack = "companion_messages/partner_custom.json"
                app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
                app.store = store

                pack = app.load_configured_companion_pack()

                self.assertEqual(
                    [message.id for message in load_default_companion_pack().messages],
                    [message.id for message in pack.messages],
                )
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_open_config_folder_returns_config_dir_and_creates_readme(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()

                folder = store.open_folder()

                self.assertEqual(Path(temp_dir), folder)
                self.assertTrue((Path(temp_dir) / "README.txt").exists())
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_rig_candidate_menu_can_open_config_file(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)

        self.assertIn("def open_config", source)
        self.assertIn("os.startfile", source)
        self.assertIn("打开配置文件", menu_source)

    def test_rig_candidate_menu_can_open_config_folder(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)

        self.assertIn("def open_config_folder", source)
        self.assertIn("open_folder", source)
        self.assertIn("打开配置文件夹", menu_source)

    def test_rig_candidate_menu_can_open_companion_message_pack(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)

        self.assertIn("def open_companion_message_pack", source)
        self.assertIn("open_companion_message_pack_file", source)
        self.assertIn("编辑陪伴语料", menu_source)

    def test_rig_candidate_has_first_launch_welcome_flow(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)

        self.assertIn("test_first_launch", source)
        self.assertIn("show_first_launch_message", source)
        self.assertIn("mark_first_launch_completed", source)

    def test_candidate_launcher_has_first_launch_preview_flag(self) -> None:
        launcher = (ROOT / "candidate_launcher.py").read_text(encoding="utf-8")

        self.assertIn("--test-first-launch", launcher)
        self.assertIn("test_first_launch=args.test_first_launch", launcher)

    def test_gift_launcher_uses_latest_candidate_batch_without_preview_title(self) -> None:
        launcher_path = ROOT / "gift_launcher.py"
        self.assertTrue(launcher_path.exists())
        launcher = launcher_path.read_text(encoding="utf-8")

        self.assertIn("20260527_motion_quality_v1", launcher)
        self.assertIn('title="DesktopCat"', launcher)
        self.assertIn("ProductionBatchFrameSource(DEFAULT_BATCH_ID)", launcher)
        self.assertIn("--smoke-ms", launcher)
        self.assertNotIn("Candidate Preview", launcher)

    def test_gift_build_script_creates_gift_named_exe_from_gift_launcher(self) -> None:
        script_path = ROOT / "build_gift.ps1"
        self.assertTrue(script_path.exists())
        script = script_path.read_text(encoding="utf-8")

        self.assertIn('AppName = "DesktopCatGift"', script)
        self.assertIn("gift_launcher.py", script)
        self.assertIn("20260527_motion_quality_v1", script)
        self.assertIn("return_home", script)
        self.assertIn("dist\\$AppName\\$AppName.exe", script)
        self.assertNotIn("DesktopCatCandidatePreview", script)

    def test_gift_build_script_packages_only_runtime_assets(self) -> None:
        script = (ROOT / "build_gift.ps1").read_text(encoding="utf-8")

        self.assertIn("assets\\production\\desktop_cat\\batches\\$BatchId\\clean", script)
        self.assertIn("assets\\companion_messages", script)
        self.assertIn("assets\\gift", script)
        self.assertIn("--icon", script)
        self.assertNotIn('$Root\\assets;assets', script)
        self.assertNotIn("raw", script)

    def test_gift_readme_is_partner_facing(self) -> None:
        readme_path = ROOT / "assets" / "gift" / "README_先看我.txt"
        self.assertTrue(readme_path.exists())
        text = readme_path.read_text(encoding="utf-8")

        self.assertIn("先解压", text)
        self.assertIn("DesktopCatGift.exe", text)
        self.assertIn("右键", text)
        self.assertIn("退出", text)
        self.assertNotIn("Candidate", text)

    def test_gift_launcher_uses_icon_path(self) -> None:
        self.assertTrue((ROOT / "assets" / "gift" / "desktopcat.ico").exists())

    def test_rig_candidate_menu_can_reset_position(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)

        self.assertIn("def reset_position", source)
        self.assertIn("update_position", source)
        self.assertIn("回到屏幕角落", menu_source)

    def test_reset_position_uses_jump_animation(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        reset_source = inspect.getsource(rig_app.RigDesktopCatApp.reset_position)

        self.assertIn("def animate_reset_position", source)
        self.assertIn("RESET_JUMP_STEPS", source)
        self.assertIn("RESET_JUMP_HOP_PX", source)
        self.assertIn("animate_reset_position", reset_source)

    def test_reset_position_uses_lively_sprite_action_during_motion(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        reset_source = inspect.getsource(rig_app.RigDesktopCatApp.reset_position)
        animate_source = inspect.getsource(rig_app.RigDesktopCatApp.animate_reset_position)

        self.assertIn("reset_return_action", source)
        self.assertIn("self.resetting_position = True", reset_source)
        self.assertIn("self.set_action(reset_return_action", reset_source)
        self.assertIn("self.resetting_position = False", animate_source)
        self.assertIn('self.set_action("idle"', animate_source)

    def test_reset_return_action_prefers_dedicated_return_home_animation(self) -> None:
        from desktop_cat import rig_app

        self.assertEqual("return_home", rig_app.reset_return_action(24, 1200))

    def test_resetting_position_does_not_apply_action_movement_twice(self) -> None:
        from desktop_cat import rig_app

        tick_source = inspect.getsource(rig_app.RigDesktopCatApp.tick)

        self.assertIn("not self.resetting_position", tick_source)

    def test_reset_position_motion_is_slow_enough_for_jump_frames(self) -> None:
        from desktop_cat import rig_app

        reset_motion_ms = rig_app.RESET_JUMP_STEPS * rig_app.RESET_JUMP_INTERVAL_MS
        happy_motion_ms = round(1000 / rig_app.ACTION_FPS["happy"]) * 48

        self.assertGreaterEqual(reset_motion_ms, happy_motion_ms - 120)
        self.assertGreaterEqual(rig_app.RESET_JUMP_STEPS, 40)

    def test_rig_menu_has_couple_specific_gift_interactions(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)

        self.assertIn("miss_partner", source)
        self.assertIn("tired_today", source)
        self.assertIn("我想他了", menu_source)
        self.assertIn("今天辛苦啦", menu_source)

    def test_saved_position_is_reused_when_it_is_on_screen(self) -> None:
        from desktop_cat.rig_app import saved_position_or_default

        self.assertEqual(
            (320, 240),
            saved_position_or_default({"x": 320, "y": 240}, (900, 600), (1200, 800)),
        )

    def test_saved_position_falls_back_when_it_is_off_screen(self) -> None:
        from desktop_cat.rig_app import saved_position_or_default

        self.assertEqual(
            (900, 600),
            saved_position_or_default({"x": 5000, "y": 240}, (900, 600), (1200, 800)),
        )

    def test_first_launch_delays_competing_bubbles(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        first_launch_source = inspect.getsource(rig_app.RigDesktopCatApp.show_first_launch_message)

        self.assertIn("FIRST_LAUNCH_COMPANION_DELAY_MS", source)
        self.assertIn("first_launch_pending", source)
        self.assertIn("hide_ms=9000", first_launch_source)
        self.assertIn("wave", first_launch_source)


if __name__ == "__main__":
    unittest.main()
