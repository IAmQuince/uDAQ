from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AlarmId, AuthorizationState, GraphMode, OutputId, ProfileId, RequestId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-INV-007', 'verifies_requirements': ['UDQ-REQ-SEC-002'], 'checks_invariants': ['UDQ-INV-STATE-001'], 'worked_example_reference': None, 'expected_proof_output': 'denied actions non-actuating'}
pytestmark = pytest.mark.invariants


def test_denied_actions_do_not_mutate_apply_or_alarm_ack_state():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-INV-AUTH-NONACT'), workspace_state=WorkspaceState(page='review', review_mode=GraphMode.REVIEW)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.REVIEW, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.submit_output_request(
        request_id=RequestId('REQ-INV-AUTH-NONACT'),
        output_id=OutputId('OUT-INV-AUTH-NONACT'),
        requested_value='9',
        actor=ActorId('observer'),
        requested_at=as_event_time(3),
        applied_value='9',
        observed_value='9',
        applied_at=as_event_time(4),
        observed_at=as_event_time(5),
    )
    controller.assert_alarm(alarm_id=AlarmId('ALM-INV-AUTH-NONACT'), timestamp=as_event_time(6))
    controller.acknowledge_alarm(alarm_id=AlarmId('ALM-INV-AUTH-NONACT'), actor=ActorId('observer'), timestamp=as_event_time(7))
    trace = controller.session.command_traces[-1]
    lifecycle = controller.session.alarm_lifecycles[-1]
    assert trace.apply_published is False
    assert [state.value for state in lifecycle.ordered_states] == ['asserted']
