from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from universaldaq.common import EventTime, as_event_time

if TYPE_CHECKING:
    from universaldaq.mapping import MappingSandboxState


RUNTIME_STATE_MODEL_VERSION = 'udq.runtime.state.v1'


@runtime_checkable
class _ToDict(Protocol):
    def to_dict(self) -> dict[str, object]: ...


class RuntimeTruthKind(StrEnum):
    REQUESTED = 'requested'
    APPLIED = 'applied'
    OBSERVED = 'observed'


class RuntimeTruthStatus(StrEnum):
    NONE = 'none'
    DRAFT = 'draft'
    SANDBOX = 'sandbox'
    PROPOSAL = 'proposal'
    PREFLIGHT = 'preflight'
    REVIEW = 'review'
    PREPARED_REQUEST = 'prepared-request'
    DIAGNOSTIC = 'diagnostic'
    APPLIED = 'applied'
    OBSERVED = 'observed'
    STALE = 'stale'
    UNAVAILABLE = 'unavailable'
    DEGRADED = 'degraded'
    SIMULATED = 'simulated'
    BLOCKED = 'blocked'
    UNKNOWN = 'unknown'


class RuntimeAuthorityZone(StrEnum):
    AUTHORITATIVE = 'authoritative'
    SANDBOX = 'sandbox'
    REVIEW = 'review'
    DIAGNOSTIC = 'diagnostic'


class RuntimeAvailability(StrEnum):
    AVAILABLE = 'available'
    STALE = 'stale'
    UNAVAILABLE = 'unavailable'
    DEGRADED = 'degraded'
    SIMULATED = 'simulated'
    UNKNOWN = 'unknown'


class RuntimePostureKind(StrEnum):
    COMMAND = 'command'
    SAFETY = 'safety'
    LOGIC = 'logic'
    UI_REVIEW = 'ui-review'


class SandboxMappingLifecycle(StrEnum):
    SANDBOX = 'sandbox'
    DRAFT = 'draft'
    PROPOSAL = 'proposal'
    PREFLIGHT = 'preflight'
    REVIEW = 'review'
    PREPARED_REQUEST = 'prepared-request'
    DIAGNOSTIC = 'diagnostic'


class RuntimeDeviceLifecycle(StrEnum):
    NO_DEVICE = 'no-device'
    DISCOVERED = 'discovered'
    CONNECTED = 'connected'
    LIVE = 'live'
    DEGRADED = 'degraded'
    STALE = 'stale'
    UNAVAILABLE = 'unavailable'
    SIMULATED = 'simulated'
    UNKNOWN = 'unknown'


def _event_time(value: EventTime | int | None) -> EventTime | None:
    if value is None:
        return None
    return as_event_time(int(value))


def _json_value(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, _ToDict):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in sorted(value.items(), key=lambda row: str(row[0]))}
    if isinstance(value, tuple | list):
        return [_json_value(item) for item in value]
    return value


def _sequence_to_dict(items: Sequence[Any]) -> list[dict[str, object]]:
    return [item.to_dict() for item in items]


