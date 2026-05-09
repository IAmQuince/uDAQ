from __future__ import annotations

import json

import pytest

from tests.conftest import DATA_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-SMK-003', 'verifies_requirements': ['UDQ-REQ-IMPL-001', 'UDQ-REQ-GOV-003'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'snapshot-load smoke output'}
pytestmark = pytest.mark.smoke


def test_first_slice_snapshots_load():
    files = [
        "first_slice_requirement_pack.json",
        "first_slice_execution_contract.json",
        "first_slice_invariant_registry.json",
        "first_slice_worked_examples.json",
    ]
    for name in files:
        data = json.loads((DATA_ROOT / name).read_text(encoding="utf-8"))
        assert data
