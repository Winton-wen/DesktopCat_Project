from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
import json
from pathlib import Path

from .paths import app_root


DEFAULT_COMPANION_CHECK_MS = 25 * 60 * 1000


@dataclass(frozen=True)
class CompanionMessage:
    id: str
    category: str
    text: str
    cooldown_hours: int
    action: str


@dataclass(frozen=True)
class CompanionMessagePack:
    messages: list[CompanionMessage]


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


def select_companion_message(
    current: datetime,
    messages: list[CompanionMessage],
    last_shown_at: dict[str, datetime],
) -> CompanionMessage | None:
    category = companion_category_for_time(current.time())
    candidates = [
        message
        for message in messages
        if message.category == category and companion_message_is_due(current, message, last_shown_at)
    ]
    if not candidates:
        candidates = [
            message
            for message in messages
            if message.category in {"miss_you", "busy_support", "comfort", "encouragement"}
            and companion_message_is_due(current, message, last_shown_at)
        ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda message: message.id)[0]


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
            )
        )
    return CompanionMessagePack(messages=messages)


def load_default_companion_pack() -> CompanionMessagePack:
    return load_companion_pack(app_root() / "assets" / "companion_messages" / "partner_default.json")
