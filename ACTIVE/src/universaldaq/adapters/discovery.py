from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .contracts import AdapterContract
from .models import DeviceIdentity, DeviceSupportTier, DiscoveredDevice, WorkbenchDescriptor


@dataclass(slots=True)
class AdapterInventoryDiscoveryProvider:
    provider_id: str
    capability_inventory_getter: Callable[[], tuple[object, ...]]
    adapter_getter: Callable[[str], AdapterContract | None]

    def discover(self, *, timestamp: int) -> tuple[DiscoveredDevice, ...]:
        del timestamp
        discovered: list[DiscoveredDevice] = []
        for capability in self.capability_inventory_getter():
            adapter_id = capability.adapter_id
            identity = DeviceIdentity(
                stable_key=f'generic::{adapter_id}',
                display_name=capability.metadata.get('display_name', adapter_id),
                vendor=capability.metadata.get('vendor'),
                model=capability.metadata.get('model'),
                serial_number=capability.metadata.get('serial_number'),
                transport=capability.metadata.get('transport', 'generic-adapter'),
                provisional=True,
                metadata={
                    'adapter_kind': capability.adapter_kind.value,
                    'operation_mode': capability.operation_mode.value,
                },
            )
            labels = tuple(sorted(set(capability.service_capabilities)))
            if any(point.point_class.value == 'analog' for point in capability.readable_points):
                labels = labels + ('analog_input',)
            if any(point.point_class.value == 'digital' for point in capability.readable_points):
                labels = labels + ('digital_input',)
            if capability.writable_points:
                labels = labels + ('manual_write',)
            discovered.append(
                DiscoveredDevice(
                    device_key=f'{self.provider_id}:{adapter_id}',
                    identity=identity,
                    provider_id=self.provider_id,
                    support_tier=DeviceSupportTier.GENERIC,
                    capability_labels=tuple(sorted(set(labels))),
                    bound_adapter_id=adapter_id,
                    workbenches=(
                        WorkbenchDescriptor(
                            workbench_id='generic_diagnostics',
                            display_name='Generic Diagnostics',
                            activation_reason='generic adapter inventory available',
                        ),
                    ),
                    metadata={'activation_mode': 'bound_adapter'},
                )
            )
        return tuple(discovered)

    def activate(self, device: DiscoveredDevice) -> AdapterContract | None:
        if device.bound_adapter_id is None:
            return None
        return self.adapter_getter(device.bound_adapter_id)

    def workbenches(self, device: DiscoveredDevice) -> tuple[WorkbenchDescriptor, ...]:
        return device.workbenches
