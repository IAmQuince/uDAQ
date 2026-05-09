from __future__ import annotations

from dataclasses import dataclass

from universaldaq.common import EventTime
from universaldaq.profiles import OperatorNote, PersistedSessionSummary


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionReviewListItem:
    summary_id: str
    saved_at: EventTime
    summary_label: str
    historical_label: str
    session_source_label: str
    preferred_adapter_id: str | None = None
    preferred_device_key: str | None = None
    preferred_channel_key: str | None = None
    signal_freshness_label: str = 'pending'
    control_mode_label: str = 'view_only'
    alarm_posture: str | None = None
    note_count: int = 0
    completeness_label: str = 'partial'
    flight_record_ready: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionReviewDetail:
    summary_id: str
    saved_at: EventTime
    session_id: str
    summary_label: str
    historical_label: str
    session_source_label: str
    completeness_label: str
    preferred_adapter_id: str | None = None
    preferred_device_key: str | None = None
    preferred_channel_key: str | None = None
    control_mode_label: str = 'view_only'
    signal_freshness_label: str = 'pending'
    signal_provenance_label: str | None = None
    last_signal_value: str | None = None
    last_signal_units: str | None = None
    alarm_posture: str | None = None
    recent_action_count: int = 0
    flight_record_ready: bool = False
    trace_preview: str = ''
    last_event_summary: str | None = None
    operator_notes: tuple[OperatorNote, ...] = ()

    @property
    def note_count(self) -> int:
        return len(self.operator_notes)


@dataclass(frozen=True, slots=True, kw_only=True)
class LightweightSessionReport:
    report_id: str
    summary_id: str
    generated_at: EventTime
    markdown: str
    payload: dict[str, object]


