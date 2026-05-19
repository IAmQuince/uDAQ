from __future__ import annotations

import pytest

from universaldaq.adapters.services import AdapterManagerService
from universaldaq_labjack.real_u6 import RealLabJackU6Adapter

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-026',
    'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-TIME-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'disconnected active adapter can be polled explicitly for bounded recovery attempts',
}
pytestmark = pytest.mark.contract


class _FakeU6:
    serialNumber = 470010
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


class _FailingReadOnceU6(_FakeU6):
    def __init__(self) -> None:
        super().__init__()
        self.failed = False

    def getAIN(self, channel: int) -> float:
        if not self.failed:
            self.failed = True
            raise RuntimeError('usb read timeout')
        return super().getAIN(channel)


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


def test_disconnected_adapter_can_be_polled_for_recovery_attempts():
    service = AdapterManagerService()
    factory = _FactorySequence([_FailingReadOnceU6(), _FakeU6(values=(0.5, 0.75, 1.25))])
    adapter = RealLabJackU6Adapter(
        adapter_id='LABJACK-U6-REAL-470010',
        serial_number='470010',
        backend_factory=factory,
    )
    service.register(adapter)

    first = service.poll_adapter(adapter_id=adapter.adapter_id, timestamp=11)
    assert first is not None and first.health is not None and first.health.state.value == 'degraded'

    service.mark_adapter_disconnected(adapter_id=adapter.adapter_id)
    blocked = service.poll_adapter(adapter_id=adapter.adapter_id, timestamp=12)
    assert blocked is None

    recovered = service.poll_adapter(adapter_id=adapter.adapter_id, timestamp=13, include_disconnected=True)
    assert recovered is not None and recovered.health is not None and recovered.health.state.value == 'healthy'
    assert len(recovered.snapshots) == 3

    status = adapter.status_snapshot().as_dict()
    assert status['disconnect_count'] == 1
    assert status['reconnect_attempts'] == 1
    assert status['reconnect_backend_open_success_count'] == 1
    assert status['post_disconnect_successful_poll_count'] == 1
    assert status['recovery_count'] == 1
    assert status['session_recovered_after_disconnect'] is True
