from __future__ import annotations

import json
import sys

from universaldaq.common import as_event_time
from universaldaq.mapping import build_demo_sandbox_state
from universaldaq.runtime import (
    RuntimeAuthorityZone,
    RuntimeAvailability,
    RuntimeDeviceLifecycle,
    RuntimeDevicePointState,
    RuntimeDeviceState,
    RuntimeMappingState,
    RuntimeSignalState,
    RuntimeSourceIdentity,
    RuntimeStateService,
    RuntimeTruthKind,
    RuntimeTruthRecord,
    RuntimeTruthStatus,
    RuntimeVariableState,
    SandboxMappingLifecycle,
    build_authoritative_runtime_snapshot,
)


def _source(*, simulated: bool = False) -> RuntimeSourceIdentity:
    return RuntimeSourceIdentity(
        source_id='SIM-SRC-001',
        source_kind='simulated' if simulated else 'adapter',
        label='generic simulated source' if simulated else 'generic adapter source',
        adapter_id='SIM-ADAPTER-001',
        device_identity_key='SIM-DEVICE-001',
        simulated=simulated,
    )


def test_authoritative_snapshot_builds_empty_json_state() -> None:
    snapshot = build_authoritative_runtime_snapshot(timestamp=100, sequence_number=1)

    payload = snapshot.to_dict()

    assert payload['identity']['model_version'] == 'udq.runtime.state.v1'
    assert payload['identity']['sequence_number'] == 1
    assert payload['devices'] == []
    assert payload['points'] == []
    assert payload['unavailable_state']['status'] == 'unavailable'
    assert payload['requested_state']['truth_kind'] == 'requested'
    assert payload['applied_state']['truth_kind'] == 'applied'
    assert payload['observed_state']['truth_kind'] == 'observed'
    json.dumps(payload, sort_keys=True)


def test_authoritative_snapshot_builds_simulated_demo_state() -> None:
    source = _source(simulated=True)
    point_observed = RuntimeTruthRecord(
        truth_kind=RuntimeTruthKind.OBSERVED,
        status=RuntimeTruthStatus.SIMULATED,
        summary='Simulated point sample.',
        value={'engineering_value': '42.0'},
        source=source,
        timestamp=as_event_time(205),
        data_age_ticks=5,
    )
    device = RuntimeDeviceState(
        device_id='SIM-DEVICE-001',
        display_name='Demo device',
        lifecycle=RuntimeDeviceLifecycle.SIMULATED,
        source=source,
        posture=RuntimeAvailability.SIMULATED,
        point_ids=('AIN0',),
    )
    point = RuntimeDevicePointState(
        point_id='AIN0',
        stable_key='SIM-DEVICE-001::AIN0',
        direction='input',
        source=source,
        availability=RuntimeAvailability.SIMULATED,
        units='V',
        observed_state=point_observed,
        last_update_timestamp=as_event_time(205),
        data_age_ticks=5,
    )
    signal = RuntimeSignalState(
        signal_id='SIG-DEMO-VOLTAGE',
        display_name='demo voltage',
        observed_state=point_observed,
        source_point_ids=(point.stable_key,),
        units='V',
        availability=RuntimeAvailability.SIMULATED,
    )

    payload = build_authoritative_runtime_snapshot(
        timestamp=210,
        sequence_number=2,
        devices=(device,),
        points=(point,),
        signals=(signal,),
        simulated=True,
    ).to_dict()

    assert payload['simulated_state']['status'] == 'simulated'
    assert payload['devices'][0]['source']['simulated'] is True
    assert payload['points'][0]['observed_state']['truth_kind'] == 'observed'
    assert payload['signals'][0]['availability'] == 'simulated'


def test_sandbox_mapping_projects_as_requested_non_authoritative_state() -> None:
    sandbox = build_demo_sandbox_state()
    before_hash = sandbox.state_hash()

    snapshot = build_authoritative_runtime_snapshot(
        timestamp=300,
        sequence_number=3,
        sandbox_mapping_state=sandbox,
        sandbox_mapping_lifecycle=SandboxMappingLifecycle.PREFLIGHT,
    )
    payload = snapshot.to_dict()

    assert sandbox.state_hash() == before_hash
    mapping = payload['mappings'][0]
    assert mapping['authority_zone'] == 'sandbox'
    assert mapping['lifecycle'] == 'preflight'
    assert mapping['requested_state']['status'] == 'preflight'
    assert mapping['requested_state']['authoritative'] is False
    assert mapping['applied_state'] is None
    assert mapping['observed_state'] is None
    assert mapping['authoritative_applied'] is False
    assert payload['applied_state']['status'] == 'none'
    assert payload['applied_state']['value']['authoritative_mapping_count'] == 0
    assert 'Sandbox mapping state is projected as requested/review state only.' in payload['diagnostic_summary']


