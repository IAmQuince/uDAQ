from __future__ import annotations

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AuthorizationState, GraphMode, OutputId, ProfileId, RequestId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-INV-ADAPT-001', 'verifies_requirements': ['UDQ-REQ-MOD-002', 'UDQ-REQ-SEC-001'], 'checks_invariants': ['UDQ-INV-STATE-004', 'UDQ-INV-TRANS-001'], 'worked_example_reference': None, 'expected_proof_output': 'authorization denial stays upstream of adapter handoff'}


def test_authorization_denial_never_reaches_adapter_handoff():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-OBS'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('observer'), role_class=RoleClass.OBSERVER),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    before = len(controller.services.adapters.command_results)

    controller.submit_output_request_via_adapter(
        request_id=RequestId('REQ-OBS-001'),
        output_id=OutputId('OUT-ADAPT-001'),
        adapter_id='SIM-WRITE-001',
        point_id='OUT-ADAPT-001',
        requested_value='1',
        actor=ActorId('observer'),
        requested_at=as_event_time(3),
        applied_value='1',
        observed_value='1',
        applied_at=as_event_time(4),
        observed_at=as_event_time(5),
    )
    trace = controller.session.command_traces[-1]

    assert trace.authorization_denied is True
    assert trace.adapter_result is None
    assert len(controller.services.adapters.command_results) == before
