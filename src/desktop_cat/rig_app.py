from __future__ import annotations

import os
import random
import math
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import Menu
from datetime import datetime, time as clock_time
from pathlib import Path

from PIL import Image, ImageTk

from .companion_messages import (
    DEFAULT_COMPANION_CHECK_MS,
    CompanionMessage,
    load_default_companion_pack,
    load_companion_pack,
    select_companion_message,
)
from .config import ConfigStore
from .paths import app_root
from .sprite_manifest import ACTIONS
from .time_reminders import reminder_for_time, reminder_instance_key, reminder_is_due


TRANSPARENT = "#fff7f0"
WIDTH = 280
HEIGHT = 240
DISPLAY_SIZE = 165
WALK_STEP_PX = 4
HAPPY_STEP_PX = 2
HAPPY_HOP_PX = 14
SCREEN_MARGIN = 8
SPEECH_BUBBLE_PET_OVERLAP_PX = 60
DISMISS_BUTTON_GAP_PX = 6
TIME_REMINDER_CHECK_MS = 5 * 60 * 1000
LOW_DISTRACTION_COMPANION_CHECK_MS = 60 * 60 * 1000
DEFAULT_COMPANION_START_DELAY_MS = 20 * 1000
FIRST_LAUNCH_COMPANION_DELAY_MS = 45 * 1000
RESET_JUMP_STEPS = 48
RESET_JUMP_INTERVAL_MS = 42
RESET_JUMP_HOP_PX = 30
MAX_PENDING_ACTIONS = 8
MAX_PENDING_BUBBLES = 8
ACTION_FPS = {
    "idle": 12,
    "blink": 10,
    "wave": 12,
    "clicked": 12,
    "happy": 24,
    "happy_right": 24,
    "return_home": 24,
    "sleep_in": 24,
    "sleep": 8,
    "wake": 32,
    "walk": 14,
    "walk_left": 14,
    "cute": 24,
    "drag": 8,
}
LOOPING_ACTIONS = {"idle", "sleep", "drag"}
ACTION_CHAIN = {
    "sleep_in": "sleep",
    "wake": "idle",
}
NORMAL_IDLE_ACTIONS = ["idle", "blink", "wave", "happy", "cute", "sleep_in", "walk"]
NORMAL_IDLE_WEIGHTS = [58, 22, 5, 5, 4, 2, 4]
LOW_DISTRACTION_IDLE_ACTIONS = ["idle", "blink", "sleep_in", "wave"]
LOW_DISTRACTION_IDLE_WEIGHTS = [76, 18, 4, 2]
MORNING_IDLE_ACTIONS = ["idle", "blink", "wave", "happy", "cute", "walk"]
MORNING_IDLE_WEIGHTS = [50, 20, 10, 6, 6, 8]
EVENING_IDLE_ACTIONS = ["idle", "blink", "wave", "happy", "cute", "sleep_in"]
EVENING_IDLE_WEIGHTS = [60, 20, 5, 4, 6, 5]
SLEEPY_IDLE_ACTIONS = ["idle", "blink", "sleep_in"]
SLEEPY_IDLE_WEIGHTS = [70, 20, 10]


TEXT = {
    "pet": "\u6478\u6478\u5934\uff0c\u6211\u5728\u54e6\u3002",
    "happy": "\u5f00\u5fc3\uff0c\u8df3\u4e00\u4e0b\u3002",
    "cute": "\u770b\u6211\u53ef\u7231\u5417\uff1f",
    "wave": "\u55e8\uff0c\u770b\u8fd9\u91cc\u3002",
    "sleep": "\u6211\u5148\u8d34\u7740\u772f\u4e00\u4f1a\u513f\u3002",
    "wake": "\u9192\u5566\u3002",
    "walk_left": "\u6211\u5f80\u5de6\u8d70\u4e24\u6b65\u3002",
    "walk_right": "\u6211\u5f80\u53f3\u8d70\u4e24\u6b65\u3002",
}
MISS_PARTNER_MESSAGES = [
    "我也很想他呀。先抱抱你，小猫陪你等他忙完。",
    "想他的时候就摸摸小猫，我会替他陪你一会儿。",
    "距离有点远，但喜欢一直都在。小猫帮你记着呢。",
]
TIRED_TODAY_MESSAGES = [
    "今天辛苦啦，先慢慢呼吸一下，别把自己绷太紧。",
    "忙完这一阵就休息一下吧，小猫在这里陪你。",
    "已经很努力啦。喝点水，摸摸头，今晚对自己温柔一点。",
]


