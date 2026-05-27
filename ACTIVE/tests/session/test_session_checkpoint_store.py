from __future__ import annotations

import json

import pytest

from universaldaq.runtime import build_authoritative_runtime_snapshot
from universaldaq.session import (
    FileSystemSessionCheckpointStore,
    SessionCheckpointStoreError,
    restore_review_session,
)
from universaldaq.session.services import DurableSessionService

TEST_DECLARATION = {
    "test_id": "UDQ-TST-SESSION-001",
    "verifies_requirements": ["UDQ-REQ-DIAG-001", "UDQ-REQ-HIS-001"],
    "checks_invariants": ["UDQ-INV-STATE-001", "UDQ-INV-STATE-004"],
    "worked_example_reference": None,
    "expected_proof_output": "filesystem session checkpoint store remains deterministic and review-only",
}
pytestmark = pytest.mark.regression


def test_checkpoint_store_round_trips_hashes_and_review_restore(tmp_path) -> None:
    service = DurableSessionService()
    session = service.create_session(session_id="SES-STORE-001", created_at=700)
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id="CHK-STORE-001",
        timestamp=701,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=701, sequence_number=11),
    )
    store = FileSystemSessionCheckpointStore(tmp_path)

    path = store.save_checkpoint(checkpoint)
    loaded = store.load_checkpoint(session_id="SES-STORE-001", checkpoint_id="CHK-STORE-001")
    restored = restore_review_session(loaded)

    assert path.name == "CHK-STORE-001.json"
    assert loaded.checkpoint_hash == checkpoint.checkpoint_hash
    assert loaded.runtime_snapshot_hash == checkpoint.runtime_snapshot_hash
    assert loaded.to_dict()["authority_scope"] == "review_session_only"
    assert restored.to_dict()["authority_scope"] == "review_session_only"
    assert restored.to_dict()["safety"]["hardware_mutation_enabled"] is False
    assert store.list_checkpoints(session_id="SES-STORE-001") == (loaded,)


def test_checkpoint_store_rejects_corrupt_hash_and_unsafe_path_ids(tmp_path) -> None:
    service = DurableSessionService()
    session = service.create_session(session_id="SES-STORE-002", created_at=710)
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id="CHK-STORE-002",
        timestamp=711,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=711),
    )
    store = FileSystemSessionCheckpointStore(tmp_path)
    path = store.save_checkpoint(checkpoint)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["runtime_snapshot"]["identity"]["sequence_number"] = 999
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    with pytest.raises(SessionCheckpointStoreError, match="checkpoint hash mismatch"):
        store.load_checkpoint(session_id="SES-STORE-002", checkpoint_id="CHK-STORE-002")
    with pytest.raises(SessionCheckpointStoreError, match="path-safe"):
        store.load_checkpoint(session_id="../bad", checkpoint_id="CHK-STORE-002")
