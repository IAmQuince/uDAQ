from __future__ import annotations

from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-ADAPT-001', 'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-DIAG-001'], 'checks_invariants': ['UDQ-INV-TIME-001'], 'worked_example_reference': None, 'expected_proof_output': 'adapter poll snapshot flow'}


def test_adapter_poll_updates_snapshot_inventory_with_timestamps():
    services = build_default_service_registry()
    results = services.adapters.poll_all(timestamp=as_event_time(10))
    snapshots = services.adapters.snapshots()

    assert len(results) >= 2
    assert snapshots
    assert all(int(item.received_timestamp) == 10 for item in snapshots)