def frame_sort_key(path: Path) -> tuple[int, str]:
    try:
        return (int(path.stem), path.name)
    except ValueError:
        return (10**9, path.name)


def next_walk_x(current_x: int, direction: int, min_x: int, max_x: int, step: int = WALK_STEP_PX) -> int:
    if direction < 0:
        if current_x <= min_x:
            return current_x
        return max(current_x - step, min_x)
    if direction > 0:
        if current_x >= max_x:
            return current_x
        return min(current_x + step, max_x)
    return current_x


def bounded_walk_direction(current_x: int, min_x: int, max_x: int, preferred: int) -> int:
    if current_x <= min_x:
        return 1
    if current_x >= max_x:
        return -1
    return -1 if preferred < 0 else 1


def pet_rhythm_for_time(current: clock_time) -> str:
    minutes = current.hour * 60 + current.minute
    if 1 * 60 + 30 <= minutes < 5 * 60:
        return "late_night"
    if 7 * 60 <= minutes < 11 * 60 + 30:
        return "morning"
    if 13 * 60 + 30 <= minutes < 18 * 60:
        return "afternoon"
    if 18 * 60 <= minutes < 22 * 60 + 30:
        return "evening"
    if minutes >= 22 * 60 + 30 or minutes < 1 * 60 + 30:
        return "bedtime"
    return "afternoon"


def idle_action_choices(
    low_distraction_mode: bool,
    current_time: clock_time | None = None,
) -> tuple[list[str], list[int]]:
    rhythm = pet_rhythm_for_time(current_time or datetime.now().time())
    if rhythm in {"bedtime", "late_night"}:
        return SLEEPY_IDLE_ACTIONS, SLEEPY_IDLE_WEIGHTS
    if low_distraction_mode:
        return LOW_DISTRACTION_IDLE_ACTIONS, LOW_DISTRACTION_IDLE_WEIGHTS
    if rhythm == "morning":
        return MORNING_IDLE_ACTIONS, MORNING_IDLE_WEIGHTS
    if rhythm == "evening":
        return EVENING_IDLE_ACTIONS, EVENING_IDLE_WEIGHTS
    return NORMAL_IDLE_ACTIONS, NORMAL_IDLE_WEIGHTS


def reset_return_action(start_x: int, target_x: int) -> str:
    return "return_home" if target_x >= start_x else "happy"


def saved_position_or_default(
    saved_position: dict[str, int] | None,
    default_position: tuple[int, int],
    screen_size: tuple[int, int],
) -> tuple[int, int]:
    if not saved_position:
        return default_position
    x = saved_position.get("x")
    y = saved_position.get("y")
    if type(x) is not int or type(y) is not int:
        return default_position
    screen_w, screen_h = screen_size
    max_x = screen_w - WIDTH - SCREEN_MARGIN
    max_y = screen_h - HEIGHT - SCREEN_MARGIN
    if SCREEN_MARGIN <= x <= max_x and SCREEN_MARGIN <= y <= max_y:
        return x, y
    return default_position


def low_distraction_menu_label(enabled: bool) -> str:
    return "退出低打扰模式" if enabled else "进入低打扰模式"


