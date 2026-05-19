from __future__ import annotations

from dataclasses import dataclass


LAYOUT_SCHEMA_VERSION = 3
_GRAPH_PRESENTATIONS = {
    'operate': 'primary',
    'session_review': 'primary',
    'logic_designer': 'compact_pip',
    'system': 'compact_pip',
}


@dataclass(frozen=True, slots=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height


@dataclass(frozen=True, slots=True)
class ShellGeometryDecision:
    requested: Rect
    resolved: Rect
    clamped: bool
    reason: str


@dataclass(frozen=True, slots=True)
class PipDecision:
    requested: Rect
    resolved: Rect
    clamped: bool



def default_window_rect(
    *,
    available: Rect,
    width_ratio: float = 0.84,
    height_ratio: float = 0.84,
    min_width: int = 1180,
    min_height: int = 760,
) -> Rect:
    width = max(min_width, min(int(available.width * width_ratio), available.width))
    height = max(min_height, min(int(available.height * height_ratio), available.height))
    width = min(width, available.width)
    height = min(height, available.height)
    x = available.x + max(0, (available.width - width) // 2)
    y = available.y + max(0, (available.height - height) // 2)
    return Rect(x=x, y=y, width=width, height=height)



def clamp_window_rect(*, requested: Rect, available: Rect, min_width: int = 960, min_height: int = 640) -> ShellGeometryDecision:
    width = max(min_width, min(requested.width, available.width))
    height = max(min_height, min(requested.height, available.height))
    width = min(width, available.width)
    height = min(height, available.height)
    x = requested.x
    y = requested.y
    if x < available.x:
        x = available.x
    if y < available.y:
        y = available.y
    if x + width > available.right:
        x = available.right - width
    if y + height > available.bottom:
        y = available.bottom - height
    resolved = Rect(x=x, y=y, width=width, height=height)
    clamped = resolved != requested
    if clamped:
        return ShellGeometryDecision(requested=requested, resolved=resolved, clamped=True, reason='requested geometry exceeded available screen bounds or minimum-size policy')
    return ShellGeometryDecision(requested=requested, resolved=resolved, clamped=False, reason='requested geometry already fits available screen bounds')



def default_graph_presentation_for_workspace(workspace_id: str) -> str:
    return _GRAPH_PRESENTATIONS.get(workspace_id, 'primary')



def normalize_splitter_sizes(*, total: int, requested: tuple[int, ...], minimums: tuple[int, ...]) -> tuple[int, ...]:
    if len(requested) != len(minimums):
        raise ValueError('requested and minimums must have equal length')
    if not requested:
        return ()
    total = max(total, sum(minimums))
    adjusted = [max(req, minimums[index]) for index, req in enumerate(requested)]
    current = sum(adjusted)
    if current == total:
        return tuple(adjusted)
    if current < total:
        adjusted[0] += total - current
        return tuple(adjusted)
    overflow = current - total
    for index in range(len(adjusted) - 1, -1, -1):
        allowed = adjusted[index] - minimums[index]
        if allowed <= 0:
            continue
        delta = min(allowed, overflow)
        adjusted[index] -= delta
        overflow -= delta
        if overflow == 0:
            break
    if overflow > 0:
        adjusted[0] = max(minimums[0], adjusted[0] - overflow)
    return tuple(adjusted)



def default_pip_rect(*, bounds: Rect, mode: str = 'compact_pip', margin: int = 12) -> Rect:
    if mode == 'primary':
        width = max(360, int(bounds.width * 0.72))
        height = max(240, int(bounds.height * 0.70))
        x = bounds.x + max(margin, (bounds.width - width) // 2)
        y = bounds.y + max(margin, (bounds.height - height) // 2)
    else:
        width = max(300, int(bounds.width * 0.34))
        height = max(190, int(bounds.height * 0.28))
        x = bounds.right - width - margin
        y = bounds.bottom - height - margin
    return clamp_pip_rect(
        requested=Rect(x=x, y=y, width=width, height=height),
        bounds=bounds,
        margin=margin,
    ).resolved


def clamp_pip_rect(*, requested: Rect, bounds: Rect, min_width: int = 280, min_height: int = 180, margin: int = 12) -> PipDecision:
    width = max(min_width, min(requested.width, max(min_width, bounds.width - margin * 2)))
    height = max(min_height, min(requested.height, max(min_height, bounds.height - margin * 2)))
    max_x = max(bounds.x + margin, bounds.right - margin - width)
    max_y = max(bounds.y + margin, bounds.bottom - margin - height)
    x = min(max(requested.x, bounds.x + margin), max_x)
    y = min(max(requested.y, bounds.y + margin), max_y)
    resolved = Rect(x=x, y=y, width=width, height=height)
    return PipDecision(requested=requested, resolved=resolved, clamped=resolved != requested)



def serialize_rect(rect: Rect) -> dict[str, int]:
    return {'x': rect.x, 'y': rect.y, 'width': rect.width, 'height': rect.height}



def deserialize_rect(payload: dict[str, int] | None) -> Rect | None:
    if not payload:
        return None
    required = {'x', 'y', 'width', 'height'}
    if not required.issubset(payload):
        return None
    return Rect(x=int(payload['x']), y=int(payload['y']), width=int(payload['width']), height=int(payload['height']))
