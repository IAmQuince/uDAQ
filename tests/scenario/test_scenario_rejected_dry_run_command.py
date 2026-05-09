from __future__ import annotations

from tools.dev._u6_live_support import bootstrap_controller, build_services, install_labjack_support_pack, prepare_u6_live_value_slice
from universaldaq.common import as_event_time

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SCN-CMD-002',
    'verifies_requirements': ['UDQ-REQ-OUT-001', 'UDQ-REQ-MOD-002'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'unsupported dry-run command is rejected with a clear capability reason',
}


def test_rejected_dry_run_command_reports_unsupported_capability():
    services = build_services()
    install_labjack_support_pack(services, real_hardware=False, simulated_serial_number='470165')
    controller = bootstrap_controller(services=services, profile_id='PROF-CMD-DRY', actor_id='cmd-tester')
    prepared = prepare_u6_live_value_slice(controller, timestamp_start=3)

    controller.submit_dry_run_adapter_command(
        command_id='CMD-DRY-U6-001',
        adapter_id=prepared.active_adapter_id,
        point_id='analog_in_0',
        requested_value='1.23',
        timestamp=as_event_time(30),
    )
    bundle = controller.lifecycle_review_bundle()
    row = bundle['recent_command_rows'][-1]

    assert row['admission_status'] == 'rejected'
    assert row['rejection_code'] == 'unsupported_capability'
    assert bundle['command_summary']['rejected_count'] == 1