def speech_bubble_geometry(
    screen_w: int,
    pet_center_x: int,
    pet_top_y: int,
    bubble_w: int,
    bubble_h: int,
) -> tuple[int, int]:
    x = max(8, min(pet_center_x - bubble_w // 2, screen_w - bubble_w - 8))
    y = max(8, pet_top_y - bubble_h + SPEECH_BUBBLE_PET_OVERLAP_PX)
    return x, y


def dismiss_button_geometry(
    screen_w: int,
    screen_h: int,
    pet_center_x: int,
    pet_top_y: int,
    button_w: int,
    button_h: int,
) -> tuple[int, int]:
    x = max(8, min(pet_center_x - button_w // 2, screen_w - button_w - 8))
    y = max(8, min(pet_top_y + DISPLAY_SIZE + DISMISS_BUTTON_GAP_PX, screen_h - button_h - 8))
    return x, y


class StableSpriteFrameSource:
    asset_folder = "sprites"

    def __init__(self) -> None:
        self.root = app_root() / "assets" / self.asset_folder
        self.frames: dict[str, list[ImageTk.PhotoImage]] = {}
        self.load()

    def load(self) -> None:
        for action in ACTIONS:
            folder = self.root / action.name
            frames = []
            for path in sorted(folder.glob("*.png"), key=frame_sort_key):
                image = Image.open(path).convert("RGBA")
                image.thumbnail((DISPLAY_SIZE, DISPLAY_SIZE), Image.Resampling.LANCZOS)
                frames.append(ImageTk.PhotoImage(image))
            if frames:
                self.frames[action.name] = frames
        if "idle" not in self.frames:
            raise RuntimeError("Missing stable idle sprites.")

    def get(self, action: str, frame: int, frame_count: int) -> ImageTk.PhotoImage:
        frames = self.frames.get(action) or self.frames["idle"]
        return frames[frame % len(frames)]

    def count(self, action: str) -> int:
        return len(self.frames.get(action) or self.frames["idle"])


class ProductionBatchFrameSource(StableSpriteFrameSource):
    def __init__(self, batch_id: str) -> None:
        self.batch_id = batch_id
        self.root = app_root() / "assets" / "production" / "desktop_cat" / "batches" / batch_id / "clean"
        self.frames: dict[str, list[ImageTk.PhotoImage]] = {}
        self.load()

    def load(self) -> None:
        stable_root = app_root() / "assets" / StableSpriteFrameSource.asset_folder
        if stable_root.exists():
            super().load()
        for folder in sorted(self.root.iterdir()):
            if not folder.is_dir() or folder.name in self.frames:
                continue
            frames = []
            for path in sorted(folder.glob("*.png"), key=frame_sort_key):
                image = Image.open(path).convert("RGBA")
                image.thumbnail((DISPLAY_SIZE, DISPLAY_SIZE), Image.Resampling.LANCZOS)
                frames.append(ImageTk.PhotoImage(image))
            if frames:
                self.frames[folder.name] = frames
        if "idle" not in self.frames:
            raise RuntimeError(f"Missing idle sprites for production batch {self.batch_id}.")


def production_batch_clean_root(batch_id: str) -> Path:
    return app_root() / "assets" / "production" / "desktop_cat" / "batches" / batch_id / "clean"


class RigSpeechBubble:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg=TRANSPARENT)
        self.window.wm_attributes("-transparentcolor", TRANSPARENT)
        self.canvas = tk.Canvas(self.window, width=1, height=1, bg=TRANSPARENT, highlightthickness=0)
        self.canvas.pack()
        self.button_window = tk.Toplevel(root)
        self.button_window.withdraw()
        self.button_window.overrideredirect(True)
        self.button_window.attributes("-topmost", True)
        self.button_window.configure(bg="#ffdce8")
        self.button = tk.Button(
            self.button_window,
            text="",
            bg="#ffdce8",
            activebackground="#ffc7da",
            fg="#6f2542",
            activeforeground="#6f2542",
            font=("Microsoft YaHei UI", 9),
            relief="raised",
            bd=2,
            padx=12,
            pady=5,
            cursor="hand2",
        )
        self.button.pack()
        self.font = tkfont.Font(family="Microsoft YaHei UI", size=10)
        self.after_id: str | None = None
        self.pending_messages: list[dict] = []
        self.pet_anchor_provider = None
        self.canvas_w = 1
        self.canvas_h = 1
        self.window_w = 1
        self.window_h = 1

    def hide(self) -> None:
        current_after = self.after_id
        self.after_id = None
        if current_after:
            try:
                self.root.after_cancel(current_after)
            except tk.TclError:
                pass
        self.window.withdraw()
        self.button_window.withdraw()
        self.show_next_queued_message()

    def queue_message_if_busy(
        self,
        text: str,
        pet_center_x: int,
        pet_top_y: int,
        button_text: str | None,
        button_command,
        hide_ms: int,
    ) -> bool:
        if self.after_id is None:
            return False
        if len(self.pending_messages) >= MAX_PENDING_BUBBLES:
            self.pending_messages.pop(0)
        self.pending_messages.append(
            {
                "text": text,
                "pet_center_x": pet_center_x,
                "pet_top_y": pet_top_y,
                "button_text": button_text,
                "button_command": button_command,
                "hide_ms": hide_ms,
            }
        )
        return True

    def show_next_queued_message(self) -> None:
        if not self.pending_messages:
            return
        message = self.pending_messages.pop(0)
        pet_center_x, pet_top_y = (
            self.pet_anchor_provider()
            if self.pet_anchor_provider
            else (message["pet_center_x"], message["pet_top_y"])
        )
        self.root.after(
            80,
            lambda: self.show(
                message["text"],
                pet_center_x,
                pet_top_y,
                button_text=message["button_text"],
                button_command=message["button_command"],
                hide_ms=message["hide_ms"],
                queue_if_busy=False,
            ),
        )

    def show(
        self,
        text: str,
        pet_center_x: int,
        pet_top_y: int,
        button_text: str | None = None,
        button_command=None,
        hide_ms: int = 3200,
        queue_if_busy: bool = True,
    ) -> None:
        if queue_if_busy and self.queue_message_if_busy(
            text=text,
            pet_center_x=pet_center_x,
            pet_top_y=pet_top_y,
            button_text=button_text,
            button_command=button_command,
            hide_ms=hide_ms,
        ):
            return
        padding_x = 18
        padding_y = 12
        tail_h = 22
        border = 3
        max_text_w = 210
        measured_text_w = self.font.measure(text)
        text_w = min(max_text_w, max(84, measured_text_w))
        lines = max(1, (measured_text_w + max_text_w - 1) // max_text_w)
        text_h = self.font.metrics("linespace") * lines
        bubble_w = text_w + padding_x * 2 + border * 2
        bubble_h = text_h + padding_y * 2 + border * 2
        self.canvas_w = bubble_w + 10
        self.canvas_h = bubble_h + tail_h + 8
        tail_x = self.canvas_w // 2

        self.canvas.configure(width=self.canvas_w, height=self.canvas_h)
        canvas = self.canvas
        canvas.delete("all")
        outline = "#111111"
        fill = "#ffffff"
        left = 5
        top = 5
        right = left + bubble_w
        bottom = top + bubble_h
        canvas.create_rectangle(left, top, right, bottom, fill=fill, outline=outline, width=border)
        canvas.create_polygon(
            tail_x - 10,
            bottom - 1,
            tail_x + 10,
            bottom - 1,
            tail_x,
            bottom + tail_h,
            fill=fill,
            outline=outline,
            width=border,
        )
        canvas.create_line(tail_x - 9, bottom, tail_x + 9, bottom, fill=fill, width=border + 1)
        canvas.create_text(
            self.canvas_w // 2,
            top + bubble_h // 2,
            text=text,
            width=text_w,
            fill="#111111",
            font=self.font,
            justify="center",
        )
        if button_text and button_command:
            def wrapped_command() -> None:
                button_command()
                self.hide()

            self.button.configure(text=button_text, command=wrapped_command)
        else:
            self.button_window.withdraw()
        self.window.update_idletasks()
        self.window_w = self.canvas_w
        self.window_h = self.canvas_h
        x, y = self.geometry_for_pet(pet_center_x, pet_top_y)
        self.window.geometry(f"{self.window_w}x{self.window_h}+{x}+{y}")
        self.window.deiconify()
        self.window.lift()
        if button_text and button_command:
            self.move_button_to_pet(pet_center_x, pet_top_y)
            self.button_window.deiconify()
            self.button_window.lift()
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.after_id = self.root.after(hide_ms, self.hide)

    def geometry_for_pet(self, pet_center_x: int, pet_top_y: int) -> tuple[int, int]:
        return speech_bubble_geometry(
            self.root.winfo_screenwidth(),
            pet_center_x,
            pet_top_y,
            self.window_w,
            self.window_h,
        )

    def move_button_to_pet(self, pet_center_x: int, pet_top_y: int) -> None:
        self.button_window.update_idletasks()
        w = self.button_window.winfo_reqwidth()
        h = self.button_window.winfo_reqheight()
        x, y = dismiss_button_geometry(
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight(),
            pet_center_x,
            pet_top_y,
            w,
            h,
        )
        self.button_window.geometry(f"+{x}+{y}")

    def move_to_pet(self, pet_center_x: int, pet_top_y: int) -> None:
        if not self.window.winfo_viewable():
            return
        x, y = self.geometry_for_pet(pet_center_x, pet_top_y)
        self.window.geometry(f"+{x}+{y}")
        if self.button_window.winfo_viewable():
            self.move_button_to_pet(pet_center_x, pet_top_y)


class RigDesktopCatApp:
    def __init__(
        self,
        frame_source: StableSpriteFrameSource | None = None,
        frame_source_factory=None,
        title: str = "DesktopCat Stable Preview",
        enable_time_reminders: bool = True,
        enable_companion_messages: bool = True,
        low_distraction_mode: bool | None = None,
        test_rhythm_time: datetime | None = None,
        test_first_launch: bool = False,
    ) -> None:
        self.store = ConfigStore()
        if low_distraction_mode is not None:
            self.store.config.low_distraction_mode = low_distraction_mode
        self.test_first_launch = test_first_launch
        self.first_launch_pending = test_first_launch or not self.store.config.first_launch_completed
        self.root = tk.Tk()
        self.root.title(title)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=TRANSPARENT)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg=TRANSPARENT, highlightthickness=0)
        self.canvas.pack()
        self.frames = frame_source or (frame_source_factory() if frame_source_factory else StableSpriteFrameSource())
        self.sprite = self.canvas.create_image(WIDTH // 2, HEIGHT // 2, anchor="center")
        self.bubble = RigSpeechBubble(self.root)
        self.bubble.pet_anchor_provider = self.pet_anchor
        self.action = "idle"
        self.frame = 0
        self.action_until = 0.0
        self.drag_start: tuple[int, int] | None = None
        self.window_start: tuple[int, int] | None = None
        self.press_action: str | None = None
        self.drag_moved = False
        self.walk_direction = 1
        self.happy_direction = 1
        self.happy_start: tuple[int, int] | None = None
        self.resetting_position = False
        self.pending_actions: list[tuple[str, float]] = []
        self.time_reminders_last_shown_at: dict[str, datetime] = {}
        self.time_reminders_dismissed: set[str] = set()
        self.companion_pack = self.load_configured_companion_pack()
        self.companion_messages_last_shown_at: dict[str, datetime] = {}
        self.test_rhythm_time = test_rhythm_time

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_menu)
        self.canvas.bind("<Double-Button-1>", lambda _event: self.wave())

        self.place_initially()
        self.draw()
        self.action_until = time.monotonic() + 2.5
        self.root.after(120, self.tick)
        if self.first_launch_pending:
            self.root.after(1200, self.show_first_launch_message)
        if enable_time_reminders:
            self.root.after(1500, self.check_time_reminder)
        if enable_companion_messages:
            delay_ms = FIRST_LAUNCH_COMPANION_DELAY_MS if self.first_launch_pending else DEFAULT_COMPANION_START_DELAY_MS
            self.root.after(delay_ms, self.check_companion_message)

    def run(self) -> None:
        self.root.mainloop()

    def load_configured_companion_pack(self):
        try:
            return load_companion_pack(self.store.companion_message_pack_path())
        except (OSError, ValueError):
            return load_default_companion_pack()

    def default_position(self) -> tuple[int, int]:
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        return sw - WIDTH - 28, sh - HEIGHT - 56

    def place_initially(self) -> None:
        x, y = saved_position_or_default(
            self.store.config.last_position,
            self.default_position(),
            (self.root.winfo_screenwidth(), self.root.winfo_screenheight()),
        )
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

    def action_frame_count(self) -> int:
        return {
            "blink": 10,
            "clicked": 9,
            "drag": 8,
            "happy": 48,
            "happy_right": 48,
            "return_home": 48,
            "cute": 44,
            "sleep_in": 99,
            "sleep": 11,
            "wake": 80,
            "walk": 16,
            "walk_left": 16,
            "wave": 17,
        }.get(self.action, self.frames.count(self.action))

    def draw(self) -> None:
        image = self.frames.get(self.action, self.frame, self.action_frame_count())
        self.canvas.itemconfigure(self.sprite, image=image)
        self.canvas.image = image

    def tick(self) -> None:
        self.frame += 1
        now = time.monotonic()
        if self.action not in LOOPING_ACTIONS and self.frame >= self.action_frame_count():
            self.finish_current_action(now)
        elif now > self.action_until and self.action == "idle" and not self.drag_start:
            self.random_idle_action(now)
        if self.action in {"happy", "happy_right"} and not self.drag_start and not self.resetting_position:
            self.advance_happy()
        elif self.action in {"walk", "walk_left"} and not self.drag_start and not self.resetting_position:
            self.advance_walk()
        self.draw()
        self.root.after(max(16, round(1000 / ACTION_FPS.get(self.action, 12))), self.tick)

    def random_idle_action(self, now: float) -> None:
        current_time = self.test_rhythm_time.time() if self.test_rhythm_time else None
        actions, weights = idle_action_choices(self.store.config.low_distraction_mode, current_time=current_time)
        action = random.choices(actions, weights=weights, k=1)[0]
        if action == "walk":
            self.walk()
            return
        if action == "happy":
            self.happy_direction = self.next_horizontal_direction()
            self.happy_start = (self.root.winfo_x(), self.root.winfo_y())
            action = self.happy_action_for_direction(self.happy_direction)
        self.action = action
        self.frame = 0
        self.action_until = now + random.uniform(3.0, 6.0)

    def action_can_start_immediately(self, action: str, force: bool) -> bool:
        if force or action in {"idle", "drag"}:
            return True
        return self.action == "idle" and not self.resetting_position and not self.drag_start

    def queue_action(self, action: str, seconds: float) -> None:
        if len(self.pending_actions) >= MAX_PENDING_ACTIONS:
            self.pending_actions.pop(0)
        self.pending_actions.append((action, seconds))

    def start_action_now(self, action: str, seconds: float) -> None:
        self.action = action
        self.frame = 0
        self.action_until = time.monotonic() + seconds
        if action not in {"happy", "happy_right"}:
            self.happy_start = None
        self.draw()

    def set_action(self, action: str, seconds: float, force: bool = False) -> bool:
        if not self.action_can_start_immediately(action, force):
            self.queue_action(action, seconds)
            return False
        self.start_action_now(action, seconds)
        return True

    def finish_current_action(self, now: float) -> None:
        if self.pending_actions:
            action, seconds = self.pending_actions.pop(0)
            self.start_action_now(action, seconds)
            return
        self.action = ACTION_CHAIN.get(self.action, "idle")
        self.frame = 0
        self.action_until = now + random.uniform(1.2, 2.2)

    def pet_anchor(self) -> tuple[int, int]:
        return self.root.winfo_x() + WIDTH // 2, self.root.winfo_y() + (HEIGHT - DISPLAY_SIZE) // 2

    def say(self, text: str) -> None:
        self.bubble.show(text, *self.pet_anchor())

    def show_first_launch_message(self) -> None:
        self.set_action("wave", 2.2, force=True)
        self.bubble.show(
            f"{self.store.config.pet_name}来陪你啦。想你或者累的时候，摸摸小猫就好。",
            *self.pet_anchor(),
            hide_ms=9000,
        )
        self.first_launch_pending = False
        if not self.test_first_launch:
            self.store.mark_first_launch_completed()

    def check_companion_message(self, now: datetime | None = None) -> None:
        current = now or datetime.now()
        message = select_companion_message(
            current,
            self.companion_pack.messages,
            self.companion_messages_last_shown_at,
        )
        if message is not None:
            self.companion_messages_last_shown_at[message.id] = current
            self.show_companion_message(message)
        delay_ms = LOW_DISTRACTION_COMPANION_CHECK_MS if self.store.config.low_distraction_mode else DEFAULT_COMPANION_CHECK_MS
        self.root.after(delay_ms, self.check_companion_message)

    def show_companion_message(self, message: CompanionMessage) -> None:
        action = message.action if message.action in ACTION_FPS else "wave"
        if action == "sleep":
            action = "sleep_in"
        self.set_action(action, 2.4)
        self.bubble.show(message.text, *self.pet_anchor(), hide_ms=12000)

    def check_time_reminder(self, now: datetime | None = None) -> None:
        current = now or datetime.now()
        reminder = reminder_for_time(current.time())
        reminder_key = reminder_instance_key(current, reminder)
        if reminder_key and reminder_is_due(
            current,
            reminder,
            self.time_reminders_last_shown_at,
            self.time_reminders_dismissed,
        ):
            self.time_reminders_last_shown_at[reminder_key] = current
            self.bubble.show(
                reminder.message,
                *self.pet_anchor(),
                button_text="谢谢小猫的关心，不用再提醒啦",
                button_command=lambda key=reminder_key: self.dismiss_time_reminder(key),
                hide_ms=30000,
            )
        self.root.after(TIME_REMINDER_CHECK_MS, self.check_time_reminder)

    def dismiss_time_reminder(self, reminder_key: str) -> None:
        self.time_reminders_dismissed.add(reminder_key)

    def toggle_low_distraction_mode(self) -> None:
        enabled = not self.store.config.low_distraction_mode
        self.store.update_low_distraction_mode(enabled)
        self.say("低打扰模式已开启。" if enabled else "低打扰模式已关闭。")

    def show_gift_interaction(self, text: str, action: str = "cute") -> None:
        self.set_action(action, 2.2)
        self.bubble.show(text, *self.pet_anchor(), hide_ms=10000)

    def miss_partner(self) -> None:
        self.show_gift_interaction(random.choice(MISS_PARTNER_MESSAGES), action="wave")

    def tired_today(self) -> None:
        self.show_gift_interaction(random.choice(TIRED_TODAY_MESSAGES), action="cute")

    def open_config(self) -> None:
        os.startfile(str(self.store.open_file()))

    def open_config_folder(self) -> None:
        os.startfile(str(self.store.open_folder()))

    def open_companion_message_pack(self) -> None:
        os.startfile(str(self.store.open_companion_message_pack_file()))

    def reset_position(self) -> None:
        target_x, target_y = self.default_position()
        start_x = self.root.winfo_x()
        start_y = self.root.winfo_y()
        self.resetting_position = True
        self.happy_direction = 1 if target_x >= start_x else -1
        self.happy_start = None
        self.set_action(reset_return_action(start_x, target_x), 2.1, force=True)
        self.animate_reset_position(
            start_x=start_x,
            start_y=start_y,
            target_x=target_x,
            target_y=target_y,
            step=0,
        )

    def animate_reset_position(
        self,
        start_x: int,
        start_y: int,
        target_x: int,
        target_y: int,
        step: int,
    ) -> None:
        progress = min(1.0, step / RESET_JUMP_STEPS)
        eased = 1 - (1 - progress) * (1 - progress)
        hop = math.sin(math.pi * progress) * RESET_JUMP_HOP_PX
        x = round(start_x + (target_x - start_x) * eased)
        y = round(start_y + (target_y - start_y) * eased - hop)
        self.root.geometry(f"+{x}+{y}")
        self.bubble.move_to_pet(x + WIDTH // 2, y + (HEIGHT - DISPLAY_SIZE) // 2)
        if step < RESET_JUMP_STEPS:
            self.root.after(
                RESET_JUMP_INTERVAL_MS,
                lambda: self.animate_reset_position(start_x, start_y, target_x, target_y, step + 1),
            )
            return
        self.root.geometry(f"+{target_x}+{target_y}")
        self.resetting_position = False
        self.store.update_position(target_x, target_y)
        self.set_action("idle", 1.0, force=True)
        self.bubble.show("我跳回屏幕角落啦。", target_x + WIDTH // 2, target_y + (HEIGHT - DISPLAY_SIZE) // 2)

    def happy(self) -> None:
        self.happy_direction = self.next_horizontal_direction()
        self.happy_start = (self.root.winfo_x(), self.root.winfo_y())
        self.set_action(self.happy_action_for_direction(self.happy_direction), 2.0)
        self.say(TEXT["happy"])

    def cute(self) -> None:
        self.set_action("cute", 1.9)
        self.say(TEXT["cute"])

    def wave(self) -> None:
        self.set_action("wave", 2.2)
        self.say(TEXT["wave"])

    def sleep(self) -> None:
        self.set_action("sleep_in", 5.0)
        self.say(TEXT["sleep"])

    def walk_right(self) -> None:
        self.walk_direction = self.next_horizontal_direction(1)
        self.set_action("walk" if self.walk_direction > 0 else "walk_left", 1.8)
        self.say(TEXT["walk_right"])

    def walk_left(self) -> None:
        self.walk_direction = self.next_horizontal_direction(-1)
        self.set_action("walk_left" if self.walk_direction < 0 else "walk", 1.8)
        self.say(TEXT["walk_left"])

    def walk(self) -> None:
        direction = self.next_horizontal_direction(random.choice([-1, 1]))
        if direction > 0:
            self.walk_right()
        else:
            self.walk_left()

    def next_horizontal_direction(self, preferred: int | None = None) -> int:
        current_x = self.root.winfo_x()
        max_x = self.root.winfo_screenwidth() - WIDTH - SCREEN_MARGIN
        return bounded_walk_direction(
            current_x,
            SCREEN_MARGIN,
            max_x,
            preferred if preferred is not None else random.choice([-1, 1]),
        )

    def happy_action_for_direction(self, direction: int) -> str:
        return "happy_right" if direction > 0 else "happy"

    def advance_walk(self) -> None:
        current_x = self.root.winfo_x()
        y = self.root.winfo_y()
        max_x = self.root.winfo_screenwidth() - WIDTH - SCREEN_MARGIN
        self.walk_direction = bounded_walk_direction(current_x, SCREEN_MARGIN, max_x, self.walk_direction)
        self.action = "walk_left" if self.walk_direction < 0 else "walk"
        x = next_walk_x(current_x, self.walk_direction, SCREEN_MARGIN, max_x)
        self.root.geometry(f"+{x}+{y}")
        self.bubble.move_to_pet(x + WIDTH // 2, y + (HEIGHT - DISPLAY_SIZE) // 2)

    def advance_happy(self) -> None:
        if self.happy_start is None:
            self.happy_start = (self.root.winfo_x(), self.root.winfo_y())
        start_x, start_y = self.happy_start
        max_x = self.root.winfo_screenwidth() - WIDTH - SCREEN_MARGIN
        self.happy_direction = bounded_walk_direction(start_x, SCREEN_MARGIN, max_x, self.happy_direction)
        self.action = self.happy_action_for_direction(self.happy_direction)
        phase = min(1.0, self.frame / max(1, self.action_frame_count() - 1))
        hop = math.sin(math.pi * phase)
        x = max(SCREEN_MARGIN, min(max_x, start_x + round(self.happy_direction * HAPPY_STEP_PX * self.frame)))
        y = max(SCREEN_MARGIN, start_y - round(HAPPY_HOP_PX * hop))
        self.root.geometry(f"+{x}+{y}")
        self.bubble.move_to_pet(x + WIDTH // 2, y + (HEIGHT - DISPLAY_SIZE) // 2)

    def on_press(self, event) -> None:
        self.drag_start = (event.x_root, event.y_root)
        self.window_start = (self.root.winfo_x(), self.root.winfo_y())
        self.press_action = self.action
        self.drag_moved = False
        if self.action in {"sleep", "sleep_in"}:
            self.set_action("wake", 4.0, force=self.action == "sleep")
            self.say(TEXT["wake"])
        else:
            self.set_action("clicked", 1.4)
            self.say(TEXT["pet"])

    def on_drag(self, event) -> None:
        if not self.drag_start or not self.window_start:
            return
        self.drag_moved = True
        self.action = "drag"
        dx = event.x_root - self.drag_start[0]
        dy = event.y_root - self.drag_start[1]
        x = self.window_start[0] + dx
        y = self.window_start[1] + dy
        self.root.geometry(f"+{x}+{y}")
        self.bubble.move_to_pet(x + WIDTH // 2, y + (HEIGHT - DISPLAY_SIZE) // 2)

    def on_release(self, _event) -> None:
        press_action = self.press_action
        drag_moved = self.drag_moved
        self.drag_start = None
        self.window_start = None
        self.press_action = None
        self.drag_moved = False
        self.store.update_position(self.root.winfo_x(), self.root.winfo_y())
        if not drag_moved and press_action in {"sleep", "sleep_in"} and self.action == "wake":
            return
        if drag_moved:
            self.set_action("idle", 1.0, force=True)
            self.bubble.move_to_pet(*self.pet_anchor())

    def on_menu(self, event) -> None:
        menu = Menu(self.root, tearoff=0)
        menu.add_command(label="\u5f00\u5fc3\u4e00\u4e0b", command=self.happy)
        menu.add_command(label="卖萌一下", command=self.cute)
        menu.add_command(label="\u6253\u4e2a\u62db\u547c", command=self.wave)
        menu.add_command(label="向左散步", command=self.walk_left)
        menu.add_command(label="向右散步", command=self.walk_right)
        menu.add_command(label="\u8d34\u7740\u7761\u4f1a\u513f", command=self.sleep)
        menu.add_separator()
        menu.add_command(label="我想他了", command=self.miss_partner)
        menu.add_command(label="今天辛苦啦", command=self.tired_today)
        menu.add_separator()
        menu.add_command(
            label=low_distraction_menu_label(self.store.config.low_distraction_mode),
            command=self.toggle_low_distraction_mode,
        )
        menu.add_command(label="回到屏幕角落", command=self.reset_position)
        menu.add_command(label="打开配置文件", command=self.open_config)
        menu.add_command(label="打开配置文件夹", command=self.open_config_folder)
        menu.add_command(label="编辑陪伴语料", command=self.open_companion_message_pack)
        menu.add_separator()
        menu.add_command(label="\u9000\u51fa rig \u9884\u89c8", command=self.quit)
        menu.tk_popup(event.x_root, event.y_root)

    def quit(self) -> None:
        self.bubble.window.destroy()
        self.root.destroy()


StableDesktopCatApp = RigDesktopCatApp


class CandidateDesktopCatApp(RigDesktopCatApp):
    def __init__(
        self,
        batch_id: str,
        enable_time_reminders: bool = True,
        enable_companion_messages: bool = True,
        low_distraction_mode: bool | None = None,
        test_rhythm_time: datetime | None = None,
        test_first_launch: bool = False,
    ) -> None:
        super().__init__(
            frame_source_factory=lambda: ProductionBatchFrameSource(batch_id),
            title=f"DesktopCat Candidate Preview - {batch_id}",
            enable_time_reminders=enable_time_reminders,
            enable_companion_messages=enable_companion_messages,
            low_distraction_mode=low_distraction_mode,
            test_rhythm_time=test_rhythm_time,
            test_first_launch=test_first_launch,
        )
