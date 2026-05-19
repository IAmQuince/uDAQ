from __future__ import annotations

import pytest

from tests.runtime_state_contract_support import (
    build_degraded_runtime_state_payload,
    build_empty_runtime_state_payload,
    materialize_runtime_state_snapshot,
    runtime_state_to_dict,
)

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-121',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'authoritative runtime-state snapshot contract covers identity, empty-state validity, degraded-state visibility, and sandbox/live boundary separation',
}
pytestmark = pytest.mark.contract


def test_runtime_state_snapshot_exposes_model_version_identity_and_empty_state_contract() -> None:
    snapshot = materialize_runtime_state_snapshot(build_empty_runtime_state_payload())
    payload = runtime_state_to_dict(snapshot)

    assert payload['identity']['model_version'] == 'udq.runtime.state.v1'
    assert payload['identity']['snapshot_id'] == 'RTSNAP-EMPTY-001'
    assert payload['identity']['timestamp'] == 1000
    assert payload['simulated_state']['status'] == 'simulated'
    assert payload['devices'] == []
    assert payload['points'] == []
    assert payload['signals'] == []
    assert payload['variables'] == []


def test_runtime_state_snapshot_keeps_requested_applied_and_observed_state_distinct() -> None:
    snapshot = materialize_runtime_state_snapshot(build_degraded_runtime_state_payload())
    payload = runtime_state_to_dict(snapshot)

    first_signal = payload['signals'][0]
    assert set(first_signal) >= {'requested_state', 'applied_state', 'observed_state'}
    assert first_signal['requested_state'] != first_signal['applied_state']
    assert first_signal['applied_state'] != first_signal['observed_state']

    first_device = payload['devices'][0]
    assert set(first_device) >= {'requested_state', 'applied_state', 'observed_state'}


def test_runtime_state_snapshot_makes_simulated_unavailable_recovering_and_stale_states_explicit() -> None:
    snapshot = materialize_runtime_state_snapshot(build_degraded_runtime_state_payload())
    payload = runtime_state_to_dict(snapshot)

    availability_states = {device['posture'] for device in payload['devices']}
    assert {'simulated', 'unavailable', 'degraded'}.issubset(availability_states)
    freshness_states = {signal['availability'] for signal in payload['signals']}
    assert {'stale', 'unknown'}.issubset(freshness_states)
    assert 'unknown' in freshness_states


def test_runtime_state_snapshot_preserves_sandbox_boundary_and_non_authoritative_postures() -> None:
    snapshot = materialize_runtime_state_snapshot(build_degraded_runtime_state_payload())
    payload = runtime_state_to_dict(snapshot)

    sandbox_mapping = next(item for item in payload['mappings'] if item['authority_zone'] == 'sandbox')
    applied_mapping = next(item for item in payload['mappings'] if item['authority_zone'] == 'authoritative')
    assert sandbox_mapping['lifecycle'] == 'preflight'
    assert sandbox_mapping['authoritative_applied'] is False
    assert applied_mapping['authoritative_applied'] is True

    assert payload['command_posture']['authority_enabled'] is False
    assert payload['safety_posture']['authority_enabled'] is False
    assert payload['logic_posture']['authority_enabled'] is False


def test_runtime_state_snapshot_handles_near_simultaneous_device_and_signal_degradation() -> None:
    snapshot = materialize_runtime_state_snapshot(build_degraded_runtime_state_payload())
    payload = runtime_state_to_dict(snapshot)

    degraded_device_ids = {
        device['device_id']
        for device in payload['devices']
        if device['posture'] in {'unavailable', 'degraded'}
    }
    degraded_signal_ids = {
        signal['signal_id']
        for signal in payload['signals']
        if signal['availability'] in {'stale', 'unknown'}
    }

    assert degraded_device_ids == {'DEV-REAL-001', 'DEV-REAL-002'}
    assert degraded_signal_ids == {'SIG-001', 'SIG-002'}
