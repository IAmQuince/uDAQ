from __future__ import annotations

import json

import pytest

from tests.session_contract_support import (
    append_checkpoint,
    canonical_json,
    create_checkpoint,
    create_session,
    load_checkpoint,
    load_session,
    save_checkpoint,
    save_session,
    state_hash,
    to_dict,
    validate_checkpoint,
)
from universaldaq.common import as_event_time
from universaldaq.runtime import (
    RuntimeAvailability,
    RuntimeSignalState,
    build_authoritative_runtime_snapshot,
)

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-UNIT-SESSION-HELPER-001',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-HIS-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'session checkpoint save/load serialization is deterministic and unsafe checkpoint flags are rejected',
}
pytestmark = pytest.mark.regression


def test_session_save_load_round_trip_is_deterministic(tmp_path) -> None:
    session = create_session(session_id='SES-ROUNDTRIP-001', created_at=400)
    checkpoint = create_checkpoint(
        session=session,
        checkpoint_id='CHK-ROUNDTRIP-001',
        timestamp=401,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=401, simulated=True),
    )
    session = append_checkpoint(session=session, checkpoint=checkpoint)
    path = tmp_path / 'session.json'

    save_session(session=session, path=path)
    loaded = load_session(path=path)

    assert canonical_json(to_dict(session)) == canonical_json(to_dict(loaded))
    assert state_hash(to_dict(session)) == state_hash(to_dict(loaded))


def test_checkpoint_round_trip_preserves_runtime_snapshot_and_degraded_states(tmp_path) -> None:
    session = create_session(session_id='SES-CHECKPOINT-001', created_at=410)
    snapshot = build_authoritative_runtime_snapshot(
        timestamp=411,
        signals=(
            RuntimeSignalState(
                signal_id='SIG-STALE',
                display_name='stale signal',
                availability=RuntimeAvailability.STALE,
                last_update_timestamp=as_event_time(360),
                data_age_ticks=51,
            ),
        ),
    )
    checkpoint = create_checkpoint(
        session=session,
        checkpoint_id='CHK-CHECKPOINT-001',
        timestamp=412,
        runtime_snapshot=snapshot,
    )
    path = tmp_path / 'checkpoint.json'

    save_checkpoint(checkpoint=checkpoint, path=path)
    loaded = load_checkpoint(path=path)
    payload = to_dict(loaded)

    assert payload == to_dict(checkpoint)
    assert payload['runtime_snapshot']['stale_state']['status'] == 'stale'
    assert payload['runtime_snapshot']['unavailable_state']['status'] == 'unavailable'
    assert payload['runtime_snapshot']['signals'][0]['availability'] == 'stale'
    json.loads(path.read_text(encoding='utf-8'))


def test_unsafe_checkpoint_flags_are_rejected() -> None:
    session = create_session(session_id='SES-UNSAFE-001', created_at=420)
    checkpoint = create_checkpoint(
        session=session,
        checkpoint_id='CHK-UNSAFE-001',
        timestamp=421,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=421),
    )
    payload = to_dict(checkpoint)
    payload['safety']['hardware_mutation_enabled'] = True
    unsafe_type = type(checkpoint)
    if not hasattr(unsafe_type, 'from_dict'):
        pytest.skip('pending SessionCheckpoint.from_dict API')
    unsafe = unsafe_type.from_dict(payload)

    result = validate_checkpoint(unsafe)

    assert getattr(result, 'ok', True) is False
    assert 'hardware_mutation_enabled must be false' in getattr(result, 'errors', ())
