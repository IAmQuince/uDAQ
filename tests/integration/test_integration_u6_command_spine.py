from __future__ import annotations

from tools.dev._u6_live_support import bootstrap_controller, build_services, install_labjack_support_pack, prepare_u6_live_value_slice, run_poll_cycles
from universaldaq.common import AlarmId, as_event_time

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-022',
    'verifies_requirements': ['UDQ-REQ-EVT-002', 'UDQ-REQ-OUT-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-EVID-004'],
    'worked_example_reference': 'UDQ-EXM-013',
    'expected_proof_output': 'bounded U6 live slice admits alarm acknowledgment and rejects unsupported dry-run output through the command spine',
}


def test_integration_u6_command_spine_ack_and_rejected_dry_run():
    services = build_services()
    install_labjack_support_pack(services, real_hardware=False, simulated_serial_number='470166')
    controller = bootstrap_controller(services=services, profile_id='PROF-U6-CMD-TST', actor_id='u6-command')
    prepared = prepare_u6_live_value_slice(controller, timestamp_start=3)
    run_poll_cycles(controller, timestamp_start=25, cycles=2)

    controller.mark_active_device_disconnected(timestamp=as_event_time(1000))
    controller.acknowledge_alarm(alarm_id=AlarmId('ALM-U6-AVG-DEGRADED'), timestamp=as_event_time(1001))
    controller.reconnect_active_device(timestamp=as_event_time(1002))
    run_poll_cycles(controller, timestamp_start=1003, cycles=1)
    controller.submit_dry_run_adapter_command(
        command_id='CMD-U6-DRY-001',
        adapter_id=prepared.active_adapter_id,
        point_id='analog_in_0',
        requested_value='2.0',
        timestamp=as_event_time(1004),
    )

    bundle = controller.lifecycle_review_bundle()
    assert bundle['command_summary']['command_count'] == 2
    assert bundle['command_summary']['admitted_count'] == 1
    assert bundle['command_summary']['rejected_count'] == 1
    assert bundle['recent_command_rows'][-2]['command_kind'] == 'ack_alarm'
    assert bundle['recent_command_rows'][-1]['rejection_code'] == 'unsupported_capability'
