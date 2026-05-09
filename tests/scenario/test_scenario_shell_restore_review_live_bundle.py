from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController
from universaldaq.common import ActorId, AlarmId, AuthorizationState, GraphMode, OutputId, ProfileId, RequestId, TraceId, as_event_time
from universaldaq.historian import summarize_bundle
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-006', 'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-PROF-001', 'UDQ-REQ-HIS-001', 'UDQ-REQ-UI-006'], 'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-002', 'UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'shell review/live evidence bundle'}
pytestmark = pytest.mark.scenario


def test_scenario_shell_restore_review_live_bundle():
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-SCN-001'),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.HISTORY),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.VIEW_ONLY, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    controller.navigate(page='review', timestamp=as_event_time(3))
    controller.set_trace_visibility(trace_id=TraceId('SIG-100'), visible=True, timestamp=as_event_time(4))
    controller.set_overlay(overlay_name='requested-applied-observed', visible=True, timestamp=as_event_time(5))
    controller.submit_output_request(
        request_id=RequestId('REQ-SCN-001'),
        output_id=OutputId('OUT-001'),
        requested_value='1',
        actor=ActorId('operator'),
        authorization_state=AuthorizationState.VIEW_ONLY,
        requested_at=as_event_time(6),
    )
    controller.assert_alarm(alarm_id=AlarmId('ALM-SCN-001'), timestamp=as_event_time(7))
    controller.acknowledge_alarm(alarm_id=AlarmId('ALM-SCN-001'), actor=ActorId('operator'), timestamp=as_event_time(8))
    controller.return_to_live(timestamp=as_event_time(9))
    bundle = controller.build_evidence_bundle(bundle_id='BUNDLE-SCN-001')
    summary = summarize_bundle(bundle)

    assert controller.session.ui_session.graph_session.mode == GraphMode.LIVE
    assert summary.overlay_count == 1
    assert summary.record_count == len(bundle.records)
    assert 'request blocked before apply' in summary.summaries
    assert 'alarm acknowledged' in summary.summaries
    assert 'return to live invoked' in summary.summaries
