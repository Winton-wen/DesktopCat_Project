import os
import sys
from pathlib import Path


APP_DIR_NAME = "DesktopCat"


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2]


def user_config_dir() -> Path:
    override = os.environ.get("DESKTOPCAT_CONFIG_DIR")
    if override:
        return Path(override)
    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / APP_DIR_NAME
    return app_root() / "user_data"
