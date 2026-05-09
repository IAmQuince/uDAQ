from __future__ import annotations

from dataclasses import dataclass, field, replace

from universaldaq.common import EvidenceRecord
from universaldaq.events import AlarmLifecycle
from universaldaq.historian import BundleBuildResult, ExportIntent
from universaldaq.outputs import CommandTrace
from universaldaq.profiles import OperatorNote, PersistedSessionSummary, ProfileSnapshot, RestoreResult
from universaldaq.security import ActorContext, AuthorizationDecision
from universaldaq.ui.session_state import UISessionState


@dataclass(frozen=True, slots=True, kw_only=True)
class ShellSession:
    session_id: str
    profile_snapshot: ProfileSnapshot
    restore_result: RestoreResult
    ui_session: UISessionState
    actor_context: ActorContext
    granted_permission_families: tuple[str, ...] = field(default_factory=tuple)
    command_traces: tuple[CommandTrace, ...] = field(default_factory=tuple)
    alarm_lifecycles: tuple[AlarmLifecycle, ...] = field(default_factory=tuple)
    shell_evidence_records: tuple[EvidenceRecord, ...] = field(default_factory=tuple)
    evidence_bundle_ids: tuple[str, ...] = field(default_factory=tuple)
    last_export_intent: ExportIntent | None = None
    last_bundle_id: str | None = None
    last_manifest_id: str | None = None
    last_review_artifact_id: str | None = None
    last_export_summary: str | None = None
    last_export_warning_count: int = 0
    export_history_ids: tuple[str, ...] = field(default_factory=tuple)
    last_authorization_decision: AuthorizationDecision | None = None
    authorization_history: tuple[AuthorizationDecision, ...] = field(default_factory=tuple)
    operator_notes: tuple[OperatorNote, ...] = field(default_factory=tuple)
    last_persisted_session_summary: PersistedSessionSummary | None = None

    @property
    def current_page(self) -> str:
        return self.ui_session.page

    @property
    def current_graph_mode(self) -> str:
        return self.ui_session.graph_session.mode.value

    @property
    def active_overlays(self) -> tuple[str, ...]:
        return self.ui_session.overlays

    def with_profile_snapshot(self, profile_snapshot: ProfileSnapshot) -> 'ShellSession':
        return replace(self, profile_snapshot=profile_snapshot)

    def with_restore_result(self, restore_result: RestoreResult) -> 'ShellSession':
        return replace(self, restore_result=restore_result)

    def with_ui_session(self, ui_session: UISessionState) -> 'ShellSession':
        return replace(self, ui_session=ui_session)

    def with_last_export_intent(self, export_intent: ExportIntent) -> 'ShellSession':
        return replace(self, last_export_intent=export_intent)

    def with_actor_context(self, actor_context: ActorContext, granted_permission_families: tuple[str, ...]) -> 'ShellSession':
        return replace(
            self,
            actor_context=actor_context,
            granted_permission_families=granted_permission_families,
            ui_session=self.ui_session.with_authorization_context(
                actor_role_label=actor_context.role_label,
                granted_capabilities=granted_permission_families,
            ),
        )

    def append_command_trace(self, command_trace: CommandTrace) -> 'ShellSession':
        return replace(self, command_traces=self.command_traces + (command_trace,))

    def record_alarm_lifecycle(self, lifecycle: AlarmLifecycle) -> 'ShellSession':
        retained = tuple(item for item in self.alarm_lifecycles if item.alarm_id != lifecycle.alarm_id)
        return replace(self, alarm_lifecycles=retained + (lifecycle,))


    def replace_alarm_lifecycles(self, lifecycles: tuple[AlarmLifecycle, ...]) -> 'ShellSession':
        return replace(self, alarm_lifecycles=tuple(lifecycles))

    def append_shell_evidence(self, evidence_record: EvidenceRecord) -> 'ShellSession':
        return replace(self, shell_evidence_records=self.shell_evidence_records + (evidence_record,))

    def append_evidence_bundle(self, bundle_id: str) -> 'ShellSession':
        return replace(self, evidence_bundle_ids=self.evidence_bundle_ids + (bundle_id,))

    def record_authorization_decision(self, decision: AuthorizationDecision) -> 'ShellSession':
        return replace(
            self,
            last_authorization_decision=decision,
            authorization_history=self.authorization_history + (decision,),
            ui_session=self.ui_session.with_authorization_decision(decision),
        )

    def append_operator_note(self, note: OperatorNote) -> 'ShellSession':
        return replace(self, operator_notes=self.operator_notes + (note,))

    def with_persisted_session_summary(self, summary: PersistedSessionSummary) -> 'ShellSession':
        return replace(self, last_persisted_session_summary=summary)

    def record_export_result(self, result: BundleBuildResult) -> 'ShellSession':
        review_artifact_id = None if result.review_artifact is None else result.review_artifact.artifact_id
        if result.authorization_decision is not None and not result.authorization_decision.allowed:
            export_summary = f'{result.export_intent.artifact_class.value} denied ({result.authorization_decision.reason_text})'
            return replace(
                self,
                last_export_intent=result.export_intent,
                last_export_summary=export_summary,
                last_export_warning_count=len(result.warnings),
                ui_session=self.ui_session.with_export_result(
                    manifest_id=None,
                    summary=export_summary,
                    warning_count=len(result.warnings),
                ),
            )
        export_summary = (
            f"{result.export_intent.artifact_class.value} exported "
            f"({len(result.bundle.records)} records, {len(result.manifest.artifacts)} artifacts)"
        )
        bundle_ids = self.evidence_bundle_ids
        if result.bundle.bundle_id not in bundle_ids:
            bundle_ids = bundle_ids + (result.bundle.bundle_id,)
        history_ids = self.export_history_ids
        if result.export_intent.export_id not in history_ids:
            history_ids = history_ids + (result.export_intent.export_id,)
        return replace(
            self,
            last_export_intent=result.export_intent,
            last_bundle_id=result.bundle.bundle_id,
            last_manifest_id=result.manifest.manifest_id,
            last_review_artifact_id=review_artifact_id,
            last_export_summary=export_summary,
            last_export_warning_count=len(result.warnings),
            evidence_bundle_ids=bundle_ids,
            export_history_ids=history_ids,
        )
