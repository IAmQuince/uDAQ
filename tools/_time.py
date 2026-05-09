from __future__ import annotations

from datetime import datetime, timezone


def timestamp_slug(*, now: datetime | None = None) -> str:
    current = datetime.now(timezone.utc) if now is None else now.astimezone(timezone.utc)
    return current.strftime('%Y-%m-%d_%H%M%S')


def iso_timestamp_utc(*, now: datetime | None = None) -> str:
    current = datetime.now(timezone.utc) if now is None else now.astimezone(timezone.utc)
    return current.isoformat(timespec='seconds').replace('+00:00', 'Z')
