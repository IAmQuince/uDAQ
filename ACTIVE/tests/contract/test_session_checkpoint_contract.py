from __future__ import annotations

import pytest

from universaldaq.runtime import build_authoritative_runtime_snapshot
from universaldaq.session import DurableSessionService

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-SESSION-001',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-HIS-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'session checkpoints preserve runtime requested/applied/observed truth and produce non-live replay views',
}
pytestmark = pytest.mark.contract


def test_session_checkpoint_contract_preserves_runtime_truth_and_non_live_replay() -> None:
    service = DurableSessionService()
    session = service.create_session(session_id='SES-CONTRACT-001', created_at=500)
    snapshot_payload = build_authoritative_runtime_snapshot(timestamp=501).to_dict()
    snapshot_payload['requested_state']['summary'] = 'requested checkpoint state'
    snapshot_payload['requested_state']['value'] = {'intent': 'review'}
    snapshot_payload['applied_state']['summary'] = 'no live apply'
    snapshot_payload['applied_state']['value'] = {'applied': False}
    snapshot_payload['observed_state']['summary'] = 'no live observed hardware state'
    snapshot_payload['observed_state']['value'] = {'observed_live': False}
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id='CHK-CONTRACT-001',
        timestamp=502,
        runtime_snapshot=snapshot_payload,
    )
    session = service.append_checkpoint(session=session, checkpoint=checkpoint)

    replay = service.build_replay_from_latest(session=session, replay_id='REPLAY-CONTRACT-001', created_at=503)
    payload = replay.to_dict()

    assert service.validate_session(session).ok is True
    assert payload['replay_is_live'] is False
    assert payload['safety']['hardware_mutation_enabled'] is False
    assert payload['safety']['live_mapping_apply_enabled'] is False
    assert payload['runtime_snapshot']['requested_state']['summary'] == 'requested checkpoint state'
    assert payload['runtime_snapshot']['applied_state']['value']['applied'] is False
    assert payload['runtime_snapshot']['observed_state']['value']['observed_live'] is False
