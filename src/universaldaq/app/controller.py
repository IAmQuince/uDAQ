from __future__ import annotations

from dataclasses import dataclass, replace
import re

from universaldaq.commands import CommandRecord
from universaldaq.common import (
    ActorId,
    AlarmId,
    AuthorizationState,
    EvidenceId,
    EvidenceKind,
    EvidenceRecord,
    EventTime,
    GraphMode,
    ProfileId,
    RequestId,
    RestoreOrigin,
    SignalId,
    TraceId,
    OutputId,
    ExportArtifactClass,
)
from universaldaq.adapters import DeviceLifecyclePhase, DiscoveredDevice, WorkbenchDescriptor, AdapterPollResult
from universaldaq.historian import ArtifactManifest, BundleBuildResult, BundleIntegrityWarning, EvidenceBundle, ExportIntent
from universaldaq.sequences import SequenceDefinition
from universaldaq.signals import BindingPolicy, VariableDefinition
from universaldaq.profiles import BenchPersistenceState, OperatorNote, PersistedSessionSummary, WorkspaceState
from universaldaq.rules import RuleDefinition
from universaldaq.security import ActorContext, AuthorizationDecision, GovernedAction, derive_role_class_from_authority_state
from universaldaq.ui import (
    BindingReviewSummary,
    DeviceLifecycleSummary,
    FirstSignalSummary,
    ReconciliationSummary,
    ShellViewModel,
    ShellViewModelBuilder,
    VariableHealthSummary,
    WorkbenchReviewState,
)
from universaldaq.ui.session_state import UISessionState

from .authoritative_binding_bridge import AuthoritativeBindingInventory, BackendBindingReadbackProvider
from .automation_review_handler import ShellAutomationReviewHandler
from .binding_variable_handler import ShellBindingVariableHandler
from .bootstrap import BootstrappedShell
from .command_export_handler import ShellCommandExportHandler
from .device_lifecycle_handler import ShellDeviceLifecycleHandler
from .mapping_apply_preflight import (
    DraftBindingRow,
    MappingApplyMode,
    MappingApplyRequest,
    MappingPreflightResult,
    MappingPreflightValidator,
    build_mapping_change_set,
    build_mapping_review_summary,
    prepare_mapping_apply_request,
)
from .lifecycle_orchestrator import ShellLifecycleOrchestrator
from .service_registry import ShellServiceRegistry
from .session import ShellSession
from .workspace_profile_handler import ShellWorkspaceProfileHandler
from .first_signal import FirstSignalReplayTape
from .trusted_session import TrustedSessionBuilder
from .session_review import LightweightSessionReport, SessionReviewBuilder, SessionReviewDetail, SessionReviewListItem

AUTOSAVE_PROFILE_ID = ProfileId('__autosave__')
LAST_SESSION_PROFILE_ID = ProfileId('__last_session__')
DEFAULT_EXPORT_ACTOR = ActorId('shell-reviewer')
CURRENT_PACKAGE_ID = 'UDQ-PKG-20260330-CONTROLLED-MAPPING-APPLY-PREFLIGHT-AND-REVIEW-PATH-R01'
CURRENT_PACKAGE_SLUG = 'controlled-mapping-apply-preflight-and-review-path'
_NON_ID_CHARS = re.compile(r'[^A-Za-z0-9]+')


@dataclass(frozen=True, slots=True, kw_only=True)
class ShellActionResult:
    action: str
    session: ShellSession


