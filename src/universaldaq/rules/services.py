from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Mapping

from universaldaq.commands import CommandRecord
from universaldaq.common import EventTime
from universaldaq.events import AlarmStatus
from universaldaq.signals import VariableSnapshot, VariableState

from .models import AutomationActionRequest, RuleDefinition, RuleEvaluationResult, RuleOutcome, RuleRow


@dataclass(slots=True)
class _RuleState:
    last_evaluated_at: EventTime | None = None
    last_triggered_at: EventTime | None = None
    last_condition_active: bool = False
    last_result: str | None = None
    trigger_count: int = 0
    suppressed_count: int = 0


@dataclass(slots=True)
class RuleEvaluationService:
    definitions: dict[str, RuleDefinition] = field(default_factory=dict)
    recent_rows_buffer: deque[RuleRow] = field(default_factory=lambda: deque(maxlen=64))
    states: dict[str, _RuleState] = field(default_factory=dict)

    def register(self, definition: RuleDefinition) -> None:
        self.definitions[definition.rule_id] = definition
        self.states.setdefault(definition.rule_id, _RuleState())

    def evaluate(
        self,
        *,
        timestamp: EventTime,
        active_alarm_statuses: Mapping[object, AlarmStatus],
        variable_snapshots: Mapping[object, VariableSnapshot],
    ) -> RuleEvaluationResult:
        requests: list[AutomationActionRequest] = []
        rows: list[RuleRow] = []
        active_alarm_map = {str(key): value for key, value in active_alarm_statuses.items()}
        snapshot_map = {str(key): value for key, value in variable_snapshots.items()}
        for definition in self.definitions.values():
            state = self.states.setdefault(definition.rule_id, _RuleState())
            condition_active = self._condition_active(definition=definition, active_alarm_statuses=active_alarm_map, variable_snapshots=snapshot_map)
            outcome = RuleOutcome.NO_MATCH
            action_kind: str | None = None
            if not definition.enabled:
                outcome = RuleOutcome.DISABLED
            elif condition_active:
                eligible = (
                    (not state.last_condition_active)
                    or state.last_triggered_at is None
                    or (definition.cooldown_ticks > 0 and (int(timestamp) - int(state.last_triggered_at)) >= definition.cooldown_ticks)
                )
                if eligible:
                    outcome = RuleOutcome.TRIGGERED
                    action_kind = definition.action_kind
                    requests.append(
                        AutomationActionRequest(
                            source_kind='rule',
                            source_id=definition.rule_id,
                            action_kind=definition.action_kind,
                            action_payload=definition.action_payload,
                        )
                    )
                    state.last_triggered_at = timestamp
                    state.trigger_count += 1
                else:
                    outcome = RuleOutcome.SUPPRESSED
                    state.suppressed_count += 1
            row = RuleRow(
                rule_id=definition.rule_id,
                timestamp=timestamp,
                outcome=outcome,
                condition_active=condition_active,
                action_kind=action_kind,
            )
            rows.append(row)
            self.recent_rows_buffer.append(row)
            state.last_condition_active = condition_active
            state.last_evaluated_at = timestamp
            state.last_result = outcome.value
        return RuleEvaluationResult(action_requests=tuple(requests), rows=tuple(rows))

    def record_action_result(self, *, rule_id: str, record: CommandRecord, timestamp: EventTime) -> RuleRow:
        outcome = RuleOutcome.TRIGGERED if record.admitted else RuleOutcome.SUPPRESSED
        row = RuleRow(
            rule_id=rule_id,
            timestamp=timestamp,
            outcome=outcome,
            condition_active=True,
            action_kind=record.intent.command_kind,
            command_id=record.intent.command_id,
            correlation_id=record.intent.correlation_id,
            result_summary=record.result_summary,
        )
        self.recent_rows_buffer.append(row)
        state = self.states.setdefault(rule_id, _RuleState())
        state.last_result = record.result_summary
        state.last_evaluated_at = timestamp
        return row

    def record_action_suppressed(
        self,
        *,
        rule_id: str,
        action_kind: str,
        timestamp: EventTime,
        claim_key: str | None,
        correlation_id: str | None,
        reason: str,
    ) -> RuleRow:
        if self.recent_rows_buffer:
            previous = self.recent_rows_buffer[-1]
            if (
                previous.rule_id == rule_id
                and previous.timestamp == timestamp
                and previous.outcome == RuleOutcome.TRIGGERED
                and previous.command_id is None
            ):
                self.recent_rows_buffer.pop()
        row = RuleRow(
            rule_id=rule_id,
            timestamp=timestamp,
            outcome=RuleOutcome.SUPPRESSED,
            condition_active=True,
            action_kind=action_kind,
            correlation_id=correlation_id,
            claim_key=claim_key,
            suppression_reason=reason,
            result_summary=reason,
        )
        self.recent_rows_buffer.append(row)
        state = self.states.setdefault(rule_id, _RuleState())
        state.suppressed_count += 1
        state.last_result = reason
        state.last_evaluated_at = timestamp
        return row

    def summary(self) -> dict[str, object]:
        enabled = [definition for definition in self.definitions.values() if definition.enabled]
        return {
            'rule_count': len(self.definitions),
            'enabled_rule_count': len(enabled),
            'recent_rule_row_count': len(self.recent_rows_buffer),
            'triggered_total': sum(state.trigger_count for state in self.states.values()),
            'suppressed_total': sum(state.suppressed_count for state in self.states.values()),
        }

    def recent_rows(self, *, limit: int = 16) -> tuple[dict[str, object], ...]:
        rows = [row.as_dict() for row in self.recent_rows_buffer]
        return tuple(rows[-max(1, limit):])

    @staticmethod
    def _condition_active(
        *,
        definition: RuleDefinition,
        active_alarm_statuses: Mapping[str, AlarmStatus],
        variable_snapshots: Mapping[str, VariableSnapshot],
    ) -> bool:
        payload = {str(key): value for key, value in definition.condition_payload.items()}
        if definition.condition_kind == 'alarm_active_unacknowledged':
            alarm_id = str(payload.get('alarm_id', ''))
            status = active_alarm_statuses.get(alarm_id)
            return status is not None and status.active and not status.acknowledged
        if definition.condition_kind == 'alarm_active':
            alarm_id = str(payload.get('alarm_id', ''))
            status = active_alarm_statuses.get(alarm_id)
            return status is not None and status.active
        if definition.condition_kind == 'variable_state':
            variable_id = str(payload.get('variable_id', ''))
            target_state = str(payload.get('state', ''))
            snapshot = variable_snapshots.get(variable_id)
            return snapshot is not None and snapshot.state == VariableState(target_state)
        return False
