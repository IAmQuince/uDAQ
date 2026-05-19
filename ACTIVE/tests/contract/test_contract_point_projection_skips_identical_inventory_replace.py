from __future__ import annotations

import pytest

from universaldaq.adapters import AdapterPointRef, PointClass
from universaldaq.common import RuntimeMetricsStore
from universaldaq.signals import DevicePointDefinition, SignalBindingService

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-025',
    'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'identical point inventory replacement is skipped for efficiency',
}
pytestmark = pytest.mark.contract


def test_replace_device_point_definitions_skips_identical_inventory():
    metrics = RuntimeMetricsStore()
    service = SignalBindingService(metrics=metrics)
    definitions = (
        DevicePointDefinition(
            point_ref=AdapterPointRef(adapter_id='A1', point_id='analog_in_0', point_class=PointClass.ANALOG),
            device_identity_key='dev-a',
            friendly_name='AIN0',
            role='analog_input',
            metadata={'vendor_namespace': 'demo'},
        ),
    )

    service.replace_device_point_definitions(device_identity_key='dev-a', definitions=definitions)
    service.replace_device_point_definitions(device_identity_key='dev-a', definitions=definitions)

    assert metrics.counters['bindings.point_definition.replace.calls'] == 1
    assert metrics.counters['bindings.point_definition.replace.skipped'] == 1
    assert metrics.gauges['bindings.point_definition.last_replace_skipped'] == 1
