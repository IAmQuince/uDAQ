from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, slots=True, kw_only=True)
class LabJackProbeRow:
    model: str
    serial_number: str
    transport: str = 'usb'
    firmware_version: str | None = None
    hardware_revision: str | None = None
    connection_label: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class LabJackAdapterStatusSnapshot:
    adapter_id: str
    hardware_mode: str
    serial_number: str | None
    lifecycle_state: str
    startup_classification: str
    backend_connected: bool
    reconnect_attempts: int = 0
    startup_open_attempts: int = 0
    startup_open_success_count: int = 0
    startup_open_failure_count: int = 0
    has_successful_startup_open: bool = False
    last_open_strategy: str | None = None
    last_open_stage: str | None = None
    last_reconnect_strategy_plan: str | None = None
    last_reconnect_attempt_trace: str | None = None
    disconnect_count: int = 0
    recovery_count: int = 0
    reconnect_backend_open_success_count: int = 0
    reconnect_backend_open_failure_count: int = 0
    post_disconnect_successful_poll_count: int = 0
    successful_poll_count: int = 0
    consecutive_failures: int = 0
    disconnect_incident_active: bool = False
    session_had_disconnect: bool = False
    session_recovered_after_disconnect: bool = False
    recovery_stage: str = 'idle'
    last_failure_reason: str | None = None
    last_disconnect_reason: str | None = None
    last_recovery_reason: str | None = None
    last_close_reason: str | None = None
    last_success_at: str | None = None
    last_failure_at: str | None = None
    last_disconnect_at: str | None = None
    last_recovery_at: str | None = None
    last_transition_at: str | None = None
    last_reconnect_attempt_at: str | None = None
    last_backend_reopen_at: str | None = None
    last_reconnect_failure_at: str | None = None
    last_recovery_failure_stage: str | None = None
    last_recovery_failure_reason: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            'adapter_id': self.adapter_id,
            'hardware_mode': self.hardware_mode,
            'serial_number': self.serial_number,
            'lifecycle_state': self.lifecycle_state,
            'startup_classification': self.startup_classification,
            'backend_connected': self.backend_connected,
            'reconnect_attempts': self.reconnect_attempts,
            'startup_open_attempts': self.startup_open_attempts,
            'startup_open_success_count': self.startup_open_success_count,
            'startup_open_failure_count': self.startup_open_failure_count,
            'has_successful_startup_open': self.has_successful_startup_open,
            'last_open_strategy': self.last_open_strategy,
            'last_open_stage': self.last_open_stage,
            'last_reconnect_strategy_plan': self.last_reconnect_strategy_plan,
            'last_reconnect_attempt_trace': self.last_reconnect_attempt_trace,
            'disconnect_count': self.disconnect_count,
            'recovery_count': self.recovery_count,
            'reconnect_backend_open_success_count': self.reconnect_backend_open_success_count,
            'reconnect_backend_open_failure_count': self.reconnect_backend_open_failure_count,
            'post_disconnect_successful_poll_count': self.post_disconnect_successful_poll_count,
            'successful_poll_count': self.successful_poll_count,
            'consecutive_failures': self.consecutive_failures,
            'disconnect_incident_active': self.disconnect_incident_active,
            'session_had_disconnect': self.session_had_disconnect,
            'session_recovered_after_disconnect': self.session_recovered_after_disconnect,
            'recovery_stage': self.recovery_stage,
            'last_failure_reason': self.last_failure_reason,
            'last_disconnect_reason': self.last_disconnect_reason,
            'last_recovery_reason': self.last_recovery_reason,
            'last_close_reason': self.last_close_reason,
            'last_success_at': self.last_success_at,
            'last_failure_at': self.last_failure_at,
            'last_disconnect_at': self.last_disconnect_at,
            'last_recovery_at': self.last_recovery_at,
            'last_transition_at': self.last_transition_at,
            'last_reconnect_attempt_at': self.last_reconnect_attempt_at,
            'last_backend_reopen_at': self.last_backend_reopen_at,
            'last_reconnect_failure_at': self.last_reconnect_failure_at,
            'last_recovery_failure_stage': self.last_recovery_failure_stage,
            'last_recovery_failure_reason': self.last_recovery_failure_reason,
        }
