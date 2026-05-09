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
class SimulatedRaspberryPiAdapter:
    adapter_id: str
    model: str
    host_id: str
    transport: str = 'local'
    enable_gpio: bool = True
    host_metrics: dict[str, str] = field(default_factory=lambda: {'host_cpu_temp_c': '48.2', 'host_uptime_s': '3600'})
    gpio_inputs: dict[str, str] = field(default_factory=lambda: {'gpio_in_17': '1', 'gpio_in_27': '0'})
    metadata: Mapping[str, str] = field(default_factory=dict)

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            adapter_id=self.adapter_id,
            adapter_kind=AdapterKind.PROTOCOL_BRIDGE,
            operation_mode=AdapterOperationMode.POLLED,
            readable_points=tuple(self._readable_points()),
            writable_points=(),
            service_capabilities=('host_metric', 'local_platform', 'gpio_input', 'review_ready'),
            is_simulated=True,
            metadata={
                'vendor': 'Raspberry Pi',
                'model': self.model,
                'host_id': self.host_id,
                'transport': self.transport,
                'support_pack': 'universaldaq_rpi',
                'adapter_family': 'local_platform',
                **self.metadata,
            },
        )

    def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_id=self.adapter_id,
            state=AdapterHealthState.HEALTHY,
            summary='simulated Raspberry Pi adapter healthy',
            metadata={'vendor': 'Raspberry Pi', 'model': self.model, 'host_id': self.host_id},
        )

    def poll(self, *, timestamp: int) -> AdapterPollResult:
        ts = as_event_time(timestamp)
        snapshots: list[PointSnapshot] = []
        for point_id, value in sorted(self.host_metrics.items()):
            units = 'degC' if point_id.endswith('_c') else 's'
            display_name = 'CPU Temp' if point_id == 'host_cpu_temp_c' else 'Uptime'
            snapshots.append(
                PointSnapshot(
                    point=AdapterPointRef(
                        adapter_id=self.adapter_id,
                        point_id=point_id,
                        display_name=display_name,
                        point_class=PointClass.STATUS,
                        units=units,
                        metadata={'vendor_namespace': 'raspberry_pi'},
                    ),
                    raw_value=value,
                    engineering_value=value,
                    quality=SignalQuality.SIMULATED,
                    source_timestamp=ts,
                    received_timestamp=ts,
                    stale=False,
                    metadata={'vendor_namespace': 'raspberry_pi'},
                )
            )
        if self.enable_gpio:
            for point_id, value in sorted(self.gpio_inputs.items()):
                channel = point_id.rsplit('_', 1)[-1]
                snapshots.append(
                    PointSnapshot(
                        point=AdapterPointRef(
                            adapter_id=self.adapter_id,
                            point_id=point_id,
                            display_name=f'GPIO {channel}',
                            point_class=PointClass.DIGITAL,
                            metadata={'vendor_namespace': 'raspberry_pi', 'hardware_channel': channel},
                        ),
                        raw_value=value,
                        engineering_value=value,
                        quality=SignalQuality.SIMULATED,
                        source_timestamp=ts,
                        received_timestamp=ts,
                        stale=False,
                        metadata={'vendor_namespace': 'raspberry_pi'},
                    )
                )
        return AdapterPollResult(
            adapter_id=self.adapter_id,
            polled_at=ts,
            snapshots=tuple(snapshots),
            health=self.health(),
            diagnostics=(
                {
                    'vendor': 'Raspberry Pi',
                    'model': self.model,
                    'host_id': self.host_id,
                    'transport': self.transport,
                    'readable_points': len(snapshots),
                },
            ),
        )

    def submit_command(self, request: AdapterCommandRequest) -> AdapterCommandResult:
        return AdapterCommandResult(
            request=request,
            outcome=AdapterCommandOutcome.TARGET_NOT_FOUND,
            reason='simulated Raspberry Pi support pack is read-only in this slice',
            health=AdapterHealth(
                adapter_id=self.adapter_id,
                state=AdapterHealthState.ERROR,
                summary='simulated Raspberry Pi support pack is read-only in this slice',
            ),
            metadata={'vendor_namespace': 'raspberry_pi'},
        )

    def _readable_points(self) -> list[AdapterPointRef]:
        points: list[AdapterPointRef] = []
        for point_id in sorted(self.host_metrics):
            units = 'degC' if point_id.endswith('_c') else 's'
            display_name = 'CPU Temp' if point_id == 'host_cpu_temp_c' else 'Uptime'
            points.append(
                AdapterPointRef(
                    adapter_id=self.adapter_id,
                    point_id=point_id,
                    display_name=display_name,
                    point_class=PointClass.STATUS,
                    units=units,
                    metadata={'vendor_namespace': 'raspberry_pi'},
                )
            )
        if self.enable_gpio:
            for point_id in sorted(self.gpio_inputs):
                channel = point_id.rsplit('_', 1)[-1]
                points.append(
                    AdapterPointRef(
                        adapter_id=self.adapter_id,
                        point_id=point_id,
                        display_name=f'GPIO {channel}',
                        point_class=PointClass.DIGITAL,
                        metadata={'vendor_namespace': 'raspberry_pi', 'hardware_channel': channel},
                    )
                )
        return points
