from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Iterable, Mapping

from universaldaq.adapters import (
    AdapterCommandRequest,
    AdapterCommandResult,
    AdapterInventoryDiscoveryProvider,
    AdapterManagerService,
    PointSnapshot,
    SimulatedReadAdapter,
    SimulatedWritableAdapter,
    load_optional_support_packs,
    survey_runtime_capabilities,
)
from universaldaq.common import ActorId, OutputId, RequestId, RuntimeMetricsStore, SignalQuality, as_event_time


_MAX_HISTORY = 720


def _build_live_runtime_adapter_manager(
    *,
    load_support_packs: bool,
    support_pack_module_names: Iterable[str] | None,
) -> AdapterManagerService:
    metrics = RuntimeMetricsStore()
    adapters = AdapterManagerService(metrics=metrics)
    adapters.register(
        SimulatedReadAdapter.from_values(
            adapter_id='SIM-READ-001',
            values={
                'PT-101': ('100.0', '100.0', 'psi'),
                'TT-201': ('42.0', '42.0', 'degC'),
            },
            timestamp=1,
        )
    )
    adapters.register(
        SimulatedWritableAdapter(
            adapter_id='SIM-WRITE-001',
            writable_points={'OUT-SMOKE-001': '0', 'OUT-DIAG-001': '0', 'OUT-ADAPT-001': '0'},
            observed_points={'OUT-SMOKE-001': '0', 'OUT-DIAG-001': '0', 'OUT-ADAPT-001': '0'},
        )
    )
    adapters.register_discovery_provider(
        AdapterInventoryDiscoveryProvider(
            provider_id='generic_adapter_inventory',
            capability_inventory_getter=adapters.capability_inventory,
            adapter_getter=lambda adapter_id: adapters.adapters.get(adapter_id),
        )
    )
    if load_support_packs:
        load_optional_support_packs(adapters, module_names=support_pack_module_names)
    return adapters


@dataclass(frozen=True, slots=True)
class LiveRuntimeDeviceRecord:
    device_key: str
    display_name: str
    serial_number: str | None
    transport: str | None
    hardware_mode: str
    writable_point_count: int
    readable_point_count: int
    driver_name: str
    live_capable: bool
    capability_mode: str
    identity_state: str
    read_state: str
    write_state: str
    limited_access_reason: str | None = None


@dataclass(frozen=True, slots=True)
class LiveSignalDescriptor:
    signal_id: str
    point_id: str
    units: str | None
    point_class: str
    source_class: str
    write_safe: bool
    labels_by_lens: Mapping[str, str]
    metadata: Mapping[str, str]

    def label_for_lens(self, lens_id: str) -> str:
        return self.labels_by_lens.get(lens_id) or self.labels_by_lens.get('logical') or self.signal_id


@dataclass(frozen=True, slots=True)
class LiveTraceSeries:
    signal_id: str
    x_values: tuple[float, ...]
    y_values: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class LiveSignalSnapshot:
    descriptor: LiveSignalDescriptor
    value: float
    quality_label: str
    freshness_label: str
    alarm_severity: str
    runtime_source_label: str


@dataclass(frozen=True, slots=True)
class LiveRuntimeSnapshot:
    runtime_mode: str
    connection_state: str
    runtime_source_label: str
    device_label: str
    elapsed_seconds: float
    signal_snapshots: tuple[LiveSignalSnapshot, ...]
    event_log: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WriteTargetDescriptor:
    signal_id: str
    point_id: str
    display_name: str
    target_class: str
    units: str | None


@dataclass(frozen=True, slots=True)
class GuardedWriteDecision:
    allowed: bool
    reason: str
    target_class: str
    point_id: str
    request_value: str
    runtime_mode: str
    posture: str
    result: AdapterCommandResult | None = None


