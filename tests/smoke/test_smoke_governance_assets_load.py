from __future__ import annotations

import json

import pytest

from tests.conftest import REGISTRY_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-SMK-002', 'verifies_requirements': ['UDQ-REQ-GOV-001', 'UDQ-REQ-GOV-002'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'registry-load smoke output'}
pytestmark = pytest.mark.smoke


def test_active_governance_assets_load():
    files = [
        "universalDAQ_governance_model_r2.json",
        "universalDAQ_execution_contract_r2.json",
        "universalDAQ_invariant_registry_r2.json",
        "universalDAQ_implementation_coverage_matrix_r2.json",
        "universalDAQ_requirement_registry_r9.json",
    ]
    for name in files:
        data = json.loads((REGISTRY_ROOT / name).read_text(encoding="utf-8"))
        assert data
