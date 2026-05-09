from __future__ import annotations

import pytest

from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INV-012',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-REL-001'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'core no-vendor support-pack invariant proof',
}
pytestmark = pytest.mark.invariants


def test_core_registry_and_discovery_work_without_vendor_support_pack_requirement():
    services = build_default_service_registry(load_support_packs=False)
    discovered = services.adapters.discover_devices(timestamp=as_event_time(40))
    assert discovered
    assert {'generic_adapter_inventory'} == {device.provider_id for device in discovered}
    assert not services.adapters.support_packs
    assert services.adapters.support_pack_load_inventory() == ()
