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
class SimulatedLabJackU6Adapter:
    adapter_id: str
    serial_number: str
    transport: str = 'usb'
    analog_values: dict[str, str] = field(default_factory=lambda: {'analog_in_0': '1.250', 'analog_in_1': '2.500', 'analog_in_2': '3.300', 'analog_in_3': '0.875'})
    digital_values: dict[str, str] = field(default_factory=lambda: {'digital_in_0': '0', 'digital_in_1': '1', 'digital_in_2': '0', 'digital_in_3': '1'})
    output_values: dict[str, str] = field(default_factory=lambda: {'analog_out_0': '0.0', 'analog_out_1': '0.0', 'digital_out_0': '0', 'digital_out_1': '1'})
    metadata: Mapping[str, str] = field(default_factory=dict)

    def capability(self) -> AdapterCapability:
        readable = tuple(self._readable_points())
        writable = tuple(self._writable_points())
        return AdapterCapability(
            adapter_id=self.adapter_id,
            adapter_kind=AdapterKind.DEVICE_DRIVER,
            operation_mode=AdapterOperationMode.POLLED,
            readable_points=readable,
            writable_points=writable,
            service_capabilities=('analog_input', 'analog_output', 'digital_io', 'stream_capable', 'timers_available', 'counters_available', 'channel_mapper_ready'),
            is_simulated=True,
            metadata={
                'vendor': 'LabJack',
                'model': 'U6',
                'serial_number': self.serial_number,
                'transport': self.transport,
                'support_pack': 'universaldaq_labjack',
                'channel_family_hint': 'ain,dac,fio',
                'review_surface_hint': 'channel_mapper,stream_setup,device_info',
                **self.metadata,
            },
        )

    def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_id=self.adapter_id,
            state=AdapterHealthState.HEALTHY,
            summary='simulated LabJack U6 adapter healthy',
            metadata={'vendor': 'LabJack', 'model': 'U6', 'serial_number': self.serial_number},
        )

    def poll(self, *, timestamp: int) -> AdapterPollResult:
        ts = as_event_time(timestamp)
        snapshots: list[PointSnapshot] = []
        for point_id, value in sorted(self.analog_values.items()):
            hardware_channel = f"AIN{point_id.rsplit('_', 1)[-1]}"
            snapshots.append(
                PointSnapshot(
                    point=AdapterPointRef(
                        adapter_id=self.adapter_id,
                        point_id=point_id,
                        display_name=hardware_channel,
                        point_class=PointClass.ANALOG,
                        units='V',
                        metadata={
                            'vendor_namespace': 'labjack',
                            'hardware_channel': hardware_channel,
                            'resolution_index': '0',
                        },
                    ),
                    raw_value=value,
                    engineering_value=value,
                    quality=SignalQuality.SIMULATED,
                    source_timestamp=ts,
                    received_timestamp=ts,
                    stale=False,
                    metadata={'vendor_namespace': 'labjack'},
                )
            )
        for point_id, value in sorted(self.digital_values.items()):
            hardware_channel = f"FIO{point_id.rsplit('_', 1)[-1]}"
            snapshots.append(
                PointSnapshot(
                    point=AdapterPointRef(
                        adapter_id=self.adapter_id,
                        point_id=point_id,
                        display_name=hardware_channel,
                        point_class=PointClass.DIGITAL,
                        units=None,
                        metadata={
                            'vendor_namespace': 'labjack',
                            'hardware_channel': hardware_channel,
                        },
                    ),
                    raw_value=value,
                    engineering_value=value,
                    quality=SignalQuality.SIMULATED,
                    source_timestamp=ts,
                    received_timestamp=ts,
                    stale=False,
                    metadata={'vendor_namespace': 'labjack'},
                )
            )
        return AdapterPollResult(
            adapter_id=self.adapter_id,
            polled_at=ts,
            snapshots=tuple(snapshots),
            health=self.health(),
            diagnostics=(
                {
                    'vendor': 'LabJack',
                    'model': 'U6',
                    'serial_number': self.serial_number,
                    'readable_points': len(snapshots),
                    'writable_points': len(self.output_values),
                },
            ),
        )

    def submit_command(self, request: AdapterCommandRequest) -> AdapterCommandResult:
        if request.point_id not in self.output_values:
            return AdapterCommandResult(
                request=request,
                outcome=AdapterCommandOutcome.TARGET_NOT_FOUND,
                reason='unknown U6 writable point',
                health=AdapterHealth(adapter_id=self.adapter_id, state=AdapterHealthState.ERROR, summary='unknown U6 writable point'),
            )
        self.output_values[request.point_id] = request.requested_value
        return AdapterCommandResult(
            request=request,
            outcome=AdapterCommandOutcome.OBSERVED,
            transmitted_at=request.requested_at,
            observed_value=request.requested_value,
            observed_at=request.requested_at,
            health=self.health(),
            metadata={'vendor_namespace': 'labjack'},
        )

    def _readable_points(self) -> list[AdapterPointRef]:
        points: list[AdapterPointRef] = []
        for point_id in sorted(self.analog_values):
            hardware_channel = f"AIN{point_id.rsplit('_', 1)[-1]}"
            points.append(
                AdapterPointRef(
                    adapter_id=self.adapter_id,
                    point_id=point_id,
                    display_name=hardware_channel,
                    point_class=PointClass.ANALOG,
                    units='V',
                    metadata={'vendor_namespace': 'labjack', 'hardware_channel': hardware_channel},
                )
            )
        for point_id in sorted(self.digital_values):
            hardware_channel = f"FIO{point_id.rsplit('_', 1)[-1]}"
            points.append(
                AdapterPointRef(
                    adapter_id=self.adapter_id,
                    point_id=point_id,
                    display_name=hardware_channel,
                    point_class=PointClass.DIGITAL,
                    metadata={'vendor_namespace': 'labjack', 'hardware_channel': hardware_channel},
                )
            )
        return points

    def _writable_points(self) -> list[AdapterPointRef]:
        points: list[AdapterPointRef] = []
        channel_names = {
            'analog_out_0': 'DAC0',
            'analog_out_1': 'DAC1',
            'digital_out_0': 'FIO2',
            'digital_out_1': 'FIO3',
        }
        for point_id in sorted(self.output_values):
            display_name = channel_names[point_id]
            point_class = PointClass.COMMAND if point_id.startswith('digital_out') else PointClass.ANALOG
            points.append(
                AdapterPointRef(
                    adapter_id=self.adapter_id,
                    point_id=point_id,
                    display_name=display_name,
                    point_class=point_class,
                    units='V' if point_id.startswith('analog_out') else None,
                    metadata={'vendor_namespace': 'labjack', 'hardware_channel': display_name},
                )
            )
        return points
