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
    'expected_proof_output': 'discovery to shell viewmodel integration flow',
}
pytestmark = pytest.mark.integration


def test_discovery_select_and_remember_flow_reaches_shell_viewmodel_cleanly():
    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(LabJackProbeRow(model='U6', serial_number='470001', transport='usb'),)
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-U6-INT'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.HISTORY)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.HISTORY, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    u6 = next(device for device in controller.discover_devices(timestamp=as_event_time(3)) if device.identity.serial_number == '470001')

    controller.select_detected_device(device_key=u6.device_key, timestamp=as_event_time(4))
    controller.remember_active_device(timestamp=as_event_time(5))
    view_model = controller.view_model()

    assert any(device.display_name.startswith('LabJack U6') for device in view_model.detected_devices)
    assert view_model.active_device is not None
    assert view_model.active_device.known_device is True
    assert view_model.known_device_restore_offer == 'restore available from profile PROF-U6-INT'


def test_controller_exposes_authoritative_binding_rows_for_shell_consumers() -> None:
    from universaldaq.adapters import AdapterPointRef, PointClass
    from universaldaq.signals import BindingPolicy, DevicePointDefinition, LogicalSignalBinding, SignalDefinition

    services = build_default_service_registry(load_support_packs=False)
    device_identity_key = 'device::controller-readback'
    source_definition = DevicePointDefinition(
        point_ref=AdapterPointRef(
            adapter_id='SIM-READ-001',
            point_id='PT-READBACK',
            display_name='Readback Pressure',
            point_class=PointClass.ANALOG,
            units='psi',
        ),
        device_identity_key=device_identity_key,
        friendly_name='Readback Pressure',
        role='analog_input',
    )
    services.bindings.register_point_definition(source_definition)
    services.signals.register_signal(
        SignalDefinition(signal_id=SignalId('SIG-READBACK'), display_name='controller_readback_pressure', engineering_units='psi')
    )
    services.bindings.bind_signal(
        LogicalSignalBinding(
            logical_signal_id=SignalId('SIG-READBACK'),
            source_point_key=source_definition.stable_point_key,
            binding_policy=BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
            metadata={'device_identity_key': device_identity_key, 'friendly_name': 'Readback Pressure'},
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-READBACK'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(20)),
        timestamp=as_event_time(21),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)

    rows = controller.authoritative_binding_rows_for_device(device_identity_key=device_identity_key)

    assert len(rows) == 1
    assert rows[0]['logical_id'] == 'SIG-READBACK'
    assert rows[0]['logical_display_name'] == 'controller_readback_pressure'
    assert rows[0]['status'] == 'applied'
    assert rows[0]['authority_kind'] == 'backend_applied'
    assert rows[0]['authority_source'] == 'ShellServiceRegistry.bindings'
