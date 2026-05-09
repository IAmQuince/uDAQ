from __future__ import annotations

import json

import pytest

from tests.conftest import DATA_ROOT, PACKAGE_ROOT, REGISTRY_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-008', 'verifies_requirements': ['UDQ-REQ-GOV-002', 'UDQ-REQ-IMPL-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'schema-convention report'}
pytestmark = pytest.mark.meta


def test_schema_policy_and_structured_companion_fields_exist():
    policy = PACKAGE_ROOT / 'docs/active/UDQ-SCHEMA-POLICY-001__Governance_Schema_Conventions__r0__WIP.md'
    assert policy.exists()

    requirement_pack = json.loads((DATA_ROOT / 'first_slice_requirement_pack.json').read_text(encoding='utf-8'))
    sample_req = requirement_pack['requirements'][0]
    assert isinstance(sample_req['primary_source_ids'], list)
    assert isinstance(sample_req['downstream_spec_ids'], list)
    assert isinstance(sample_req['intended_module_areas'], list)

    decision_log = json.loads((REGISTRY_ROOT / 'universalDAQ_decision_log_r1.json').read_text(encoding='utf-8'))
    sample_decision = decision_log['rows'][0]
    assert isinstance(sample_decision['affected_requirement_ids'], list)
