from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class SpeechBubblePolishTests(unittest.TestCase):
    def test_rig_speech_bubble_uses_wrapped_canvas_layout(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigSpeechBubble)
        self.assertIn("tk.Canvas", source)
        self.assertIn("tkfont.Font", source)
        self.assertIn("max_text_w", source)
        self.assertIn("create_text", source)
        self.assertIn("width=text_w", source)
        self.assertIn("window_w", source)
        self.assertIn("window_h", source)

    def test_rig_speech_bubble_keeps_separate_dismiss_button(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigSpeechBubble)
        self.assertIn("button_window", source)
        self.assertIn("move_button_to_pet", source)
        self.assertIn("button_text and button_command", source)

    def test_reminder_button_uses_approved_light_blue_palette(self) -> None:
        from desktop_cat import rig_app

        self.assertEqual("#DCEEFF", rig_app.REMINDER_BUTTON_BG)
        self.assertEqual("#C4E2FF", rig_app.REMINDER_BUTTON_ACTIVE_BG)
        self.assertEqual("#28527A", rig_app.REMINDER_BUTTON_FG)
        source = inspect.getsource(rig_app.RigSpeechBubble.__init__)
        self.assertIn("REMINDER_BUTTON_BG", source)
        self.assertIn("REMINDER_BUTTON_ACTIVE_BG", source)
        self.assertIn("REMINDER_BUTTON_FG", source)

    def test_companion_messages_use_short_display_duration(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp.show_companion_message)
        self.assertIn("hide_ms=COMPANION_MESSAGE_HIDE_MS", source)
        self.assertEqual(3000, rig_app.COMPANION_MESSAGE_HIDE_MS)

    def test_rig_speech_bubble_sits_lower_near_pet(self) -> None:
        from desktop_cat import rig_app

        self.assertGreaterEqual(rig_app.SPEECH_BUBBLE_PET_OVERLAP_PX, 58)

    def test_rig_speech_bubble_queues_new_text_while_previous_text_is_visible(self) -> None:
        from desktop_cat import rig_app

        bubble = rig_app.RigSpeechBubble.__new__(rig_app.RigSpeechBubble)
        bubble.after_id = "visible"
        bubble.pending_messages = []

        queued = bubble.queue_message_if_busy(
            text="next",
            pet_center_x=100,
            pet_top_y=120,
            button_text=None,
            button_command=None,
            hide_ms=3200,
        )

        self.assertTrue(queued)
        self.assertEqual(1, len(bubble.pending_messages))
        self.assertEqual("next", bubble.pending_messages[0]["text"])

    def test_queued_speech_bubble_uses_current_pet_anchor_when_it_is_shown(self) -> None:
        from desktop_cat import rig_app

        class FakeRoot:
            def after(self, _delay_ms, callback):
                callback()

        shown: list[tuple[str, int, int]] = []
        bubble = rig_app.RigSpeechBubble.__new__(rig_app.RigSpeechBubble)
        bubble.root = FakeRoot()
        bubble.pending_messages = [
            {
                "text": "queued",
                "pet_center_x": 100,
                "pet_top_y": 120,
                "button_text": None,
                "button_command": None,
                "hide_ms": 3200,
            }
        ]
        bubble.pet_anchor_provider = lambda: (360, 420)
        bubble.show = lambda text, pet_center_x, pet_top_y, **_kwargs: shown.append(
            (text, pet_center_x, pet_top_y)
        )

        bubble.show_next_queued_message()

        self.assertEqual([("queued", 360, 420)], shown)

    def test_clear_owner_hides_matching_visible_bubble_and_drops_matching_queue(self) -> None:
        from desktop_cat import rig_app

        hidden: list[bool] = []
        bubble = rig_app.RigSpeechBubble.__new__(rig_app.RigSpeechBubble)
        bubble.current_owner = 12
        bubble.pending_messages = [
            {"text": "same action", "owner": 12},
            {"text": "reminder", "owner": None},
        ]
        bubble.hide = lambda: hidden.append(True)

        bubble.clear_owner(12)

        self.assertEqual([True], hidden)
        self.assertEqual(
            [{"text": "reminder", "owner": None}],
            bubble.pending_messages,
        )

    def test_clear_owner_does_not_hide_unowned_reminder_bubble(self) -> None:
        from desktop_cat import rig_app

        hidden: list[bool] = []
        bubble = rig_app.RigSpeechBubble.__new__(rig_app.RigSpeechBubble)
        bubble.current_owner = None
        bubble.pending_messages = []
        bubble.hide = lambda: hidden.append(True)

        bubble.clear_owner(12)

        self.assertEqual([], hidden)


if __name__ == "__main__":
    unittest.main()
