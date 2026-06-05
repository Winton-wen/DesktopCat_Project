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

    def test_companion_messages_use_longer_display_duration(self) -> None:
        from desktop_cat import rig_app

        source = inspect.getsource(rig_app.RigDesktopCatApp.show_companion_message)
        self.assertIn("hide_ms=12000", source)

    def test_rig_speech_bubble_sits_lower_near_pet(self) -> None:
        from desktop_cat import rig_app

        self.assertGreaterEqual(rig_app.SPEECH_BUBBLE_PET_OVERLAP_PX, 58)


if __name__ == "__main__":
    unittest.main()
