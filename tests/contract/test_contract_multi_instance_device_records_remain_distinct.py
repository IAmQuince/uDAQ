from __future__ import annotations

import pytest

from universaldaq.adapters import DeviceIdentity, ReconciliationOutcomeKind
from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-022',
    'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-DEV-002'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'multi-instance device identity proof',
}
pytestmark = pytest.mark.contract


def test_identical_model_devices_with_distinct_serials_remain_distinct_records():
    services = build_default_service_registry()
    first = services.device_registry.register_or_attach(
        identity=DeviceIdentity(
            stable_key='labjack::u6::111111',
            display_name='LabJack U6',
            vendor='LabJack',
            model='U6',
            serial_number='111111',
            transport='usb',
        ),
        provider_id='labjack_bridge',
        transport_path='usb:1',
        timestamp=as_event_time(10),
    )
    second = services.device_registry.register_or_attach(
        identity=DeviceIdentity(
            stable_key='labjack::u6::222222',
            display_name='LabJack U6',
            vendor='LabJack',
            model='U6',
            serial_number='222222',
            transport='usb',
        ),
        provider_id='labjack_bridge',
        transport_path='usb:2',
        timestamp=as_event_time(11),
    )

    assert first.kind == ReconciliationOutcomeKind.NEW_DEVICE_ENROLLED
    assert second.kind == ReconciliationOutcomeKind.NEW_DEVICE_ENROLLED
    assert first.device_record.device_record_id != second.device_record.device_record_id
    assert {record.serial_number for record in services.device_registry.active_records()} == {'111111', '222222'}
