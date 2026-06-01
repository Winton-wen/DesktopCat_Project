import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .paths import app_root, user_config_dir


APP_NAME = "DesktopCat"
PET_NAME = "\u5976\u7cd6\u732b"

DEFAULT_MESSAGES = [
    "\u4eca\u5929\u4e5f\u60f3\u8d34\u8d34\u4f60\u3002",
    "\u6211\u5728\u684c\u9762\u966a\u4f60\u5440\u3002",
    "\u5fd9\u5b8c\u8981\u8bb0\u5f97\u559d\u6c34\u3002",
    "\u6478\u6478\u5934\uff0c\u4eca\u5929\u4e5f\u4f1a\u987a\u5229\u3002",
    "\u770b\u5230\u6211\uff0c\u5c31\u5f53\u6211\u5728\u60f3\u4f60\u3002",
    "\u4e0d\u8981\u592a\u7d2f\uff0c\u6211\u4f1a\u5fc3\u75bc\u3002",
]

@dataclass
class CatConfig:
    pet_name: str = PET_NAME
    messages: list[str] = field(default_factory=lambda: DEFAULT_MESSAGES.copy())
    autostart: bool = False
    last_position: dict[str, int] | None = None


class ConfigStore:
    def __init__(self) -> None:
        self.dir = user_config_dir()
        self.path = self.dir / "config.json"
        self.config = self.load()

    def _ensure_dir(self) -> None:
        try:
            self.dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            self.dir = app_root() / "user_data"
            self.path = self.dir / "config.json"
            self.dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> CatConfig:
        self._ensure_dir()
        if not self.path.exists():
            config = CatConfig()
            self.save(config)
            return config

        try:
            raw: dict[str, Any] = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            backup = self.path.with_suffix(".broken.json")
            try:
                self.path.replace(backup)
            except OSError:
                pass
            config = CatConfig()
            self.save(config)
            return config

        config = CatConfig()
        config.pet_name = str(raw.get("pet_name") or config.pet_name)
        messages = raw.get("messages")
        if isinstance(messages, list) and all(isinstance(item, str) for item in messages):
            config.messages = [item for item in messages if item.strip()] or config.messages
        config.autostart = bool(raw.get("autostart", False))
        pos = raw.get("last_position")
        if isinstance(pos, dict) and isinstance(pos.get("x"), int) and isinstance(pos.get("y"), int):
            config.last_position = {"x": pos["x"], "y": pos["y"]}
        return config

    def save(self, config: CatConfig | None = None) -> None:
        if config is not None:
            self.config = config
        self._ensure_dir()
        payload = {
            "pet_name": self.config.pet_name,
            "messages": self.config.messages,
            "autostart": self.config.autostart,
            "last_position": self.config.last_position,
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def update_position(self, x: int, y: int) -> None:
        self.config.last_position = {"x": x, "y": y}
        self.save()

    def open_file(self) -> Path:
        self._ensure_dir()
        if not self.path.exists():
            self.save()
        return self.path
