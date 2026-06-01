from __future__ import annotations

import os
import random
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import Menu
from typing import Callable

from PIL import Image, ImageTk
import pystray

from . import autostart
from .config import ConfigStore
from .paths import app_root
from .sprite_manifest import ACTIONS


TRANSPARENT = "#fff7f0"
WIDTH = 280
HEIGHT = 240
DISPLAY_SIZE = 150
ACTION_FPS = {action.name: action.fps for action in ACTIONS}
LOOPING_ACTIONS = {"idle", "sleep", "walk", "walk_left", "drag"}

TEXT = {
    "arrive": "\u6765\u966a\u4f60\u5566\u3002",
    "back": "\u6211\u56de\u6765\u5566\u3002",
    "pet": "\u6478\u6478\u5934\uff0c\u597d\u8212\u670d\u3002",
    "happy": "\u770b\u5230\u4f60\u5c31\u5f00\u5fc3\u3002",
    "wave": "\u55e8\uff0c\u6211\u5728\u8fd9\u91cc\u5440\u3002",
    "sleep": "\u6211\u772f\u5566\uff0c\u8d34\u4e00\u4f1a\u513f\u3002",
    "wake": "\u9192\u5566\uff0c\u518d\u966a\u4f60\u3002",
    "reset": "\u6211\u4e56\u4e56\u56de\u5230\u89d2\u843d\u5566\u3002",
    "auto_on": "\u4ee5\u540e\u5f00\u673a\u5c31\u6765\u627e\u4f60\u3002",
    "auto_off": "\u597d\u5440\uff0c\u6211\u5148\u4e0d\u81ea\u542f\u3002",
}

MENU = {
    "toggle": "\u663e\u793a/\u9690\u85cf",
    "happy": "\u5f00\u5fc3\u4e00\u4e0b",
    "wave": "\u6253\u4e2a\u62db\u547c",
    "sleep": "\u8d34\u7740\u7761\u4f1a\u513f",
    "autostart": "\u968f Windows \u542f\u52a8",
    "reset": "\u91cd\u7f6e\u4f4d\u7f6e",
    "config": "\u6253\u5f00\u914d\u7f6e\u6587\u4ef6",
    "quit": "\u9000\u51fa",
}

