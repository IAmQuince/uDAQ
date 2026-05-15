from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, TraceId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-007', 'verifies_requirements': ['UDQ-REQ-HIS-002', 'UDQ-REQ-EXP-001', 'UDQ-REQ-EXP-002'], 'checks_invariants': ['UDQ-INV-TRANS-004', 'UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'review export from history range'}
pytestmark = pytest.mark.scenario


def test_review_export_from_history_range_keeps_scope_and_artifacts_clear():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-SCN-EXP-001'),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.HISTORY),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.VIEW_ONLY, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.navigate(page='review', timestamp=as_event_time(3))
    controller.set_trace_visibility(trace_id=TraceId('SIG-SCN-001'), visible=True, timestamp=as_event_time(4))
    controller.set_overlay(overlay_name='commands', visible=True, timestamp=as_event_time(5))
    controller.select_history_range(start=as_event_time(100), end=as_event_time(130), timestamp=as_event_time(6))

    result = controller.export_review_artifact(
        export_id='EXPORT-SCN-001',
        manifest_id='MAN-SCN-001',
        actor=ActorId('reviewer'),
        timestamp=as_event_time(7),
        include_profiles=True,
    )

    assert result.export_intent.scope.selected_range == (as_event_time(100), as_event_time(130))
    assert result.manifest.scope_summary['selected_pages'] == ['review']
    assert any(item.descriptor.relative_path == 'review.md' for item in result.serialized_artifacts)
    assert any(item.descriptor.relative_path == 'profiles.json' for item in result.serialized_artifacts)
