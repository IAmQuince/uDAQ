from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from universaldaq.common import AuthorizationState, EvidenceId, EvidenceKind, EvidenceRecord, EventTime, GraphMode


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthoritySurface:
    authorization_state: AuthorizationState
    ui_enabled: bool
    visible: bool = True

    @property
    def presents_false_authority(self) -> bool:
        return self.ui_enabled and self.authorization_state != AuthorizationState.ALLOWED

    @property
    def status_label(self) -> str:
        if self.authorization_state == AuthorizationState.ALLOWED:
            return 'interactive'
        if self.ui_enabled:
            return 'review-only'
        return 'disabled'


@dataclass(frozen=True, slots=True, kw_only=True)
class GraphModeSession:
    mode: GraphMode
    transitions: tuple[tuple[EventTime, GraphMode], ...] = field(default_factory=tuple)
    evidence_records: tuple[EvidenceRecord, ...] = field(default_factory=tuple)

    @staticmethod
    def _build_evidence(
        *,
        timestamp: EventTime,
        mode: GraphMode,
        previous_mode: GraphMode | None,
        summary: str,
        attributes: Mapping[str, str] | None = None,
    ) -> EvidenceRecord:
        payload = {
            'mode': mode.value,
            'previous_mode': '' if previous_mode is None else previous_mode.value,
        }
        if attributes:
            payload.update({str(key): str(value) for key, value in attributes.items()})
        return EvidenceRecord(
            evidence_id=EvidenceId(f'EVID-GRAPH-{timestamp}-{mode.value}'),
            kind=EvidenceKind.TRACE,
            timestamp=timestamp,
            summary=summary,
            attributes=payload,
        )

    @staticmethod
    def start(mode: GraphMode, timestamp: EventTime) -> 'GraphModeSession':
        evidence = GraphModeSession._build_evidence(
            timestamp=timestamp,
            mode=mode,
            previous_mode=None,
            summary='graph mode entered',
        )
        return GraphModeSession(mode=mode, transitions=((timestamp, mode),), evidence_records=(evidence,))

    def transition(
        self,
        mode: GraphMode,
        timestamp: EventTime,
        *,
        summary: str = 'graph mode changed',
        attributes: Mapping[str, str] | None = None,
    ) -> 'GraphModeSession':
        evidence = self._build_evidence(
            timestamp=timestamp,
            mode=mode,
            previous_mode=self.mode,
            summary=summary,
            attributes=attributes,
        )
        return GraphModeSession(mode=mode, transitions=self.transitions + ((timestamp, mode),), evidence_records=self.evidence_records + (evidence,))

    def return_to_live(self, timestamp: EventTime) -> 'GraphModeSession':
        return self.transition(
            GraphMode.LIVE,
            timestamp,
            summary='returned to live graph mode',
            attributes={'return_to_live': 'true'},
        )

    @property
    def transition_modes(self) -> tuple[GraphMode, ...]:
        return tuple(mode for _, mode in self.transitions)

    @property
    def is_live(self) -> bool:
        return self.mode == GraphMode.LIVE

    @property
    def return_to_live_available(self) -> bool:
        return not self.is_live


@dataclass(frozen=True, slots=True, kw_only=True)
class FirstSignalTracePoint:
    timestamp: EventTime
    value: str


@dataclass(frozen=True, slots=True, kw_only=True)
class FirstSignalSummary:
    signal_id: str
    display_name: str
    point_key: str
    point_class: str
    latest_value: str
    quality_label: str
    latest_timestamp: EventTime | None = None
    engineering_units: str | None = None
    auto_bound: bool = False
    source_device_key: str | None = None
    source_adapter_id: str | None = None
    device_identity_key: str | None = None
    source_transport: str | None = None
    hardware_channel: str | None = None
    freshness_label: str = 'pending'
    provenance_label: str | None = None
    channel_metadata: Mapping[str, str] = field(default_factory=dict)
    trace_points: tuple[FirstSignalTracePoint, ...] = ()

    @property
    def trace_point_count(self) -> int:
        return len(self.trace_points)


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionEventSummary:
    timestamp: EventTime
    category: str
    summary: str
    phase_after: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ActionAuditEntry:
    timestamp: EventTime
    category: str
    summary: str
    outcome: str
    actor_id: str | None = None
    target_kind: str | None = None
    target_id: str | None = None




