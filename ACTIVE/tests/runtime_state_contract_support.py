from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import universaldaq.runtime as runtime_module
from universaldaq.common import as_event_time
from universaldaq.mapping import build_demo_sandbox_state
from universaldaq.runtime import (
    RuntimeAuthorityZone,
    RuntimeAvailability,
    RuntimeDeviceLifecycle,
    RuntimeDeviceState,
    RuntimeMappingState,
    RuntimeSignalState,
    RuntimeSourceIdentity,
    RuntimeTruthKind,
    RuntimeTruthRecord,
    RuntimeTruthStatus,
    RuntimeVariableState,
    SandboxMappingLifecycle,
)


def load_authoritative_runtime_state_api() -> tuple[type[Any] | None, Any | None]:
    snapshot_type = getattr(runtime_module, 'RuntimeStateSnapshot', None)
    builder = getattr(runtime_module, 'build_runtime_state_snapshot', None)
    if snapshot_type is None and builder is None:
        raise AssertionError('authoritative runtime-state API is not exported from universaldaq.runtime')
    return snapshot_type, builder


def materialize_runtime_state_snapshot(payload: Mapping[str, Any]) -> Any:
    snapshot_type, builder = load_authoritative_runtime_state_api()
    assert snapshot_type is not None
    assert builder is not None
    case = str(payload.get('case', 'empty'))
    if case == 'degraded':
        return _build_degraded_runtime_snapshot(builder)
    return builder(timestamp=1000, sequence_number=1, snapshot_id='RTSNAP-EMPTY-001', simulated=True)


def runtime_state_to_dict(snapshot: Any) -> dict[str, Any]:
    if isinstance(snapshot, Mapping):
        return {str(key): value for key, value in snapshot.items()}
    for method_name in ('as_dict', 'to_dict', 'model_dump', 'dict'):
        method = getattr(snapshot, method_name, None)
        if callable(method):
            payload = method()
            if isinstance(payload, Mapping):
                return {str(key): value for key, value in payload.items()}
    raise AssertionError(
        'authoritative runtime-state snapshot is not serializable through as_dict(), '
        'to_dict(), model_dump(), dict(), or dataclasses.asdict()'
    )


def canonical_runtime_state_json(snapshot: Any) -> str:
    return json.dumps(runtime_state_to_dict(snapshot), sort_keys=True, separators=(',', ':'))


def build_empty_runtime_state_payload() -> dict[str, Any]:
    return {'case': 'empty'}


def build_degraded_runtime_state_payload() -> dict[str, Any]:
    return {'case': 'degraded'}


def _source(*, source_id: str, simulated: bool = False) -> RuntimeSourceIdentity:
    return RuntimeSourceIdentity(
        source_id=source_id,
        source_kind='simulated' if simulated else 'adapter',
        adapter_id=source_id,
        device_identity_key=source_id.replace('SRC', 'DEV'),
        simulated=simulated,
    )


def _truth(
    *,
    kind: RuntimeTruthKind,
    status: RuntimeTruthStatus,
    value: object,
    timestamp: int,
    authoritative: bool = False,
) -> RuntimeTruthRecord:
    return RuntimeTruthRecord(
        truth_kind=kind,
        status=status,
        summary=f'{kind.value} test truth',
        value=value,
        timestamp=as_event_time(timestamp),
        authoritative=authoritative,
    )


