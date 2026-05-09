from __future__ import annotations

import pytest

from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time
from universaldaq_rpi.models import RaspberryPiProbeRow
from universaldaq_rpi.plugin import build_support_pack_registration

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-032',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-DEV-001'],
    'checks_invariants': ['UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'raspberry pi support pack exposes the shared support-pack contract',
}
pytestmark = pytest.mark.contract


def test_raspberry_pi_support_pack_discovery_activation_and_capability_shape():
    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(RaspberryPiProbeRow(model='5', host_id='rpi-edge-001', enable_gpio=True),)
        )
    )

    device = next(item for item in services.adapters.discover_devices(timestamp=as_event_time(30)) if item.identity.serial_number == 'rpi-edge-001')
    assert device.identity.transport == 'local'
    assert 'Raspberry Pi Host Health' in {workbench.display_name for workbench in device.workbenches}

    activated, adapter_id, workbenches = services.adapters.activate_discovered_device(device_key=device.device_key)
    assert adapter_id is not None
    assert activated.bound_adapter_id == adapter_id
    assert 'Raspberry Pi GPIO Map' in {workbench.display_name for workbench in workbenches}

    capability = services.adapters.adapters[adapter_id].capability()
    assert capability.metadata['support_pack'] == 'universaldaq_rpi'
    assert capability.metadata['adapter_family'] == 'local_platform'
    assert {point.point_id for point in capability.readable_points} >= {'host_cpu_temp_c', 'host_uptime_s', 'gpio_in_17', 'gpio_in_27'}