def test_requested_applied_and_observed_mapping_truths_remain_separate() -> None:
    source = _source()
    requested = RuntimeTruthRecord(
        truth_kind=RuntimeTruthKind.REQUESTED,
        status=RuntimeTruthStatus.REVIEW,
        summary='Operator requested mapping review.',
        value={'endpoint': 'AIN0'},
        source=source,
        timestamp=as_event_time(400),
        authoritative=False,
    )
    applied = RuntimeTruthRecord(
        truth_kind=RuntimeTruthKind.APPLIED,
        status=RuntimeTruthStatus.APPLIED,
        summary='Controller-applied mapping placeholder from future live boundary.',
        value={'endpoint': 'AIN1'},
        source=source,
        timestamp=as_event_time(401),
        authoritative=True,
    )
    observed = RuntimeTruthRecord(
        truth_kind=RuntimeTruthKind.OBSERVED,
        status=RuntimeTruthStatus.OBSERVED,
        summary='Observed readback placeholder.',
        value={'endpoint': 'AIN2'},
        source=source,
        timestamp=as_event_time(402),
        authoritative=False,
    )
    mapping = RuntimeMappingState(
        mapping_id='authoritative::demo',
        authority_zone=RuntimeAuthorityZone.AUTHORITATIVE,
        lifecycle='applied',
        device_identity_key='SIM-DEVICE-001',
        requested_state=requested,
        applied_state=applied,
        observed_state=observed,
        binding_count=1,
        state_hash='hash-demo',
    )

    payload = RuntimeStateService().build_snapshot(timestamp=410, mappings=(mapping,)).to_dict()
    mapping_payload = payload['mappings'][0]

    assert mapping_payload['requested_state']['value']['endpoint'] == 'AIN0'
    assert mapping_payload['applied_state']['value']['endpoint'] == 'AIN1'
    assert mapping_payload['observed_state']['value']['endpoint'] == 'AIN2'
    assert payload['applied_state']['value']['authoritative_mapping_count'] == 1
    assert payload['observed_state']['value']['observed_mapping_count'] == 1


def test_stale_degraded_and_unavailable_states_serialize() -> None:
    source = _source()
    device = RuntimeDeviceState(
        device_id='DEV-DEGRADED',
        lifecycle=RuntimeDeviceLifecycle.DEGRADED,
        source=source,
        posture=RuntimeAvailability.DEGRADED,
        diagnostic_summary='device degraded for test',
    )
    signal = RuntimeSignalState(
        signal_id='SIG-STALE',
        display_name='stale signal',
        availability=RuntimeAvailability.STALE,
        data_age_ticks=999,
    )
    variable = RuntimeVariableState(
        variable_id='VAR-UNAVAILABLE',
        expression_label='missing(SIG-STALE)',
        availability=RuntimeAvailability.UNAVAILABLE,
        dependency_ids=('SIG-STALE',),
    )

    payload = build_authoritative_runtime_snapshot(
        timestamp=500,
        devices=(device,),
        signals=(signal,),
        variables=(variable,),
    ).to_dict()

    assert payload['degraded_state']['status'] == 'degraded'
    assert payload['degraded_state']['value']['count'] == 1
    assert payload['stale_state']['status'] == 'stale'
    assert payload['stale_state']['value']['count'] == 1
    assert payload['unavailable_state']['status'] == 'unavailable'
    assert payload['unavailable_state']['value']['count'] == 1
    json.dumps(payload, sort_keys=True)


def test_runtime_state_import_does_not_load_vendor_support_packs() -> None:
    assert not any(
        name.startswith(('universaldaq_labjack', 'universaldaq_arduino', 'universaldaq_rpi'))
        for name in sys.modules
    )


def test_default_postures_do_not_grant_live_apply_or_hardware_writes() -> None:
    payload = build_authoritative_runtime_snapshot(timestamp=600).to_dict()

    assert payload['command_posture']['authority_enabled'] is False
    assert payload['command_posture']['applied_state'] is None
    assert payload['command_posture']['requested_state']['status'] == 'blocked'
    assert payload['logic_posture']['authority_enabled'] is False
    assert payload['logic_posture']['requested_state']['status'] == 'blocked'
