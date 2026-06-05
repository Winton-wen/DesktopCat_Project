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


if __name__ == "__main__":
    unittest.main()
