from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AuthorizationState, AlarmLifecycleState, AlarmId, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-012', 'verifies_requirements': ['UDQ-REQ-SEC-002', 'UDQ-REQ-EVT-002', 'UDQ-REQ-EXP-002'], 'checks_invariants': ['UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'operator allowed ack and export'}
pytestmark = pytest.mark.scenario


def test_operator_can_acknowledge_alarm_and_export_evidence_bundle():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-SCN-AUTH-ALLOW'), workspace_state=WorkspaceState(page='review', review_mode=GraphMode.HISTORY)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.assert_alarm(alarm_id=AlarmId('ALM-SCN-AUTH-ALLOW'), timestamp=as_event_time(3))
    controller.acknowledge_alarm(alarm_id=AlarmId('ALM-SCN-AUTH-ALLOW'), actor=ActorId('operator'), timestamp=as_event_time(4))
    export_result = controller.export_evidence_bundle(
        export_id='EXP-SCN-AUTH-ALLOW',
        bundle_id='BUNDLE-SCN-AUTH-ALLOW',
        manifest_id='MAN-SCN-AUTH-ALLOW',
        actor=ActorId('operator'),
        timestamp=as_event_time(5),
    )
    lifecycle = controller.session.alarm_lifecycles[-1]
    assert lifecycle.ordered_states[-1] == AlarmLifecycleState.ACKNOWLEDGED
    assert export_result.authorization_decision is not None and export_result.authorization_decision.allowed is True
    assert export_result.manifest.manifest_id == 'MAN-SCN-AUTH-ALLOW'
