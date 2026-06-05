import argparse
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from desktop_cat.rig_app import CandidateDesktopCatApp


DEFAULT_BATCH_ID = "20260527_motion_quality_v1"


def parse_test_reminder_time(value: str) -> datetime:
    try:
        parsed_time = datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use HH:MM in 24-hour time, for example 17:00") from exc
    now = datetime.now()
    return datetime.combine(now.date(), parsed_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("batch_id", nargs="?", default=DEFAULT_BATCH_ID)
    parser.add_argument("--smoke-ms", type=int, help="Start the preview, then close it after this many milliseconds.")
    parser.add_argument(
        "--test-reminder-time",
        type=parse_test_reminder_time,
        help="Show the reminder for an HH:MM test time and disable real-time reminder checks.",
    )
    parser.add_argument(
        "--test-companion-time",
        type=parse_test_reminder_time,
        help="Show an offline companion message for an HH:MM test time.",
    )
    parser.add_argument(
        "--test-rhythm-time",
        type=parse_test_reminder_time,
        help="Preview idle action choices as if the current time were HH:MM.",
    )
    parser.add_argument(
        "--low-distraction",
        action="store_true",
        help="Preview the candidate with quieter idle behavior and less frequent companion messages.",
    )
    parser.add_argument(
        "--test-first-launch",
        action="store_true",
        help="Preview the one-time arrival message without marking first launch as completed.",
    )
    args = parser.parse_args()

    app = CandidateDesktopCatApp(
        args.batch_id,
        enable_time_reminders=False if args.test_reminder_time or args.test_companion_time else True,
        enable_companion_messages=False if args.test_companion_time else True,
        low_distraction_mode=args.low_distraction,
        test_rhythm_time=args.test_rhythm_time,
        test_first_launch=args.test_first_launch,
    )
    if args.test_reminder_time:
        app.root.after(800, lambda: app.check_time_reminder(args.test_reminder_time))
    if args.test_companion_time:
        app.root.after(800, lambda: app.check_companion_message(args.test_companion_time))
    if args.smoke_ms:
        app.root.after(args.smoke_ms, app.quit)
    app.run()
    if args.smoke_ms:
        print(f"candidate_preview_smoke_ok batch={args.batch_id}")
