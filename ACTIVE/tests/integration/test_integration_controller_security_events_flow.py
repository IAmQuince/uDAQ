from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AlarmId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-INT-007', 'verifies_requirements': ['UDQ-REQ-SEC-002', 'UDQ-REQ-EVT-002'], 'checks_invariants': ['UDQ-INV-TRANS-003'], 'worked_example_reference': None, 'expected_proof_output': 'controller security events flow'}
pytestmark = pytest.mark.integration


def test_controller_security_events_flow_records_denied_ack_without_transition_mutation():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-INT-AUTH-EVT'), workspace_state=WorkspaceState(page='review', review_mode=GraphMode.REVIEW)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.REVIEW, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.assert_alarm(alarm_id=AlarmId('ALM-INT-AUTH-EVT'), timestamp=as_event_time(3))
    controller.acknowledge_alarm(alarm_id=AlarmId('ALM-INT-AUTH-EVT'), actor=ActorId('observer'), timestamp=as_event_time(4))
    lifecycle = controller.session.alarm_lifecycles[-1]
    assert [state.value for state in lifecycle.ordered_states] == ['asserted']
    assert any('authorization policy' in record.summary for record in lifecycle.evidence_records)
