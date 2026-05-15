from __future__ import annotations

import pytest

from universaldaq.security import AuthorizationService, GovernedAction

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-014', 'verifies_requirements': ['UDQ-REQ-SEC-001'], 'checks_invariants': ['UDQ-INV-STATE-002'], 'worked_example_reference': None, 'expected_proof_output': 'action permission resolution'}
pytestmark = pytest.mark.contract


def test_governed_actions_resolve_to_expected_permission_families():
    service = AuthorizationService.from_default_policy()
    assert service.policy.permission_for_action(GovernedAction.ACK_ALARM).value == 'acknowledge_alarms'
    assert service.policy.permission_for_action(GovernedAction.ISSUE_OUTPUT_COMMAND).value == 'issue_manual_commands'
    assert service.policy.permission_for_action(GovernedAction.EXPORT_REVIEW_ARTIFACT).value == 'export_artifacts'
