from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from time import perf_counter
from typing import Iterator, Mapping


@dataclass(slots=True)
class TimingStat:
    count: int = 0
    total_ms: float = 0.0
    max_ms: float = 0.0
    min_ms: float | None = None

    def observe(self, duration_ms: float) -> None:
        self.count += 1
        self.total_ms += duration_ms
        self.max_ms = max(self.max_ms, duration_ms)
        self.min_ms = duration_ms if self.min_ms is None else min(self.min_ms, duration_ms)

    def as_dict(self) -> dict[str, float | int | None]:
        average_ms = 0.0 if self.count == 0 else self.total_ms / self.count
        return {
            'count': self.count,
            'total_ms': round(self.total_ms, 6),
            'average_ms': round(average_ms, 6),
            'max_ms': round(self.max_ms, 6),
            'min_ms': None if self.min_ms is None else round(self.min_ms, 6),
        }


@dataclass(slots=True)
class RuntimeMetricsStore:
    counters: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    timings: dict[str, TimingStat] = field(default_factory=dict)
    gauges: dict[str, int | float | str] = field(default_factory=dict)

    def increment(self, metric_name: str, amount: int = 1) -> None:
        self.counters[metric_name] += amount

    def increment_many(self, metric_amounts: Mapping[str, int]) -> None:
        for metric_name, amount in metric_amounts.items():
            self.increment(metric_name, amount)

    def observe_duration(self, metric_name: str, duration_ms: float) -> None:
        stat = self.timings.setdefault(metric_name, TimingStat())
        stat.observe(duration_ms)

    def set_gauge(self, metric_name: str, value: int | float | str) -> None:
        self.gauges[metric_name] = value

    def set_gauges(self, metric_values: Mapping[str, int | float | str]) -> None:
        self.gauges.update(metric_values)

    @contextmanager
    def measure(self, metric_name: str) -> Iterator[None]:
        start = perf_counter()
        try:
            yield
        finally:
            self.observe_duration(metric_name, (perf_counter() - start) * 1000.0)

    def snapshot(self) -> dict[str, object]:
        return {
            'counters': dict(sorted(self.counters.items())),
            'timings': {name: stat.as_dict() for name, stat in sorted(self.timings.items())},
            'gauges': dict(sorted(self.gauges.items())),
        }


class NullMetrics:
    def increment(self, metric_name: str, amount: int = 1) -> None:
        return None

    def increment_many(self, metric_amounts: Mapping[str, int]) -> None:
        return None

    def observe_duration(self, metric_name: str, duration_ms: float) -> None:
        return None

    def set_gauge(self, metric_name: str, value: int | float | str) -> None:
        return None

    def set_gauges(self, metric_values: Mapping[str, int | float | str]) -> None:
        return None

    @contextmanager
    def measure(self, metric_name: str) -> Iterator[None]:
        yield

    def snapshot(self) -> dict[str, object]:
        return {'counters': {}, 'timings': {}, 'gauges': {}}
