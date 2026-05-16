from __future__ import annotations

import pytest

from tests.session_contract_support import (
    accepted_session_api_names,
    append_checkpoint,
    build_replay_from_checkpoint,
    create_checkpoint,
    create_session,
    to_dict,
    validate_session,
)
from universaldaq.runtime import build_authoritative_runtime_snapshot

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-SESSION-001',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-HIS-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'session checkpoints preserve runtime truth channels and replay remains explicitly non-live',
}
pytestmark = pytest.mark.contract


def test_session_checkpoint_contract_preserves_runtime_truth_and_non_live_replay() -> None:
    assert {'DurableSession', 'SessionCheckpoint', 'ReplayView', 'DurableSessionService'}.issubset(
        set(accepted_session_api_names())
    )
    session = create_session(session_id='SES-CONTRACT-001', created_at=500)
    snapshot_payload = build_authoritative_runtime_snapshot(timestamp=501).to_dict()
    snapshot_payload['requested_state']['summary'] = 'requested checkpoint state'
    snapshot_payload['requested_state']['value'] = {'intent': 'review'}
    snapshot_payload['applied_state']['summary'] = 'no live apply'
    snapshot_payload['applied_state']['value'] = {'applied': False}
    snapshot_payload['observed_state']['summary'] = 'no live observed hardware state'
    snapshot_payload['observed_state']['value'] = {'observed_live': False}

    checkpoint = create_checkpoint(
        session=session,
        checkpoint_id='CHK-CONTRACT-001',
        timestamp=502,
        runtime_snapshot=snapshot_payload,
    )
    session = append_checkpoint(session=session, checkpoint=checkpoint)
    replay = build_replay_from_checkpoint(
        session=session,
        checkpoint=checkpoint,
        replay_id='REPLAY-CONTRACT-001',
        created_at=503,
    )
    payload = to_dict(replay)
    safety = payload['safety']

    assert validate_session(session).ok is True
    assert payload['replay_is_live'] is False
    assert safety['hardware_mutation_enabled'] is False
    assert safety['live_mapping_apply_enabled'] is False
    assert safety['replay_is_live'] is False
    assert safety['production_historian_enabled'] is False
    assert payload['runtime_snapshot']['requested_state']['summary'] == 'requested checkpoint state'
    assert payload['runtime_snapshot']['applied_state']['value']['applied'] is False
    assert payload['runtime_snapshot']['observed_state']['value']['observed_live'] is False
