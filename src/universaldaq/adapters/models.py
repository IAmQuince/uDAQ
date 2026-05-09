from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Mapping

from universaldaq.common import ActorId, EvidenceId, EvidenceKind, EvidenceRecord, EventTime, OutputId, RequestId, SignalId, SignalQuality
from universaldaq.security import AuthorizationDecision

if TYPE_CHECKING:
    from .contracts import DiscoveryProvider


class AdapterKind(StrEnum):
    SIMULATED = 'simulated'
    PROTOCOL_BRIDGE = 'protocol_bridge'
    DEVICE_DRIVER = 'device_driver'


class AdapterHealthState(StrEnum):
    UNKNOWN = 'unknown'
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    DISCONNECTED = 'disconnected'
    ERROR = 'error'


class AdapterOperationMode(StrEnum):
    POLLED = 'polled'
    SUBSCRIBED = 'subscribed'
    HYBRID = 'hybrid'


class PointClass(StrEnum):
    ANALOG = 'analog'
    DIGITAL = 'digital'
    STATUS = 'status'
    COMMAND = 'command'


class AdapterCommandOutcome(StrEnum):
    ACCEPTED_FOR_TRANSMISSION = 'accepted_for_transmission'
    TARGET_NOT_FOUND = 'target_not_found'
    TRANSPORT_FAILED = 'transport_failed'
    DEVICE_REJECTED = 'device_rejected'
    OBSERVED = 'observed'
    OBSERVATION_PENDING = 'observation_pending'


class DeviceSupportTier(StrEnum):
    GENERIC = 'generic'
    PROTOCOL_FAMILY = 'protocol_family'
    ENHANCED = 'enhanced'


class DeviceLifecyclePhase(StrEnum):
    NO_DEVICE = 'no_device'
    DISCOVERED = 'discovered'
    IDENTIFIED = 'identified'
    READY_TO_CONFIGURE = 'ready_to_configure'
    QUICK_START_READY = 'quick_start_ready'
    ADVANCED_SETUP = 'advanced_setup'
    LIVE = 'live'
    DISCONNECTED = 'disconnected'
    DEGRADED = 'degraded'


class SupportPackLoadState(StrEnum):
    INSTALLED = 'installed'
    UNAVAILABLE = 'unavailable'
    MISSING = 'missing'
    ERROR = 'error'


@dataclass(frozen=True, slots=True, kw_only=True)
class AdapterPointRef:
    adapter_id: str
    point_id: str
    signal_id: SignalId | None = None
    display_name: str | None = None
    point_class: PointClass = PointClass.STATUS
    units: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    @property
    def stable_key(self) -> str:
        return f'{self.adapter_id}:{self.point_id}'


