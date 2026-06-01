from __future__ import annotations

import random
import time
import tkinter as tk
from tkinter import Menu
from pathlib import Path

from PIL import Image, ImageTk

from .config import ConfigStore
from .paths import app_root
from .sprite_manifest import ACTIONS


TRANSPARENT = "#fff7f0"
WIDTH = 280
HEIGHT = 240
DISPLAY_SIZE = 165
WALK_STEP_PX = 4
SCREEN_MARGIN = 8
ACTION_FPS = {
    "idle": 12,
    "blink": 10,
    "wave": 12,
    "clicked": 12,
    "happy": 24,
    "sleep_in": 10,
    "sleep": 8,
    "wake": 10,
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
            for path in sorted(folder.glob("*.png")):
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
        screen_w = self.root.winfo_screenwidth()
        x = max(8, min(pet_center_x - w // 2, screen_w - w - 8))
        y = max(8, pet_top_y - h - 8)
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
        self.walk_direction = 1

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_menu)
        self.canvas.bind("<Double-Button-1>", lambda _event: self.wave())

        self.place_initially()
        self.draw()
        self.root.after(120, self.tick)

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
            "cute": 44,
            "sleep_in": 11,
            "sleep": 11,
            "wake": 11,
            "walk": 14,
            "walk_left": 14,
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
        if self.action in {"walk", "walk_left"} and not self.drag_start:
            self.advance_walk()
        self.draw()
        self.root.after(max(42, round(1000 / ACTION_FPS.get(self.action, 12))), self.tick)

    def random_idle_action(self, now: float) -> None:
        action = random.choices(["idle", "blink", "wave", "happy", "cute", "sleep_in", "walk"], weights=[58, 22, 5, 5, 4, 2, 4], k=1)[0]
        self.action = action
        self.frame = 0
        self.action_until = now + random.uniform(3.0, 6.0)

    def set_action(self, action: str, seconds: float) -> None:
        self.action = action
        self.frame = 0
        self.action_until = time.monotonic() + seconds
        self.draw()

    def pet_anchor(self) -> tuple[int, int]:
        return self.root.winfo_x() + WIDTH // 2, self.root.winfo_y() + (HEIGHT - DISPLAY_SIZE) // 2

    def say(self, text: str) -> None:
        self.bubble.show(text, *self.pet_anchor())

    def happy(self) -> None:
        self.set_action("happy", 2.0)
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
        self.walk_direction = 1
        self.set_action("walk", 1.8)
        self.say(TEXT["walk_right"])

    def walk_left(self) -> None:
        self.walk_direction = -1
        self.set_action("walk_left", 1.8)
        self.say(TEXT["walk_left"])

    def walk(self) -> None:
        if random.choice([True, False]):
            self.walk_right()
        else:
            self.walk_left()

    def advance_walk(self) -> None:
        current_x = self.root.winfo_x()
        y = self.root.winfo_y()
        max_x = self.root.winfo_screenwidth() - WIDTH - SCREEN_MARGIN
        x = next_walk_x(current_x, self.walk_direction, SCREEN_MARGIN, max_x)
        self.root.geometry(f"+{x}+{y}")
        self.bubble.move_to_pet(x + WIDTH // 2, y + (HEIGHT - DISPLAY_SIZE) // 2)

    def on_press(self, event) -> None:
        self.drag_start = (event.x_root, event.y_root)
        self.window_start = (self.root.winfo_x(), self.root.winfo_y())
        if self.action in {"sleep", "sleep_in"}:
            self.set_action("wake", 1.2)
            self.say(TEXT["wake"])
        else:
            self.set_action("clicked", 1.4)
            self.say(TEXT["pet"])

    def on_drag(self, event) -> None:
        if not self.drag_start or not self.window_start:
            return
        self.action = "drag"
        dx = event.x_root - self.drag_start[0]
        dy = event.y_root - self.drag_start[1]
        x = self.window_start[0] + dx
        y = self.window_start[1] + dy
        self.root.geometry(f"+{x}+{y}")
        self.bubble.move_to_pet(x + WIDTH // 2, y + (HEIGHT - DISPLAY_SIZE) // 2)

    def on_release(self, _event) -> None:
        self.drag_start = None
        self.window_start = None
        self.store.update_position(self.root.winfo_x(), self.root.winfo_y())
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
    def __init__(self, batch_id: str) -> None:
        super().__init__(
            frame_source_factory=lambda: ProductionBatchFrameSource(batch_id),
            title=f"DesktopCat Candidate Preview - {batch_id}",
        )
