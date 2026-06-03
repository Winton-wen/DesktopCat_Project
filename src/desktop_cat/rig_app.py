from __future__ import annotations

import random
import math
import time
import tkinter as tk
from tkinter import Menu
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageTk

from .config import ConfigStore
from .paths import app_root
from .sprite_manifest import ACTIONS
from .time_reminders import reminder_for_time


TRANSPARENT = "#fff7f0"
WIDTH = 280
HEIGHT = 240
DISPLAY_SIZE = 165
WALK_STEP_PX = 4
HAPPY_STEP_PX = 2
HAPPY_HOP_PX = 14
SCREEN_MARGIN = 8
SPEECH_BUBBLE_PET_OVERLAP_PX = 40
TIME_REMINDER_CHECK_MS = 5 * 60 * 1000
ACTION_FPS = {
    "idle": 12,
    "blink": 10,
    "wave": 12,
    "clicked": 12,
    "happy": 24,
    "happy_right": 24,
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
        self.label = tk.Label(
            self.window,
            text="",
            bg="white",
            fg="#111111",
            font=("Microsoft YaHei UI", 10),
            padx=14,
            pady=8,
            bd=2,
            relief="solid",
        )
        self.label.pack()
        self.after_id: str | None = None

    def show(self, text: str, pet_center_x: int, pet_top_y: int) -> None:
        self.label.configure(text=text)
        self.window.update_idletasks()
        w = self.window.winfo_reqwidth()
        h = self.window.winfo_reqheight()
        x, y = speech_bubble_geometry(self.root.winfo_screenwidth(), pet_center_x, pet_top_y, w, h)
        self.window.geometry(f"+{x}+{y}")
        self.window.deiconify()
        self.window.lift()
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.after_id = self.root.after(3200, self.window.withdraw)

    def move_to_pet(self, pet_center_x: int, pet_top_y: int) -> None:
        if not self.window.winfo_viewable():
            return
        self.show(self.label.cget("text"), pet_center_x, pet_top_y)


class RigDesktopCatApp:
    def __init__(
        self,
        frame_source: StableSpriteFrameSource | None = None,
        frame_source_factory=None,
        title: str = "DesktopCat Stable Preview",
        enable_time_reminders: bool = True,
    ) -> None:
        self.store = ConfigStore()
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
        self.time_reminders_shown: set[str] = set()

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_menu)
        self.canvas.bind("<Double-Button-1>", lambda _event: self.wave())

        self.place_initially()
        self.draw()
        self.root.after(120, self.tick)
        if enable_time_reminders:
            self.root.after(1500, self.check_time_reminder)

    def run(self) -> None:
        self.root.mainloop()

    def place_initially(self) -> None:
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{sw - WIDTH - 28}+{sh - HEIGHT - 56}")

    def action_frame_count(self) -> int:
        return {
            "blink": 10,
            "clicked": 9,
            "drag": 8,
            "happy": 48,
            "happy_right": 48,
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
            self.action = ACTION_CHAIN.get(self.action, "idle")
            self.frame = 0
            self.action_until = now + random.uniform(1.2, 2.2)
        elif now > self.action_until and self.action == "idle" and not self.drag_start:
            self.random_idle_action(now)
        if self.action in {"happy", "happy_right"} and not self.drag_start:
            self.advance_happy()
        elif self.action in {"walk", "walk_left"} and not self.drag_start:
            self.advance_walk()
        self.draw()
        self.root.after(max(16, round(1000 / ACTION_FPS.get(self.action, 12))), self.tick)

    def random_idle_action(self, now: float) -> None:
        action = random.choices(["idle", "blink", "wave", "happy", "cute", "sleep_in", "walk"], weights=[58, 22, 5, 5, 4, 2, 4], k=1)[0]
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

    def set_action(self, action: str, seconds: float) -> None:
        self.action = action
        self.frame = 0
        self.action_until = time.monotonic() + seconds
        if action not in {"happy", "happy_right"}:
            self.happy_start = None
        self.draw()

    def pet_anchor(self) -> tuple[int, int]:
        return self.root.winfo_x() + WIDTH // 2, self.root.winfo_y() + (HEIGHT - DISPLAY_SIZE) // 2

    def say(self, text: str) -> None:
        self.bubble.show(text, *self.pet_anchor())

    def check_time_reminder(self, now: datetime | None = None) -> None:
        current = now or datetime.now()
        reminder = reminder_for_time(current.time())
        if reminder:
            reminder_key = f"{current.date().isoformat()}:{reminder.key}"
            if reminder_key not in self.time_reminders_shown:
                self.time_reminders_shown.add(reminder_key)
                self.say(reminder.message)
        self.root.after(TIME_REMINDER_CHECK_MS, self.check_time_reminder)

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
            self.set_action("wake", 4.0)
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
        self.set_action("idle", 1.0)

    def on_menu(self, event) -> None:
        menu = Menu(self.root, tearoff=0)
        menu.add_command(label="\u5f00\u5fc3\u4e00\u4e0b", command=self.happy)
        menu.add_command(label="卖萌一下", command=self.cute)
        menu.add_command(label="\u6253\u4e2a\u62db\u547c", command=self.wave)
        menu.add_command(label="向左散步", command=self.walk_left)
        menu.add_command(label="向右散步", command=self.walk_right)
        menu.add_command(label="\u8d34\u7740\u7761\u4f1a\u513f", command=self.sleep)
        menu.add_separator()
        menu.add_command(label="\u9000\u51fa rig \u9884\u89c8", command=self.quit)
        menu.tk_popup(event.x_root, event.y_root)

    def quit(self) -> None:
        self.bubble.window.destroy()
        self.root.destroy()


StableDesktopCatApp = RigDesktopCatApp


class CandidateDesktopCatApp(RigDesktopCatApp):
    def __init__(self, batch_id: str, enable_time_reminders: bool = True) -> None:
        super().__init__(
            frame_source_factory=lambda: ProductionBatchFrameSource(batch_id),
            title=f"DesktopCat Candidate Preview - {batch_id}",
            enable_time_reminders=enable_time_reminders,
        )
