import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from desktop_cat.rig_app import CandidateDesktopCatApp


DEFAULT_BATCH_ID = "20260527_motion_quality_v1"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("batch_id", nargs="?", default=DEFAULT_BATCH_ID)
    parser.add_argument("--smoke-ms", type=int, help="Start the preview, then close it after this many milliseconds.")
    args = parser.parse_args()

    app = CandidateDesktopCatApp(args.batch_id)
    if args.smoke_ms:
        app.root.after(args.smoke_ms, app.quit)
    app.run()
    if args.smoke_ms:
        print(f"candidate_preview_smoke_ok batch={args.batch_id}")
