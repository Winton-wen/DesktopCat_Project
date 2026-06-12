from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from desktop_cat.companion_messages import (
    LUNAR_SPECIAL_DAYS_BY_YEAR,
    load_default_companion_pack,
    render_companion_text,
)
from desktop_cat.rig_app import TEXT
from desktop_cat.time_reminders import (
    BEDTIME_REMINDER,
    DINNER_REMINDER,
    LATE_NIGHT_REMINDER,
    LUNCH_REMINDER,
)
from tools.run_copywriting_visual_tour import (
    CopywritingVisualTour,
    build_tour_items,
    run_with_temporary_config,
)


class CopywritingVisualTourCollectionTests(unittest.TestCase):
    def test_collects_every_interaction_template(self) -> None:
        expected = {
            (key, template)
            for key, templates in TEXT.items()
            for template in templates
        }
        actual = {
            (item.source_id, item.text)
            for item in build_tour_items()
            if item.group == "interaction"
        }

        self.assertEqual(expected, actual)

    def test_collects_all_fixed_reminders(self) -> None:
        expected = {
            reminder.key: reminder.message
            for reminder in (
                LUNCH_REMINDER,
                DINNER_REMINDER,
                BEDTIME_REMINDER,
                LATE_NIGHT_REMINDER,
            )
        }
        reminder_items = [
            item for item in build_tour_items() if item.group == "reminder"
        ]

        self.assertEqual(
            expected,
            {item.source_id: item.text for item in reminder_items},
        )
        self.assertTrue(
            all(
                item.button_text == "谢谢呆呆的关心，不用再提醒啦"
                for item in reminder_items
            )
        )

    def test_collects_every_companion_message_once(self) -> None:
        expected = load_default_companion_pack().messages
        actual = [
            item for item in build_tour_items() if item.group == "companion"
        ]

        self.assertEqual(
            [message.id for message in expected],
            [item.source_id for item in actual],
        )
        self.assertEqual(
            [message.text for message in expected],
            [item.text for item in actual],
        )
        self.assertEqual(len(actual), len({item.source_id for item in actual}))

    def test_special_day_items_have_matching_2026_dates(self) -> None:
        messages = {
            message.id: message
            for message in load_default_companion_pack().messages
        }
        special_items = [
            item
            for item in build_tour_items()
            if item.group == "companion" and item.category == "special_day"
        ]

        self.assertTrue(special_items)
        for item in special_items:
            with self.subTest(item=item.source_id):
                self.assertIsNotNone(item.current)
                self.assertEqual(2026, item.current.year)
                message = messages[item.source_id]
                if message.month_day:
                    expected_month_day = message.month_day
                else:
                    expected_month_day = LUNAR_SPECIAL_DAYS_BY_YEAR[2026][
                        message.lunar_month_day
                    ]
                self.assertEqual(
                    expected_month_day,
                    item.current.strftime("%m-%d"),
                )

    def test_anniversary_item_renders_second_anniversary(self) -> None:
        item = next(
            item
            for item in build_tour_items()
            if item.source_id == "special_anniversary_0324"
        )

        rendered = render_companion_text(
            item.text,
            pet_name="呆呆",
            mama_nickname="麻麻",
            papa_nickname="粑粑",
            current=item.current,
        )

        self.assertIn("二周年纪念日", rendered)


class FakeBubble:
    def __init__(self) -> None:
        self.after_id = "existing"
        self.pending_messages = [{"text": "old"}]
        self.shown: list[dict] = []

    def show(self, text, x, y, **kwargs) -> None:
        self.after_id = "new"
        self.shown.append(
            {
                "text": text,
                "x": x,
                "y": y,
                **kwargs,
            }
        )


class FakeRoot:
    def __init__(self) -> None:
        self.cancelled: list[str] = []

    def after_cancel(self, after_id: str) -> None:
        self.cancelled.append(after_id)


class FakeApp:
    def __init__(self) -> None:
        self.bubble = FakeBubble()
        self.root = FakeRoot()
        self.store = SimpleNamespace(
            config=SimpleNamespace(
                pet_name="呆呆",
                mama_nickname="麻麻",
                papa_nickname="粑粑",
            )
        )
        self.actions: list[tuple[str, float, bool]] = []
        self.happy_preparations: list[bool] = []
        self.quit_calls = 0

    def pet_anchor(self) -> tuple[int, int]:
        return 100, 200

    def render_text(self, text: str, current=None) -> str:
        return render_companion_text(
            text,
            pet_name=self.store.config.pet_name,
            mama_nickname=self.store.config.mama_nickname,
            papa_nickname=self.store.config.papa_nickname,
            current=current,
        )

    def set_action(self, action: str, seconds: float, force: bool = False) -> bool:
        self.actions.append((action, seconds, force))
        return True

    def prepare_happy_action(self, force: bool = False) -> bool:
        self.happy_preparations.append(force)
        return True

    def quit(self) -> None:
        self.quit_calls += 1


class CopywritingVisualTourNavigationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.items = build_tour_items()[:3]
        self.app = FakeApp()
        self.status_labels: list[str] = []
        self.tour = CopywritingVisualTour(
            self.app,
            self.items,
            status_callback=self.status_labels.append,
        )

    def test_show_replaces_existing_bubble_and_labels_item(self) -> None:
        self.tour.show(0)

        self.assertEqual(["existing"], self.app.root.cancelled)
        self.assertEqual([], self.app.bubble.pending_messages)
        shown = self.app.bubble.shown[-1]
        self.assertNotIn("[1/3]", shown["text"])
        self.assertNotIn(self.items[0].source_id, shown["text"])
        self.assertIn("[1/3]", self.status_labels[-1])
        self.assertIn(self.items[0].source_id, self.status_labels[-1])
        self.assertEqual(24 * 60 * 60 * 1000, shown["hide_ms"])
        self.assertFalse(shown["queue_if_busy"])

    def test_next_and_previous_stop_at_boundaries(self) -> None:
        self.tour.show(0)
        self.tour.previous()
        self.assertEqual(0, self.tour.index)

        self.tour.next()
        self.assertEqual(1, self.tour.index)
        self.tour.next()
        self.assertEqual(2, self.tour.index)
        self.tour.next()
        self.assertEqual(2, self.tour.index)

        self.tour.previous()
        self.assertEqual(1, self.tour.index)

    def test_replay_keeps_index_and_restarts_current_action(self) -> None:
        self.tour.show(1)
        previous_call_count = len(self.app.actions)

        self.tour.replay()

        self.assertEqual(1, self.tour.index)
        self.assertEqual(previous_call_count + 1, len(self.app.actions))

    def test_happy_items_use_runtime_happy_direction_preparation(self) -> None:
        happy_item = next(
            item for item in build_tour_items() if item.action == "happy"
        )
        tour = CopywritingVisualTour(
            self.app,
            [happy_item],
            status_callback=self.status_labels.append,
        )

        tour.show(0)
        tour.replay()

        self.assertEqual([True, True], self.app.happy_preparations)

    def test_four_emoticon_templates_use_explicit_line_breaks(self) -> None:
        items = {item.source_id: item.text for item in build_tour_items()}

        self.assertEqual(
            "{pet_name}会乖乖安静地陪着{mama_nickname}\n꜀(^. .^꜀  )꜆੭",
            items["low_distraction_on"],
        )
        self.assertEqual(
            "已经很晚啦，{mama_nickname}早点休息呀\n꜀(^. .^꜀  )꜆੭",
            items["bedtime"],
        )
        self.assertEqual(
            "{mama_nickname}辛苦一天啦，{pet_name}来贴贴你\n꜀(^. .^꜀  )꜆੭",
            items["evening_01"],
        )
        self.assertEqual(
            "{mama_nickname}还没睡嘛，{pet_name}好心疼{mama_nickname}\n"
            "(｡í _ ì｡)，{mama_nickname}忙完就早点休息吧。",
            items["late_night_01"],
        )

    def test_escape_quits_app(self) -> None:
        self.tour.quit()

        self.assertEqual(1, self.app.quit_calls)


class CopywritingVisualTourCliTests(unittest.TestCase):
    def test_list_mode_does_not_require_gui(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "tools/run_copywriting_visual_tour.py",
                "--list",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="replace",
        )

        self.assertEqual(0, completed.returncode, completed.stdout)
        self.assertIn("special_anniversary_0324", completed.stdout)
        self.assertIn("late_night", completed.stdout)

    def test_temporary_config_is_restored(self) -> None:
        old_value = os.environ.get("DESKTOPCAT_CONFIG_DIR")
        os.environ["DESKTOPCAT_CONFIG_DIR"] = "existing-config"
        seen: list[str] = []

        try:
            run_with_temporary_config(
                lambda: seen.append(os.environ["DESKTOPCAT_CONFIG_DIR"])
            )
            self.assertEqual("existing-config", os.environ["DESKTOPCAT_CONFIG_DIR"])
        finally:
            if old_value is None:
                os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
            else:
                os.environ["DESKTOPCAT_CONFIG_DIR"] = old_value

        self.assertEqual(1, len(seen))
        self.assertNotEqual("existing-config", seen[0])
        self.assertTrue(Path(seen[0]).name.startswith("desktopcat_copy_tour_"))


if __name__ == "__main__":
    unittest.main()
