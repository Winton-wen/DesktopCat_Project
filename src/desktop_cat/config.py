import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .paths import app_root, user_config_dir


APP_NAME = "DesktopCat"
PET_NAME = "\u5446\u5446"
MAMA_NICKNAME = "\u9ebb\u9ebb"
PAPA_NICKNAME = "\u7c91\u7c91"
PARTNER_NICKNAME = MAMA_NICKNAME
DEFAULT_COMPANION_MESSAGE_PACK = "assets/companion_messages/partner_default.json"
USER_COMPANION_MESSAGE_PACK = "companion_messages/partner_custom.json"
README_NAME = "README.txt"
README_TEXT = """DesktopCat 配置说明

呆呆是麻麻和粑粑一起养的电子小猫。

config.json 里的称呼设置：
- pet_name: 小猫名字，默认“呆呆”。
- mama_nickname: 呆呆对她的称呼，默认“麻麻”。
- papa_nickname: 呆呆对你的称呼，默认“粑粑”。
- partner_nickname: 旧版本兼容字段，一般不用再修改。

其他设置：
- low_distraction_mode: true 表示更安静，false 表示正常陪伴。
- companion_message_pack: 当前使用的陪伴语料文件路径。
- first_launch_completed: 是否已经显示过首次欢迎语。
- last_position: 呆呆上次停留的位置。

companion_messages/partner_custom.json 是高级自定义陪伴语料文件。
text 支持 {pet_name}、{mama_nickname}、{papa_nickname}。
周年纪念日还可以使用 {anniversary_year_cn} 自动显示中文周年数。
也可以调整 category、cooldown_hours 和 action。
公历特殊日子使用 category=special_day 和 MM-DD 格式的 month_day，例如 07-18。
农历特殊日子使用 category=special_day 和 MM-DD 格式的 lunar_month_day，例如 08-15。

如果自定义语料改坏了，删除 partner_custom.json，程序会继续使用内置默认语料。
"""

DEFAULT_MESSAGES: list[str] = []

@dataclass
class CatConfig:
    pet_name: str = PET_NAME
    mama_nickname: str = MAMA_NICKNAME
    papa_nickname: str = PAPA_NICKNAME
    partner_nickname: str = PARTNER_NICKNAME
    messages: list[str] = field(default_factory=lambda: DEFAULT_MESSAGES.copy())
    autostart: bool = False
    low_distraction_mode: bool = False
    first_launch_completed: bool = False
    companion_message_pack: str = DEFAULT_COMPANION_MESSAGE_PACK
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
        config.pet_name = self._text_or_default(raw.get("pet_name"), config.pet_name)
        config.partner_nickname = self._text_or_default(raw.get("partner_nickname"), config.partner_nickname)
        config.mama_nickname = self._text_or_default(
            raw.get("mama_nickname"),
            config.partner_nickname,
        )
        config.papa_nickname = self._text_or_default(raw.get("papa_nickname"), config.papa_nickname)
        messages = raw.get("messages")
        if isinstance(messages, list) and all(isinstance(item, str) for item in messages):
            config.messages = [item for item in messages if item.strip()] or config.messages
        config.autostart = raw["autostart"] if isinstance(raw.get("autostart"), bool) else config.autostart
        config.low_distraction_mode = (
            raw["low_distraction_mode"]
            if isinstance(raw.get("low_distraction_mode"), bool)
            else config.low_distraction_mode
        )
        config.first_launch_completed = (
            raw["first_launch_completed"]
            if isinstance(raw.get("first_launch_completed"), bool)
            else config.first_launch_completed
        )
        config.companion_message_pack = self._text_or_default(
            raw.get("companion_message_pack"),
            config.companion_message_pack,
        )
        pos = raw.get("last_position")
        if isinstance(pos, dict) and type(pos.get("x")) is int and type(pos.get("y")) is int:
            config.last_position = {"x": pos["x"], "y": pos["y"]}
        return config

    def _text_or_default(self, value: Any, default: str) -> str:
        if not isinstance(value, str):
            return default
        stripped = value.strip()
        return stripped or default

    def save(self, config: CatConfig | None = None) -> None:
        if config is not None:
            self.config = config
        self._ensure_dir()
        payload = {
            "pet_name": self.config.pet_name,
            "mama_nickname": self.config.mama_nickname,
            "papa_nickname": self.config.papa_nickname,
            "partner_nickname": self.config.partner_nickname,
            "messages": self.config.messages,
            "autostart": self.config.autostart,
            "low_distraction_mode": self.config.low_distraction_mode,
            "first_launch_completed": self.config.first_launch_completed,
            "companion_message_pack": self.config.companion_message_pack,
            "last_position": self.config.last_position,
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def update_position(self, x: int, y: int) -> None:
        self.config.last_position = {"x": x, "y": y}
        self.save()

    def update_low_distraction_mode(self, enabled: bool) -> None:
        self.config.low_distraction_mode = enabled
        self.save()

    def mark_first_launch_completed(self) -> None:
        self.config.first_launch_completed = True
        try:
            self.save()
        except OSError:
            pass

    def open_file(self) -> Path:
        self._ensure_dir()
        if not self.path.exists():
            self.save()
        self.ensure_readme()
        return self.path

    def ensure_readme(self) -> Path:
        self._ensure_dir()
        readme_path = self.dir / README_NAME
        if not readme_path.exists():
            readme_path.write_text(README_TEXT, encoding="utf-8")
        return readme_path

    def open_folder(self) -> Path:
        self._ensure_dir()
        if not self.path.exists():
            self.save()
        self.ensure_readme()
        return self.dir

    def default_companion_message_pack_path(self) -> Path:
        return app_root() / DEFAULT_COMPANION_MESSAGE_PACK

    def companion_message_pack_path(self) -> Path:
        configured = Path(self.config.companion_message_pack)
        candidates = []
        if configured.is_absolute():
            candidates.append(configured)
        else:
            candidates.append(app_root() / configured)
            candidates.append(self.dir / configured)
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return self.default_companion_message_pack_path()

    def open_companion_message_pack_file(self) -> Path:
        self._ensure_dir()
        self.ensure_readme()
        editable_path = self.dir / USER_COMPANION_MESSAGE_PACK
        editable_path.parent.mkdir(parents=True, exist_ok=True)
        if not editable_path.exists():
            shutil.copyfile(self.default_companion_message_pack_path(), editable_path)
        self.config.companion_message_pack = USER_COMPANION_MESSAGE_PACK
        self.save()
        return editable_path
