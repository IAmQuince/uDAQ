from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AlarmId, AuthorizationState, GraphMode, OutputId, ProfileId, RequestId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-009', 'verifies_requirements': ['UDQ-REQ-EXP-001', 'UDQ-REQ-ARCH-001'], 'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'review artifact export is non-mutating'}
pytestmark = pytest.mark.contract


def test_review_artifact_export_is_non_mutating_for_session_collections():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-CON-NONMUT-001'),
            workspace_state=WorkspaceState(page='review', review_mode=GraphMode.HISTORY),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.submit_output_request(
        request_id=RequestId('REQ-NONMUT-001'),
        output_id=OutputId('OUT-NONMUT-001'),
        requested_value='7',
        actor=ActorId('operator'),
        authorization_state=AuthorizationState.ALLOWED,
        requested_at=as_event_time(3),
        applied_value='7',
        observed_value='7',
        applied_at=as_event_time(4),
        observed_at=as_event_time(5),
    )
    controller.assert_alarm(alarm_id=AlarmId('ALM-NONMUT-001'), timestamp=as_event_time(6))
    command_trace_count = len(controller.session.command_traces)
    alarm_count = len(controller.session.alarm_lifecycles)
    shell_evidence_count = len(controller.session.shell_evidence_records)

    controller.export_review_artifact(
        export_id='EXPORT-NONMUT-001',
        manifest_id='MAN-NONMUT-001',
        actor=ActorId('reviewer'),
        timestamp=as_event_time(7),
    )

    assert len(controller.session.command_traces) == command_trace_count
    assert len(controller.session.alarm_lifecycles) == alarm_count
    assert len(controller.session.shell_evidence_records) == shell_evidence_count + 1
