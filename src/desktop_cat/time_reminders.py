from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta


@dataclass(frozen=True)
class TimeReminder:
    key: str
    message: str


TIME_REMINDER_REPEAT = timedelta(minutes=10)


LUNCH_REMINDER = TimeReminder("lunch", "小猪猪要乖乖按时吃午饭哟！")
DINNER_REMINDER = TimeReminder("dinner", "小猪猪要乖乖按时吃晚饭哟！")
BEDTIME_REMINDER = TimeReminder("bedtime", "要早点休息呀小猪猪")
LATE_NIGHT_REMINDER = TimeReminder("late_night", "小猪猪还在忙嘛...熬夜工作辛苦惹，要记得喝点水喔！")


def _minutes(value: time) -> int:
    return value.hour * 60 + value.minute


def _in_window(current: time, start_hour: int, start_minute: int, end_hour: int, end_minute: int) -> bool:
    current_minute = _minutes(current)
    start = start_hour * 60 + start_minute
    end = end_hour * 60 + end_minute
    return start <= current_minute < end


def reminder_for_time(current: time) -> TimeReminder | None:
    if _in_window(current, 11, 30, 13, 30):
        return LUNCH_REMINDER
    if _in_window(current, 17, 0, 19, 0):
        return DINNER_REMINDER
    if _in_window(current, 0, 0, 1, 30):
        return BEDTIME_REMINDER
    if _in_window(current, 1, 30, 5, 0):
        return LATE_NIGHT_REMINDER
    return None


def reminder_instance_key(current: datetime, reminder: TimeReminder | None) -> str | None:
    if reminder is None:
        return None
    return f"{current.date().isoformat()}:{reminder.key}"


def reminder_is_due(
    current: datetime,
    reminder: TimeReminder | None,
    last_shown_at: dict[str, datetime],
    dismissed_keys: set[str],
) -> bool:
    key = reminder_instance_key(current, reminder)
    if key is None or key in dismissed_keys:
        return False
    previous = last_shown_at.get(key)
    return previous is None or current - previous >= TIME_REMINDER_REPEAT
