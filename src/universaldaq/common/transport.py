from __future__ import annotations

from typing import NotRequired, TypedDict


class TraceEvent(TypedDict):
    t: int
    event: str
    state: NotRequired[str]
    result: NotRequired[str]
    reason: NotRequired[str]
    observed: NotRequired[str]
    expected: NotRequired[str]
    actor: NotRequired[str]
    mode: NotRequired[str]
    alarm: NotRequired[str]


class WorkspacePayload(TypedDict):
    page: str
    review_mode: str
