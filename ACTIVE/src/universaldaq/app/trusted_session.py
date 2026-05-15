from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping

from universaldaq.ui import ActionAuditEntry, SessionEventSummary, TrustedSessionSummary

if TYPE_CHECKING:
    from .session import ShellSession

_SPARK_BARS = '▁▂▃▄▅▆▇█'


@dataclass(frozen=True, slots=True, kw_only=True)
class TrustedSessionInventory:
    summary: TrustedSessionSummary
    trace_numeric_points: tuple[float, ...] = ()


class TrustedSessionBuilder:
    @staticmethod
    def _numeric_points(summary) -> tuple[float, ...]:
        if summary is None:
            return ()
        numeric: list[float] = []
        for point in summary.trace_points:
            try:
                numeric.append(float(point.value))
            except (TypeError, ValueError):
                continue
        return tuple(numeric)

    @staticmethod
    def _sparkline(values: tuple[float, ...]) -> str:
        if not values:
            return ''
        if len(values) == 1:
            return _SPARK_BARS[-1]
        low = min(values)
        high = max(values)
        if high == low:
            return _SPARK_BARS[len(_SPARK_BARS) // 2] * len(values)
        span = high - low
        pieces: list[str] = []
        for value in values:
            scaled = (value - low) / span
            index = round(scaled * (len(_SPARK_BARS) - 1))
            pieces.append(_SPARK_BARS[max(0, min(len(_SPARK_BARS) - 1, index))])
        return ''.join(pieces)

    @staticmethod
    def _event_category(record) -> str:
        summary = record.summary.lower()
        if 'disconnect' in summary:
            return 'disconnect'
        if 'reconnect' in summary or 'recovered' in summary:
            return 'reconnect'
        if 'quick start' in summary:
            return 'quick_start'
        if 'device discovery' in summary:
            return 'discovery'
        if 'detected device selected' in summary:
            return 'selection'
        if 'adapter poll' in summary:
            return 'poll'
        if 'trace visibility' in summary or 'overlay' in summary or 'history range' in summary:
            return 'graph'
        return 'session'

    @staticmethod
    def _recent_events(*, shell_session: 'ShellSession', limit: int) -> tuple[SessionEventSummary, ...]:
        events = []
        for record in shell_session.shell_evidence_records[-max(1, limit):]:
            phase_after = record.attributes.get('phase_after')
            if phase_after is None:
                phase_after = record.attributes.get('phase')
            events.append(
                SessionEventSummary(
                    timestamp=record.timestamp,
                    category=TrustedSessionBuilder._event_category(record),
                    summary=record.summary,
                    phase_after=phase_after,
                )
            )
        return tuple(events)

    @staticmethod
    def _action_category_from_summary(summary: str) -> str:
        lowered = summary.lower()
        if 'authorize' in lowered or 'denied' in lowered:
            return 'authorization'
        if 'export' in lowered:
            return 'export'
        if 'alarm' in lowered:
            return 'alarm'
        if 'trace visibility' in lowered or 'overlay' in lowered or 'graph mode' in lowered or 'return to live' in lowered:
            return 'graph'
        if 'workspace' in lowered or 'profile' in lowered or 'restore' in lowered or 'autosave' in lowered:
            return 'workspace'
        if 'device' in lowered or 'adapter poll' in lowered:
            return 'device'
        return 'session'

    @staticmethod
    def _action_entries(*, shell_session: 'ShellSession', limit: int) -> tuple[ActionAuditEntry, ...]:
        records = shell_session.shell_evidence_records[-max(1, limit):]
        actions: list[ActionAuditEntry] = []
        for record in records:
            outcome = 'recorded'
            target_kind = record.source_kind
            target_id = record.source_id
            if record.summary == 'authorization decision recorded':
                allowed = record.attributes.get('allowed', 'false').lower() == 'true'
                outcome = 'allowed' if allowed else 'denied'
                target_kind = record.attributes.get('target_kind') or target_kind
                target_id = record.attributes.get('target_id') or target_id
            elif 'denied' in record.summary.lower():
                outcome = 'denied'
            actions.append(
                ActionAuditEntry(
                    timestamp=record.timestamp,
                    category=TrustedSessionBuilder._action_category_from_summary(record.summary),
                    summary=record.summary,
                    outcome=outcome,
                    actor_id=record.actor_id,
                    target_kind=target_kind,
                    target_id=target_id,
                )
            )
        return tuple(actions)

    @staticmethod
    def _graph_status_label(*, lifecycle_state: str, signal_summary) -> str:
        if signal_summary is None:
            return 'pending'
        quality = str(signal_summary.quality_label)
        if quality == 'disconnected' or lifecycle_state == 'disconnected':
            return 'disconnected'
        if quality in {'stale', 'degraded'} or lifecycle_state == 'degraded':
            return 'stale'
        if len(signal_summary.trace_points) >= 2:
            return 'live'
        return 'pending'

    @staticmethod
    def _truthfulness_warnings(*, lifecycle_state: str, signal_summary, graph_visible: bool, live_numeric_visible: bool) -> tuple[str, ...]:
        warnings: list[str] = []
        if lifecycle_state == 'disconnected' and signal_summary is not None and signal_summary.quality_label != 'disconnected':
            warnings.append('lifecycle says disconnected but first-signal quality is not disconnected')
        if lifecycle_state == 'live' and signal_summary is None:
            warnings.append('lifecycle says live but no first-signal summary is present')
        if graph_visible and not live_numeric_visible:
            warnings.append('graph claims visible without a numeric first-signal value')
        if signal_summary is not None and signal_summary.freshness_label == 'offline' and lifecycle_state != 'disconnected':
            warnings.append('first-signal freshness is offline while lifecycle is not disconnected')
        return tuple(warnings)

    @staticmethod
    def _control_mode_label(*, shell_session: 'ShellSession') -> str:
        permissions = set(shell_session.granted_permission_families)
        if 'edit_configuration' in permissions or 'apply_configuration' in permissions:
            return 'engineering'
        if 'issue_manual_commands' in permissions:
            return 'armed_control'
        return 'view_only'

    @staticmethod
    def build(
        *,
        shell_session: 'ShellSession',
        recent_event_limit: int = 6,
        recent_action_limit: int = 8,
        event_summary: Mapping[str, object] | None = None,
    ) -> TrustedSessionInventory:
        ui_session = shell_session.ui_session
        lifecycle_state = ui_session.device_lifecycle_phase.value
        signal_summary = ui_session.first_signal_summary
        numeric_points = TrustedSessionBuilder._numeric_points(signal_summary)
        graph_visible = signal_summary is not None and signal_summary.trace_point_count >= 2
        live_numeric_visible = bool(signal_summary is not None and numeric_points)
        trace_span_seconds = None
        latest_value_age_seconds = None
        if signal_summary is not None and signal_summary.trace_points:
            first_ts = int(signal_summary.trace_points[0].timestamp)
            last_ts = int(signal_summary.trace_points[-1].timestamp)
            trace_span_seconds = max(0, last_ts - first_ts)
            if signal_summary.latest_timestamp is not None:
                latest_value_age_seconds = max(0, int(signal_summary.trace_points[-1].timestamp) - int(signal_summary.latest_timestamp))
        recent_events = TrustedSessionBuilder._recent_events(shell_session=shell_session, limit=recent_event_limit)
        recent_actions = TrustedSessionBuilder._action_entries(shell_session=shell_session, limit=recent_action_limit)
        disconnect_count = sum(1 for event in recent_events if event.category == 'disconnect')
        reconnect_count = sum(1 for event in recent_events if event.category == 'reconnect')
        graph_status_label = TrustedSessionBuilder._graph_status_label(lifecycle_state=lifecycle_state, signal_summary=signal_summary)
        truthfulness_warnings = TrustedSessionBuilder._truthfulness_warnings(
            lifecycle_state=lifecycle_state,
            signal_summary=signal_summary,
            graph_visible=graph_visible,
            live_numeric_visible=live_numeric_visible,
        )
        event_summary = {} if event_summary is None else dict(event_summary)
        active_alarm_count = int(event_summary.get('active_alarm_count', 0) or 0)
        unacknowledged_alarm_count = int(event_summary.get('unacknowledged_alarm_count', 0) or 0)
        highest_active_severity = event_summary.get('highest_active_severity')
        control_mode_label = TrustedSessionBuilder._control_mode_label(shell_session=shell_session)
        ready_for_operator = (
            lifecycle_state == 'live'
            and graph_status_label == 'live'
            and graph_visible
            and live_numeric_visible
            and not truthfulness_warnings
        )
        flight_record_ready = bool(signal_summary is not None and signal_summary.trace_point_count >= 2 and recent_actions and recent_events)
        summary = TrustedSessionSummary(
            lifecycle_state=lifecycle_state,
            graph_status_label=graph_status_label,
            live_numeric_visible=live_numeric_visible,
            graph_visible=graph_visible,
            trace_point_count=0 if signal_summary is None else signal_summary.trace_point_count,
            session_event_count=len(shell_session.shell_evidence_records),
            ready_for_operator=ready_for_operator,
            trace_span_seconds=trace_span_seconds,
            latest_value_age_seconds=latest_value_age_seconds,
            disconnect_count=disconnect_count,
            reconnect_count=reconnect_count,
            last_event_summary=None if not recent_events else recent_events[-1].summary,
            sparkline=TrustedSessionBuilder._sparkline(numeric_points),
            truthfulness_warnings=truthfulness_warnings,
            recent_events=recent_events,
            signal_quality_label=None if signal_summary is None else signal_summary.quality_label,
            signal_freshness_label='pending' if signal_summary is None else signal_summary.freshness_label,
            control_mode_label=control_mode_label,
            active_alarm_count=active_alarm_count,
            unacknowledged_alarm_count=unacknowledged_alarm_count,
            highest_active_severity=None if highest_active_severity in {'', None} else str(highest_active_severity),
            recent_action_count=len(recent_actions),
            recent_actions=recent_actions,
            flight_record_ready=flight_record_ready,
        )
        return TrustedSessionInventory(summary=summary, trace_numeric_points=numeric_points)
