from __future__ import annotations

import argparse
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from desktop_cat.companion_messages import CompanionMessage
from desktop_cat.rig_app import CandidateDesktopCatApp


DEFAULT_BATCH_ID = "20260527_motion_quality_v1"
DEFAULT_ACTIONS = "idle,blink,wave,clicked,happy,sleep_in,sleep,wake,walk,walk_left,cute,drag"
PYTEST_TARGETS = [
    "tests/test_stable_sprite_route.py",
    "tests/test_production_pipeline.py",
    "tests/test_rig_preview.py",
    "tests/test_companion_messages.py",
    "tests/test_low_distraction_mode.py",
    "tests/test_time_rhythm.py",
    "tests/test_speech_bubble_polish.py",
    "tests/test_gift_config_experience.py",
    "tests/test_candidate_feature_qa_script.py",
]


@dataclass
class CommandResult:
    name: str
    command: list[str]
    returncode: int
    seconds: float
    output: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0


def run_command(name: str, command: list[str]) -> CommandResult:
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
    )
    return CommandResult(
        name=name,
        command=command,
        returncode=completed.returncode,
        seconds=time.monotonic() - started,
        output=completed.stdout,
    )


def backend_commands(batch_id: str, fast: bool) -> list[tuple[str, list[str]]]:
    if fast:
        pytest_targets = [
            "tests/test_rig_preview.py",
            "tests/test_companion_messages.py",
            "tests/test_low_distraction_mode.py",
            "tests/test_time_rhythm.py",
            "tests/test_speech_bubble_polish.py",
            "tests/test_gift_config_experience.py",
            "tests/test_candidate_feature_qa_script.py",
        ]
        actions = "idle,blink,wake"
    else:
        pytest_targets = PYTEST_TARGETS
        actions = DEFAULT_ACTIONS
    return [
        ("pytest", [sys.executable, "-m", "pytest", *pytest_targets]),
        (
            "production-batch-qa",
            [
                sys.executable,
                "tools/run_production_batch_qa.py",
                "--batch",
                batch_id,
                "--actions",
                actions,
            ],
        ),
    ]


def run_backend_qa(batch_id: str, fast: bool, results: queue.Queue[CommandResult]) -> None:
    for name, command in backend_commands(batch_id, fast):
        result = run_command(name, command)
        results.put(result)


def write_report(report_dir: Path, batch_id: str, results: list[CommandResult]) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"candidate_feature_qa_{timestamp}.txt"
    lines = [
        "DesktopCat candidate feature QA",
        f"Batch: {batch_id}",
        f"Created: {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        lines.extend(
            [
                f"[{status}] {result.name} ({result.seconds:.1f}s)",
                "Command: " + " ".join(result.command),
                result.output.rstrip(),
                "",
            ]
        )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


