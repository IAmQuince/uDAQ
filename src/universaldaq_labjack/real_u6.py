from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from time import sleep
from typing import Callable, Mapping

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

from .models import LabJackAdapterStatusSnapshot

BackendFactory = Callable[[str | None], object]


class RealU6OpenError(RuntimeError):
    def __init__(self, *, stage: str, strategy: str, serial_number: str | None, detail_rows: tuple[Mapping[str, object], ...], original: Exception) -> None:
        self.stage = stage
        self.strategy = strategy
        self.serial_number = serial_number
        self.detail_rows = detail_rows
        self.original = original
        super().__init__(f"{stage} via {strategy}: {original}")


class ReconnectAcquisitionError(RuntimeError):
    def __init__(self, *, strategy: str, stage: str, serial_number: str | None, message: str, detail_rows: tuple[Mapping[str, object], ...] = ()) -> None:
        self.strategy = strategy
        self.stage = stage
        self.serial_number = serial_number
        self.detail_rows = detail_rows
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class RealU6DirectOpenProbeResult:
    requested_serial_number: str | None
    resolved_serial_number: str | None
    success: bool
    driver_name: str
    open_strategy: str | None = None
    open_stage: str | None = None
    firmware_version: str | None = None
    hardware_revision: str | None = None
    ain0_value: str | None = None
    calibration_loaded: bool = False
    close_succeeded: bool = False
    error_type: str | None = None
    error_message: str | None = None
    detail_rows: tuple[Mapping[str, object], ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            'requested_serial_number': self.requested_serial_number,
            'resolved_serial_number': self.resolved_serial_number,
            'success': self.success,
            'driver_name': self.driver_name,
            'open_strategy': self.open_strategy,
            'open_stage': self.open_stage,
            'firmware_version': self.firmware_version,
            'hardware_revision': self.hardware_revision,
            'ain0_value': self.ain0_value,
            'calibration_loaded': self.calibration_loaded,
            'close_succeeded': self.close_succeeded,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'detail_rows': [dict(row) for row in self.detail_rows],
        }

    def probe_row(self) -> dict[str, str] | None:
        if not self.success or self.resolved_serial_number in {None, '', 'unknown'}:
            return None
        return {
            'model': 'U6',
            'serial_number': self.resolved_serial_number,
            'transport': 'usb',
            'firmware_version': self.firmware_version,
            'hardware_revision': self.hardware_revision,
            'connection_label': 'direct-open-probed',
            'hardware_mode': 'real',
            'driver_name': self.driver_name,
            'open_strategy': '' if self.open_strategy is None else self.open_strategy,
            'open_stage': '' if self.open_stage is None else self.open_stage,
        }


def _normalized_serial_arg(serial_number: str | None) -> int | str | None:
    if serial_number in {None, '', 'AUTO'}:
        return None
    serial_text = str(serial_number).strip()
    if not serial_text:
        return None
    return int(serial_text) if serial_text.isdigit() else serial_text


def _match_opened_backend(opened: Mapping[object, object], serial_arg: int | str | None) -> object | None:
    if serial_arg is None:
        for candidate in opened.values():
            return candidate
        return None
    serial_text = str(serial_arg)
    candidate = opened.get(serial_arg)
    if candidate is not None:
        return candidate
    candidate = opened.get(serial_text)
    if candidate is not None:
        return candidate
    if isinstance(serial_arg, str) and serial_arg.isdigit():
        candidate = opened.get(int(serial_arg))
        if candidate is not None:
            return candidate
    for key, value in opened.items():
        if str(key) == serial_text:
            return value
        serial_number = getattr(value, 'serialNumber', None)
        if serial_number is not None and str(serial_number) == serial_text:
            return value
    return None


def _close_backend_quietly(device: object | None) -> bool:
    closer = None if device is None else getattr(device, 'close', None)
    if callable(closer):
        try:
            closer()
            return True
        except Exception:
            return False
    return True


def _attempt_documented_constructor_open(driver, serial_arg: int | str | None) -> object:
    if serial_arg is None:
        return driver()
    return driver(firstFound=False, serial=serial_arg)


def _attempt_explicit_open(driver, serial_arg: int | str | None) -> object:
    device = driver(autoOpen=False)
    opener = getattr(device, 'open', None)
    if not callable(opener):
        raise RuntimeError('u6.U6 instance does not expose open()')
    if serial_arg is None:
        opener()
    else:
        opener(firstFound=False, serial=serial_arg)
    return device


def _attempt_open_all(module, serial_arg: int | str | None) -> object:
    open_all = getattr(module, 'openAllU6', None)
    if not callable(open_all):
        raise RuntimeError('u6.openAllU6 unavailable')
    opened = open_all()
    target = _match_opened_backend(opened, serial_arg)
    if target is None:
        for candidate in opened.values():
            _close_backend_quietly(candidate)
        raise RuntimeError('requested serial not returned by openAllU6')
    for candidate in opened.values():
        if candidate is target:
            continue
        _close_backend_quietly(candidate)
    return target


