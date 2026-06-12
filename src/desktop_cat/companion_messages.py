from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
import json
from pathlib import Path
import random
import re

from .paths import app_root


DEFAULT_COMPANION_CHECK_MS = 25 * 60 * 1000
COMPANION_PLACEHOLDER_PATTERN = re.compile(
    r"(?<!\{)\{(pet_name|mama_nickname|papa_nickname)\}(?!\})"
)
ANNIVERSARY_PLACEHOLDER_PATTERN = re.compile(
    r"(?<!\{)\{anniversary_year_cn\}(?!\})"
)
ANNIVERSARY_BASE_YEAR = 2024
GENERAL_COMPANION_CATEGORIES = {
    "miss_you",
    "busy_support",
    "comfort",
    "encouragement",
}


@dataclass(frozen=True)
class CompanionMessage:
    id: str
    category: str
    text: str
    cooldown_hours: int
    action: str
    month_day: str | None = None
    lunar_month_day: str | None = None


@dataclass(frozen=True)
class CompanionMessagePack:
    messages: list[CompanionMessage]


def render_companion_text(
    text: str,
    *,
    pet_name: str,
    mama_nickname: str,
    papa_nickname: str,
    current: datetime | None = None,
) -> str:
    values = {
        "pet_name": pet_name,
        "mama_nickname": mama_nickname,
        "papa_nickname": papa_nickname,
    }
    rendered = COMPANION_PLACEHOLDER_PATTERN.sub(
        lambda match: values[match.group(1)],
        text,
    )
    anniversary_year = max(1, (current or datetime.now()).year - ANNIVERSARY_BASE_YEAR)
    return ANNIVERSARY_PLACEHOLDER_PATTERN.sub(
        lambda _match: chinese_number(anniversary_year),
        rendered,
        count=1,
    ) if "{anniversary_year_cn}" in rendered else rendered


def chinese_number(number: int) -> str:
    digits = "零一二三四五六七八九"
    if number < 10:
        return digits[number]
    if number < 20:
        return "十" + (digits[number % 10] if number % 10 else "")
    if number < 100:
        return digits[number // 10] + "十" + (
            digits[number % 10] if number % 10 else ""
        )
    return str(number)


def companion_category_for_time(current: time) -> str:
    minutes = current.hour * 60 + current.minute
    if 1 * 60 + 30 <= minutes < 5 * 60:
        return "late_night"
    if 7 * 60 <= minutes < 11 * 60 + 30:
        return "morning"
    if 11 * 60 + 30 <= minutes < 13 * 60 + 30:
        return "lunch"
    if 13 * 60 + 30 <= minutes < 18 * 60:
        return "afternoon"
    if 18 * 60 <= minutes < 22 * 60 + 30:
        return "evening"
    return "bedtime"


def companion_message_is_due(
    current: datetime,
    message: CompanionMessage,
    last_shown_at: dict[str, datetime],
) -> bool:
    previous = last_shown_at.get(message.id)
    if previous is None:
        return True
    return current - previous >= timedelta(hours=message.cooldown_hours)


LUNAR_SPECIAL_DAYS_BY_YEAR = {
    2026: {
        "01-01": "02-17",
        "01-15": "03-03",
        "05-05": "06-19",
        "07-07": "08-19",
        "08-15": "09-25",
        "09-09": "10-18",
    },
    2027: {
        "01-01": "02-06",
        "01-15": "02-20",
        "05-05": "06-09",
        "07-07": "08-08",
        "08-15": "09-15",
        "09-09": "10-08",
    },
    2028: {
        "01-01": "01-26",
        "01-15": "02-09",
        "05-05": "05-28",
        "07-07": "08-26",
        "08-15": "10-03",
        "09-09": "10-26",
    },
    2029: {
        "01-01": "02-13",
        "01-15": "02-27",
        "05-05": "06-16",
        "07-07": "08-16",
        "08-15": "09-22",
        "09-09": "10-16",
    },
    2030: {
        "01-01": "02-03",
        "01-15": "02-17",
        "05-05": "06-05",
        "07-07": "08-05",
        "08-15": "09-12",
        "09-09": "10-06",
    },
}


def lunar_month_day_matches(current: datetime, lunar_month_day: str | None) -> bool:
    if not lunar_month_day:
        return False
    return LUNAR_SPECIAL_DAYS_BY_YEAR.get(current.year, {}).get(lunar_month_day) == current.strftime("%m-%d")


def select_companion_message(
    current: datetime,
    messages: list[CompanionMessage],
    last_shown_at: dict[str, datetime],
) -> CompanionMessage | None:
    today = current.strftime("%m-%d")
    special_day_candidates = [
        message
        for message in messages
        if message.category == "special_day"
        and (message.month_day == today or lunar_month_day_matches(current, message.lunar_month_day))
        and companion_message_is_due(current, message, last_shown_at)
    ]
    if special_day_candidates:
        return sorted(special_day_candidates, key=lambda message: message.id)[0]

    category = companion_category_for_time(current.time())
    candidates = [
        message
        for message in messages
        if (
            message.category == category
            or message.category in GENERAL_COMPANION_CATEGORIES
        )
        and companion_message_is_due(current, message, last_shown_at)
    ]
    if not candidates:
        return None
    return random.choice(candidates)


def load_companion_pack(path: Path) -> CompanionMessagePack:
    raw = json.loads(path.read_text(encoding="utf-8"))
    messages: list[CompanionMessage] = []
    for item in raw.get("messages", []):
        if not isinstance(item, dict):
            continue
        message_id = str(item.get("id") or "").strip()
        category = str(item.get("category") or "").strip()
        text = str(item.get("text") or "").strip()
        if not message_id or not category or not text:
            continue
        messages.append(
            CompanionMessage(
                id=message_id,
                category=category,
                text=text,
                cooldown_hours=max(1, min(72, int(item.get("cooldown_hours") or 24))),
                action=str(item.get("action") or "wave"),
                month_day=str(item.get("month_day") or "").strip() or None,
                lunar_month_day=str(item.get("lunar_month_day") or "").strip() or None,
            )
        )
    if not messages:
        raise ValueError(f"No valid companion messages in {path}")
    return CompanionMessagePack(messages=messages)


def load_default_companion_pack() -> CompanionMessagePack:
    return load_companion_pack(app_root() / "assets" / "companion_messages" / "partner_default.json")
