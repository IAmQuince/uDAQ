from __future__ import annotations

import pytest

from universaldaq.common import SignalQuality, as_event_time
from universaldaq_labjack.models import LabJackProbeRow
from universaldaq_labjack.discovery import LabJackU6DiscoveryProvider
from universaldaq_labjack.real_u6 import RealLabJackU6Adapter, RealU6DirectOpenProbeResult, run_real_u6_direct_open_probe

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-025',
    'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-DEV-002', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-TIME-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'real labjack U6 bounded capability, lifecycle, and poll proof',
}
pytestmark = pytest.mark.contract


class _FakeU6:
    serialNumber = 470001
    firmwareVersion = '1.15'
    hardwareVersion = '2.0'

    def __init__(self, values: tuple[float, float, float] = (1.25, 2.5, 3.75)) -> None:
        self.values = values

    def getCalibrationData(self) -> None:  # pragma: no cover - compatibility hook
        return None

    def getAIN(self, channel: int) -> float:
        return self.values[channel]

    def close(self) -> None:  # pragma: no cover - compatibility hook
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




class _FakeU6Module:
    class U6(_FakeU6):
        def __init__(self, *args, **kwargs):
            serial = kwargs.get('serial')
            first_found = kwargs.get('firstFound', True)
            auto_open = kwargs.get('autoOpen', True)
            super().__init__()
            self.open_calls: list[dict[str, object]] = []
            self.serialNumber = int(serial) if serial is not None else 470001
            if auto_open:
                if serial is not None and not first_found:
                    self.serialNumber = int(serial) if str(serial).isdigit() else 470001
                elif serial is not None:
                    raise RuntimeError('explicit serial requires firstFound=False')

        def open(self, *args, **kwargs):
            self.open_calls.append({'args': args, 'kwargs': kwargs})
            serial = kwargs.get('serial')
            if serial is not None:
                self.serialNumber = int(serial) if str(serial).isdigit() else 470001

    @staticmethod
    def openAllU6():
        return {'470001': _FakeU6()}


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


def test_real_u6_adapter_publishes_three_analog_snapshots():
    adapter = RealLabJackU6Adapter(
        adapter_id='LABJACK-U6-REAL-470001',
        serial_number='470001',
        backend_factory=lambda serial_number: _FakeU6(),
    )

    result = adapter.poll(timestamp=7)

    assert len(result.snapshots) == 3
    assert tuple(snapshot.point.display_name for snapshot in result.snapshots) == ('AIN0', 'AIN1', 'AIN2')
    assert all(snapshot.quality == SignalQuality.GOOD for snapshot in result.snapshots)
    assert result.health is not None and result.health.state.value == 'healthy'
    status = adapter.status_snapshot().as_dict()
    assert status['lifecycle_state'] == 'ready'
    assert status['startup_classification'] == 'real_device_connected'
    assert status['successful_poll_count'] == 1


def test_real_u6_adapter_reports_disconnected_when_backend_init_fails():
    adapter = RealLabJackU6Adapter(
        adapter_id='LABJACK-U6-REAL-470002',
        serial_number='470002',
        backend_factory=lambda serial_number: (_ for _ in ()).throw(RuntimeError('device not found')),
    )

    result = adapter.poll(timestamp=9)

    assert result.snapshots == ()
    assert result.health is not None and result.health.state.value == 'disconnected'
    assert result.health.metadata['startup_classification'] == 'real_device_startup_open_failed'
    assert result.diagnostics[0]['poll_success'] == 'false'
    assert result.diagnostics[0]['lifecycle_state'] == 'disconnected'


