from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AuthorizationState, GraphMode, OutputId, ProfileId, RequestId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-INV-009', 'verifies_requirements': ['UDQ-REQ-SEC-002'], 'checks_invariants': ['UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'authorization evidence attribution'}
pytestmark = pytest.mark.invariants


def test_authorization_evidence_preserves_actor_session_and_origin():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-INV-AUTH-EVID'), workspace_state=WorkspaceState(page='review', review_mode=GraphMode.REVIEW)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.REVIEW, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER, origin='local-shell'),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.submit_output_request(
        request_id=RequestId('REQ-INV-AUTH-EVID'),
        output_id=OutputId('OUT-INV-AUTH-EVID'),
        requested_value='1',
        actor=ActorId('observer'),
        requested_at=as_event_time(3),
        applied_value='1',
        observed_value='1',
        applied_at=as_event_time(4),
        observed_at=as_event_time(5),
    )
    decision = controller.session.last_authorization_decision
    assert decision is not None
    assert str(decision.actor_id) == 'observer'
    assert decision.session_id == controller.session.session_id
    assert decision.origin == 'local-shell'
