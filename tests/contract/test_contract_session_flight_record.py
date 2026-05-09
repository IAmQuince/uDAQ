from __future__ import annotations

import pytest

from universaldaq.adapters import DeterministicWaveformAdapter
from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AlarmId, AuthorizationState, GraphMode, ProfileId, VariableId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.events import AlarmDefinition
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-054',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-SEC-001', 'UDQ-REQ-EVT-001'],
    'checks_invariants': ['UDQ-INV-EVID-004', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'trusted-session flight record preserves signal replay, action audit, control posture, and active-alarm summary for the first bench slice',
}
pytestmark = pytest.mark.contract


def test_session_flight_record_carries_action_audit_alarm_summary_and_replay():
    services = build_default_service_registry(load_support_packs=False)
    services.adapters.register(DeterministicWaveformAdapter(adapter_id='DEMO-FIRST-SIGNAL-001'))
    services.events.register_alarm_definition(
        AlarmDefinition(
            alarm_id=AlarmId('ALM-FIRST-BENCH'),
            summary='First bench warning',
            severity='warning',
            source_kind='manual',
            source_id='first_bench',
            variable_id=VariableId('manual_alarm_stub'),
            condition_kind='variable_boolean_true',
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-FLIGHT-RECORD'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
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
    controller.assert_alarm(alarm_id=AlarmId('ALM-FIRST-BENCH'), timestamp=as_event_time(8))

    flight = controller.session_flight_record()
    trusted = flight['trusted_session_inventory']
    assert trusted['control_mode_label'] == 'armed_control'
    assert trusted['signal_freshness_label'] == 'simulated'
    assert trusted['active_alarm_count'] == 1
    assert trusted['recent_action_count'] >= 3
    assert trusted['flight_record_ready'] is True
    assert flight['first_signal_replay_tape'] is not None
    assert flight['first_signal_replay_tape']['provenance_label']
    assert trusted['signal_provenance']['channel_metadata']['source_point_id'] == 'demo_wave_0'
