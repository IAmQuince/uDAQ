from __future__ import annotations

import pytest

from universaldaq.runtime import build_authoritative_runtime_snapshot
from universaldaq.session import (
    REPLAY_EVIDENCE_SCHEMA_VERSION,
    DurableSessionService,
    build_checkpoint_replay_evidence,
)

TEST_DECLARATION = {
    "test_id": "UDQ-TST-SESSION-002",
    "verifies_requirements": ["UDQ-REQ-DIAG-001", "UDQ-REQ-HIS-001"],
    "checks_invariants": ["UDQ-INV-STATE-001", "UDQ-INV-STATE-004"],
    "worked_example_reference": None,
    "expected_proof_output": "checkpoint replay evidence carries deterministic hashes and no live authority",
}
pytestmark = pytest.mark.regression


def test_replay_view_carries_checkpoint_hash_and_review_authority_scope() -> None:
    service = DurableSessionService()
    session = service.create_session(session_id="SES-REPLAY-001", created_at=720)
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id="CHK-REPLAY-001",
        timestamp=721,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=721, sequence_number=21),
    )
    replay = service.build_replay_view(
        session=service.append_checkpoint(session=session, checkpoint=checkpoint),
        checkpoint=checkpoint,
        replay_id="REPLAY-001",
        created_at=722,
    )
    payload = replay.to_dict()

    assert payload["authority_scope"] == "review_session_only"
    assert payload["checkpoint_hash"] == checkpoint.checkpoint_hash
    assert payload["runtime_snapshot_hash"] == checkpoint.runtime_snapshot_hash
    assert payload["replay_is_live"] is False
    assert payload["safety"]["live_mapping_apply_enabled"] is False
    assert payload["safety"]["hardware_mutation_enabled"] is False


def test_checkpoint_replay_evidence_is_deterministic_and_summary_only() -> None:
    service = DurableSessionService()
    session = service.create_session(session_id="SES-EVIDENCE-001", created_at=730)
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id="CHK-EVIDENCE-001",
        timestamp=731,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=731, sequence_number=31),
    )
    session = service.append_checkpoint(session=session, checkpoint=checkpoint)
    replay = service.build_replay_view(
        session=session,
        checkpoint=checkpoint,
        replay_id="REPLAY-EVIDENCE-001",
        created_at=732,
    )

    evidence_a = build_checkpoint_replay_evidence(
        replay=replay, checkpoint=checkpoint, session=session
    )
    evidence_b = service.build_replay_evidence(
        session=session,
        checkpoint=checkpoint,
        replay_id="REPLAY-EVIDENCE-001",
        created_at=732,
    )

    assert evidence_a == evidence_b
    assert evidence_a["schema_version"] == REPLAY_EVIDENCE_SCHEMA_VERSION
    assert evidence_a["authority_scope"] == "review_session_only"
    assert evidence_a["replay_is_live"] is False
    assert evidence_a["checkpoint_hash"] == checkpoint.checkpoint_hash
    assert evidence_a["runtime_snapshot_hash"] == checkpoint.runtime_snapshot_hash
    assert evidence_a["replay_evidence_hash"]
    assert "runtime_snapshot" not in evidence_a
