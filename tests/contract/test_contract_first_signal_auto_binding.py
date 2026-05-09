from __future__ import annotations

import pytest

from universaldaq.adapters import DeterministicWaveformAdapter
from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-051',
    'verifies_requirements': ['UDQ-REQ-UI-006', 'UDQ-REQ-DEV-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'quick-start auto-binds one first signal and surfaces a bounded trace preview',
}
pytestmark = pytest.mark.contract


def test_quick_start_auto_binds_first_signal_when_device_has_no_existing_bindings():
    services = build_default_service_registry(load_support_packs=False)
    services.adapters.register(DeterministicWaveformAdapter(adapter_id='DEMO-FIRST-SIGNAL-001'))
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-FIRST-SIGNAL-CONTRACT'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
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

    view = controller.view_model()
    assert view.device_phase == 'live'
    assert view.lifecycle_summary is not None
    assert view.lifecycle_summary.published_signal_count == 1
    assert view.first_signal_summary is not None
    assert view.first_signal_summary.auto_bound is True
    assert view.first_signal_summary.point_class == 'analog'
    assert view.first_signal_summary.trace_point_count >= 2
    assert view.first_signal_summary.latest_numeric_value is not None
