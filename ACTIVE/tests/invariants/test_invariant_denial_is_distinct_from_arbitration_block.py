from __future__ import annotations

import pytest

from universaldaq.common import ActorId, AuthorizationState, OutputId, RequestId, as_event_time
from universaldaq.outputs import OutputArbiter
from universaldaq.security import ActorContext, AuthorizationService, GovernedAction, RoleClass

TEST_DECLARATION = {'test_id': 'UDQ-TST-INV-008', 'verifies_requirements': ['UDQ-REQ-SEC-002', 'UDQ-REQ-OUT-002'], 'checks_invariants': ['UDQ-INV-TRANS-001'], 'worked_example_reference': None, 'expected_proof_output': 'auth denial distinct from arbitration block'}
pytestmark = pytest.mark.invariants


def test_authorization_denial_stays_distinct_from_arbitration_block():
    service = AuthorizationService.from_default_policy()
    decision = service.evaluate(
        action=GovernedAction.ISSUE_OUTPUT_COMMAND,
        actor_context=ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER, session_id='SESSION-INV-001'),
        target_kind='output',
        target_id='OUT-INV-001',
    )
    request = OutputArbiter.build_request(
        request_id=RequestId('REQ-INV-001'),
        output_id=OutputId('OUT-INV-001'),
        requested_value='1',
        actor=ActorId('observer'),
        requested_at=as_event_time(1),
    )
    denied = OutputArbiter.issue_trace(
        request=request,
        authorization_decision=decision,
        authorization_state=decision.authorization_state,
        applied_value='1',
        observed_value='1',
        applied_at=as_event_time(2),
        observed_at=as_event_time(3),
    )
    blocked = OutputArbiter.issue_trace(
        request=request,
        authorization_state=AuthorizationState.ALLOWED,
        applied_value=None,
        observed_value=None,
        applied_at=None,
        observed_at=None,
    )
    assert denied.rejection_phase == 'authorization'
    assert blocked.rejection_phase == 'arbitration'