def _calibrate_backend(device: object) -> None:
    calibrate = getattr(device, 'getCalibrationData', None)
    if callable(calibrate):
        calibrate()


def _open_backend_with_diagnostics(serial_number: str | None) -> tuple[object, dict[str, object]]:
    module = import_module('u6')
    driver = getattr(module, 'U6')
    serial_arg = _normalized_serial_arg(serial_number)
    detail_rows: list[Mapping[str, object]] = []
    last_exc: Exception | None = None
    last_stage = 'open'
    last_strategy = 'unattempted'
    strategies: list[tuple[str, Callable[[], object]]] = []
    if serial_arg is None:
        strategies.append(('constructor_first_found', lambda: _attempt_documented_constructor_open(driver, serial_arg)))
        strategies.append(('explicit_open_first_found', lambda: _attempt_explicit_open(driver, serial_arg)))
        strategies.append(('open_all_first_found', lambda: _attempt_open_all(module, serial_arg)))
    else:
        strategies.append(('constructor_explicit_serial', lambda: _attempt_documented_constructor_open(driver, serial_arg)))
        strategies.append(('explicit_open_explicit_serial', lambda: _attempt_explicit_open(driver, serial_arg)))
        strategies.append(('open_all_match_serial', lambda: _attempt_open_all(module, serial_arg)))
    for strategy_name, opener in strategies:
        last_strategy = strategy_name
        device = None
        try:
            device = opener()
            detail_rows.append({'strategy': strategy_name, 'stage': 'open', 'status': 'success', 'serial_arg': None if serial_arg is None else str(serial_arg)})
            try:
                _calibrate_backend(device)
                detail_rows.append({'strategy': strategy_name, 'stage': 'calibration', 'status': 'success'})
            except Exception as exc:
                last_exc = exc
                last_stage = 'calibration'
                detail_rows.append({'strategy': strategy_name, 'stage': 'calibration', 'status': 'failure', 'error_type': type(exc).__name__, 'error_message': str(exc)})
                _close_backend_quietly(device)
                continue
            return device, {
                'driver_name': 'u6',
                'serial_arg': None if serial_arg is None else str(serial_arg),
                'open_strategy': strategy_name,
                'open_stage': 'calibration',
                'detail_rows': tuple(detail_rows),
            }
        except Exception as exc:
            last_exc = exc
            last_stage = 'open'
            detail_rows.append({'strategy': strategy_name, 'stage': 'open', 'status': 'failure', 'serial_arg': None if serial_arg is None else str(serial_arg), 'error_type': type(exc).__name__, 'error_message': str(exc)})
            _close_backend_quietly(device)
    if last_exc is None:
        last_exc = RuntimeError('unknown backend open failure')
    raise RealU6OpenError(stage=last_stage, strategy=last_strategy, serial_number=serial_number, detail_rows=tuple(detail_rows), original=last_exc)


def _default_backend_factory(serial_number: str | None) -> object:
    backend, _ = _open_backend_with_diagnostics(serial_number)
    return backend




