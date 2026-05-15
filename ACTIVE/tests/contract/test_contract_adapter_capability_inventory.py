from __future__ import annotations

from universaldaq.adapters import AdapterManagerService, SimulatedReadAdapter, SimulatedWritableAdapter

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-ADAPT-001', 'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-DEV-002'], 'checks_invariants': ['UDQ-INV-TIME-001'], 'worked_example_reference': None, 'expected_proof_output': 'adapter capability inventory report'}


def test_adapter_capability_inventory_surfaces_point_and_operation_metadata():
    manager = AdapterManagerService()
    manager.register(SimulatedReadAdapter.from_values(adapter_id='SIM-READ', values={'PT-101': ('1', '1', 'psi')}, timestamp=1))
    manager.register(SimulatedWritableAdapter(adapter_id='SIM-WRITE', writable_points={'OUT-1': '0'}, observed_points={'OUT-1': '0'}))

    inventory = {cap.adapter_id: cap for cap in manager.capability_inventory()}

    assert set(inventory) == {'SIM-READ', 'SIM-WRITE'}
    assert inventory['SIM-READ'].readable_points[0].point_id == 'PT-101'
    assert inventory['SIM-WRITE'].supports_write('OUT-1') is True
