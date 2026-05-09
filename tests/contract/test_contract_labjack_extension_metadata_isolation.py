from __future__ import annotations

import pytest

from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time
from universaldaq_labjack.models import LabJackProbeRow
from universaldaq_labjack.plugin import build_support_pack_registration

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-019',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-ARCH-002'],
    'checks_invariants': ['UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'vendor metadata isolation proof for LabJack pilot',
}
pytestmark = pytest.mark.contract


def test_labjack_specific_channel_terms_remain_in_extension_metadata_not_core_point_identity():
    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(LabJackProbeRow(model='U6', serial_number='470001', transport='usb'),)
        )
    )
    discovered = services.adapters.discover_devices(timestamp=as_event_time(20))
    u6 = next(device for device in discovered if device.identity.serial_number == '470001')
    _, adapter_id, _ = services.adapters.activate_discovered_device(device_key=u6.device_key)
    capability = services.adapters.adapters[adapter_id].capability()

    point_ids = {point.point_id for point in capability.readable_points}
    assert 'AIN0' not in point_ids
    assert 'FIO0' not in point_ids
    assert {'analog_in_0', 'analog_in_1', 'digital_in_0', 'digital_in_1'}.issubset(point_ids)
    assert any(point.metadata.get('hardware_channel') == 'AIN0' for point in capability.readable_points)
    assert any(point.metadata.get('vendor_namespace') == 'labjack' for point in capability.readable_points)
