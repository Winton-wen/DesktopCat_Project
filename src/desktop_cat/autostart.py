import os
import sys
from pathlib import Path


STARTUP_FILE = "DesktopCat.bat"


def startup_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return Path.home()
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def startup_path() -> Path:
    return startup_dir() / STARTUP_FILE


def is_enabled() -> bool:
    return startup_path().exists()


def _launch_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    root = Path(__file__).resolve().parents[2]
    pythonw = root / ".petvenv" / "Scripts" / "pythonw.exe"
    python = pythonw if pythonw.exists() else Path(sys.executable)
    return f'cd /d "{root}" && "{python}" launcher.py'


def set_enabled(enabled: bool) -> None:
    target = startup_path()
    if enabled:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f'@echo off\r\nstart "" {_launch_command()}\r\n', encoding="utf-8")
        return
    if target.exists():
        target.unlink()
