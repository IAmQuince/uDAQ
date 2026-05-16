from __future__ import annotations

import json

import pytest

from universaldaq.runtime import build_authoritative_runtime_snapshot
from universaldaq.session import DurableSessionService, SessionCheckpoint, canonical_json, state_hash

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-UNIT-SESSION-002',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-HIS-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'session checkpoint save/load serialization is deterministic and unsafe checkpoint flags are rejected',
}
pytestmark = pytest.mark.regression


def test_session_save_load_round_trip_is_deterministic(tmp_path) -> None:
    service = DurableSessionService()
    session = service.create_session(session_id='SES-ROUNDTRIP-001', created_at=400)
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id='CHK-ROUNDTRIP-001',
        timestamp=401,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=401, simulated=True),
    )
    session = service.append_checkpoint(session=session, checkpoint=checkpoint)
    path = tmp_path / 'session.json'

    service.save_session(session=session, path=path)
    loaded = service.load_session(path=path)

    assert canonical_json(session.to_dict()) == canonical_json(loaded.to_dict())
    assert state_hash(session.to_dict()) == state_hash(loaded.to_dict())


def test_checkpoint_save_load_round_trip_preserves_runtime_snapshot(tmp_path) -> None:
    service = DurableSessionService()
    session = service.create_session(session_id='SES-CHECKPOINT-001', created_at=410)
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id='CHK-CHECKPOINT-001',
        timestamp=411,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=411),
    )
    path = tmp_path / 'checkpoint.json'

    service.save_checkpoint(checkpoint=checkpoint, path=path)
    loaded = service.load_checkpoint(path=path)

    assert loaded.to_dict() == checkpoint.to_dict()
    json.loads(path.read_text(encoding='utf-8'))


def test_unsafe_checkpoint_flags_are_rejected() -> None:
    service = DurableSessionService()
    session = service.create_session(session_id='SES-UNSAFE-001', created_at=420)
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id='CHK-UNSAFE-001',
        timestamp=421,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=421),
    )
    payload = checkpoint.to_dict()
    payload['safety']['hardware_mutation_enabled'] = True
    unsafe = SessionCheckpoint.from_dict(payload)

    result = service.validate_checkpoint(unsafe)

    assert result.ok is False
    assert 'hardware_mutation_enabled must be false' in result.errors
