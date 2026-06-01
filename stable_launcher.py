from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from desktop_cat.rig_app import StableDesktopCatApp


if __name__ == "__main__":
    StableDesktopCatApp().run()
