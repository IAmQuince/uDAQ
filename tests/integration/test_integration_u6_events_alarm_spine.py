from tools.dev._u6_live_support import bootstrap_controller, build_services, install_labjack_support_pack, prepare_u6_live_value_slice, run_poll_cycles
from universaldaq.common import AlarmId, as_event_time

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-021',
    'verifies_requirements': ['UDQ-REQ-EVT-001', 'UDQ-REQ-EVT-002', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-TRANS-003'],
    'worked_example_reference': 'UDQ-EXM-012',
    'expected_proof_output': 'bounded U6 live slice emits event/alarm transitions for disconnect, acknowledge, and reconnect through the canonical journal path',
}


def test_integration_u6_events_alarm_spine_disconnect_ack_reconnect():
    services = build_services()
    install_labjack_support_pack(services, real_hardware=False, simulated_serial_number='470155')
    controller = bootstrap_controller(services=services, profile_id='PROF-U6-EVT-TST', actor_id='evt-tester')
    prepare_u6_live_value_slice(controller, timestamp_start=3)
    run_poll_cycles(controller, timestamp_start=25, cycles=3)

    controller.mark_active_device_disconnected(timestamp=as_event_time(1000))
    summary_after_disconnect = controller.lifecycle_review_bundle()
    assert summary_after_disconnect['event_alarm_summary']['active_alarm_count'] == 1
    assert summary_after_disconnect['recent_event_rows'][-1]['event_type'] == 'alarm_raised'

    controller.acknowledge_alarm(alarm_id=AlarmId('ALM-U6-AVG-DEGRADED'), timestamp=as_event_time(1001))
    summary_after_ack = controller.lifecycle_review_bundle()
    assert summary_after_ack['event_alarm_summary']['unacknowledged_alarm_count'] == 0
    assert any(row['event_type'] == 'alarm_acknowledged' for row in summary_after_ack['recent_event_rows'])

    controller.reconnect_active_device(timestamp=as_event_time(1002))
    run_poll_cycles(controller, timestamp_start=1003, cycles=1)
    final_summary = controller.lifecycle_review_bundle()
    assert final_summary['event_alarm_summary']['active_alarm_count'] == 0
    assert any(row['event_type'] == 'alarm_cleared' for row in final_summary['recent_event_rows'])