def prime_real_u6_backend(*, requested_serial_number: str | None = None, perform_ain0_read: bool = True) -> tuple[object | None, RealU6DirectOpenProbeResult]:
    try:
        backend, diagnostics = _open_backend_with_diagnostics(requested_serial_number)
    except RealU6OpenError as exc:
        return None, RealU6DirectOpenProbeResult(
            requested_serial_number=requested_serial_number,
            resolved_serial_number=None,
            success=False,
            driver_name='u6',
            open_strategy=exc.strategy,
            open_stage=exc.stage,
            error_type=type(exc.original).__name__,
            error_message=str(exc.original),
            detail_rows=tuple(exc.detail_rows),
        )
    ain0_value = None
    try:
        if perform_ain0_read:
            ain_reader = getattr(backend, 'getAIN', None)
            if callable(ain_reader):
                ain0_value = f"{float(ain_reader(0)):.6f}"
        resolved_serial_number = str(getattr(backend, 'serialNumber', requested_serial_number or 'unknown'))
        probe = RealU6DirectOpenProbeResult(
            requested_serial_number=requested_serial_number,
            resolved_serial_number=resolved_serial_number,
            success=requested_serial_number in {None, '', 'AUTO'} or resolved_serial_number == requested_serial_number,
            driver_name='u6',
            open_strategy=diagnostics.get('open_strategy'),
            open_stage='first_read' if perform_ain0_read else diagnostics.get('open_stage'),
            firmware_version=None if getattr(backend, 'firmwareVersion', None) is None else str(getattr(backend, 'firmwareVersion')),
            hardware_revision=None if getattr(backend, 'hardwareVersion', None) is None else str(getattr(backend, 'hardwareVersion')),
            ain0_value=ain0_value,
            calibration_loaded=True,
            close_succeeded=False,
            error_type=None if requested_serial_number in {None, '', 'AUTO'} or resolved_serial_number == requested_serial_number else 'IdentityMismatch',
            error_message=None if requested_serial_number in {None, '', 'AUTO'} or resolved_serial_number == requested_serial_number else f'requested serial {requested_serial_number} but backend reported {resolved_serial_number}',
            detail_rows=tuple(diagnostics.get('detail_rows', ())),
        )
        if probe.success:
            return backend, probe
        _close_backend_quietly(backend)
        return None, probe
    except Exception as exc:
        resolved_serial_number = None if getattr(backend, 'serialNumber', None) is None else str(getattr(backend, 'serialNumber'))
        probe = RealU6DirectOpenProbeResult(
            requested_serial_number=requested_serial_number,
            resolved_serial_number=resolved_serial_number,
            success=False,
            driver_name='u6',
            open_strategy=diagnostics.get('open_strategy'),
            open_stage='first_read',
            firmware_version=None if getattr(backend, 'firmwareVersion', None) is None else str(getattr(backend, 'firmwareVersion')),
            hardware_revision=None if getattr(backend, 'hardwareVersion', None) is None else str(getattr(backend, 'hardwareVersion')),
            ain0_value=ain0_value,
            calibration_loaded=True,
            close_succeeded=False,
            error_type=type(exc).__name__,
            error_message=str(exc),
            detail_rows=tuple(diagnostics.get('detail_rows', ())),
        )
        _close_backend_quietly(backend)
        return None, probe


def build_primed_backend_factory(primed_backend: object | None, *, fallback_factory: BackendFactory = _default_backend_factory) -> BackendFactory:
    primed_serial = None if primed_backend is None else str(getattr(primed_backend, 'serialNumber', ''))
    consumed = False

    def _factory(serial_number: str | None) -> object:
        nonlocal consumed, primed_backend
        requested = _normalized_serial_arg(serial_number)
        if not consumed and primed_backend is not None:
            requested_text = None if requested is None else str(requested)
            if requested_text in {None, '', primed_serial}:
                consumed = True
                backend = primed_backend
                primed_backend = None
                return backend
        return fallback_factory(serial_number)

    return _factory

def run_real_u6_direct_open_probe(*, requested_serial_number: str | None = None, perform_ain0_read: bool = True) -> RealU6DirectOpenProbeResult:
    backend, probe = prime_real_u6_backend(requested_serial_number=requested_serial_number, perform_ain0_read=perform_ain0_read)
    if backend is None:
        return probe
    close_succeeded = _close_backend_quietly(backend)
    payload = probe.as_dict()
    payload['close_succeeded'] = close_succeeded
    return RealU6DirectOpenProbeResult(**payload)


def probe_real_u6_row(*, requested_serial_number: str | None = None) -> dict[str, str] | None:
    probe = run_real_u6_direct_open_probe(requested_serial_number=requested_serial_number, perform_ain0_read=False)
    return probe.probe_row()


def _prime_reconnect_backend(
    *,
    expected_serial_number: str | None,
    requested_serial_number: str | None,
    strategy_name: str,
) -> tuple[object, dict[str, object]]:
    backend, probe = prime_real_u6_backend(requested_serial_number=requested_serial_number, perform_ain0_read=True)
    if backend is None:
        raise ReconnectAcquisitionError(
            strategy=strategy_name,
            stage=probe.open_stage or 'open',
            serial_number=expected_serial_number,
            message=probe.error_message or 'reconnect direct-open probe failed',
            detail_rows=tuple(probe.detail_rows),
        )
    resolved = probe.resolved_serial_number
    if expected_serial_number not in {None, '', 'AUTO'} and resolved != expected_serial_number:
        _close_backend_quietly(backend)
        raise ReconnectAcquisitionError(
            strategy=strategy_name,
            stage='identity_check',
            serial_number=expected_serial_number,
            message=f'expected serial {expected_serial_number} but reconnect probe opened {resolved}',
            detail_rows=tuple(probe.detail_rows),
        )
    strategy = probe.open_strategy or strategy_name
    return backend, {
        'open_strategy': f'{strategy}_verified_serial',
        'open_stage': probe.open_stage or 'open',
        'detail_rows': tuple(probe.detail_rows),
    }


