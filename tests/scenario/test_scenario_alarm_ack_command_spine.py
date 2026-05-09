from __future__ import annotations

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AlarmId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SCN-CMD-001',
    'verifies_requirements': ['UDQ-REQ-EVT-002', 'UDQ-REQ-OUT-002'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-EVID-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'alarm acknowledgment enters through the canonical command admission spine',
}


def test_alarm_acknowledgment_is_recorded_as_admitted_command():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-CMD-ACK'), workspace_state=WorkspaceState(page='review', review_mode=GraphMode.REVIEW)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.REVIEW, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.assert_alarm(alarm_id=AlarmId('ALM-CMD-ACK'), timestamp=as_event_time(3))

    controller.acknowledge_alarm(alarm_id=AlarmId('ALM-CMD-ACK'), actor=ActorId('operator'), timestamp=as_event_time(4))
    bundle = controller.lifecycle_review_bundle()
    row = bundle['recent_command_rows'][-1]

    assert row['command_kind'] == 'ack_alarm'
    assert row['admission_status'] == 'admitted'
    assert row['dispatch_status'] == 'completed'
    assert row['target_kind'] == 'alarm'
    assert bundle['command_summary']['admitted_count'] == 1
    assert bundle['event_alarm_summary']['unacknowledged_alarm_count'] == 0
