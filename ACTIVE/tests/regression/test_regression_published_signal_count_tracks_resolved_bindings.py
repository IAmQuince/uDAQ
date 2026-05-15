from tools.dev._u6_live_support import bootstrap_controller, build_services, install_labjack_support_pack, prepare_u6_live_value_slice
from universaldaq.common import as_event_time

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-REG-012',
    'verifies_requirements': ['UDQ-REQ-DEV-001'],
    'checks_invariants': ['UDQ-INV-TRANS-003'],
    'worked_example_reference': 'UDQ-EXM-013',
    'expected_proof_output': 'published signal count tracks resolved bindings rather than only changed signals during bounded live polls',
}


def test_regression_published_signal_count_tracks_resolved_bindings():
    services = build_services()
    install_labjack_support_pack(services, real_hardware=False, simulated_serial_number='470155')
    controller = bootstrap_controller(services=services, profile_id='PROF-U6-PUB-SIG', actor_id='pub-sig')
    prepare_u6_live_value_slice(controller, timestamp_start=3)

    bundle = controller.lifecycle_review_bundle()
    assert bundle['lifecycle_summary']['projected_point_count'] >= 3
    assert bundle['lifecycle_summary']['published_signal_count'] == 3
