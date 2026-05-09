from __future__ import annotations

from dataclasses import replace

import pytest

from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, SignalId, VariableId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.signals import VariableDefinition, VariableSourceKind
from universaldaq.ui import AuthoritySurface, GraphModeSession
from universaldaq_labjack.models import LabJackProbeRow
from universaldaq_labjack.plugin import build_support_pack_registration


def _bootstrap_controller(*, profile_id: str):
    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(LabJackProbeRow(model='U6', serial_number='470001', transport='usb'),)
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId(profile_id), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    device = next(item for item in controller.discover_devices(timestamp=as_event_time(3)) if item.identity.serial_number == '470001')
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))
    return controller, services, device


def _point_key_for(device, services, point_id: str) -> str:
    return next(
        point_key
        for point_key, definition in services.bindings.point_definitions.items()
        if definition.device_identity_key == device.identity.stable_key and definition.point_ref.point_id == point_id
    )


TEST_DECLARATION = {
    'test_id': 'UDQ-TST-REG-004',
    'verifies_requirements': ['UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'reconnect reprojection does not duplicate device point definitions',
}
pytestmark = pytest.mark.regression


def test_repeated_reconnect_does_not_duplicate_projected_points():
    controller, services, device = _bootstrap_controller(profile_id='PROF-REG-DEDUPE')
    controller.bind_logical_signal_to_point(logical_signal_id=SignalId('stack_voltage'), point_key=_point_key_for(device, services, 'analog_in_0'), timestamp=as_event_time(5))
    controller.begin_quick_start(timestamp=as_event_time(6))
    initial_keys = set(services.bindings.point_definitions.keys())

    for offset in range(3):
        controller.mark_active_device_disconnected(timestamp=as_event_time(7 + offset * 2))
        controller.reconnect_active_device(timestamp=as_event_time(8 + offset * 2))

    assert set(services.bindings.point_definitions.keys()) == initial_keys
