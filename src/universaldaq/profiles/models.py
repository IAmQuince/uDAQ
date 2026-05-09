from __future__ import annotations

from dataclasses import dataclass, field

from universaldaq.common import EvidenceId, EvidenceKind, EvidenceRecord, EventTime, GraphMode, ProfileId, RestoreOrigin, TraceId


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkspaceState:
    page: str
    review_mode: GraphMode
    visible_traces: tuple[TraceId, ...] = field(default_factory=tuple)

    def export_summary(self) -> dict[str, object]:
        return {
            'page': self.page,
            'review_mode': self.review_mode.value,
            'visible_traces': tuple(str(item) for item in self.visible_traces),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileSnapshot:
    profile_id: ProfileId
    workspace_state: WorkspaceState

    def export_summary(self) -> dict[str, object]:
        return {
            'profile_id': str(self.profile_id),
            'workspace_state': self.workspace_state.export_summary(),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RestorePlan:
    snapshot: ProfileSnapshot
    origin: RestoreOrigin
    machine_write_intent: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class RestoreResult:
    restored_workspace: WorkspaceState
    machine_write_intent: bool
    evidence_records: tuple[EvidenceRecord, ...]
    origin: RestoreOrigin = RestoreOrigin.SESSION
    profile_id: ProfileId | None = None
    restored_at: EventTime | None = None

    def export_row(self) -> dict[str, str]:
        return {
            'record_type': 'restore',
            'profile_id': '' if self.profile_id is None else str(self.profile_id),
            'origin': self.origin.value,
            'restored_at': '' if self.restored_at is None else str(self.restored_at),
            'machine_write_intent': str(self.machine_write_intent).lower(),
            'page': self.restored_workspace.page,
            'review_mode': self.restored_workspace.review_mode.value,
        }


class RestorePlanner:
    @staticmethod
    def apply(plan: RestorePlan, timestamp: EventTime) -> RestoreResult:
        evidence = (
            EvidenceRecord(
                evidence_id=EvidenceId(f"EVID-{plan.snapshot.profile_id}-RESTORE-{timestamp}"),
                kind=EvidenceKind.EVENT,
                timestamp=timestamp,
                summary="restore-origin workspace rebuild",
                attributes={
                    "origin": plan.origin.value,
                    "machine_write_intent": str(plan.machine_write_intent).lower(),
                    "profile_id": str(plan.snapshot.profile_id),
                },
                source_kind='restore',
                source_id=str(plan.snapshot.profile_id),
                origin=plan.origin.value,
                tags=('restore',),
            ),
        )
        return RestoreResult(
            restored_workspace=plan.snapshot.workspace_state,
            machine_write_intent=plan.machine_write_intent,
            evidence_records=evidence,
            origin=plan.origin,
            profile_id=plan.snapshot.profile_id,
            restored_at=timestamp,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class OperatorNote:
    note_id: str
    timestamp: EventTime
    text: str
    category: str = "operator_note"
    actor_id: str | None = None

    def export_summary(self) -> dict[str, object]:
        return {
            "note_id": self.note_id,
            "timestamp": int(self.timestamp),
            "text": self.text,
            "category": self.category,
            "actor_id": self.actor_id,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class PersistedSessionSummary:
    summary_id: str
    saved_at: EventTime
    session_id: str
    profile_id: ProfileId | None
    workspace_state: WorkspaceState
    preferred_adapter_id: str | None = None
    preferred_device_key: str | None = None
    preferred_channel_key: str | None = None
    control_mode_label: str = "view_only"
    signal_freshness_label: str = "pending"
    last_signal_display_name: str | None = None
    last_signal_value: str | None = None
    last_signal_units: str | None = None
    alarm_posture: str | None = None
    recent_action_count: int = 0
    flight_record_ready: bool = False
    signal_provenance_label: str | None = None
    trace_preview: str = ''
    session_source_label: str = 'historical_saved'
    completeness_label: str = 'partial'
    last_event_summary: str | None = None
    operator_notes: tuple[OperatorNote, ...] = field(default_factory=tuple)

    def export_summary(self) -> dict[str, object]:
        return {
            "summary_id": self.summary_id,
            "saved_at": int(self.saved_at),
            "session_id": self.session_id,
            "profile_id": None if self.profile_id is None else str(self.profile_id),
            "workspace_state": self.workspace_state.export_summary(),
            "preferred_adapter_id": self.preferred_adapter_id,
            "preferred_device_key": self.preferred_device_key,
            "preferred_channel_key": self.preferred_channel_key,
            "control_mode_label": self.control_mode_label,
            "signal_freshness_label": self.signal_freshness_label,
            "last_signal_display_name": self.last_signal_display_name,
            "last_signal_value": self.last_signal_value,
            "last_signal_units": self.last_signal_units,
            "alarm_posture": self.alarm_posture,
            "recent_action_count": self.recent_action_count,
            "flight_record_ready": self.flight_record_ready,
            "signal_provenance_label": self.signal_provenance_label,
            "trace_preview": self.trace_preview,
            "session_source_label": self.session_source_label,
            "completeness_label": self.completeness_label,
            "last_event_summary": self.last_event_summary,
            "operator_notes": [item.export_summary() for item in self.operator_notes],
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class BenchPersistenceState:
    schema_version: int
    saved_at: EventTime
    profile_snapshot: ProfileSnapshot
    preferred_adapter_id: str | None = None
    preferred_device_key: str | None = None
    preferred_channel_key: str | None = None
    historical_summary: PersistedSessionSummary | None = None
    pending_note_draft: str | None = None
    restored_historical_only: bool = True

    def export_summary(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "saved_at": int(self.saved_at),
            "profile_snapshot": self.profile_snapshot.export_summary(),
            "preferred_adapter_id": self.preferred_adapter_id,
            "preferred_device_key": self.preferred_device_key,
            "preferred_channel_key": self.preferred_channel_key,
            "historical_summary": None if self.historical_summary is None else self.historical_summary.export_summary(),
            "pending_note_draft": self.pending_note_draft,
            "restored_historical_only": self.restored_historical_only,
        }
