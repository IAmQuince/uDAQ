from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from universaldaq.adapters import DeviceIdentity, DeviceSupportTier, DiscoveredDevice, WorkbenchDescriptor
from universaldaq.adapters.contracts import AdapterContract

from .models import ArduinoProbeRow
from .simulated_serial import SimulatedArduinoSerialAdapter


@dataclass(slots=True)
class ArduinoSerialDiscoveryProvider:
    provider_id: str = 'arduino_serial_support'
    probe_rows: tuple[ArduinoProbeRow, ...] = field(default_factory=tuple)

    def discover(self, *, timestamp: int) -> tuple[DiscoveredDevice, ...]:
        del timestamp
        discovered: list[DiscoveredDevice] = []
        for row in self.probe_rows:
            identity = DeviceIdentity(
                stable_key=f'arduino::{row.board.lower()}::{row.serial_number}',
                display_name=f'Arduino {row.board} ({row.serial_number})',
                vendor='Arduino',
                model=row.board,
                serial_number=row.serial_number,
                transport=row.transport,
                firmware_version=row.firmware_version,
                metadata={'port': row.port, **row.metadata},
            )
            discovered.append(
                DiscoveredDevice(
                    device_key=f'{self.provider_id}:{row.serial_number}',
                    identity=identity,
                    provider_id=self.provider_id,
                    support_tier=DeviceSupportTier.PROTOCOL_FAMILY,
                    capability_labels=('analog_input', 'digital_input', 'serial_transport', 'microcontroller_protocol', 'review_ready'),
                    bound_adapter_id=None,
                    workbenches=self.workbenches_from_row(row),
                    metadata={
                        'enhancement_pack': 'universaldaq_arduino',
                        'transport_hint': 'serial',
                        'review_surface_hint': 'serial_console,pin_map,firmware_info',
                    },
                )
            )
        return tuple(discovered)

    def activate(self, device: DiscoveredDevice) -> AdapterContract | None:
        serial_number = device.identity.serial_number
        if serial_number is None:
            return None
        board = device.identity.model or 'Uno'
        port = device.identity.metadata.get('port', 'auto')
        return SimulatedArduinoSerialAdapter(
            adapter_id=f'ARDUINO-{board.upper()}-{serial_number}',
            board=board,
            serial_number=serial_number,
            port=port,
            transport=device.identity.transport or 'serial',
            metadata={'activation_source': self.provider_id},
        )

    def workbenches(self, device: DiscoveredDevice) -> tuple[WorkbenchDescriptor, ...]:
        return device.workbenches

    def workbenches_from_row(self, row: ArduinoProbeRow) -> tuple[WorkbenchDescriptor, ...]:
        return (
            WorkbenchDescriptor(
                workbench_id='arduino_serial_console',
                display_name='Arduino Serial Console',
                activation_reason=f'arduino serial endpoint detected on {row.port}',
                metadata={'vendor_namespace': 'arduino'},
            ),
            WorkbenchDescriptor(
                workbench_id='arduino_pin_map',
                display_name='Arduino Pin Map',
                activation_reason='microcontroller serial protocol inventory available',
                metadata={'vendor_namespace': 'arduino'},
            ),
            WorkbenchDescriptor(
                workbench_id='arduino_firmware_info',
                display_name='Arduino Firmware Info',
                activation_reason='firmware identity and serial protocol diagnostics available',
                metadata={'vendor_namespace': 'arduino'},
            ),
        )


def build_probe_rows(rows: Iterable[dict[str, str]]) -> tuple[ArduinoProbeRow, ...]:
    return tuple(
        ArduinoProbeRow(
            board=row.get('board', 'Uno'),
            serial_number=row['serial_number'],
            port=row.get('port', 'auto'),
            transport=row.get('transport', 'serial'),
            firmware_version=row.get('firmware_version'),
            connection_label=row.get('connection_label'),
            metadata={
                key: value
                for key, value in row.items()
                if key not in {'board', 'serial_number', 'port', 'transport', 'firmware_version', 'connection_label'}
            },
        )
        for row in rows
    )