class SessionReviewBuilder:
    @staticmethod
    def _summary_label(summary: PersistedSessionSummary) -> str:
        return summary.last_signal_display_name or summary.preferred_channel_key or summary.summary_id

    @staticmethod
    def _historical_label(summary: PersistedSessionSummary) -> str:
        return f'historical review only · saved session · {summary.session_source_label}'

    @staticmethod
    def build_list_item(summary: PersistedSessionSummary) -> SessionReviewListItem:
        return SessionReviewListItem(
            summary_id=summary.summary_id, saved_at=summary.saved_at, summary_label=SessionReviewBuilder._summary_label(summary), historical_label=SessionReviewBuilder._historical_label(summary), session_source_label=summary.session_source_label, preferred_adapter_id=summary.preferred_adapter_id, preferred_device_key=summary.preferred_device_key, preferred_channel_key=summary.preferred_channel_key, signal_freshness_label=summary.signal_freshness_label, control_mode_label=summary.control_mode_label, alarm_posture=summary.alarm_posture, note_count=len(summary.operator_notes), completeness_label=summary.completeness_label, flight_record_ready=summary.flight_record_ready)

    @staticmethod
    def build_detail(summary: PersistedSessionSummary) -> SessionReviewDetail:
        return SessionReviewDetail(
            summary_id=summary.summary_id, saved_at=summary.saved_at, session_id=summary.session_id, summary_label=SessionReviewBuilder._summary_label(summary), historical_label=SessionReviewBuilder._historical_label(summary), session_source_label=summary.session_source_label, completeness_label=summary.completeness_label, preferred_adapter_id=summary.preferred_adapter_id, preferred_device_key=summary.preferred_device_key, preferred_channel_key=summary.preferred_channel_key, control_mode_label=summary.control_mode_label, signal_freshness_label=summary.signal_freshness_label, signal_provenance_label=summary.signal_provenance_label, last_signal_value=summary.last_signal_value, last_signal_units=summary.last_signal_units, alarm_posture=summary.alarm_posture, recent_action_count=summary.recent_action_count, flight_record_ready=summary.flight_record_ready, trace_preview=summary.trace_preview, last_event_summary=summary.last_event_summary, operator_notes=summary.operator_notes)

    @staticmethod
    def build_recent_list(*, summaries: tuple[PersistedSessionSummary, ...]) -> tuple[SessionReviewListItem, ...]:
        ordered = tuple(sorted(summaries, key=lambda item: int(item.saved_at), reverse=True))
        return tuple(SessionReviewBuilder.build_list_item(item) for item in ordered)

    @staticmethod
    def build_report(*, summary: PersistedSessionSummary, generated_at: EventTime, package_id: str, package_slug: str) -> LightweightSessionReport:
        detail = SessionReviewBuilder.build_detail(summary)
        note_rows = [
            {'note_id': note.note_id, 'timestamp': int(note.timestamp), 'text': note.text, 'category': note.category, 'actor_id': note.actor_id}
            for note in detail.operator_notes
        ]
        payload: dict[str, object] = {
            'report_id': f'RPT-{summary.summary_id}-{int(generated_at)}',
            'summary_id': summary.summary_id, 'generated_at': int(generated_at), 'package_id': package_id, 'package_slug': package_slug, 'historical_label': detail.historical_label,
            'session': {'saved_at': int(detail.saved_at), 'session_id': detail.session_id, 'summary_label': detail.summary_label, 'session_source_label': detail.session_source_label, 'completeness_label': detail.completeness_label},
            'selection': {'preferred_adapter_id': detail.preferred_adapter_id, 'preferred_device_key': detail.preferred_device_key, 'preferred_channel_key': detail.preferred_channel_key},
            'signal': {'freshness_label': detail.signal_freshness_label, 'provenance_label': detail.signal_provenance_label, 'last_signal_value': detail.last_signal_value, 'last_signal_units': detail.last_signal_units, 'trace_preview': detail.trace_preview},
            'posture': {'control_mode_label': detail.control_mode_label, 'alarm_posture': detail.alarm_posture, 'recent_action_count': detail.recent_action_count, 'flight_record_ready': detail.flight_record_ready},
            'notes': note_rows, 'last_event_summary': detail.last_event_summary,
        }
        lines=['# Lightweight Session Report','',f'- report_id: `{payload["report_id"]}`',f'- package_id: `{package_id}`',f'- package_slug: `{package_slug}`',f'- summary_id: `{summary.summary_id}`',f'- generated_at: `{int(generated_at)}`',f'- review_posture: `{detail.historical_label}`','','## Session summary',f'- saved_at: `{int(detail.saved_at)}`',f'- session_id: `{detail.session_id}`',f'- summary_label: `{detail.summary_label}`',f'- session_source_label: `{detail.session_source_label}`',f'- completeness_label: `{detail.completeness_label}`','','## Selection',f'- preferred_adapter_id: `{detail.preferred_adapter_id or ""}`',f'- preferred_device_key: `{detail.preferred_device_key or ""}`',f'- preferred_channel_key: `{detail.preferred_channel_key or ""}`','','## Signal summary',f'- signal_freshness_label: `{detail.signal_freshness_label}`',f'- signal_provenance_label: `{detail.signal_provenance_label or ""}`',f'- last_signal_value: `{detail.last_signal_value or ""}`',f'- last_signal_units: `{detail.last_signal_units or ""}`',f'- trace_preview: `{detail.trace_preview}`','','## Control and alarm posture',f'- control_mode_label: `{detail.control_mode_label}`',f'- alarm_posture: `{detail.alarm_posture or ""}`',f'- recent_action_count: `{detail.recent_action_count}`',f'- flight_record_ready: `{str(detail.flight_record_ready).lower()}`','','## Operator notes']
        lines.extend([f"- `{n['timestamp']}` [{n['category']}] {n['text']}" for n in note_rows] or ['- none'])
        lines.extend(['','## Last event summary',f"- `{detail.last_event_summary or ''}`",'', 'Historical session review only. This report does not assert current live truth.',''])
        return LightweightSessionReport(report_id=str(payload['report_id']), summary_id=summary.summary_id, generated_at=generated_at, markdown='\n'.join(lines), payload=payload)
