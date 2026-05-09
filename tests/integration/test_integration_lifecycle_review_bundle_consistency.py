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
    'test_id': 'UDQ-TST-INT-012',
    'verifies_requirements': ['UDQ-REQ-UI-006', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'lifecycle review bundle counts stay consistent with session summaries and runtime diagnostics',
}
pytestmark = pytest.mark.integration


def test_lifecycle_review_bundle_remains_consistent_with_session_state_and_runtime_summary():
    controller, services, device = _bootstrap_controller(profile_id='PROF-BUNDLE-CONSISTENCY')
    controller.bind_logical_signal_to_point(logical_signal_id=SignalId('stack_voltage'), point_key=_point_key_for(device, services, 'analog_in_0'), timestamp=as_event_time(5))
    controller.register_variable_definition(
        definition=VariableDefinition(variable_id=VariableId('stack_voltage_copy'), display_name='Stack Voltage Copy', source_kind=VariableSourceKind.SIGNAL, signal_dependencies=(SignalId('stack_voltage'),)),
        timestamp=as_event_time(6),
    )
    controller.begin_quick_start(timestamp=as_event_time(7))
    controller.mark_active_device_disconnected(timestamp=as_event_time(8))
    controller.reconnect_active_device(timestamp=as_event_time(9))

    bundle = controller.lifecycle_review_bundle()
    ui_session = controller.session.ui_session
    assert bundle['lifecycle_summary']['phase'] == ui_session.lifecycle_summary.phase
    assert bundle['binding_review_summary']['total_signal_binding_count'] == ui_session.binding_review_summary.total_signal_binding_count
    assert bundle['variable_health_summary']['healthy_count'] == ui_session.variable_health_summary.healthy_count
    assert bundle['workbench_review_state']['total_workbench_count'] == ui_session.workbench_review_state.total_workbench_count
    assert bundle['incremental_runtime_summary']['lifecycle.transition.current_phase'] == ui_session.device_lifecycle_phase.value
    assert 'gauges' in bundle['runtime_performance']
    assert len(bundle['transition_trace']) >= 4



def test_degraded_disconnect_incident_does_not_render_as_ready_to_configure():
    from tools.dev._u6_live_support import bootstrap_controller, build_services, install_labjack_support_pack, prepare_u6_live_value_slice
    from universaldaq.common import as_event_time
    from universaldaq_labjack.real_u6 import RealLabJackU6Adapter

    class _FailingReadOnceU6:
        serialNumber = 470099
        firmwareVersion = '1.15'
        hardwareVersion = '2.0'

        def __init__(self) -> None:
            self.failed = False

        def getCalibrationData(self) -> None:
            return None

        def getAIN(self, channel: int) -> float:
            if not self.failed:
                self.failed = True
                raise RuntimeError('usb read timeout')
            return (0.1, 0.2, 0.3)[channel]

        def close(self) -> None:
            return None

    services = build_services()
    install_labjack_support_pack(services, real_hardware=False, simulated_serial_number='470211')
    controller = bootstrap_controller(services=services, profile_id='PROF-U6-DEGRADED-PHASE', actor_id='u6-degraded-phase')
    prepared = prepare_u6_live_value_slice(controller, timestamp_start=3)
    services.adapters.adapters[prepared.active_adapter_id] = RealLabJackU6Adapter(
        adapter_id=prepared.active_adapter_id,
        serial_number='470211',
        backend_factory=lambda serial_number: _FailingReadOnceU6(),
    )

    controller.poll_adapters(timestamp=as_event_time(200))
    bundle = controller.lifecycle_review_bundle()
    assert bundle['lifecycle_summary']['phase'] == 'degraded'
    assert bundle['reviewer_runtime_rollup']['state_family'] == 'degraded'
