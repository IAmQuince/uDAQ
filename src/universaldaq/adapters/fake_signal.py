from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(slots=True)
class DeterministicWaveformAdapter:
    adapter_id: str
    device_label: str = 'First Signal Demo Device'
    point_id: str = 'demo_wave_0'
    units: str = 'V'
    amplitude: float = 1.5
    offset: float = 2.0
    period_seconds: float = 12.0
    disconnect_after_polls: int | None = None
    stale_after_polls: int | None = None
    _poll_count: int = 0

    def capability(self):
        from universaldaq.adapters import AdapterCapability, AdapterKind, AdapterOperationMode, AdapterPointRef, PointClass
        return AdapterCapability(
            adapter_id=self.adapter_id,
            adapter_kind=AdapterKind.SIMULATED,
            operation_mode=AdapterOperationMode.POLLED,
            readable_points=(
                AdapterPointRef(
                    adapter_id=self.adapter_id,
                    point_id=self.point_id,
                    display_name='Wave 0',
                    point_class=PointClass.ANALOG,
                    units=self.units,
                    metadata={'demo': 'true', 'waveform': 'sine'},
                ),
            ),
            writable_points=(),
            service_capabilities=('first_signal_demo', 'deterministic_waveform'),
            is_simulated=True,
            metadata={
                'display_name': self.device_label,
                'vendor': 'UniversalDAQ',
                'model': 'FirstSignalDemo',
                'transport': 'in_memory',
                'serial_number': 'DEMO-001',
            },
        )

    def _state_label(self) -> str:
        if self.disconnect_after_polls is not None and self._poll_count >= self.disconnect_after_polls:
            return 'disconnected'
        if self.stale_after_polls is not None and self._poll_count >= self.stale_after_polls:
            return 'degraded'
        return 'ready'

    def status_snapshot(self) -> dict[str, object]:
        state_label = self._state_label()
        return {
            'lifecycle_state': state_label,
            'disconnect_count': 1 if state_label == 'disconnected' else 0,
            'reconnect_attempts': 0,
            'recovery_count': 0,
            'startup_open_attempts': 1,
            'startup_open_success_count': 1,
            'startup_open_failure_count': 0,
            'last_disconnect_reason': 'simulated_disconnect' if state_label == 'disconnected' else '',
            'last_disconnect_at': self._poll_count if state_label == 'disconnected' else '',
            'consecutive_failures': 1 if state_label in {'degraded', 'disconnected'} else 0,
            'startup_classification': 'simulated_first_signal_demo',
            'serial_number': 'DEMO-001',
            'recovery_stage': '',
            'last_reconnect_attempt_at': '',
            'last_reconnect_strategy_plan': '',
            'last_reconnect_attempt_trace': '',
            'last_reconnect_failure_at': '',
            'last_backend_reopen_at': '',
        }

    def health(self):
        from universaldaq.adapters import AdapterHealth, AdapterHealthState
        state_label = self._state_label()
        state = {
            'ready': AdapterHealthState.HEALTHY,
            'degraded': AdapterHealthState.DEGRADED,
            'disconnected': AdapterHealthState.DISCONNECTED,
        }[state_label]
        return AdapterHealth(adapter_id=self.adapter_id, state=state, summary=f'first signal demo adapter {state_label}')

    def poll(self, *, timestamp: int):
        from universaldaq.adapters import AdapterPollResult, AdapterPointRef, PointClass, PointSnapshot
        from universaldaq.common import SignalQuality, as_event_time
        self._poll_count += 1
        ts = as_event_time(timestamp)
        state_label = self._state_label()
        if state_label == 'disconnected':
            return AdapterPollResult(
                adapter_id=self.adapter_id,
                polled_at=ts,
                snapshots=(),
                health=self.health(),
                diagnostics=({'adapter_id': self.adapter_id, 'state': state_label, 'poll_count': self._poll_count},),
            )
        phase = 2.0 * math.pi * (float(timestamp) / self.period_seconds)
        value = self.offset + self.amplitude * math.sin(phase)
        rendered = f'{value:.3f}'
        stale = state_label == 'degraded'
        quality = SignalQuality.STALE if stale else SignalQuality.SIMULATED
        snapshot = PointSnapshot(
            point=AdapterPointRef(
                adapter_id=self.adapter_id,
                point_id=self.point_id,
                display_name='Wave 0',
                point_class=PointClass.ANALOG,
                units=self.units,
                metadata={'demo': 'true', 'waveform': 'sine'},
            ),
            raw_value=rendered,
            engineering_value=rendered,
            quality=quality,
            source_timestamp=ts,
            received_timestamp=ts,
            stale=stale,
            metadata={'demo': 'true', 'poll_count': str(self._poll_count)},
        )
        return AdapterPollResult(
            adapter_id=self.adapter_id,
            polled_at=ts,
            snapshots=(snapshot,),
            health=self.health(),
            diagnostics=({'adapter_id': self.adapter_id, 'state': state_label, 'poll_count': self._poll_count, 'value': rendered},),
        )

    def submit_command(self, request):
        from universaldaq.adapters import AdapterCommandOutcome, AdapterCommandResult
        return AdapterCommandResult(
            request=request,
            outcome=AdapterCommandOutcome.DEVICE_REJECTED,
            reason='first signal demo adapter is read-only',
            health=self.health(),
        )
