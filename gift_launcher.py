import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from desktop_cat.rig_app import ProductionBatchFrameSource, RigDesktopCatApp


DEFAULT_BATCH_ID = "20260527_motion_quality_v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the gift-ready DesktopCat build.")
    parser.add_argument("--smoke-ms", type=int, help="Start the pet, then close after this many milliseconds.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    app = RigDesktopCatApp(
        frame_source_factory=lambda: ProductionBatchFrameSource(DEFAULT_BATCH_ID),
        title="DesktopCat",
    )
    if args.smoke_ms:
        app.root.after(args.smoke_ms, app.quit)
    app.run()
