from __future__ import annotations

import pytest

from universaldaq.common import ActorId
from universaldaq.security import ActorContext, AuthorizationService, GovernedAction, RoleClass

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-015', 'verifies_requirements': ['UDQ-REQ-SEC-001', 'UDQ-REQ-SEC-002'], 'checks_invariants': ['UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'authorization denial reasons'}
pytestmark = pytest.mark.contract


def test_denied_decisions_include_stable_reason_code_and_text():
    service = AuthorizationService.from_default_policy()
    decision = service.evaluate(
        action=GovernedAction.ISSUE_OUTPUT_COMMAND,
        actor_context=ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER, session_id='SESSION-1'),
        target_kind='output',
        target_id='OUT-001',
    )
    assert decision.allowed is False
    assert decision.reason_code.value in {'insufficient_role', 'action_not_permitted'}
    assert decision.reason_text
