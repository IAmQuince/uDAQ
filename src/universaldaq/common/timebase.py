from __future__ import annotations

from typing import NewType

EventTime = NewType("EventTime", int)


def as_event_time(value: int) -> EventTime:
    return EventTime(value)
