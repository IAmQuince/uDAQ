from __future__ import annotations

import pytest

from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time
from universaldaq.tags import CanonicalTagRegistryService, MultiAdapterAcquisitionBroker
from universaldaq_arduino.models import ArduinoProbeRow
from universaldaq_arduino.plugin import build_support_pack_registration as build_arduino_pack
from universaldaq_labjack.models import LabJackProbeRow
from universaldaq_labjack.plugin import build_support_pack_registration as build_labjack_pack

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-038',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-DEV-001', 'UDQ-REQ-SIG-001'],
    'checks_invariants': ['UDQ-INV-STATE-004', 'UDQ-INV-TIME-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'canonical tag registry projects multiple adapter families into stable, queryable, capability-based tag definitions without vendor logic in the core service',
}
pytestmark = pytest.mark.contract


def test_canonical_tag_registry_projects_multiple_adapter_families():
    services = build_default_service_registry(load_support_packs=False)
    services.adapters.install_support_pack(
        build_labjack_pack(probe_rows=(LabJackProbeRow(model='U6', serial_number='470301', transport='usb'),))
    )
    services.adapters.install_support_pack(
        build_arduino_pack(probe_rows=(ArduinoProbeRow(board='Uno', serial_number='ARD-501', port='COM51'),))
    )
    discovered = services.adapters.discover_devices(timestamp=as_event_time(1))
    adapter_ids: list[str] = []
    for device in discovered:
        if device.provider_id not in {'labjack_u6_support', 'arduino_serial_support'}:
            continue
        _, adapter_id, _ = services.adapters.activate_discovered_device(device_key=device.device_key)
        assert adapter_id is not None
        adapter_ids.append(adapter_id)

    registry = CanonicalTagRegistryService(metrics=services.runtime_metrics)
    broker = MultiAdapterAcquisitionBroker(adapter_manager=services.adapters, tag_registry=registry, metrics=services.runtime_metrics)
    batch = broker.poll(adapter_ids=tuple(adapter_ids), timestamp=as_event_time(2))

    assert len(batch.adapter_ids) == 2
    assert len(batch.samples) >= 4
    assert len(registry.definitions) >= len(batch.samples)
    tag_rows = registry.latest_sample_rows()
    assert any(row['canonical_name'].startswith('labjack_u6_470301.') for row in tag_rows)
    assert any(row['canonical_name'].startswith('arduino_uno_ard_501.') for row in tag_rows)
    assert registry.counts_by_adapter()[adapter_ids[0]] > 0
    assert registry.counts_by_adapter()[adapter_ids[1]] > 0
