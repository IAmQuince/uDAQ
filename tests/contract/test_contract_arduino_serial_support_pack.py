from __future__ import annotations

import pytest

from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time
from universaldaq_arduino.models import ArduinoProbeRow
from universaldaq_arduino.plugin import build_support_pack_registration

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-031',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-DEV-001'],
    'checks_invariants': ['UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'arduino serial support pack exposes the shared support-pack contract',
}
pytestmark = pytest.mark.contract


def test_arduino_serial_support_pack_discovery_activation_and_capability_shape():
    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(ArduinoProbeRow(board='Uno', serial_number='A-001', port='COM7', firmware_version='1.0.0'),)
        )
    )

    device = next(item for item in services.adapters.discover_devices(timestamp=as_event_time(20)) if item.identity.serial_number == 'A-001')
    assert device.identity.transport == 'serial'
    assert device.support_tier.value == 'protocol_family'
    assert 'Arduino Serial Console' in {workbench.display_name for workbench in device.workbenches}

    activated, adapter_id, workbenches = services.adapters.activate_discovered_device(device_key=device.device_key)
    assert adapter_id is not None
    assert activated.bound_adapter_id == adapter_id
    assert 'Arduino Firmware Info' in {workbench.display_name for workbench in workbenches}

    capability = services.adapters.adapters[adapter_id].capability()
    assert capability.metadata['support_pack'] == 'universaldaq_arduino'
    assert capability.metadata['protocol_family'] == 'microcontroller_serial'
    assert {point.point_id for point in capability.readable_points} >= {'analog_in_0', 'analog_in_1', 'digital_in_2', 'digital_in_3', 'firmware_alive'}
