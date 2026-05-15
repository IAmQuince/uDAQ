from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AuthorizationState, GraphMode, OutputId, ProfileId, RequestId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-INT-006', 'verifies_requirements': ['UDQ-REQ-SEC-002', 'UDQ-REQ-OUT-002'], 'checks_invariants': ['UDQ-INV-STATE-001'], 'worked_example_reference': None, 'expected_proof_output': 'controller security outputs flow'}
pytestmark = pytest.mark.integration


def test_controller_security_outputs_flow_preserves_denial_and_trace_reasoning():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-INT-AUTH-OUT'), workspace_state=WorkspaceState(page='review', review_mode=GraphMode.REVIEW)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.REVIEW, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.submit_output_request(
        request_id=RequestId('REQ-INT-AUTH-OUT'),
        output_id=OutputId('OUT-INT-AUTH-OUT'),
        requested_value='1',
        actor=ActorId('observer'),
        requested_at=as_event_time(3),
        applied_value='1',
        observed_value='1',
        applied_at=as_event_time(4),
        observed_at=as_event_time(5),
    )
    trace = controller.session.command_traces[-1]
    assert trace.decision.value == 'rejected'
    assert trace.rejection_phase == 'authorization'
    assert trace.authorization_decision is not None
