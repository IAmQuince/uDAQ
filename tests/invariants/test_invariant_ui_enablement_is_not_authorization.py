from __future__ import annotations

import pytest

from universaldaq.common import ActorId
from universaldaq.security import ActorContext, AuthorizationService, GovernedAction, RoleClass
from universaldaq.ui import AuthoritySurface
from universaldaq.common import AuthorizationState

TEST_DECLARATION = {'test_id': 'UDQ-TST-INV-006', 'verifies_requirements': ['UDQ-REQ-SEC-001'], 'checks_invariants': ['UDQ-INV-STATE-002'], 'worked_example_reference': None, 'expected_proof_output': 'ui enablement distinct from authorization'}
pytestmark = pytest.mark.invariants


def test_ui_enablement_does_not_imply_backend_authorization():
    surface = AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True)
    service = AuthorizationService.from_default_policy()
    decision = service.evaluate(
        action=GovernedAction.ISSUE_OUTPUT_COMMAND,
        actor_context=ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER),
        target_kind='output',
        target_id='OUT-INV-001',
    )
    assert surface.ui_enabled is True
    assert decision.allowed is False