def test_real_u6_adapter_releases_backend_and_recovers_after_disconnect():
    factory = _FactorySequence([_FailingReadOnceU6(), _FakeU6(values=(0.5, 0.75, 1.25))])
    adapter = RealLabJackU6Adapter(
        adapter_id='LABJACK-U6-REAL-470003',
        serial_number='470003',
        backend_factory=factory,
    )

    first = adapter.poll(timestamp=11)
    second = adapter.poll(timestamp=12)

    assert first.health is not None and first.health.state.value == 'degraded'
    assert first.diagnostics[0]['backend_connected'] is False
    assert second.health is not None and second.health.state.value == 'healthy'
    assert len(second.snapshots) == 3
    status = adapter.status_snapshot().as_dict()
    assert status['lifecycle_state'] == 'ready'
    assert status['reconnect_attempts'] == 1
    assert status['disconnect_count'] == 1
    assert status['recovery_count'] == 1
    assert status['session_had_disconnect'] is True
    assert status['session_recovered_after_disconnect'] is True
    assert status['disconnect_incident_active'] is False
    assert status['last_disconnect_reason'] == 'real LabJack U6 poll failed: usb read timeout'
    assert status['last_recovery_reason'] == 'real_device_recovered'
    assert status['last_disconnect_at'] == '11'
    assert status['last_recovery_at'] == '12'
    assert status['startup_classification'] == 'real_device_recovered'


def test_discovery_provider_prefers_real_adapter_when_enabled(monkeypatch: pytest.MonkeyPatch):
    provider = LabJackU6DiscoveryProvider(
        probe_rows=(
            LabJackProbeRow(
                model='U6',
                serial_number='470001',
                transport='usb',
                metadata={'hardware_mode': 'real'},
            ),
        ),
        prefer_real_hardware=True,
    )
    monkeypatch.setattr('universaldaq_labjack.discovery.probe_driver_status', lambda: (True, 'u6'))
    devices = provider.discover(timestamp=1)
    assert devices[0].identity.metadata['hardware_mode'] == 'real'
    adapter = provider.activate(devices[0])
    assert isinstance(adapter, RealLabJackU6Adapter)
    assert adapter.prefer_direct_reacquire is True


def test_real_u6_missing_startup_does_not_increment_disconnect_incident_count():
    adapter = RealLabJackU6Adapter(
        adapter_id='LABJACK-U6-REAL-470004',
        serial_number='470004',
        backend_factory=lambda serial_number: (_ for _ in ()).throw(RuntimeError('device not found')),
    )

    result = adapter.poll(timestamp=21)

    assert result.health is not None and result.health.state.value == 'disconnected'
    status = adapter.status_snapshot().as_dict()
    assert status['disconnect_count'] == 0
    assert status['session_had_disconnect'] is False
    assert status['last_disconnect_at'] is None


def test_real_u6_repeated_startup_failures_stay_classified_as_startup_open_failures():
    adapter = RealLabJackU6Adapter(
        adapter_id='LABJACK-U6-REAL-470005',
        serial_number='470005',
        backend_factory=lambda serial_number: (_ for _ in ()).throw(RuntimeError('device not found')),
    )

    adapter.poll(timestamp=31)
    adapter.poll(timestamp=32)
    status = adapter.status_snapshot().as_dict()

    assert status['startup_open_attempts'] == 2
    assert status['startup_open_failure_count'] == 2
    assert status['startup_open_success_count'] == 0
    assert status['has_successful_startup_open'] is False
    assert status['reconnect_attempts'] == 0
    assert status['startup_classification'] == 'real_device_startup_open_failed'


def test_real_u6_reconnect_prefers_verified_probe_path(monkeypatch: pytest.MonkeyPatch):
    factory = _FactorySequence([_FailingReadOnceU6(), RuntimeError('fallback backend factory should not be used')])
    adapter = RealLabJackU6Adapter(
        adapter_id='LABJACK-U6-REAL-470006',
        serial_number='470006',
        backend_factory=factory,
        prefer_direct_reacquire=True,
    )

    def _fake_prime(*, requested_serial_number: str | None = None, perform_ain0_read: bool = True):
        del requested_serial_number, perform_ain0_read
        backend = _FakeU6(values=(0.4, 0.5, 0.6))
        backend.serialNumber = 470006
        probe = RealU6DirectOpenProbeResult(
            requested_serial_number=None,
            resolved_serial_number='470006',
            success=True,
            driver_name='u6',
            open_strategy='constructor_first_found',
            open_stage='first_read',
            calibration_loaded=True,
            close_succeeded=False,
        )
        return backend, probe

    monkeypatch.setattr('universaldaq_labjack.real_u6.prime_real_u6_backend', _fake_prime)

    first = adapter.poll(timestamp=41)
    second = adapter.poll(timestamp=42)

    assert first.health is not None and first.health.state.value == 'degraded'
    assert second.health is not None and second.health.state.value == 'healthy'
    status = adapter.status_snapshot().as_dict()
    assert status['reconnect_attempts'] == 1
    assert status['reconnect_backend_open_success_count'] == 1
    assert status['recovery_count'] == 1
    assert status['post_disconnect_successful_poll_count'] == 1
    assert status['last_open_strategy'] == 'constructor_first_found_verified_serial'


