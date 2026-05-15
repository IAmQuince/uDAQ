from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, SignalId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession
from universaldaq_labjack.models import LabJackProbeRow
from universaldaq_labjack.plugin import build_support_pack_registration

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-011',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'lifecycle review bundle exposes shell-visible review counts and workbench state',
}
pytestmark = pytest.mark.integration


def test_lifecycle_review_bundle_contains_summary_counts_and_workbench_names():
    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(LabJackProbeRow(model='U6', serial_number='470001', transport='usb'),)
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-U6-BUNDLE'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    device = next(item for item in controller.discover_devices(timestamp=as_event_time(3)) if item.identity.serial_number == '470001')
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))

    point_key = next(
        point_key
        for point_key, definition in services.bindings.point_definitions.items()
        if definition.device_identity_key == device.identity.stable_key and definition.point_ref.point_id == 'analog_in_0'
    )
    controller.bind_logical_signal_to_point(
        logical_signal_id=SignalId('stack_voltage'),
        point_key=point_key,
        display_name='Stack Voltage',
        timestamp=as_event_time(5),
    )
    controller.begin_quick_start(timestamp=as_event_time(6))

    bundle = controller.lifecycle_review_bundle()

    assert bundle['active_device_key'] == device.device_key
    assert bundle['lifecycle_summary']['projected_point_count'] >= 1
    assert bundle['binding_review_summary']['total_signal_binding_count'] == 1
    assert bundle['workbench_review_state']['total_workbench_count'] >= 1
    assert 'LabJack U6 Stream Setup' in bundle['workbench_review_state']['available_workbench_names']
