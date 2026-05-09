from __future__ import annotations

from dataclasses import dataclass, field
from importlib.util import find_spec
from typing import Iterable

from universaldaq.adapters import DeviceIdentity, DeviceSupportTier, DiscoveredDevice, WorkbenchDescriptor
from universaldaq.adapters.contracts import AdapterContract

from .models import LabJackProbeRow
from .real_u6 import BackendFactory, RealLabJackU6Adapter, _default_backend_factory, probe_real_u6_row
from .simulated_u6 import SimulatedLabJackU6Adapter


@dataclass(slots=True)
class LabJackU6DiscoveryProvider:
    provider_id: str = 'labjack_u6_support'
    probe_rows: tuple[LabJackProbeRow, ...] = field(default_factory=tuple)
    prefer_real_hardware: bool = False
    auto_probe_real_hardware: bool = False
    requested_serial_number: str | None = None
    real_backend_factory: BackendFactory | None = None

    def discover(self, *, timestamp: int) -> tuple[DiscoveredDevice, ...]:
        del timestamp
        rows = list(self.probe_rows)
        if self.auto_probe_real_hardware:
            real_row = probe_real_u6_row(requested_serial_number=self.requested_serial_number)
            if real_row is not None:
                rows.append(build_probe_rows((real_row,))[0])
        discovered: list[DiscoveredDevice] = []
        driver_available, driver_name = probe_driver_status()
        for row in rows:
            hardware_mode = row.metadata.get('hardware_mode', 'simulated')
            identity = DeviceIdentity(
                stable_key=f'labjack::u6::{row.serial_number}',
                display_name=f'LabJack U6 ({row.serial_number})',
                vendor='LabJack',
                model=row.model,
                serial_number=row.serial_number,
                transport=row.transport,
                firmware_version=row.firmware_version,
                hardware_revision=row.hardware_revision,
                provisional=False,
                metadata={
                    'driver_available': str(driver_available).lower(),
                    'driver_name': driver_name,
                    'hardware_mode': hardware_mode,
                    **row.metadata,
                },
            )
            discovered.append(
                DiscoveredDevice(
                    device_key=f'{self.provider_id}:{row.serial_number}',
                    identity=identity,
                    provider_id=self.provider_id,
                    support_tier=DeviceSupportTier.ENHANCED,
                    capability_labels=('analog_input', 'analog_output', 'digital_io', 'stream_capable', 'timers_available', 'counters_available', 'review_ready'),
                    bound_adapter_id=None,
                    workbenches=self.workbenches_from_row(row),
                    metadata={
                        'enhancement_pack': 'universaldaq_labjack',
                        'connection_label': '' if row.connection_label is None else row.connection_label,
                        'channel_family_hint': 'ain,dac,fio',
                        'review_surface_hint': 'channel_mapper,stream_setup,device_info',
                        'hardware_mode': hardware_mode,
                    },
                )
            )
        return tuple(discovered)

    def activate(self, device: DiscoveredDevice) -> AdapterContract | None:
        serial_number = device.identity.serial_number
        if serial_number is None:
            return None
        hardware_mode = device.identity.metadata.get('hardware_mode', device.metadata.get('hardware_mode', 'simulated'))
        should_use_real = self.prefer_real_hardware or hardware_mode == 'real'
        if should_use_real and probe_driver_status()[0]:
            return RealLabJackU6Adapter(
                adapter_id=f'LABJACK-U6-REAL-{serial_number}',
                serial_number=serial_number,
                transport=device.identity.transport or 'usb',
                metadata={'activation_source': self.provider_id, 'hardware_mode': 'real'},
                backend_factory=self.real_backend_factory or _default_backend_factory,
                prefer_direct_reacquire=True,
            )
        return SimulatedLabJackU6Adapter(
            adapter_id=f'LABJACK-U6-{serial_number}',
            serial_number=serial_number,
            transport=device.identity.transport or 'usb',
            metadata={'activation_source': self.provider_id, 'hardware_mode': 'simulated'},
        )

    def workbenches(self, device: DiscoveredDevice) -> tuple[WorkbenchDescriptor, ...]:
        return device.workbenches

    def workbenches_from_row(self, row: LabJackProbeRow) -> tuple[WorkbenchDescriptor, ...]:
        mode = row.metadata.get('hardware_mode', 'simulated')
        return (
            WorkbenchDescriptor(
                workbench_id='labjack_u6_channel_mapper',
                display_name='LabJack Channel Mapper',
                activation_reason=f'U6 detected on {row.transport}',
                metadata={'vendor_namespace': 'labjack', 'hardware_mode': mode},
            ),
            WorkbenchDescriptor(
                workbench_id='labjack_u6_stream_setup',
                display_name='LabJack U6 Stream Setup',
                activation_reason='stream-capable LabJack U6 support pack active',
                metadata={'vendor_namespace': 'labjack', 'hardware_mode': mode},
            ),
            WorkbenchDescriptor(
                workbench_id='labjack_u6_device_info',
                display_name='LabJack U6 Device Info',
                activation_reason='enhanced identity and diagnostics available',
                metadata={'vendor_namespace': 'labjack', 'hardware_mode': mode},
            ),
        )


def probe_driver_status() -> tuple[bool, str]:
    for module_name in ('u6', 'labjack.ljm'):
        try:
            if find_spec(module_name) is not None:
                return True, module_name
        except ModuleNotFoundError:
            continue
    return False, 'not-installed'


def build_probe_rows(rows: Iterable[dict[str, str]]) -> tuple[LabJackProbeRow, ...]:
    return tuple(
        LabJackProbeRow(
            model=row.get('model', 'U6'),
            serial_number=row['serial_number'],
            transport=row.get('transport', 'usb'),
            firmware_version=row.get('firmware_version'),
            hardware_revision=row.get('hardware_revision'),
            connection_label=row.get('connection_label'),
            metadata={key: value for key, value in row.items() if key not in {'model', 'serial_number', 'transport', 'firmware_version', 'hardware_revision', 'connection_label'}},
        )
        for row in rows
    )
