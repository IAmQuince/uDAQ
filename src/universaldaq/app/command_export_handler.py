from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from universaldaq.commands import CommandDispatchStatus, CommandIntent, CommandRecordFactory, CommandRejectionCode
from universaldaq.common import (
    ActorId,
    AlarmId,
    AuthorizationState,
    EventTime,
    ExportArtifactClass,
    OutputId,
    RequestId,
    as_event_time,
)
from universaldaq.adapters import AdapterCommandRequest, DeviceLifecyclePhase
from universaldaq.historian import BundleBuildResult, EvidenceBundle
from universaldaq.outputs import OutputArbiter
from universaldaq.security import GovernedAction

if TYPE_CHECKING:
    from .controller import ShellActionResult, ShellController


@dataclass(slots=True)
class ShellCommandExportHandler:
    controller: 'ShellController'

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
    ) -> 'ShellActionResult':
        if authorization_state is not None and authorization_state != AuthorizationState.ALLOWED:
            request_actor = self.controller.session.actor_context.actor_id if actor is None else actor
            request = OutputArbiter.build_request(
                request_id=request_id,
                output_id=output_id,
                requested_value=requested_value,
                actor=request_actor,
                requested_at=requested_at,
            )
            trace = self.controller.services.outputs.submit(
                request=request,
                authorization_state=authorization_state,
                applied_value=applied_value,
                observed_value=observed_value,
                applied_at=applied_at,
                observed_at=observed_at,
            )
            return self.controller._commit('submit_output_request', self.controller.session.append_command_trace(trace))
        decision = self.controller._authorize(
            action=GovernedAction.ISSUE_OUTPUT_COMMAND,
            actor=actor,
            authorization_state=authorization_state,
            target_kind='output',
            target_id=str(output_id),
            timestamp=requested_at,
        )
        request = OutputArbiter.build_request(
            request_id=request_id,
            output_id=output_id,
            requested_value=requested_value,
            actor=decision.actor_id,
            requested_at=requested_at,
        )
        trace = self.controller.services.outputs.submit(
            request=request,
            authorization_decision=decision,
            authorization_state=decision.authorization_state,
            applied_value=applied_value,
            observed_value=observed_value,
            applied_at=applied_at,
            observed_at=observed_at,
        )
        return self.controller._commit('submit_output_request', self.controller.session.append_command_trace(trace))

    def assert_alarm(self, *, alarm_id: AlarmId, timestamp: EventTime) -> 'ShellActionResult':
        lifecycle = self.controller.services.events.assert_alarm(alarm_id, timestamp)
        self.controller.services.runtime_quality.record_operational_entry(
            timestamp=timestamp,
            record_type='alarm_transition',
            payload={'alarm_id': str(alarm_id), 'state': 'asserted', 'source': 'manual'},
        )
        self.controller._sync_alarm_lifecycles_from_service()
        return self.controller._commit('assert_alarm', self.controller.session.record_alarm_lifecycle(lifecycle))

    def acknowledge_alarm(
        self,
        *,
        alarm_id: AlarmId,
        actor: ActorId | None = None,
        authorization_state: AuthorizationState | None = None,
        timestamp: EventTime,
        command_id: str | None = None,
        correlation_id: str | None = None,
    ) -> 'ShellActionResult':
        request_actor = self.controller.session.actor_context.actor_id if actor is None else actor
        intent = CommandIntent(
            command_id=self.controller._ack_command_id(alarm_id=alarm_id, actor=request_actor, timestamp=timestamp) if command_id is None else command_id,
            command_kind='ack_alarm',
            target_kind='alarm',
            target_id=str(alarm_id),
            requested_by=request_actor,
            requested_at=timestamp,
            correlation_id=self.controller._ack_correlation_id(alarm_id=alarm_id, timestamp=timestamp) if correlation_id is None else correlation_id,
            requested_payload={'alarm_id': str(alarm_id)},
            dry_run=False,
        )
        decision = self.controller._authorize(
            action=GovernedAction.ACK_ALARM,
            actor=actor,
            authorization_state=authorization_state,
            target_kind='alarm',
            target_id=str(alarm_id),
            timestamp=timestamp,
        )
        alarm_exists = (
            alarm_id in self.controller.services.events.active_statuses
            or alarm_id in self.controller.services.events.lifecycles
            or alarm_id in self.controller.services.events.definitions
        )
        if not alarm_exists:
            record = CommandRecordFactory.rejected(
                intent=intent,
                authorization_state=decision.authorization_state,
                rejection_code=CommandRejectionCode.INVALID_TARGET,
                rejection_reason='alarm target does not exist in the bounded shell slice',
                authorization_decision=decision,
                governed_action=GovernedAction.ACK_ALARM.value,
            )
            self.controller._append_command_record(record=record, timestamp=timestamp)
            return self.controller._commit('acknowledge_alarm', self.controller.session)
        lifecycle, event = self.controller.services.events.acknowledge_with_event(
            alarm_id=alarm_id,
            actor=decision.actor_id,
            timestamp=timestamp,
            authorization_decision=decision,
            event_id=f'EVT-ACK-{intent.command_id}',
            correlation_id=intent.correlation_id,
        )
        self.controller.services.runtime_quality.record_operational_entry(
            timestamp=timestamp,
            record_type='alarm_transition',
            payload={
                'alarm_id': str(alarm_id),
                'state': 'acknowledged' if decision.allowed else 'acknowledge_denied',
                'actor': str(decision.actor_id),
                'allowed': decision.allowed,
            },
        )
        if event is not None:
            self.controller.services.runtime_quality.record_operational_entry(
                timestamp=timestamp,
                record_type='event',
                payload=event.as_dict(),
            )
        if not decision.allowed:
            record = CommandRecordFactory.rejected(
                intent=intent,
                authorization_state=decision.authorization_state,
                rejection_code=CommandRejectionCode.AUTHORIZATION_DENIED,
                rejection_reason=decision.reason_text,
                authorization_decision=decision,
                governed_action=GovernedAction.ACK_ALARM.value,
                result_payload={'alarm_id': str(alarm_id)},
            )
        else:
            record = CommandRecordFactory.completed(
                intent=intent,
                authorization_state=decision.authorization_state,
                dispatch_status=CommandDispatchStatus.COMPLETED,
                result_summary='alarm acknowledged',
                authorization_decision=decision,
                governed_action=GovernedAction.ACK_ALARM.value,
                result_payload={'alarm_id': str(alarm_id), 'event_emitted': event is not None},
            )
        self.controller._append_command_record(record=record, timestamp=timestamp)
        self.controller._sync_alarm_lifecycles_from_service()
        return self.controller._commit('acknowledge_alarm', self.controller.session.record_alarm_lifecycle(lifecycle))

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
    ) -> 'ShellActionResult':
        request_actor = self.controller.session.actor_context.actor_id if actor is None else actor
        intent = CommandIntent(
            command_id=command_id,
            command_kind='dry_run_output_request',
            target_kind='adapter_point',
            target_id=f'{adapter_id}:{point_id}',
            requested_by=request_actor,
            requested_at=timestamp,
            correlation_id=correlation_id,
            requested_payload={'adapter_id': adapter_id, 'point_id': point_id, 'requested_value': requested_value},
            dry_run=True,
        )
        decision = self.controller._authorize(
            action=GovernedAction.ISSUE_OUTPUT_COMMAND,
            actor=actor,
            authorization_state=authorization_state,
            target_kind='adapter_point',
            target_id=f'{adapter_id}:{point_id}',
            timestamp=timestamp,
        )
        adapter = self.controller.services.adapters.adapters.get(adapter_id)
        if not decision.allowed:
            record = CommandRecordFactory.rejected(
                intent=intent,
                authorization_state=decision.authorization_state,
                rejection_code=CommandRejectionCode.AUTHORIZATION_DENIED,
                rejection_reason=decision.reason_text,
                authorization_decision=decision,
                governed_action=GovernedAction.ISSUE_OUTPUT_COMMAND.value,
            )
            self.controller._append_command_record(record=record, timestamp=timestamp)
            return self.controller._commit('submit_dry_run_adapter_command', self.controller.session)
        if adapter is None:
            record = CommandRecordFactory.rejected(
                intent=intent,
                authorization_state=decision.authorization_state,
                rejection_code=CommandRejectionCode.INVALID_TARGET,
                rejection_reason='adapter target was not found',
                authorization_decision=decision,
                governed_action=GovernedAction.ISSUE_OUTPUT_COMMAND.value,
            )
            self.controller._append_command_record(record=record, timestamp=timestamp)
            return self.controller._commit('submit_dry_run_adapter_command', self.controller.session)
        capability = adapter.capability()
        point_exists = any(point.point_id == point_id for point in capability.readable_points + capability.writable_points)
        if not point_exists:
            record = CommandRecordFactory.rejected(
                intent=intent,
                authorization_state=decision.authorization_state,
                rejection_code=CommandRejectionCode.INVALID_TARGET,
                rejection_reason='point target was not found on adapter capability inventory',
                authorization_decision=decision,
                governed_action=GovernedAction.ISSUE_OUTPUT_COMMAND.value,
            )
            self.controller._append_command_record(record=record, timestamp=timestamp)
            return self.controller._commit('submit_dry_run_adapter_command', self.controller.session)
        if self.controller.session.ui_session.device_lifecycle_phase != DeviceLifecyclePhase.LIVE:
            record = CommandRecordFactory.rejected(
                intent=intent,
                authorization_state=decision.authorization_state,
                rejection_code=CommandRejectionCode.STATE_GATE_FAILED,
                rejection_reason='dry-run command requires the bounded shell slice to be live',
                authorization_decision=decision,
                governed_action=GovernedAction.ISSUE_OUTPUT_COMMAND.value,
            )
            self.controller._append_command_record(record=record, timestamp=timestamp)
            return self.controller._commit('submit_dry_run_adapter_command', self.controller.session)
        if not capability.supports_write(point_id):
            record = CommandRecordFactory.rejected(
                intent=intent,
                authorization_state=decision.authorization_state,
                rejection_code=CommandRejectionCode.UNSUPPORTED_CAPABILITY,
                rejection_reason='target point does not advertise write capability',
                authorization_decision=decision,
                governed_action=GovernedAction.ISSUE_OUTPUT_COMMAND.value,
                result_payload={'adapter_kind': capability.adapter_kind.value, 'point_id': point_id},
            )
            self.controller._append_command_record(record=record, timestamp=timestamp)
            return self.controller._commit('submit_dry_run_adapter_command', self.controller.session)
        record = CommandRecordFactory.completed(
            intent=intent,
            authorization_state=decision.authorization_state,
            dispatch_status=CommandDispatchStatus.DRY_RUN_COMPLETED,
            result_summary='dry-run command admitted without hardware dispatch',
            authorization_decision=decision,
            governed_action=GovernedAction.ISSUE_OUTPUT_COMMAND.value,
            result_payload={'adapter_id': adapter_id, 'point_id': point_id, 'requested_value': requested_value},
        )
        self.controller._append_command_record(record=record, timestamp=timestamp)
        return self.controller._commit('submit_dry_run_adapter_command', self.controller.session)

    def return_alarm_to_normal(self, *, alarm_id: AlarmId, timestamp: EventTime) -> 'ShellActionResult':
        lifecycle = self.controller.services.events.return_to_normal(alarm_id, timestamp)
        self.controller.services.runtime_quality.record_operational_entry(
            timestamp=timestamp,
            record_type='alarm_transition',
            payload={'alarm_id': str(alarm_id), 'state': 'returned_to_normal', 'source': 'manual'},
        )
        self.controller._sync_alarm_lifecycles_from_service()
        return self.controller._commit('return_alarm_to_normal', self.controller.session.record_alarm_lifecycle(lifecycle))

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
        scope = self.controller.services.historian.resolve_export_scope(
            graph_mode=self.controller.session.ui_session.graph_session.mode,
            selected_range=self.controller.session.ui_session.selected_range,
            selected_pages=(self.controller.session.ui_session.page,),
            selected_trace_ids=tuple(str(item) for item in self.controller.session.ui_session.workspace_state.visible_traces),
            overlays=self.controller.session.ui_session.overlays,
            include_commands=include_commands,
            include_alarms=include_alarms,
            include_restores=include_restores,
            include_shell_evidence=include_shell_evidence,
            include_profiles=include_profiles,
            include_diagnostics=include_diagnostics,
        )
        intent = self.controller.services.historian.build_export_intent(
            export_id=export_id,
            artifact_class=artifact_class,
            requested_by_actor=actor,
            session_id=self.controller.session.session_id,
            requested_at=int(timestamp),
            authority_state=self.controller.session.ui_session.authority_surface.authorization_state,
            scope=scope,
            origin=origin,
        )
        preview = (
            f"{artifact_class.value}: page={self.controller.session.ui_session.page}; "
            f"mode={scope.graph_mode.value}; traces={len(scope.selected_trace_ids)}; overlays={len(scope.overlays)}"
        )
        ui_session = self.controller.session.ui_session.with_export_preview(preview)
        self.controller.session = self.controller.session.with_last_export_intent(intent).with_ui_session(ui_session)
        return intent

    def _export_with_policy(
        self,
        *,
        export_id: str,
        bundle_id: str,
        manifest_id: str,
        artifact_class: ExportArtifactClass,
        actor: ActorId,
        timestamp: EventTime,
        include_profiles: bool,
        include_diagnostics: bool,
        diagnostics: tuple[dict[str, object], ...],
    ) -> BundleBuildResult:
        intent = self.build_export_intent(
            export_id=export_id,
            artifact_class=artifact_class,
            actor=actor,
            timestamp=timestamp,
            include_profiles=include_profiles,
            include_diagnostics=include_diagnostics,
        )
        decision = self.controller._authorize(
            action={
                ExportArtifactClass.REVIEW_ARTIFACT: GovernedAction.EXPORT_REVIEW_ARTIFACT,
                ExportArtifactClass.EVIDENCE_BUNDLE: GovernedAction.EXPORT_EVIDENCE_BUNDLE,
                ExportArtifactClass.DIAGNOSTIC_SNAPSHOT: GovernedAction.EXPORT_DIAGNOSTIC_SNAPSHOT,
                ExportArtifactClass.SIMPLE_EXPORT: GovernedAction.EXPORT_REVIEW_ARTIFACT,
            }[artifact_class],
            actor=actor,
            authorization_state=None,
            target_kind='export_artifact',
            target_id=artifact_class.value,
            timestamp=timestamp,
        )
        if not decision.allowed:
            result = self.controller._denied_export_result(
                export_intent=intent,
                bundle_id=bundle_id,
                manifest_id=manifest_id,
                decision=decision,
            )
            self.controller.session = self.controller.session.record_export_result(result)
            return result
        result = self.controller.services.historian.build_bundle_from_intent(
            intent=intent,
            bundle_id=bundle_id,
            manifest_id=manifest_id,
            command_traces=self.controller.session.command_traces,
            restore_results=(self.controller.session.restore_result,),
            alarm_lifecycles=self.controller.session.alarm_lifecycles,
            session_records=self.controller.session.shell_evidence_records,
            overlays=self.controller.session.ui_session.overlays,
            profile_snapshots=(self.controller.session.profile_snapshot,) if include_profiles else (),
            diagnostics=diagnostics if include_diagnostics else (),
        )
        result = replace(result, authorization_decision=decision)
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='EXPORT',
            summary=f'{artifact_class.value} exported',
            attributes={'export_id': export_id, 'manifest_id': manifest_id, 'artifact_class': intent.artifact_class.value},
        )
        session = self.controller.session.append_shell_evidence(evidence).record_export_result(result)
        session = session.with_ui_session(
            session.ui_session.with_export_result(
                manifest_id=result.manifest.manifest_id,
                summary=session.last_export_summary,
                warning_count=session.last_export_warning_count,
            )
        )
        self.controller.session = session
        return result

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
        return self._export_with_policy(
            export_id=export_id,
            bundle_id=f'{export_id}-BUNDLE',
            manifest_id=manifest_id,
            artifact_class=ExportArtifactClass.REVIEW_ARTIFACT,
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
        return self._export_with_policy(
            export_id=export_id,
            bundle_id=bundle_id,
            manifest_id=manifest_id,
            artifact_class=ExportArtifactClass.EVIDENCE_BUNDLE,
            actor=actor,
            timestamp=timestamp,
            include_profiles=include_profiles,
            include_diagnostics=include_diagnostics,
            diagnostics=diagnostics,
        )

    def build_evidence_bundle(self, *, bundle_id: str) -> EvidenceBundle:
        timestamp = as_event_time(max(1, int(self.controller.session.restore_result.restored_at or 0)) + len(self.controller.session.evidence_bundle_ids) + 1)
        intent = self.controller.services.historian.build_export_intent(
            export_id=bundle_id,
            artifact_class=ExportArtifactClass.EVIDENCE_BUNDLE,
            requested_by_actor=self.controller.DEFAULT_EXPORT_ACTOR,
            session_id=self.controller.session.session_id,
            requested_at=int(timestamp),
            authority_state=AuthorizationState.ALLOWED,
            scope=self.controller.services.historian.resolve_export_scope(
                graph_mode=self.controller.session.ui_session.graph_session.mode,
                selected_range=self.controller.session.ui_session.selected_range,
                selected_pages=(self.controller.session.ui_session.page,),
                selected_trace_ids=tuple(str(item) for item in self.controller.session.ui_session.workspace_state.visible_traces),
                overlays=self.controller.session.ui_session.overlays,
            ),
            origin='service-wrapper',
        )
        result = self.controller.services.historian.build_bundle_from_intent(
            intent=intent,
            bundle_id=bundle_id,
            manifest_id=f'{bundle_id}-MANIFEST',
            command_traces=self.controller.session.command_traces,
            restore_results=(self.controller.session.restore_result,),
            alarm_lifecycles=self.controller.session.alarm_lifecycles,
            session_records=self.controller.session.shell_evidence_records,
            overlays=self.controller.session.ui_session.overlays,
        )
        result = replace(result, authorization_decision=None)
        self.controller.session = self.controller.session.record_export_result(result)
        return result.bundle

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
    ) -> 'ShellActionResult':
        result = self.submit_output_request(
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
        trace = result.session.command_traces[-1]
        if trace.authorization_denied or trace.rejection_phase == 'arbitration':
            return result
        adapter_request = AdapterCommandRequest(
            adapter_id=adapter_id,
            point_id=point_id,
            request_id=request_id,
            output_id=output_id,
            requested_value=requested_value,
            requested_at=requested_at,
            actor_id=trace.request.actor,
            authorization_decision=trace.authorization_decision,
        )
        adapter_result = self.controller.services.adapters.submit_command(adapter_request)
        updated_trace = self.controller.services.outputs.attach_adapter_result(request_id=str(request_id), adapter_result=adapter_result)
        if updated_trace is not None:
            traces = list(self.controller.session.command_traces)
            traces[-1] = updated_trace
            self.controller.session = replace(self.controller.session, command_traces=tuple(traces))
            for record in adapter_result.evidence_records():
                self.controller.session = self.controller.session.append_shell_evidence(record)
        return self.controller._commit('submit_output_request_via_adapter', self.controller.session)
