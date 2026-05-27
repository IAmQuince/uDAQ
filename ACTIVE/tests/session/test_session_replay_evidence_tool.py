from __future__ import annotations

import json

import pytest

from tools.diagnostics.dump_session_replay_evidence import main

TEST_DECLARATION = {
    "test_id": "UDQ-TST-SESSION-003",
    "verifies_requirements": ["UDQ-REQ-DIAG-001", "UDQ-REQ-HIS-001"],
    "checks_invariants": ["UDQ-INV-STATE-001", "UDQ-INV-STATE-004"],
    "worked_example_reference": None,
    "expected_proof_output": "session replay evidence diagnostic export is deterministic and non-live",
}
pytestmark = pytest.mark.regression


def test_replay_evidence_tool_writes_non_live_summary(tmp_path) -> None:
    output = tmp_path / "session_replay_evidence.json"

    exit_code = main(["--package-root", ".", "--output", str(output)])
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert payload["schema_version"] == "udq.session.replay.evidence.v1"
    assert payload["authority_scope"] == "review_session_only"
    assert payload["replay_is_live"] is False
    assert payload["safety"]["hardware_mutation_enabled"] is False
    assert payload["safety"]["live_mapping_apply_enabled"] is False
    assert payload["replay_evidence_hash"]
    assert "runtime_snapshot" not in payload