@dataclass(frozen=True, slots=True, kw_only=True)
class PersistedSessionSurface:
    summary_id: str | None = None
    summary_label: str | None = None
    preferred_adapter_id: str | None = None
    preferred_device_key: str | None = None
    preferred_channel_key: str | None = None
    restored_historical_only: bool = True
    pending_note_draft: str | None = None
    operator_note_count: int = 0

@dataclass(frozen=True, slots=True, kw_only=True)
class TrustedSessionSummary:
    lifecycle_state: str
    graph_status_label: str
    live_numeric_visible: bool
    graph_visible: bool
    trace_point_count: int
    session_event_count: int
    ready_for_operator: bool = False
    trace_span_seconds: int | None = None
    latest_value_age_seconds: int | None = None
    disconnect_count: int = 0
    reconnect_count: int = 0
    last_event_summary: str | None = None
    sparkline: str = ''
    truthfulness_warnings: tuple[str, ...] = ()
    recent_events: tuple[SessionEventSummary, ...] = ()
    signal_quality_label: str | None = None
    signal_freshness_label: str = 'pending'
    control_mode_label: str = 'view_only'
    active_alarm_count: int = 0
    unacknowledged_alarm_count: int = 0
    highest_active_severity: str | None = None
    recent_action_count: int = 0
    recent_actions: tuple[ActionAuditEntry, ...] = ()
    flight_record_ready: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class DeviceLifecycleSummary:
    phase: str
    detected_device_count: int = 0
    active_device_key: str | None = None
    active_adapter_id: str | None = None
    projected_point_count: int = 0
    published_signal_count: int = 0
    last_poll_snapshot_count: int = 0
    disconnected_signal_count: int = 0
    last_transition: str | None = None
    needs_review: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class BindingReviewSummary:
    total_signal_binding_count: int = 0
    total_output_binding_count: int = 0
    resolved_signal_count: int = 0
    auto_rebound_signal_count: int = 0
    manual_review_signal_count: int = 0
    unresolved_signal_count: int = 0
    blocked_signal_count: int = 0
    resolved_output_count: int = 0
    unresolved_output_count: int = 0
    highlighted_items: tuple[str, ...] = ()

    @property
    def requires_review(self) -> bool:
        return self.manual_review_signal_count > 0 or self.unresolved_signal_count > 0 or self.blocked_signal_count > 0 or self.unresolved_output_count > 0


@dataclass(frozen=True, slots=True, kw_only=True)
class VariableHealthSummary:
    total_variable_count: int = 0
    healthy_count: int = 0
    substituted_count: int = 0
    stale_count: int = 0
    invalid_count: int = 0
    unresolved_count: int = 0
    degraded_count: int = 0
    highlighted_variables: tuple[str, ...] = ()

    @property
    def impacted_count(self) -> int:
        return self.substituted_count + self.stale_count + self.invalid_count + self.unresolved_count + self.degraded_count


@dataclass(frozen=True, slots=True, kw_only=True)
class ReconciliationSummary:
    outcome_kind: str | None = None
    confidence: str | None = None
    reason: str | None = None
    remap_candidate_count: int = 0
    auto_rebound_signal_count: int = 0
    manual_review_required: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkbenchReviewState:
    total_workbench_count: int = 0
    available_workbench_names: tuple[str, ...] = ()
    active_workbench_name: str | None = None
    highlighted_workbenches: tuple[str, ...] = ()
