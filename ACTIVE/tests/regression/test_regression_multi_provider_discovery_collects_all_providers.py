from __future__ import annotations

from dataclasses import dataclass

import pytest

from universaldaq.adapters import AdapterManagerService, DeviceIdentity, DeviceSupportTier, DiscoveredDevice
from universaldaq.common import as_event_time

TEST_DECLARATION = {'test_id': 'UDQ-TST-REG-001', 'verifies_requirements': ['UDQ-REQ-DEV-001'], 'checks_invariants': ['UDQ-INV-STATE-001'], 'worked_example_reference': None, 'expected_proof_output': 'multi-provider discovery aggregation regression'}
pytestmark = pytest.mark.regression


@dataclass(slots=True)
class _StaticProvider:
    provider_id: str
    device: DiscoveredDevice

    def discover(self, *, timestamp: int) -> tuple[DiscoveredDevice, ...]:
        del timestamp
        return (self.device,)

    def activate(self, device: DiscoveredDevice):
        del device
        return None

    def workbenches(self, device: DiscoveredDevice) -> tuple[object, ...]:
        return device.workbenches


def _device(*, provider_id: str, suffix: str) -> DiscoveredDevice:
    return DiscoveredDevice(
        device_key=f'{provider_id}:{suffix}',
        identity=DeviceIdentity(stable_key=f'{provider_id}::{suffix}', display_name=f'{provider_id}-{suffix}'),
        provider_id=provider_id,
        support_tier=DeviceSupportTier.GENERIC,
    )


def test_multi_provider_discovery_collects_devices_from_every_registered_provider():
    service = AdapterManagerService()
    service.register_discovery_provider(_StaticProvider(provider_id='provider_a', device=_device(provider_id='provider_a', suffix='one')))
    service.register_discovery_provider(_StaticProvider(provider_id='provider_b', device=_device(provider_id='provider_b', suffix='two')))

    discovered = service.discover_devices(timestamp=as_event_time(5))

    assert [device.provider_id for device in discovered] == ['provider_a', 'provider_b']
    assert {device.device_key for device in discovered} == {'provider_a:one', 'provider_b:two'}
