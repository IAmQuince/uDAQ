from __future__ import annotations

import json
from pathlib import Path

import pytest

from universaldaq.testing import run_session_replay_evidence_export

TEST_DECLARATION = {
    "test_id": "UDQ-TST-SESSION-004",
    "verifies_requirements": ["UDQ-REQ-DIAG-001", "UDQ-REQ-HIS-001"],
    "checks_invariants": ["UDQ-INV-STATE-001", "UDQ-INV-STATE-004"],
    "worked_example_reference": None,
    "expected_proof_output": "Testing menu session replay evidence helper exports review-only proof",
}
pytestmark = pytest.mark.regression


def test_testing_helper_exports_review_only_replay_evidence(tmp_path) -> None:
    result = run_session_replay_evidence_export(package_root=tmp_path)
    payload = json.loads(Path(result.report_path).read_text(encoding="utf-8"))

    assert result.passed is True
    assert payload["checks"]["authority_scope_review_only"] is True
    assert payload["checks"]["replay_is_not_live"] is True
    assert payload["checks"]["summary_only_payload"] is True
    assert payload["evidence"]["authority_scope"] == "review_session_only"
    assert payload["evidence"]["replay_is_live"] is False
