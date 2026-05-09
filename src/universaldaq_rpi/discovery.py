from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from universaldaq.adapters import DeviceIdentity, DeviceSupportTier, DiscoveredDevice, WorkbenchDescriptor
from universaldaq.adapters.contracts import AdapterContract

from .models import RaspberryPiProbeRow
from .simulated_local import SimulatedRaspberryPiAdapter


@dataclass(slots=True)
class RaspberryPiDiscoveryProvider:
    provider_id: str = 'raspberry_pi_support'
    probe_rows: tuple[RaspberryPiProbeRow, ...] = field(default_factory=tuple)

    def discover(self, *, timestamp: int) -> tuple[DiscoveredDevice, ...]:
        del timestamp
        discovered: list[DiscoveredDevice] = []
        for row in self.probe_rows:
            identity = DeviceIdentity(
                stable_key=f'raspberry_pi::{row.host_id}',
                display_name=f'Raspberry Pi {row.model} ({row.host_id})',
                vendor='Raspberry Pi',
                model=row.model,
                serial_number=row.host_id,
                transport=row.transport,
                firmware_version=row.firmware_version,
                metadata={'enable_gpio': str(row.enable_gpio).lower(), **row.metadata},
            )
            discovered.append(
                DiscoveredDevice(
                    device_key=f'{self.provider_id}:{row.host_id}',
                    identity=identity,
                    provider_id=self.provider_id,
                    support_tier=DeviceSupportTier.PROTOCOL_FAMILY,
                    capability_labels=('host_metric', 'local_platform', 'gpio_input' if row.enable_gpio else 'host_only', 'review_ready'),
                    bound_adapter_id=None,
                    workbenches=self.workbenches_from_row(row),
                    metadata={
                        'enhancement_pack': 'universaldaq_rpi',
                        'transport_hint': 'local',
                        'review_surface_hint': 'host_health,gpio_map,system_info',
                    },
                )
            )
        return tuple(discovered)

    def activate(self, device: DiscoveredDevice) -> AdapterContract | None:
        host_id = device.identity.serial_number
        if host_id is None:
            return None
        enable_gpio = device.identity.metadata.get('enable_gpio', 'true') == 'true'
        return SimulatedRaspberryPiAdapter(
            adapter_id=f'RPI-{host_id.upper()}',
            model=device.identity.model or '4B',
            host_id=host_id,
            transport=device.identity.transport or 'local',
            enable_gpio=enable_gpio,
            metadata={'activation_source': self.provider_id},
        )

    def workbenches(self, device: DiscoveredDevice) -> tuple[WorkbenchDescriptor, ...]:
        return device.workbenches

    def workbenches_from_row(self, row: RaspberryPiProbeRow) -> tuple[WorkbenchDescriptor, ...]:
        return (
            WorkbenchDescriptor(
                workbench_id='rpi_host_health',
                display_name='Raspberry Pi Host Health',
                activation_reason='local platform identity and host metrics available',
                metadata={'vendor_namespace': 'raspberry_pi'},
            ),
            WorkbenchDescriptor(
                workbench_id='rpi_gpio_map',
                display_name='Raspberry Pi GPIO Map',
                activation_reason='gpio-backed points available' if row.enable_gpio else 'gpio surface disabled for this probe row',
                metadata={'vendor_namespace': 'raspberry_pi'},
            ),
            WorkbenchDescriptor(
                workbench_id='rpi_system_info',
                display_name='Raspberry Pi System Info',
                activation_reason='system-level diagnostics and identity available',
                metadata={'vendor_namespace': 'raspberry_pi'},
            ),
        )


def build_probe_rows(rows: Iterable[dict[str, str]]) -> tuple[RaspberryPiProbeRow, ...]:
    return tuple(
        RaspberryPiProbeRow(
            model=row.get('model', '4B'),
            host_id=row['host_id'],
            transport=row.get('transport', 'local'),
            firmware_version=row.get('firmware_version'),
            enable_gpio=row.get('enable_gpio', 'true').lower() == 'true',
            metadata={
                key: value
                for key, value in row.items()
                if key not in {'model', 'host_id', 'transport', 'firmware_version', 'enable_gpio'}
            },
        )
        for row in rows
    )
