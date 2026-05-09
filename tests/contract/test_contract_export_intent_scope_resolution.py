from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AuthorizationState, ExportArtifactClass, GraphMode, ProfileId, TraceId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-007', 'verifies_requirements': ['UDQ-REQ-EXP-001', 'UDQ-REQ-HIS-002', 'UDQ-REQ-UI-006'], 'checks_invariants': ['UDQ-INV-STATE-003', 'UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'export intent scope resolution'}
pytestmark = pytest.mark.contract


def test_export_intent_scope_resolution_follows_shell_state():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-CON-EXP-001'),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.HISTORY),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.VIEW_ONLY, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.navigate(page='review', timestamp=as_event_time(3))
    controller.set_trace_visibility(trace_id=TraceId('SIG-01'), visible=True, timestamp=as_event_time(4))
    controller.set_overlay(overlay_name='alarms', visible=True, timestamp=as_event_time(5))
    controller.select_history_range(start=as_event_time(10), end=as_event_time(20), timestamp=as_event_time(6))

    intent = controller.build_export_intent(
        export_id='EXPORT-CON-001',
        artifact_class=ExportArtifactClass.REVIEW_ARTIFACT,
        actor=ActorId('reviewer'),
        timestamp=as_event_time(7),
        include_profiles=True,
    )

    assert intent.scope.graph_mode == GraphMode.HISTORY
    assert intent.scope.selected_pages == ('review',)
    assert intent.scope.selected_trace_ids == ('SIG-01',)
    assert intent.scope.overlays == ('alarms',)
    assert intent.scope.selected_range == (as_event_time(10), as_event_time(20))
    assert intent.scope.include_profiles is True
    assert controller.session.ui_session.export_scope_preview is not None
