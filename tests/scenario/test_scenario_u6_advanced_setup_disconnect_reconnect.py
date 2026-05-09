from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession
from universaldaq_labjack.models import LabJackProbeRow
from universaldaq_labjack.plugin import build_support_pack_registration

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SCN-011',
    'verifies_requirements': ['UDQ-REQ-UI-006', 'UDQ-REQ-ARCH-002'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'u6 advanced setup disconnect and reconnect flow',
}
pytestmark = pytest.mark.scenario


def test_u6_advanced_setup_disconnect_and_reconnect_preserve_contextual_state():
    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(LabJackProbeRow(model='U6', serial_number='470001', transport='usb'),)
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-U6-ADV'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    u6 = next(device for device in controller.discover_devices(timestamp=as_event_time(3)) if device.identity.serial_number == '470001')

    controller.select_detected_device(device_key=u6.device_key, timestamp=as_event_time(4))
    controller.enter_advanced_setup(timestamp=as_event_time(5))
    controller.remember_active_device(timestamp=as_event_time(6))
    controller.mark_active_device_disconnected(timestamp=as_event_time(7))
    assert controller.view_model().device_phase == 'disconnected'
    controller.reconnect_active_device(timestamp=as_event_time(8))
    view_model = controller.view_model()

    assert view_model.device_phase == 'ready_to_configure'
    assert view_model.onboarding_mode == 'advanced_setup'
    assert view_model.known_device_restore_offer == 'restore available from profile PROF-U6-ADV'
