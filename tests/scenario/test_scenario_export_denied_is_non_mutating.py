from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-013', 'verifies_requirements': ['UDQ-REQ-SEC-002', 'UDQ-REQ-EXP-002'], 'checks_invariants': ['UDQ-INV-STATE-001'], 'worked_example_reference': None, 'expected_proof_output': 'denied export non-mutation'}
pytestmark = pytest.mark.scenario


def test_denied_export_does_not_create_successful_manifest_or_bundle_state():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-SCN-AUTH-EXP'), workspace_state=WorkspaceState(page='review', review_mode=GraphMode.HISTORY)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    result = controller.export_evidence_bundle(
        export_id='EXP-SCN-AUTH-DENY',
        bundle_id='BUNDLE-SCN-AUTH-DENY',
        manifest_id='MAN-SCN-AUTH-DENY',
        actor=ActorId('observer'),
        timestamp=as_event_time(3),
    )
    assert result.authorization_decision is not None and result.authorization_decision.allowed is False
    assert result.serialized_artifacts == ()
    assert controller.session.last_manifest_id is None
    assert controller.session.last_export_summary is not None and 'denied' in controller.session.last_export_summary
