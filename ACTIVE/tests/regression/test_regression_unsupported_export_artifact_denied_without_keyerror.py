from __future__ import annotations

import pytest

from universaldaq.common import ActorId
from universaldaq.security import ActorContext, AuthorizationReasonCode, AuthorizationService, RoleClass

TEST_DECLARATION = {'test_id': 'UDQ-TST-REG-003', 'verifies_requirements': ['UDQ-REQ-SEC-002', 'UDQ-REQ-EXP-002'], 'checks_invariants': ['UDQ-INV-STATE-001'], 'worked_example_reference': None, 'expected_proof_output': 'unsupported export artifact safe denial regression'}
pytestmark = pytest.mark.regression


def test_unsupported_export_artifact_is_denied_without_keyerror():
    service = AuthorizationService.from_default_policy()
    actor = ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER, session_id='SESSION-REG-003')

    decision = service.can_export_artifact(actor_context=actor, artifact_class='unexpected_export_class')

    assert decision.allowed is False
    assert decision.reason_code == AuthorizationReasonCode.NO_POLICY
    assert decision.target_kind == 'export_artifact'
    assert decision.target_id == 'unexpected_export_class'
    assert 'unsupported export artifact class' in decision.reason_text
