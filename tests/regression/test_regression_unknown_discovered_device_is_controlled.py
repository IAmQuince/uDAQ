from __future__ import annotations

import pytest

from universaldaq.adapters import AdapterManagerService, UnknownDiscoveredDeviceError

TEST_DECLARATION = {'test_id': 'UDQ-TST-REG-002', 'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-UI-006'], 'checks_invariants': ['UDQ-INV-STATE-001'], 'worked_example_reference': None, 'expected_proof_output': 'unknown discovered device controlled failure regression'}
pytestmark = pytest.mark.regression


def test_activate_discovered_device_raises_typed_error_for_unknown_key():
    service = AdapterManagerService()

    with pytest.raises(UnknownDiscoveredDeviceError, match='unknown discovered device: missing-device'):
        service.activate_discovered_device(device_key='missing-device')
