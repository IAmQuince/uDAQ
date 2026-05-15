from __future__ import annotations

import pytest

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-004', 'verifies_requirements': ['UDQ-REQ-AUD-003', 'UDQ-REQ-GOV-003'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'readiness consistency report'}
pytestmark = pytest.mark.meta


def test_first_slice_snapshot_matches_execution_contract(first_slice_requirement_pack, execution_contract):
    pack_ids = {row["requirement_id"] for row in first_slice_requirement_pack["requirements"]}
    contract_ids = {row["requirement_id"] for row in execution_contract["entries"] if row["entry_gate_status"] == "READY"}
    assert pack_ids.issubset(contract_ids)
    assert pack_ids
