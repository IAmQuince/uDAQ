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
    "test_id": "UDQ-TST-SESSION-003",
    "verifies_requirements": ["UDQ-REQ-DIAG-001", "UDQ-REQ-HIS-001"],
    "checks_invariants": ["UDQ-INV-STATE-001", "UDQ-INV-STATE-004"],
    "worked_example_reference": None,
    "expected_proof_output": "corrupt or unsafe checkpoint payloads fail closed at store load and review restore",
}
pytestmark = pytest.mark.regression


def test_checkpoint_store_rejects_invalid_json_and_missing_fields(tmp_path) -> None:
    service = DurableSessionService()
    session = service.create_session(session_id="SES-HARDEN-001", created_at=800)
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id="CHK-HARDEN-001",
        timestamp=801,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=801),
    )
    store = FileSystemSessionCheckpointStore(tmp_path)
    path = store.save_checkpoint(checkpoint)

    path.write_text("{not-json", encoding="utf-8")
    with pytest.raises(SessionCheckpointStoreError, match="invalid checkpoint payload"):
        store.load_checkpoint(session_id="SES-HARDEN-001", checkpoint_id="CHK-HARDEN-001")

    path.write_text(json.dumps({"schema_version": "udq.session.checkpoint.v1"}), encoding="utf-8")
    with pytest.raises(SessionCheckpointStoreError, match="invalid checkpoint payload"):
        store.load_checkpoint(session_id="SES-HARDEN-001", checkpoint_id="CHK-HARDEN-001")


def test_restore_review_session_rejects_unsafe_checkpoint() -> None:
    service = DurableSessionService()
    session = service.create_session(session_id="SES-HARDEN-002", created_at=810)
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id="CHK-HARDEN-002",
        timestamp=811,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=811),
    )
    payload = checkpoint.to_dict()
    payload["safety"]["replay_is_live"] = True
    unsafe = type(checkpoint).from_dict(payload)

    with pytest.raises(ValueError, match="checkpoint is not safe to restore"):
        restore_review_session(unsafe)
