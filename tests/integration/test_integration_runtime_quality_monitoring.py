from __future__ import annotations

import json

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
    'test_id': 'UDQ-TST-INT-013',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-SIG-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-STATE-003', 'UDQ-INV-TIME-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'runtime quality layer journals live samples and exposes bounded runtime status in lifecycle review output',
}
pytestmark = pytest.mark.integration


def _bootstrap_controller(tmp_path):
    services = build_default_service_registry()
    services.runtime_quality.journal.file_path = tmp_path / 'runtime' / 'session.jsonl'
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(LabJackProbeRow(model='U6', serial_number='470055', transport='usb'),)
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-RUNTIME-QUALITY'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    device = next(item for item in controller.discover_devices(timestamp=as_event_time(3)) if item.identity.serial_number == '470055')
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))
    point_key = next(
        point_key
        for point_key, definition in services.bindings.point_definitions.items()
        if definition.device_identity_key == device.identity.stable_key and definition.point_ref.point_id == 'analog_in_0'
    )
    controller.bind_logical_signal_to_point(logical_signal_id=SignalId('stack_voltage'), point_key=point_key, timestamp=as_event_time(5))
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
    return controller, services


def test_runtime_quality_bundle_contains_status_and_journaled_rows(tmp_path):
    controller, services = _bootstrap_controller(tmp_path)
    controller.mark_active_device_disconnected(timestamp=as_event_time(8))
    controller.reconnect_active_device(timestamp=as_event_time(9))

    bundle = controller.lifecycle_review_bundle()
    journal_path = services.runtime_quality.journal.file_path
    assert bundle['runtime_status']['journal_write_count'] > 0
    assert bundle['runtime_status']['recent_signal_count'] >= 1
    assert bundle['runtime_status']['recent_runtime_event_count'] >= 2
    assert bundle['incremental_runtime_summary']['runtime.presentation.publish_total'] >= 1
    rows = [json.loads(line) for line in journal_path.read_text(encoding='utf-8').splitlines()]
    record_types = {row['record_type'] for row in rows}
    assert {'sample', 'cycle', 'runtime_event'} <= record_types


def test_runtime_quality_coalesces_repeated_presentation_updates(tmp_path):
    controller, services = _bootstrap_controller(tmp_path)

    controller.poll_adapters(timestamp=as_event_time(10))
    controller.poll_adapters(timestamp=as_event_time(10))

    status = services.runtime_quality.snapshot()
    assert status.presentation_publish_count >= 1
    assert status.presentation_coalesced_count >= 1
