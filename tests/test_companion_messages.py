from __future__ import annotations

import inspect
import sys
import unittest
from datetime import datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class CompanionMessageTests(unittest.TestCase):
    def test_default_partner_message_pack_has_core_categories(self) -> None:
        from desktop_cat.companion_messages import load_companion_pack

        pack = load_companion_pack(ROOT / "assets" / "companion_messages" / "partner_default.json")
        categories = {message.category for message in pack.messages}

        self.assertTrue({"morning", "lunch", "evening", "bedtime", "miss_you", "busy_support"}.issubset(categories))
        self.assertTrue(all(message.text.strip() for message in pack.messages))
        self.assertTrue(all(1 <= message.cooldown_hours <= 72 for message in pack.messages))

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

    def test_candidate_launcher_has_companion_message_preview_mode(self) -> None:
        launcher = (ROOT / "candidate_launcher.py").read_text(encoding="utf-8")

        self.assertIn("--test-companion-time", launcher)
        self.assertIn("check_companion_message(args.test_companion_time)", launcher)

    def test_rig_app_has_companion_message_runtime_flow(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp)
        self.assertIn("load_default_companion_pack", source)
        self.assertIn("check_companion_message", source)
        self.assertIn("show_companion_message", source)


if __name__ == "__main__":
    unittest.main()