def _build_degraded_runtime_snapshot(builder: Any) -> Any:
    sim_source = _source(source_id='SRC-SIM-001', simulated=True)
    real_source = _source(source_id='SRC-REAL-001')
    unavailable_source = _source(source_id='SRC-REAL-002')
    devices = (
        RuntimeDeviceState(
            device_id='DEV-SIM-001',
            lifecycle=RuntimeDeviceLifecycle.SIMULATED,
            source=sim_source,
            posture=RuntimeAvailability.SIMULATED,
            requested_state=_truth(
                kind=RuntimeTruthKind.REQUESTED,
                status=RuntimeTruthStatus.SIMULATED,
                value='discover',
                timestamp=2000,
            ),
            applied_state=_truth(
                kind=RuntimeTruthKind.APPLIED,
                status=RuntimeTruthStatus.SIMULATED,
                value='simulated_attached',
                timestamp=2001,
            ),
            observed_state=_truth(
                kind=RuntimeTruthKind.OBSERVED,
                status=RuntimeTruthStatus.SIMULATED,
                value='simulated_attached',
                timestamp=2002,
            ),
        ),
        RuntimeDeviceState(
            device_id='DEV-REAL-001',
            lifecycle=RuntimeDeviceLifecycle.UNAVAILABLE,
            source=unavailable_source,
            posture=RuntimeAvailability.UNAVAILABLE,
            requested_state=_truth(
                kind=RuntimeTruthKind.REQUESTED,
                status=RuntimeTruthStatus.REVIEW,
                value='discover',
                timestamp=2000,
            ),
            applied_state=_truth(
                kind=RuntimeTruthKind.APPLIED,
                status=RuntimeTruthStatus.UNAVAILABLE,
                value='not_attached',
                timestamp=2001,
            ),
            observed_state=_truth(
                kind=RuntimeTruthKind.OBSERVED,
                status=RuntimeTruthStatus.UNAVAILABLE,
                value='device_missing',
                timestamp=2002,
            ),
        ),
        RuntimeDeviceState(
            device_id='DEV-REAL-002',
            lifecycle=RuntimeDeviceLifecycle.DEGRADED,
            source=real_source,
            posture=RuntimeAvailability.DEGRADED,
            requested_state=_truth(
                kind=RuntimeTruthKind.REQUESTED,
                status=RuntimeTruthStatus.REVIEW,
                value='connected',
                timestamp=2000,
            ),
            applied_state=_truth(
                kind=RuntimeTruthKind.APPLIED,
                status=RuntimeTruthStatus.DEGRADED,
                value='degraded',
                timestamp=2001,
            ),
            observed_state=_truth(
                kind=RuntimeTruthKind.OBSERVED,
                status=RuntimeTruthStatus.STALE,
                value='stale',
                timestamp=2002,
            ),
        ),
    )
    signals = (
        RuntimeSignalState(
            signal_id='SIG-001',
            display_name='stale test signal',
            requested_state=_truth(
                kind=RuntimeTruthKind.REQUESTED,
                status=RuntimeTruthStatus.REVIEW,
                value={'value': 10},
                timestamp=2000,
            ),
            applied_state=_truth(
                kind=RuntimeTruthKind.APPLIED,
                status=RuntimeTruthStatus.APPLIED,
                value={'value': 9},
                timestamp=2001,
                authoritative=True,
            ),
            observed_state=_truth(
                kind=RuntimeTruthKind.OBSERVED,
                status=RuntimeTruthStatus.STALE,
                value={'value': 8},
                timestamp=2002,
            ),
            availability=RuntimeAvailability.STALE,
        ),
        RuntimeSignalState(
            signal_id='SIG-002',
            display_name='unknown test signal',
            requested_state=_truth(
                kind=RuntimeTruthKind.REQUESTED,
                status=RuntimeTruthStatus.REVIEW,
                value={'value': None},
                timestamp=2000,
            ),
            applied_state=_truth(
                kind=RuntimeTruthKind.APPLIED,
                status=RuntimeTruthStatus.NONE,
                value={'value': None},
                timestamp=2001,
            ),
            observed_state=_truth(
                kind=RuntimeTruthKind.OBSERVED,
                status=RuntimeTruthStatus.UNKNOWN,
                value={'value': None},
                timestamp=2002,
            ),
            availability=RuntimeAvailability.UNKNOWN,
        ),
    )
    variables = (
        RuntimeVariableState(
            variable_id='VAR-UNAVAILABLE',
            expression_label='missing(SIG-001)',
            dependency_ids=('SIG-001',),
            availability=RuntimeAvailability.UNAVAILABLE,
        ),
    )
    applied_mapping = RuntimeMappingState(
        mapping_id='authoritative::MAP-APPLIED-001',
        authority_zone=RuntimeAuthorityZone.AUTHORITATIVE,
        lifecycle='applied',
        device_identity_key='DEV-SIM-001',
        requested_state=_truth(
            kind=RuntimeTruthKind.REQUESTED,
            status=RuntimeTruthStatus.REVIEW,
            value={'mapping_id': 'MAP-APPLIED-001'},
            timestamp=2000,
        ),
        applied_state=_truth(
            kind=RuntimeTruthKind.APPLIED,
            status=RuntimeTruthStatus.APPLIED,
            value={'mapping_id': 'MAP-APPLIED-001'},
            timestamp=2001,
            authoritative=True,
        ),
        observed_state=_truth(
            kind=RuntimeTruthKind.OBSERVED,
            status=RuntimeTruthStatus.OBSERVED,
            value={'mapping_id': 'MAP-APPLIED-001'},
            timestamp=2002,
        ),
        binding_count=1,
    )
    return builder(
        timestamp=2000,
        sequence_number=2,
        snapshot_id='RTSNAP-DEGRADED-001',
        devices=devices,
        mappings=(applied_mapping,),
        sandbox_mapping_state=build_demo_sandbox_state(),
        sandbox_mapping_lifecycle=SandboxMappingLifecycle.PREFLIGHT,
        signals=signals,
        variables=variables,
        simulated=True,
    )