def test_real_u6_reconnect_tries_explicit_verified_probe_before_backend_factory(monkeypatch: pytest.MonkeyPatch):
    factory = _FactorySequence([_FailingReadOnceU6(), RuntimeError('backend factory fallback should not be used')])
    adapter = RealLabJackU6Adapter(
        adapter_id='LABJACK-U6-REAL-470007',
        serial_number='470007',
        backend_factory=factory,
        prefer_direct_reacquire=True,
    )

    calls: list[tuple[str | None, bool]] = []

    def _fake_prime(*, requested_serial_number: str | None = None, perform_ain0_read: bool = True):
        calls.append((requested_serial_number, perform_ain0_read))
        if requested_serial_number is None:
            return None, RealU6DirectOpenProbeResult(
                requested_serial_number=None,
                resolved_serial_number=None,
                success=False,
                driver_name='u6',
                open_strategy='constructor_first_found',
                open_stage='open',
                calibration_loaded=False,
                close_succeeded=False,
                error_type='RuntimeError',
                error_message='device not ready',
            )
        backend = _FakeU6(values=(0.7, 0.8, 0.9))
        backend.serialNumber = 470007
        probe = RealU6DirectOpenProbeResult(
            requested_serial_number=requested_serial_number,
            resolved_serial_number='470007',
            success=True,
            driver_name='u6',
            open_strategy='constructor_explicit_serial',
            open_stage='first_read',
            calibration_loaded=True,
            close_succeeded=False,
        )
        return backend, probe

    monkeypatch.setattr('universaldaq_labjack.real_u6.prime_real_u6_backend', _fake_prime)

    first = adapter.poll(timestamp=51)
    second = adapter.poll(timestamp=52)

    assert first.health is not None and first.health.state.value == 'degraded'
    assert second.health is not None and second.health.state.value == 'healthy'
    assert calls == [(None, True), ('470007', True)]
    status = adapter.status_snapshot().as_dict()
    assert status['reconnect_attempts'] == 1
    assert status['reconnect_backend_open_success_count'] == 1
    assert status['recovery_count'] == 1
    assert status['last_open_strategy'] == 'constructor_explicit_serial_verified_serial'
    assert 'constructor_first_found_verified_serial:failure@open' in (status['last_reconnect_attempt_trace'] or '')
    assert 'constructor_explicit_serial_verified:success@first_read' in (status['last_reconnect_attempt_trace'] or '')


def test_direct_open_probe_uses_explicit_serial_constructor(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr('universaldaq_labjack.real_u6.import_module', lambda name: _FakeU6Module())

    probe = run_real_u6_direct_open_probe(requested_serial_number='470001', perform_ain0_read=True)

    assert probe.success is True
    assert probe.resolved_serial_number == '470001'
    assert probe.open_strategy == 'constructor_explicit_serial'
    assert probe.open_stage == 'first_read'
    assert probe.ain0_value == '1.250000'


def test_direct_open_probe_reports_open_stage_on_failure(monkeypatch: pytest.MonkeyPatch):
    class _FailingModule:
        class U6:
            def __init__(self, *args, **kwargs):
                raise RuntimeError('device not found')

        @staticmethod
        def openAllU6():
            raise RuntimeError('device not found')

    monkeypatch.setattr('universaldaq_labjack.real_u6.import_module', lambda name: _FailingModule())

    probe = run_real_u6_direct_open_probe(requested_serial_number='470001', perform_ain0_read=True)

    assert probe.success is False
    assert probe.open_stage == 'open'
    assert probe.error_type == 'RuntimeError'
    assert 'device not found' in (probe.error_message or '')
