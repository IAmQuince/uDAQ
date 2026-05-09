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
    'test_id': 'UDQ-TST-SCN-010',
    'verifies_requirements': ['UDQ-REQ-UI-006', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'u6 quick-start onboarding flow',
}
pytestmark = pytest.mark.scenario


def test_u6_quick_start_flow_sets_active_device_live_and_surfaces_workbenches():
    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(LabJackProbeRow(model='U6', serial_number='470001', transport='usb'),)
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-U6-QUICK'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)

    devices = controller.discover_devices(timestamp=as_event_time(3))
    u6 = next(device for device in devices if device.identity.serial_number == '470001')
    controller.select_detected_device(device_key=u6.device_key, timestamp=as_event_time(4))
    controller.begin_quick_start(timestamp=as_event_time(5))
    view_model = controller.view_model()

    assert view_model.active_device is not None
    assert view_model.active_device.display_name.startswith('LabJack U6')
    assert view_model.device_phase == 'live'
    assert 'LabJack U6 Stream Setup' in view_model.available_workbenches
