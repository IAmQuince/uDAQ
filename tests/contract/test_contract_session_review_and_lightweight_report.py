from __future__ import annotations

import pytest

from universaldaq.adapters import DeterministicWaveformAdapter
from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-057',
    'verifies_requirements': ['UDQ-REQ-PROF-001', 'UDQ-REQ-DIAG-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-EVID-004', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'recent-session review rows and lightweight session report preserve historical posture, notes, and persisted signal context',
}
pytestmark = pytest.mark.contract


def _controller() -> tuple[ShellController, str]:
    services = build_default_service_registry(load_support_packs=False)
    services.adapters.register(DeterministicWaveformAdapter(adapter_id='DEMO-FIRST-SIGNAL-001'))
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-SESSION-REVIEW-CONTRACT'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    device = next(item for item in controller.discover_devices(timestamp=as_event_time(3)) if item.identity.serial_number == 'DEMO-001')
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))
    controller.begin_quick_start(timestamp=as_event_time(5))
    controller.poll_adapters(timestamp=as_event_time(6))
    controller.poll_adapters(timestamp=as_event_time(7))
    controller.add_operator_note(note_text='captured for session review', timestamp=as_event_time(8), category='operator_annotation')
    state = controller.save_bench_state(timestamp=as_event_time(9))
    return controller, state.historical_summary.summary_id


def test_contract_recent_session_review_and_report_are_historical_and_structured():
    controller, summary_id = _controller()
    recent = controller.recent_session_review(limit=5)
    assert recent
    latest = recent[0]
    assert latest.summary_id == summary_id
    assert latest.historical_label.startswith('historical review only')
    assert latest.note_count == 1
    assert latest.completeness_label == 'complete'
    assert latest.flight_record_ready is True

    detail = controller.session_review_detail(summary_id=summary_id)
    assert detail.signal_provenance_label
    assert detail.trace_preview
    assert detail.operator_notes[0].text == 'captured for session review'
    assert detail.historical_label.startswith('historical review only')

    report = controller.generate_lightweight_session_report(summary_id=summary_id, timestamp=as_event_time(10))
    assert report.summary_id == summary_id
    assert 'Historical session review only' in report.markdown
    assert 'captured for session review' in report.markdown
    assert report.payload['signal']['provenance_label'] == detail.signal_provenance_label
    assert report.payload['session']['completeness_label'] == 'complete'
