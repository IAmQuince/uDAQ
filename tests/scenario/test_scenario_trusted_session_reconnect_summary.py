from __future__ import annotations

import pytest

from universaldaq.adapters import DeterministicWaveformAdapter
from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SCN-012',
    'verifies_requirements': ['UDQ-REQ-UI-006', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'trusted-session summary remains truthful across manual disconnect and reconnect on the first-signal path',
}
pytestmark = pytest.mark.scenario


def test_trusted_session_summary_recovers_after_manual_disconnect_and_reconnect():
    services = build_default_service_registry(load_support_packs=False)
    services.adapters.register(DeterministicWaveformAdapter(adapter_id='DEMO-FIRST-SIGNAL-001'))
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-TRUSTED-SESSION-RECOVER'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
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
    controller.mark_active_device_disconnected(timestamp=as_event_time(8))

    disconnected = controller.view_model().trusted_session_summary
    assert disconnected is not None
    assert disconnected.lifecycle_state == 'disconnected'
    assert disconnected.graph_status_label == 'disconnected'
    assert disconnected.ready_for_operator is False

    controller.reconnect_active_device(timestamp=as_event_time(9))
    controller.poll_adapters(timestamp=as_event_time(10))
    controller.poll_adapters(timestamp=as_event_time(11))

    recovered = controller.view_model().trusted_session_summary
    assert recovered is not None
    assert recovered.lifecycle_state == 'live'
    assert recovered.graph_status_label == 'live'
    assert recovered.graph_visible is True
    assert recovered.live_numeric_visible is True
    assert recovered.ready_for_operator is True
    assert recovered.reconnect_count >= 1
    assert recovered.last_event_summary is not None and 'adapter poll completed' in recovered.last_event_summary