class VisualFeatureTour:
    def __init__(
        self,
        app: CandidateDesktopCatApp,
        backend_results: queue.Queue[CommandResult],
        expected_backend_results: int,
        step_ms: int,
        report_dir: Path,
        batch_id: str,
    ) -> None:
        self.app = app
        self.backend_results = backend_results
        self.expected_backend_results = expected_backend_results
        self.step_ms = step_ms
        self.report_dir = report_dir
        self.batch_id = batch_id
        self.results: list[CommandResult] = []
        self.started_at = time.monotonic()

    def start(self) -> None:
        self.schedule(300, self.intro)
        self.schedule(self.step_ms * 1, self.show_first_launch_message)
        self.schedule(self.step_ms * 2, self.show_morning_companion_message)
        self.schedule(self.step_ms * 3, self.show_time_reminder)
        self.schedule(self.step_ms * 4, self.happy)
        self.schedule(self.step_ms * 5, self.cute)
        self.schedule(self.step_ms * 6, self.wave)
        self.schedule(self.step_ms * 7, self.walk_left)
        self.schedule(self.step_ms * 8, self.walk_right)
        self.schedule(self.step_ms * 9, self.sleep)
        self.schedule(self.step_ms * 10, self.wake_from_sleep)
        self.schedule(self.step_ms * 11, self.toggle_low_distraction_mode)
        self.schedule(self.step_ms * 12, self.reset_position)
        self.schedule(self.step_ms * 13, self.show_backend_progress)
        self.schedule(self.step_ms * 14, self.maybe_finish)

    def schedule(self, delay_ms: int, callback) -> None:
        self.app.root.after(delay_ms, callback)

    def intro(self) -> None:
        self.app.say("自动巡检开始：前台展示视觉效果，后台测试功能。")

    def show_first_launch_message(self) -> None:
        self.app.show_first_launch_message()

    def show_morning_companion_message(self) -> None:
        message = CompanionMessage(
            id="qa_visual_companion",
            category="morning",
            text="这是陪伴语料气泡：会按时间出现，也会自动换动作。",
            cooldown_hours=1,
            action="wave",
        )
        self.app.show_companion_message(message)

    def show_time_reminder(self) -> None:
        self.app.check_time_reminder(datetime(2026, 6, 5, 17, 30))

    def happy(self) -> None:
        self.app.happy()

    def cute(self) -> None:
        self.app.cute()

    def wave(self) -> None:
        self.app.wave()

    def walk_left(self) -> None:
        self.app.walk_left()

    def walk_right(self) -> None:
        self.app.walk_right()

    def sleep(self) -> None:
        self.app.sleep()

    def wake_from_sleep(self) -> None:
        self.app.set_action("wake", 3.0)
        self.app.say("现在展示睡醒动画。")

    def toggle_low_distraction_mode(self) -> None:
        self.app.toggle_low_distraction_mode()

    def reset_position(self) -> None:
        screen_h = self.app.root.winfo_screenheight()
        y = max(8, screen_h - 320)
        self.app.root.geometry(f"+24+{y}")
        self.app.bubble.move_to_pet(24 + 140, y + 37)
        self.app.reset_position()

    def drain_backend_results(self) -> None:
        while True:
            try:
                self.results.append(self.backend_results.get_nowait())
            except queue.Empty:
                break

    def show_backend_progress(self) -> None:
        self.drain_backend_results()
        passed = sum(1 for result in self.results if result.passed)
        total = len(self.results)
        self.app.say(f"后台测试进度：{passed}/{total} 项已通过。")

    def maybe_finish(self) -> None:
        self.drain_backend_results()
        if len(self.results) < self.expected_backend_results:
            self.app.say("前端巡演已完成，正在等待后台测试收尾。")
            self.schedule(2000, self.maybe_finish)
            return
        report_path = write_report(self.report_dir, self.batch_id, self.results)
        failed = [result for result in self.results if not result.passed]
        if failed:
            self.app.say(f"巡检完成：{len(failed)} 项后台测试失败，报告已写入。")
        else:
            self.app.say("巡检完成：前端已展示，后台测试全部通过。")
        print(f"candidate_feature_qa_report={report_path}")
        print(f"candidate_feature_qa_elapsed={time.monotonic() - self.started_at:.1f}s")
        self.schedule(3500, self.app.quit)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show DesktopCat visual features while backend QA runs.")
    parser.add_argument("batch_id", nargs="?", default=DEFAULT_BATCH_ID)
    parser.add_argument("--backend-only", action="store_true", help="Run backend QA without opening the visual tour.")
    parser.add_argument("--visual-only", action="store_true", help="Show the visual tour without backend QA.")
    parser.add_argument("--fast", action="store_true", help="Use a shorter backend suite for quick local checks.")
    parser.add_argument("--smoke", action="store_true", help="Use shorter visual timing and fast backend checks.")
    parser.add_argument("--step-ms", type=int, default=2600, help="Delay between visual tour steps.")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "qa_reports", help="Directory for text QA reports.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    step_ms = 2400 if args.smoke else args.step_ms
    fast = args.fast or args.smoke
    results: queue.Queue[CommandResult] = queue.Queue()
    commands = [] if args.visual_only else backend_commands(args.batch_id, fast)

    if args.backend_only and args.visual_only:
        raise SystemExit("Choose at most one of --backend-only and --visual-only.")

    if args.backend_only:
        completed = [run_command(name, command) for name, command in commands]
        report_path = write_report(args.report_dir, args.batch_id, completed)
        for result in completed:
            status = "PASS" if result.passed else "FAIL"
            print(f"[{status}] {result.name} ({result.seconds:.1f}s)")
        print(f"candidate_feature_qa_report={report_path}")
        return 0 if all(result.passed for result in completed) else 1

    if commands:
        threading.Thread(
            target=run_backend_qa,
            args=(args.batch_id, fast, results),
            daemon=True,
        ).start()

    with tempfile.TemporaryDirectory(prefix="desktopcat_feature_qa_") as temp_dir:
        old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
        os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
        try:
            app = CandidateDesktopCatApp(
                args.batch_id,
                enable_time_reminders=False,
                enable_companion_messages=False,
                test_first_launch=True,
            )
            tour = VisualFeatureTour(
                app=app,
                backend_results=results,
                expected_backend_results=len(commands),
                step_ms=step_ms,
                report_dir=args.report_dir,
                batch_id=args.batch_id,
            )
            tour.start()
            app.run()
            return 0 if all(result.passed for result in tour.results) else 1
        finally:
            if old_config_dir is None:
                os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
            else:
                os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir


if __name__ == "__main__":
    raise SystemExit(main())
