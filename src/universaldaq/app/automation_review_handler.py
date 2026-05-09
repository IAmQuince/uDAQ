from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from universaldaq.automation import GovernedActionClaimStatus
from universaldaq.common import AlarmId, ActorId, EventTime
from universaldaq.runtime import (
    build_canonical_runtime_evidence_bundle,
    build_runtime_event_taxonomy,
    build_runtime_metric_layers,
    build_runtime_reviewer_rollup,
    build_runtime_semantic_state,
    build_runtime_truth_surface_inventory,
    build_runtime_vocabulary_map,
)

if TYPE_CHECKING:
    from .controller import ShellActionResult, ShellController


@dataclass(slots=True)
class ShellAutomationReviewHandler:
    controller: 'ShellController'

    def register_rule_definition(self, *, definition, timestamp: EventTime) -> 'ShellActionResult':
        self.controller.services.rules.register(definition)
        self.controller.services.runtime_quality.record_operational_entry(
            timestamp=timestamp,
            record_type='rule_definition',
            payload=definition.as_dict(),
        )
        return self.controller._commit('register_rule_definition', self.controller.session)

    def register_sequence_definition(self, *, definition, timestamp: EventTime) -> 'ShellActionResult':
        self.controller.services.sequences.register(definition)
        self.controller.services.runtime_quality.record_operational_entry(
            timestamp=timestamp,
            record_type='sequence_definition',
            payload=definition.as_dict(),
        )
        return self.controller._commit('register_sequence_definition', self.controller.session)

    def start_sequence(self, *, sequence_id: str, timestamp: EventTime) -> 'ShellActionResult':
        rows = self.controller.services.sequences.start(sequence_id=sequence_id, timestamp=timestamp)
        for row in rows:
            self.controller.services.runtime_quality.record_operational_entry(
                timestamp=timestamp,
                record_type='sequence_transition',
                payload=row.as_dict(),
            )
        return self.controller._commit('start_sequence', self.controller.session)

    def evaluate_automation(self, *, timestamp: EventTime) -> 'ShellActionResult':
        rule_result = self.controller.services.rules.evaluate(
            timestamp=timestamp,
            active_alarm_statuses=self.controller.services.events.active_statuses,
            variable_snapshots=self.controller.services.variables.snapshots,
        )
        for row in rule_result.rows:
            self.controller.services.runtime_quality.record_operational_entry(
                timestamp=timestamp,
                record_type='rule_evaluation',
                payload=row.as_dict(),
            )
        sequence_result = self.controller.services.sequences.evaluate(
            timestamp=timestamp,
            active_alarm_statuses=self.controller.services.events.active_statuses,
        )
        for row in sequence_result.rows:
            self.controller.services.runtime_quality.record_operational_entry(
                timestamp=timestamp,
                record_type='sequence_transition',
                payload=row.as_dict(),
            )
        action_requests = list(sequence_result.action_requests) + list(rule_result.action_requests)
        for action in action_requests:
            claim_key, governed_action, target_kind, target_id, correlation_id = self._automation_claim_context(action=action, timestamp=timestamp)
            if self._automation_action_already_satisfied(action=action):
                if claim_key is not None:
                    claim_row = self.controller.services.claims.record_suppression(
                        claim_key=claim_key,
                        governed_action=governed_action,
                        target_kind=target_kind,
                        target_id=target_id,
                        claimed_by=f'{action.source_kind}-{action.source_id}',
                        correlation_id=correlation_id,
                        timestamp=timestamp,
                        reason='already_satisfied',
                    )
                    self.controller.services.runtime_quality.record_operational_entry(
                        timestamp=timestamp,
                        record_type='automation_claim',
                        payload=claim_row.as_dict(),
                    )
                self._record_automation_suppression(
                    action=action,
                    timestamp=timestamp,
                    claim_key=claim_key,
                    correlation_id=correlation_id,
                    reason='already_satisfied',
                )
                continue
            if claim_key is not None and self.controller.services.claims.has_active_claim(claim_key=claim_key):
                claim_row = self.controller.services.claims.record_suppression(
                    claim_key=claim_key,
                    governed_action=governed_action,
                    target_kind=target_kind,
                    target_id=target_id,
                    claimed_by=f'{action.source_kind}-{action.source_id}',
                    correlation_id=correlation_id,
                    timestamp=timestamp,
                    reason='already_claimed',
                )
                self.controller.services.runtime_quality.record_operational_entry(
                    timestamp=timestamp,
                    record_type='automation_claim',
                    payload=claim_row.as_dict(),
                )
                self._record_automation_suppression(
                    action=action,
                    timestamp=timestamp,
                    claim_key=claim_key,
                    correlation_id=correlation_id,
                    reason='already_claimed',
                )
                continue
            if claim_key is not None:
                claim_row = self.controller.services.claims.claim(
                    claim_key=claim_key,
                    governed_action=governed_action,
                    target_kind=target_kind,
                    target_id=target_id,
                    claimed_by=f'{action.source_kind}-{action.source_id}',
                    correlation_id=correlation_id,
                    timestamp=timestamp,
                )
                self.controller.services.runtime_quality.record_operational_entry(
                    timestamp=timestamp,
                    record_type='automation_claim',
                    payload=claim_row.as_dict(),
                )
            if action.action_kind == 'ack_alarm':
                alarm_id = AlarmId(str(action.action_payload.get('alarm_id', '')))
                actor = ActorId(f'{action.source_kind}-{action.source_id}')
                self.controller.acknowledge_alarm(
                    alarm_id=alarm_id,
                    actor=actor,
                    timestamp=timestamp,
                    command_id=self.controller._ack_command_id(alarm_id=alarm_id, actor=actor, timestamp=timestamp),
                    correlation_id=correlation_id,
                )
                record = self.controller.services.commands.records[-1]
            elif action.action_kind == 'dry_run_adapter_command':
                actor = ActorId(f'{action.source_kind}-{action.source_id}')
                self.controller.submit_dry_run_adapter_command(
                    command_id=str(action.action_payload.get('command_id', f'CMD-{action.source_id}-{int(timestamp)}')),
                    adapter_id=str(action.action_payload.get('adapter_id', '')),
                    point_id=str(action.action_payload.get('point_id', '')),
                    requested_value=str(action.action_payload.get('requested_value', '0')),
                    actor=actor,
                    timestamp=timestamp,
                    correlation_id=correlation_id,
                )
                record = self.controller.services.commands.records[-1]
            else:
                self.controller.services.runtime_quality.record_operational_entry(
                    timestamp=timestamp,
                    record_type='automation_unsupported_action',
                    payload=action.as_dict(),
                )
                if claim_key is not None:
                    resolved = self.controller.services.claims.resolve(
                        claim_key=claim_key,
                        timestamp=timestamp,
                        status=GovernedActionClaimStatus.SUPPRESSED,
                        command_id=None,
                        reason='unsupported_action',
                    )
                    if resolved is not None:
                        self.controller.services.runtime_quality.record_operational_entry(
                            timestamp=timestamp,
                            record_type='automation_claim',
                            payload=resolved.as_dict(),
                        )
                continue
            if claim_key is not None:
                resolved = self.controller.services.claims.resolve(
                    claim_key=claim_key,
                    timestamp=timestamp,
                    status=GovernedActionClaimStatus.COMPLETED if record.admitted else GovernedActionClaimStatus.REJECTED,
                    command_id=record.intent.command_id,
                    reason=record.result_summary if record.admitted else (record.rejection_reason or record.result_summary),
                )
                if resolved is not None:
                    self.controller.services.runtime_quality.record_operational_entry(
                        timestamp=timestamp,
                        record_type='automation_claim',
                        payload=resolved.as_dict(),
                    )
            if action.source_kind == 'rule':
                row = self.controller.services.rules.record_action_result(rule_id=action.source_id, record=record, timestamp=timestamp)
                self.controller.services.runtime_quality.record_operational_entry(
                    timestamp=timestamp,
                    record_type='rule_action_result',
                    payload=row.as_dict(),
                )
            elif action.source_kind == 'sequence':
                rows = self.controller.services.sequences.apply_command_result(sequence_id=action.source_id, record=record, timestamp=timestamp)
                for row in rows:
                    self.controller.services.runtime_quality.record_operational_entry(
                        timestamp=timestamp,
                        record_type='sequence_transition',
                        payload=row.as_dict(),
                    )
        return self.controller._commit('evaluate_automation', self.controller.session)

    def _automation_claim_context(self, *, action: object, timestamp: EventTime) -> tuple[str | None, str, str, str, str | None]:
        action_kind = str(getattr(action, 'action_kind', ''))
        action_payload = getattr(action, 'action_payload', {})
        if action_kind == 'ack_alarm':
            alarm_id = AlarmId(str(action_payload.get('alarm_id', '')))
            status = self.controller.services.events.active_statuses.get(alarm_id)
            state_version = int(timestamp)
            if status is not None:
                if status.first_raised_at is not None:
                    state_version = int(status.first_raised_at)
                elif status.last_changed_at is not None:
                    state_version = int(status.last_changed_at)
            claim_key = f'ack_alarm:{self.controller._id_token(alarm_id)}:{state_version}'
            correlation_id = f'ACT-ACK-{self.controller._id_token(alarm_id)}-{state_version}'
            return claim_key, 'ack_alarm', 'alarm', str(alarm_id), correlation_id
        return None, action_kind, 'unknown', '', None

    def _automation_action_already_satisfied(self, *, action: object) -> bool:
        action_kind = str(getattr(action, 'action_kind', ''))
        action_payload = getattr(action, 'action_payload', {})
        if action_kind == 'ack_alarm':
            alarm_id = AlarmId(str(action_payload.get('alarm_id', '')))
            status = self.controller.services.events.active_statuses.get(alarm_id)
            return status is None or not status.active or status.acknowledged
        return False

    def _record_automation_suppression(
        self,
        *,
        action: object,
        timestamp: EventTime,
        claim_key: str | None,
        correlation_id: str | None,
        reason: str,
    ) -> None:
        action_kind = str(getattr(action, 'action_kind', ''))
        source_kind = str(getattr(action, 'source_kind', ''))
        source_id = str(getattr(action, 'source_id', ''))
        if source_kind == 'rule':
            row = self.controller.services.rules.record_action_suppressed(
                rule_id=source_id,
                action_kind=action_kind,
                timestamp=timestamp,
                claim_key=claim_key,
                correlation_id=correlation_id,
                reason=reason,
            )
            self.controller.services.runtime_quality.record_operational_entry(
                timestamp=timestamp,
                record_type='rule_action_result',
                payload=row.as_dict(),
            )
        elif source_kind == 'sequence':
            row = self.controller.services.sequences.record_action_suppressed(
                sequence_id=source_id,
                timestamp=timestamp,
                action_kind=action_kind,
                claim_key=claim_key,
                correlation_id=correlation_id,
                reason=reason,
            )
            self.controller.services.runtime_quality.record_operational_entry(
                timestamp=timestamp,
                record_type='sequence_transition',
                payload=row.as_dict(),
            )


    def _active_adapter_status_snapshot(self) -> dict[str, object] | None:
        return self.controller._device_handler()._active_adapter_status_snapshot()

    def lifecycle_review_bundle(self) -> dict[str, object]:
        bundle = self.controller._lifecycle().build_review_bundle(ui_session=self.controller.session.ui_session).as_dict()
        bundle['transition_trace'] = list(self.controller._recent_lifecycle_transition_trace())
        bundle['incremental_runtime_summary'] = self.controller._incremental_runtime_summary()
        bundle['runtime_performance'] = self.controller.services.runtime_metrics.snapshot()
        bundle['runtime_status'] = self.controller.services.runtime_quality.snapshot().as_dict()
        bundle['runtime_checkpoint_summary'] = self.controller.services.runtime_quality.latest_checkpoint_summary()
        bundle['runtime_recovery_bundle'] = self.controller.services.runtime_quality.build_recovery_bundle()
        bundle['event_alarm_summary'] = self.controller._event_alarm_summary()
        bundle['command_summary'] = self.controller._command_summary()
        bundle['action_claim_summary'] = self.controller.services.claims.summary()
        bundle['rule_summary'] = self.controller._rule_summary()
        bundle['sequence_summary'] = self.controller._sequence_summary()
        bundle['active_alarm_rows'] = list(self.controller.services.events.active_alarm_rows())
        bundle['recent_event_rows'] = list(self.controller.services.events.recent_rows())
        bundle['recent_runtime_event_rows'] = list(self.controller.services.runtime_quality.recent_event_rows())
        bundle['recent_command_rows'] = list(self.controller.services.commands.recent_rows())
        bundle['recent_action_claim_rows'] = list(self.controller.services.claims.recent_rows())
        bundle['recent_rule_rows'] = list(self.controller.services.rules.recent_rows())
        bundle['recent_sequence_rows'] = list(self.controller.services.sequences.recent_rows())
        bundle['variable_snapshot_rows'] = list(self.controller._variable_snapshot_rows())
        bundle['runtime_variable_rows'] = list(self.controller.services.runtime_quality.variable_rows())
        bundle['active_adapter_status'] = self._active_adapter_status_snapshot()
        bundle['runtime_truth_surface_inventory'] = build_runtime_truth_surface_inventory()
        bundle['runtime_vocabulary'] = build_runtime_vocabulary_map(
            ui_phase=self.controller.session.ui_session.device_lifecycle_phase.value,
            lifecycle_summary_phase=bundle['lifecycle_summary']['phase'],
            adapter_status=bundle['active_adapter_status'],
        )
        semantic_state = build_runtime_semantic_state(
            ui_phase=self.controller.session.ui_session.device_lifecycle_phase.value,
            lifecycle_summary_phase=bundle['lifecycle_summary']['phase'],
            adapter_status=bundle['active_adapter_status'],
        )
        bundle['runtime_event_taxonomy'] = build_runtime_event_taxonomy(
            recent_runtime_event_rows=bundle['recent_runtime_event_rows'],
            recent_event_rows=bundle['recent_event_rows'],
            recent_command_rows=bundle['recent_command_rows'],
            recent_action_claim_rows=bundle['recent_action_claim_rows'],
            runtime_variable_rows=bundle['runtime_variable_rows'],
        )
        metric_layers = build_runtime_metric_layers(
            runtime_status=bundle['runtime_status'],
            event_alarm_summary=bundle['event_alarm_summary'],
            command_summary=bundle['command_summary'],
            runtime_performance=bundle['runtime_performance'],
            adapter_status=bundle['active_adapter_status'],
            semantic_state=semantic_state,
        )
        bundle['runtime_metric_layers'] = metric_layers.as_dict()
        bundle['reviewer_runtime_rollup'] = build_runtime_reviewer_rollup(
            semantic_state=semantic_state,
            metric_layers=metric_layers,
            event_taxonomy=bundle['runtime_event_taxonomy'],
            adapter_status=bundle['active_adapter_status'],
        )
        bundle['canonical_runtime_evidence_bundle_v1'] = build_canonical_runtime_evidence_bundle(
            lifecycle_summary=bundle['lifecycle_summary'],
            binding_review_summary=bundle['binding_review_summary'],
            variable_health_summary=bundle['variable_health_summary'],
            runtime_status=bundle['runtime_status'],
            runtime_performance=bundle['runtime_performance'],
            event_alarm_summary=bundle['event_alarm_summary'],
            command_summary=bundle['command_summary'],
            action_claim_summary=bundle['action_claim_summary'],
            runtime_vocabulary=bundle['runtime_vocabulary'],
            event_taxonomy=bundle['runtime_event_taxonomy'],
            metric_layers=metric_layers,
            reviewer_rollup=bundle['reviewer_runtime_rollup'],
            adapter_status=bundle['active_adapter_status'],
            active_adapter_id=bundle['active_adapter_id'],
            active_device_key=bundle['active_device_key'],
        )
        return bundle
