from __future__ import annotations

import pytest

from tools.dev._u6_live_support import bootstrap_controller, build_services, install_labjack_support_pack, prepare_u6_live_value_slice
from universaldaq.common import as_event_time
from universaldaq_labjack.real_u6 import RealLabJackU6Adapter

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-021',
    'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-TIME-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'same-run U6 recovery emits reconnect-stage runtime events and returns to live after disconnect',
}
pytestmark = pytest.mark.integration


class _FakeU6:
    serialNumber = 470011
    firmwareVersion = '1.15'
    hardwareVersion = '2.0'

    def __init__(self, values: tuple[float, float, float] = (1.0, 2.0, 3.0)) -> None:
        self.values = values

    def getCalibrationData(self) -> None:
        return None

    def getAIN(self, channel: int) -> float:
        return self.values[channel]

    def close(self) -> None:
        return None


class _AlwaysFailingReadU6(_FakeU6):
    def getAIN(self, channel: int) -> float:
        del channel
        raise RuntimeError('usb read timeout')


class _FactorySequence:
    def __init__(self, backends: list[object]) -> None:
        self.backends = backends
        self.calls = 0

    def __call__(self, serial_number: str | None) -> object:
        del serial_number
        index = min(self.calls, len(self.backends) - 1)
        self.calls += 1
        backend = self.backends[index]
        if isinstance(backend, Exception):
            raise backend
        return backend


def test_u6_recovery_pipeline_emits_stage_events_and_returns_to_live():
    services = build_services()
    install_labjack_support_pack(services, real_hardware=False, simulated_serial_number='470211')
    controller = bootstrap_controller(services=services, profile_id='PROF-U6-RECOVERY-PIPE', actor_id='u6-recovery')
    prepared = prepare_u6_live_value_slice(controller, timestamp_start=3)
    active_adapter_id = prepared.active_adapter_id
    assert active_adapter_id is not None

    factory = _FactorySequence([
        _AlwaysFailingReadU6(),
        RuntimeError('device not found'),
        _FakeU6(values=(0.25, 0.5, 0.75)),
    ])
    services.adapters.adapters[active_adapter_id] = RealLabJackU6Adapter(
        adapter_id=active_adapter_id,
        serial_number='470211',
        backend_factory=factory,
    )

    controller.poll_adapters(timestamp=as_event_time(100))
    controller.poll_adapters(timestamp=as_event_time(101))
    controller.poll_adapters(timestamp=as_event_time(102))

    bundle = controller.lifecycle_review_bundle()
    event_types = [row.get('event_type') for row in bundle.get('recent_runtime_event_rows', ())]
    assert 'device_disconnect_incident_opened' in event_types
    assert 'device_degraded' in event_types
    assert 'device_reconnect_attempt_started' in event_types
    assert 'device_reconnect_attempt_started' in event_types
    assert 'backend_reopen_succeeded' in event_types
    assert 'post_disconnect_poll_resumed' in event_types
    assert 'adapter_rebind_succeeded' in event_types
    assert 'device_recovered' in event_types

    status = bundle['transition_trace'][-1]
    assert status['phase_after'] == 'live'

    assert bundle['lifecycle_summary']['phase'] == 'live'
    active_status = getattr(controller.services.adapters.adapters[active_adapter_id], 'status_snapshot')().as_dict()
    assert active_status['session_recovered_after_disconnect'] is True
    assert active_status['reconnect_backend_open_success_count'] == 1
    assert active_status['post_disconnect_successful_poll_count'] == 1
