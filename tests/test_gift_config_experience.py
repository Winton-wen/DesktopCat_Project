from __future__ import annotations

import inspect
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

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

                self.assertEqual("呆呆", store.config.pet_name)
                self.assertEqual("麻麻", store.config.mama_nickname)
                self.assertEqual("粑粑", store.config.papa_nickname)
                self.assertEqual("麻麻", store.config.partner_nickname)
                self.assertFalse(store.config.low_distraction_mode)
                self.assertFalse(store.config.first_launch_completed)
                self.assertEqual("assets/companion_messages/partner_default.json", store.config.companion_message_pack)
                self.assertEqual("麻麻", raw["mama_nickname"])
                self.assertEqual("粑粑", raw["papa_nickname"])
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
                            "mama_nickname": {"bad": "type"},
                            "papa_nickname": 42,
                            "low_distraction_mode": "false",
                            "first_launch_completed": "true",
                            "companion_message_pack": 42,
                            "last_position": {"x": True, "y": 20},
                        }
                    ),
                    encoding="utf-8",
                )

                config = ConfigStore().config

                self.assertEqual("呆呆", config.pet_name)
                self.assertEqual("麻麻", config.mama_nickname)
                self.assertEqual("粑粑", config.papa_nickname)
                self.assertEqual("麻麻", config.partner_nickname)
                self.assertFalse(config.low_distraction_mode)
                self.assertFalse(config.first_launch_completed)
                self.assertEqual("assets/companion_messages/partner_default.json", config.companion_message_pack)
                self.assertIsNone(config.last_position)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_identity_fields_round_trip(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()
                store.config.pet_name = "团团"
                store.config.mama_nickname = "妈妈"
                store.config.papa_nickname = "爸爸"
                store.config.partner_nickname = "旧称呼"

                store.save()
                reloaded = ConfigStore().config

                self.assertEqual("团团", reloaded.pet_name)
                self.assertEqual("妈妈", reloaded.mama_nickname)
                self.assertEqual("爸爸", reloaded.papa_nickname)
                self.assertEqual("旧称呼", reloaded.partner_nickname)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_legacy_partner_nickname_migrates_to_mama_nickname(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                path = Path(temp_dir) / "config.json"
                path.write_text(
                    json.dumps({"partner_nickname": "娘亲"}, ensure_ascii=False),
                    encoding="utf-8",
                )

                config = ConfigStore().config

                self.assertEqual("娘亲", config.mama_nickname)
                self.assertEqual("娘亲", config.partner_nickname)
                self.assertEqual("粑粑", config.papa_nickname)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_old_default_names_migrate_to_shared_kitten_defaults(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                path = Path(temp_dir) / "config.json"
                path.write_text(
                    json.dumps(
                        {
                            "pet_name": "奶糖猫",
                            "partner_nickname": "宝贝",
                            "first_launch_completed": True,
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

                store = ConfigStore()
                raw = json.loads(path.read_text(encoding="utf-8"))

                self.assertEqual("呆呆", store.config.pet_name)
                self.assertEqual("麻麻", store.config.mama_nickname)
                self.assertEqual("麻麻", store.config.partner_nickname)
                self.assertEqual("呆呆", raw["pet_name"])
                self.assertEqual("麻麻", raw["mama_nickname"])
                self.assertEqual("麻麻", raw["partner_nickname"])
                self.assertTrue(store.config.first_launch_completed)
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

    def test_exit_state_round_trips(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()
                store.update_exit_state("left", 420)

                loaded = ConfigStore()

                self.assertEqual("left", loaded.config.last_exit_side)
                self.assertEqual(420, loaded.config.last_exit_y)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_exit_state_can_be_consumed_after_entry(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                store = ConfigStore()
                store.update_exit_state("right", 300)
                store.clear_exit_state()

                loaded = ConfigStore()

                self.assertIsNone(loaded.config.last_exit_side)
                self.assertIsNone(loaded.config.last_exit_y)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_invalid_exit_state_is_ignored(self) -> None:
        from desktop_cat.config import ConfigStore

        with self.with_config_dir() as temp_dir:
            old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
            os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
            try:
                path = Path(temp_dir) / "config.json"
                path.write_text(
                    json.dumps(
                        {
                            "last_exit_side": "top",
                            "last_exit_y": True,
                        }
                    ),
                    encoding="utf-8",
                )

                store = ConfigStore()

                self.assertIsNone(store.config.last_exit_side)
                self.assertIsNone(store.config.last_exit_y)
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
                self.assertIn("mama_nickname", text)
                self.assertIn("papa_nickname", text)
                self.assertIn("partner_nickname", text)
                self.assertIn("low_distraction_mode", text)
                self.assertIn("companion_message_pack", text)
                self.assertIn("partner_custom.json", text)
                self.assertIn("{pet_name}", text)
                self.assertIn("{mama_nickname}", text)
                self.assertIn("{papa_nickname}", text)
            finally:
                if old_config_dir is None:
                    os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
                else:
                    os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir

    def test_default_partner_facing_text_is_readable_chinese(self) -> None:
        from desktop_cat.config import MAMA_NICKNAME, PAPA_NICKNAME, PARTNER_NICKNAME, PET_NAME, README_TEXT
        from desktop_cat.rig_app import TEXT, low_distraction_menu_label
        from desktop_cat.time_reminders import (
            BEDTIME_REMINDER,
            DINNER_REMINDER,
            LATE_NIGHT_REMINDER,
            LUNCH_REMINDER,
        )

        readable_text = "\n".join(
            [
                PET_NAME,
                MAMA_NICKNAME,
                PAPA_NICKNAME,
                PARTNER_NICKNAME,
                README_TEXT,
                *(text for values in TEXT.values() for text in values),
                low_distraction_menu_label(False),
                low_distraction_menu_label(True),
                LUNCH_REMINDER.message,
                DINNER_REMINDER.message,
                BEDTIME_REMINDER.message,
                LATE_NIGHT_REMINDER.message,
            ]
        )

        self.assertIn("呆呆", readable_text)
        self.assertIn("麻麻", readable_text)
        self.assertNotIn("小猪猪", readable_text)
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

    def test_rig_candidate_keeps_config_file_backend_off_frontend_menu(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)

        self.assertIn("def open_config", source)
        self.assertIn("os.startfile", source)
        self.assertNotIn("打开配置文件", menu_source)

    def test_rig_candidate_keeps_config_folder_backend_off_frontend_menu(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)

        self.assertIn("def open_config_folder", source)
        self.assertIn("open_folder", source)
        self.assertNotIn("打开配置文件夹", menu_source)

    def test_rig_candidate_keeps_companion_pack_backend_off_frontend_menu(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)

        self.assertIn("def open_companion_message_pack", source)
        self.assertIn("open_companion_message_pack_file", source)
        self.assertNotIn("编辑陪伴语料", menu_source)

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

        self.assertIn("[char]0x5446", script)
        self.assertNotIn('AppName = "DesktopCatGift"', script)
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
        self.assertIn("呆呆.exe", text)
        self.assertNotIn("DesktopCatGift.exe", text)
        self.assertIn("右键", text)
        self.assertIn("退出", text)
        self.assertIn("呆呆", text)
        self.assertIn("麻麻", text)
        self.assertIn("粑粑", text)
        self.assertIn("一起养", text)
        self.assertNotIn("Candidate", text)

    def test_copywriting_catalog_matches_shared_kitten_narrative(self) -> None:
        text = (ROOT / "docs" / "copywriting-message-catalog.md").read_text(encoding="utf-8")

        self.assertIn("呆呆", text)
        self.assertIn("mama_nickname", text)
        self.assertIn("papa_nickname", text)
        self.assertIn("{pet_name}", text)
        self.assertIn("{mama_nickname}", text)
        self.assertIn("{papa_nickname}", text)
        self.assertNotIn("## E. 右键“我想他了”随机回复", text)
        self.assertNotIn("## E. “麻麻辛苦啦”随机回复", text)
        self.assertNotIn("旧版 `sprite_app.py`", text)

    def test_copywriting_catalog_is_complete_and_ready_for_manual_editing(self) -> None:
        from desktop_cat.config import DEFAULT_MESSAGES, README_TEXT
        from desktop_cat.rig_app import TEXT
        from desktop_cat.time_reminders import (
            BEDTIME_REMINDER,
            DINNER_REMINDER,
            LATE_NIGHT_REMINDER,
            LUNCH_REMINDER,
        )

        catalog = (ROOT / "docs" / "copywriting-message-catalog.md").read_text(
            encoding="utf-8"
        )
        gift_readme = (ROOT / "assets" / "gift" / "README_先看我.txt").read_text(
            encoding="utf-8"
        )
        message_pack = json.loads(
            (
                ROOT / "assets" / "companion_messages" / "partner_default.json"
            ).read_text(encoding="utf-8")
        )

        self.assertIn("修改后文案：", catalog)
        self.assertIn("修改后触发条件/时间：", catalog)
        for category_window in (
            "`morning`: 07:00-11:30",
            "`lunch`: 11:30-13:30",
            "`afternoon`: 13:30-18:00",
            "`evening`: 18:00-22:30",
            "`late_night`: 01:30-05:00",
            "`bedtime`: 其余时间",
        ):
            self.assertIn(category_window, catalog)
        for message in message_pack["messages"]:
            self.assertIn(f"`{message['id']}`", catalog)
            self.assertIn(message["text"].replace("\n", "\\n"), catalog)
        for runtime_text in (
            *(text for values in TEXT.values() for text in values),
            LUNCH_REMINDER.message,
            DINNER_REMINDER.message,
            BEDTIME_REMINDER.message,
            LATE_NIGHT_REMINDER.message,
            *DEFAULT_MESSAGES,
        ):
            self.assertIn(runtime_text.replace("\n", "\\n"), catalog)
        for menu_text in (
            "开心一下",
            "卖萌一下",
            "打个招呼",
            "向左走两步",
            "向右走两步",
            "睡一会儿",
            "呆呆安静一下",
            "不用保持安静啦",
            "回到屏幕角落",
            "退出",
        ):
            self.assertIn(menu_text, catalog)
        self.assertIn("谢谢呆呆的关心，不用再提醒啦", catalog)
        for source_text in (README_TEXT, gift_readme):
            for line in source_text.splitlines():
                if line.strip():
                    self.assertIn(line, catalog)

    def test_gift_icon_is_generated_from_full_cat_reference_with_white_background(self) -> None:
        from PIL import Image, ImageChops

        generator = ROOT / "tools" / "build_gift_icon.py"
        preview_path = ROOT / "assets" / "gift" / "desktopcat_icon_head_preview.png"
        icon_path = ROOT / "assets" / "gift" / "desktopcat.ico"

        self.assertTrue(generator.exists())
        generator_source = generator.read_text(encoding="utf-8")
        self.assertIn('"1.png"', generator_source)
        self.assertIn("reference", generator_source.lower())
        self.assertNotIn("retain_center_component", generator_source)
        self.assertTrue(preview_path.exists())

        with Image.open(preview_path) as preview:
            self.assertEqual((512, 512), preview.size)
            self.assertEqual("RGBA", preview.mode)
            alpha = preview.getchannel("A")
            self.assertEqual((0, 0, 512, 512), alpha.getbbox())
            self.assertEqual((255, 255), alpha.getextrema())
            for point in ((0, 0), (511, 0), (0, 511), (511, 511)):
                red, green, blue, opacity = preview.getpixel(point)
                self.assertGreaterEqual(red, 240)
                self.assertGreaterEqual(green, 240)
                self.assertGreaterEqual(blue, 240)
                self.assertEqual(255, opacity)

            background_color = preview.convert("RGB").getpixel((0, 0))
            background = Image.new("RGB", preview.size, background_color)
            difference = ImageChops.difference(preview.convert("RGB"), background)
            foreground_mask = difference.convert("L").point(
                lambda value: 255 if value >= 15 else 0
            )
            content_box = foreground_mask.getbbox()
            self.assertIsNotNone(content_box)
            self.assertGreaterEqual(content_box[3] - content_box[1], 440)

        with Image.open(icon_path) as icon:
            self.assertEqual(
                {(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)},
                icon.info["sizes"],
            )

    def test_target_machine_acceptance_checklist_covers_manual_gift_handoff(self) -> None:
        checklist_path = ROOT / "docs" / "target-machine-acceptance-checklist.md"
        self.assertTrue(checklist_path.exists())
        text = checklist_path.read_text(encoding="utf-8")

        for required in [
            "首次启动",
            "右键菜单",
            "拖拽",
            "回到屏幕角落",
            "退出",
            "中文 UI",
            "DesktopCatGift_20260613_final.zip",
        ]:
            self.assertIn(required, text)

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

    def test_rig_copy_matches_family_companion_voice(self) -> None:
        from desktop_cat import rig_app

        rendered = {
            key: [
                rig_app.render_companion_text(
                    text,
                    pet_name="呆呆",
                    mama_nickname="麻麻",
                    papa_nickname="粑粑",
                )
                for text in values
            ]
            for key, values in rig_app.TEXT.items()
        }
        self.assertEqual(
            {
                "pet": [
                    "喜欢麻麻摸我的头៷>ᴗ<៷",
                    "哎呀呀好痒呀好痒呀！",
                    "喵喵喵꜀(^. .^꜀  )꜆੭",
                ],
                "happy": ["麻麻看，呆呆跳一下！", "(*^ω^*)开心", "cchh，嘟嘟哒哒⌯ᵔᗜᵔ⌯"],
                "cute": [
                    "麻麻看呆呆可爱嘛",
                    "呆呆最最最喜欢麻麻啦˶>ᗜ<˶",
                    "真的不和呆呆玩一下嘛ₒ⦁⩊⦁ₒ",
                ],
                "wave": ["麻麻，看这里呀。", "你好呀，我是呆呆~"],
                "sleep": ["ᶻz ₍^_ ̫ _^₎"],
                "wake": ["呆呆醒啦՞･∞･՞"],
                "walk_left": ["天才在左。"],
                "walk_right": ["疯子在右。"],
            },
            rendered,
        )

    def test_rig_menu_removes_missing_partner_interaction(self) -> None:
        from desktop_cat import rig_app

        module_source = inspect.getsource(rig_app)
        source = inspect.getsource(rig_app.RigDesktopCatApp)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)

        self.assertNotIn("MISS_PARTNER_MESSAGES", module_source)
        self.assertNotIn("miss_partner", source)
        self.assertNotIn("我想他了", menu_source)

    def test_rig_menu_removes_mama_tired_interaction_and_shortens_bubbles(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)

        self.assertNotIn("tired_today", source)
        self.assertNotIn("TIRED_TODAY_MESSAGES", inspect.getsource(rig_app))
        self.assertNotIn("麻麻辛苦啦", menu_source)
        self.assertEqual(3000, rig_app.SHORT_BUBBLE_HIDE_MS)
        self.assertEqual(10000, rig_app.FIRST_LAUNCH_HIDE_MS)
        self.assertEqual(15000, rig_app.TIME_REMINDER_HIDE_MS)
        self.assertEqual(3000, rig_app.COMPANION_MESSAGE_HIDE_MS)

    def test_rig_menu_binds_task3_commands_without_tk(self) -> None:
        from desktop_cat import rig_app

        class FakeMenu:
            instances: list["FakeMenu"] = []

            def __init__(self, root, tearoff: int) -> None:
                self.root = root
                self.tearoff = tearoff
                self.commands: list[tuple[str, object]] = []
                self.popup_position: tuple[int, int] | None = None
                self.instances.append(self)

            def add_command(self, *, label: str, command) -> None:
                self.commands.append((label, command))

            def add_separator(self) -> None:
                pass

            def tk_popup(self, x: int, y: int) -> None:
                self.popup_position = (x, y)

        class Config:
            low_distraction_mode = False

        class Store:
            config = Config()

        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.root = object()
        app.store = Store()
        handlers = {
            name: (lambda handler_name=name: handler_name)
            for name in (
                "happy",
                "cute",
                "wave",
                "walk_left",
                "walk_right",
                "sleep",
                "toggle_low_distraction_mode",
                "reset_position",
                "begin_exit",
                "quit",
            )
        }
        for name, handler in handlers.items():
            setattr(app, name, handler)
        event = type("Event", (), {"x_root": 120, "y_root": 240})()

        with patch.object(rig_app, "Menu", FakeMenu):
            app.on_menu(event)

        menu = FakeMenu.instances[0]
        commands = dict(menu.commands)
        self.assertIs(commands["呆呆安静一下"], handlers["toggle_low_distraction_mode"])
        self.assertIs(commands["退出"], handlers["begin_exit"])
        self.assertNotIn("打开配置文件", commands)
        self.assertNotIn("打开配置文件夹", commands)
        self.assertNotIn("编辑陪伴语料", commands)
        self.assertNotIn("我想他了", commands)
        self.assertNotIn("麻麻辛苦啦", commands)
        self.assertEqual((120, 240), menu.popup_position)

    def test_rig_menu_is_disabled_during_entry_and_exit(self) -> None:
        from desktop_cat import rig_app

        event = type("Event", (), {"x_root": 120, "y_root": 240})()
        for entering, exiting in ((True, False), (False, True)):
            with self.subTest(entering=entering, exiting=exiting):
                app = rig_app.RigDesktopCatApp.__new__(
                    rig_app.RigDesktopCatApp
                )
                app.entering = entering
                app.exiting = exiting
                with patch.object(
                    rig_app,
                    "Menu",
                    side_effect=AssertionError("menu must stay closed"),
                ):
                    app.on_menu(event)

    def test_first_launch_welcome_uses_all_three_identity_fields(self) -> None:
        from desktop_cat import rig_app

        class Config:
            pet_name = "团团"
            mama_nickname = "妈妈"
            papa_nickname = "爸爸"

        class Store:
            config = Config()

            def mark_first_launch_completed(self) -> None:
                completion_marks.append(True)

        shown: list[tuple[str, tuple[int, int], int]] = []
        actions: list[tuple[str, float, bool]] = []
        completion_marks: list[bool] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.store = Store()
        app.test_first_launch = False
        app.first_launch_pending = True
        app.pet_anchor = lambda: (320, 240)
        app.set_action = lambda action, seconds, force=False: actions.append((action, seconds, force))
        app.bubble = type(
            "Bubble",
            (),
            {"show": lambda _self, text, x, y, hide_ms: shown.append((text, (x, y), hide_ms))},
        )()

        app.show_first_launch_message()

        self.assertEqual([("wave", 2.2, True)], actions)
        self.assertEqual(
            [("团团来啦！我以后就是妈妈的桌面小猫啦", (320, 240), 10000)],
            shown,
        )
        self.assertFalse(app.first_launch_pending)
        self.assertEqual([True], completion_marks)

    def test_current_welcome_is_pending_for_legacy_completed_config(self) -> None:
        from desktop_cat.config import CatConfig
        from desktop_cat.rig_app import first_launch_welcome_is_pending

        config = CatConfig(first_launch_completed=True)

        self.assertTrue(first_launch_welcome_is_pending(config))

    def test_current_welcome_is_not_pending_after_version_is_recorded(self) -> None:
        from desktop_cat.config import CatConfig, WELCOME_VERSION
        from desktop_cat.rig_app import first_launch_welcome_is_pending

        config = CatConfig(
            first_launch_completed=True,
            welcome_version=WELCOME_VERSION,
        )

        self.assertFalse(first_launch_welcome_is_pending(config))

    def test_mark_first_launch_completed_persists_current_welcome_version(self) -> None:
        from desktop_cat.config import ConfigStore, WELCOME_VERSION

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                os.environ,
                {"DESKTOPCAT_CONFIG_DIR": temp_dir},
                clear=False,
            ):
                store = ConfigStore()
                store.mark_first_launch_completed()
                loaded = ConfigStore()

        self.assertTrue(loaded.config.first_launch_completed)
        self.assertEqual(WELCOME_VERSION, loaded.config.welcome_version)

    def test_first_launch_preview_does_not_persist_completion(self) -> None:
        from desktop_cat import rig_app

        class Config:
            pet_name = "团团"
            mama_nickname = "妈妈"
            papa_nickname = "爸爸"

        completion_marks: list[bool] = []

        class Store:
            config = Config()

            def mark_first_launch_completed(self) -> None:
                completion_marks.append(True)

        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.store = Store()
        app.test_first_launch = True
        app.first_launch_pending = True
        app.pet_anchor = lambda: (320, 240)
        app.set_action = lambda *_args, **_kwargs: True
        app.bubble = type("Bubble", (), {"show": lambda *_args, **_kwargs: None})()

        app.show_first_launch_message()

        self.assertEqual([], completion_marks)
        self.assertFalse(app.first_launch_pending)

    def test_low_distraction_toggle_uses_companion_copy(self) -> None:
        from desktop_cat import rig_app

        class Config:
            low_distraction_mode = False

        class Store:
            config = Config()

            def update_low_distraction_mode(self, enabled: bool) -> None:
                self.config.low_distraction_mode = enabled

        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.store = Store()
        messages: list[str] = []
        app.say_unbound = messages.append

        app.toggle_low_distraction_mode()
        app.toggle_low_distraction_mode()

        self.assertEqual(
            [
                "{pet_name}会乖乖安静地陪着{mama_nickname}\n꜀(^. .^꜀  )꜆੭",
                "呆呆要和麻麻玩！",
            ],
            messages,
        )

    def test_custom_identity_fields_render_across_runtime_message_paths(self) -> None:
        from desktop_cat import rig_app

        class Config:
            pet_name = "团团"
            mama_nickname = "妈妈"
            papa_nickname = "爸爸"
            low_distraction_mode = False

        class Store:
            config = Config()

            def update_low_distraction_mode(self, enabled: bool) -> None:
                self.config.low_distraction_mode = enabled

        shown: list[tuple[str, dict[str, object]]] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.store = Store()
        app.pet_anchor = lambda: (320, 240)
        app.set_action = lambda *_args, **_kwargs: True
        app.bubble = type(
            "Bubble",
            (),
            {
                "show": lambda _self, text, *_args, **kwargs: shown.append(
                    (text, kwargs)
                )
            },
        )()
        app.root = type("Root", (), {"after": lambda *_args: None})()
        app.time_reminders_last_shown_at = {}
        app.time_reminders_dismissed = set()

        app.say("{mama_nickname}看，{pet_name}跳一下！")
        app.show_gift_interaction(
            "{mama_nickname}辛苦啦，{pet_name}和{papa_nickname}都关心你。"
        )
        app.check_time_reminder(datetime(2026, 6, 6, 12, 0))

        self.assertEqual(
            [
                "妈妈看，团团跳一下！",
                "妈妈辛苦啦，团团和爸爸都关心你。",
                "妈妈要记得按时吃午饭呀，不然呆呆和粑粑都会担心的喔՞･∞･՞",
            ],
            [text for text, _kwargs in shown],
        )

    def test_sleeping_skips_fixed_time_reminders_without_marking_them(self) -> None:
        from desktop_cat import rig_app

        for action in ("sleep_in", "sleep"):
            with self.subTest(action=action):
                shown: list[object] = []
                scheduled: list[int] = []
                app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
                app.action = action
                app.root = type(
                    "Root",
                    (),
                    {"after": lambda _self, delay, _callback: scheduled.append(delay)},
                )()
                app.time_reminders_last_shown_at = {}
                app.time_reminders_dismissed = set()
                app.render_text = lambda text: text
                app.pet_anchor = lambda: (10, 20)
                app.bubble = type(
                    "Bubble",
                    (),
                    {"show": lambda *_args, **_kwargs: shown.append(True)},
                )()

                app.check_time_reminder(datetime(2026, 6, 14, 12, 0))

                self.assertEqual([], shown)
                self.assertEqual({}, app.time_reminders_last_shown_at)
                self.assertEqual([rig_app.TIME_REMINDER_CHECK_MS], scheduled)

    def test_rejected_gift_interaction_does_not_show_bubble(self) -> None:
        from desktop_cat import rig_app

        shown: list[object] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.set_action = lambda *_args, **_kwargs: False
        app.render_text = lambda text: text
        app.pet_anchor = lambda: (20, 30)
        app.bubble = type(
            "Bubble",
            (),
            {"show": lambda *_args, **_kwargs: shown.append(True)},
        )()

        app.show_gift_interaction("ignored", action="cute")

        self.assertEqual([], shown)

    def test_reset_completion_and_quit_menu_use_final_copy(self) -> None:
        from desktop_cat import rig_app

        animate_source = inspect.getsource(rig_app.RigDesktopCatApp.animate_reset_position)
        menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)

        self.assertIn("{pet_name}跳回屏幕角落啦。", animate_source)
        self.assertIn("self.render_text", animate_source)
        self.assertIn('label="退出"', menu_source)
        self.assertNotIn("退出 rig 预览", menu_source)

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
        self.assertIn("hide_ms=FIRST_LAUNCH_HIDE_MS", first_launch_source)
        self.assertEqual(10000, rig_app.FIRST_LAUNCH_HIDE_MS)
        self.assertIn("wave", first_launch_source)


if __name__ == "__main__":
    unittest.main()