class SpeechBubble:
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
        self.font = tkfont.Font(family="Microsoft YaHei UI", size=10)
        self.after_id: str | None = None
        self.canvas_w = 1
        self.canvas_h = 1

    def show(self, text: str, pet_center_x: int, pet_top_y: int) -> None:
        padding_x = 18
        padding_y = 12
        tail_h = 22
        border = 3
        max_text_w = 190
        text_w = min(max_text_w, max(72, self.font.measure(text)))
        lines = max(1, (self.font.measure(text) + max_text_w - 1) // max_text_w)
        text_h = self.font.metrics("linespace") * lines
        bubble_w = text_w + padding_x * 2 + border * 2
        bubble_h = text_h + padding_y * 2 + border * 2
        self.canvas_w = bubble_w + 10
        self.canvas_h = bubble_h + tail_h + 8
        x, y = self.geometry_for_pet(pet_center_x, pet_top_y)
        tail_x = max(28, min(pet_center_x - x, self.canvas_w - 28))

        self.canvas.configure(width=self.canvas_w, height=self.canvas_h)
        c = self.canvas
        c.delete("all")
        outline = "#111111"
        fill = "#ffffff"
        left = 5
        top = 5
        right = left + bubble_w
        bottom = top + bubble_h
        c.create_rectangle(left, top, right, bottom, fill=fill, outline=outline, width=border)
        c.create_polygon(tail_x - 10, bottom - 1, tail_x + 10, bottom - 1, tail_x, bottom + tail_h, fill=fill, outline=outline, width=border)
        c.create_line(tail_x - 9, bottom, tail_x + 9, bottom, fill=fill, width=border + 1)
        c.create_text(self.canvas_w // 2, top + bubble_h // 2, text=text, width=text_w, fill="#111111", font=self.font, justify="center")
        self.window.geometry(f"{self.canvas_w}x{self.canvas_h}+{x}+{y}")
        self.window.deiconify()
        self.window.lift()
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.after_id = self.root.after(4200, self.window.withdraw)

    def geometry_for_pet(self, pet_center_x: int, pet_top_y: int) -> tuple[int, int]:
        screen_w = self.root.winfo_screenwidth()
        x = max(8, min(pet_center_x - self.canvas_w // 2, screen_w - self.canvas_w - 8))
        y = max(8, pet_top_y - self.canvas_h + 8)
        return x, y

    def move_to_pet(self, pet_center_x: int, pet_top_y: int) -> None:
        if not self.window.winfo_viewable():
            return
        x, y = self.geometry_for_pet(pet_center_x, pet_top_y)
        self.window.geometry(f"+{x}+{y}")


class SpriteLoader:
    def __init__(self) -> None:
        self.root = app_root() / "assets" / "sprites"
        self.frames: dict[str, list[ImageTk.PhotoImage]] = {}
        self.load()

    def load(self) -> None:
        for action in ACTIONS:
            folder = self.root / action.name
            images = []
            for path in sorted(folder.glob("*.png")):
                img = Image.open(path).convert("RGBA")
                img.thumbnail((DISPLAY_SIZE, DISPLAY_SIZE), Image.Resampling.LANCZOS)
                images.append(ImageTk.PhotoImage(img))
            if images:
                self.frames[action.name] = images
        if "idle" not in self.frames:
            raise RuntimeError("Missing idle sprites. Run tools/process_generated_strips.py first.")

    def get(self, action: str, index: int) -> ImageTk.PhotoImage:
        frames = self.frames.get(action) or self.frames["idle"]
        return frames[index % len(frames)]

    def count(self, action: str) -> int:
        return len(self.frames.get(action) or self.frames["idle"])


class DesktopCatApp:
    def __init__(self) -> None:
        self.store = ConfigStore()
        self.root = tk.Tk()
        self.root.title("DesktopCat")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=TRANSPARENT)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg=TRANSPARENT, highlightthickness=0)
        self.canvas.pack()
        self.loader = SpriteLoader()
        self.sprite = self.canvas.create_image(WIDTH // 2, HEIGHT // 2, anchor="center")
        self.bubble = SpeechBubble(self.root)
        self.action = "idle"
        self.frame = 0
        self.action_until = 0.0
        self.idle_bridge_until = 0.0
        self.drag_start: tuple[int, int] | None = None
        self.window_start: tuple[int, int] | None = None
        self.hidden = False
        self.direction = 1
        self.sleeping = False
        self.tray: pystray.Icon | None = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_menu)
        self.canvas.bind("<Double-Button-1>", lambda _event: self.wave())

        self.place_initially()
        self.make_tray()
        self.draw()
        self.root.after(1200, lambda: self.say(self.store.config.pet_name + TEXT["arrive"]))
        self.root.after(120, self.tick)
        self.root.after(30000, self.random_message)

    def run(self) -> None:
        self.root.mainloop()

    def place_initially(self) -> None:
        pos = self.store.config.last_position
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = pos["x"] if pos else sw - WIDTH - 28
        y = pos["y"] if pos else sh - HEIGHT - 56
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{max(0, x)}+{max(0, y)}")

    def draw(self) -> None:
        img = self.loader.get(self.action, self.frame)
        self.canvas.itemconfigure(self.sprite, image=img)
        self.canvas.image = img

    def tick(self) -> None:
        self.frame += 1
        now = time.monotonic()
        if self.action not in LOOPING_ACTIONS and self.frame >= self.loader.count(self.action):
            if self.action == "sleep_in":
                self.sleeping = True
                self.action = "sleep"
                self.frame = 0
                self.action_until = float("inf")
            elif self.action == "wake":
                self.sleeping = False
                self.action = "idle"
                self.frame = 0
                self.action_until = now + random.uniform(0.8, 1.2)
            else:
                self.action = "idle"
                self.frame = 0
                self.action_until = now + random.uniform(0.45, 0.8)
        if now > self.action_until and not self.drag_start:
            self.advance_idle_state(now)
        if self.action in {"walk", "walk_left"} and not self.drag_start and not self.hidden:
            self.step_walk()
        self.draw()
        delay = max(42, round(1000 / ACTION_FPS.get(self.action, 12)))
        self.root.after(delay, self.tick)

    def advance_idle_state(self, now: float) -> None:
        if self.sleeping:
            return
        if self.action != "idle":
            self.action = "idle"
            self.frame = 0
            self.idle_bridge_until = now + random.uniform(0.45, 0.8)
            self.action_until = self.idle_bridge_until
            return
        if now < self.idle_bridge_until:
            return
        action = random.choices(
            ["idle", "blink", "walk", "happy", "wave", "sleep_in"],
            weights=[68, 18, 4, 4, 3, 2],
            k=1,
        )[0]
        if action == "walk":
            self.choose_walk_direction()
            action = self.walk_action()
        self.action = action
        self.action_until = now + random.uniform(2.8, 8.0)
        self.frame = 0

    def step_walk(self) -> None:
        x, y = self.root.winfo_x(), self.root.winfo_y()
        sw = self.root.winfo_screenwidth()
        left_limit = 0
        right_limit = max(0, sw - WIDTH)
        if x <= left_limit + 2:
            self.direction = 1
        elif x >= right_limit - 2:
            self.direction = -1
        expected_action = self.walk_action()
        if self.action != expected_action:
            self.action = expected_action
            self.frame = 0
        nx = x + self.direction * 2
        if nx < left_limit:
            nx = left_limit
            self.direction = 1
            self.action = self.walk_action()
            self.frame = 0
        elif nx > right_limit:
            nx = right_limit
            self.direction = -1
            self.action = self.walk_action()
            self.frame = 0
        self.root.geometry(f"+{nx}+{y}")

    def choose_walk_direction(self) -> None:
        x = self.root.winfo_x()
        right_limit = max(0, self.root.winfo_screenwidth() - WIDTH)
        if x <= 24:
            self.direction = 1
        elif x >= right_limit - 24:
            self.direction = -1
        else:
            self.direction = random.choice([-1, 1])

    def walk_action(self) -> str:
        return "walk" if self.direction > 0 else "walk_left"

    def set_action(self, action: str, seconds: float = 4.5) -> None:
        self.sleeping = action == "sleep"
        self.action = action
        self.action_until = time.monotonic() + seconds
        self.frame = 0
        self.draw()

    def pet_anchor(self) -> tuple[int, int]:
        pet_center_x = self.root.winfo_x() + WIDTH // 2
        pet_top_y = self.root.winfo_y() + (HEIGHT - DISPLAY_SIZE) // 2
        return pet_center_x, pet_top_y

    def move_bubble_to_pet(self) -> None:
        self.bubble.move_to_pet(*self.pet_anchor())

    def say(self, text: str) -> None:
        self.bubble.show(text, *self.pet_anchor())

    def happy(self) -> None:
        self.set_action("happy", 3.2)
        self.say(TEXT["happy"])

    def wave(self) -> None:
        self.set_action("wave", 3.2)
        self.say(TEXT["wave"])

    def sleep(self) -> None:
        self.sleeping = False
        self.set_action("sleep_in", 2.0)
        self.say(TEXT["sleep"])

    def wake(self) -> None:
        self.sleeping = False
        self.set_action("wake", 1.8)
        self.say(TEXT["wake"])

    def is_sleeping_state(self) -> bool:
        return self.sleeping or self.action in {"sleep_in", "sleep"}

    def random_message(self) -> None:
        if not self.hidden and not self.is_sleeping_state() and self.store.config.messages:
            self.say(random.choice(self.store.config.messages))
        self.root.after(random.randint(24000, 42000), self.random_message)

    def on_press(self, event) -> None:
        self.drag_start = (event.x_root, event.y_root)
        self.window_start = (self.root.winfo_x(), self.root.winfo_y())
        if self.sleeping or self.action in {"sleep", "sleep_in"}:
            self.wake()
            return
        self.set_action("clicked", 2.8)
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

    def on_menu(self, event) -> None:
        menu = Menu(self.root, tearoff=0)
        self.fill_menu(menu)
        menu.tk_popup(event.x_root, event.y_root)

    def fill_menu(self, menu: Menu) -> None:
        menu.add_command(label=MENU["happy"], command=self.happy)
        menu.add_command(label=MENU["wave"], command=self.wave)
        menu.add_command(label=MENU["sleep"], command=self.sleep)
        menu.add_separator()
        menu.add_command(label=MENU["toggle"], command=self.toggle_visible)
        menu.add_command(label=MENU["reset"], command=self.reset_position)
        menu.add_command(label=MENU["config"], command=self.open_config)
        menu.add_separator()
        menu.add_command(label=MENU["quit"], command=self.quit)

    def tray_image(self) -> Image.Image:
        image = Image.open(app_root() / "assets" / "sprites" / "idle" / "00.png").convert("RGBA")
        image.thumbnail((64, 64), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        canvas.alpha_composite(image, ((64 - image.width) // 2, (64 - image.height) // 2))
        return canvas

    def make_tray(self) -> None:
        menu = pystray.Menu(
            pystray.MenuItem(MENU["happy"], self.tray_call(self.happy)),
            pystray.MenuItem(MENU["wave"], self.tray_call(self.wave)),
            pystray.MenuItem(MENU["sleep"], self.tray_call(self.sleep)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(MENU["toggle"], self.tray_call(self.toggle_visible)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(MENU["autostart"], self.tray_call(self.toggle_autostart), checked=lambda _item: autostart.is_enabled()),
            pystray.MenuItem(MENU["reset"], self.tray_call(self.reset_position)),
            pystray.MenuItem(MENU["config"], self.tray_call(self.open_config)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(MENU["quit"], self.tray_call(self.quit)),
        )
        self.tray = pystray.Icon("DesktopCat", self.tray_image(), "DesktopCat", menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

    def tray_call(self, callback: Callable) -> Callable:
        def wrapped(_icon=None, _item=None) -> None:
            self.root.after(0, callback)

        return wrapped

    def toggle_visible(self) -> None:
        self.hidden = not self.hidden
        if self.hidden:
            self.root.withdraw()
            self.bubble.window.withdraw()
        else:
            self.root.deiconify()
            self.root.lift()
            self.say(TEXT["back"])

    def toggle_autostart(self) -> None:
        enabled = not autostart.is_enabled()
        autostart.set_enabled(enabled)
        self.store.config.autostart = enabled
        self.store.save()
        self.say(TEXT["auto_on"] if enabled else TEXT["auto_off"])

    def reset_position(self) -> None:
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x, y = sw - WIDTH - 28, sh - HEIGHT - 56
        self.root.geometry(f"+{x}+{y}")
        self.store.update_position(x, y)
        self.bubble.show(TEXT["reset"], x + WIDTH // 2, y + (HEIGHT - DISPLAY_SIZE) // 2)

    def open_config(self) -> None:
        os.startfile(str(self.store.open_file()))

    def quit(self) -> None:
        if self.tray:
            self.tray.stop()
        self.bubble.window.destroy()
        self.root.destroy()
