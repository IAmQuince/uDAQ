from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from universaldaq.adapters import (
    AdapterCapability,
    AdapterCommandOutcome,
    AdapterCommandRequest,
    AdapterCommandResult,
    AdapterHealth,
    AdapterHealthState,
    AdapterKind,
    AdapterOperationMode,
    AdapterPointRef,
    AdapterPollResult,
    PointClass,
    PointSnapshot,
)
from universaldaq.common import SignalQuality, as_event_time


@dataclass(slots=True)
class SimulatedArduinoSerialAdapter:
    adapter_id: str
    board: str
    serial_number: str
    port: str = 'auto'
    transport: str = 'serial'
    analog_values: dict[str, str] = field(default_factory=lambda: {'analog_in_0': '0.812', 'analog_in_1': '1.437'})
    digital_values: dict[str, str] = field(default_factory=lambda: {'digital_in_2': '1', 'digital_in_3': '0'})
    metadata: Mapping[str, str] = field(default_factory=dict)

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            adapter_id=self.adapter_id,
            adapter_kind=AdapterKind.PROTOCOL_BRIDGE,
            operation_mode=AdapterOperationMode.POLLED,
            readable_points=tuple(self._readable_points()),
            writable_points=(),
            service_capabilities=('analog_input', 'digital_input', 'serial_transport', 'microcontroller_protocol', 'review_ready'),
            is_simulated=True,
            metadata={
                'vendor': 'Arduino',
                'board': self.board,
                'serial_number': self.serial_number,
                'transport': self.transport,
                'port': self.port,
                'support_pack': 'universaldaq_arduino',
                'protocol_family': 'microcontroller_serial',
                **self.metadata,
            },
        )

    def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_id=self.adapter_id,
            state=AdapterHealthState.HEALTHY,
            summary='simulated Arduino serial adapter healthy',
            metadata={'vendor': 'Arduino', 'board': self.board, 'serial_number': self.serial_number, 'port': self.port},
        )

    def poll(self, *, timestamp: int) -> AdapterPollResult:
        ts = as_event_time(timestamp)
        snapshots: list[PointSnapshot] = []
        for point_id, value in sorted(self.analog_values.items()):
            label = f"A{point_id.rsplit('_', 1)[-1]}"
            snapshots.append(
                PointSnapshot(
                    point=AdapterPointRef(
                        adapter_id=self.adapter_id,
                        point_id=point_id,
                        display_name=label,
                        point_class=PointClass.ANALOG,
                        units='V',
                        metadata={'vendor_namespace': 'arduino', 'hardware_channel': label},
                    ),
                    raw_value=value,
                    engineering_value=value,
                    quality=SignalQuality.SIMULATED,
                    source_timestamp=ts,
                    received_timestamp=ts,
                    stale=False,
                    metadata={'vendor_namespace': 'arduino'},
                )
            )
        for point_id, value in sorted(self.digital_values.items()):
            label = f"D{point_id.rsplit('_', 1)[-1]}"
            snapshots.append(
                PointSnapshot(
                    point=AdapterPointRef(
                        adapter_id=self.adapter_id,
                        point_id=point_id,
                        display_name=label,
                        point_class=PointClass.DIGITAL,
                        metadata={'vendor_namespace': 'arduino', 'hardware_channel': label},
                    ),
                    raw_value=value,
                    engineering_value=value,
                    quality=SignalQuality.SIMULATED,
                    source_timestamp=ts,
                    received_timestamp=ts,
                    stale=False,
                    metadata={'vendor_namespace': 'arduino'},
                )
            )
        snapshots.append(
            PointSnapshot(
                point=AdapterPointRef(
                    adapter_id=self.adapter_id,
                    point_id='firmware_alive',
                    display_name='Firmware Alive',
                    point_class=PointClass.STATUS,
                    metadata={'vendor_namespace': 'arduino'},
                ),
                raw_value='1',
                engineering_value='1',
                quality=SignalQuality.SIMULATED,
                source_timestamp=ts,
                received_timestamp=ts,
                stale=False,
                metadata={'vendor_namespace': 'arduino'},
            )
        )
        return AdapterPollResult(
            adapter_id=self.adapter_id,
            polled_at=ts,
            snapshots=tuple(snapshots),
            health=self.health(),
            diagnostics=(
                {
                    'vendor': 'Arduino',
                    'board': self.board,
                    'serial_number': self.serial_number,
                    'transport': self.transport,
                    'port': self.port,
                    'readable_points': len(snapshots),
                },
            ),
        )

    def submit_command(self, request: AdapterCommandRequest) -> AdapterCommandResult:
        return AdapterCommandResult(
            request=request,
            outcome=AdapterCommandOutcome.TARGET_NOT_FOUND,
            reason='simulated Arduino serial adapter read-only in this slice',
            health=AdapterHealth(
                adapter_id=self.adapter_id,
                state=AdapterHealthState.ERROR,
                summary='simulated Arduino serial adapter read-only in this slice',
            ),
            metadata={'vendor_namespace': 'arduino'},
        )

    def _readable_points(self) -> list[AdapterPointRef]:
        points: list[AdapterPointRef] = []
        for point_id in sorted(self.analog_values):
            label = f"A{point_id.rsplit('_', 1)[-1]}"
            points.append(
                AdapterPointRef(
                    adapter_id=self.adapter_id,
                    point_id=point_id,
                    display_name=label,
                    point_class=PointClass.ANALOG,
                    units='V',
                    metadata={'vendor_namespace': 'arduino', 'hardware_channel': label},
                )
            )
        for point_id in sorted(self.digital_values):
            label = f"D{point_id.rsplit('_', 1)[-1]}"
            points.append(
                AdapterPointRef(
                    adapter_id=self.adapter_id,
                    point_id=point_id,
                    display_name=label,
                    point_class=PointClass.DIGITAL,
                    metadata={'vendor_namespace': 'arduino', 'hardware_channel': label},
                )
            )
        points.append(
            AdapterPointRef(
                adapter_id=self.adapter_id,
                point_id='firmware_alive',
                display_name='Firmware Alive',
                point_class=PointClass.STATUS,
                metadata={'vendor_namespace': 'arduino'},
            )
        )
        return points