@dataclass(frozen=True, slots=True, kw_only=True)
class PointSnapshot:
    point: AdapterPointRef
    raw_value: str
    engineering_value: str
    quality: SignalQuality
    source_timestamp: EventTime
    received_timestamp: EventTime
    stale: bool = False
    metadata: Mapping[str, str] = field(default_factory=dict)

    def export_row(self) -> dict[str, str]:
        return {
            'record_type': 'point_snapshot',
            'adapter_id': self.point.adapter_id,
            'point_id': self.point.point_id,
            'signal_id': '' if self.point.signal_id is None else str(self.point.signal_id),
            'point_class': self.point.point_class.value,
            'quality': self.quality.value,
            'raw_value': self.raw_value,
            'engineering_value': self.engineering_value,
            'units': '' if self.point.units is None else self.point.units,
            'source_timestamp': str(self.source_timestamp),
            'received_timestamp': str(self.received_timestamp),
            'stale': str(self.stale).lower(),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class AdapterCapability:
    adapter_id: str
    adapter_kind: AdapterKind
    operation_mode: AdapterOperationMode
    readable_points: tuple[AdapterPointRef, ...] = field(default_factory=tuple)
    writable_points: tuple[AdapterPointRef, ...] = field(default_factory=tuple)
    service_capabilities: tuple[str, ...] = field(default_factory=tuple)
    is_simulated: bool = False
    metadata: Mapping[str, str] = field(default_factory=dict)

    def supports_write(self, point_id: str) -> bool:
        return any(point.point_id == point_id for point in self.writable_points)


@dataclass(frozen=True, slots=True, kw_only=True)
class AdapterHealth:
    adapter_id: str
    state: AdapterHealthState
    summary: str
    last_success_at: EventTime | None = None
    last_failure_at: EventTime | None = None
    consecutive_failures: int = 0
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class AdapterPollResult:
    adapter_id: str
    polled_at: EventTime
    snapshots: tuple[PointSnapshot, ...] = field(default_factory=tuple)
    health: AdapterHealth | None = None
    diagnostics: tuple[dict[str, object], ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True, kw_only=True)
class AdapterCommandRequest:
    adapter_id: str
    point_id: str
    request_id: RequestId
    output_id: OutputId
    requested_value: str
    requested_at: EventTime
    actor_id: ActorId
    authorization_decision: AuthorizationDecision | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AdapterCommandResult:
    request: AdapterCommandRequest
    outcome: AdapterCommandOutcome
    reason: str | None = None
    transmitted_at: EventTime | None = None
    observed_value: str | None = None
    observed_at: EventTime | None = None
    health: AdapterHealth | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    @property
    def successful(self) -> bool:
        return self.outcome in {
            AdapterCommandOutcome.ACCEPTED_FOR_TRANSMISSION,
            AdapterCommandOutcome.OBSERVED,
            AdapterCommandOutcome.OBSERVATION_PENDING,
        }

    def export_row(self) -> dict[str, str]:
        return {
            'record_type': 'adapter_command',
            'adapter_id': self.request.adapter_id,
            'point_id': self.request.point_id,
            'request_id': str(self.request.request_id),
            'output_id': str(self.request.output_id),
            'actor_id': str(self.request.actor_id),
            'outcome': self.outcome.value,
            'reason': '' if self.reason is None else self.reason,
            'requested_value': self.request.requested_value,
            'transmitted_at': '' if self.transmitted_at is None else str(self.transmitted_at),
            'observed_value': '' if self.observed_value is None else self.observed_value,
            'observed_at': '' if self.observed_at is None else str(self.observed_at),
        }

    def evidence_records(self) -> tuple[EvidenceRecord, ...]:
        summary = {
            AdapterCommandOutcome.ACCEPTED_FOR_TRANSMISSION: 'adapter accepted command for transmission',
            AdapterCommandOutcome.TARGET_NOT_FOUND: 'adapter target not found',
            AdapterCommandOutcome.TRANSPORT_FAILED: 'adapter transport failed',
            AdapterCommandOutcome.DEVICE_REJECTED: 'device rejected command',
            AdapterCommandOutcome.OBSERVED: 'adapter observed requested value',
            AdapterCommandOutcome.OBSERVATION_PENDING: 'adapter accepted command but observation pending',
        }[self.outcome]
        timestamp = self.transmitted_at if self.transmitted_at is not None else self.request.requested_at
        record = EvidenceRecord(
            evidence_id=EvidenceId(f'EVID-ADAPTER-{self.request.request_id}-{self.outcome.value}'),
            kind=EvidenceKind.EVENT,
            timestamp=timestamp,
            summary=summary,
            attributes={
                'adapter_id': self.request.adapter_id,
                'point_id': self.request.point_id,
                'outcome': self.outcome.value,
                'reason': '' if self.reason is None else self.reason,
                'requested_value': self.request.requested_value,
                'observed_value': '' if self.observed_value is None else self.observed_value,
            },
            source_kind='adapter_command',
            source_id=self.request.adapter_id,
            actor_id=str(self.request.actor_id),
            session_id=None if self.request.authorization_decision is None else self.request.authorization_decision.session_id,
            origin=None if self.request.authorization_decision is None else self.request.authorization_decision.origin,
            tags=('adapters', 'commands'),
        )
        return (record,)


@dataclass(frozen=True, slots=True, kw_only=True)
class DeviceIdentity:
    stable_key: str
    display_name: str
    vendor: str | None = None
    model: str | None = None
    serial_number: str | None = None
    transport: str | None = None
    firmware_version: str | None = None
    hardware_revision: str | None = None
    provisional: bool = False
    metadata: Mapping[str, str] = field(default_factory=dict)

    @property
    def summary(self) -> str:
        parts = [self.display_name]
        if self.serial_number:
            parts.append(f'serial {self.serial_number}')
        if self.transport:
            parts.append(self.transport)
        return ' | '.join(parts)


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkbenchDescriptor:
    workbench_id: str
    display_name: str
    activation_reason: str
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class DiscoveredDevice:
    device_key: str
    identity: DeviceIdentity
    provider_id: str
    support_tier: DeviceSupportTier
    capability_labels: tuple[str, ...] = field(default_factory=tuple)
    bound_adapter_id: str | None = None
    workbenches: tuple[WorkbenchDescriptor, ...] = field(default_factory=tuple)
    known_device_key: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        return self.identity.display_name

    @property
    def quick_start_allowed(self) -> bool:
        return self.bound_adapter_id is not None or self.support_tier != DeviceSupportTier.GENERIC

    @property
    def advanced_setup_allowed(self) -> bool:
        return True


@dataclass(frozen=True, slots=True, kw_only=True)
class KnownDeviceRecord:
    known_device_key: str
    identity_key: str
    display_name: str
    last_profile_id: str | None = None
    last_seen_at: EventTime | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class SupportPackDescriptor:
    pack_id: str
    display_name: str
    plugin_module: str | None = None
    support_tier: DeviceSupportTier = DeviceSupportTier.ENHANCED
    enhancement_only: bool = True
    provides_driver_bridge: bool = False
    dependency_hints: tuple[str, ...] = field(default_factory=tuple)
    transport_hints: tuple[str, ...] = field(default_factory=tuple)
    adapter_family: str = 'generic'
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class SupportPackRegistration:
    descriptor: SupportPackDescriptor
    discovery_providers: tuple[DiscoveryProvider, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True, kw_only=True)
class SupportPackProbeResult:
    descriptor: SupportPackDescriptor
    available: bool
    summary: str
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class SupportPackLoadReport:
    pack_id: str
    module_name: str
    state: SupportPackLoadState
    summary: str
    metadata: Mapping[str, str] = field(default_factory=dict)

    @property
    def installed(self) -> bool:
        return self.state == SupportPackLoadState.INSTALLED