@dataclass(slots=True)
class ShellController:
    services: ShellServiceRegistry
    session: ShellSession

    AUTOSAVE_PROFILE_ID = AUTOSAVE_PROFILE_ID
    LAST_SESSION_PROFILE_ID = LAST_SESSION_PROFILE_ID
    DEFAULT_EXPORT_ACTOR = DEFAULT_EXPORT_ACTOR

    @classmethod
    def from_bootstrapped_shell(cls, bootstrapped_shell: BootstrappedShell) -> 'ShellController':
        return cls(services=bootstrapped_shell.services, session=bootstrapped_shell.session)

    def _shell_evidence(self, *, timestamp: EventTime, suffix: str, summary: str, attributes: dict[str, str]) -> EvidenceRecord:
        profile_id = str(self.session.profile_snapshot.profile_id)
        return EvidenceRecord(
            evidence_id=EvidenceId(f'EVID-SHELL-{profile_id}-{suffix}-{timestamp}'),
            kind=EvidenceKind.EVENT,
            timestamp=timestamp,
            summary=summary,
            attributes=attributes,
            source_kind='shell_session',
            source_id=self.session.session_id,
            session_id=self.session.session_id,
            tags=('shell',),
        )

    def _commit(self, action: str, session: ShellSession) -> ShellActionResult:
        self.session = session
        return ShellActionResult(action=action, session=session)

    @staticmethod
    def _id_token(value: object) -> str:
        text = _NON_ID_CHARS.sub('-', str(value)).strip('-')
        return text or 'anon'

    def _ack_correlation_id(self, *, alarm_id: AlarmId, timestamp: EventTime) -> str:
        status = self.services.events.active_statuses.get(alarm_id)
        state_version = int(timestamp)
        if status is not None:
            if status.first_raised_at is not None:
                state_version = int(status.first_raised_at)
            elif status.last_changed_at is not None:
                state_version = int(status.last_changed_at)
        return f'ACT-ACK-{self._id_token(alarm_id)}-{state_version}'

    def _ack_command_id(self, *, alarm_id: AlarmId, actor: ActorId, timestamp: EventTime) -> str:
        return f'CMD-ACK-{self._id_token(alarm_id)}-{int(timestamp)}-{self._id_token(actor)}'

    def _decision_evidence(self, *, decision: AuthorizationDecision, timestamp: EventTime) -> EvidenceRecord:
        return EvidenceRecord(
            evidence_id=EvidenceId(f'EVID-AUTH-{decision.action.value}-{timestamp}-{decision.actor_id}'),
            kind=EvidenceKind.ASSERTION,
            timestamp=timestamp,
            summary='authorization decision recorded',
            attributes={
                'action': decision.action.value,
                'allowed': str(decision.allowed).lower(),
                'reason_code': decision.reason_code.value,
                'reason': decision.reason_text,
                'target_kind': '' if decision.target_kind is None else decision.target_kind,
                'target_id': '' if decision.target_id is None else decision.target_id,
            },
            source_kind='authorization',
            source_id=decision.action.value,
            session_id=decision.session_id,
            actor_id=str(decision.actor_id),
            origin=decision.origin,
            tags=('authorization',),
        )

    def _effective_actor_context(
        self,
        *,
        actor: ActorId | None = None,
        authorization_state: AuthorizationState | None = None,
        origin: str | None = None,
    ) -> ActorContext:
        context = self.session.actor_context
        if actor is not None and actor != context.actor_id:
            context = context.with_actor(actor)
        if authorization_state is not None:
            context = ActorContext(
                actor_id=context.actor_id,
                display_name=context.display_name,
                role_class=derive_role_class_from_authority_state(authorization_state),
                origin=context.origin if origin is None else origin,
                is_local=context.is_local,
                session_id=self.session.session_id,
                tags=context.tags,
            )
        elif origin is not None:
            context = ActorContext(
                actor_id=context.actor_id,
                display_name=context.display_name,
                role_class=context.role_class,
                origin=origin,
                is_local=context.is_local,
                session_id=self.session.session_id,
                tags=context.tags,
            )
        return context.with_session(self.session.session_id)

    def _authorize(
        self,
        *,
        action: GovernedAction,
        actor: ActorId | None,
        authorization_state: AuthorizationState | None,
        target_kind: str,
        target_id: str,
        origin: str = 'local-shell',
        timestamp: EventTime,
    ) -> AuthorizationDecision:
        actor_context = self._effective_actor_context(actor=actor, authorization_state=authorization_state, origin=origin)
        decision = self.services.security.evaluate(
            action=action,
            actor_context=actor_context,
            target_kind=target_kind,
            target_id=target_id,
        )
        self.session = self.session.record_authorization_decision(decision)
        if not decision.allowed:
            self.session = self.session.append_shell_evidence(self._decision_evidence(decision=decision, timestamp=timestamp))
        return decision

    def _denied_export_result(
        self,
        *,
        export_intent: ExportIntent,
        bundle_id: str,
        manifest_id: str,
        decision: AuthorizationDecision,
    ) -> BundleBuildResult:
        warnings = (BundleIntegrityWarning(code='authorization_denied', message=decision.reason_text),)
        bundle = EvidenceBundle(
            bundle_id=bundle_id,
            records=(),
            overlays=self.session.ui_session.overlays,
            review_mode=export_intent.scope.graph_mode,
            export_id=export_intent.export_id,
            manifest_id=manifest_id,
            source_counts=(),
            warnings=warnings,
        )
        manifest = ArtifactManifest(
            manifest_id=manifest_id,
            export_id=export_intent.export_id,
            artifact_class=export_intent.artifact_class,
            created_at=export_intent.requested_at,
            created_by_actor=export_intent.requested_by_actor,
            session_id=export_intent.session_id,
            authority_state=decision.authorization_state,
            review_mode=export_intent.scope.graph_mode,
            scope_summary=export_intent.scope.summary(),
            artifacts=(),
            omission_notes=('export denied by authorization policy',),
            warnings=warnings,
        )
        return BundleBuildResult(
            export_intent=export_intent,
            bundle=bundle,
            manifest=manifest,
            serialized_artifacts=(),
            warnings=warnings,
            authorization_decision=decision,
        )

    def view_model(self) -> ShellViewModel:
        base = ShellViewModelBuilder.build_from_ui_session(self.session.ui_session)
        trusted_summary = TrustedSessionBuilder.build(
            shell_session=self.session,
            event_summary=self.services.events.summary(),
        ).summary
        persisted = self.session.last_persisted_session_summary
        return replace(
            base,
            trusted_session_summary=trusted_summary,
            preferred_adapter_id=self.session.ui_session.preferred_adapter_id,
            preferred_device_key=self.session.ui_session.preferred_device_key,
            preferred_channel_key=self.session.ui_session.preferred_channel_key,
            restored_historical_context_label=self.session.ui_session.restored_historical_context_label,
            last_session_summary_id=None if persisted is None else persisted.summary_id,
            last_session_summary_label=None if persisted is None else persisted.last_signal_display_name,
            session_note_count=len(self.session.operator_notes) if self.session.operator_notes else (0 if persisted is None else len(persisted.operator_notes)),
            pending_note_draft=self.session.ui_session.pending_note_draft,
        )

    def authoritative_binding_inventory(self, *, device_identity_key: str) -> AuthoritativeBindingInventory:
        return BackendBindingReadbackProvider(services=self.services).list_authoritative_bindings(device_identity_key=device_identity_key)

    def authoritative_binding_rows_for_device(self, *, device_identity_key: str) -> tuple[dict[str, object], ...]:
        inventory = self.authoritative_binding_inventory(device_identity_key=device_identity_key)
        return tuple(
            {
                'row_id': row.row_id,
                'authority_kind': row.authority_kind,
                'direction': row.direction,
                'logical_id': row.logical_id,
                'logical_display_name': row.logical_display_name,
                'source_endpoint': row.source_endpoint,
                'destination_endpoint': row.destination_endpoint,
                'status': row.status,
                'binding_policy': row.binding_policy,
                'device_identity_key': row.device_identity_key,
                'provenance_label': row.provenance_label,
                'engineering_units': row.engineering_units or '',
                'enabled': row.enabled,
                'note': row.note,
                'authority_source': row.authority_source,
                'last_confirmed_timestamp': row.last_confirmed_timestamp,
            }
            for row in inventory.rows
        )


    def build_mapping_change_set_for_device(
        self,
        *,
        device_identity_key: str,
        draft_rows: tuple[DraftBindingRow, ...],
        authoritative_snapshot_timestamp: EventTime | None,
    ):
        inventory = self.authoritative_binding_inventory(device_identity_key=device_identity_key)
        return build_mapping_change_set(
            device_identity_key=device_identity_key,
            authoritative_rows=inventory.rows,
            draft_rows=draft_rows,
            authoritative_snapshot_timestamp=authoritative_snapshot_timestamp,
            readback_available=inventory.readback_available,
            authority_source=inventory.authority_source,
        )

    def preflight_mapping_change_set_for_device(
        self,
        *,
        device_identity_key: str,
        draft_rows: tuple[DraftBindingRow, ...],
        authoritative_snapshot_timestamp: EventTime | None,
        validator: MappingPreflightValidator | None = None,
    ) -> MappingPreflightResult:
        change_set = self.build_mapping_change_set_for_device(
            device_identity_key=device_identity_key,
            draft_rows=draft_rows,
            authoritative_snapshot_timestamp=authoritative_snapshot_timestamp,
        )
        active_validator = validator or MappingPreflightValidator()
        return active_validator.validate(change_set)

    def mapping_apply_review_text_for_device(
        self,
        *,
        device_identity_key: str,
        draft_rows: tuple[DraftBindingRow, ...],
        authoritative_snapshot_timestamp: EventTime | None,
        validator: MappingPreflightValidator | None = None,
    ) -> str:
        result = self.preflight_mapping_change_set_for_device(
            device_identity_key=device_identity_key,
            draft_rows=draft_rows,
            authoritative_snapshot_timestamp=authoritative_snapshot_timestamp,
            validator=validator,
        )
        return build_mapping_review_summary(result).text

    def prepare_mapping_apply_request_for_device(
        self,
        *,
        device_identity_key: str,
        draft_rows: tuple[DraftBindingRow, ...],
        authoritative_snapshot_timestamp: EventTime | None,
        created_timestamp: EventTime,
        mode: MappingApplyMode = MappingApplyMode.PREPARED_ONLY,
        validator: MappingPreflightValidator | None = None,
    ) -> MappingApplyRequest:
        result = self.preflight_mapping_change_set_for_device(
            device_identity_key=device_identity_key,
            draft_rows=draft_rows,
            authoritative_snapshot_timestamp=authoritative_snapshot_timestamp,
            validator=validator,
        )
        return prepare_mapping_apply_request(
            preflight_result=result,
            mode=mode,
            created_timestamp=created_timestamp,
        )

    def trusted_session_inventory(self) -> dict[str, object]:
        trusted = TrustedSessionBuilder.build(
            shell_session=self.session,
            event_summary=self.services.events.summary(),
        )
        summary = trusted.summary
        signal_summary = self.session.ui_session.first_signal_summary
        channel_metadata = {} if signal_summary is None else {str(key): str(value) for key, value in signal_summary.channel_metadata.items()}
        return {
            'lifecycle_state': summary.lifecycle_state,
            'graph_status_label': summary.graph_status_label,
            'live_numeric_visible': summary.live_numeric_visible,
            'graph_visible': summary.graph_visible,
            'trace_point_count': summary.trace_point_count,
            'trace_span_seconds': summary.trace_span_seconds,
            'latest_value_age_seconds': summary.latest_value_age_seconds,
            'disconnect_count': summary.disconnect_count,
            'reconnect_count': summary.reconnect_count,
            'session_event_count': summary.session_event_count,
            'ready_for_operator': summary.ready_for_operator,
            'last_event_summary': summary.last_event_summary,
            'sparkline': summary.sparkline,
            'signal_quality_label': summary.signal_quality_label,
            'signal_freshness_label': summary.signal_freshness_label,
            'control_mode_label': summary.control_mode_label,
            'active_alarm_count': summary.active_alarm_count,
            'unacknowledged_alarm_count': summary.unacknowledged_alarm_count,
            'highest_active_severity': summary.highest_active_severity,
            'recent_action_count': summary.recent_action_count,
            'flight_record_ready': summary.flight_record_ready,
            'truthfulness_warnings': list(summary.truthfulness_warnings),
            'signal_provenance': {
                'source_device_key': None if signal_summary is None else signal_summary.source_device_key,
                'source_adapter_id': None if signal_summary is None else signal_summary.source_adapter_id,
                'device_identity_key': None if signal_summary is None else signal_summary.device_identity_key,
                'source_transport': None if signal_summary is None else signal_summary.source_transport,
                'hardware_channel': None if signal_summary is None else signal_summary.hardware_channel,
                'provenance_label': None if signal_summary is None else signal_summary.provenance_label,
                'channel_metadata': channel_metadata,
            },
            'alarm_summary': self.services.events.summary(),
            'active_alarm_rows': list(self.services.events.active_alarm_rows()),
            'recent_domain_events': list(self.services.events.recent_event_rows(limit=8)),
            'recent_events': [
                {
                    'timestamp': int(event.timestamp),
                    'category': event.category,
                    'summary': event.summary,
                    'phase_after': event.phase_after,
                }
                for event in summary.recent_events
            ],
            'recent_actions': [
                {
                    'timestamp': int(action.timestamp),
                    'category': action.category,
                    'summary': action.summary,
                    'outcome': action.outcome,
                    'actor_id': action.actor_id,
                    'target_kind': action.target_kind,
                    'target_id': action.target_id,
                }
                for action in summary.recent_actions
            ],
            'trace_numeric_points': list(trusted.trace_numeric_points),
        }

    def session_flight_record(self) -> dict[str, object]:
        trusted_inventory = self.trusted_session_inventory()
        replay_tape = FirstSignalReplayTape.from_summary(self.session.ui_session.first_signal_summary)
        return {
            'session_id': self.session.session_id,
            'actor': {
                'actor_id': str(self.session.actor_context.actor_id),
                'role_class': self.session.actor_context.role_class.value,
                'origin': self.session.actor_context.origin,
            },
            'control_posture': trusted_inventory.get('control_mode_label'),
            'first_signal_replay_tape': None if replay_tape is None else replay_tape.as_dict(),
            'trusted_session_inventory': trusted_inventory,
            'authorization_history': [
                {
                    'action': decision.action.value,
                    'allowed': decision.allowed,
                    'permission_family': decision.permission_family.value,
                    'reason_code': decision.reason_code.value,
                    'reason_text': decision.reason_text,
                    'actor_id': str(decision.actor_id),
                    'target_kind': decision.target_kind,
                    'target_id': decision.target_id,
                }
                for decision in self.session.authorization_history[-8:]
            ],
            'command_trace_count': len(self.session.command_traces),
            'alarm_lifecycle_count': len(self.session.alarm_lifecycles),
            'shell_evidence_count': len(self.session.shell_evidence_records),
            'operator_note_count': len(self.session.operator_notes),
            'last_persisted_session_summary_id': None if self.session.last_persisted_session_summary is None else self.session.last_persisted_session_summary.summary_id,
            'preferred_channel_key': self.session.ui_session.preferred_channel_key,
        }

    def build_persisted_session_summary(self, *, timestamp: EventTime) -> PersistedSessionSummary:
        trusted = TrustedSessionBuilder.build(
            shell_session=self.session,
            event_summary=self.services.events.summary(),
        ).summary
        first_signal = self.session.ui_session.first_signal_summary
        alarm_posture = None
        if trusted.active_alarm_count:
            alarm_posture = f"{trusted.active_alarm_count} active / {trusted.unacknowledged_alarm_count} unack"
        if trusted.lifecycle_state == 'live' and trusted.graph_status_label == 'live':
            completeness_label = 'complete'
        elif trusted.lifecycle_state in {'degraded', 'disconnected'}:
            completeness_label = 'degraded'
        else:
            completeness_label = 'partial'
        session_source_label = f"{self.session.restore_result.origin.value}_capture"
        summary = PersistedSessionSummary(
            summary_id=f"SUM-{self.session.session_id}-{int(timestamp)}",
            saved_at=timestamp,
            session_id=self.session.session_id,
            profile_id=self.session.profile_snapshot.profile_id,
            workspace_state=self.session.ui_session.workspace_state,
            preferred_adapter_id=self.session.ui_session.preferred_adapter_id or self.session.ui_session.active_adapter_id,
            preferred_device_key=self.session.ui_session.preferred_device_key or self.session.ui_session.canonical_active_device_key,
            preferred_channel_key=self.session.ui_session.preferred_channel_key or (None if first_signal is None else first_signal.point_key),
            control_mode_label=trusted.control_mode_label,
            signal_freshness_label=trusted.signal_freshness_label,
            last_signal_display_name=None if first_signal is None else first_signal.display_name,
            last_signal_value=None if first_signal is None else first_signal.latest_value,
            last_signal_units=None if first_signal is None else first_signal.engineering_units,
            alarm_posture=alarm_posture,
            recent_action_count=trusted.recent_action_count,
            flight_record_ready=trusted.flight_record_ready,
            signal_provenance_label=None if first_signal is None else first_signal.provenance_label,
            trace_preview=trusted.sparkline,
            session_source_label=session_source_label,
            completeness_label=completeness_label,
            last_event_summary=trusted.last_event_summary,
            operator_notes=self.session.operator_notes,
        )
        return summary

    def bench_persistence_snapshot(self, *, timestamp: EventTime) -> BenchPersistenceState:
        summary = self.build_persisted_session_summary(timestamp=timestamp)
        state = BenchPersistenceState(
            schema_version=1,
            saved_at=timestamp,
            profile_snapshot=self.session.profile_snapshot,
            preferred_adapter_id=self.session.ui_session.preferred_adapter_id or self.session.ui_session.active_adapter_id,
            preferred_device_key=self.session.ui_session.preferred_device_key or self.session.ui_session.canonical_active_device_key,
            preferred_channel_key=self.session.ui_session.preferred_channel_key or (None if self.session.ui_session.first_signal_summary is None else self.session.ui_session.first_signal_summary.point_key),
            historical_summary=summary,
            pending_note_draft=self.session.ui_session.pending_note_draft,
            restored_historical_only=True,
        )
        return state

    def save_bench_state(self, *, timestamp: EventTime) -> BenchPersistenceState:
        summary = self.build_persisted_session_summary(timestamp=timestamp)
        state = BenchPersistenceState(
            schema_version=1,
            saved_at=timestamp,
            profile_snapshot=self.session.profile_snapshot,
            preferred_adapter_id=self.session.ui_session.preferred_adapter_id or self.session.ui_session.active_adapter_id,
            preferred_device_key=self.session.ui_session.preferred_device_key or self.session.ui_session.canonical_active_device_key,
            preferred_channel_key=self.session.ui_session.preferred_channel_key or (None if self.session.ui_session.first_signal_summary is None else self.session.ui_session.first_signal_summary.point_key),
            historical_summary=summary,
            pending_note_draft=self.session.ui_session.pending_note_draft,
            restored_historical_only=True,
        )
        self.services.bench_state.save_summary(summary)
        self.services.bench_state.save_state(state)
        self.session = self.session.with_persisted_session_summary(summary)
        self.session = self.session.with_ui_session(
            self.session.ui_session.with_persistence_context(
                preferred_adapter_id=state.preferred_adapter_id or '',
                preferred_device_key=state.preferred_device_key or '',
                preferred_channel_key=state.preferred_channel_key or '',
                restored_historical_context_label='restored context remains historical until a live reconnect occurs',
                last_session_summary_id=summary.summary_id,
                last_session_summary_label=summary.last_signal_display_name or summary.preferred_channel_key or 'last session',
                session_note_count=len(summary.operator_notes),
                pending_note_draft=state.pending_note_draft,
            )
        )
        evidence = self._shell_evidence(
            timestamp=timestamp,
            suffix='BENCHSTATE',
            summary='bench continuity state saved',
            attributes={
                'summary_id': summary.summary_id,
                'preferred_adapter_id': '' if state.preferred_adapter_id is None else state.preferred_adapter_id,
                'preferred_channel_key': '' if state.preferred_channel_key is None else state.preferred_channel_key,
                'operator_note_count': str(len(summary.operator_notes)),
            },
        )
        self.session = self.session.append_shell_evidence(evidence)
        return state

    def restore_bench_state(self) -> BenchPersistenceState:
        state = self.services.bench_state.load_state()
        summary = state.historical_summary
        ui_session = self.session.ui_session.with_workspace_state(state.profile_snapshot.workspace_state).with_persistence_context(
            preferred_adapter_id=state.preferred_adapter_id or '',
            preferred_device_key=state.preferred_device_key or '',
            preferred_channel_key=state.preferred_channel_key or '',
            restored_historical_context_label='restored context remains historical until a live reconnect occurs',
            last_session_summary_id=None if summary is None else summary.summary_id,
            last_session_summary_label=None if summary is None else (summary.last_signal_display_name or summary.preferred_channel_key or 'last session'),
            session_note_count=0 if summary is None else len(summary.operator_notes),
            pending_note_draft=state.pending_note_draft,
        )
        self.session = self.session.with_profile_snapshot(state.profile_snapshot).with_ui_session(ui_session)
        if summary is not None:
            self.session = self.session.with_persisted_session_summary(summary)
        return state

    def set_pending_note_draft(self, *, note_text: str | None) -> None:
        self.session = self.session.with_ui_session(
            self.session.ui_session.with_persistence_context(pending_note_draft='' if note_text is None else note_text)
        )

    def add_operator_note(self, *, note_text: str, timestamp: EventTime, category: str = 'operator_note') -> OperatorNote:
        actor_id = str(self.session.actor_context.actor_id) if self.session.actor_context.actor_id is not None else None
        note = OperatorNote(
            note_id=f"NOTE-{self.session.session_id}-{int(timestamp)}-{len(self.session.operator_notes)+1}",
            timestamp=timestamp,
            text=note_text,
            category=category,
            actor_id=actor_id,
        )
        self.session = self.session.append_operator_note(note)
        self.session = self.session.with_ui_session(
            self.session.ui_session.with_persistence_context(session_note_count=len(self.session.operator_notes))
        )
        self.session = self.session.append_shell_evidence(
            self._shell_evidence(
                timestamp=timestamp,
                suffix='NOTE',
                summary='operator note captured',
                attributes={'category': category, 'note_id': note.note_id},
            )
        )
        return note

    def recent_persisted_summaries(self, *, limit: int = 5) -> tuple[PersistedSessionSummary, ...]:
        return self.services.bench_state.list_recent_summaries(limit=limit)

    def recent_session_review(self, *, limit: int = 5) -> tuple[SessionReviewListItem, ...]:
        return SessionReviewBuilder.build_recent_list(summaries=self.recent_persisted_summaries(limit=limit))

    def session_review_detail(self, *, summary_id: str) -> SessionReviewDetail:
        summary = self.services.bench_state.load_summary(summary_id)
        return SessionReviewBuilder.build_detail(summary)

    def generate_lightweight_session_report(self, *, summary_id: str, timestamp: EventTime) -> LightweightSessionReport:
        summary = self.services.bench_state.load_summary(summary_id)
        return SessionReviewBuilder.build_report(summary=summary, generated_at=timestamp, package_id=CURRENT_PACKAGE_ID, package_slug=CURRENT_PACKAGE_SLUG)

    def session_review_inventory(self, *, limit: int = 5) -> dict[str, object]:
        recent = self.recent_session_review(limit=limit)
        selected_detail = None
        if recent:
            detail = self.session_review_detail(summary_id=recent[0].summary_id)
            selected_detail = {
                'summary_id': detail.summary_id, 'saved_at': int(detail.saved_at), 'session_id': detail.session_id, 'summary_label': detail.summary_label, 'historical_label': detail.historical_label, 'session_source_label': detail.session_source_label, 'completeness_label': detail.completeness_label, 'preferred_adapter_id': detail.preferred_adapter_id, 'preferred_device_key': detail.preferred_device_key, 'preferred_channel_key': detail.preferred_channel_key, 'control_mode_label': detail.control_mode_label, 'signal_freshness_label': detail.signal_freshness_label, 'signal_provenance_label': detail.signal_provenance_label, 'last_signal_value': detail.last_signal_value, 'last_signal_units': detail.last_signal_units, 'alarm_posture': detail.alarm_posture, 'recent_action_count': detail.recent_action_count, 'flight_record_ready': detail.flight_record_ready, 'trace_preview': detail.trace_preview, 'last_event_summary': detail.last_event_summary, 'operator_notes': [note.export_summary() for note in detail.operator_notes],
            }
        return {
            'package_id': CURRENT_PACKAGE_ID, 'package_slug': CURRENT_PACKAGE_SLUG, 'review_count': len(recent),
            'recent_sessions': [{ 'summary_id': item.summary_id, 'saved_at': int(item.saved_at), 'summary_label': item.summary_label, 'historical_label': item.historical_label, 'session_source_label': item.session_source_label, 'preferred_adapter_id': item.preferred_adapter_id, 'preferred_device_key': item.preferred_device_key, 'preferred_channel_key': item.preferred_channel_key, 'signal_freshness_label': item.signal_freshness_label, 'control_mode_label': item.control_mode_label, 'alarm_posture': item.alarm_posture, 'note_count': item.note_count, 'completeness_label': item.completeness_label, 'flight_record_ready': item.flight_record_ready } for item in recent],
            'selected_detail': selected_detail,
        }

    def _lifecycle(self) -> ShellLifecycleOrchestrator:
        return ShellLifecycleOrchestrator(self.services)

    def _device_handler(self) -> ShellDeviceLifecycleHandler:
        return ShellDeviceLifecycleHandler(self)

    def _binding_handler(self) -> ShellBindingVariableHandler:
        return ShellBindingVariableHandler(self)

    def _workspace_handler(self) -> ShellWorkspaceProfileHandler:
        return ShellWorkspaceProfileHandler(self)

    def _command_handler(self) -> ShellCommandExportHandler:
        return ShellCommandExportHandler(self)

    def _automation_handler(self) -> ShellAutomationReviewHandler:
        return ShellAutomationReviewHandler(self)

    def _workspace_from_current(self, *, page: str | None = None, review_mode: GraphMode | None = None, visible_traces: tuple[TraceId, ...] | None = None) -> WorkspaceState:
        return WorkspaceState(
            page=self.session.ui_session.workspace_state.page if page is None else page,
            review_mode=self.session.ui_session.graph_session.mode if review_mode is None else review_mode,
            visible_traces=self.session.ui_session.workspace_state.visible_traces if visible_traces is None else visible_traces,
        )

    def _ui_session_with_lifecycle_update(
        self,
        *,
        phase: DeviceLifecyclePhase | None = None,
        detected_devices: tuple[DiscoveredDevice, ...] | None = None,
        active_device: DiscoveredDevice | None = None,
        active_adapter_id: str | None = None,
        onboarding_mode: str | None = None,
        known_device_restore_offer: str | None = None,
        available_workbenches: tuple[WorkbenchDescriptor, ...] | None = None,
        lifecycle_summary: DeviceLifecycleSummary | None = None,
        binding_review_summary: BindingReviewSummary | None = None,
        variable_health_summary: VariableHealthSummary | None = None,
        reconciliation_summary: ReconciliationSummary | None = None,
        workbench_review_state: WorkbenchReviewState | None = None,
        first_signal_summary: FirstSignalSummary | None = None,
    ) -> UISessionState:
        ui_session = self.session.ui_session
        if phase is not None:
            ui_session = ui_session.with_lifecycle_context(
                phase=phase,
                detected_devices=None if detected_devices is None else tuple(detected_devices),
                active_device=active_device,
                active_adapter_id=active_adapter_id,
                onboarding_mode=onboarding_mode,
                known_device_restore_offer=known_device_restore_offer,
                available_workbenches=None if available_workbenches is None else tuple(available_workbenches),
            )
        elif detected_devices is not None:
            ui_session = ui_session.with_detected_devices(tuple(detected_devices), phase=ui_session.device_lifecycle_phase)
        return ui_session.with_review_state(
            lifecycle_summary=lifecycle_summary,
            binding_review_summary=binding_review_summary,
            variable_health_summary=variable_health_summary,
            reconciliation_summary=reconciliation_summary,
            workbench_review_state=workbench_review_state,
            first_signal_summary=first_signal_summary,
        )

    def _record_lifecycle_transition_metrics(self, *, action: str, previous_ui_session: UISessionState, current_ui_session: UISessionState) -> None:
        metrics = self.services.runtime_metrics
        if metrics is None:
            return
        previous_phase = previous_ui_session.device_lifecycle_phase.value
        current_phase = current_ui_session.device_lifecycle_phase.value
        metrics.set_gauge('lifecycle.transition.previous_phase', previous_phase)
        metrics.set_gauge('lifecycle.transition.current_phase', current_phase)
        metrics.set_gauge('lifecycle.transition.changed', int(previous_phase != current_phase))
        transition = None if current_ui_session.lifecycle_summary is None else current_ui_session.lifecycle_summary.last_transition
        metrics.set_gauge('lifecycle.transition.last_trigger', action if transition is None else transition)

    def _commit_with_ui_session(self, action: str, *, ui_session: UISessionState, evidence: EvidenceRecord | None = None) -> ShellActionResult:
        previous_ui_session = self.session.ui_session
        self._record_lifecycle_transition_metrics(action=action, previous_ui_session=previous_ui_session, current_ui_session=ui_session)
        session = self.session.with_ui_session(ui_session)
        if evidence is not None:
            attributes = dict(evidence.attributes)
            attributes.setdefault('phase_before', previous_ui_session.device_lifecycle_phase.value)
            attributes.setdefault('phase_after', ui_session.device_lifecycle_phase.value)
            if ui_session.lifecycle_summary is not None and ui_session.lifecycle_summary.last_transition is not None:
                attributes.setdefault('transition', ui_session.lifecycle_summary.last_transition)
            evidence = replace(evidence, attributes=attributes)
            session = session.append_shell_evidence(evidence)
        return self._commit(action, session)

    def _sync_alarm_lifecycles_from_service(self) -> None:
        self.session = self.session.replace_alarm_lifecycles(self.services.events.export_lifecycles())

    def _event_alarm_summary(self) -> dict[str, object]:
        return self.services.events.summary()

    def _command_summary(self) -> dict[str, object]:
        return self.services.commands.summary()

    def _rule_summary(self) -> dict[str, object]:
        return self.services.rules.summary()

    def _sequence_summary(self) -> dict[str, object]:
        return self.services.sequences.summary()

    def _append_command_record(self, *, record: CommandRecord, timestamp: EventTime) -> None:
        self.services.commands.append(record)
        for evidence in record.evidence_records:
            self.session = self.session.append_shell_evidence(evidence)
        self.services.runtime_quality.record_operational_entry(
            timestamp=timestamp,
            record_type='command',
            payload=record.as_dict(),
        )

    def _recent_lifecycle_transition_trace(self, *, limit: int = 8) -> tuple[dict[str, object], ...]:
        rows: list[dict[str, object]] = []
        for record in self.session.shell_evidence_records:
            if 'phase_before' not in record.attributes or 'phase_after' not in record.attributes:
                continue
            rows.append(
                {
                    'evidence_id': str(record.evidence_id),
                    'timestamp': int(record.timestamp),
                    'summary': record.summary,
                    'phase_before': record.attributes.get('phase_before'),
                    'phase_after': record.attributes.get('phase_after'),
                    'transition': record.attributes.get('transition'),
                    'attributes': dict(sorted(record.attributes.items())),
                }
            )
        return tuple(rows[-limit:])

    def _incremental_runtime_summary(self) -> dict[str, object]:
        gauges = self.services.runtime_metrics.snapshot()['gauges']
        mapping = {
            'bindings.point_definition.last_replace_skipped': 'bindings.point_definition.last_replace_skipped',
            'bindings.review.scope.output.count': 'bindings.review.scope.output.count',
            'bindings.review.scope.signal.count': 'bindings.review.scope.signal.count',
            'lifecycle.changed_signal_ids.count': 'lifecycle.changed_signal_ids.count',
            'runtime.variables.requested_change_count': 'runtime.variables.requested_change_count',
            'runtime.variables.impacted_count': 'variables.impacted.count',
            'runtime.variables.evaluated_count': 'variables.last_evaluated.count',
            'runtime.variables.value_changed_count': 'runtime.variables.value_changed_count',
            'runtime.variables.state_changed_count': 'runtime.variables.state_changed_count',
            'runtime.variables.skipped_count': 'variables.skipped.count',
            'lifecycle.projected_points.count': 'lifecycle.projected_points.count',
            'lifecycle.projected_points.last_replace_skipped': 'lifecycle.projected_points.last_replace_skipped',
            'lifecycle.transition.changed': 'lifecycle.transition.changed',
            'lifecycle.transition.current_phase': 'lifecycle.transition.current_phase',
            'lifecycle.transition.last_trigger': 'lifecycle.transition.last_trigger',
            'lifecycle.transition.previous_phase': 'lifecycle.transition.previous_phase',
            'runtime.acquisition.queue.depth': 'runtime.acquisition.queue.depth',
            'runtime.acquisition.queue.dropped': 'runtime.acquisition.queue.dropped',
            'runtime.acquisition.queue.high_watermark': 'runtime.acquisition.queue.high_watermark',
            'runtime.journal.queue.depth': 'runtime.journal.queue.depth',
            'runtime.journal.queue.dropped': 'runtime.journal.queue.dropped',
            'runtime.presentation.coalesced_total': 'runtime.presentation.coalesced_total',
            'runtime.presentation.publish_total': 'runtime.presentation.publish_total',
            'runtime.variable.recent_count': 'runtime.variable.recent_count',
            'runtime.variable.transition_total': 'runtime.variable.transition_total',
            'events.active_alarm_count': 'events.active_alarm_count',
            'events.unacknowledged_alarm_count': 'events.unacknowledged_alarm_count',
            'events.recent_domain_event_count': 'events.recent_domain_event_count',
        }
        summary: dict[str, object] = {}
        for summary_key, gauge_key in mapping.items():
            if gauge_key in gauges:
                summary[summary_key] = gauges[gauge_key]
        return summary

    def _variable_snapshot_rows(self, *, limit: int = 12) -> tuple[dict[str, object], ...]:
        rows: list[dict[str, object]] = []
        for snapshot in self.services.variables.snapshots.values():
            rows.append(
                {
                    'variable_id': str(snapshot.variable_id),
                    'value': snapshot.value,
                    'quality': snapshot.quality.value,
                    'state': snapshot.state.value,
                    'timestamp': int(snapshot.timestamp),
                    'dependency_values': dict(sorted(snapshot.dependency_values.items())),
                }
            )
        rows.sort(key=lambda item: (str(item['variable_id']), int(item['timestamp'])))
        return tuple(rows[-max(1, limit):])

    def navigate(self, *, page: str, timestamp: EventTime) -> ShellActionResult:
        return self._workspace_handler().navigate(page=page, timestamp=timestamp)

    def set_trace_visibility(self, *, trace_id: TraceId, visible: bool, timestamp: EventTime) -> ShellActionResult:
        return self._workspace_handler().set_trace_visibility(trace_id=trace_id, visible=visible, timestamp=timestamp)

    def set_overlay(self, *, overlay_name: str, visible: bool, timestamp: EventTime) -> ShellActionResult:
        return self._workspace_handler().set_overlay(overlay_name=overlay_name, visible=visible, timestamp=timestamp)

    def select_history_range(self, *, start: EventTime, end: EventTime, timestamp: EventTime) -> ShellActionResult:
        return self._workspace_handler().select_history_range(start=start, end=end, timestamp=timestamp)

    def switch_graph_mode(self, *, mode: GraphMode, timestamp: EventTime) -> ShellActionResult:
        return self._workspace_handler().switch_graph_mode(mode=mode, timestamp=timestamp)

    def return_to_live(self, *, timestamp: EventTime) -> ShellActionResult:
        return self._workspace_handler().return_to_live(timestamp=timestamp)

    def save_profile(self, *, profile_id: ProfileId, timestamp: EventTime) -> ShellActionResult:
        return self._workspace_handler().save_profile(profile_id=profile_id, timestamp=timestamp)

    def save_autosave(self, *, timestamp: EventTime) -> ShellActionResult:
        return self._workspace_handler().save_autosave(timestamp=timestamp)

    def save_last_session(self, *, timestamp: EventTime) -> ShellActionResult:
        return self._workspace_handler().save_last_session(timestamp=timestamp)

    def restore_profile(self, *, profile_id: ProfileId, origin: RestoreOrigin, timestamp: EventTime) -> ShellActionResult:
        return self._workspace_handler().restore_profile(profile_id=profile_id, origin=origin, timestamp=timestamp)

    def submit_output_request(
        self,
        *,
        request_id: RequestId,
        output_id: OutputId,
        requested_value: str,
        actor: ActorId | None = None,
        authorization_state: AuthorizationState | None = None,
        requested_at: EventTime,
        applied_value: str | None = None,
        observed_value: str | None = None,
        applied_at: EventTime | None = None,
        observed_at: EventTime | None = None,
    ) -> ShellActionResult:
        return self._command_handler().submit_output_request(
            request_id=request_id,
            output_id=output_id,
            requested_value=requested_value,
            actor=actor,
            authorization_state=authorization_state,
            requested_at=requested_at,
            applied_value=applied_value,
            observed_value=observed_value,
            applied_at=applied_at,
            observed_at=observed_at,
        )

    def assert_alarm(self, *, alarm_id: AlarmId, timestamp: EventTime) -> ShellActionResult:
        return self._command_handler().assert_alarm(alarm_id=alarm_id, timestamp=timestamp)

    def acknowledge_alarm(
        self,
        *,
        alarm_id: AlarmId,
        actor: ActorId | None = None,
        authorization_state: AuthorizationState | None = None,
        timestamp: EventTime,
        command_id: str | None = None,
        correlation_id: str | None = None,
    ) -> ShellActionResult:
        return self._command_handler().acknowledge_alarm(
            alarm_id=alarm_id,
            actor=actor,
            authorization_state=authorization_state,
            timestamp=timestamp,
            command_id=command_id,
            correlation_id=correlation_id,
        )

    def submit_dry_run_adapter_command(
        self,
        *,
        command_id: str,
        adapter_id: str,
        point_id: str,
        requested_value: str,
        actor: ActorId | None = None,
        authorization_state: AuthorizationState | None = None,
        timestamp: EventTime,
        correlation_id: str | None = None,
    ) -> ShellActionResult:
        return self._command_handler().submit_dry_run_adapter_command(
            command_id=command_id,
            adapter_id=adapter_id,
            point_id=point_id,
            requested_value=requested_value,
            actor=actor,
            authorization_state=authorization_state,
            timestamp=timestamp,
            correlation_id=correlation_id,
        )

    def return_alarm_to_normal(self, *, alarm_id: AlarmId, timestamp: EventTime) -> ShellActionResult:
        return self._command_handler().return_alarm_to_normal(alarm_id=alarm_id, timestamp=timestamp)

    def build_export_intent(
        self,
        *,
        export_id: str,
        artifact_class: ExportArtifactClass,
        actor: ActorId,
        timestamp: EventTime,
        include_commands: bool = True,
        include_alarms: bool = True,
        include_restores: bool = True,
        include_shell_evidence: bool = True,
        include_profiles: bool = False,
        include_diagnostics: bool = False,
        origin: str = 'local-shell',
    ):
        return self._command_handler().build_export_intent(
            export_id=export_id,
            artifact_class=artifact_class,
            actor=actor,
            timestamp=timestamp,
            include_commands=include_commands,
            include_alarms=include_alarms,
            include_restores=include_restores,
            include_shell_evidence=include_shell_evidence,
            include_profiles=include_profiles,
            include_diagnostics=include_diagnostics,
            origin=origin,
        )

    def export_review_artifact(
        self,
        *,
        export_id: str,
        manifest_id: str,
        actor: ActorId,
        timestamp: EventTime,
        include_profiles: bool = False,
        include_diagnostics: bool = False,
        diagnostics: tuple[dict[str, object], ...] = (),
    ) -> BundleBuildResult:
        return self._command_handler().export_review_artifact(
            export_id=export_id,
            manifest_id=manifest_id,
            actor=actor,
            timestamp=timestamp,
            include_profiles=include_profiles,
            include_diagnostics=include_diagnostics,
            diagnostics=diagnostics,
        )

    def export_evidence_bundle(
        self,
        *,
        export_id: str,
        bundle_id: str,
        manifest_id: str,
        actor: ActorId,
        timestamp: EventTime,
        include_profiles: bool = False,
        include_diagnostics: bool = False,
        diagnostics: tuple[dict[str, object], ...] = (),
    ) -> BundleBuildResult:
        return self._command_handler().export_evidence_bundle(
            export_id=export_id,
            bundle_id=bundle_id,
            manifest_id=manifest_id,
            actor=actor,
            timestamp=timestamp,
            include_profiles=include_profiles,
            include_diagnostics=include_diagnostics,
            diagnostics=diagnostics,
        )

    def build_evidence_bundle(self, *, bundle_id: str) -> EvidenceBundle:
        return self._command_handler().build_evidence_bundle(bundle_id=bundle_id)

    def discover_devices(self, *, timestamp: EventTime) -> tuple[DiscoveredDevice, ...]:
        return self._device_handler().discover_devices(timestamp=timestamp)

    def select_detected_device(self, *, device_key: str, timestamp: EventTime) -> ShellActionResult:
        return self._device_handler().select_detected_device(device_key=device_key, timestamp=timestamp)

    def begin_quick_start(self, *, timestamp: EventTime) -> ShellActionResult:
        return self._device_handler().begin_quick_start(timestamp=timestamp)

    def enter_advanced_setup(self, *, timestamp: EventTime) -> ShellActionResult:
        return self._device_handler().enter_advanced_setup(timestamp=timestamp)

    def remember_active_device(self, *, timestamp: EventTime) -> ShellActionResult:
        return self._device_handler().remember_active_device(timestamp=timestamp)

    def mark_active_device_disconnected(self, *, timestamp: EventTime) -> ShellActionResult:
        return self._device_handler().mark_active_device_disconnected(timestamp=timestamp)

    def reconnect_active_device(self, *, timestamp: EventTime) -> ShellActionResult:
        return self._device_handler().reconnect_active_device(timestamp=timestamp)

    def poll_adapters(self, *, timestamp: EventTime) -> tuple[AdapterPollResult, ...]:
        return self._device_handler().poll_adapters(timestamp=timestamp)

    def bind_logical_signal_to_point(
        self,
        *,
        logical_signal_id: SignalId,
        point_key: str,
        display_name: str | None = None,
        binding_policy: BindingPolicy = BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
        timestamp: EventTime,
    ) -> ShellActionResult:
        return self._binding_handler().bind_logical_signal_to_point(
            logical_signal_id=logical_signal_id,
            point_key=point_key,
            display_name=display_name,
            binding_policy=binding_policy,
            timestamp=timestamp,
        )

    def register_variable_definition(self, *, definition: VariableDefinition, timestamp: EventTime) -> ShellActionResult:
        return self._binding_handler().register_variable_definition(definition=definition, timestamp=timestamp)

    def evaluate_variables(self, *, timestamp: EventTime) -> ShellActionResult:
        return self._binding_handler().evaluate_variables(timestamp=timestamp)

    def register_rule_definition(self, *, definition: RuleDefinition, timestamp: EventTime) -> ShellActionResult:
        return self._automation_handler().register_rule_definition(definition=definition, timestamp=timestamp)

    def register_sequence_definition(self, *, definition: SequenceDefinition, timestamp: EventTime) -> ShellActionResult:
        return self._automation_handler().register_sequence_definition(definition=definition, timestamp=timestamp)

    def start_sequence(self, *, sequence_id: str, timestamp: EventTime) -> ShellActionResult:
        return self._automation_handler().start_sequence(sequence_id=sequence_id, timestamp=timestamp)

    def evaluate_automation(self, *, timestamp: EventTime) -> ShellActionResult:
        return self._automation_handler().evaluate_automation(timestamp=timestamp)

    def lifecycle_review_bundle(self) -> dict[str, object]:
        return self._automation_handler().lifecycle_review_bundle()

    def submit_output_request_via_adapter(
        self,
        *,
        request_id: RequestId,
        output_id: OutputId,
        adapter_id: str,
        point_id: str,
        requested_value: str,
        actor: ActorId | None = None,
        authorization_state: AuthorizationState | None = None,
        requested_at: EventTime,
        applied_value: str | None = None,
        observed_value: str | None = None,
        applied_at: EventTime | None = None,
        observed_at: EventTime | None = None,
    ) -> ShellActionResult:
        return self._command_handler().submit_output_request_via_adapter(
            request_id=request_id,
            output_id=output_id,
            adapter_id=adapter_id,
            point_id=point_id,
            requested_value=requested_value,
            actor=actor,
            authorization_state=authorization_state,
            requested_at=requested_at,
            applied_value=applied_value,
            observed_value=observed_value,
            applied_at=applied_at,
            observed_at=observed_at,
        )
