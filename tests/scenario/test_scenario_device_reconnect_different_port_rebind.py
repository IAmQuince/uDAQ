from __future__ import annotations

import pytest

from universaldaq.adapters import DeviceIdentity, ReconciliationOutcomeKind
from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SCN-017',
    'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-DEV-002'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'same-device reconnect on new port proof',
}
pytestmark = pytest.mark.scenario


def test_known_device_reconnects_on_new_port_without_becoming_new_device():
    services = build_default_service_registry()
    first = services.device_registry.register_or_attach(
        identity=DeviceIdentity(
            stable_key='labjack::u6::470001',
            display_name='LabJack U6',
            vendor='LabJack',
            model='U6',
            serial_number='470001',
            transport='usb',
        ),
        provider_id='labjack_bridge',
        transport_path='usb:1',
        timestamp=as_event_time(30),
    )
    disconnected = services.device_registry.disconnect(
        connection_instance_id=first.connection.connection_instance_id,
        timestamp=as_event_time(31),
    )
    second = services.device_registry.register_or_attach(
        identity=DeviceIdentity(
            stable_key='labjack::u6::470001',
            display_name='LabJack U6',
            vendor='LabJack',
            model='U6',
            serial_number='470001',
            transport='usb',
        ),
        provider_id='labjack_bridge',
        transport_path='usb:7',
        timestamp=as_event_time(32),
    )

    assert disconnected.state.value == 'disconnected'
    assert second.kind == ReconciliationOutcomeKind.RESTORED_WITH_PORT_CHANGE
    assert first.device_record.device_record_id == second.device_record.device_record_id
    assert second.device_record.last_transport_path == 'usb:7'
