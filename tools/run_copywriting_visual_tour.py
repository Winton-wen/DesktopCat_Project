from __future__ import annotations

import argparse
import os
import tempfile
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys
from typing import Callable, TypeVar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from desktop_cat.companion_messages import (
    LUNAR_SPECIAL_DAYS_BY_YEAR,
    CompanionMessage,
    load_default_companion_pack,
)
from desktop_cat.rig_app import ACTION_FPS, CandidateDesktopCatApp, TEXT
from desktop_cat.time_reminders import (
    BEDTIME_REMINDER,
    DINNER_REMINDER,
    LATE_NIGHT_REMINDER,
    LUNCH_REMINDER,
    TimeReminder,
)


DEFAULT_BATCH_ID = "20260527_motion_quality_v1"
TOUR_BUBBLE_HIDE_MS = 24 * 60 * 60 * 1000
REMINDER_BUTTON_TEXT = "谢谢呆呆的关心，不用再提醒啦"
T = TypeVar("T")


@dataclass(frozen=True)
class TourItem:
    id: str
    source_id: str
    group: str
    category: str
    text: str
    action: str
    current: datetime | None = None
    button_text: str | None = None


INTERACTION_ACTIONS = {
    "pet": "clicked",
    "happy": "happy",
    "cute": "cute",
    "wave": "wave",
    "sleep": "sleep_in",
    "wake": "wake",
    "walk_left": "walk_left",
    "walk_right": "walk",
}

STATE_ITEMS = (
    TourItem(
        id="state:low_distraction_on",
        source_id="low_distraction_on",
        group="state",
        category="state",
        text="{pet_name}会乖乖安静地陪着{mama_nickname}\n꜀(^. .^꜀  )꜆੭",
        action="idle",
    ),
    TourItem(
        id="state:low_distraction_off",
        source_id="low_distraction_off",
        group="state",
        category="state",
        text="呆呆要和麻麻玩！",
        action="idle",
    ),
    TourItem(
        id="state:return_corner_done",
        source_id="return_corner_done",
        group="state",
        category="state",
        text="{pet_name}跳回屏幕角落啦。",
        action="return_home",
    ),
)


def special_day_test_datetime(message: CompanionMessage) -> datetime | None:
    if message.category != "special_day":
        return None
    if message.month_day:
        return datetime.strptime(
            f"2026-{message.month_day}",
            "%Y-%m-%d",
        )
    if message.lunar_month_day:
        month_day = LUNAR_SPECIAL_DAYS_BY_YEAR[2026][message.lunar_month_day]
        return datetime.strptime(f"2026-{month_day}", "%Y-%m-%d")
    raise ValueError(f"Special-day message has no date: {message.id}")


def interaction_items() -> list[TourItem]:
    items: list[TourItem] = []
    for source_id, templates in TEXT.items():
        for index, template in enumerate(templates, 1):
            items.append(
                TourItem(
                    id=f"interaction:{source_id}:{index:02d}",
                    source_id=source_id,
                    group="interaction",
                    category="interaction",
                    text=template,
                    action=INTERACTION_ACTIONS[source_id],
                )
            )
    return items


def reminder_items() -> list[TourItem]:
    reminders: tuple[TimeReminder, ...] = (
        LUNCH_REMINDER,
        DINNER_REMINDER,
        BEDTIME_REMINDER,
        LATE_NIGHT_REMINDER,
    )
    return [
        TourItem(
            id=f"reminder:{reminder.key}",
            source_id=reminder.key,
            group="reminder",
            category="reminder",
            text=reminder.message,
            action="idle",
            button_text=REMINDER_BUTTON_TEXT,
        )
        for reminder in reminders
    ]


def companion_items() -> list[TourItem]:
    return [
        TourItem(
            id=f"companion:{message.id}",
            source_id=message.id,
            group="companion",
            category=message.category,
            text=message.text,
            action=message.action,
            current=special_day_test_datetime(message),
        )
        for message in load_default_companion_pack().messages
    ]


def build_tour_items() -> list[TourItem]:
    first_launch = TourItem(
        id="state:first_launch",
        source_id="first_launch",
        group="state",
        category="state",
        text="{pet_name}来啦！我以后就是{mama_nickname}的桌面小猫啦",
        action="wave",
    )
    return [
        first_launch,
        *interaction_items(),
        *STATE_ITEMS,
        *reminder_items(),
        *companion_items(),
    ]


def runtime_action(action: str) -> str:
    if action == "sleep":
        return "sleep_in"
    return action if action in ACTION_FPS else "wave"


