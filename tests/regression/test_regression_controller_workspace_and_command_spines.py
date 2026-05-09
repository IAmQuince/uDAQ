from __future__ import annotations

import pytest

from universaldaq.app import AUTOSAVE_PROFILE_ID, ShellBootstrapper, ShellController
from universaldaq.common import AlarmId, AuthorizationState, GraphMode, ProfileId, RestoreOrigin, TraceId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-REG-011',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-PROF-001', 'UDQ-REQ-EVT-001', 'UDQ-REQ-UI-007'],
    'checks_invariants': ['UDQ-INV-STATE-002', 'UDQ-INV-EVID-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'workspace/profile/command public spines remain stable after controller decomposition',
}
pytestmark = pytest.mark.regression


def test_public_workspace_profile_and_alarm_command_spines_remain_stable():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-REG-SPINE-001'),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.HISTORY),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
    )
    controller = ShellController.from_bootstrapped_shell(boot)

    controller.navigate(page='review', timestamp=as_event_time(3))
    controller.set_trace_visibility(trace_id=TraceId('SIG-CTRL-001'), visible=True, timestamp=as_event_time(4))
    controller.set_overlay(overlay_name='alarms', visible=True, timestamp=as_event_time(5))
    controller.select_history_range(start=as_event_time(10), end=as_event_time(20), timestamp=as_event_time(6))
    controller.save_autosave(timestamp=as_event_time(7))
    controller.return_to_live(timestamp=as_event_time(8))
    controller.restore_profile(profile_id=AUTOSAVE_PROFILE_ID, origin=RestoreOrigin.AUTOSAVE, timestamp=as_event_time(9))
    controller.assert_alarm(alarm_id=AlarmId('ALM-REG-SPINE-001'), timestamp=as_event_time(10))
    controller.acknowledge_alarm(alarm_id=AlarmId('ALM-REG-SPINE-001'), timestamp=as_event_time(11))

    assert controller.session.ui_session.restore_profile_id == AUTOSAVE_PROFILE_ID
    assert controller.session.ui_session.workspace_state.page == 'review'
    assert controller.session.ui_session.selected_range is None
    assert controller.session.ui_session.graph_session.mode == GraphMode.HISTORY
    assert TraceId('SIG-CTRL-001') in controller.session.ui_session.workspace_state.visible_traces
    assert controller.session.ui_session.overlays == ()
    assert controller.session.alarm_lifecycles[-1].ordered_states[-1].value == 'acknowledged'
    assert controller.services.commands.records[-1].intent.command_kind == 'ack_alarm'
    assert len(controller.session.shell_evidence_records) >= 7
