from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, SignalId, VariableId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.signals import VariableDefinition, VariableSourceKind
from universaldaq.ui import AuthoritySurface, GraphModeSession
from universaldaq_arduino.models import ArduinoProbeRow
from universaldaq_arduino.plugin import build_support_pack_registration as build_arduino_pack
from universaldaq_labjack.models import LabJackProbeRow
from universaldaq_labjack.plugin import build_support_pack_registration as build_labjack_pack
from universaldaq_rpi.models import RaspberryPiProbeRow
from universaldaq_rpi.plugin import build_support_pack_registration as build_rpi_pack

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-012',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-SIG-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-005'],
    'worked_example_reference': None,
    'expected_proof_output': 'shared live-monitor slice works across labjack, arduino, and raspberry pi support packs',
}
pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    ('pack_name', 'registration_builder', 'expected_identity_token', 'target_point_id'),
    [
        (
            'labjack',
            lambda: build_labjack_pack(probe_rows=(LabJackProbeRow(model='U6', serial_number='470099', transport='usb'),)),
            '470099',
            'analog_in_0',
        ),
        (
            'arduino',
            lambda: build_arduino_pack(probe_rows=(ArduinoProbeRow(board='Uno', serial_number='ARD-200', port='COM9'),)),
            'ARD-200',
            'analog_in_0',
        ),
        (
            'rpi',
            lambda: build_rpi_pack(probe_rows=(RaspberryPiProbeRow(model='5', host_id='rpi-lab-003', enable_gpio=True),)),
            'rpi-lab-003',
            'host_cpu_temp_c',
        ),
    ],
)
def test_shared_live_slice_across_optional_support_packs(pack_name, registration_builder, expected_identity_token, target_point_id):
    services = build_default_service_registry()
    services.adapters.install_support_pack(registration_builder())
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId(f'PROF-{pack_name.upper()}-LIVE'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId(f'{pack_name}-operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)

    device = next(item for item in controller.discover_devices(timestamp=as_event_time(3)) if item.identity.serial_number == expected_identity_token)
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))

    point_key = next(
        point_key
        for point_key, definition in services.bindings.point_definitions.items()
        if definition.device_identity_key == device.identity.stable_key and definition.point_ref.point_id == target_point_id
    )
    controller.bind_logical_signal_to_point(
        logical_signal_id=SignalId(f'{pack_name}_primary'),
        point_key=point_key,
        display_name=f'{pack_name.title()} Primary',
        timestamp=as_event_time(5),
    )
    controller.register_variable_definition(
        definition=VariableDefinition(
            variable_id=VariableId(f'{pack_name}_primary_copy'),
            display_name=f'{pack_name.title()} Primary Copy',
            source_kind=VariableSourceKind.SIGNAL,
            signal_dependencies=(SignalId(f'{pack_name}_primary'),),
        ),
        timestamp=as_event_time(6),
    )

    controller.begin_quick_start(timestamp=as_event_time(7))
    view_model = controller.view_model()

    assert view_model.device_phase == 'live'
    assert view_model.lifecycle_summary is not None
    assert view_model.lifecycle_summary.published_signal_count == 1
    assert view_model.binding_review_summary is not None
    assert view_model.binding_review_summary.total_signal_binding_count == 1
    assert view_model.variable_health_summary is not None
    assert view_model.variable_health_summary.healthy_count == 1
