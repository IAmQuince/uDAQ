from __future__ import annotations

import pytest

from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-030',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-DEV-001'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'optional support packs load lazily and leave generic discovery intact',
}
pytestmark = pytest.mark.contract


def test_optional_support_pack_loader_records_install_reports_without_discovery_drift():
    services = build_default_service_registry()
    reports = {report.pack_id: report for report in services.adapters.support_pack_load_inventory()}

    assert {'universaldaq_labjack', 'universaldaq_arduino', 'universaldaq_rpi'} <= set(reports)
    assert reports['universaldaq_labjack'].installed
    assert reports['universaldaq_arduino'].installed
    assert reports['universaldaq_rpi'].installed

    discovered = services.adapters.discover_devices(timestamp=as_event_time(12))
    assert discovered
    assert {device.provider_id for device in discovered} == {'generic_adapter_inventory'}
