from __future__ import annotations

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AuthorizationState, GraphMode, OutputId, ProfileId, RequestId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-INT-ADAPT-001', 'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-DIAG-001', 'UDQ-REQ-MOD-002'], 'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-TIME-001'], 'worked_example_reference': None, 'expected_proof_output': 'controller-to-adapter integration flow'}


def test_controller_can_poll_adapters_and_attach_handoff_result_to_trace():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-INT-ADAPT'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR),
    )
    controller = ShellController.from_bootstrapped_shell(boot)

    poll_results = controller.poll_adapters(timestamp=as_event_time(3))
    action = controller.submit_output_request_via_adapter(
        request_id=RequestId('REQ-INT-ADAPT-001'),
        output_id=OutputId('OUT-ADAPT-001'),
        adapter_id='SIM-WRITE-001',
        point_id='OUT-ADAPT-001',
        requested_value='1',
        actor=ActorId('operator'),
        requested_at=as_event_time(4),
        applied_value='1',
        observed_value='1',
        applied_at=as_event_time(5),
        observed_at=as_event_time(6),
    )

    assert poll_results
    assert action.session.command_traces[-1].adapter_result is not None
    assert any('adapter' in record.summary for record in action.session.shell_evidence_records)
