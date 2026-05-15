from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import AuthorizationState, GraphMode, ProfileId, TraceId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-006', 'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-UI-003', 'UDQ-REQ-UI-004', 'UDQ-REQ-UI-006'], 'checks_invariants': ['UDQ-INV-STATE-003', 'UDQ-INV-TRANS-004', 'UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'shell controller navigation and return-to-live trace'}
pytestmark = pytest.mark.contract


def test_shell_controller_navigation_and_return_to_live_semantics():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-CON-CTRL-001'),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.HISTORY),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.VIEW_ONLY, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.navigate(page='review', timestamp=as_event_time(3))
    controller.set_trace_visibility(trace_id=TraceId('SIG-01'), visible=True, timestamp=as_event_time(4))
    controller.set_overlay(overlay_name='commands', visible=True, timestamp=as_event_time(5))
    controller.return_to_live(timestamp=as_event_time(6))

    vm = controller.view_model()
    assert controller.session.ui_session.workspace_state.page == 'review'
    assert controller.session.ui_session.graph_session.mode == GraphMode.LIVE
    assert controller.session.ui_session.selected_range is None
    assert controller.session.ui_session.workspace_state.visible_traces == (TraceId('SIG-01'),)
    assert vm.graph_panel.overlay_count == 1
    assert vm.graph_panel.return_to_live_available is False
    assert len(controller.session.shell_evidence_records) == 4
