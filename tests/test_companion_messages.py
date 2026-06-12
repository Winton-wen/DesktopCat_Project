from __future__ import annotations

import inspect
import json
import re
import sys
import tempfile
import unittest
from datetime import datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class CompanionMessageTests(unittest.TestCase):
    def test_render_companion_text_replaces_supported_placeholders(self) -> None:
        from desktop_cat.companion_messages import render_companion_text

        rendered = render_companion_text(
            "{pet_name} likes {mama_nickname} and {papa_nickname}.",
            pet_name="Mimi",
            mama_nickname="Mama",
            papa_nickname="Papa",
        )

        self.assertEqual("Mimi likes Mama and Papa.", rendered)

    def test_render_companion_text_does_not_render_tokens_inserted_from_config(self) -> None:
        from desktop_cat.companion_messages import render_companion_text

        rendered = render_companion_text(
            "{pet_name}",
            pet_name="{mama_nickname}",
            mama_nickname="Mama",
            papa_nickname="Papa",
        )

        self.assertEqual("{mama_nickname}", rendered)

    def test_render_companion_text_preserves_supported_token_in_double_braces(self) -> None:
        from desktop_cat.companion_messages import render_companion_text

        rendered = render_companion_text(
            "{{pet_name}}",
            pet_name="Mimi",
            mama_nickname="Mama",
            papa_nickname="Papa",
        )

        self.assertEqual("{{pet_name}}", rendered)

    def test_render_companion_text_replaces_adjacent_supported_tokens(self) -> None:
        from desktop_cat.companion_messages import render_companion_text

        rendered = render_companion_text(
            "{pet_name}{mama_nickname}{papa_nickname}",
            pet_name="Mimi",
            mama_nickname="Mama",
            papa_nickname="Papa",
        )

        self.assertEqual("MimiMamaPapa", rendered)

    def test_render_companion_text_preserves_unknown_placeholders(self) -> None:
        from desktop_cat.companion_messages import render_companion_text

        rendered = render_companion_text(
            "Hello, {unknown_name}.",
            pet_name="Mimi",
            mama_nickname="Mama",
            papa_nickname="Papa",
        )

        self.assertEqual("Hello, {unknown_name}.", rendered)

    def test_render_companion_text_returns_original_for_unmatched_braces(self) -> None:
        from desktop_cat.companion_messages import render_companion_text

        text = "Hello, {pet_name"

        rendered = render_companion_text(
            text,
            pet_name="Mimi",
            mama_nickname="Mama",
            papa_nickname="Papa",
        )

        self.assertEqual(text, rendered)

    def test_render_companion_text_preserves_non_literal_format_fields(self) -> None:
        from desktop_cat.companion_messages import render_companion_text

        texts = [
            "{unknown}",
            "{unknown.attr}",
            "{unknown[0]}",
            "{unknown!r}",
            "{pet_name[0]}",
            "{pet_name!r}",
            "{pet_name:>12}",
        ]

        for text in texts:
            with self.subTest(text=text):
                rendered = render_companion_text(
                    text,
                    pet_name="Mimi",
                    mama_nickname="Mama",
                    papa_nickname="Papa",
                )

                self.assertEqual(text, rendered)

    def test_render_companion_text_preserves_literal_and_unmatched_braces(self) -> None:
        from desktop_cat.companion_messages import render_companion_text

        texts = [
            "{{literal braces}}",
            "left { brace",
            "right } brace",
        ]

        for text in texts:
            with self.subTest(text=text):
                rendered = render_companion_text(
                    text,
                    pet_name="Mimi",
                    mama_nickname="Mama",
                    papa_nickname="Papa",
                )

                self.assertEqual(text, rendered)

    def test_default_partner_message_pack_has_core_categories(self) -> None:
        from desktop_cat.companion_messages import load_companion_pack

        pack = load_companion_pack(ROOT / "assets" / "companion_messages" / "partner_default.json")
        categories = {message.category for message in pack.messages}

        self.assertTrue({"morning", "lunch", "evening", "bedtime", "miss_you", "busy_support"}.issubset(categories))
        self.assertTrue(all(message.text.strip() for message in pack.messages))
        self.assertTrue(all(1 <= message.cooldown_hours <= 72 for message in pack.messages))

    def test_default_partner_message_pack_preserves_metadata_snapshot(self) -> None:
        path = ROOT / "assets" / "companion_messages" / "partner_default.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        messages = payload["messages"]

        expected_metadata = [
            ("morning_01", "morning", 24, "wave", None),
            ("morning_02", "morning", 24, "cute", None),
            ("lunch_01", "lunch", 12, "wave", None),
            ("afternoon_01", "afternoon", 18, "cute", None),
            ("evening_01", "evening", 18, "happy", None),
            ("bedtime_01", "bedtime", 12, "sleep", None),
            ("late_night_01", "late_night", 12, "sleep", None),
            ("miss_you_01", "miss_you", 36, "wave", None),
            ("busy_support_01", "busy_support", 24, "blink", None),
            ("comfort_01", "comfort", 36, "cute", None),
            ("comfort_02", "comfort", 36, "cute", None),
            ("comfort_03", "comfort", 36, "cute", None),
            ("encouragement_01", "encouragement", 36, "happy", None),
            ("encouragement_02", "encouragement", 36, "happy", None),
            ("special_anniversary_0324", "special_day", 72, "happy", "03-24"),
            ("special_valentine_0214", "special_day", 72, "happy", "02-14"),
            ("special_love_day_0520", "special_day", 72, "cute", "05-20"),
            ("special_labor_day_0501", "special_day", 72, "wave", "05-01"),
            ("special_papa_birthday_0912", "special_day", 72, "happy", "09-12"),
            ("special_mama_birthday_1022", "special_day", 72, "happy", "10-22"),
            ("special_national_day_1001", "special_day", 72, "wave", "10-01"),
            ("special_christmas_1225", "special_day", 72, "cute", "12-25"),
            ("special_year_end_1231", "special_day", 72, "wave", "12-31"),
            ("special_new_year_0101", "special_day", 72, "wave", "01-01"),
            ("special_spring_festival", "special_day", 72, "happy", None),
            ("special_lantern_festival", "special_day", 72, "cute", None),
            ("special_dragon_boat", "special_day", 72, "wave", None),
            ("special_qixi", "special_day", 72, "cute", None),
            ("special_mid_autumn", "special_day", 72, "happy", None),
            ("special_double_ninth", "special_day", 72, "wave", None),
        ]
        actual_metadata = [
            (
                message["id"],
                message["category"],
                message["cooldown_hours"],
                message["action"],
                message.get("month_day"),
            )
            for message in messages
        ]

        self.assertEqual(expected_metadata, actual_metadata)

    def test_default_partner_message_pack_uses_exact_narrative_by_id(self) -> None:
        path = ROOT / "assets" / "companion_messages" / "partner_default.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        messages = payload["messages"]
        expected_text_by_id = {
            "morning_01": "早上好呀{mama_nickname}！{pet_name}来陪你开启新的一天啦꜀(^. .^꜀  )꜆੭",
            "morning_02": "{mama_nickname}先伸个懒腰吧，{pet_name}也要醒醒啦₍ᵔ･•･ᵔ₎",
            "lunch_01": "{mama_nickname}要好好吃午饭呀，{pet_name}会帮粑粑认真监督你的喔",
            "afternoon_01": "{mama_nickname}下午也辛苦啦，累了的话就和{pet_name}一起发一会儿呆吧₍ᵔ･•･ᵔ₎",
            "evening_01": "{mama_nickname}辛苦一天啦，{pet_name}来贴贴你\n꜀(^. .^꜀  )꜆੭",
            "bedtime_01": "很晚啦，{pet_name}想和{mama_nickname}一起早点睡觉呀ᶻz ₍^_ ̫ _^₎",
            "late_night_01": (
                "{mama_nickname}还没睡嘛，{pet_name}好心疼{mama_nickname}\n"
                "(｡í _ ì｡)，{mama_nickname}忙完就早点休息吧。"
            ),
            "miss_you_01": (
                "{pet_name}也想{papa_nickname}啦。"
                "等以后住在一起，我们就能天天在一个家里啦。"
            ),
            "busy_support_01": (
                "{mama_nickname}先忙啵，{pet_name}会安安静静待在这里。"
            ),
            "comfort_01": (
                "事情不顺利也没关系，{pet_name}会一直陪伴{mama_nickname}呀，"
                "有什么不开心的事情可以和粑粑说呀。"
            ),
            "comfort_02": "{mama_nickname}今天辛苦啦，先摸摸{pet_name}好好放松一下吧₍⑅ᐢ..ᐢ₎",
            "comfort_03": "忙完这一阵就休息一会儿吧，{pet_name}在这里陪{mama_nickname}哟՞･∞･՞",
            "encouragement_01": "今天已经做得很好啦，{mama_nickname}的努力{pet_name}都看见了喔ₒ⦁⩊⦁ₒ",
            "encouragement_02": "{mama_nickname}已经很努力啦。喝点水，今晚也要对自己温柔一点呀⌯ᵔᗜᵔ⌯",
            "special_anniversary_0324": (
                "今天是{mama_nickname}和{papa_nickname}在一起的"
                "{anniversary_year_cn}周年纪念日，希望{mama_nickname}"
                "{papa_nickname}和{pet_name}可以永远在一起呀˶>ᗜ<˶"
            ),
            "special_valentine_0214": (
                "{mama_nickname}情人节快乐呀！{pet_name}想看{mama_nickname}和{papa_nickname}亲亲¯꒳¯"
            ),
            "special_love_day_0520": (
                "{mama_nickname}520快乐呀！{pet_name}和{papa_nickname}都爱{mama_nickname}呀៷>ᴗ<៷"
            ),
            "special_labor_day_0501": "{mama_nickname}劳动节快乐呀，{pet_name}眼中的{mama_nickname}是全世界最勤劳滴(๓´˘`๓)",
            "special_papa_birthday_0912": "今天是{papa_nickname}的生日耶！{pet_name}想和{mama_nickname}一起给{papa_nickname}买蛋糕៷>ᴗ<៷",
            "special_mama_birthday_1022": "{mama_nickname}生日快乐呀！希望{mama_nickname}以后也要天天开心呀˶>ᗜ<˶",
            "special_national_day_1001": "{mama_nickname}国庆快乐呀，终于可以休息一段时间啦꜀(^. .^꜀  )꜆੭",
            "special_christmas_1225": "{mama_nickname}圣诞快乐呀，{pet_name}想把小铃铛摇给{mama_nickname}听₍ᵔ･•･ᵔ₎",
            "special_year_end_1231": (
                "{pet_name}已经忍不住期待和{mama_nickname}{papa_nickname}一起走进新的一年啦˶>ᗜ<˶"
            ),
            "special_new_year_0101": "{mama_nickname}新年快乐呀，{pet_name}今年也要一直陪着{mama_nickname}和{papa_nickname}(๓´˘`๓)",
            "special_spring_festival": "{mama_nickname}春节快乐呀，{pet_name}要陪{mama_nickname}和{papa_nickname}一起过年˶>ᗜ<˶",
            "special_lantern_festival": "{mama_nickname}元宵节快乐呀，{pet_name}想和{mama_nickname}一起吃甜甜的汤圆(*^ω^*)",
            "special_dragon_boat": "{mama_nickname}端午安康呀，{pet_name}今天也要乖乖陪{mama_nickname}꜀(^. .^꜀  )꜆੭",
            "special_qixi": "{mama_nickname}七夕快乐呀，{pet_name}要用乐高积木帮{mama_nickname}和{papa_nickname}搭鹊桥¯꒳¯",
            "special_mid_autumn": "{mama_nickname}中秋快乐呀，{pet_name}想陪{mama_nickname}和{papa_nickname}一起看月亮՞･∞･՞",
            "special_double_ninth": "重阳节到啦，{pet_name}提醒{mama_nickname}今天也要照顾好自己呀(๓´˘`๓)",
        }

        self.assertEqual(expected_text_by_id, {message["id"]: message["text"] for message in messages})

    def test_default_partner_message_pack_has_valid_special_day_schema(self) -> None:
        from desktop_cat.companion_messages import load_companion_pack

        pack = load_companion_pack(ROOT / "assets" / "companion_messages" / "partner_default.json")
        message_ids = [message.id for message in pack.messages]
        special_month_days = []
        special_lunar_days = []

        self.assertEqual(len(message_ids), len(set(message_ids)))
        for message in pack.messages:
            with self.subTest(message_id=message.id):
                if message.category == "special_day":
                    self.assertTrue(message.month_day or message.lunar_month_day)
                    if message.month_day:
                        self.assertRegex(message.month_day, re.compile(r"\d{2}-\d{2}"))
                        datetime.strptime(message.month_day, "%m-%d")
                        special_month_days.append(message.month_day)
                    if message.lunar_month_day:
                        self.assertRegex(message.lunar_month_day, re.compile(r"\d{2}-\d{2}"))
                        special_lunar_days.append(message.lunar_month_day)
                else:
                    self.assertIsNone(message.month_day)
                    self.assertIsNone(message.lunar_month_day)

        self.assertEqual(len(special_month_days), len(set(special_month_days)))
        self.assertEqual(len(special_lunar_days), len(set(special_lunar_days)))

    def test_default_partner_message_pack_uses_all_supported_placeholders(self) -> None:
        path = ROOT / "assets" / "companion_messages" / "partner_default.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        narrative = "\n".join(message["text"] for message in payload["messages"])

        for placeholder in ("{pet_name}", "{mama_nickname}", "{papa_nickname}"):
            with self.subTest(placeholder=placeholder):
                self.assertIn(placeholder, narrative)

    def test_default_partner_message_pack_avoids_first_person_partner_narrative(self) -> None:
        path = ROOT / "assets" / "companion_messages" / "partner_default.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        narrative = "\n".join(message["text"] for message in payload["messages"])

        for forbidden_text in ("替我", "当我抱你", "我一直站在你这边"):
            with self.subTest(forbidden_text=forbidden_text):
                self.assertNotIn(forbidden_text, narrative)

    def test_companion_category_for_time_matches_daily_rhythm(self) -> None:
        from desktop_cat.companion_messages import companion_category_for_time

        self.assertEqual("morning", companion_category_for_time(time(8, 30)))
        self.assertEqual("lunch", companion_category_for_time(time(12, 10)))
        self.assertEqual("afternoon", companion_category_for_time(time(15, 30)))
        self.assertEqual("evening", companion_category_for_time(time(20, 30)))
        self.assertEqual("bedtime", companion_category_for_time(time(23, 40)))
        self.assertEqual("late_night", companion_category_for_time(time(2, 30)))

    def test_companion_message_is_due_after_cooldown_only(self) -> None:
        from desktop_cat.companion_messages import CompanionMessage, companion_message_is_due

        message = CompanionMessage(
            id="evening_01",
            category="evening",
            text="今天辛苦啦。",
            cooldown_hours=12,
            action="wave",
        )
        current = datetime(2026, 6, 4, 20, 0)
        key = "evening_01"

        self.assertTrue(companion_message_is_due(current, message, {}))
        self.assertFalse(companion_message_is_due(current + timedelta(hours=11, minutes=59), message, {key: current}))
        self.assertTrue(companion_message_is_due(current + timedelta(hours=12), message, {key: current}))

    def test_select_companion_message_prefers_current_time_category(self) -> None:
        from desktop_cat.companion_messages import CompanionMessage, select_companion_message

        messages = [
            CompanionMessage(id="morning_01", category="morning", text="早上好。", cooldown_hours=12, action="wave"),
            CompanionMessage(id="evening_01", category="evening", text="辛苦啦。", cooldown_hours=12, action="cute"),
        ]
        selected = select_companion_message(datetime(2026, 6, 4, 20, 0), messages, {})

        self.assertIsNotNone(selected)
        self.assertEqual("evening_01", selected.id)
        self.assertEqual("cute", selected.action)

    def test_select_companion_message_mixes_current_time_and_general_messages(self) -> None:
        from desktop_cat import companion_messages
        from desktop_cat.companion_messages import CompanionMessage, select_companion_message

        messages = [
            CompanionMessage(
                id="evening_01",
                category="evening",
                text="辛苦啦。",
                cooldown_hours=12,
                action="cute",
            ),
            CompanionMessage(
                id="comfort_01",
                category="comfort",
                text="先休息一下吧。",
                cooldown_hours=12,
                action="wave",
            ),
            CompanionMessage(
                id="morning_01",
                category="morning",
                text="早上好。",
                cooldown_hours=12,
                action="wave",
            ),
        ]
        captured_candidates: list[list[str]] = []

        def choose(candidates):
            captured_candidates.append([message.id for message in candidates])
            return candidates[-1]

        with patch.object(companion_messages.random, "choice", side_effect=choose):
            selected = select_companion_message(
                datetime(2026, 6, 4, 20, 0),
                messages,
                {},
            )

        self.assertEqual([["evening_01", "comfort_01"]], captured_candidates)
        self.assertEqual("comfort_01", selected.id)

    def test_anniversary_message_renders_year_count_from_system_year(self) -> None:
        from desktop_cat.companion_messages import render_companion_text

        template = (
            "今天是{mama_nickname}和{papa_nickname}在一起的"
            "{anniversary_year_cn}周年纪念日，希望{mama_nickname}"
            "{papa_nickname}和{pet_name}可以永远在一起呀˶>ᗜ<˶"
        )

        self.assertEqual(
            "今天是麻麻和粑粑在一起的二周年纪念日，希望麻麻粑粑和呆呆可以永远在一起呀˶>ᗜ<˶",
            render_companion_text(
                template,
                pet_name="呆呆",
                mama_nickname="麻麻",
                papa_nickname="粑粑",
                current=datetime(2026, 3, 24, 12, 0),
            ),
        )
        self.assertEqual(
            "今天是麻麻和粑粑在一起的三周年纪念日，希望麻麻粑粑和呆呆可以永远在一起呀˶>ᗜ<˶",
            render_companion_text(
                template,
                pet_name="呆呆",
                mama_nickname="麻麻",
                papa_nickname="粑粑",
                current=datetime(2027, 3, 24, 12, 0),
            ),
        )

    def test_select_companion_message_prioritizes_matching_special_day(self) -> None:
        from desktop_cat.companion_messages import CompanionMessage, select_companion_message

        messages = [
            CompanionMessage(
                id="evening_01",
                category="evening",
                text="今天辛苦啦。",
                cooldown_hours=12,
                action="cute",
            ),
            CompanionMessage(
                id="special_anniversary_0101",
                category="special_day",
                text="今天是我们的小日子。",
                cooldown_hours=72,
                action="happy",
                month_day="01-01",
            ),
        ]

        selected = select_companion_message(datetime(2026, 1, 1, 20, 0), messages, {})

        self.assertIsNotNone(selected)
        self.assertEqual("special_anniversary_0101", selected.id)
        self.assertEqual("happy", selected.action)

    def test_select_companion_message_prioritizes_matching_lunar_special_day(self) -> None:
        from desktop_cat.companion_messages import CompanionMessage, select_companion_message

        messages = [
            CompanionMessage(
                id="evening_01",
                category="evening",
                text="今天辛苦啦。",
                cooldown_hours=12,
                action="cute",
            ),
            CompanionMessage(
                id="special_mid_autumn",
                category="special_day",
                text="中秋快乐。",
                cooldown_hours=72,
                action="happy",
                lunar_month_day="08-15",
            ),
        ]

        selected = select_companion_message(datetime(2026, 9, 25, 20, 0), messages, {})

        self.assertIsNotNone(selected)
        self.assertEqual("special_mid_autumn", selected.id)

    def test_default_partner_message_pack_includes_editable_special_day_templates(self) -> None:
        from desktop_cat.companion_messages import load_companion_pack

        pack = load_companion_pack(ROOT / "assets" / "companion_messages" / "partner_default.json")
        special_days = [message for message in pack.messages if message.category == "special_day"]

        self.assertGreaterEqual(len(special_days), 3)
        self.assertTrue(all(message.month_day or message.lunar_month_day for message in special_days))

    def test_candidate_launcher_has_companion_message_preview_mode(self) -> None:
        launcher = (ROOT / "candidate_launcher.py").read_text(encoding="utf-8")

        self.assertIn("--test-companion-time", launcher)
        self.assertIn("check_companion_message(args.test_companion_time)", launcher)

    def test_empty_companion_message_pack_is_rejected(self) -> None:
        from desktop_cat.companion_messages import load_companion_pack

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "empty_companion_pack.json"
            path.write_text('{"messages": []}', encoding="utf-8")

            with self.assertRaises(ValueError):
                load_companion_pack(path)

    def test_invalid_companion_message_pack_is_rejected(self) -> None:
        from desktop_cat.companion_messages import load_companion_pack

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "invalid_companion_pack.json"
            path.write_text('{"messages": [{"id": "broken"}]}', encoding="utf-8")

            with self.assertRaises(ValueError):
                load_companion_pack(path)

    def test_rig_app_has_companion_message_runtime_flow(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        show_source = inspect.getsource(rig_app.RigDesktopCatApp.show_companion_message)
        self.assertIn("load_default_companion_pack", source)
        self.assertIn("check_companion_message", source)
        self.assertIn("show_companion_message", source)
        self.assertIn("self.render_text", show_source)
        render_source = inspect.getsource(rig_app.RigDesktopCatApp.render_text)
        self.assertIn("render_companion_text", render_source)
        self.assertIn("self.store.config.pet_name", render_source)
        self.assertIn("self.store.config.mama_nickname", render_source)
        self.assertIn("self.store.config.papa_nickname", render_source)

    def test_show_companion_message_renders_text_without_tk_and_preserves_message(self) -> None:
        from desktop_cat.rig_app import CompanionMessage, RigDesktopCatApp

        action_calls: list[tuple[str, float]] = []
        bubble_calls: list[tuple[str, int, int, int]] = []

        class FakeBubble:
            def show(self, text: str, x: int, y: int, *, hide_ms: int) -> None:
                bubble_calls.append((text, x, y, hide_ms))

        app = RigDesktopCatApp.__new__(RigDesktopCatApp)
        app.store = SimpleNamespace(
            config=SimpleNamespace(
                pet_name="Mimi",
                mama_nickname="Mama",
                papa_nickname="Papa",
            )
        )
        app.bubble = FakeBubble()
        app.set_action = lambda action, duration: action_calls.append((action, duration))
        app.pet_anchor = lambda: (17, 29)
        message = CompanionMessage(
            id="sleep_01",
            category="bedtime",
            text="{pet_name} says goodnight to {mama_nickname} and {papa_nickname}.",
            cooldown_hours=12,
            action="sleep",
        )
        original_message = message

        app.show_companion_message(message)

        self.assertEqual([("sleep_in", 2.4)], action_calls)
        self.assertEqual(
            [("Mimi says goodnight to Mama and Papa.", 17, 29, 3000)],
            bubble_calls,
        )
        self.assertIs(original_message, message)
        self.assertEqual(
            "{pet_name} says goodnight to {mama_nickname} and {papa_nickname}.",
            message.text,
        )

    def test_low_distraction_mode_skips_automatic_companion_messages(self) -> None:
        from desktop_cat import rig_app

        scheduled: list[int] = []
        shown: list[object] = []
        app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
        app.store = SimpleNamespace(config=SimpleNamespace(low_distraction_mode=True))
        app.root = SimpleNamespace(after=lambda delay, _callback: scheduled.append(delay))
        app.companion_pack = SimpleNamespace(messages=[])
        app.companion_messages_last_shown_at = {}
        app.show_companion_message = shown.append

        with patch.object(
            rig_app,
            "select_companion_message",
            side_effect=AssertionError("selection should be skipped"),
        ):
            app.check_companion_message(datetime(2026, 6, 4, 20, 0))

        self.assertEqual([], shown)
        self.assertEqual([rig_app.LOW_DISTRACTION_COMPANION_CHECK_MS], scheduled)


if __name__ == "__main__":
    unittest.main()
