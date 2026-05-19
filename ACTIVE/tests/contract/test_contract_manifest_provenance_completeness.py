from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-008', 'verifies_requirements': ['UDQ-REQ-EXP-001', 'UDQ-REQ-EXP-002'], 'checks_invariants': ['UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'manifest provenance completeness'}
pytestmark = pytest.mark.contract


def test_manifest_provenance_is_complete_for_review_export():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-CON-MAN-001'),
            workspace_state=WorkspaceState(page='review', review_mode=GraphMode.REVIEW),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.REVIEW, as_event_time(1)),
        timestamp=as_event_time(2),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    result = controller.export_review_artifact(
        export_id='EXPORT-CON-MAN-001',
        manifest_id='MAN-CON-MAN-001',
        actor=ActorId('auditor'),
        timestamp=as_event_time(3),
        include_profiles=True,
    )

    manifest = result.manifest
    assert manifest.export_id == 'EXPORT-CON-MAN-001'
    assert str(manifest.created_by_actor) == 'auditor'
    assert manifest.session_id.startswith('SESSION-PROF-CON-MAN-001-')
    assert manifest.authority_state == AuthorizationState.ALLOWED
    assert manifest.scope_summary['selected_pages'] == ['review']
    assert any(item.relative_path == 'manifest.json' for item in manifest.artifacts)
