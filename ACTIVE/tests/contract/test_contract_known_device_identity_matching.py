from __future__ import annotations

import pytest

from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time
from universaldaq_labjack.models import LabJackProbeRow
from universaldaq_labjack.plugin import build_support_pack_registration

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-020',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-PROF-001'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'known-device identity match proof',
}
pytestmark = pytest.mark.contract


def test_known_device_record_matches_rediscovered_identity_by_stable_key():
    services = build_default_service_registry()
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(LabJackProbeRow(model='U6', serial_number='470001', transport='usb'),)
        )
    )
    discovered = services.adapters.discover_devices(timestamp=as_event_time(30))
    u6 = next(device for device in discovered if device.identity.serial_number == '470001')
    record = services.adapters.remember_known_device(identity=u6.identity, timestamp=as_event_time(31), profile_id='PROF-U6')

    rediscovered = services.adapters.discover_devices(timestamp=as_event_time(32))
    matched = next(device for device in rediscovered if device.identity.serial_number == '470001')

    assert matched.known_device_key == record.known_device_key
