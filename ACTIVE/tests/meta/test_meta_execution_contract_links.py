from __future__ import annotations

import pytest

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-003', 'verifies_requirements': ['UDQ-REQ-AUD-002', 'UDQ-REQ-GOV-002'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'execution-contract link audit'}
pytestmark = pytest.mark.meta


def test_execution_contract_only_references_known_requirements(execution_contract, requirement_registry):
    valid = {row["requirement_id"] for row in requirement_registry["requirements"]}
    missing = [row["requirement_id"] for row in execution_contract["entries"] if row["requirement_id"] not in valid]
    assert not missing
