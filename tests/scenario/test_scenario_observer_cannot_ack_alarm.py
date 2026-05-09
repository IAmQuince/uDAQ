from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AuthorizationState, AlarmLifecycleState, AlarmId, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-011', 'verifies_requirements': ['UDQ-REQ-SEC-002', 'UDQ-REQ-EVT-002'], 'checks_invariants': ['UDQ-INV-TRANS-003'], 'worked_example_reference': None, 'expected_proof_output': 'observer alarm-ack denial'}
pytestmark = pytest.mark.scenario


def test_observer_cannot_acknowledge_alarm_and_lifecycle_state_does_not_advance():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-SCN-AUTH-ACK'), workspace_state=WorkspaceState(page='review', review_mode=GraphMode.REVIEW)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.REVIEW, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.assert_alarm(alarm_id=AlarmId('ALM-SCN-AUTH-ACK'), timestamp=as_event_time(3))
    controller.acknowledge_alarm(alarm_id=AlarmId('ALM-SCN-AUTH-ACK'), actor=ActorId('observer'), timestamp=as_event_time(4))
    lifecycle = controller.session.alarm_lifecycles[-1]
    assert lifecycle.ordered_states == (AlarmLifecycleState.ASSERTED,)
    assert any('denied' in record.summary for record in lifecycle.evidence_records)
