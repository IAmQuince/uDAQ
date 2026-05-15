from __future__ import annotations

from typing import Any

from universaldaq.common import GraphMode, ProfileId, TraceId, as_event_time

from .models import BenchPersistenceState, OperatorNote, PersistedSessionSummary, ProfileSnapshot, WorkspaceState

BENCH_PERSISTENCE_SCHEMA_VERSION = 1


def serialize_workspace_state(workspace_state: WorkspaceState) -> dict[str, Any]:
    return {
        'page': workspace_state.page,
        'review_mode': workspace_state.review_mode.value,
        'visible_traces': [str(item) for item in workspace_state.visible_traces],
    }


def deserialize_workspace_state(payload: dict[str, Any]) -> WorkspaceState:
    return WorkspaceState(
        page=str(payload['page']),
        review_mode=GraphMode(str(payload['review_mode'])),
        visible_traces=tuple(TraceId(str(item)) for item in payload.get('visible_traces', [])),
    )


def serialize_profile_snapshot(snapshot: ProfileSnapshot) -> dict[str, Any]:
    return {
        'profile_id': str(snapshot.profile_id),
        'workspace_state': serialize_workspace_state(snapshot.workspace_state),
    }


def deserialize_profile_snapshot(payload: dict[str, Any]) -> ProfileSnapshot:
    return ProfileSnapshot(
        profile_id=ProfileId(str(payload['profile_id'])),
        workspace_state=deserialize_workspace_state(dict(payload['workspace_state'])),
    )


def serialize_profile_snapshot_for_export(snapshot: ProfileSnapshot) -> dict[str, Any]:
    return {
        'profile_id': str(snapshot.profile_id),
        'workspace': serialize_workspace_state(snapshot.workspace_state),
        'export_summary': snapshot.export_summary(),
    }


def serialize_profile_snapshots_for_export(snapshots: tuple[ProfileSnapshot, ...]) -> list[dict[str, Any]]:
    return [serialize_profile_snapshot_for_export(snapshot) for snapshot in snapshots]


def serialize_operator_note(note: OperatorNote) -> dict[str, Any]:
    return {
        'note_id': note.note_id,
        'timestamp': int(note.timestamp),
        'text': note.text,
        'category': note.category,
        'actor_id': note.actor_id,
    }


def deserialize_operator_note(payload: dict[str, Any]) -> OperatorNote:
    return OperatorNote(
        note_id=str(payload['note_id']),
        timestamp=as_event_time(int(payload['timestamp'])),
        text=str(payload['text']),
        category=str(payload.get('category', 'operator_note')),
        actor_id=None if payload.get('actor_id') in {None, ''} else str(payload.get('actor_id')),
    )


def serialize_persisted_session_summary(summary: PersistedSessionSummary) -> dict[str, Any]:
    return {
        'summary_id': summary.summary_id,
        'saved_at': int(summary.saved_at),
        'session_id': summary.session_id,
        'profile_id': None if summary.profile_id is None else str(summary.profile_id),
        'workspace_state': serialize_workspace_state(summary.workspace_state),
        'preferred_adapter_id': summary.preferred_adapter_id,
        'preferred_device_key': summary.preferred_device_key,
        'preferred_channel_key': summary.preferred_channel_key,
        'control_mode_label': summary.control_mode_label,
        'signal_freshness_label': summary.signal_freshness_label,
        'last_signal_display_name': summary.last_signal_display_name,
        'last_signal_value': summary.last_signal_value,
        'last_signal_units': summary.last_signal_units,
        'alarm_posture': summary.alarm_posture,
        'recent_action_count': summary.recent_action_count,
        'flight_record_ready': summary.flight_record_ready,
        'signal_provenance_label': summary.signal_provenance_label,
        'trace_preview': summary.trace_preview,
        'session_source_label': summary.session_source_label,
        'completeness_label': summary.completeness_label,
        'last_event_summary': summary.last_event_summary,
        'operator_notes': [serialize_operator_note(item) for item in summary.operator_notes],
    }


