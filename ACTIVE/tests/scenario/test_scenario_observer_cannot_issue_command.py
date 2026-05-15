from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AuthorizationState, GraphMode, OutputId, ProfileId, RequestId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-010', 'verifies_requirements': ['UDQ-REQ-SEC-002', 'UDQ-REQ-OUT-002'], 'checks_invariants': ['UDQ-INV-STATE-001'], 'worked_example_reference': None, 'expected_proof_output': 'observer command denial'}
pytestmark = pytest.mark.scenario


def test_observer_cannot_issue_output_command_and_trace_is_non_actuating():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-SCN-AUTH-CMD'), workspace_state=WorkspaceState(page='review', review_mode=GraphMode.REVIEW)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.REVIEW, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.submit_output_request(
        request_id=RequestId('REQ-SCN-AUTH-CMD'),
        output_id=OutputId('OUT-SCN-AUTH-CMD'),
        requested_value='7',
        actor=ActorId('observer'),
        requested_at=as_event_time(3),
        applied_value='7',
        observed_value='7',
        applied_at=as_event_time(4),
        observed_at=as_event_time(5),
    )
    trace = controller.session.command_traces[-1]
    assert trace.authorization_denied is True
    assert trace.apply_published is False
    assert trace.authorization_decision is not None and trace.authorization_decision.allowed is False