@dataclass(frozen=True, slots=True, kw_only=True)
class RuntimeSourceIdentity:
    source_id: str
    source_kind: str
    label: str = ''
    adapter_id: str | None = None
    device_identity_key: str | None = None
    simulated: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            'source_id': self.source_id,
            'source_kind': self.source_kind,
            'label': self.label,
            'adapter_id': self.adapter_id,
            'device_identity_key': self.device_identity_key,
            'simulated': self.simulated,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RuntimeTruthRecord:
    truth_kind: RuntimeTruthKind
    status: RuntimeTruthStatus
    summary: str
    value: object | None = None
    source: RuntimeSourceIdentity | None = None
    timestamp: EventTime | None = None
    sequence_number: int | None = None
    data_age_ticks: int | None = None
    authoritative: bool = False
    diagnostics: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            'truth_kind': self.truth_kind.value,
            'status': self.status.value,
            'summary': self.summary,
            'value': _json_value(self.value),
            'source': None if self.source is None else self.source.to_dict(),
            'timestamp': None if self.timestamp is None else int(self.timestamp),
            'sequence_number': self.sequence_number,
            'data_age_ticks': self.data_age_ticks,
            'authoritative': self.authoritative,
            'diagnostics': list(self.diagnostics),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RuntimeStateIdentity:
    snapshot_id: str
    model_version: str
    timestamp: EventTime
    sequence_number: int | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            'snapshot_id': self.snapshot_id,
            'model_version': self.model_version,
            'timestamp': int(self.timestamp),
            'sequence_number': self.sequence_number,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RuntimeDevicePointState:
    point_id: str
    stable_key: str
    direction: str
    source: RuntimeSourceIdentity
    availability: RuntimeAvailability = RuntimeAvailability.UNKNOWN
    units: str | None = None
    requested_state: RuntimeTruthRecord | None = None
    applied_state: RuntimeTruthRecord | None = None
    observed_state: RuntimeTruthRecord | None = None
    last_update_timestamp: EventTime | None = None
    data_age_ticks: int | None = None
    diagnostic_summary: str = ''

    def to_dict(self) -> dict[str, object]:
        return {
            'point_id': self.point_id,
            'stable_key': self.stable_key,
            'direction': self.direction,
            'source': self.source.to_dict(),
            'availability': self.availability.value,
            'units': self.units,
            'requested_state': None if self.requested_state is None else self.requested_state.to_dict(),
            'applied_state': None if self.applied_state is None else self.applied_state.to_dict(),
            'observed_state': None if self.observed_state is None else self.observed_state.to_dict(),
            'last_update_timestamp': None if self.last_update_timestamp is None else int(self.last_update_timestamp),
            'data_age_ticks': self.data_age_ticks,
            'diagnostic_summary': self.diagnostic_summary,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RuntimeDeviceState:
    device_id: str
    lifecycle: RuntimeDeviceLifecycle
    source: RuntimeSourceIdentity
    posture: RuntimeAvailability = RuntimeAvailability.UNKNOWN
    display_name: str = ''
    point_ids: tuple[str, ...] = ()
    requested_state: RuntimeTruthRecord | None = None
    applied_state: RuntimeTruthRecord | None = None
    observed_state: RuntimeTruthRecord | None = None
    last_update_timestamp: EventTime | None = None
    data_age_ticks: int | None = None
    diagnostic_summary: str = ''

    def to_dict(self) -> dict[str, object]:
        return {
            'device_id': self.device_id,
            'display_name': self.display_name,
            'lifecycle': self.lifecycle.value,
            'source': self.source.to_dict(),
            'posture': self.posture.value,
            'point_ids': list(self.point_ids),
            'requested_state': None if self.requested_state is None else self.requested_state.to_dict(),
            'applied_state': None if self.applied_state is None else self.applied_state.to_dict(),
            'observed_state': None if self.observed_state is None else self.observed_state.to_dict(),
            'last_update_timestamp': None if self.last_update_timestamp is None else int(self.last_update_timestamp),
            'data_age_ticks': self.data_age_ticks,
            'diagnostic_summary': self.diagnostic_summary,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RuntimeMappingState:
    mapping_id: str
    authority_zone: RuntimeAuthorityZone
    lifecycle: str
    device_identity_key: str
    requested_state: RuntimeTruthRecord | None = None
    applied_state: RuntimeTruthRecord | None = None
    observed_state: RuntimeTruthRecord | None = None
    binding_count: int = 0
    state_hash: str | None = None
    last_update_timestamp: EventTime | None = None
    data_age_ticks: int | None = None
    diagnostic_summary: str = ''

    @property
    def authoritative_applied(self) -> bool:
        return self.authority_zone == RuntimeAuthorityZone.AUTHORITATIVE and self.applied_state is not None

    def to_dict(self) -> dict[str, object]:
        return {
            'mapping_id': self.mapping_id,
            'authority_zone': self.authority_zone.value,
            'lifecycle': self.lifecycle,
            'device_identity_key': self.device_identity_key,
            'binding_count': self.binding_count,
            'state_hash': self.state_hash,
            'requested_state': None if self.requested_state is None else self.requested_state.to_dict(),
            'applied_state': None if self.applied_state is None else self.applied_state.to_dict(),
            'observed_state': None if self.observed_state is None else self.observed_state.to_dict(),
            'authoritative_applied': self.authoritative_applied,
            'last_update_timestamp': None if self.last_update_timestamp is None else int(self.last_update_timestamp),
            'data_age_ticks': self.data_age_ticks,
            'diagnostic_summary': self.diagnostic_summary,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RuntimeSignalState:
    signal_id: str
    display_name: str
    requested_state: RuntimeTruthRecord | None = None
    applied_state: RuntimeTruthRecord | None = None
    observed_state: RuntimeTruthRecord | None = None
    source_point_ids: tuple[str, ...] = ()
    units: str | None = None
    availability: RuntimeAvailability = RuntimeAvailability.UNKNOWN
    last_update_timestamp: EventTime | None = None
    data_age_ticks: int | None = None
    diagnostic_summary: str = ''

    def to_dict(self) -> dict[str, object]:
        return {
            'signal_id': self.signal_id,
            'display_name': self.display_name,
            'source_point_ids': list(self.source_point_ids),
            'units': self.units,
            'availability': self.availability.value,
            'requested_state': None if self.requested_state is None else self.requested_state.to_dict(),
            'applied_state': None if self.applied_state is None else self.applied_state.to_dict(),
            'observed_state': None if self.observed_state is None else self.observed_state.to_dict(),
            'last_update_timestamp': None if self.last_update_timestamp is None else int(self.last_update_timestamp),
            'data_age_ticks': self.data_age_ticks,
            'diagnostic_summary': self.diagnostic_summary,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RuntimeVariableState:
    variable_id: str
    expression_label: str
    requested_state: RuntimeTruthRecord | None = None
    applied_state: RuntimeTruthRecord | None = None
    observed_state: RuntimeTruthRecord | None = None
    dependency_ids: tuple[str, ...] = ()
    availability: RuntimeAvailability = RuntimeAvailability.UNKNOWN
    last_update_timestamp: EventTime | None = None
    data_age_ticks: int | None = None
    diagnostic_summary: str = ''

    def to_dict(self) -> dict[str, object]:
        return {
            'variable_id': self.variable_id,
            'expression_label': self.expression_label,
            'dependency_ids': list(self.dependency_ids),
            'availability': self.availability.value,
            'requested_state': None if self.requested_state is None else self.requested_state.to_dict(),
            'applied_state': None if self.applied_state is None else self.applied_state.to_dict(),
            'observed_state': None if self.observed_state is None else self.observed_state.to_dict(),
            'last_update_timestamp': None if self.last_update_timestamp is None else int(self.last_update_timestamp),
            'data_age_ticks': self.data_age_ticks,
            'diagnostic_summary': self.diagnostic_summary,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RuntimePostureState:
    posture_id: str
    posture_kind: RuntimePostureKind
    summary: str
    authority_zone: RuntimeAuthorityZone = RuntimeAuthorityZone.REVIEW
    requested_state: RuntimeTruthRecord | None = None
    applied_state: RuntimeTruthRecord | None = None
    observed_state: RuntimeTruthRecord | None = None
    availability: RuntimeAvailability = RuntimeAvailability.UNKNOWN
    authority_enabled: bool = False
    last_update_timestamp: EventTime | None = None
    diagnostic_summary: str = ''

    def to_dict(self) -> dict[str, object]:
        return {
            'posture_id': self.posture_id,
            'posture_kind': self.posture_kind.value,
            'summary': self.summary,
            'authority_zone': self.authority_zone.value,
            'requested_state': None if self.requested_state is None else self.requested_state.to_dict(),
            'applied_state': None if self.applied_state is None else self.applied_state.to_dict(),
            'observed_state': None if self.observed_state is None else self.observed_state.to_dict(),
            'availability': self.availability.value,
            'authority_enabled': self.authority_enabled,
            'last_update_timestamp': None if self.last_update_timestamp is None else int(self.last_update_timestamp),
            'diagnostic_summary': self.diagnostic_summary,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RuntimeStateSnapshot:
    identity: RuntimeStateIdentity
    devices: tuple[RuntimeDeviceState, ...] = ()
    points: tuple[RuntimeDevicePointState, ...] = ()
    mappings: tuple[RuntimeMappingState, ...] = ()
    signals: tuple[RuntimeSignalState, ...] = ()
    variables: tuple[RuntimeVariableState, ...] = ()
    logic_posture: RuntimePostureState | None = None
    command_posture: RuntimePostureState | None = None
    safety_posture: RuntimePostureState | None = None
    ui_review_projection: RuntimePostureState | None = None
    requested_state: RuntimeTruthRecord = field(default_factory=lambda: _default_truth(RuntimeTruthKind.REQUESTED))
    applied_state: RuntimeTruthRecord = field(default_factory=lambda: _default_truth(RuntimeTruthKind.APPLIED))
    observed_state: RuntimeTruthRecord = field(default_factory=lambda: _default_truth(RuntimeTruthKind.OBSERVED))
    stale_state: RuntimeTruthRecord = field(default_factory=lambda: _availability_truth(RuntimeTruthStatus.NONE, 'No stale runtime state is present.'))
    unavailable_state: RuntimeTruthRecord = field(default_factory=lambda: _availability_truth(RuntimeTruthStatus.NONE, 'No unavailable runtime state is present.'))
    degraded_state: RuntimeTruthRecord = field(default_factory=lambda: _availability_truth(RuntimeTruthStatus.NONE, 'No degraded runtime state is present.'))
    simulated_state: RuntimeTruthRecord = field(default_factory=lambda: _availability_truth(RuntimeTruthStatus.NONE, 'No simulated runtime state is present.'))
    diagnostic_summary: tuple[str, ...] = ()
    runtime_status: Mapping[str, object] = field(default_factory=dict)

    @classmethod
    def build(cls, **kwargs: Any) -> RuntimeStateSnapshot:
        return build_authoritative_runtime_snapshot(**kwargs)

    def to_dict(self) -> dict[str, object]:
        return {
            'identity': self.identity.to_dict(),
            'devices': _sequence_to_dict(self.devices),
            'points': _sequence_to_dict(self.points),
            'mappings': _sequence_to_dict(self.mappings),
            'signals': _sequence_to_dict(self.signals),
            'variables': _sequence_to_dict(self.variables),
            'logic_posture': None if self.logic_posture is None else self.logic_posture.to_dict(),
            'command_posture': None if self.command_posture is None else self.command_posture.to_dict(),
            'safety_posture': None if self.safety_posture is None else self.safety_posture.to_dict(),
            'ui_review_projection': None if self.ui_review_projection is None else self.ui_review_projection.to_dict(),
            'requested_state': self.requested_state.to_dict(),
            'applied_state': self.applied_state.to_dict(),
            'observed_state': self.observed_state.to_dict(),
            'stale_state': self.stale_state.to_dict(),
            'unavailable_state': self.unavailable_state.to_dict(),
            'degraded_state': self.degraded_state.to_dict(),
            'simulated_state': self.simulated_state.to_dict(),
            'diagnostic_summary': list(self.diagnostic_summary),
            'runtime_status': _json_value(dict(self.runtime_status)),
        }


def _default_truth(kind: RuntimeTruthKind) -> RuntimeTruthRecord:
    return RuntimeTruthRecord(
        truth_kind=kind,
        status=RuntimeTruthStatus.NONE,
        summary=f'No {kind.value} runtime truth is present.',
        authoritative=False,
    )


def _availability_truth(status: RuntimeTruthStatus, summary: str, *, value: object | None = None) -> RuntimeTruthRecord:
    return RuntimeTruthRecord(
        truth_kind=RuntimeTruthKind.OBSERVED,
        status=status,
        summary=summary,
        value=value,
        authoritative=False,
    )


def _sandbox_status(lifecycle: SandboxMappingLifecycle) -> RuntimeTruthStatus:
    return RuntimeTruthStatus(lifecycle.value)


def _sandbox_mapping_projection(
    *,
    sandbox_mapping_state: MappingSandboxState,
    lifecycle: SandboxMappingLifecycle,
    timestamp: EventTime,
    sequence_number: int | None,
) -> RuntimeMappingState:
    state_payload = sandbox_mapping_state.to_dict()
    binding_count = len(state_payload.get('bindings', ()))
    state_hash = sandbox_mapping_state.state_hash()
    source = RuntimeSourceIdentity(
        source_id='mapping-sandbox',
        source_kind='sandbox',
        label='Sprint 1 sandbox mapping state',
        device_identity_key=str(state_payload.get('device_identity_key', '')),
    )
    requested = RuntimeTruthRecord(
        truth_kind=RuntimeTruthKind.REQUESTED,
        status=_sandbox_status(lifecycle),
        summary='Sandbox mapping is visible for review only; it is not live applied state.',
        value={
            'sandbox_id': state_payload.get('sandbox_id'),
            'revision': state_payload.get('revision'),
            'binding_count': binding_count,
            'state_hash': state_hash,
            'bindings': state_payload.get('bindings', ()),
        },
        source=source,
        timestamp=timestamp,
        sequence_number=sequence_number,
        authoritative=False,
        diagnostics=('sandbox mapping remains non-authoritative',),
    )
    return RuntimeMappingState(
        mapping_id=f"sandbox::{state_payload.get('sandbox_id', 'mapping-sandbox')}",
        authority_zone=RuntimeAuthorityZone.SANDBOX,
        lifecycle=lifecycle.value,
        device_identity_key=str(state_payload.get('device_identity_key', '')),
        requested_state=requested,
        applied_state=None,
        observed_state=None,
        binding_count=binding_count,
        state_hash=state_hash,
        last_update_timestamp=_event_time(state_payload.get('updated_timestamp')) or timestamp,
        diagnostic_summary='Sandbox/proposal/preflight state only; not hardware configuration or output authority.',
    )


def _posture(
    *,
    posture_id: str,
    posture_kind: RuntimePostureKind,
    summary: str,
    status: RuntimeTruthStatus = RuntimeTruthStatus.REVIEW,
) -> RuntimePostureState:
    requested = RuntimeTruthRecord(
        truth_kind=RuntimeTruthKind.REQUESTED,
        status=status,
        summary=summary,
        authoritative=False,
    )
    return RuntimePostureState(
        posture_id=posture_id,
        posture_kind=posture_kind,
        summary=summary,
        requested_state=requested,
        applied_state=None,
        observed_state=None,
        availability=RuntimeAvailability.UNKNOWN,
        authority_enabled=False,
        diagnostic_summary='Posture is represented without granting runtime authority.',
    )


def _count_availability(items: Sequence[Any], availability: RuntimeAvailability) -> int:
    return sum(1 for item in items if getattr(item, 'availability', getattr(item, 'posture', None)) == availability)


def _has_simulated_sources(
    *,
    devices: Sequence[RuntimeDeviceState],
    points: Sequence[RuntimeDevicePointState],
    explicit_simulated: bool,
) -> bool:
    return explicit_simulated or any(item.source.simulated for item in devices) or any(item.source.simulated for item in points)


def build_authoritative_runtime_snapshot(
    *,
    timestamp: EventTime | int = 0,
    sequence_number: int | None = None,
    snapshot_id: str | None = None,
    devices: Sequence[RuntimeDeviceState] = (),
    points: Sequence[RuntimeDevicePointState] = (),
    mappings: Sequence[RuntimeMappingState] = (),
    sandbox_mapping_state: MappingSandboxState | None = None,
    sandbox_mapping_lifecycle: SandboxMappingLifecycle = SandboxMappingLifecycle.SANDBOX,
    signals: Sequence[RuntimeSignalState] = (),
    variables: Sequence[RuntimeVariableState] = (),
    logic_posture: RuntimePostureState | None = None,
    command_posture: RuntimePostureState | None = None,
    safety_posture: RuntimePostureState | None = None,
    ui_review_projection: RuntimePostureState | None = None,
    runtime_status: Mapping[str, object] | None = None,
    diagnostic_summary: Sequence[str] = (),
    simulated: bool = False,
) -> RuntimeStateSnapshot:
    snapshot_time = as_event_time(int(timestamp))
    resolved_snapshot_id = snapshot_id or f'runtime-state::{int(snapshot_time)}::{0 if sequence_number is None else sequence_number}'
    sorted_devices = tuple(sorted(devices, key=lambda item: item.device_id))
    sorted_points = tuple(sorted(points, key=lambda item: item.stable_key))
    mapping_rows = list(mappings)
    if sandbox_mapping_state is not None:
        mapping_rows.append(
            _sandbox_mapping_projection(
                sandbox_mapping_state=sandbox_mapping_state,
                lifecycle=sandbox_mapping_lifecycle,
                timestamp=snapshot_time,
                sequence_number=sequence_number,
            )
        )
    sorted_mappings = tuple(sorted(mapping_rows, key=lambda item: item.mapping_id))
    sorted_signals = tuple(sorted(signals, key=lambda item: item.signal_id))
    sorted_variables = tuple(sorted(variables, key=lambda item: item.variable_id))
    runtime_status_payload = {} if runtime_status is None else {str(key): value for key, value in runtime_status.items()}

    stale_count = (
        _count_availability(sorted_devices, RuntimeAvailability.STALE)
        + _count_availability(sorted_points, RuntimeAvailability.STALE)
        + _count_availability(sorted_signals, RuntimeAvailability.STALE)
        + _count_availability(sorted_variables, RuntimeAvailability.STALE)
    )
    unavailable_count = (
        _count_availability(sorted_devices, RuntimeAvailability.UNAVAILABLE)
        + _count_availability(sorted_points, RuntimeAvailability.UNAVAILABLE)
        + _count_availability(sorted_signals, RuntimeAvailability.UNAVAILABLE)
        + _count_availability(sorted_variables, RuntimeAvailability.UNAVAILABLE)
    )
    degraded_count = (
        _count_availability(sorted_devices, RuntimeAvailability.DEGRADED)
        + _count_availability(sorted_points, RuntimeAvailability.DEGRADED)
        + _count_availability(sorted_signals, RuntimeAvailability.DEGRADED)
        + _count_availability(sorted_variables, RuntimeAvailability.DEGRADED)
    )
    simulated_present = _has_simulated_sources(devices=sorted_devices, points=sorted_points, explicit_simulated=simulated)
    if not sorted_devices:
        unavailable_count += 1

    summaries = list(diagnostic_summary)
    if not sorted_devices:
        summaries.append('No runtime devices are present in this snapshot.')
    if sandbox_mapping_state is not None:
        summaries.append('Sandbox mapping state is projected as requested/review state only.')

    return RuntimeStateSnapshot(
        identity=RuntimeStateIdentity(
            snapshot_id=resolved_snapshot_id,
            model_version=RUNTIME_STATE_MODEL_VERSION,
            timestamp=snapshot_time,
            sequence_number=sequence_number,
        ),
        devices=sorted_devices,
        points=sorted_points,
        mappings=sorted_mappings,
        signals=sorted_signals,
        variables=sorted_variables,
        logic_posture=logic_posture or _posture(
            posture_id='logic-posture',
            posture_kind=RuntimePostureKind.LOGIC,
            summary='Runtime logic deployment is not active in this sprint.',
            status=RuntimeTruthStatus.BLOCKED,
        ),
        command_posture=command_posture or _posture(
            posture_id='command-posture',
            posture_kind=RuntimePostureKind.COMMAND,
            summary='Production command authority is unavailable; no output writes are granted.',
            status=RuntimeTruthStatus.BLOCKED,
        ),
        safety_posture=safety_posture or _posture(
            posture_id='safety-posture',
            posture_kind=RuntimePostureKind.SAFETY,
            summary='Safety posture is visible for review without physical output authority.',
            status=RuntimeTruthStatus.REVIEW,
        ),
        ui_review_projection=ui_review_projection or _posture(
            posture_id='ui-review-projection',
            posture_kind=RuntimePostureKind.UI_REVIEW,
            summary='UI/review projections should read this snapshot without becoming machine truth.',
            status=RuntimeTruthStatus.REVIEW,
        ),
        requested_state=RuntimeTruthRecord(
            truth_kind=RuntimeTruthKind.REQUESTED,
            status=RuntimeTruthStatus.REVIEW if sandbox_mapping_state is not None else RuntimeTruthStatus.NONE,
            summary='Requested runtime truth is separate from applied and observed truth.',
            value={'mapping_request_count': sum(1 for item in sorted_mappings if item.requested_state is not None)},
            timestamp=snapshot_time,
            sequence_number=sequence_number,
            authoritative=False,
        ),
        applied_state=RuntimeTruthRecord(
            truth_kind=RuntimeTruthKind.APPLIED,
            status=RuntimeTruthStatus.APPLIED if any(item.authoritative_applied for item in sorted_mappings) else RuntimeTruthStatus.NONE,
            summary='Applied runtime truth is present only for authoritative applied state.',
            value={'authoritative_mapping_count': sum(1 for item in sorted_mappings if item.authoritative_applied)},
            timestamp=snapshot_time,
            sequence_number=sequence_number,
            authoritative=any(item.authoritative_applied for item in sorted_mappings),
        ),
        observed_state=RuntimeTruthRecord(
            truth_kind=RuntimeTruthKind.OBSERVED,
            status=RuntimeTruthStatus.OBSERVED if any(item.observed_state is not None for item in sorted_mappings) else RuntimeTruthStatus.NONE,
            summary='Observed runtime truth is readback/evidence, not a request or apply claim.',
            value={'observed_mapping_count': sum(1 for item in sorted_mappings if item.observed_state is not None)},
            timestamp=snapshot_time,
            sequence_number=sequence_number,
            authoritative=False,
        ),
        stale_state=_availability_truth(
            RuntimeTruthStatus.STALE if stale_count else RuntimeTruthStatus.NONE,
            'Stale runtime state is present.' if stale_count else 'No stale runtime state is present.',
            value={'count': stale_count},
        ),
        unavailable_state=_availability_truth(
            RuntimeTruthStatus.UNAVAILABLE if unavailable_count else RuntimeTruthStatus.NONE,
            'Unavailable runtime state is present.' if unavailable_count else 'No unavailable runtime state is present.',
            value={'count': unavailable_count},
        ),
        degraded_state=_availability_truth(
            RuntimeTruthStatus.DEGRADED if degraded_count else RuntimeTruthStatus.NONE,
            'Degraded runtime state is present.' if degraded_count else 'No degraded runtime state is present.',
            value={'count': degraded_count},
        ),
        simulated_state=_availability_truth(
            RuntimeTruthStatus.SIMULATED if simulated_present else RuntimeTruthStatus.NONE,
            'Simulated/demo runtime state is present.' if simulated_present else 'No simulated runtime state is present.',
            value={'present': simulated_present},
        ),
        diagnostic_summary=tuple(summaries),
        runtime_status=runtime_status_payload,
    )


@dataclass(frozen=True, slots=True)
class RuntimeStateService:
    def build_snapshot(
        self,
        *,
        timestamp: EventTime | int = 0,
        sequence_number: int | None = None,
        snapshot_id: str | None = None,
        devices: Sequence[RuntimeDeviceState] = (),
        points: Sequence[RuntimeDevicePointState] = (),
        mappings: Sequence[RuntimeMappingState] = (),
        sandbox_mapping_state: MappingSandboxState | None = None,
        sandbox_mapping_lifecycle: SandboxMappingLifecycle = SandboxMappingLifecycle.SANDBOX,
        signals: Sequence[RuntimeSignalState] = (),
        variables: Sequence[RuntimeVariableState] = (),
        logic_posture: RuntimePostureState | None = None,
        command_posture: RuntimePostureState | None = None,
        safety_posture: RuntimePostureState | None = None,
        ui_review_projection: RuntimePostureState | None = None,
        runtime_status: Mapping[str, object] | None = None,
        diagnostic_summary: Sequence[str] = (),
        simulated: bool = False,
    ) -> RuntimeStateSnapshot:
        return build_authoritative_runtime_snapshot(
            timestamp=timestamp,
            sequence_number=sequence_number,
            snapshot_id=snapshot_id,
            devices=devices,
            points=points,
            mappings=mappings,
            sandbox_mapping_state=sandbox_mapping_state,
            sandbox_mapping_lifecycle=sandbox_mapping_lifecycle,
            signals=signals,
            variables=variables,
            logic_posture=logic_posture,
            command_posture=command_posture,
            safety_posture=safety_posture,
            ui_review_projection=ui_review_projection,
            runtime_status=runtime_status,
            diagnostic_summary=diagnostic_summary,
            simulated=simulated,
        )
