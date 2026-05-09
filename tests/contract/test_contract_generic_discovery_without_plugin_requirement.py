from __future__ import annotations

import pytest

from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time
from universaldaq.adapters import DeviceSupportTier

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-018',
    'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'generic discovery inventory without vendor pack requirement',
}
pytestmark = pytest.mark.contract


def test_generic_discovery_remains_available_without_vendor_support_pack_requirement():
    services = build_default_service_registry()
    discovered = services.adapters.discover_devices(timestamp=as_event_time(10))

    assert 'generic_adapter_inventory' in services.adapters.discovery_providers
    assert discovered
    assert {device.support_tier for device in discovered} == {DeviceSupportTier.GENERIC}
    assert {device.bound_adapter_id for device in discovered} == {'SIM-READ-001', 'SIM-WRITE-001'}