class CopywritingVisualTour:
    def __init__(
        self,
        app: CandidateDesktopCatApp,
        items: list[TourItem],
        status_callback: Callable[[str], None] | None = None,
    ) -> None:
        if not items:
            raise ValueError("The copywriting visual tour has no items.")
        self.app = app
        self.items = items
        self.index = 0
        self.status_callback = status_callback or (lambda _text: None)

    @property
    def current_item(self) -> TourItem:
        return self.items[self.index]

    def clear_current_bubble(self) -> None:
        after_id = self.app.bubble.after_id
        if after_id:
            try:
                self.app.root.after_cancel(after_id)
            except Exception:
                pass
        self.app.bubble.after_id = None
        self.app.bubble.pending_messages.clear()

    def item_label(self, item: TourItem) -> str:
        return (
            f"[{self.index + 1}/{len(self.items)}] "
            f"{item.source_id} · {item.category} · {item.action}"
        )

    def play_action(self, item: TourItem) -> None:
        if item.action == "happy":
            self.app.prepare_happy_action(force=True)
            return
        if item.action == "walk_left":
            self.app.walk_direction = -1
            self.app.walk_can_reverse = False
        elif item.action == "walk":
            self.app.walk_direction = 1
            self.app.walk_can_reverse = False
        self.app.set_action(runtime_action(item.action), 2.4, force=True)

    def show(self, index: int) -> None:
        self.index = max(0, min(index, len(self.items) - 1))
        item = self.current_item
        self.clear_current_bubble()
        self.play_action(item)
        rendered = self.app.render_text(item.text, current=item.current)
        self.status_callback(self.item_label(item))
        button_command = None
        if item.button_text:
            button_command = lambda: self.app.root.after(
                100,
                lambda: self.show(self.index),
            )
        self.app.bubble.show(
            rendered,
            *self.app.pet_anchor(),
            button_text=item.button_text,
            button_command=button_command,
            hide_ms=TOUR_BUBBLE_HIDE_MS,
            queue_if_busy=False,
        )

    def next(self, _event=None) -> None:
        self.show(min(self.index + 1, len(self.items) - 1))

    def previous(self, _event=None) -> None:
        self.show(max(self.index - 1, 0))

    def replay(self, _event=None) -> None:
        self.play_action(self.current_item)

    def quit(self, _event=None) -> None:
        self.app.quit()

    def bind_controls(self) -> None:
        self.app.root.bind("<space>", self.next)
        self.app.root.bind("<Right>", self.next)
        self.app.root.bind("<Left>", self.previous)
        self.app.root.bind("<KeyPress-r>", self.replay)
        self.app.root.bind("<KeyPress-R>", self.replay)
        self.app.root.bind("<Escape>", self.quit)


class TourStatusWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#EAF4FF")
        self.label = tk.Label(
            self.window,
            text="",
            bg="#EAF4FF",
            fg="#28527A",
            font=("Microsoft YaHei UI", 9),
            padx=10,
            pady=6,
        )
        self.label.pack()
        self.window.geometry("+16+16")

    def update(self, text: str) -> None:
        self.label.configure(text=text)
        self.window.update_idletasks()
        self.window.deiconify()
        self.window.lift()


def run_with_temporary_config(callback: Callable[[], T]) -> T:
    old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
    with tempfile.TemporaryDirectory(prefix="desktopcat_copy_tour_") as temp_dir:
        os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
        try:
            return callback()
        finally:
            if old_config_dir is None:
                os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
            else:
                os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir


def print_tour_items(items: list[TourItem]) -> None:
    print(f"copywriting_visual_tour_items={len(items)}")
    for index, item in enumerate(items, 1):
        date = item.current.strftime("%Y-%m-%d") if item.current else "-"
        print(
            f"{index:02d}\t{item.source_id}\t{item.group}\t"
            f"{item.category}\t{item.action}\t{date}"
        )


def run_gui(batch_id: str, smoke: bool) -> None:
    def launch() -> None:
        app = CandidateDesktopCatApp(
            batch_id,
            enable_time_reminders=False,
            enable_companion_messages=False,
        )
        app.random_idle_action = lambda now: app.start_action_now(
            "idle",
            TOUR_BUBBLE_HIDE_MS / 1000,
        )
        status = TourStatusWindow(app.root)
        tour = CopywritingVisualTour(
            app,
            build_tour_items(),
            status_callback=status.update,
        )
        tour.bind_controls()

        def start_tour() -> None:
            tour.show(0)
            app.root.lift()
            app.root.focus_force()

        app.root.after(500, start_tour)
        if smoke:
            app.root.after(3000, tour.quit)
        app.run()

    run_with_temporary_config(launch)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manually inspect every DesktopCat message with its real bubble and action."
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all tour items without opening the GUI.",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Show the first item and exit automatically after 3 seconds.",
    )
    parser.add_argument(
        "--batch",
        default=DEFAULT_BATCH_ID,
        help="Production sprite batch to preview.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    items = build_tour_items()
    if args.list:
        print_tour_items(items)
        return 0
    print(
        "DesktopCat 全部语料视觉巡演："
        "空格/右方向键=下一条，左方向键=上一条，R=重播动作，Esc=退出"
    )
    print(f"copywriting_visual_tour_items={len(items)}")
    run_gui(args.batch, args.smoke)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
