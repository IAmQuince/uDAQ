from __future__ import annotations

import json

import pytest

from universaldaq.common import as_event_time
from universaldaq.runtime import RuntimeAvailability, RuntimeSignalState, build_authoritative_runtime_snapshot
from universaldaq.session import DurableSessionService, SessionMode

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-UNIT-SESSION-001',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-HIS-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'durable session and checkpoint models serialize authoritative runtime snapshots without live authority',
}
pytestmark = pytest.mark.regression


def test_empty_session_creation_is_hardware_free_and_non_live() -> None:
    service = DurableSessionService()
    session = service.create_session(session_id='SES-EMPTY-001', created_at=100, mode=SessionMode.DEMO)

    payload = session.to_dict()

    assert payload['model_version'] == 'udq.session.v1'
    assert payload['session_id'] == 'SES-EMPTY-001'
    assert payload['checkpoint_count'] == 0
    assert payload['safety']['hardware_mutation_enabled'] is False
    assert payload['safety']['live_mapping_apply_enabled'] is False
    assert payload['safety']['replay_is_live'] is False
    json.dumps(payload, sort_keys=True)


def test_checkpoint_embeds_runtime_snapshot_and_preserves_truth_channels() -> None:
    service = DurableSessionService()
    session = service.create_session(session_id='SES-RUNTIME-001', created_at=200)
    snapshot = build_authoritative_runtime_snapshot(timestamp=201, sequence_number=7)

    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id='CHK-RUNTIME-001',
        timestamp=202,
        runtime_snapshot=snapshot,
    )

    payload = checkpoint.to_dict()
    runtime_payload = payload['runtime_snapshot']

    assert payload['runtime_snapshot_model_version'] == 'udq.runtime.state.v1'
    assert runtime_payload['requested_state']['truth_kind'] == 'requested'
    assert runtime_payload['applied_state']['truth_kind'] == 'applied'
    assert runtime_payload['observed_state']['truth_kind'] == 'observed'
    assert service.validate_checkpoint(checkpoint).ok is True


def test_checkpoint_preserves_degraded_stale_unavailable_snapshot_state() -> None:
    service = DurableSessionService()
    session = service.create_session(session_id='SES-DEGRADED-001', created_at=300)
    snapshot = build_authoritative_runtime_snapshot(
        timestamp=301,
        signals=(
            RuntimeSignalState(
                signal_id='SIG-STALE',
                display_name='stale signal',
                availability=RuntimeAvailability.STALE,
                last_update_timestamp=as_event_time(250),
                data_age_ticks=51,
            ),
        ),
    )

    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id='CHK-DEGRADED-001',
        timestamp=302,
        runtime_snapshot=snapshot,
    )
    runtime_payload = checkpoint.to_dict()['runtime_snapshot']

    assert runtime_payload['stale_state']['status'] == 'stale'
    assert runtime_payload['unavailable_state']['status'] == 'unavailable'
    assert runtime_payload['signals'][0]['availability'] == 'stale'