@dataclass(slots=True)
class RealLabJackU6Adapter:
    adapter_id: str
    serial_number: str | None
    transport: str = 'usb'
    metadata: Mapping[str, str] = field(default_factory=dict)
    backend_factory: BackendFactory = _default_backend_factory
    prefer_direct_reacquire: bool = False
    _backend: object | None = field(default=None, init=False, repr=False)
    _lifecycle_state: str = field(default='configured', init=False, repr=False)
    _startup_classification: str = field(default='not_attempted', init=False, repr=False)
    _last_failure_reason: str | None = field(default=None, init=False, repr=False)
    _last_disconnect_reason: str | None = field(default=None, init=False, repr=False)
    _last_recovery_reason: str | None = field(default=None, init=False, repr=False)
    _last_close_reason: str | None = field(default='never_opened', init=False, repr=False)
    _consecutive_failures: int = field(default=0, init=False, repr=False)
    _reconnect_attempts: int = field(default=0, init=False, repr=False)
    _disconnect_count: int = field(default=0, init=False, repr=False)
    _recovery_count: int = field(default=0, init=False, repr=False)
    _reconnect_backend_open_success_count: int = field(default=0, init=False, repr=False)
    _reconnect_backend_open_failure_count: int = field(default=0, init=False, repr=False)
    _post_disconnect_successful_poll_count: int = field(default=0, init=False, repr=False)
    _successful_polls: int = field(default=0, init=False, repr=False)
    _startup_attempted: bool = field(default=False, init=False, repr=False)
    _startup_open_attempts: int = field(default=0, init=False, repr=False)
    _startup_open_success_count: int = field(default=0, init=False, repr=False)
    _startup_open_failure_count: int = field(default=0, init=False, repr=False)
    _has_successful_startup_open: bool = field(default=False, init=False, repr=False)
    _last_open_strategy: str | None = field(default=None, init=False, repr=False)
    _last_open_stage: str | None = field(default=None, init=False, repr=False)
    _last_reconnect_strategy_plan: str | None = field(default=None, init=False, repr=False)
    _last_reconnect_attempt_trace: str | None = field(default=None, init=False, repr=False)
    _disconnect_incident_active: bool = field(default=False, init=False, repr=False)
    _session_had_disconnect: bool = field(default=False, init=False, repr=False)
    _session_recovered_after_disconnect: bool = field(default=False, init=False, repr=False)
    _recovery_stage: str = field(default='idle', init=False, repr=False)
    _last_success_at: int | None = field(default=None, init=False, repr=False)
    _last_failure_at: int | None = field(default=None, init=False, repr=False)
    _last_disconnect_at: int | None = field(default=None, init=False, repr=False)
    _last_recovery_at: int | None = field(default=None, init=False, repr=False)
    _last_transition_at: int | None = field(default=None, init=False, repr=False)
    _last_reconnect_attempt_at: int | None = field(default=None, init=False, repr=False)
    _last_backend_reopen_at: int | None = field(default=None, init=False, repr=False)
    _last_reconnect_failure_at: int | None = field(default=None, init=False, repr=False)
    _last_recovery_failure_stage: str | None = field(default=None, init=False, repr=False)
    _last_recovery_failure_reason: str | None = field(default=None, init=False, repr=False)
    startup_open_retry_limit: int = 3
    startup_open_retry_delay_seconds: float = 0.4
    reconnect_open_retry_limit: int = 3
    reconnect_open_retry_delay_seconds: float = 0.35

    def capability(self) -> AdapterCapability:
        readable = tuple(
            AdapterPointRef(
                adapter_id=self.adapter_id,
                point_id=f'analog_in_{channel}',
                display_name=f'AIN{channel}',
                point_class=PointClass.ANALOG,
                units='V',
                metadata={
                    'vendor_namespace': 'labjack',
                    'hardware_channel': f'AIN{channel}',
                    'hardware_mode': 'real',
                },
            )
            for channel in range(3)
        )
        return AdapterCapability(
            adapter_id=self.adapter_id,
            adapter_kind=AdapterKind.DEVICE_DRIVER,
            operation_mode=AdapterOperationMode.POLLED,
            readable_points=readable,
            writable_points=(),
            service_capabilities=('analog_input', 'channel_mapper_ready', 'device_info', 'diagnostics_bundle_ready'),
            is_simulated=False,
            metadata={
                'vendor': 'LabJack',
                'model': 'U6',
                'serial_number': '' if self.serial_number is None else self.serial_number,
                'transport': self.transport,
                'support_pack': 'universaldaq_labjack',
                'hardware_mode': 'real',
                **self.metadata,
            },
        )

    def _transition(self, state: str, *, timestamp: int | None, startup_classification: str | None = None) -> None:
        self._lifecycle_state = state
        self._last_transition_at = timestamp
        if startup_classification is not None:
            self._startup_classification = startup_classification

    def _event_time_or_none(self, value: int | None) -> str | None:
        return None if value is None else str(as_event_time(value))

    def _begin_disconnect_incident(self, *, timestamp: int, reason: str) -> None:
        self._last_failure_at = timestamp
        self._last_failure_reason = reason
        self._last_disconnect_reason = reason
        self._last_disconnect_at = timestamp
        self._session_had_disconnect = True
        self._recovery_stage = 'incident_open'
        self._last_recovery_failure_stage = 'device_loss_detected'
        self._last_recovery_failure_reason = reason
        if not self._disconnect_incident_active:
            self._disconnect_incident_active = True
            self._disconnect_count += 1

    def _mark_recovered(self, *, timestamp: int, classification: str) -> None:
        if self._disconnect_incident_active:
            self._disconnect_incident_active = False
            self._session_recovered_after_disconnect = True
            self._recovery_count += 1
            self._last_recovery_at = timestamp
            self._last_recovery_reason = classification
            self._recovery_stage = 'recovered'
            self._last_recovery_failure_stage = None
            self._last_recovery_failure_reason = None

    def status_snapshot(self) -> LabJackAdapterStatusSnapshot:
        return LabJackAdapterStatusSnapshot(
            adapter_id=self.adapter_id,
            hardware_mode='real',
            serial_number=self.serial_number,
            lifecycle_state=self._lifecycle_state,
            startup_classification=self._startup_classification,
            backend_connected=self._backend is not None,
            reconnect_attempts=self._reconnect_attempts,
            startup_open_attempts=self._startup_open_attempts,
            startup_open_success_count=self._startup_open_success_count,
            startup_open_failure_count=self._startup_open_failure_count,
            has_successful_startup_open=self._has_successful_startup_open,
            last_open_strategy=self._last_open_strategy,
            last_open_stage=self._last_open_stage,
            last_reconnect_strategy_plan=self._last_reconnect_strategy_plan,
            last_reconnect_attempt_trace=self._last_reconnect_attempt_trace,
            disconnect_count=self._disconnect_count,
            recovery_count=self._recovery_count,
            reconnect_backend_open_success_count=self._reconnect_backend_open_success_count,
            reconnect_backend_open_failure_count=self._reconnect_backend_open_failure_count,
            post_disconnect_successful_poll_count=self._post_disconnect_successful_poll_count,
            successful_poll_count=self._successful_polls,
            consecutive_failures=self._consecutive_failures,
            disconnect_incident_active=self._disconnect_incident_active,
            session_had_disconnect=self._session_had_disconnect,
            session_recovered_after_disconnect=self._session_recovered_after_disconnect,
            recovery_stage=self._recovery_stage,
            last_failure_reason=self._last_failure_reason,
            last_disconnect_reason=self._last_disconnect_reason,
            last_recovery_reason=self._last_recovery_reason,
            last_close_reason=self._last_close_reason,
            last_success_at=self._event_time_or_none(self._last_success_at),
            last_failure_at=self._event_time_or_none(self._last_failure_at),
            last_disconnect_at=self._event_time_or_none(self._last_disconnect_at),
            last_recovery_at=self._event_time_or_none(self._last_recovery_at),
            last_transition_at=self._event_time_or_none(self._last_transition_at),
            last_reconnect_attempt_at=self._event_time_or_none(self._last_reconnect_attempt_at),
            last_backend_reopen_at=self._event_time_or_none(self._last_backend_reopen_at),
            last_reconnect_failure_at=self._event_time_or_none(self._last_reconnect_failure_at),
            last_recovery_failure_stage=self._last_recovery_failure_stage,
            last_recovery_failure_reason=self._last_recovery_failure_reason,
        )

    def _health_metadata(self) -> dict[str, str]:
        snapshot = self.status_snapshot().as_dict()
        base = {
            'vendor': 'LabJack',
            'model': 'U6',
            'serial_number': '' if self.serial_number is None else self.serial_number,
        }
        for key, value in snapshot.items():
            base[key] = '' if value is None else str(value).lower() if isinstance(value, bool) else str(value)
        return base

    def _health_state(self) -> AdapterHealthState:
        if self._lifecycle_state == 'ready':
            return AdapterHealthState.HEALTHY
        if self._lifecycle_state == 'degraded':
            return AdapterHealthState.DEGRADED
        if self._lifecycle_state == 'disconnected':
            return AdapterHealthState.DISCONNECTED
        if self._lifecycle_state == 'faulted':
            return AdapterHealthState.ERROR
        return AdapterHealthState.UNKNOWN

    def _health_summary(self) -> str:
        if self._lifecycle_state == 'ready':
            if self._session_recovered_after_disconnect and self._last_recovery_at is not None:
                return 'real LabJack U6 adapter healthy after recovery'
            return 'real LabJack U6 adapter healthy'
        if self._lifecycle_state == 'disconnected':
            return 'real LabJack U6 adapter disconnected'
        if self._lifecycle_state == 'degraded':
            return 'real LabJack U6 adapter degraded'
        if self._lifecycle_state == 'stopped':
            return 'real LabJack U6 adapter stopped'
        if self._last_failure_reason:
            return self._last_failure_reason
        return 'real LabJack U6 adapter ready'

    def _release_backend(self, *, reason: str) -> None:
        closer = None if self._backend is None else getattr(self._backend, 'close', None)
        if callable(closer):
            try:
                closer()
            except Exception:
                if self._last_failure_reason is None:
                    self._last_failure_reason = 'real LabJack U6 backend close raised during recovery'
        self._backend = None
        self._last_close_reason = reason

    def _open_backend_for_attempt(self, *, is_reconnect: bool) -> tuple[object, str, str, str | None]:
        if is_reconnect and self.prefer_direct_reacquire:
            strategy_attempts = (
                (
                    'constructor_first_found_verified_serial',
                    lambda: _prime_reconnect_backend(
                        expected_serial_number=self.serial_number,
                        requested_serial_number=None,
                        strategy_name='constructor_first_found_verified_serial',
                    ),
                ),
                (
                    'constructor_explicit_serial_verified',
                    lambda: _prime_reconnect_backend(
                        expected_serial_number=self.serial_number,
                        requested_serial_number=self.serial_number,
                        strategy_name='constructor_explicit_serial_verified',
                    ),
                ),
            )
            self._last_reconnect_strategy_plan = ' -> '.join(name for name, _ in strategy_attempts) + ' -> backend_factory'
            trace_rows: list[str] = []
            for strategy_name, opener in strategy_attempts:
                trace_rows.append(f'{strategy_name}:attempted')
                try:
                    backend, diagnostics = opener()
                    strategy = str(diagnostics.get('open_strategy') or strategy_name)
                    stage = str(diagnostics.get('open_stage') or 'open')
                    trace_rows.append(f'{strategy_name}:success@{stage}')
                    return backend, strategy, stage, ' | '.join(trace_rows)
                except ReconnectAcquisitionError as exc:
                    self._last_open_strategy = exc.strategy
                    self._last_open_stage = exc.stage
                    trace_rows.append(f'{strategy_name}:failure@{exc.stage}:{exc}')
            trace_rows.append('backend_factory:entered')
            backend = self.backend_factory(self.serial_number)
            return backend, 'backend_factory', 'opened', ' | '.join(trace_rows)
        backend = self.backend_factory(self.serial_number)
        return backend, 'backend_factory', 'opened', None

    def _ensure_backend(self, *, timestamp: int) -> object:
        if self._backend is not None:
            return self._backend
        had_prior_success = self._has_successful_startup_open or self._successful_polls > 0 or self._session_had_disconnect
        is_reconnect = had_prior_success or self._disconnect_incident_active
        is_startup_open = not is_reconnect
        self._startup_attempted = True
        if is_reconnect:
            self._last_reconnect_attempt_trace = None
        else:
            self._last_reconnect_strategy_plan = None
            self._last_reconnect_attempt_trace = None
        if is_reconnect:
            self._reconnect_attempts += 1
            self._last_reconnect_attempt_at = timestamp
            self._recovery_stage = 'attempt_started'
        else:
            self._startup_open_attempts += 1
            self._recovery_stage = 'startup_open_attempted'
        self._transition('initializing', timestamp=timestamp)
        open_attempts = max(1, self.reconnect_open_retry_limit if is_reconnect else self.startup_open_retry_limit)
        retry_delay_seconds = self.reconnect_open_retry_delay_seconds if is_reconnect else self.startup_open_retry_delay_seconds
        backend = None
        open_error = None
        for attempt_index in range(open_attempts):
            try:
                backend, strategy, stage, attempt_trace = self._open_backend_for_attempt(is_reconnect=is_reconnect)
                self._last_open_strategy = strategy
                self._last_open_stage = stage
                if is_reconnect:
                    self._last_reconnect_attempt_trace = attempt_trace
                break
            except Exception as exc:
                open_error = exc
                if isinstance(exc, RealU6OpenError):
                    self._last_open_strategy = exc.strategy
                    self._last_open_stage = exc.stage
                elif isinstance(exc, ReconnectAcquisitionError):
                    self._last_open_strategy = exc.strategy
                    self._last_open_stage = exc.stage
                else:
                    self._last_open_strategy = 'backend_factory'
                    self._last_open_stage = 'open'
                if is_reconnect and self._last_reconnect_attempt_trace is None and self._last_reconnect_strategy_plan is not None:
                    self._last_reconnect_attempt_trace = 'backend_factory:failure-before-trace'
                if attempt_index < open_attempts - 1 and retry_delay_seconds > 0:
                    sleep(retry_delay_seconds)
        if backend is None:
            exc = open_error if open_error is not None else RuntimeError('unknown backend open failure')
            stage = self._last_open_stage or 'open'
            strategy = self._last_open_strategy or 'backend_factory'
            reason = f'real LabJack U6 backend init failed [{stage}/{strategy}]: {exc}'
            self._last_failure_reason = reason
            self._last_failure_at = timestamp
            self._consecutive_failures += 1
            self._last_recovery_failure_reason = reason
            if is_reconnect:
                self._last_reconnect_failure_at = timestamp
                self._last_recovery_failure_stage = 'backend_reopen_failed'
                self._reconnect_backend_open_failure_count += 1
                self._recovery_stage = 'backend_reopen_failed'
                classification = 'real_device_reconnect_failed'
            else:
                self._startup_open_failure_count += 1
                self._last_recovery_failure_stage = 'startup_open_failed'
                self._recovery_stage = 'startup_open_failed'
                classification = 'real_device_startup_open_failed'
            if self._disconnect_incident_active:
                self._last_disconnect_reason = reason
            self._transition('disconnected', timestamp=timestamp, startup_classification=classification)
            raise exc
        self._backend = backend
        self._last_close_reason = 'backend_open'
        self._consecutive_failures = 0
        self._last_failure_reason = None
        self._last_failure_at = None
        if is_startup_open:
            self._startup_open_success_count += 1
            self._has_successful_startup_open = True
        if is_reconnect:
            self._reconnect_backend_open_success_count += 1
            self._last_backend_reopen_at = timestamp
            self._recovery_stage = 'backend_reopen_succeeded'
            if self._last_reconnect_attempt_trace is None:
                self._last_reconnect_attempt_trace = f'{self._last_open_strategy or "backend_factory"}:success@{self._last_open_stage or "open"}'
        if self._disconnect_incident_active:
            classification = 'real_device_backend_reopened'
            self._transition('degraded', timestamp=timestamp, startup_classification=classification)
            return backend
        if is_reconnect:
            classification = 'real_device_reconnected'
        elif self._startup_open_failure_count:
            classification = 'real_device_connected_after_startup_retry'
        else:
            classification = 'real_device_connected'
        self._transition('ready', timestamp=timestamp, startup_classification=classification)
        return backend

    def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_id=self.adapter_id,
            state=self._health_state(),
            summary=self._health_summary(),
            last_success_at=None if self._last_success_at is None else as_event_time(self._last_success_at),
            last_failure_at=None if self._last_failure_at is None else as_event_time(self._last_failure_at),
            consecutive_failures=self._consecutive_failures,
            metadata=self._health_metadata(),
        )

    def _diagnostic_row(self, *, timestamp: int, poll_success: bool) -> dict[str, object]:
        return {
            'vendor': 'LabJack',
            'model': 'U6',
            'serial_number': None if self.serial_number is None else self.serial_number,
            'hardware_mode': 'real',
            'readable_points': 3,
            'poll_success': str(bool(poll_success)).lower(),
            'lifecycle_state': self._lifecycle_state,
            'startup_classification': self._startup_classification,
            'reconnect_attempts': self._reconnect_attempts,
            'startup_open_attempts': self._startup_open_attempts,
            'startup_open_success_count': self._startup_open_success_count,
            'startup_open_failure_count': self._startup_open_failure_count,
            'has_successful_startup_open': self._has_successful_startup_open,
            'last_open_strategy': self._last_open_strategy,
            'last_open_stage': self._last_open_stage,
            'last_reconnect_strategy_plan': self._last_reconnect_strategy_plan,
            'last_reconnect_attempt_trace': self._last_reconnect_attempt_trace,
            'disconnect_count': self._disconnect_count,
            'recovery_count': self._recovery_count,
            'reconnect_backend_open_success_count': self._reconnect_backend_open_success_count,
            'reconnect_backend_open_failure_count': self._reconnect_backend_open_failure_count,
            'post_disconnect_successful_poll_count': self._post_disconnect_successful_poll_count,
            'successful_poll_count': self._successful_polls,
            'consecutive_failures': self._consecutive_failures,
            'disconnect_incident_active': self._disconnect_incident_active,
            'session_had_disconnect': self._session_had_disconnect,
            'session_recovered_after_disconnect': self._session_recovered_after_disconnect,
            'recovery_stage': self._recovery_stage,
            'backend_connected': self._backend is not None,
            'last_close_reason': self._last_close_reason,
            'last_failure_reason': self._last_failure_reason,
            'last_disconnect_reason': self._last_disconnect_reason,
            'last_recovery_reason': self._last_recovery_reason,
            'last_success_at': self._event_time_or_none(self._last_success_at),
            'last_failure_at': self._event_time_or_none(self._last_failure_at),
            'last_disconnect_at': self._event_time_or_none(self._last_disconnect_at),
            'last_recovery_at': self._event_time_or_none(self._last_recovery_at),
            'last_transition_at': self._event_time_or_none(self._last_transition_at),
            'last_reconnect_attempt_at': self._event_time_or_none(self._last_reconnect_attempt_at),
            'last_backend_reopen_at': self._event_time_or_none(self._last_backend_reopen_at),
            'last_reconnect_failure_at': self._event_time_or_none(self._last_reconnect_failure_at),
            'last_recovery_failure_stage': self._last_recovery_failure_stage,
            'last_recovery_failure_reason': self._last_recovery_failure_reason,
            'polled_at': str(as_event_time(timestamp)),
        }

    def poll(self, *, timestamp: int) -> AdapterPollResult:
        ts = as_event_time(timestamp)
        snapshots: list[PointSnapshot] = []
        try:
            backend = self._ensure_backend(timestamp=timestamp)
        except Exception:
            return AdapterPollResult(
                adapter_id=self.adapter_id,
                polled_at=ts,
                snapshots=(),
                health=self.health(),
                diagnostics=(self._diagnostic_row(timestamp=timestamp, poll_success=False),),
            )

        try:
            for channel in range(3):
                value = float(getattr(backend, 'getAIN')(channel))
                formatted = f'{value:.6f}'
                snapshots.append(
                    PointSnapshot(
                        point=AdapterPointRef(
                            adapter_id=self.adapter_id,
                            point_id=f'analog_in_{channel}',
                            display_name=f'AIN{channel}',
                            point_class=PointClass.ANALOG,
                            units='V',
                            metadata={
                                'vendor_namespace': 'labjack',
                                'hardware_channel': f'AIN{channel}',
                                'hardware_mode': 'real',
                            },
                        ),
                        raw_value=formatted,
                        engineering_value=formatted,
                        quality=SignalQuality.GOOD,
                        source_timestamp=ts,
                        received_timestamp=ts,
                        stale=False,
                        metadata={'vendor_namespace': 'labjack', 'hardware_mode': 'real'},
                    )
                )
            had_disconnect_incident = self._disconnect_incident_active
            self._last_success_at = timestamp
            self._consecutive_failures = 0
            self._successful_polls += 1
            if had_disconnect_incident:
                self._post_disconnect_successful_poll_count += 1
                classification = 'real_device_recovered'
                self._mark_recovered(timestamp=timestamp, classification=classification)
            else:
                classification = self._startup_classification
            self._transition('ready', timestamp=timestamp, startup_classification=classification)
            health = self.health()
        except Exception as exc:
            reason = f'real LabJack U6 poll failed: {exc}'
            self._begin_disconnect_incident(timestamp=timestamp, reason=reason)
            self._consecutive_failures += 1
            self._last_recovery_failure_stage = 'post_disconnect_poll_failed' if self._reconnect_attempts else 'runtime_read_failed'
            self._last_recovery_failure_reason = reason
            self._recovery_stage = 'post_disconnect_poll_failed' if self._reconnect_backend_open_success_count else 'incident_open'
            if self._consecutive_failures == 1:
                self._transition('degraded', timestamp=timestamp, startup_classification='runtime_read_failed')
                self._release_backend(reason='runtime_read_failed')
            else:
                self._transition('disconnected', timestamp=timestamp, startup_classification='runtime_device_lost')
                self._release_backend(reason='runtime_device_lost')
            health = self.health()
        return AdapterPollResult(
            adapter_id=self.adapter_id,
            polled_at=ts,
            snapshots=tuple(snapshots),
            health=health,
            diagnostics=(self._diagnostic_row(timestamp=timestamp, poll_success=bool(snapshots)),),
        )

    def submit_command(self, request: AdapterCommandRequest) -> AdapterCommandResult:
        return AdapterCommandResult(
            request=request,
            outcome=AdapterCommandOutcome.TARGET_NOT_FOUND,
            reason='real U6 narrow proof does not expose writable points',
            health=self.health(),
            metadata={'vendor_namespace': 'labjack', 'hardware_mode': 'real'},
        )

    def close(self) -> None:
        faulted = False
        if self._backend is not None:
            closer = getattr(self._backend, 'close', None)
            if callable(closer):
                try:
                    closer()
                    self._last_close_reason = 'close_called'
                except Exception as exc:
                    self._last_failure_reason = f'real LabJack U6 close failed: {exc}'
                    faulted = True
                    self._transition('faulted', timestamp=self._last_transition_at, startup_classification='shutdown_failed')
                finally:
                    self._backend = None
        if not faulted:
            self._transition('stopped', timestamp=self._last_transition_at)
