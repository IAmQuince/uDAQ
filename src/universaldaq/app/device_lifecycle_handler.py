from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import TYPE_CHECKING

from universaldaq.adapters import AdapterPollResult, DeviceLifecyclePhase, DiscoveredDevice
from universaldaq.common import EventTime, SignalId
from universaldaq.signals import BindingPolicy

from .first_signal import FirstSignalPlanner

if TYPE_CHECKING:
    from .controller import ShellActionResult, ShellController


@dataclass(slots=True)
class ShellDeviceLifecycleHandler:
    controller: 'ShellController'

    def _active_adapter_status_snapshot(self) -> dict[str, object] | None:
        adapter_id = self.controller.session.ui_session.active_adapter_id
        if adapter_id is None:
            return None
        adapter = self.controller.services.adapters.adapters.get(adapter_id)
        if adapter is None:
            return None
        status_snapshot = getattr(adapter, 'status_snapshot', None)
        if not callable(status_snapshot):
            return None
        snapshot = status_snapshot()
        if hasattr(snapshot, 'as_dict'):
            return snapshot.as_dict()
        if hasattr(snapshot, '__dataclass_fields__'):
            return asdict(snapshot)
        return dict(snapshot)

    def _first_signal_binding_reason(self, summary) -> str:
        if summary is None:
            return 'no first-signal binding available'
        if getattr(summary, 'auto_bound', False):
            return 'auto-bound first readable point for quick-start usability slice'
        return 'existing device binding retained'

    def _record_runtime_transition_event(
        self,
        *,
        timestamp: EventTime,
        before_status: dict[str, object] | None,
        after_status: dict[str, object] | None,
    ) -> None:
        if after_status is None:
            return
        before = {} if before_status is None else before_status
        before_state = before.get('lifecycle_state')
        after_state = after_status.get('lifecycle_state')
        adapter_id = self.controller.session.ui_session.active_adapter_id

        def _record(event_type: str, attributes: dict[str, object]) -> None:
            self.controller.services.runtime_quality.record_state_event(
                timestamp=timestamp,
                event_type=event_type,
                attributes={'adapter_id': '' if adapter_id is None else adapter_id, **attributes},
            )

        before_disconnect_count = int(before.get('disconnect_count', 0) or 0)
        after_disconnect_count = int(after_status.get('disconnect_count', 0) or 0)
        before_startup_open_attempts = int(before.get('startup_open_attempts', 0) or 0)
        after_startup_open_attempts = int(after_status.get('startup_open_attempts', 0) or 0)
        before_startup_open_successes = int(before.get('startup_open_success_count', 0) or 0)
        after_startup_open_successes = int(after_status.get('startup_open_success_count', 0) or 0)
        before_startup_open_failures = int(before.get('startup_open_failure_count', 0) or 0)
        after_startup_open_failures = int(after_status.get('startup_open_failure_count', 0) or 0)
        before_reconnect_attempts = int(before.get('reconnect_attempts', 0) or 0)
        after_reconnect_attempts = int(after_status.get('reconnect_attempts', 0) or 0)
        before_backend_reopen_successes = int(before.get('reconnect_backend_open_success_count', 0) or 0)
        after_backend_reopen_successes = int(after_status.get('reconnect_backend_open_success_count', 0) or 0)
        before_backend_reopen_failures = int(before.get('reconnect_backend_open_failure_count', 0) or 0)
        after_backend_reopen_failures = int(after_status.get('reconnect_backend_open_failure_count', 0) or 0)
        before_post_disconnect_polls = int(before.get('post_disconnect_successful_poll_count', 0) or 0)
        after_post_disconnect_polls = int(after_status.get('post_disconnect_successful_poll_count', 0) or 0)

        if after_startup_open_attempts > before_startup_open_attempts:
            _record(
                'device_startup_open_attempted',
                {
                    'attempt_count': after_startup_open_attempts,
                    'lifecycle_state': after_status.get('lifecycle_state', ''),
                    'startup_classification': after_status.get('startup_classification', ''),
                    'serial_number': after_status.get('serial_number', ''),
                },
            )
        if after_startup_open_failures > before_startup_open_failures:
            _record(
                'device_startup_open_failed',
                {
                    'failure_count': after_startup_open_failures,
                    'lifecycle_state': after_status.get('lifecycle_state', ''),
                    'startup_classification': after_status.get('startup_classification', ''),
                    'last_failure_at': after_status.get('last_failure_at', ''),
                    'last_failure_reason': after_status.get('last_failure_reason', ''),
                },
            )
        if after_startup_open_successes > before_startup_open_successes:
            _record(
                'device_startup_open_succeeded',
                {
                    'success_count': after_startup_open_successes,
                    'lifecycle_state': after_status.get('lifecycle_state', ''),
                    'startup_classification': after_status.get('startup_classification', ''),
                    'has_successful_startup_open': after_status.get('has_successful_startup_open', False),
                },
            )
        if after_disconnect_count > before_disconnect_count:
            _record(
                'device_disconnect_incident_opened',
                {
                    'disconnect_count': after_disconnect_count,
                    'lifecycle_state': after_status.get('lifecycle_state', ''),
                    'startup_classification': after_status.get('startup_classification', ''),
                    'last_disconnect_at': after_status.get('last_disconnect_at', ''),
                    'last_disconnect_reason': after_status.get('last_disconnect_reason', ''),
                },
            )
        if after_reconnect_attempts > before_reconnect_attempts:
            _record(
                'device_reconnect_attempt_started',
                {
                    'attempt_count': after_reconnect_attempts,
                    'disconnect_count': after_status.get('disconnect_count', 0),
                    'recovery_stage': after_status.get('recovery_stage', ''),
                    'last_reconnect_attempt_at': after_status.get('last_reconnect_attempt_at', ''),
                    'last_reconnect_strategy_plan': after_status.get('last_reconnect_strategy_plan', ''),
                    'last_reconnect_attempt_trace': after_status.get('last_reconnect_attempt_trace', ''),
                },
            )
        if after_backend_reopen_failures > before_backend_reopen_failures:
            _record(
                'backend_reopen_failed',
                {
                    'failure_count': after_backend_reopen_failures,
                    'recovery_stage': after_status.get('recovery_stage', ''),
                    'last_reconnect_failure_at': after_status.get('last_reconnect_failure_at', ''),
                    'last_recovery_failure_stage': after_status.get('last_recovery_failure_stage', ''),
                    'last_recovery_failure_reason': after_status.get('last_recovery_failure_reason', ''),
                    'last_open_strategy': after_status.get('last_open_strategy', ''),
                    'last_open_stage': after_status.get('last_open_stage', ''),
                    'last_reconnect_strategy_plan': after_status.get('last_reconnect_strategy_plan', ''),
                    'last_reconnect_attempt_trace': after_status.get('last_reconnect_attempt_trace', ''),
                },
            )
        if after_backend_reopen_successes > before_backend_reopen_successes:
            _record(
                'backend_reopen_succeeded',
                {
                    'success_count': after_backend_reopen_successes,
                    'recovery_stage': after_status.get('recovery_stage', ''),
                    'last_backend_reopen_at': after_status.get('last_backend_reopen_at', ''),
                },
            )
        if after_post_disconnect_polls > before_post_disconnect_polls:
            _record(
                'post_disconnect_poll_resumed',
                {
                    'post_disconnect_successful_poll_count': after_post_disconnect_polls,
                    'last_recovery_at': after_status.get('last_recovery_at', ''),
                    'last_recovery_reason': after_status.get('last_recovery_reason', ''),
                },
            )

        if (
            before_state == after_state
            and after_startup_open_attempts == before_startup_open_attempts
            and after_startup_open_successes == before_startup_open_successes
            and after_startup_open_failures == before_startup_open_failures
            and after_reconnect_attempts == before_reconnect_attempts
            and after_backend_reopen_successes == before_backend_reopen_successes
            and after_backend_reopen_failures == before_backend_reopen_failures
            and after_post_disconnect_polls == before_post_disconnect_polls
        ):
            return
        if after_state == 'degraded' and before_state != 'degraded':
            _record(
                'device_degraded',
                {
                    'lifecycle_state': after_state,
                    'startup_classification': after_status.get('startup_classification', ''),
                    'disconnect_count': after_status.get('disconnect_count', 0),
                    'consecutive_failures': after_status.get('consecutive_failures', 0),
                },
            )
        if after_state == 'disconnected' and before_state != 'disconnected':
            _record(
                'device_disconnected',
                {
                    'lifecycle_state': after_state,
                    'startup_classification': after_status.get('startup_classification', ''),
                    'disconnect_count': after_status.get('disconnect_count', 0),
                    'reconnect_attempts': after_status.get('reconnect_attempts', 0),
                    'last_disconnect_at': after_status.get('last_disconnect_at', ''),
                    'last_disconnect_reason': after_status.get('last_disconnect_reason', ''),
                },
            )
        if after_state == 'ready' and before_state in {'degraded', 'disconnected'}:
            _record(
                'adapter_rebind_succeeded',
                {
                    'lifecycle_state': after_state,
                    'startup_classification': after_status.get('startup_classification', ''),
                    'recovery_stage': after_status.get('recovery_stage', ''),
                    'disconnect_count': after_status.get('disconnect_count', 0),
                    'recovery_count': after_status.get('recovery_count', 0),
                },
            )
            _record(
                'device_recovered',
                {
                    'lifecycle_state': after_state,
                    'startup_classification': after_status.get('startup_classification', ''),
                    'disconnect_count': after_status.get('disconnect_count', 0),
                    'recovery_count': after_status.get('recovery_count', 0),
                    'last_recovery_at': after_status.get('last_recovery_at', ''),
                    'last_recovery_reason': after_status.get('last_recovery_reason', ''),
                },
            )

    def _normalize_phase_for_adapter_status(
        self,
        *,
        lifecycle_summary,
        adapter_status: dict[str, object] | None,
    ):
        onboarding_mode = self.controller.session.ui_session.onboarding_mode
        current_phase = self.controller.session.ui_session.device_lifecycle_phase
        if adapter_status is None:
            if onboarding_mode == 'quick_start' or current_phase == DeviceLifecyclePhase.LIVE:
                return replace(lifecycle_summary, phase=DeviceLifecyclePhase.LIVE.value)
            return lifecycle_summary
        state = adapter_status.get('lifecycle_state')
        if state is None:
            if onboarding_mode == 'quick_start' or current_phase == DeviceLifecyclePhase.LIVE:
                return replace(lifecycle_summary, phase=DeviceLifecyclePhase.LIVE.value)
            return lifecycle_summary
        adapter_id = self.controller.session.ui_session.active_adapter_id
        if state == 'disconnected':
            if adapter_id is not None:
                self.controller.services.adapters.mark_adapter_disconnected(adapter_id=adapter_id)
            return replace(lifecycle_summary, phase=DeviceLifecyclePhase.DISCONNECTED.value)
        if state == 'degraded':
            if adapter_id is not None:
                self.controller.services.adapters.reconnect_adapter(adapter_id=adapter_id)
            return replace(lifecycle_summary, phase=DeviceLifecyclePhase.DEGRADED.value)
        if state == 'ready':
            if adapter_id is not None:
                self.controller.services.adapters.reconnect_adapter(adapter_id=adapter_id)
            if onboarding_mode == 'quick_start' or current_phase == DeviceLifecyclePhase.LIVE:
                return replace(lifecycle_summary, phase=DeviceLifecyclePhase.LIVE.value)
            if current_phase == DeviceLifecyclePhase.DISCONNECTED:
                return replace(lifecycle_summary, phase=DeviceLifecyclePhase.READY_TO_CONFIGURE.value)
        return lifecycle_summary

    def discover_devices(self, *, timestamp: EventTime) -> tuple[DiscoveredDevice, ...]:
        workflow = self.controller._lifecycle().discover_devices(timestamp=timestamp)
        phase = DeviceLifecyclePhase.NO_DEVICE if not workflow.devices else DeviceLifecyclePhase.DISCOVERED
        ui_session = self.controller._ui_session_with_lifecycle_update(
            phase=phase,
            detected_devices=tuple(workflow.devices),
            lifecycle_summary=workflow.lifecycle_summary,
        )
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='DISCOVERY',
            summary='device discovery completed',
            attributes={'device_count': str(len(workflow.devices))},
        )
        self.controller._commit_with_ui_session('discover_devices', ui_session=ui_session, evidence=evidence)
        return workflow.devices

    def select_detected_device(self, *, device_key: str, timestamp: EventTime) -> 'ShellActionResult':
        workflow = self.controller._lifecycle().activate_detected_device(
            device_key=device_key,
            timestamp=timestamp,
            current_profile_id=str(self.controller.session.profile_snapshot.profile_id),
        )
        first_signal_summary = FirstSignalPlanner.build_summary(
            services=self.controller.services,
            device=workflow.device,
            previous_summary=self.controller.session.ui_session.first_signal_summary,
            lifecycle_phase=workflow.lifecycle_phase,
        )
        ui_session = self.controller._ui_session_with_lifecycle_update(
            phase=workflow.lifecycle_phase,
            active_device=workflow.device,
            active_adapter_id=workflow.adapter_id,
            onboarding_mode=None,
            known_device_restore_offer=workflow.known_device_restore_offer,
            available_workbenches=workflow.workbenches,
            lifecycle_summary=workflow.lifecycle_summary,
            binding_review_summary=workflow.binding_review_summary,
            variable_health_summary=workflow.variable_health_summary,
            reconciliation_summary=workflow.reconciliation_summary,
            workbench_review_state=workflow.workbench_review_state,
            first_signal_summary=first_signal_summary,
        )
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='DEVICESELECT',
            summary='detected device selected',
            attributes={
                'device_key': workflow.device.device_key,
                'support_tier': workflow.device.support_tier.value,
                'adapter_id': '' if workflow.adapter_id is None else workflow.adapter_id,
                'projected_points': str(workflow.lifecycle_summary.projected_point_count),
            },
        )
        return self.controller._commit_with_ui_session('select_detected_device', ui_session=ui_session, evidence=evidence)

    def begin_quick_start(self, *, timestamp: EventTime) -> 'ShellActionResult':
        active_device = self.controller.session.ui_session.active_device
        if active_device is None:
            return self.controller._commit('begin_quick_start', self.controller.session)
        ui_session = self.controller.session.ui_session.with_device_phase(phase=DeviceLifecyclePhase.QUICK_START_READY, onboarding_mode='quick_start')
        binding_decision = FirstSignalPlanner.ensure_default_binding(
            services=self.controller.services,
            device=active_device,
            adapter_id=self.controller.session.ui_session.active_adapter_id,
        )
        workflow = self.controller._lifecycle().poll_active_adapter(
            ui_session=ui_session,
            timestamp=timestamp,
            desired_phase=DeviceLifecyclePhase.LIVE,
        )
        first_signal_summary = FirstSignalPlanner.build_summary(
            services=self.controller.services,
            device=active_device,
            previous_summary=self.controller.session.ui_session.first_signal_summary,
            preferred_signal_id=binding_decision.signal_id,
            lifecycle_phase=DeviceLifecyclePhase.LIVE,
            auto_bound=binding_decision.auto_bound,
        )
        ui_session = ui_session.with_device_phase(phase=DeviceLifecyclePhase.LIVE, onboarding_mode='quick_start').with_review_state(
            lifecycle_summary=workflow.lifecycle_summary,
            binding_review_summary=workflow.binding_review_summary,
            variable_health_summary=workflow.variable_health_summary,
            reconciliation_summary=workflow.reconciliation_summary,
            first_signal_summary=first_signal_summary,
        )
        self.controller._sync_alarm_lifecycles_from_service()
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='QUICKSTART',
            summary='quick start initiated for active device',
            attributes={
                'device_key': active_device.device_key,
                'phase': DeviceLifecyclePhase.LIVE.value,
                'published_signals': str(workflow.lifecycle_summary.published_signal_count),
                'first_signal_binding_reason': self._first_signal_binding_reason(first_signal_summary),
            },
        )
        return self.controller._commit_with_ui_session('begin_quick_start', ui_session=ui_session, evidence=evidence)

    def enter_advanced_setup(self, *, timestamp: EventTime) -> 'ShellActionResult':
        active_device = self.controller.session.ui_session.active_device
        if active_device is None:
            return self.controller._commit('enter_advanced_setup', self.controller.session)
        lifecycle_summary = self.controller.session.ui_session.lifecycle_summary
        if lifecycle_summary is not None:
            lifecycle_summary = replace(lifecycle_summary, phase=DeviceLifecyclePhase.ADVANCED_SETUP.value, last_transition='enter_advanced_setup')
        ui_session = self.controller.session.ui_session.with_device_phase(phase=DeviceLifecyclePhase.ADVANCED_SETUP, onboarding_mode='advanced_setup').with_review_state(
            lifecycle_summary=lifecycle_summary,
        )
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='ADVSETUP',
            summary='advanced setup entered for active device',
            attributes={'device_key': active_device.device_key},
        )
        return self.controller._commit('enter_advanced_setup', self.controller.session.with_ui_session(ui_session).append_shell_evidence(evidence))

    def remember_active_device(self, *, timestamp: EventTime) -> 'ShellActionResult':
        active_device = self.controller.session.ui_session.active_device
        if active_device is None:
            return self.controller._commit('remember_active_device', self.controller.session)
        record = self.controller.services.adapters.remember_known_device(
            identity=active_device.identity,
            timestamp=timestamp,
            profile_id=str(self.controller.session.profile_snapshot.profile_id),
        )
        refreshed = self.controller.services.adapters.discover_devices(timestamp=timestamp)
        selected = next((item for item in refreshed if item.device_key == active_device.device_key), active_device)
        ui_session = self.controller._ui_session_with_lifecycle_update(
            phase=self.controller.session.ui_session.device_lifecycle_phase,
            detected_devices=tuple(refreshed),
            active_device=selected,
            active_adapter_id=self.controller.session.ui_session.active_adapter_id,
            onboarding_mode=self.controller.session.ui_session.onboarding_mode,
            known_device_restore_offer=f'restore available from profile {self.controller.session.profile_snapshot.profile_id}',
            available_workbenches=self.controller.session.ui_session.available_workbenches,
        )
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='KNOWNDEVICE',
            summary='active device remembered for safe restore matching',
            attributes={'known_device_key': record.known_device_key, 'device_key': active_device.device_key},
        )
        return self.controller._commit_with_ui_session('remember_active_device', ui_session=ui_session, evidence=evidence)

    def mark_active_device_disconnected(self, *, timestamp: EventTime) -> 'ShellActionResult':
        active_device = self.controller.session.ui_session.active_device
        adapter_id = self.controller.session.ui_session.active_adapter_id
        if active_device is None or adapter_id is None:
            return self.controller._commit('mark_active_device_disconnected', self.controller.session)
        workflow = self.controller._lifecycle().mark_active_device_disconnected(ui_session=self.controller.session.ui_session, timestamp=timestamp)
        first_signal_summary = FirstSignalPlanner.build_summary(
            services=self.controller.services,
            device=active_device,
            previous_summary=self.controller.session.ui_session.first_signal_summary,
            lifecycle_phase=DeviceLifecyclePhase.DISCONNECTED,
        )
        ui_session = self.controller._ui_session_with_lifecycle_update(
            phase=DeviceLifecyclePhase.DISCONNECTED,
            lifecycle_summary=workflow.lifecycle_summary,
            binding_review_summary=workflow.binding_review_summary,
            variable_health_summary=workflow.variable_health_summary,
            reconciliation_summary=workflow.reconciliation_summary,
            first_signal_summary=first_signal_summary,
        )
        self.controller._sync_alarm_lifecycles_from_service()
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='DISCONNECT',
            summary='active device marked disconnected',
            attributes={
                'device_key': active_device.device_key,
                'adapter_id': adapter_id,
                'disconnected_signals': str(workflow.lifecycle_summary.disconnected_signal_count),
            },
        )
        return self.controller._commit_with_ui_session('mark_active_device_disconnected', ui_session=ui_session, evidence=evidence)

    def reconnect_active_device(self, *, timestamp: EventTime) -> 'ShellActionResult':
        active_device = self.controller.session.ui_session.active_device
        adapter_id = self.controller.session.ui_session.active_adapter_id
        if active_device is None or adapter_id is None:
            return self.controller._commit('reconnect_active_device', self.controller.session)
        workflow = self.controller._lifecycle().reconnect_active_device(ui_session=self.controller.session.ui_session, timestamp=timestamp)
        phase = DeviceLifecyclePhase.LIVE if self.controller.session.ui_session.onboarding_mode == 'quick_start' else DeviceLifecyclePhase.READY_TO_CONFIGURE
        first_signal_summary = FirstSignalPlanner.build_summary(
            services=self.controller.services,
            device=active_device,
            previous_summary=self.controller.session.ui_session.first_signal_summary,
            lifecycle_phase=phase,
        )
        ui_session = self.controller._ui_session_with_lifecycle_update(
            phase=phase,
            onboarding_mode=self.controller.session.ui_session.onboarding_mode,
            lifecycle_summary=workflow.lifecycle_summary,
            binding_review_summary=workflow.binding_review_summary,
            variable_health_summary=workflow.variable_health_summary,
            reconciliation_summary=workflow.reconciliation_summary,
            first_signal_summary=first_signal_summary,
        )
        self.controller._sync_alarm_lifecycles_from_service()
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='RECONNECT',
            summary='active device reconnected',
            attributes={
                'device_key': active_device.device_key,
                'adapter_id': adapter_id,
                'published_signals': str(workflow.lifecycle_summary.published_signal_count),
                'first_signal_binding_reason': self._first_signal_binding_reason(first_signal_summary),
            },
        )
        return self.controller._commit_with_ui_session('reconnect_active_device', ui_session=ui_session, evidence=evidence)

    def poll_adapters(self, *, timestamp: EventTime) -> tuple[AdapterPollResult, ...]:
        if self.controller.session.ui_session.active_adapter_id is None or self.controller.session.ui_session.active_device is None:
            results = self.controller.services.adapters.poll_all(timestamp=timestamp)
            evidence = self.controller._shell_evidence(
                timestamp=timestamp,
                suffix='ADAPTERPOLL',
                summary='adapter poll completed',
                attributes={
                    'adapter_count': str(len(results)),
                    'snapshot_count': str(sum(len(item.snapshots) for item in results)),
                    'published_signals': '0',
                },
            )
            self.controller.session = self.controller.session.append_shell_evidence(evidence)
            return results
        before_status = self._active_adapter_status_snapshot()
        workflow = self.controller._lifecycle().poll_active_adapter(ui_session=self.controller.session.ui_session, timestamp=timestamp)
        after_status = self._active_adapter_status_snapshot()
        lifecycle_summary = self._normalize_phase_for_adapter_status(
            lifecycle_summary=workflow.lifecycle_summary,
            adapter_status=after_status,
        )
        first_signal_summary = FirstSignalPlanner.build_summary(
            services=self.controller.services,
            device=self.controller.session.ui_session.active_device,
            previous_summary=self.controller.session.ui_session.first_signal_summary,
            lifecycle_phase=DeviceLifecyclePhase(lifecycle_summary.phase),
        )
        self._record_runtime_transition_event(timestamp=timestamp, before_status=before_status, after_status=after_status)
        self.controller._sync_alarm_lifecycles_from_service()
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='ADAPTERPOLL',
            summary='adapter poll completed',
            attributes={
                'adapter_count': str(len(workflow.poll_results)),
                'snapshot_count': str(sum(len(item.snapshots) for item in workflow.poll_results)),
                'published_signals': str(workflow.lifecycle_summary.published_signal_count),
                'first_signal_binding_reason': self._first_signal_binding_reason(first_signal_summary),
                'first_signal_trace_points': '0' if first_signal_summary is None else str(first_signal_summary.trace_point_count),
            },
        )
        self.controller._commit_with_ui_session(
            'poll_adapters',
            ui_session=self.controller._ui_session_with_lifecycle_update(
                phase=DeviceLifecyclePhase(lifecycle_summary.phase),
                onboarding_mode=self.controller.session.ui_session.onboarding_mode,
                lifecycle_summary=lifecycle_summary,
                binding_review_summary=workflow.binding_review_summary,
                variable_health_summary=workflow.variable_health_summary,
                reconciliation_summary=workflow.reconciliation_summary,
                first_signal_summary=first_signal_summary,
            ),
            evidence=evidence,
        )
        return workflow.poll_results

    def run_device_quick_start(
        self,
        *,
        device_key: str,
        timestamp: EventTime,
        signal_bindings: tuple[tuple[SignalId, str, BindingPolicy], ...],
    ) -> 'ShellActionResult':
        self.select_detected_device(device_key=device_key, timestamp=timestamp)
        result = self.begin_quick_start(timestamp=timestamp)
        active_adapter_id = self.controller.session.ui_session.active_adapter_id
        if active_adapter_id is None:
            return result
        for index, (signal_id, point_id, binding_policy) in enumerate(signal_bindings, start=1):
            self.controller._binding_handler().bind_logical_signal_to_point(
                logical_signal_id=signal_id,
                point_key=f'{active_adapter_id}:{point_id}',
                display_name=point_id,
                binding_policy=binding_policy,
                timestamp=EventTime(int(timestamp) + index),
            )
        self.poll_adapters(timestamp=EventTime(int(timestamp) + len(signal_bindings) + 1))
        return result
