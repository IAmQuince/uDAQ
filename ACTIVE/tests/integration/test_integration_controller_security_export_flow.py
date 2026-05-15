from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-INT-008', 'verifies_requirements': ['UDQ-REQ-SEC-002', 'UDQ-REQ-EXP-002'], 'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'controller security export flow'}
pytestmark = pytest.mark.integration


def test_controller_security_export_flow_denies_bundle_for_observer_but_allows_review_export():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-INT-AUTH-EXP'), workspace_state=WorkspaceState(page='review', review_mode=GraphMode.HISTORY)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    denied = controller.export_evidence_bundle(
        export_id='EXP-INT-AUTH-DENY',
        bundle_id='BUNDLE-INT-AUTH-DENY',
        manifest_id='MAN-INT-AUTH-DENY',
        actor=ActorId('observer'),
        timestamp=as_event_time(3),
    )
    allowed = controller.export_review_artifact(
        export_id='EXP-INT-AUTH-ALLOW',
        manifest_id='MAN-INT-AUTH-ALLOW',
        actor=ActorId('observer'),
        timestamp=as_event_time(4),
    )
    assert denied.authorization_decision is not None and denied.authorization_decision.allowed is False
    assert allowed.authorization_decision is not None and allowed.authorization_decision.allowed is True
    assert allowed.manifest.manifest_id == 'MAN-INT-AUTH-ALLOW'