def _install_visible_runtime_specimen(*, services) -> None:
    adapters = services
    specimen_id = 'LIVE-SHELL-IO-001'
    if specimen_id in adapters.adapters:
        return
    adapters.register(
        SimulatedWritableAdapter(
            adapter_id=specimen_id,
            writable_points={
                'analog_out_0': '0.000',
                'digital_out_0': '0',
            },
            observed_points={
                'analog_in_0': '2.100',
                'analog_in_1': '1.650',
                'analog_out_0': '0.000',
                'digital_out_0': '0',
            },
            metadata={
                'display_name': 'Visible Runtime Specimen',
                'vendor': 'UniversalDAQ',
                'model': 'VisibleRuntimeSpecimen',
                'serial_number': 'LIVE-001',
                'transport': 'in_memory',
                'runtime_profile': 'generic_baseline',
            },
        )
    )


class LiveRuntimeEngine:
    """Visible-shell-friendly live runtime bridge.

    The shell talks only to the generic runtime seam. Optional support packs may enrich
    discovery and activation, but the shell keeps one generic specimen path available so
    live-mode read/write posture can be exercised even when no support pack is present.
    """

    def __init__(
        self,
        *,
        load_support_packs: bool = True,
        support_pack_module_names: Iterable[str] | None = None,
    ) -> None:
        self._adapters = _build_live_runtime_adapter_manager(
            load_support_packs=load_support_packs,
            support_pack_module_names=support_pack_module_names,
        )
        _install_visible_runtime_specimen(services=self._adapters)
        self._elapsed_seconds = 0.0
        self._event_log: Deque[str] = deque(maxlen=80)
        self._discovered = tuple()
        self._active_device_key: str | None = None
        self._active_adapter_id: str | None = None
        self._adapter = None
        self._descriptors: tuple[LiveSignalDescriptor, ...] = ()
        self._latest_rows: dict[str, PointSnapshot] = {}
        self._histories: dict[str, Deque[tuple[float, float]]] = {}
        self._runtime_source_label = 'disconnected'
        self._connection_state = 'disconnected'
        self._last_survey_summary: str | None = None
        self._last_support_pack_note: str | None = None
        self._refresh_inventory()

    @property
    def runtime_mode(self) -> str:
        return 'LIVE'

    @property
    def connection_state(self) -> str:
        return self._connection_state

    @property
    def runtime_source_label(self) -> str:
        return self._runtime_source_label

    def _refresh_inventory(self) -> None:
        self._discovered = self._adapters.discover_devices(timestamp=as_event_time(int(self._elapsed_seconds * 1000)))
        survey = survey_runtime_capabilities(
            adapters=self._adapters,
            timestamp=as_event_time(int(self._elapsed_seconds * 1000) + 1),
        )
        if survey.summary != self._last_survey_summary:
            self._event_log.append(survey.summary)
            self._last_survey_summary = survey.summary
        support_pack_note = None
        if not survey.support_packs:
            support_pack_note = 'optional support packs absent: generic baseline discovery remains active'
        if support_pack_note and support_pack_note != self._last_support_pack_note:
            self._event_log.append(support_pack_note)
        self._last_support_pack_note = support_pack_note

    def available_devices(self) -> tuple[LiveRuntimeDeviceRecord, ...]:
        self._refresh_inventory()
        survey = survey_runtime_capabilities(
            adapters=self._adapters,
            timestamp=as_event_time(int(self._elapsed_seconds * 1000) + 2),
        )
        survey_by_key = {row.device_key: row for row in survey.devices}
        records: list[LiveRuntimeDeviceRecord] = []
        for device in self._discovered:
            capability = None
            if device.bound_adapter_id is not None and device.bound_adapter_id in self._adapters.adapters:
                capability = self._adapters.adapters[device.bound_adapter_id].capability()
            hardware_mode = 'simulated' if capability is not None and capability.is_simulated else 'connected'
            driver_name = str(device.identity.metadata.get('driver_name', 'generic-runtime'))
            survey_row = survey_by_key.get(device.device_key)
            records.append(
                LiveRuntimeDeviceRecord(
                    device_key=device.device_key,
                    display_name=device.identity.display_name,
                    serial_number=device.identity.serial_number,
                    transport=device.identity.transport,
                    hardware_mode=hardware_mode,
                    writable_point_count=0 if capability is None else len(capability.writable_points),
                    readable_point_count=0 if capability is None else len(capability.readable_points),
                    driver_name=driver_name,
                    live_capable=device.bound_adapter_id is not None,
                    capability_mode='unknown' if survey_row is None else survey_row.capability_mode,
                    identity_state='unknown' if survey_row is None else survey_row.identity_state,
                    read_state='unknown' if survey_row is None else survey_row.read_state,
                    write_state='unknown' if survey_row is None else survey_row.write_state,
                    limited_access_reason=None if survey_row is None else survey_row.limited_access_reason,
                )
            )
        return tuple(records)

    def connect(self, *, device_key: str) -> bool:
        self._refresh_inventory()
        device = next((item for item in self._discovered if item.device_key == device_key), None)
        if device is None:
            self._connection_state = 'connect_failed'
            self._runtime_source_label = 'missing_device'
            self._event_log.append(f'connect failed: unknown device {device_key}')
            return False
        try:
            activated, adapter_id, _workbenches = self._adapters.activate_discovered_device(device_key=device_key)
        except Exception as exc:  # pragma: no cover - defensive runtime bridge path
            self._connection_state = 'connect_failed'
            self._runtime_source_label = 'activation_error'
            self._event_log.append(f'connect failed: {type(exc).__name__}: {exc}')
            return False
        if adapter_id is None or adapter_id not in self._adapters.adapters:
            self._connection_state = 'connect_failed'
            self._runtime_source_label = 'activation_unavailable'
            self._event_log.append(f'connect failed: no generic activation path for {device.identity.display_name}')
            return False
        self._adapter = self._adapters.adapters[adapter_id]
        self._active_adapter_id = adapter_id
        self._active_device_key = device_key
        self._connection_state = 'connected'
        capability = self._adapter.capability()
        mode = 'generic' if activated.provider_id == 'generic_adapter_inventory' else 'enhanced'
        hardware_mode = 'simulated' if capability.is_simulated else 'connected'
        self._runtime_source_label = f'live::{mode}::{hardware_mode}'
        self._descriptors = tuple(self._descriptor_from_point(point) for point in capability.readable_points)
        self._latest_rows = {}
        self._histories = {descriptor.signal_id: deque(maxlen=_MAX_HISTORY) for descriptor in self._descriptors}
        self._event_log.append(f'connected: {activated.identity.display_name} via {self._runtime_source_label}')
        return True

    def disconnect(self) -> None:
        if self._active_device_key is not None:
            self._event_log.append(f'disconnected: {self._active_device_key}')
        self._active_device_key = None
        self._active_adapter_id = None
        self._adapter = None
        self._connection_state = 'disconnected'
        self._runtime_source_label = 'disconnected'
        self._latest_rows = {}

    def writable_targets(self) -> tuple[WriteTargetDescriptor, ...]:
        if self._adapter is None:
            return ()
        capability = self._adapter.capability()
        rows = []
        for point in capability.writable_points:
            rows.append(
                WriteTargetDescriptor(
                    signal_id=self._signal_id_from_point(point.point_id),
                    point_id=point.point_id,
                    display_name=point.display_name or point.point_id,
                    target_class='writable_live_capable',
                    units=point.units,
                )
            )
        return tuple(rows)

    def step(self, *, dt_seconds: float = 0.20) -> LiveRuntimeSnapshot:
        self._elapsed_seconds += dt_seconds
        if self._adapter is not None and self._connection_state == 'connected':
            result = self._adapter.poll(timestamp=int(self._elapsed_seconds * 1000))
            for snapshot in result.snapshots:
                self._latest_rows[snapshot.point.point_id] = snapshot
                signal_id = self._signal_id_from_point(snapshot.point.point_id)
                history = self._histories.setdefault(signal_id, deque(maxlen=_MAX_HISTORY))
                try:
                    numeric = float(snapshot.engineering_value)
                except (TypeError, ValueError):
                    numeric = 0.0
                history.append((self._elapsed_seconds, numeric))
        elif self._connection_state == 'connected':
            self._connection_state = 'degraded'
            self._runtime_source_label = 'adapter_missing'
            self._event_log.append('live runtime degraded: adapter missing during step')
        return self.snapshot()

    def snapshot(self) -> LiveRuntimeSnapshot:
        return LiveRuntimeSnapshot(
            runtime_mode='LIVE',
            connection_state=self._connection_state,
            runtime_source_label=self._runtime_source_label,
            device_label=self._active_device_key or 'no live device selected',
            elapsed_seconds=self._elapsed_seconds,
            signal_snapshots=self.signal_snapshots(),
            event_log=tuple(self._event_log),
        )

    def signal_descriptors(self, *, lens_id: str | None = None) -> tuple[LiveSignalDescriptor, ...]:
        _ = lens_id
        return self._descriptors

    def signal_snapshots(self, *, lens_id: str | None = None) -> tuple[LiveSignalSnapshot, ...]:
        _ = lens_id
        rows: list[LiveSignalSnapshot] = []
        for descriptor in self._descriptors:
            latest = self._latest_rows.get(descriptor.point_id)
            if latest is None:
                rows.append(
                    LiveSignalSnapshot(
                        descriptor=descriptor,
                        value=0.0,
                        quality_label='pending',
                        freshness_label='pending',
                        alarm_severity='normal',
                        runtime_source_label=self._runtime_source_label,
                    )
                )
                continue
            try:
                numeric = float(latest.engineering_value)
            except (TypeError, ValueError):
                numeric = 0.0
            rows.append(
                LiveSignalSnapshot(
                    descriptor=descriptor,
                    value=numeric,
                    quality_label=latest.quality.value,
                    freshness_label=self._freshness_label(latest.quality, latest.stale),
                    alarm_severity=self._alarm_severity(descriptor.point_id, numeric),
                    runtime_source_label=self._runtime_source_label,
                )
            )
        return tuple(rows)

    def trace_series(self, signal_id: str) -> LiveTraceSeries:
        history = self._histories.get(signal_id, ())
        x_values = tuple(item[0] for item in history)
        y_values = tuple(item[1] for item in history)
        return LiveTraceSeries(signal_id=signal_id, x_values=x_values, y_values=y_values)

    def request_write(self, *, point_id: str, request_value: str, posture: str) -> GuardedWriteDecision:
        target = next((item for item in self.writable_targets() if item.point_id == point_id), None)
        target_class = 'unknown' if target is None else target.target_class
        if target is None:
            self._event_log.append(f'write blocked: unknown target {point_id}')
            return GuardedWriteDecision(
                allowed=False,
                reason='target not found',
                target_class=target_class,
                point_id=point_id,
                request_value=request_value,
                runtime_mode='LIVE',
                posture=posture,
            )
        if posture != 'armed_control':
            self._event_log.append(f'write blocked: posture {posture} cannot actuate {point_id}')
            return GuardedWriteDecision(
                allowed=False,
                reason='control posture does not permit live writes',
                target_class=target_class,
                point_id=point_id,
                request_value=request_value,
                runtime_mode='LIVE',
                posture=posture,
            )
        if self._adapter is None or self._active_adapter_id is None:
            self._event_log.append(f'write blocked: no adapter connected for {point_id}')
            return GuardedWriteDecision(
                allowed=False,
                reason='no connected adapter',
                target_class=target_class,
                point_id=point_id,
                request_value=request_value,
                runtime_mode='LIVE',
                posture=posture,
            )
        request = AdapterCommandRequest(
            adapter_id=self._active_adapter_id,
            point_id=point_id,
            request_id=RequestId(f'REQ-{point_id}-{int(self._elapsed_seconds * 1000)}'),
            output_id=OutputId(f'OUT-{point_id}'),
            requested_value=request_value,
            requested_at=as_event_time(int(self._elapsed_seconds * 1000)),
            actor_id=ActorId('operator-shell'),
        )
        result = self._adapter.submit_command(request)
        self._event_log.append(f'write {result.outcome.value}: {point_id} -> {request_value}')
        return GuardedWriteDecision(
            allowed=result.successful,
            reason='' if result.reason is None else result.reason,
            target_class=target_class,
            point_id=point_id,
            request_value=request_value,
            runtime_mode='LIVE',
            posture=posture,
            result=result,
        )

    def inventory(self) -> dict[str, object]:
        survey = survey_runtime_capabilities(
            adapters=self._adapters,
            timestamp=as_event_time(int(self._elapsed_seconds * 1000) + 2),
        )
        return {
            'runtime_mode': 'LIVE',
            'connection_state': self._connection_state,
            'runtime_source_label': self._runtime_source_label,
            'available_devices': [
                {
                    'device_key': record.device_key,
                    'display_name': record.display_name,
                    'serial_number': record.serial_number,
                    'transport': record.transport,
                    'hardware_mode': record.hardware_mode,
                    'writable_point_count': record.writable_point_count,
                    'readable_point_count': record.readable_point_count,
                    'driver_name': record.driver_name,
                    'live_capable': record.live_capable,
                }
                for record in self.available_devices()
            ],
            'active_device_key': self._active_device_key,
            'signal_count': len(self._descriptors),
            'writable_target_count': len(self.writable_targets()),
            'support_pack_state': [
                {
                    'pack_id': item.pack_id,
                    'state': item.state,
                    'summary': item.summary,
                }
                for item in survey.support_packs
            ],
            'event_log_tail': list(self._event_log)[-8:],
        }

    def _descriptor_from_point(self, point) -> LiveSignalDescriptor:
        hardware_label = point.display_name or point.point_id
        logical_label = self._logical_name(point.point_id)
        derived_label = f'{logical_label}_filtered' if point.point_class.value != 'command' else f'{logical_label}_command_watch'
        control_label = logical_label if point.point_class.value == 'command' else f'{logical_label}_control_view'
        labels = {
            'hardware': hardware_label,
            'raw': point.point_id,
            'logical': logical_label,
            'derived': derived_label,
            'control': control_label,
            'saved': f'Live / {logical_label}',
        }
        return LiveSignalDescriptor(
            signal_id=self._signal_id_from_point(point.point_id),
            point_id=point.point_id,
            units=point.units,
            point_class=point.point_class.value,
            source_class='control' if point.point_class.value == 'command' else 'hardware',
            write_safe=point.point_class.value == 'command',
            labels_by_lens=labels,
            metadata={str(key): str(value) for key, value in point.metadata.items()},
        )

    @staticmethod
    def _signal_id_from_point(point_id: str) -> str:
        return f'live::{point_id}'

    @staticmethod
    def _logical_name(point_id: str) -> str:
        parts = point_id.split('_')
        if parts[:2] == ['analog', 'in']:
            return f'analog_input_{parts[-1]}'
        if parts[:2] == ['digital', 'in']:
            return f'digital_input_{parts[-1]}'
        if parts[:2] == ['analog', 'out']:
            return f'analog_output_{parts[-1]}_cmd'
        if parts[:2] == ['digital', 'out']:
            return f'digital_output_{parts[-1]}_cmd'
        return point_id

    @staticmethod
    def _freshness_label(quality: SignalQuality, stale: bool) -> str:
        if stale:
            return 'stale'
        if quality == SignalQuality.GOOD:
            return 'fresh'
        if quality == SignalQuality.SIMULATED:
            return 'fresh'
        if quality == SignalQuality.DEGRADED:
            return 'degraded'
        if quality == SignalQuality.INVALID:
            return 'invalid'
        return 'pending'

    @staticmethod
    def _alarm_severity(point_id: str, value: float) -> str:
        if point_id == 'analog_in_0':
            if value > 3.0:
                return 'high'
            if value > 2.2:
                return 'warning'
        if point_id == 'analog_in_1' and value > 2.8:
            return 'warning'
        return 'normal'
