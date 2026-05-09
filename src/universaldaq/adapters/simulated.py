from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Mapping

from universaldaq.common import SignalQuality, as_event_time

from .models import (
    AdapterCapability,
    AdapterCommandOutcome,
    AdapterCommandRequest,
    AdapterCommandResult,
    AdapterHealth,
    AdapterHealthState,
    AdapterKind,
    AdapterOperationMode,
    AdapterPointRef,
    AdapterPollResult,
    PointClass,
    PointSnapshot,
)


@dataclass(slots=True)
class SimulatedReadAdapter:
    adapter_id: str
    points: dict[str, PointSnapshot]
    metadata: Mapping[str, str] = field(default_factory=dict)

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            adapter_id=self.adapter_id,
            adapter_kind=AdapterKind.SIMULATED,
            operation_mode=AdapterOperationMode.POLLED,
            readable_points=tuple(snapshot.point for snapshot in self.points.values()),
            is_simulated=True,
            metadata=self.metadata,
        )

    def health(self) -> AdapterHealth:
        return AdapterHealth(adapter_id=self.adapter_id, state=AdapterHealthState.HEALTHY, summary='simulated read adapter healthy')

    def poll(self, *, timestamp: int) -> AdapterPollResult:
        ts = as_event_time(timestamp)
        snapshots = tuple(
            replace(snapshot, received_timestamp=ts, stale=ts > snapshot.source_timestamp)
            for snapshot in self.points.values()
        )
        return AdapterPollResult(
            adapter_id=self.adapter_id,
            polled_at=ts,
            snapshots=snapshots,
            health=self.health(),
            diagnostics=({'adapter_id': self.adapter_id, 'snapshot_count': len(snapshots)},),
        )

    def submit_command(self, request: AdapterCommandRequest) -> AdapterCommandResult:
        return AdapterCommandResult(
            request=request,
            outcome=AdapterCommandOutcome.DEVICE_REJECTED,
            reason='read-only simulated adapter',
            health=AdapterHealth(adapter_id=self.adapter_id, state=AdapterHealthState.DEGRADED, summary='write attempted on read-only adapter'),
        )

    @classmethod
    def from_values(cls, *, adapter_id: str, values: Mapping[str, tuple[str, str, str | None]], timestamp: int) -> 'SimulatedReadAdapter':
        ts = as_event_time(timestamp)
        points = {}
        for point_id, (raw_value, engineering_value, units) in values.items():
            point = AdapterPointRef(
                adapter_id=adapter_id,
                point_id=point_id,
                display_name=point_id,
                point_class=PointClass.STATUS,
                units=units,
            )
            points[point_id] = PointSnapshot(
                point=point,
                raw_value=raw_value,
                engineering_value=engineering_value,
                quality=SignalQuality.SIMULATED,
                source_timestamp=ts,
                received_timestamp=ts,
                stale=False,
            )
        return cls(adapter_id=adapter_id, points=points)


@dataclass(slots=True)
class SimulatedWritableAdapter:
    adapter_id: str
    writable_points: dict[str, str] = field(default_factory=dict)
    observed_points: dict[str, str] = field(default_factory=dict)
    fail_transport_for: set[str] = field(default_factory=set)
    reject_targets: set[str] = field(default_factory=set)
    metadata: Mapping[str, str] = field(default_factory=dict)

    def capability(self) -> AdapterCapability:
        readable = tuple(
            AdapterPointRef(adapter_id=self.adapter_id, point_id=point_id, display_name=point_id, point_class=PointClass.STATUS)
            for point_id in sorted(self.observed_points)
        )
        writable = tuple(
            AdapterPointRef(adapter_id=self.adapter_id, point_id=point_id, display_name=point_id, point_class=PointClass.COMMAND)
            for point_id in sorted(self.writable_points)
        )
        return AdapterCapability(
            adapter_id=self.adapter_id,
            adapter_kind=AdapterKind.SIMULATED,
            operation_mode=AdapterOperationMode.POLLED,
            readable_points=readable,
            writable_points=writable,
            service_capabilities=('self_test',),
            is_simulated=True,
            metadata=self.metadata,
        )

    def health(self) -> AdapterHealth:
        return AdapterHealth(adapter_id=self.adapter_id, state=AdapterHealthState.HEALTHY, summary='simulated writable adapter healthy')

    def poll(self, *, timestamp: int) -> AdapterPollResult:
        ts = as_event_time(timestamp)
        snapshots = tuple(
            PointSnapshot(
                point=AdapterPointRef(adapter_id=self.adapter_id, point_id=point_id, display_name=point_id, point_class=PointClass.STATUS),
                raw_value=value,
                engineering_value=value,
                quality=SignalQuality.SIMULATED,
                source_timestamp=ts,
                received_timestamp=ts,
                stale=False,
            )
            for point_id, value in sorted(self.observed_points.items())
        )
        return AdapterPollResult(adapter_id=self.adapter_id, polled_at=ts, snapshots=snapshots, health=self.health())

    def submit_command(self, request: AdapterCommandRequest) -> AdapterCommandResult:
        if request.point_id not in self.writable_points:
            return AdapterCommandResult(
                request=request,
                outcome=AdapterCommandOutcome.TARGET_NOT_FOUND,
                reason='point is not writable on this adapter',
                health=AdapterHealth(adapter_id=self.adapter_id, state=AdapterHealthState.ERROR, summary='unknown writable point'),
            )
        if request.point_id in self.fail_transport_for:
            return AdapterCommandResult(
                request=request,
                outcome=AdapterCommandOutcome.TRANSPORT_FAILED,
                reason='simulated transport failure',
                health=AdapterHealth(
                    adapter_id=self.adapter_id,
                    state=AdapterHealthState.DEGRADED,
                    summary='simulated transport failure',
                    consecutive_failures=1,
                    last_failure_at=request.requested_at,
                ),
            )
        if request.point_id in self.reject_targets:
            return AdapterCommandResult(
                request=request,
                outcome=AdapterCommandOutcome.DEVICE_REJECTED,
                reason='simulated device rejection',
                transmitted_at=request.requested_at,
                health=AdapterHealth(adapter_id=self.adapter_id, state=AdapterHealthState.DEGRADED, summary='simulated device rejection'),
            )
        self.writable_points[request.point_id] = request.requested_value
        self.observed_points[request.point_id] = request.requested_value
        return AdapterCommandResult(
            request=request,
            outcome=AdapterCommandOutcome.OBSERVED,
            transmitted_at=request.requested_at,
            observed_value=request.requested_value,
            observed_at=request.requested_at,
            health=self.health(),
        )