def deserialize_persisted_session_summary(payload: dict[str, Any]) -> PersistedSessionSummary:
    profile_raw = payload.get('profile_id')
    return PersistedSessionSummary(
        summary_id=str(payload['summary_id']),
        saved_at=as_event_time(int(payload['saved_at'])),
        session_id=str(payload['session_id']),
        profile_id=None if profile_raw in {None, ''} else ProfileId(str(profile_raw)),
        workspace_state=deserialize_workspace_state(dict(payload['workspace_state'])),
        preferred_adapter_id=None if payload.get('preferred_adapter_id') in {None, ''} else str(payload.get('preferred_adapter_id')),
        preferred_device_key=None if payload.get('preferred_device_key') in {None, ''} else str(payload.get('preferred_device_key')),
        preferred_channel_key=None if payload.get('preferred_channel_key') in {None, ''} else str(payload.get('preferred_channel_key')),
        control_mode_label=str(payload.get('control_mode_label', 'view_only')),
        signal_freshness_label=str(payload.get('signal_freshness_label', 'pending')),
        last_signal_display_name=None if payload.get('last_signal_display_name') in {None, ''} else str(payload.get('last_signal_display_name')),
        last_signal_value=None if payload.get('last_signal_value') in {None, ''} else str(payload.get('last_signal_value')),
        last_signal_units=None if payload.get('last_signal_units') in {None, ''} else str(payload.get('last_signal_units')),
        alarm_posture=None if payload.get('alarm_posture') in {None, ''} else str(payload.get('alarm_posture')),
        recent_action_count=int(payload.get('recent_action_count', 0)),
        flight_record_ready=bool(payload.get('flight_record_ready', False)),
        signal_provenance_label=None if payload.get('signal_provenance_label') in {None, ''} else str(payload.get('signal_provenance_label')),
        trace_preview=str(payload.get('trace_preview', '')),
        session_source_label=str(payload.get('session_source_label', 'historical_saved')),
        completeness_label=str(payload.get('completeness_label', 'partial')),
        last_event_summary=None if payload.get('last_event_summary') in {None, ''} else str(payload.get('last_event_summary')),
        operator_notes=tuple(deserialize_operator_note(dict(item)) for item in payload.get('operator_notes', [])),
    )


def serialize_bench_persistence_state(state: BenchPersistenceState) -> dict[str, Any]:
    return {
        'schema_version': state.schema_version,
        'saved_at': int(state.saved_at),
        'profile_snapshot': serialize_profile_snapshot(state.profile_snapshot),
        'preferred_adapter_id': state.preferred_adapter_id,
        'preferred_device_key': state.preferred_device_key,
        'preferred_channel_key': state.preferred_channel_key,
        'historical_summary': None if state.historical_summary is None else serialize_persisted_session_summary(state.historical_summary),
        'pending_note_draft': state.pending_note_draft,
        'restored_historical_only': state.restored_historical_only,
    }


def deserialize_bench_persistence_state(payload: dict[str, Any]) -> BenchPersistenceState:
    schema_version = int(payload.get('schema_version', BENCH_PERSISTENCE_SCHEMA_VERSION))
    historical = payload.get('historical_summary')
    return BenchPersistenceState(
        schema_version=schema_version,
        saved_at=as_event_time(int(payload['saved_at'])),
        profile_snapshot=deserialize_profile_snapshot(dict(payload['profile_snapshot'])),
        preferred_adapter_id=None if payload.get('preferred_adapter_id') in {None, ''} else str(payload.get('preferred_adapter_id')),
        preferred_device_key=None if payload.get('preferred_device_key') in {None, ''} else str(payload.get('preferred_device_key')),
        preferred_channel_key=None if payload.get('preferred_channel_key') in {None, ''} else str(payload.get('preferred_channel_key')),
        historical_summary=None if historical is None or historical == '' else deserialize_persisted_session_summary(dict(historical)),
        pending_note_draft=None if payload.get('pending_note_draft') in {None, ''} else str(payload.get('pending_note_draft')),
        restored_historical_only=bool(payload.get('restored_historical_only', True)),
    )
