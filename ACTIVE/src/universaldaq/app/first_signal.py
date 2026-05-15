from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import TYPE_CHECKING

from universaldaq.adapters import DeviceLifecyclePhase, DiscoveredDevice, PointClass
from universaldaq.common import EventTime, SignalId
from universaldaq.signals import BindingPolicy, LogicalSignalBinding, SignalDefinition
from universaldaq.ui import FirstSignalSummary, FirstSignalTracePoint

if TYPE_CHECKING:
    from universaldaq.app.service_registry import ShellServiceRegistry


_TRACE_LIMIT = 120
_ID_TOKEN_RE = re.compile(r"[^A-Za-z0-9]+")


@dataclass(frozen=True, slots=True, kw_only=True)
class FirstSignalBindingDecision:
    signal_id: SignalId | None
    point_key: str | None
    display_name: str | None
    auto_bound: bool
    reason: str


class FirstSignalPlanner:
    @staticmethod
    def _id_token(value: object) -> str:
        text = _ID_TOKEN_RE.sub("_", str(value)).strip("_")
        return text.lower() or "anon"

    @staticmethod
    def _binding_rows_for_device(*, services: 'ShellServiceRegistry', device_identity_key: str) -> list[tuple[SignalId, str, object]]:
        rows: list[tuple[SignalId, str, object]] = []
        for signal_id, binding in services.bindings.signal_bindings_for_device_identity(device_identity_key):
            point_definition = services.bindings.point_definitions.get(binding.source_point_key)
            if point_definition is None or point_definition.device_identity_key != device_identity_key:
                continue
            rows.append((signal_id, binding.source_point_key, point_definition))
        return rows

    @staticmethod
    def _point_priority(point_definition: object) -> tuple[int, str]:
        point_class = getattr(point_definition.point_ref, 'point_class', PointClass.STATUS)
        if point_class == PointClass.ANALOG:
            rank = 0
        elif point_class == PointClass.DIGITAL:
            rank = 1
        elif point_class == PointClass.STATUS:
            rank = 2
        else:
            rank = 3
        return rank, str(point_definition.stable_point_key)

    @staticmethod
    def _preferred_projected_point(*, services: 'ShellServiceRegistry', device_identity_key: str):
        projected = [
            definition
            for definition in services.bindings.point_definitions_for_device(device_identity_key)
            if getattr(definition, 'enabled', True)
        ]
        if not projected:
            return None
        projected.sort(key=FirstSignalPlanner._point_priority)
        return projected[0]

    @staticmethod
    def ensure_default_binding(
        *,
        services: 'ShellServiceRegistry',
        device: DiscoveredDevice | None,
        adapter_id: str | None,
    ) -> FirstSignalBindingDecision:
        if device is None or adapter_id is None:
            return FirstSignalBindingDecision(
                signal_id=None,
                point_key=None,
                display_name=None,
                auto_bound=False,
                reason='no active device or adapter available',
            )
        existing = FirstSignalPlanner._binding_rows_for_device(
            services=services,
            device_identity_key=device.identity.stable_key,
        )
        if existing:
            signal_id, point_key, point_definition = sorted(existing, key=lambda item: (str(item[0]), item[1]))[0]
            return FirstSignalBindingDecision(
                signal_id=signal_id,
                point_key=point_key,
                display_name=str(point_definition.friendly_name),
                auto_bound=False,
                reason='existing device binding retained',
            )
        preferred = FirstSignalPlanner._preferred_projected_point(
            services=services,
            device_identity_key=device.identity.stable_key,
        )
        if preferred is None:
            return FirstSignalBindingDecision(
                signal_id=None,
                point_key=None,
                display_name=None,
                auto_bound=False,
                reason='no projected readable points available for first signal',
            )
        signal_id = SignalId(f"first_signal__{FirstSignalPlanner._id_token(device.identity.stable_key)}")
        display_name = str(preferred.friendly_name)
        if signal_id not in services.signals.definitions:
            services.signals.register_signal(
                SignalDefinition(
                    signal_id=signal_id,
                    display_name=display_name,
                    engineering_units='' if preferred.point_ref.units is None else str(preferred.point_ref.units),
                )
            )
        services.bindings.bind_signal(
            LogicalSignalBinding(
                logical_signal_id=signal_id,
                source_point_key=preferred.stable_point_key,
                binding_policy=BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
                metadata={
                    'device_identity_key': device.identity.stable_key,
                    'point_id': preferred.point_ref.point_id,
                    'friendly_name': display_name,
                    'auto_bound': 'true',
                    'binding_policy': BindingPolicy.AUTO_REBIND_IF_CONFIDENT.value,
                },
            )
        )
        return FirstSignalBindingDecision(
            signal_id=signal_id,
            point_key=preferred.stable_point_key,
            display_name=display_name,
            auto_bound=True,
            reason='auto-bound first readable point for quick-start usability slice',
        )

    @staticmethod
    def _append_trace_point(
        *,
        previous_summary: FirstSignalSummary | None,
        timestamp: EventTime | None,
        value: str,
    ) -> tuple[FirstSignalTracePoint, ...]:
        prior = () if previous_summary is None else previous_summary.trace_points
        if timestamp is None:
            return prior
        if prior and int(prior[-1].timestamp) == int(timestamp) and prior[-1].value == value:
            return prior
        updated = prior + (FirstSignalTracePoint(timestamp=timestamp, value=value),)
        if len(updated) > _TRACE_LIMIT:
            updated = updated[-_TRACE_LIMIT:]
        return updated

    @staticmethod
    def _signal_quality_label(*, snapshot, lifecycle_phase: DeviceLifecyclePhase | None) -> str:
        if lifecycle_phase == DeviceLifecyclePhase.DISCONNECTED:
            return 'disconnected'
        if lifecycle_phase == DeviceLifecyclePhase.DEGRADED:
            return 'degraded'
        if snapshot is None:
            return 'pending'
        return snapshot.quality.value

    @staticmethod
    def _fallback_value(*, snapshot, previous_summary: FirstSignalSummary | None) -> str:
        if snapshot is not None:
            return snapshot.value
        if previous_summary is not None:
            return previous_summary.latest_value
        return ''

    @staticmethod
    def _freshness_label(*, quality_label: str, lifecycle_phase: DeviceLifecyclePhase | None) -> str:
        if lifecycle_phase == DeviceLifecyclePhase.DISCONNECTED:
            return 'offline'
        if quality_label in {'degraded', 'stale'}:
            return 'stale'
        if quality_label == 'invalid':
            return 'invalid'
        if quality_label == 'simulated':
            return 'simulated'
        if quality_label == 'good':
            return 'fresh'
        return 'pending'

    @staticmethod
    def _channel_metadata(*, device: DiscoveredDevice, point_definition: object, binding_metadata: dict[str, str], auto_bound: bool) -> dict[str, str]:
        point_ref = point_definition.point_ref
        metadata = {
            'device_identity_key': device.identity.stable_key,
            'device_key': device.device_key,
            'device_display_name': device.display_name,
            'device_serial_number': '' if device.identity.serial_number is None else str(device.identity.serial_number),
            'source_adapter_id': str(point_ref.adapter_id),
            'source_point_id': str(point_ref.point_id),
            'point_class': point_ref.point_class.value,
            'source_transport': '' if device.identity.transport is None else str(device.identity.transport),
            'binding_policy': binding_metadata.get('binding_policy', ''),
            'binding_origin': 'auto_bound' if auto_bound else 'retained_binding',
            'friendly_name': str(point_definition.friendly_name),
        }
        for key, value in point_ref.metadata.items():
            metadata[f'point_meta::{key}'] = str(value)
        for key, value in point_definition.metadata.items():
            metadata[f'definition_meta::{key}'] = str(value)
        return metadata

    @staticmethod
    def _provenance_label(*, device: DiscoveredDevice, point_definition: object) -> str:
        point_ref = point_definition.point_ref
        adapter_id = str(point_ref.adapter_id)
        point_label = point_ref.display_name or point_ref.point_id
        return f'{device.display_name} / {adapter_id} / {point_label}'

    @staticmethod
    def build_summary(
        *,
        services: 'ShellServiceRegistry',
        device: DiscoveredDevice | None,
        previous_summary: FirstSignalSummary | None = None,
        preferred_signal_id: SignalId | None = None,
        lifecycle_phase: DeviceLifecyclePhase | None = None,
        auto_bound: bool = False,
    ) -> FirstSignalSummary | None:
        if device is None:
            return None
        rows = FirstSignalPlanner._binding_rows_for_device(
            services=services,
            device_identity_key=device.identity.stable_key,
        )
        if not rows:
            return None

        def sort_key(item: tuple[SignalId, str, object]) -> tuple[int, str, str]:
            signal_id, point_key, point_definition = item
            priority = FirstSignalPlanner._point_priority(point_definition)[0]
            return priority, str(signal_id), point_key

        chosen: tuple[SignalId, str, object] | None = None
        if preferred_signal_id is not None:
            for row in rows:
                if row[0] == preferred_signal_id:
                    chosen = row
                    break
        if chosen is None and previous_summary is not None:
            for row in rows:
                if str(row[0]) == previous_summary.signal_id:
                    chosen = row
                    break
        if chosen is None:
            chosen = sorted(rows, key=sort_key)[0]

        signal_id, point_key, point_definition = chosen
        signal_snapshot = services.signals.snapshots.get(signal_id)
        signal_definition = services.signals.definitions.get(signal_id)
        display_name = point_definition.friendly_name if signal_definition is None else signal_definition.display_name
        engineering_units = point_definition.point_ref.units if signal_definition is None else signal_definition.engineering_units
        latest_timestamp = None if signal_snapshot is None else signal_snapshot.timestamp
        latest_value = FirstSignalPlanner._fallback_value(snapshot=signal_snapshot, previous_summary=previous_summary)
        trace_points = FirstSignalPlanner._append_trace_point(
            previous_summary=previous_summary,
            timestamp=latest_timestamp,
            value=latest_value,
        )
        resolved_auto_bound = auto_bound or (False if previous_summary is None else previous_summary.auto_bound)
        if previous_summary is not None and previous_summary.signal_id != str(signal_id):
            trace_points = () if latest_timestamp is None else (FirstSignalTracePoint(timestamp=latest_timestamp, value=latest_value),)
            resolved_auto_bound = auto_bound
        binding = services.bindings.signal_bindings.get(signal_id)
        binding_metadata = {} if binding is None else {str(key): str(value) for key, value in binding.metadata.items()}
        quality_label = FirstSignalPlanner._signal_quality_label(snapshot=signal_snapshot, lifecycle_phase=lifecycle_phase)
        freshness_label = FirstSignalPlanner._freshness_label(quality_label=quality_label, lifecycle_phase=lifecycle_phase)
        channel_metadata = FirstSignalPlanner._channel_metadata(
            device=device,
            point_definition=point_definition,
            binding_metadata=binding_metadata,
            auto_bound=resolved_auto_bound,
        )
        hardware_channel = point_definition.point_ref.metadata.get('hardware_channel')
        if hardware_channel is None:
            hardware_channel = point_definition.point_ref.point_id
        provenance_label = FirstSignalPlanner._provenance_label(device=device, point_definition=point_definition)
        return FirstSignalSummary(
            signal_id=str(signal_id),
            display_name=str(display_name),
            point_key=point_key,
            point_class=point_definition.point_ref.point_class.value,
            engineering_units=None if engineering_units in {'', None} else str(engineering_units),
            latest_value=latest_value,
            latest_timestamp=latest_timestamp,
            quality_label=quality_label,
            auto_bound=resolved_auto_bound,
            source_device_key=device.device_key,
            source_adapter_id=point_definition.point_ref.adapter_id,
            device_identity_key=device.identity.stable_key,
            source_transport=None if device.identity.transport in {'', None} else str(device.identity.transport),
            hardware_channel=None if hardware_channel in {'', None} else str(hardware_channel),
            freshness_label=freshness_label,
            provenance_label=provenance_label,
            channel_metadata=channel_metadata,
            trace_points=trace_points,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class FirstSignalReplayTape:
    signal_id: str
    display_name: str
    engineering_units: str | None
    quality_label: str
    freshness_label: str = 'pending'
    provenance_label: str | None = None
    channel_metadata: dict[str, str] | None = None
    trace_points: tuple[FirstSignalTracePoint, ...] = ()

    @staticmethod
    def from_summary(summary: FirstSignalSummary | None) -> 'FirstSignalReplayTape | None':
        if summary is None:
            return None
        return FirstSignalReplayTape(
            signal_id=summary.signal_id,
            display_name=summary.display_name,
            engineering_units=summary.engineering_units,
            quality_label=summary.quality_label,
            freshness_label=summary.freshness_label,
            provenance_label=summary.provenance_label,
            channel_metadata=dict(summary.channel_metadata),
            trace_points=summary.trace_points,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            'signal_id': self.signal_id,
            'display_name': self.display_name,
            'engineering_units': self.engineering_units,
            'quality_label': self.quality_label,
            'freshness_label': self.freshness_label,
            'provenance_label': self.provenance_label,
            'channel_metadata': {} if self.channel_metadata is None else dict(self.channel_metadata),
            'trace_points': [
                {
                    'timestamp': int(item.timestamp),
                    'value': item.value,
                    'numeric_value': float(item.value) if _is_float(item.value) else None,
                }
                for item in self.trace_points
            ],
        }

    @staticmethod
    def from_dict(payload: dict[str, object]) -> 'FirstSignalReplayTape':
        trace_points = tuple(
            FirstSignalTracePoint(timestamp=EventTime(int(item['timestamp'])), value=str(item['value']))
            for item in payload.get('trace_points', [])
        )
        return FirstSignalReplayTape(
            signal_id=str(payload.get('signal_id', '')),
            display_name=str(payload.get('display_name', '')),
            engineering_units=None if payload.get('engineering_units') in {'', None} else str(payload.get('engineering_units')),
            quality_label=str(payload.get('quality_label', 'pending')),
            freshness_label=str(payload.get('freshness_label', 'pending')),
            provenance_label=None if payload.get('provenance_label') in {'', None} else str(payload.get('provenance_label')),
            channel_metadata={str(key): str(value) for key, value in dict(payload.get('channel_metadata', {})).items()},
            trace_points=trace_points,
        )




def _is_float(value: str) -> bool:
    try:
        float(value)
    except (TypeError, ValueError):
        return False
    return True
