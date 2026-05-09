from __future__ import annotations

import pytest

from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, SignalId, VariableId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.signals import VariableDefinition, VariableSourceKind
from universaldaq.ui import AuthoritySurface, GraphModeSession
from universaldaq_labjack.models import LabJackProbeRow
from universaldaq_labjack.plugin import build_support_pack_registration

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SCN-012',
    'verifies_requirements': ['UDQ-REQ-UI-006', 'UDQ-REQ-ARCH-001', 'UDQ-REQ-SIG-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-005'],
    'worked_example_reference': None,
    'expected_proof_output': 'vertical slice from discovery through binding, variable health, disconnect, and reconnect',
}
pytestmark = pytest.mark.scenario


def test_vertical_slice_binding_variable_disconnect_and_reconnect_updates_review_state():
    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(LabJackProbeRow(model='U6', serial_number='470001', transport='usb'),)
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-U6-VSLICE'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
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
    controller.register_variable_definition(
        definition=VariableDefinition(
            variable_id=VariableId('stack_voltage_copy'),
            display_name='Stack Voltage Copy',
            source_kind=VariableSourceKind.SIGNAL,
            signal_dependencies=(SignalId('stack_voltage'),),
        ),
        timestamp=as_event_time(6),
    )

    controller.begin_quick_start(timestamp=as_event_time(7))
    view_model = controller.view_model()
    assert view_model.device_phase == 'live'
    assert view_model.lifecycle_summary is not None
    assert view_model.lifecycle_summary.projected_point_count >= 1
    assert view_model.lifecycle_summary.published_signal_count == 1
    assert view_model.binding_review_summary is not None
    assert view_model.binding_review_summary.total_signal_binding_count == 1
    assert view_model.variable_health_summary is not None
    assert view_model.variable_health_summary.total_variable_count == 1
    assert view_model.variable_health_summary.healthy_count == 1

    controller.mark_active_device_disconnected(timestamp=as_event_time(8))
    disconnected = controller.view_model()
    assert disconnected.device_phase == 'disconnected'
    assert disconnected.lifecycle_summary is not None
    assert disconnected.lifecycle_summary.disconnected_signal_count == 1
    assert disconnected.variable_health_summary is not None
    assert disconnected.variable_health_summary.impacted_count >= 1

    controller.reconnect_active_device(timestamp=as_event_time(9))
    reconnected = controller.view_model()
    assert reconnected.device_phase == 'live'
    assert reconnected.variable_health_summary is not None
    assert reconnected.variable_health_summary.healthy_count == 1
    assert reconnected.lifecycle_summary is not None
    assert reconnected.lifecycle_summary.published_signal_count == 1
